from PySide2 import QtGui, QtWidgets, QtCore, QtSvg
from gui_methods import *
import os


class cuDropList(QtWidgets.QListWidget):

    nodesDropped = QtCore.Signal(bytes)

    def __init__(self, parent=None):
        super(cuDropList, self).__init__(parent)
        self.setAcceptDrops(False)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # str = event.mimeData().text()
        # print(str)
        print("Dropping is working")
        mime_data = event.mimeData()
        # Check if a node path was dropped.
        data = mime_data.data(hou.qt.mimeType.nodePath)
        if not data.isEmpty():
            print(data)
            string_data = str(data)
            print(string_data)
            # string_data.decode("UTF-8")
            # node_paths = string_data.split("\\t")
            # print(node_paths)
            event.setDropAction(QtCore.Qt.CopyAction)
            # event.accept()
            # links = []
            # links.append(node_path)
            self.nodesDropped.emit(data)
            # print(node_paths)
            event.acceptProposedAction()

        else:
            event.ignore()


class DropListItemLayout(QtWidgets.QWidget):
    def __init__(self, node_path: str, uuid: str, parent=None):
        super(DropListItemLayout, self).__init__()

        Framing = QtWidgets.QFrame()
        # self.setObjectName("HoudiniDropListLayout")
        box = QtWidgets.QHBoxLayout()

        self.dlo_info = DropListObjectInfo(uuid)
        self.job_path = self.dlo_info.GetFileType()
        self.internal = self.dlo_info.IsLocal(node_path)

        self.ItemIcon = DrawingMethods.IconToShow(os.path.basename(self.job_path))

        self.uuid = uuid

        self.item_type = self.dlo_info.GetNodeType(node_path)
        self.node_name = node_path.split("/")[-1]
        self.node_path = node_path

        self.InfoGridLayout = QtWidgets.QGridLayout()

        self.InfoGridLayout.setSpacing(10)

        self.InfoGridLayout.addWidget(self.ItemIcon, 0, 0)

        self.InfoBox = QtWidgets.QWidget()
        self.NodeAndIcon = QtWidgets.QHBoxLayout()

        self.newItemLabel = QtWidgets.QLabel(self.node_name)

        self.NodeAndIcon.addWidget(self.newItemLabel)
        self.InfoBox.setLayout(self.NodeAndIcon)
        self.InfoBox.setStyleSheet("background-color: transparent;")

        self.widg_cmds = [None, None, None, None]

        self.ItemDict = {
            "ifd": self.MantraItem,
            "arnold": self.ArnoldItem,
            "opengl": self.OpenGlItem,
            "filecache": self.MantraItem,
            "usdexport": self.MantraItem,
            "hammer::fbx_export::1.0": self.OpenGlItem,
            "rop_alembic": self.MantraItem,
            "rop_gltf": self.OpenGlItem,
            "topnet": self.MantraItem,
        }
        # Generate dropwidget based on dropped node type
        self.ItemDict[self.item_type]()

        self.setLayout(self.InfoGridLayout)

        # Check if in another file or current file
        self.InternalOrNot()

        StylingMethods.CleanupWidgets(self.widg_cmds)

        # self.setStyleSheet(f""" background-color: green;""")

    """
    DropListItem Operators
    """

    # def GenerateItem(self,type_name: str):
    #     self.ItemDict[type_name]()

    def StyleSwitcher(self, base: str, cooked: str, rendered: str):
        print("Style Thingy Happening")
        self.setStyleSheet(f""" background-color: {base}; """)

        if self.dlo_info.GetCookStatus():
            self.setStyleSheet(f""" background-color: {cooked}; """)
            # print(newItemWidget.layout().findChild(QtWidgets.QLabel, node))
        elif self.dlo_info.GetRenderStatus():
            self.setStyleSheet(f""" background-color: {rendered}; """)
        else:
            self.setStyleSheet(
                f"""QWidget#HoudiniDropListLayout {{ background-color: {base} }} """
            )

    def InternalOrNot(self):
        if self.internal:
            self.newItemLabel.setText(self.node_name)
            print(ColorLayout.ext_base.value)
            self.StyleSwitcher(
                ColorLayout.base.value,
                ColorLayout.cooked.value,
                ColorLayout.rendered.value,
            )
        else:
            self.newItemLabel.setText(self.node_name + " (External)")
            self.StyleSwitcher(
                ColorLayout.ext_base.value,
                ColorLayout.ext_cooked.value,
                ColorLayout.ext_rendered.value,
            )

    """
    DropListItem Generics
    """

    def BakableMethod(self):

        print("BAKABLE HAPPENING!!!! FOOFOOFOFOFOOOOO")

        newItemBakeChecker = QtWidgets.QCheckBox("Tops")
        newItemBakeChecker.setChecked(False)
        newItemTractorChecker = QtWidgets.QCheckBox("Tractor")

        newItemBakeChecker.toggle()
        newItemBakeChecker.stateChanged.connect(
            lambda: BooleanMethods.WidgetBlockOnCheck(
                newItemTractorChecker, newItemBakeChecker.isChecked()
            )
        )

        self.InfoGridLayout.addWidget(self.InfoBox, 0, 1)
        self.InfoGridLayout.addWidget(newItemBakeChecker, 0, 2)
        self.InfoGridLayout.addWidget(newItemTractorChecker, 0, 3)

        return newItemBakeChecker, newItemTractorChecker

    """
    DropListItem Types
    """

    def MantraItem(self):

        m_ico = DrawingMethods.PixmapFromIcon(mantra_render())
        self.NodeAndIcon.addWidget(m_ico)

        bake, tractor = self.BakableMethod()

        self.widg_cmds = [
            self.newItemLabel,
            bake,
            tractor,
            None,
        ]

    def OpenGlItem(self):
        ogl_ico = DrawingMethods.PixmapFromIcon(ogl_render())
        self.NodeAndIcon.addWidget(ogl_ico)

        self.InfoGridLayout.addWidget(self.InfoBox, 0, 1)

        self.widg_cmds = [self.newItemLabel, None, None, None]

    def ArnoldItem(self):
        m_ico = DrawingMethods.PixmapFromIcon(render())
        self.NodeAndIcon.addWidget(m_ico)

        bake, tractor = self.BakableMethod()

        ItemDescription = QtWidgets.QComboBox()
        # self.blades.setStyleSheet(widget_stylesheet)
        DescriptionOpts = ["Animated", "Light-Only", "Static"]

        for opt in DescriptionOpts:
            ItemDescription.addItem(opt)
        ItemDescription.setCurrentIndex(0)

        self.InfoGridLayout.addWidget(ItemDescription, 0, 4)

        self.widg_cmds = [
            self.newItemLabel,
            bake,
            tractor,
            ItemDescription,
        ]
