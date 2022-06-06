try:
    import tractor_py3.api.author as author
    import hou
    import bpy
    import nuke
    import maya.cmds as cmds
except ImportError:
    print("some packages not loaded")
    pass

from .submitter import Spool
from time import sleep
import os
import shutil

from .hslu_houdini_methods import NodeHandlingMethods, NodeProcessMethods
from ProjectManager.Utils.makers import CreationMethods, NumberMethods

"""
<activate_hython_terminal.sh> :
The command calls <activate_hython_terminal.sh> that uses ecosystem.py to create a replica of the current
houdini environment in the Slave. 
=> Then it creates a temporary script </tmp/tmp_HythonCall_command.sh> that calls <templates/call_hython_template.sh> with 
the houdini parameters 
=> Then it opens a Terminal in The Gui of the slave and calls </tmp/script.sh> with it.
    ||
    ||
    |_=> </tmp/tmp_HythonCall_command.sh>:
            First the just generated </tmp/ecosystem.env> is sourced
            then we setup_houdini
            Through the Gui Terminal <houdini_node_processor.py> is called with hython feeding in the houdini parameters.
                    ||
                    ||
                    |_=> <houdini_node_processor.py> decides depending on the node sent what to do next.
                            ||
                            ||
                            |_=> Given an OpenGL, Simulation or TopCooking node a Houdini Gui instance needs to be opened
                                <call_houdini_terminal.sh>:
                                    => creates a temporary script </tmp/tmp_HoudiniRender_command.sh> that calls <templates/call_houdini..termplate.sh> with 
                                        the houdini parameters
                                    => <templates/call_Houdini_template.py> gets copied to </tmp/call_houdini_process.py>
                                    => Then <py_template_rewrite.py> rewrites the script </tmp/call_houdini_process.py> to contain the submitted node
                                        
                                        ==> then </tmp/tmp_HoudiniRender_command.sh> gets executed with a gui terminal :
                                            opeining houdini with </tmp/call_houdini_process.py
"""


