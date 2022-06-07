try:
    import hou
except ImportError:
    print("hou python not found")
from uuid import uuid4
import os
from ProjectManager.db_methods import MethodsDB
from ProjectManager.Utils.makers import CreationMethods
from PySide2 import QtWidgets

def ExportTypes():
    return [
            "ifd",
            "arnold",
            "filecache",
            "usdexport",
            "hammer::fbx_export::1.0",
            "rop_alembic",
            "rop_gltf",
            "topnet",
            "opengl",
        ]

def RenderTypes():
    return {
        
            "ifd": {
                "imgs": "vm_picture",
                "frame_range": "trange",
                "frame_start": "f1",
                "frame_end": "f2",
                "skip": "f3",
                "ext" : "ifd",
                "bool": "soho_outputmode", 
                "path": "soho_diskfile"
                }
        ,
            "arnold": {
                "imgs": "ar_picture",
                "frame_range": "trange",
                "frame_start": "f1",
                "frame_end": "f2",
                "skip": "f3",
                "ext" : "ass",
                "bool": "ar_ass_export_enable", 
                "path": "ar_ass_file"
                }
        , 
            "Redshift_ROP": {
                "imgs": "vm_picture",
                "frame_range": "trange",
                "frame_start": "f1",
                "frame_end": "f2",
                "skip": "f3",
                "ext" : "rs",
                "bool": "soho_outputmode", 
                "path": "soho_diskfile"
                }
        ,
            "ris::22": {
                "imgs": "vm_picture",
                "frame_range": "trange",
                "frame_start": "f1",
                "frame_end": "f2",
                "skip": "f3",
                "ext" : "rib",
                "bool": "soho_outputmode", 
                "path": "soho_diskfile"
                }
        ,
    }


class TopManagingMethods:
    def __init__(self, sequenceshot: str, selection: list):
        # TODO: find way to feed sequenceshot into class in main_gui
        self.sequenceshot = sequenceshot
        self.selection = selection

        self.render_types = RenderTypes()
        self.type_dict = self.render_types["ifd"]

        self.ext = self.type_dict["ext"]
        self.rp_parm = self.type_dict["imgs"]
        self.rf_switch = self.type_dict["bool"]
        self.rf_parm = self.type_dict["path"]
        self.range = self.type_dict["frame_range"]
        self.start = self.type_dict["frame_start"]
        self.end = self.type_dict["frame_end"]
        self.skip = self.type_dict["skip"]

    def CreateTopGraphAndCook(self, tractor=False):

        if tractor:
            print("Tractor Send Command is on")
            print(self.selection)

        else:
            print("Tractor Send Command OFF setting up Top locally")
            # create a top network called like the sequence in /out

            output = self.BuildRopfetchTree()
            cook_out = self.StartCooking(output)
            # bind them to a waitforall node
            # connect to output
            # cook node

            # when finished send a signal to a tractor manager that the files have been written out
            # when finished store information of the tops written out in database

            return cook_out

    def CreateTop(self):
        ParentGrp = NodeProcessMethods.CleanString(hou.hipFile.basename().split(".")[0])
        ParentPath = f"/out/HSLU_NP_{ParentGrp}"

        graph_uuid = uuid4()
        top_name = NodeProcessMethods.CleanString(self.sequenceshot)

        if NodeProcessMethods.VerifyHouNode(ParentPath):
            pass
        else:
            hou.node("/out").createNode("subnet", ParentPath)

        new_top = hou.node(ParentPath).createNode("topnet", top_name)
        

        # add uuid to top graph
        new_top.setUserData("top_uuid", graph_uuid)
        ParentPath.layoutChildren()
        # uuid of top to Database

        return new_top

    def BuildRopfetchTree(self):

        new_top = self.CreateTop()
        # inside of that top create ropfetch node that link to the the nodes selected in the tractor manager
        rop_base_pos = [0, 0]

        waitforall = new_top.createNode("waitforall", "waitforall")
        output = new_top.createNode("output", "output")

        output.setInput(0, waitforall)

        for i, node in enumerate(self.selection):
            self.type_dict = self.render_types[node.type().name()]
            self.ChangeToFileExport(node)

            add_rop = new_top.createNode("ropfetch", f"ropfetch_{node.name()}")
            add_rop.setPosition(rop_base_pos)
            rop_base_pos[0] += 2

            waitforall.setInput(i, add_rop)

            self.RopToFetch(node,add_rop)

        avg_x = rop_base_pos[0] / 2

        waitforall.setPosition([avg_x, -5])
        output.setPosition([avg_x, -5])

        return output

    def ChangeToFileExport(self,node : hou.node):
        # takes a renderer type and tweaks its parameters to make it a file export if not already
        # specified by the user

        rel_render_path = node.parm(self.rp_parm).rawValue()
        abs_render_path = node.parm(self.rp_parm).eval()
        base_rel = os.path.basename(rel_render_path)
        output_frmt = base_rel.split(".")[-1]
        rfile_base = base_rel.replace(
            f".{output_frmt}", ".{}".format(self.ext)
        )

        afile_path = os.path.join(os.path.dirname(abs_render_path),self.ext)
        CreationMethods.makedir(afile_path)

        rfile_path = os.path.join(os.path.dirname(rel_render_path),self.ext,rfile_base)

        if node.parm(self.rf_switch).eval() == 0:
            node.parm(self.rf_switch).set(1)

            node.parm(self.rf_parm).set(rfile_path)
        else:
            pass

    def RopToFetch(self, rop_node: hou.node, fetch_node: hou.node ):

        fetch_node.parm("roporder").set(1)
        fetch_node.parm("roppath").set(rop_node.path())
        fetch_node.parm("framegeneration").set(1)
        fetch_node.parm("range1").set(
            rop_node.parm(self.start.eval())
            )
        fetch_node.parm("range2").set(
            rop_node.parm(self.end.eval())
            )
        fetch_node.parm("range3").set(
            rop_node.parm(self.skip.eval())
            )
    
    def StartCooking(self, cook_node: hou.node):
        # TODO: cook the nodes, when finished if succesfull return True else return False
        if cook_node.executeGraph(False,True,False,False):
            return True
        else:
            return False

    


