from enum import Enum
try:
    from PySide2 import QtGui, QtWidgets, QtCore, QtSvg
except ImportError:
    from PyQt5 import QtGui, QtWidgets, QtCore, QtSvg
    
import os
# import hou
# from plugins.houdini.houdini_methods import ExportTypes
# from plugins.houdini.houdini_buttons import *
from db_methods import MethodsDB
from Utils.makers import NumberMethods




class DropListObjectInfo:
    def __init__(self, uuid: str):
        self.Database = MethodsDB()
        self.uuid = uuid
    
    
    def GetCookStatus(self):
        try:
            job_history = self.Database.FetchAllJobHistoryByUUID(self.uuid)
            cook_status = NumberMethods.IntToBool(job_history[0][6])
            
        except Exception as e:
            print(e)
            cook_status = False
        
        finally:
            return cook_status

    
    def GetRenderStatus(self):
        try:
            job_history = self.Database.FetchAllJobHistoryByUUID(self.uuid)
            render_status = NumberMethods.IntToBool(job_history[0][5])
            
        except Exception as e:
            print(e)
            render_status = False
        
        finally:
            return render_status

    def IsLocal(self,node_path):
        internal = True
        try:
            if hou.node(node_path).userData("uuid") == self.uuid:
                internal = True
        except:
            internal = False
        finally:
            return internal

    def GetFileType(self):
        """
        Get the file type of current list item
        """
        try:
            job_history = self.Database.FetchAllJobHistoryByUUID(self.uuid)
            print(job_history)
            job_path = job_history[0][3]
        except Exception as e:
            print(e)

            job_path = hou.hipFile.name()

        finally:
            return job_path
    
    def GetNodeType(self,node_name: str):
        try:
            job_history = self.Database.FetchAllJobHistoryByUUID(self.uuid)
            print(job_history)
            node_type = job_history[0][4]
        except Exception as e:
            print(e)

            node_type = hou.node(node_name).type().name()

        finally:
            return node_type


class ColorLayout(Enum):
    base = "rgba(100,100,100,100)"
    cooked = "rgba(0,10,180,100)"
    rendered = "rgba(0,180,10,100)"
    ext_base = "rgba(120,120,0,100)"
    ext_cooked = "rgba(50,10,180,100)"
    ext_rendered = "rgba(50,180,10,100)"



class StylingMethods:

    @staticmethod
    def SetLabelStyle(widget: QtWidgets.QLabel, negative=True):
        if negative:
            widget.setStyleSheet(
                """
                        QLabel {
                        font-size: 16px;
                        font-weight: bold;
                        font-style: italic;
                        color: red;
                        border: 3px solid grey;
                        border-radius: 3px;
                        }
                        """
            )
        else:
            widget.setStyleSheet(
                """
                        QLabel {
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                        border: 3px solid grey;
                        border-radius: 3px;
                        }
                        """
            )

    def ChangeBgCol(receiver_widg: QtWidgets.QWidget, color: str):
        receiver_widg.setStyleSheet(
            f"""
            background-color: {color};
            """
            )
    
    def CleanupWidgets(widgetlist: list):
        for value in widgetlist:
            if value is not None:
                value.setStyleSheet(""" background-color: transparent; """)





class BooleanMethods:
    @staticmethod
    def InfoConditionShower(condition: bool, message: str):

        if condition:
            MessageBox = QtWidgets.QHBoxLayout()
            MessageLabel = QtWidgets.QLabel(message)
            MessageBox.addWidget(MessageLabel)

        return MessageBox

    @staticmethod
    def WidgetBlockOnCheck(Activation: QtWidgets.QCheckBox, activate: bool):
        # print(Activation.__class__.__name__)

        if Activation.__class__.__name__ == "QCheckBox":
            if Activation.isChecked() == activate:
                Activation.setChecked(activate)
                Activation.setEnabled(activate)
            else:
                Activation.setChecked(False)
                Activation.setEnabled(activate)

        elif Activation.__class__.__name__ == "QPushButton":
            Activation.setEnabled(activate)

    @staticmethod
    def TreeSelectionBool(widget, widget_class):
        # childnum = self.projectlist.indexFromItem(parent)
        # list_of_children = self.ShotArray[self.sequence_index()][parent]
        # try:
        #     for i in range(parent.childCount()):
        #         return parent.child(i)
        # except:
        #     print('Sequence list is empty')
        if widget.parent().__class__.__name__ == widget_class:
            print("this is a Shot")
            print(widget)
            return True
        else:
            print("This is currently a Sequence")
            return False