class HoudiniSubmissionMethods:
    def __init__(self, node):

        # self.type = type
        self.node = node
        ##### TRACTOR VARIABLES ######
        ##### PRIVATE VARIABLES ######

        self.tractorEngineName = os.environ.get("TRACTOR_HOST")
        self.tractorEnginePort = os.environ.get("TRACTOR_PORT")

        if "TRACTOR_ENGINE" in os.environ.keys():
            name = os.environ["TRACTOR_ENGINE"]
            self.tractorEngineName, n, p = name.partition(":")
            if p:
                self.tractorEnginePort = int(p)
        self.envlist = self.ListifyInput(os.environ.get("TOOLS"))
        self.envkey = os.environ.get("TOOLS")

        ## HIP FILE INFO EXTRACTION ##
        self.hipfile_path = hou.hipFile.path()
        self.spooldirname = os.path.dirname(self.hipfile_path)
        self.basefilename = os.path.basename(os.path.splitext(self.hipfile_path)[0])

        """
        Method flawed, Path needs to be OS independent => Possible Solution:
        copy an instance of batch_calls folder to /tmp/
        always check if it exists and if not copy it.
        """
        #### BASE ####
        self.ecosystem_path = os.getenv("AVEEE_CASKS")
        self.houdini_major = os.getenv("HOUDINI_MAJOR_VERSION")
        self.houdini_minor = os.getenv("HOUDINI_MINOR_VERSION")
        self.houdini_patch = os.getenv("HOUDINI_PATCH_VERSION")
        self.houdini_version = "{}.{}".format(self.houdini_major, self.houdini_minor)

        #### ESTABLISH TMP FOLDER ###

        self.tmp_path = os.path.join(self.spooldirname, ".tmp_rendering")
        # CreationMethods.makedir(self.tmp_path)

        self.tmp_job_path = os.path.join(self.tmp_path, NumberMethods.HostAndDateNow())
        CreationMethods.makedir(self.tmp_job_path)

        ### CREATE JOB PATH VARIABLES ###
        self.alf_job_name = "{}_{}_{}.alf".format(
            self.basefilename, self.node.name(), NumberMethods.now()
        )

        self.alf_job_path = os.path.join(self.tmp_job_path, self.alf_job_name)

        ### Create Dict of Source and Target PATHS ###
        self.batch_calls_src = os.path.join(
            self.ecosystem_path,
            "plugins",
            "houdini",
            self.houdini_version,
            "HSLU",
            "scripts",
            "python",
            "tractor_submitter",
            "batch_calls",
        )

        self.batch_calls_tar = os.path.join(self.tmp_job_path, "batch_calls")

        self.ecosystem_script_src = os.path.join(os.getenv("AVEEE_CASKS"), "ecosystem")

        self.ecosystem_script_tar = os.path.join(self.batch_calls_tar, "ecosystem")

        self.env_files_src = os.path.join(os.getenv("AVEEE_CASKS"), "ecosystem-env")

        self.env_files_tar = os.path.join(self.batch_calls_tar, "ecosystem-env")

        self.hslu_postscripts_src = os.path.join(
            self.ecosystem_path, "scripts", "tractor", "cleanup"
        )
        self.hslu_postscript_tar = os.path.join(self.batch_calls_tar, "cleanup")

        src_paths = [
            self.batch_calls_src,
            self.ecosystem_script_src,
            self.env_files_src,
            self.hslu_postscripts_src,
        ]
        dest_paths = [
            self.batch_calls_tar,
            self.ecosystem_script_tar,
            self.env_files_tar,
            self.hslu_postscript_tar,
        ]

        zipped_paths = zip(src_paths, dest_paths)

        ### Copy Folders from Source to Target PATHS ###
        # CreationMethods.CopyTreeFromDict(zipped_paths)

        ### CMDS TO CALL ###

        self.batchstart_path = os.path.join(
            self.batch_calls_tar, "activators", "activate_hython_terminal.sh"
        )

    # --------------------------#
    #      TRACTOR METHODS      #
    # --------------------------#

    """
    Send Job
    """

    def SpoolJob(self, jobScript):
        # self.updateVariables()

        self.tractorEngine = (
            "" + str(self.tractorEngineName) + ":" + str(self.tractorEnginePort)
        )

        args = []
        args.append("--engine=" + self.tractorEngine)
        # if self.doJobPause:
        #    args.append('--paused')
        args.append(jobScript)

        Spool(args)

    """
    Key And Parameter Tweakers
    """

    def ListifyInput(self, text):
        text_list_space = text.split(" ")
        text_list_comma = text.split(",")
        if len(text_list_space) > 1:
            listified = [string for string in text_list_space if len(string) >= 1]
        else:
            listified = text_list_comma
        return listified

    """
    Submission Keys and Parameters
    """

    def RenderService(self, blades):

        if blades.currentText() == "D300 GPUs":
            service = "HoudiniRenderD300"
        elif blades.currentText() == "D500 GPUs":
            service = "HoudiniRenderD500"
        elif blades.currentText() == "Linux":
            service = "Linux"
        else:
            service = "HoudiniRender"

        return service

    def MoreEnvkeys(self, extrakeys):
        extrakeylist = self.ListifyInput(extrakeys)
        self.envkey = "TOOLS={}".format(self.envlist + extrakeylist)

    """
    Create Job Scripts
    """

    def SingleSlaveJob(self):

        alf_job = author.Job()
        alf_job.title = self.alf_job_name
        alf_job.service = "HoudiniRender"
        # alf_job.projects = "Default"

        BatchTask = author.Task()
        BatchTask.title = "RemoteCmd {}".format(self.node.type().name())
        BatchTaskCommand = author.Command()
        BatchTaskCommand.argv = "{} {} {} {}".format(
            self.batchstart_path, self.envkey, self.hipfile_path, self.node.path()
        )
        BatchTask.addCommand(BatchTaskCommand)

        alf_job.addChild(BatchTask)
        self.WriteAlfFile(alf_job.asTcl())

        sleep(1)

        self.SpoolJob(self.alf_job_path)
        # alf_job.spool()

    def GuiDebugJob(self):

        alf_job = author.Job()
        alf_job.title = self.alf_job_name
        alf_job.service = "Linux"
        # alf_job.projects = "Default"

        BatchTask = author.Task()
        BatchTask.title = "RemoteCmd {}".format(self.node.type().name())
        BatchTaskCommand = author.Command()
        BatchTaskCommand.argv = "{} {}".format(
            os.path.join(self.batch_calls_tar, "create_environment.sh"), self.envkey
        )
        BatchTask.addCommand(BatchTaskCommand)

        # RemoveTask = author.Post

        alf_job.addChild(BatchTask)
        # alf_job.newPostscript(
        #     argv="/usr/bin/env python3 {}/temp_file_remover.py {}".format(
        #         self.hslu_postscript_tar, self.tmp_job_path
        #     ),
        #     service="HoudiniRender",
        # )
        self.WriteAlfFile(alf_job.asTcl())

        sleep(1)

        self.SpoolJob(self.alf_job_path)

    def WriteAlfFile(self, job_as_tcl):
        new_alf_file = open(self.alf_job_path, "w")
        new_alf_file.write(job_as_tcl)
        new_alf_file.close()

    def MultiSlaveJob(self, node):

        # Create the .alf script to write on
        alf_job_name = "{}_{}_{}.alf".format(
            self.basefilename, node.name(), NumberMethods.now()
        )
        alf_job_path = os.path.join(self.spooldirname, alf_job_name)

        alf_job = author.Job()
        alf_job.title = alf_job_name
        alf_job.priority = self.priority.currentText()
        alf_job.tags = self.ListifyInput(self.inputs["Tags"])
        alf_job.service = self.RenderService()
        alf_job.crews = self.ListifyInput(self.inputs["Crews"])
        alf_job.projects = self.ProjectDataInfo[0][0]
        alf_job.envkey = self.envkey
        alf_job.serialsubtasks = True

        pass

    def CreateRenderFileJobScript(self, node):

        # Dispatch the job to tractor.
        # Spool out the houdini file.

        # spooledfiles = []

        if self.blades.currentText() == "D300 GPUs":
            service = "HoudiniRenderD300"
        elif self.blades.currentText() == "D500 GPUs":
            service = "HoudiniRenderD500"
        elif self.blades.currentText() == "Linux":
            service = "Linux"
        else:
            service = "HoudiniRender"

        fpu = self.fpu.value()

        # Create the .alf script to write on
        jobshort = "{}_{}_{}.alf".format(
            self.basefilename, node.name(), NumberMethods.now()
        )
        jobfull = os.path.join(self.spooldirname, jobshort)

        # start writing into .alf
        self.file = open(jobfull, "w")
        # spooledfiles.append(jobfull)
        self.file.write("Job -title {{{}}}".format(jobshort))

        self.file.write(" -priority {}".format(self.priority.currentText()))
        self.file.write(" -tags {{ Houdini {} }}".format(self.inputs["Tags"].text()))

        self.file.write(" -service {{ {} }}".format(service))
        self.file.write(" -crews {{{}}}".format(self.inputs["Crews"].text()))

        self.file.write(" -projects Default")
        self.file.write(" -envkey {{{}}}".format(self.envkey))
        self.file.write(" -serialsubtasks 1")
        self.file.write(" -subtasks {\n")

        self.file.write("    Task {Render Frames} -subtasks {\n")

        # node range setting
        validFrameRange = node.parm("trange").eval()

        if validFrameRange == 0:
            node_start = int(hou.frame())
            node_end = int(hou.frame())
            node_step = 1
        else:
            node_start = int(node.parm("f1").eval())
            node_end = int(node.parm("f2").eval())
            node_step = int(node.parm("f3").eval())

        # start standard hqueue render

        # def export_mode(self,node,cachefile_extension):
        # relative path for file export in houdini

        node_type_name = node.type().name()  # ifd, arnold, ris

        if "ifd" in node_type_name:
            cachefile_extension = "ifd"
            # renderer = "mantra"
            renderer = "mantra-shim"
            renderer_arguments = "-V 1a -f"

            outputpicture_param = "vm_picture"
            outputpicture_mode_param = "soho_outputmode"
            outputpicture_path_param = "soho_diskfile"
            tempstorage_path_param = "vm_tmpsharedstorage"
            tempstorage_name = "storage"

        elif "arnold" in node_type_name:
            cachefile_extension = "ass"
            renderer = "kick"
            renderer_arguments = "-dw -dp -nostdin"

            outputpicture_param = "ar_picture"
            outputpicture_mode_param = "ar_ass_export_enable"
            outputpicture_path_param = "ar_ass_file"
            tempstorage_path_param = False  # unused
            tempstorage_name = False  # unused

        else:
            cachefile_extension = "rib"
            renderer = "prman"
            renderer_arguments = ""

            outputpicture_param = "ri_display_0"
            outputpicture_mode_param = "diskfile"
            outputpicture_path_param = "soho_diskfile"
            tempstorage_path_param = "vdbpath"
            tempstorage_name = "vdbs"

        outputpicture_rawvalue = node.parm(outputpicture_param).rawValue()
        renderfile_folder = "{}_{}_{}".format(
            basefilename, node.name(), node.type().name()
        )
        renderfile_name = "{}.$F4.{}".format(node.name(), cachefile_extension)

        outputpicture_dirname = os.path.dirname(outputpicture_rawvalue)
        renderimage_path = os.path.join(outputpicture_dirname, renderfile_folder)

        # setup parameters for file export
        node.parm(outputpicture_mode_param).set(True)
        node.parm(outputpicture_path_param).set(
            "{}/{}".format(renderimage_path, renderfile_name)
        )

        if tempstorage_path_param:
            node.parm(tempstorage_path_param).set(
                "{}/{}".format(renderimage_path, tempstorage_name)
            )

        # absolute path for folder creation
        outputpicture_evalvalue = node.parm(outputpicture_param).eval()

        # create render folder
        # outputpicture_evalvalue_dirname = os.path.dirname(outputpicture_evalvalue)
        # MethodsHSLU.makedir(outputpicture_evalvalue_dirname)

        # create export folder
        tempfile_path = os.path.join(
            os.path.dirname(outputpicture_evalvalue), renderfile_folder
        )
        CreationMethods.makedir(tempfile_path)

        renderfile_query = []

        # write (ifd) files to disk and start a process afterwards
        if NodeProcessMethods.ButtonPressReaction(node.parm("execute")):

            # all_render_files = [render_file for render_file in sorted(os.listdir(tempfile_path) if cachefile_extension in render_file]
            for render_file in sorted(os.listdir(tempfile_path)):
                ext = render_file.split(".")[-1]
                if cachefile_extension == ext:
                    print(render_file.split("."))
                    number = int(render_file.split(".")[-2])
                    if (
                        number >= node_start
                        and number <= node_end
                        and (number - node_start) % node_step == 0
                    ):
                        renderfile_query.append(render_file)

            print(renderfile_query)

            # reset param to cache files
            node.parm(outputpicture_mode_param).set(False)

            for render_file in renderfile_query:
                # title = "Frame {}".format(s) if s == e else "Frame {} - {}".format(s, e)
                tempfile_name = os.path.join(tempfile_path, render_file)
                title = "Frame from {}".format(render_file)

                self.file.write("        Task {{ {} }} -cmds {{\n".format(title))
                # self.file.write("            RemoteCmd {{{} {}/houBatch.py {} {} {} {} {}}} -service {{ {} }} -envkey {{ {} }} -priority {{ {} }} -tags {{ Houdini {} }}\n".format( "/opt/houdini/18.0.416/bin/hython", cur_script_path, hipfile_tmp_fullpath, node.path(), s, e, node_step, service, self.envkey, self.priority.currentIndex(), self.dict_of_fields["Tags"].text() ))
                self.file.write(
                    "            RemoteCmd {{{} {} {} }} -service {{ {} }} -envkey {{ {} }} -priority {{ {} }} -tags {{ Houdini {} }}\n".format(
                        renderer,
                        renderer_arguments,
                        tempfile_name,
                        service,
                        self.envkey,
                        self.priority.currentIndex(),
                        self.inputs["Tags"].text(),
                    )
                )
                self.file.write("        }\n")

            self.file.write("    }\n")

            self.file.write(" Task { Cleanup temp files } -cleanup {\n")

            self.file.write(
                "       RemoteCmd {{ {} {} {} {} }} \n".format(
                    "/usr/bin/env", "python", self.file_remover, tempfile_path
                )
            )
            self.file.write("}\n")

            self.file.write("}\n")
            self.file.close()

            # Just to make doubly sure the .alf script is available on disk.
            sleep(1)
            # Dispatch the job to tractor.
            # tractor_host = os.environ.get('TRACTOR_HOST')
            # tractor_port = os.environ.get('TRACTOR_PORT')
            # command = "tractor-spool --engine={}:{} {}".format(tractor_host, tractor_port, jobfull)

        return jobfull