class NodeProcessMethods:
    @staticmethod
    def VerifyHouNode(node_path):
        try:
            hou.node(node_path)
            return True
        except hou.OperationFailed:
            return False

    @staticmethod
    def ButtonPressReaction(node_parm):
        False
        node_parm.pressButton()
        return True

    @staticmethod
    def CleanString(name: str):
        if name.split(" "):
            name.replace(" ", "_")
        return name


class NodeHandlingMethods:
    def __init__(self, selection):

        self.selection = selection

    def QueryNodes(self):

        active_sel = []
        # query all node types as selectable widgets and connect their utilities to the nodes
        if self.SelectedRenderNodes():
            # draw_method(self.SelectedRenderNodes())
            for node in self.SelectedRenderNodes():
                active_sel.append(node)
        elif self.SelectedRopNodes():
            # draw_method(self.SelectedRopNodes())
            for node in self.SelectedRopNodes():
                active_sel.append(node)
        elif len(self.SelectedRenderNodes()) < 1 or len(self.SelectedRopNodes()) < 1:
            # draw_method(self.AllRenderableNodes())
            for node in self.AllRenderableNodes():
                active_sel.append(node)

        return active_sel

    ###houdini list functions###
    def ExistingRenderers(self):
        # add some existing renderers
        renderers = ["ifd"]
        # plugin_renderers = ["Redshift_ROP", "ris::22", "arnold","opengl"]
        plugin_renderers = ["arnold", "ris::22"]

        for node_type in hou.ropNodeTypeCategory().nodeTypes().values():
            for renderer in plugin_renderers:
                if renderer in node_type.name():
                    renderers.append(renderer)

        return renderers

    def AllRenderableNodes(self):
        all_rendernodes = []
        for node in hou.node("/").allSubChildren():
            if node.type().name() in self.ExistingRenderers():
                all_rendernodes.append(node)

        return all_rendernodes

    def SelectedRenderNodes(self):
        # list all selected renderers
        rendernode_list = []

        for node in self.selection:
            if node.type().name() in self.ExistingRenderers():
                rendernode_list.append(node)

        return rendernode_list

    def SelectedRopNodes(self):
        # list of renderers inside of ropnodes
        rop_rendernode_list = []

        for ropnode in self.selection:
            if ropnode.type().name() == "ropnet":
                for rendernode in hou.node(ropnode.path()).allSubChildren():
                    if rendernode.type().name() in self.ExistingRenderers():
                        rop_rendernode_list.append(rendernode)

        return rop_rendernode_list

    # def is_copy_paste_event(kwargs):
    #     if not kwargs["node"].name().startswith("original") and not kwargs[
    #         "old_name"
    #     ].startswith("original"):
    #         original_node = (
    #             kwargs["node"].parent().node("original0_of_%s" % kwargs["old_name"])
    #         )
    #         return True if original_node else False