class DrawingMethods:
    @staticmethod
    def DrawImage(image_path: str):
        labelImage = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(image_path)
        pixmap_small = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        labelImage.setPixmap(pixmap_small)
        # pic_layout = QtWidgets.QHBoxLayout()
        # pic_layout.addWidget(labelImage)
        # pic_layout.setAlignment(QtCore.Qt.AlignLeft)

        return labelImage

    @staticmethod
    def IconFromSvg(svg_path: str):
        labelImage = QtWidgets.QLabel()
        svg_renderer = QtSvg.QSvgRenderer(svg_path)
        image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.darkGreen)
        svg_renderer.render(QtGui.QPainter(image))
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap_small = pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio)
        labelImage.setPixmap(pixmap)

        return labelImage

    @staticmethod
    def SvgIcon(img_path: str):
        svg_widg = QtSvg.QSvgWidget()
        svg_widg.load(img_path)
        svg_widg.setStyleSheet(
            """ 
            background-color: transparent;
            border: none;
            fill: white;
            color: white;
            """
        )
        svg_widg.setFixedSize(QtCore.QSize(20, 20))

        return svg_widg

    @staticmethod
    def IconToShow(filepath: str):

        # self.ListOfItems = []
        cur_path = os.path.dirname(os.path.realpath(__file__))
        houdini_svg = os.path.join(cur_path, "../../../config/icons/houdini.svg")
        nuke_svg = os.path.join(cur_path, "../../../config/icons/nuke.svg")
        maya_svg = os.path.join(cur_path, "../../../config/icons/maya.svg")
        blender_svg = os.path.join(cur_path, "../../../config/icons/blender.svg")

        HouSvg = DrawingMethods.SvgIcon(houdini_svg)
        NukeSvg = DrawingMethods.SvgIcon(nuke_svg)
        MayaSvg = DrawingMethods.SvgIcon(maya_svg)
        BlenderSvg = DrawingMethods.SvgIcon(blender_svg)

        print(filepath.split(".")[-1])

        if "hip" in filepath.split(".")[-1]:
            return HouSvg
        elif "nk" in filepath.split(".")[-1]:
            return NukeSvg
        elif "ma" in filepath.split(".")[-1]:
            return MayaSvg
        elif "blend" in filepath.split(".")[-1]:
            return BlenderSvg

    @staticmethod
    def PixmapFromIcon(icon: QtGui.QIcon):
        pixmap = icon.pixmap(16, 16)
        pix_of_ic = QtGui.QPixmap(pixmap)
        ItemTypeIcon = QtWidgets.QLabel()
        ItemTypeIcon.setPixmap(pix_of_ic)
        ItemTypeIcon.setStyleSheet(
            """ 
            background-color: transparent;
            """
        )
        ItemTypeIcon.setAlignment(QtCore.Qt.AlignLeft)
        return ItemTypeIcon

    #### LIST HANDLING #####
    @staticmethod
    # update call functions
    def AddSelToList(ListWidget: QtWidgets.QListWidget, info: str):
        message = QtWidgets.QListWidgetItem(info)
        ListWidget.addItem(message)
    



class GuiInfoMethods:
    @staticmethod
    def GetResolution():
        temporary_app = QtWidgets.QApplication
        screen = temporary_app.primaryScreen()
        geo = screen.availableGeometry()

        return (geo.width(), geo.height())

    @staticmethod
    def GetText(parent):
        if parent is not None:
            return parent.text()
        else:
            return "Empty"