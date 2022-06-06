from sqlite3 import dbapi2
# import hou
import sys
import os
import platform
from uuid import uuid4, UUID
import shutil

from PySide2 import QtGui, QtWidgets, QtCore, QtSvg
from collections import OrderedDict
import json

# from submitter import Spool
from time import sleep

from errno import ESRCH


from Utils.makers import (
    CreationMethods,
    NumberMethods,
    ExecuteMethods,
)
from db_methods import MethodsDB, ProjectInfoRetriever
from gui_methods import (
    BooleanMethods,
    DrawingMethods,
    DropListObjectInfo,
    GuiInfoMethods,
    StylingMethods,
)
from gui_objects import cuDropList, DropListItemLayout

# from .houdini_methods import TopManagingMethods, ExportTypes
from submission_methods import HoudiniSubmissionMethods

# from .hou_buttons import *


## ------------------------------------------------------------- ##
sys.path.insert(1, os.path.join(sys.path[0], "blade-modules"))
## ------------------------------------------------------------- ##

# Creates the dialog box
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        x, y = GuiInfoMethods.GetResolution()
        left = QtCore.Qt.AlignLeft
        right = QtCore.Qt.AlignRight
        up = QtCore.Qt.AlignTop
        down = QtCore.Qt.AlignRight

        if x > 1920 and y > 1080:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            QtWidgets.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        else:
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_EnableHighDpiScaling, False
            )
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, False)

        stylesheet = hou.qt.styleSheet()

        self.setWindowTitle("Tractor Export Manager")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # self.setSizePolicy(sizePolicy)

        # create a style guide for the layout colors
        self.setStyleSheet(stylesheet)

        ###### SETUP THE TIMER #######
        # self.Timer = QtCore.QTimer()
        # self.Timer.timeout.connect(self.FlushAndRebuild)

        ###### Image PATHS #######
        cur_dir = os.path.dirname(__file__)
        self.ugly_tractor = "{}/../../../config/Icons/ugly_tractor.jpg".format(cur_dir)
        self.tractor_image = "{}/../../../config/Icons/TractorRenderSpool.png".format(
            cur_dir
        )

        self.home = os.path.expanduser("")

        ###### Initiate DB Class #######
        self.Database = MethodsDB()

        ################ Draw MAIN MENU ################

        self.menuwidget = QtWidgets.QWidget()

        self.splashbox = QtWidgets.QHBoxLayout()
        self.menubox = QtWidgets.QVBoxLayout()

        ####################################################
        ###############  SPLASH BOX WIDGET #################
        ####################################################
        self.initbox = QtWidgets.QVBoxLayout()

        self.setupbox = QtWidgets.QHBoxLayout()
        self.projectinfobox = QtWidgets.QGridLayout()

        self.new_project_bt = QtWidgets.QPushButton("Set Project")
        self.load_project_bt = QtWidgets.QPushButton("Load Project")

        self.projectname_lbl = QtWidgets.QLabel("PROJECT NAME:")
        self.projectname_lbl.setAlignment(right)
        self.projectname_widg = QtWidgets.QLabel("No Project Loaded")

        StylingMethods.SetLabelStyle(self.projectname_widg, True)

        self.projectname_widg.setAlignment(left)
        self.projectname_widg.setMaximumWidth(500)

        self.projectname = self.projectname_widg.text()

        self.new_project_bt.clicked.connect(self.SetProject)
        self.load_project_bt.clicked.connect(self.LoadProject)
        """
        Little Autocomplete test
        """
        self.crew_suggestions = [
            "patxi.aguirre@hslu.ch",
            "jean.first@hslu.ch",
            "juergen.haas@hslu.ch",
            "jochen.ehmann@hslu.ch",
            "gerd.gockel@hslu.ch",
            "procedural.godart@gmail.com",
            "paxigalaxi@gmail.com",
        ]

        completer = QtWidgets.QCompleter(self.crew_suggestions)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCurrentRow

        self.crew_lbl = QtWidgets.QLabel("E-MAILS:")
        self.crew_lbl.setAlignment(right)
        self.crew_widg = QtWidgets.QLineEdit()
        self.crew_widg.setAlignment(left)
        self.crew_widg.setMaximumWidth(500)

        self.crew_widg.setCompleter(completer)

        self.projectinfobox.addWidget(self.projectname_lbl, 0, 0)
        self.projectinfobox.addWidget(self.projectname_widg, 0, 1)

        self.projectinfobox.addWidget(self.crew_lbl, 1, 0)
        self.projectinfobox.addWidget(self.crew_widg, 1, 1)

        self.setupbox.addStretch(1)
        self.setupbox.addWidget(self.new_project_bt)
        self.setupbox.addWidget(self.load_project_bt)
        self.setupbox.setAlignment(left)

        self.initbox.addLayout(self.projectinfobox)
        self.initbox.addLayout(self.setupbox)

        splash_img = DrawingMethods.DrawImage(self.tractor_image)
        self.splashbox.addWidget(splash_img)
        self.splashbox.addLayout(self.initbox)
        # self.splashbox.setAlignment(right)
        # self.splashbox.addStretch()

        # self.splashbox.insertStretch(1, 1)

        ####################################################
        ##############  PROJECT BOX WIDGET #################
        ####################################################

        self.projectbox = QtWidgets.QVBoxLayout()
        self.linebox = QtWidgets.QHBoxLayout()

        self.sequencename = QtWidgets.QLineEdit("SEQUENCE NAME")
        self.sequencebutton = QtWidgets.QPushButton("ADD")
        self.delete_sequence = QtWidgets.QPushButton()
        self.delete_sequence.setIcon(
            self.style().standardIcon(getattr(QtWidgets.QStyle, "SP_TrashIcon"))
        )

        self.linebox.addWidget(self.sequencename)
        self.linebox.addWidget(self.sequencebutton)
        self.linebox.addWidget(self.delete_sequence)

        self.ProjectList = QtWidgets.QTreeWidget()
        self.ProjectList.setColumnCount(1)
        self.ProjectList.setHeaderHidden(True)

        self.projectbox.addLayout(self.linebox)
        self.projectbox.addWidget(self.ProjectList)

        ###############
        ## DATA FLOW ##
        ###############

        self.BranchArray = []
        self.BranchDict = {}

        # self.ShotArray = []
        ##############
        # Acces Data #
        ##############
        self.ProjectData = {}

        ##############
        # Acces Info #
        ##############
        self.ProjectDataInfo = []

        #############
        #  MAX IDS  #
        #############

        self.max_seq = None
        self.max_shot = None
        # self.max_nodes = None

        ## DRAW THE MENU ##

        self.menubox.addLayout(self.splashbox)

        #### DRAW PROJECTBOX ####
        self.menubox.addLayout(self.projectbox)

        #############      ###############
        ##### SET MENU COMPONENTS ########
        ##################################
        self.tab_widgets = ProjectTabs(
            self.ProjectData, self.ProjectDataInfo, self.ProjectList,
        )

        self.DroppedWidgetList = {}

        self.menuwidget.setLayout(self.menubox)
        self.widget_box = QtWidgets.QHBoxLayout()
        self.widget_box.addWidget(self.menuwidget)

        self.setMenuWidget(self.menuwidget)
        self.setCentralWidget(self.tab_widgets)

        ###################################################
        ############### PROJECT BUTTONS ###################
        ###################################################
        self.sequencebutton.clicked.connect(self.AddSequence)

        self.delete_sequence.clicked.connect(
            lambda: self.RemoveSelectedSequence(self.ProjectList.currentItem())
        )

        # connect the touching of lines to the same function
        self.ProjectList.itemClicked.connect(self.UnlockSequenceButtons)

        self.ProjectList.itemClicked.connect(
            lambda: self.SequenceChildSelected(self.ProjectList.currentItem())
        )

        ## INITIATE THE PROJECT BASED ON THE DATABASE ##

        self.InitProject()

    # Project History Handling

    def InitProject(self):

        db_path = ProjectInfoRetriever.GetProject()

        if db_path:
            if self.Database.CheckConn():
                self.Database.CloseConnection()

            self.GetMaxIDs()

            db_path_basename = os.path.basename(db_path).split(".proj")[0]
            print(db_path_basename)

            self.Database.LoadDB(db_path)

            self.tab_widgets.InitDB(db_path)

            self.projectname_widg.setText(db_path_basename)

            StylingMethods.SetLabelStyle(self.projectname_widg, False)

            # REGENERATE THE PROJECT DATA FROM THE DATABASE
            self.Rebuild()
            self.tab_widgets.HideAllItems()

            # self.tab_widgets.Make

        else:
            self.projectname_widg.setText("No Project Loaded")
            StylingMethods.SetLabelStyle(self.projectname_widg, True)

    def GetMaxIDs(self):

        self.max_seq = self.Database.GetSequenceMaxId()
        print(f"The Maximum Sequence ID is currently: {self.max_seq}")
        self.max_shot = self.Database.GetShotMaxId()
        print(f"The Maximum Shot ID is currently: {self.max_shot}")
        # self.max_nodes = self.Database.GetJobMaxId()
        # print(f"The Maximum Job ID is currently: {self.max_nodes}")

    def Rebuild(self):
        Fetched_Sequences = self.Database.FetchAllSequences()
        Fetched_Shots = self.Database.FetchAllShots()
        Fetched_Nodes = self.Database.FetchAllJobs()
        Fetched_Job_History = self.Database.FetchAllJobHistory()

        self.RebuildCascade(
            Fetched_Sequences, Fetched_Shots, Fetched_Nodes, Fetched_Job_History
        )

    def RebuildCascade(self, sequence_list, shot_list, node_list, node_history):
        """
        acces the widget by storing it in a temporary array
        """
        t_widg = []

        """
        Establish a list of of node_list elements and arrange them in a way 
        that allows to collect all dropped shots by uuid
        """
        nps_list = [(n[1], [n[2], n[-1]]) for n in node_list]

        """
        Start Recreation Cascade
        """
        for i, seq_id in enumerate(sequence_list):
            seq_widg = self.AddSequenceWidget(seq_id[1])
            t_widg.append(seq_widg)
            self.AddSequenceToDict(seq_id[0], seq_id[1])

            cur_seq_shots = self.Database.FetchAllShotsBySequence(seq_id[0])

            print(cur_seq_shots)
            if len(cur_seq_shots) >= 1:
                for shot_tuple in cur_seq_shots:
                    cur_seq_widg = t_widg[i]
                    new_shot, sequence_parent = self.AddShotToSequence(cur_seq_widg)

                    parent_index = self.ProjectList.indexOfTopLevelItem(sequence_parent)

                    shot_nodes_d = self.AddShotToDict(
                        shot_tuple[0], parent_index, new_shot
                    )

                    cur_shot_jobs = self.Database.FetchAllJobsByShot(shot_tuple[0])
                    print(cur_shot_jobs)

                    if len(cur_shot_jobs) >= 1:
                        for shot_job in cur_shot_jobs:
                            shot_nodes_d[shot_job[1]] = [shot_tuple[0], shot_job[2]]
        try:
            for history in node_history:
                self.tab_widgets.ReloadNodeHistory(
                    history[1], history[2], history[3], history[5], history[6],
                )
                self.tab_widgets.DropWidgetCreation(history[1], history[2])
                self.tab_widgets.MakeOnlyShotNodesVisible(shot_nodes_d)

                if hou.node(history[2]) and hou.node(history[2]).userData("uuid"):
                    if hou.node(history[2]).userData("uuid") == history[1]:
                        hou.node(history[2]).addEventCallback(
                            (
                                hou.nodeEventType.NameChanged,
                                hou.nodeEventType.BeingDeleted,
                            ),
                            self.tab_widgets.NodeChangeCallback,
                        )

        except Exception as e:
            print(e)
            pass

        self.tab_widgets.max_nodes = self.Database.GetJobMaxId()
        self.tab_widgets.max_history = self.Database.GetJobHistoryMaxId()
        self.ProjectDataInfo = self.tab_widgets.ReturnProjectDataInfo()
        self.DroppedWidgetList = self.tab_widgets.ReturnDroppedWidgetList()

    def FlushCurrentHistory(self):
        """
        Removes all items from the project list and the shot list
        """
        self.ProjectList.clear()
        # self.ShotArray = []
        # self.max_seq = 0
        self.BranchArray = []
        self.BranchDict = {}
        self.ProjectData = {}
        self.ProjectDataInfo = []

        self.tab_widgets.DropListWidget.clear()
        self.tab_widgets.DroppedWidgetList = {}
        self.tab_widgets.ProjectData = {}
        self.tab_widgets.ProjectDataInfo = []
        self.tab_widgets.NodeHistoryList = {}

        self.tab_widgets.DroppedWidgetList = {}
        self.tab_widgets.NodePropertyWidgets = {}

        self.tab_widgets.GraphId = {}

    def FlushAndRebuild(self):
        self.FlushCurrentHistory()
        self.Rebuild()

    def CheckForNewContentInDatabase(self):
        pass

    def SetProject(self):
        """
        This function will save the current project in the database.
        """
        ################################################################
        ############### SAVE THE PROJECT IN THE DATABASE ###############
        ################################################################

        Dialog = QtWidgets.QFileDialog()
        input_path = Dialog.getSaveFileUrl(
            None, "Select a file:", os.path.expanduser("~"), "*.proj",
        )
        # get the stored path from input_path
        input_dir = input_path[0].toLocalFile()
        saved_name = os.path.basename(input_dir).split(".proj")[0]

        print("THIS IS WHERE THE FILE IS STORED:", input_dir)

        if Dialog.Accepted and saved_name:

            self.ProjectFileHistory(input_dir)
            db_path = ProjectInfoRetriever.GetProject()
            # print(input_dir)
            ############### INITIATE DATABASE #################
            try:
                if db_path:
                    if self.Database.CheckConn():
                        self.Database.CloseConnection()

                self.Database.CreateDB(input_dir)

                self.tab_widgets.InitDB(input_dir)

                self.GetMaxIDs()

                self.FlushCurrentHistory()

                self.Rebuild()

                self.projectname_widg.setText(saved_name)
                StylingMethods.SetLabelStyle(self.projectname_widg, False)

            except Exception as e:
                print(e)
                # raise

            ###################################################
            Dialog.close()
        else:
            print("Cancelled")
            Dialog.close()

    def LoadProject(self):
        """
        This function will load a project from the database.
        """
        ################################################################
        ############### LOAD A DIFFERENT PROJECT FROM THE DATABASE #####
        ################################################################
        Dialog = QtWidgets.QFileDialog()
        # Dialog.getOpenFileUrl and filter out any file that doesnt end with .proj
        input_path = Dialog.getOpenFileUrl(
            None, "Select a .proj File:", os.path.expanduser("~"), "*.proj",
        )
        # get the stored path from input_path
        input_dir = input_path[0].toLocalFile()
        saved_name = os.path.basename(input_dir).split(".proj")[0]

        if Dialog.Accepted and saved_name:

            self.ProjectFileHistory(input_dir)
            db_path = ProjectInfoRetriever.GetProject()

            ############### Load DATABASE #################
            try:
                if db_path:
                    if self.Database.CheckConn():
                        self.Database.CloseConnection()

                self.Database.LoadDB(input_dir)
                self.tab_widgets.InitDB(input_dir)

                self.GetMaxIDs()

                self.FlushCurrentHistory()

                self.Rebuild()

                self.projectname_widg.setText(saved_name)
                StylingMethods.SetLabelStyle(self.projectname_widg, False)

            except Exception as e:
                print(e)
                # raise

            ###################################################
            Dialog.close()
        else:
            print("Cancelled")
            Dialog.close()

    def ProjectFileHistory(self, projectpath):
        """
        Store the information of the currently saved or loaded project in a file
        """
        path_to_store_info = os.path.join(
            os.path.expanduser("~"), ".active_hslu_project"
        )

        if os.path.exists(path_to_store_info):
            shutil.rmtree(path_to_store_info)

        CreationMethods.makedir(path_to_store_info)
        file_to_store = os.path.join(path_to_store_info, "project_history.txt")
        with open(file_to_store, "w") as f:
            f.write(f"{projectpath}")

        return file_to_store

    # USER DATA RETRIEVERS

    def SequenceIndex(self):
        return self.ProjectList.indexOfTopLevelItem(self.ProjectList.currentItem())

    """ 
    SEQUENCE ADDITION AND DELETION
    """

    def AddSequence(self):
        print("This is the first ProjectdataInfo:", self.ProjectDataInfo)
        if self.max_seq:
            self.max_seq += 1
        else:
            self.max_seq = 1

        self.AddSequenceWidget(self.sequencename.text())
        self.AddSequenceToDict(self.max_seq, self.sequencename.text())
        self.AddSequenceToDB(self.max_seq, self.sequencename.text())

        # self.FlushAndRebuild()

        # self.FlushAndRebuild()

    def AddSequenceWidget(self, sequence_name):

        treebranch_container = QtWidgets.QWidget()
        treebranchbox = QtWidgets.QHBoxLayout()
        sequence_label = QtWidgets.QLabel(sequence_name)
        add_scene_button = QtWidgets.QPushButton("+")
        add_scene_button.setEnabled(True)
        add_scene_button.setFixedSize(22, 22)
        remove_scene_button = QtWidgets.QPushButton("-")
        remove_scene_button.setFixedSize(22, 22)
        remove_scene_button.setEnabled(True)
        treebranchbox.addWidget(sequence_label)
        treebranchbox.addWidget(add_scene_button)
        treebranchbox.addWidget(remove_scene_button)
        treebranch_container.setLayout(treebranchbox)

        treebranch = QtWidgets.QTreeWidgetItem()

        # self.treebranch.setText(1,'WTF')
        self.ProjectList.addTopLevelItem(treebranch)
        self.ProjectList.setItemWidget(treebranch, 0, treebranch_container)

        """
        Add and Remove functionality
        """
        self.BranchDict[treebranch] = [
            add_scene_button,
            remove_scene_button,
        ]
        self.BranchArray.append(self.BranchDict)

        for tb in list(self.BranchDict.keys()):
            tb.setSelected(False)

        treebranch.setSelected(True)

        self.ProjectList.setCurrentItem(treebranch)
        """
        After selecting the generated project run the unlock function to lock all buttons 
        but the ones on the selected branch
        """
        self.UnlockSequenceButtons()

        add_scene_button.clicked.connect(self.AddShot)

        # ShotDict = {}
        # ShotDict[self.treebranch] = []
        # self.ShotArray.append(ShotDict)

        """
        Here the two different types of Data are given.
        One to give on functionality
        The other to retrieve and store state-information
        """
        self.ProjectData[treebranch] = []

        # treebranch_name = GuiInfoMethods.GetText(self.treebranch)
        return treebranch

    def AddSequenceToDict(self, id, sequence_name):
        print("This is happening")
        """
        Every new sequence info group has the name of the sequence and a dict to identify the scene later
        """
        # we keep the size constant by first measuring max size of database and then adding the new item to the size
        NewSequenceGroup = (sequence_name, id, {})
        self.ProjectDataInfo.append(NewSequenceGroup)
        print("This is all of ProjectdataInfo: ", self.ProjectDataInfo)
        # print(self.ProjectDataInfo)

    def AddSequenceToDB(self, id, sequence_name):

        # DATABASE HANDLING
        db_path = ProjectInfoRetriever.GetProject()
        # we keep the size constant by first measuring max size of database and then adding the new item to the size
        DB_SeqGroup = (id, sequence_name)

        if db_path:
            if self.Database.CheckConn():
                self.Database.InsertSequenceDB(DB_SeqGroup)
            else:
                self.Database.LoadDB(db_path)
                self.Database.InsertSequenceDB(DB_SeqGroup)

        # self.SequenceNamesUpdater(project_name)

    def UpdateProjectDataInfo(self, parent):

        del self.ProjectDataInfo[parent]

        # size = self.ProjectList.topLevelItemCount()
        """
        Perform this operation only if the currently deleted item is not the last selected one
        """
        # if self.SequenceIndex() + 1 < size:
        """
        Check if number of sequence is larger than the index of the current listitem
        and substract an index from it.
        """
        # for i, seq_info in enumerate(self.ProjectDataInfo):
        #     cur_size = i + 1
        #     if cur_size > parent:
        #         # print(cur_size, " ... ", parent)
        #         print("This is the seq info before\n")
        #         print(seq_info)

        #         seq_info_conv = list(seq_info)
        #         seq_info_conv[1] -= 1
        #         seq_info = tuple(seq_info_conv)
        #         self.ProjectDataInfo[i] = seq_info

        #         print("This is the seq info afterwards\n")
        #         print(seq_info)

        # print(self.SequenceNames)

    def RemoveSelectedSequence(self, parent):
        try:
            # self.UpdateIndexOfSequenceNamesList(self.SequenceIndex())
            cur_proj_index = self.ProjectDataInfo[self.SequenceIndex()][1]
            cur_shot_index = self.ProjectDataInfo[self.SequenceIndex()][2]
            print(f"{cur_proj_index} index deleted")
            # we use the stored index to delete the sequence from the database

            all_shots_to_delete = self.Database.FetchAllShotsBySequence(cur_proj_index)

            for shot_tuple in all_shots_to_delete:
                all_jobs_to_delete = self.Database.FetchAllJobsByShot(shot_tuple[0])
                self.Database.RemoveJobGroupFromDB(shot_tuple[0])

                for job_t in all_jobs_to_delete:
                    uuid = job_t[1]
                    all_jobs_of_uuid = self.Database.FetchAllJobsByUUID(uuid)
                    print(f"These are all jobs of {uuid}: {all_jobs_of_uuid}")
                    if len(all_jobs_of_uuid) == 0:
                        self.Database.RemoveJobHistoryByUUID(uuid)
                        del self.tab_widgets.NodeHistoryList[uuid]

            self.Database.RemoveShotGroupFromDB(cur_proj_index)
            self.Database.RemoveSequenceFromDB(cur_proj_index)

            self.UpdateProjectDataInfo(self.SequenceIndex())

            self.ProjectList.takeTopLevelItem(self.SequenceIndex())

            self.tab_widgets.UpdateMaxJobID()
            self.tab_widgets.UpdateMaxHistoryID()

            # self.FlushAndRebuild()
            try:
                self.ProjectList.setItemSelected(
                    self.ProjectList.topLevelItem(self.SequenceIndex()), False
                )
            except:
                pass

            # parent.removeChild(parent)
            print("working...")
            del self.BranchDict[parent]

            # del self.ShotArray[self.SequenceIndex()]

            del self.ProjectData[parent]

            print("The Sequence Index deleted \n")
            print(self.SequenceIndex())

            print("You deleted a Sequence and these are the current ones:\n")
            print(self.ProjectDataInfo)

        except Exception as e:
            print(e)
            # treenum = self.ProjectList.indexOfTopLevelItem(parent)
            # print(treenum)
            print("No Tree to remove")
            pass

    def ProjectSelection(self):
        print(self.ProjectList.currentItem().isSelected())

        # cur_button.setEnabled(True)

    def UnlockSequenceButtons(self):
        try:
            for treebranch in self.BranchDict:
                self.BranchDict[treebranch][0].setEnabled(False)
                self.BranchDict[treebranch][1].setEnabled(False)

            cur_plus_button = self.BranchDict[self.ProjectList.currentItem()][0]
            cur_min_button = self.BranchDict[self.ProjectList.currentItem()][1]

            cur_plus_button.setEnabled(True)
            cur_min_button.setEnabled(True)

        except:
            print("There are currently no other buttons")

    """
    SHOT TO SEQUENCE ADDITION
    """

    def AddShot(self):

        if self.max_shot:
            self.max_shot += 1
        else:
            self.max_shot = 1

        print(f"This is happening: {self.max_shot} added")

        new_shot, sequence_parent = self.AddShotToSequence(
            self.ProjectList.currentItem()
        )

        parent_index = self.ProjectList.indexOfTopLevelItem(sequence_parent)
        print(f"Shot to Parent with THIS INDEX: {parent_index} added")

        self.AddShotToDict(self.max_shot, parent_index, new_shot)
        """
        AddShotToSequence returns a shot object that we can use to retrieve infromation
        """
        self.AddShotToDB(self.max_shot, new_shot)

    def AddShotToSequence(self, parent: QtWidgets.QTreeWidgetItem):
        num_shotwidgets = parent.childCount()

        # for treebranch in self.BranchDict:
        #     if treebranch is parent and treebranch.isSelected():
        shotwidget = QtWidgets.QTreeWidgetItem()
        shotwidget.setText(0, "SHOT_{}".format(NumberMethods.add_one(num_shotwidgets)))

        parent.addChild(shotwidget)

        print(f"{shotwidget.text(0)} added to {parent}")

        return shotwidget, parent

    def AddShotToDict(
        self, shot_id: int, seq_index: int, shotwidget: QtWidgets.QTreeWidgetItem,
    ):

        # self.ShotArray[self.SequenceIndex()][parent].append(shotwidget)

        """
        Similar to the process in the Main Function
        We create a dict of shot data to store the list of nodes in them
        And also create a ShotDataInfo Dict to be able to to store and regenerate the information
        """
        # ShotData = {}
        # ShotData[shotwidget] = []
        # self.ProjectData[parent].append(ShotData)

        """
        Add name of the shot to the dict of the corresponding sequence and make it contain a list
        To later add nodes, and node information to it.
        """

        """
        We identify the shot_id of the shot we are adding to the sequence and put it in a tuple with the dictof job_ids
        """

        print(shotwidget.text(0))
        self.ProjectDataInfo[seq_index][2][shotwidget.text(0)] = [shot_id, {}]

        # print(self.ProjectDataInfo)

        return self.ProjectDataInfo[seq_index][2][shotwidget.text(0)][1]

    def AddShotToDB(self, shot_id, shotwidget: QtWidgets.QTreeWidgetItem):
        db_path = ProjectInfoRetriever.GetProject()
        # total_shots = self.ReturnTotalShots()

        # cur_shots = list(self.ProjectDataInfo[self.SequenceIndex()][2].keys())

        cur_shot_name = shotwidget.text(0)
        cur_seq_id = self.ProjectDataInfo[self.SequenceIndex()][1]

        SH_SeqGroup = (shot_id, cur_shot_name, cur_seq_id)

        if db_path:
            if self.Database.CheckConn():
                """
                insert the shot into the table
                """
                self.Database.InsertShotDB(SH_SeqGroup)
            else:
                self.Database.LoadDB(db_path)
                self.Database.InsertShotDB(SH_SeqGroup)

    def ReturnTotalShots(self):
        total_shots = 0

        for sequence in self.ProjectDataInfo:
            total_shots += len(list(sequence[2].keys()))
        return total_shots

    def SequenceChildSelected(self, widget):

        self.tab_widgets.UpdateProject(
            self.projectname, self.ProjectData, self.ProjectDataInfo, self.ProjectList,
        )
        self.tab_widgets.max_nodes = self.Database.GetJobMaxId()
        print(
            f"These are max nodes in tab widgets seen from other class: {self.tab_widgets.max_nodes}"
        )
        self.ProjectDataInfo = self.tab_widgets.ReturnProjectDataInfo()
        self.DroppedWidgetList = self.tab_widgets.ReturnDroppedWidgetList()
        try:
            if widget.parent().__class__.__name__ == "QTreeWidgetItem":
                print("this is a Shot")
                # print(widget)
                cur_shot_nodes_info = self.tab_widgets.PreShotDrop(
                    self.ProjectDataInfo
                )[1]
                self.tab_widgets.DropActivation(True)

                # self.tab_widgets.HideAllItems(True)

                self.tab_widgets.MakeOnlyShotNodesVisible(cur_shot_nodes_info)

                # self.tab_widgets.DropsPerShot(self.ProjectData,self.ProjectList)

            else:
                print("This is currently a Sequence")
                print(self.SequenceIndex())
                # print(self.SequenceNames)
                self.tab_widgets.DropActivation(False)
                self.tab_widgets.HideAllItems()

        except Exception as e:
            print(e)
            print("No Shot in the Sequence!")
            raise


class ProjectTabs(QtWidgets.QWidget):

    finished = QtCore.Signal()

    def __init__(
        self,
        ProjectData: dict,
        ProjectDataInfo: dict,
        ProjectList: QtWidgets.QTreeWidget,
        *args,
        **kwargs,
    ):
        super(ProjectTabs, self).__init__(*args, **kwargs)

        """ 
        Base Vars
        """
        # self.projectname = ProjectName
        self.ProjectData = ProjectData
        self.ProjectDataInfo = ProjectDataInfo
        self.ProjectList = ProjectList
        self.Database = MethodsDB()
        # self.Database = Database

        self.max_nodes = None
        self.max_history = None

        """
        Accepted Node Types
        """
        self.selection = hou.selectedNodes()

        """
        Information Handling
        """

        self.DropListWidget = HoudiniList(self)
        self.DropListWidget.setStyleSheet(hou.qt.styleSheet())
        self.DropListWidget.itemClicked.connect(self.MakePropsTabVisible)
        self.DropListWidget.itemSelectionChanged.connect(self.MakePropsTabVisible)

        self.NodeHistoryList = {}

        self.DroppedWidgetList = {}
        self.NodePropertyWidgets = {}

        self.GraphId = {}

        self.execute_methods = ExecuteMethods()

        self.hip_file_name = hou.hipFile.basename()

        self.tab_container = QtWidgets.QTabWidget()

        self.initUI()

    def initUI(self):

        # The main layout for the window

        processing_tab = QtWidgets.QWidget()
        # self.submission_tab = QtWidgets.QWidget()

        processing_tab.setLayout(self.ProcessingTab())
        processing_tab.setStyleSheet(""" background-color: rgb(100, 100, 100, 255) """)
        # self.submission_tab.setLayout(self.SubmissionTab())

        self.tab_container.addTab(processing_tab, "NODES")
        # self.tab_container.addTab(self.submission_tab, "SUBMISSION PROPERTIES")
        # self.submission_tab.setHidden(True)
        ###SETUP TABS###
        tab_placement = QtWidgets.QHBoxLayout()
        tab_placement.addWidget(self.tab_container)

        self.setLayout(tab_placement)

    """
    Data Between Classes Update Handling
    """

    def InitDB(self, db_path):
        self.Database.LoadDB(db_path)

    def UpdateProject(
        self, ProjectName, ProjectData, ProjectDataInfo, ProjectList,
    ):
        self.projectname = ProjectName
        self.ProjectData = ProjectData
        self.ProjectDataInfo = ProjectDataInfo
        self.ProjectList = ProjectList

    def ReturnProjectDataInfo(self):
        return self.ProjectDataInfo

    def ReturnDroppedWidgetList(self):
        return self.DroppedWidgetList

    """
    Cook and Submission Tab
    """

    def SceneWidgetInfo(self):

        shot = self.ProjectList.currentItem()
        shot_name = shot.text(0)
        shot_parent_index = self.ProjectList.indexOfTopLevelItem(shot.parent())

        return shot_name, shot_parent_index

    def ProcessingTab(self):

        commandsbox = QtWidgets.QHBoxLayout()
        nodelistbox = QtWidgets.QVBoxLayout()

        processing_box = QtWidgets.QVBoxLayout()

        # data = hou.qt.mimeType.nodePath

        # self.DropListWidget.viewport().setAcceptDrops(True)
        self.DropListWidget.nodesDropped.connect(self.NodeDropper)
        self.DropListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # self.CookNodes = QtWidgets.QPushButton('')

        cookbutton = QtWidgets.QPushButton("Cook")
        cookbutton.setIcon(cook2())
        submitbutton = QtWidgets.QPushButton("Render with Tractor")
        submitbutton.setIcon(render())

        cookbutton.clicked.connect(lambda: self.ProcessNodes(True))
        submitbutton.clicked.connect(lambda: self.ProcessNodes(False))

        commandsbox.addWidget(cookbutton)
        commandsbox.addWidget(submitbutton)

        nodelistbox.addWidget(self.DropListWidget)

        processing_box.addLayout(commandsbox)
        processing_box.addLayout(nodelistbox)

        return processing_box

    """
    Cook Nodes Dropplist Widget Handling
    """

    def DropActivation(self, Bool):
        self.DropListWidget.setAcceptDrops(Bool)

    def UpdateDroppedWidgetList(self, uuid, item_widget, prop_tab_widget):
        self.DroppedWidgetList[uuid] = [item_widget, prop_tab_widget]

    def NodeDropper(self, l):
        # print(l)
        decoded_l = str(l, "utf-8")
        list_nodes = decoded_l.split("\t")
        print(list_nodes)
        cur_shot_nodes_info = self.PreShotDrop(self.ProjectDataInfo)[1]
        cur_shot_id = self.PreShotDrop(self.ProjectDataInfo)[0]
        print(f"Current shot ID is:{cur_shot_id}")
        for node in list_nodes:
            print(node)
            # decoded_node = bytes(node, encoding="utf8").decode("utf-8")
            cur_node_type = hou.node(node).type().name()

            if cur_node_type in ExportTypes():
                cur_dropped_id = self.CreateIdOnDrop(self.ProjectDataInfo, node)

                print("DROPPED NODE ID is:", cur_dropped_id)

                self.AddNodeToDB(cur_dropped_id, node, cur_shot_id)

            elif cur_node_type == "ropnet":
                for child_node in hou.node(node).allSubChildren():
                    if child_node.type().name() in ExportTypes():
                        cur_dropped_id = self.CreateIdOnDrop(
                            self.ProjectDataInfo, child_node.path()
                        )
                        self.AddNodeToDB(cur_dropped_id, child_node.path(), cur_shot_id)

            self.UpdateProject(
                self.projectname,
                self.ProjectData,
                self.ProjectDataInfo,
                self.ProjectList,
            )
            self.MakeOnlyShotNodesVisible(cur_shot_nodes_info)

    """
    ListWidgetItem Handling & Creation
    """

    def DropWidgetCreation(self, uuid, node):

        node_name = node.split("/")[-1]
        stored_node_history = self.Database.FetchAllJobHistory()

        newNodeItem = QtWidgets.QListWidgetItem()

        if hou.node(node):
            newTabProp = self.CreatePropertyTab(hou.node(node).type().name())
        else:
            if len(stored_node_history) >= 1:
                chosen_one = [n_h for n_h in stored_node_history if n_h[1] == uuid][0]
                newTabProp = self.CreatePropertyTab(chosen_one[4])
            else:
                newTabProp = self.CreatePropertyTab("unknown")

        newNodeLayout = HoudiniDropListLayout(node, uuid, self)
        self.NodePropertyWidgets[uuid] = newNodeLayout.widg_cmds

        newNodeItem.setSizeHint(newNodeLayout.sizeHint())

        self.UpdateDroppedWidgetList(uuid, newNodeItem, newTabProp)
        # self.ListOfItems.append(newNodeItem)

        """
        self.DropListWidget.itemClicked(newNodeItem).connect(self.debug)
        """
        self.DropListWidget.addItem(newNodeItem)
        self.DropListWidget.setItemWidget(newNodeItem, newNodeLayout)
        self.DropListWidget.setItemSelected(newNodeItem, False)
        print(self.DropListWidget.count())

    """
    ListWidgetItem to Node Methods
    """

    def ProcessNodes(self, no_cook=False):
        # Cook the nodes locall

        cur_shot_nodes_info = self.PreShotDrop(self.ProjectDataInfo)[1]
        ordered_cur_shot_nodes = OrderedDict(cur_shot_nodes_info.items())

        cook_locally = {}
        cook_remotely = {}

        if len(ordered_cur_shot_nodes) >= 1:
            for uuid, node_grp in ordered_cur_shot_nodes.items():
                node = node_grp[1]
                if hou.node(node) != None:
                    if hou.node(node).userData("uuid") == uuid:
                        if self.DroppedWidgetList[uuid][0].isSelected():
                            if hou.node(node).type().name() == "opengl":
                                if no_cook:
                                    print("opengl nodes dont get cooked")
                                    pass
                                else:
                                    print("Tried Submitting OpenGL Node")
                                    submission = HoudiniSubmissionMethods(
                                        hou.node(node)
                                    )
                                    submission.SingleSlaveJob()
                                    # submission.GuiDebugJob()
                            else:

                                if (
                                    self.NodePropertyWidgets[uuid][1].isChecked()
                                    and self.NodePropertyWidgets[uuid][2].isChecked()
                                    == False
                                ):
                                    cook_locally[uuid] = hou.node(node)

                                elif (
                                    self.NodePropertyWidgets[uuid][1].isChecked()
                                    and self.NodePropertyWidgets[uuid][2].isChecked()
                                ):
                                    cook_remotely[uuid] = hou.node(node)

        if len(cook_locally.keys()) >= 1:
            top_job = TopManagingMethods(cook_locally)
            if top_job.CreateTopGraphAndCook():
                for uuid, node in cook_locally.items():
                    self.Database.ChangeJobCookedByUUID(1, uuid)
                    StylingMethods.ChangeBgCol(
                        self.DroppedWidgetList[uuid][0], self.CookedCd
                    )

        if len(cook_remotely.keys()) >= 1:
            top_job = TopManagingMethods(cook_remotely)
            top_job.CreateTopGraphAndCook(tractor=True)

    """
    Node Visibility Handling
    """

    def HideNodeListItem(self, uuid):
        """
        The ListWidgetStays. The cur_shot_nodes_info gets deleted though.
        Important for later processing of node.
        """
        cur_shot_nodes_info = self.PreShotDrop(self.ProjectDataInfo)[1]
        del cur_shot_nodes_info[uuid]
        self.DroppedWidgetList[uuid][0].setHidden(True)

    def HideAllItems(self):
        if len(self.NodeHistoryList) >= 1:
            ordered_list_widgets = OrderedDict(self.DroppedWidgetList.items())
            for widget in ordered_list_widgets.values():
                widget[0].setHidden(True)
                widget[1].setHidden(True)
        else:
            pass

    def MakeOnlyShotNodesVisible(self, cur_shot_nodes_info):
        print(cur_shot_nodes_info)

        if len(cur_shot_nodes_info) == 0:
            self.HideAllItems()
        elif len(cur_shot_nodes_info) >= 1:
            ordered_current_nodes = OrderedDict(cur_shot_nodes_info.items())
            # ordered_nodes_history = OrderedDict(self.NodeHistoryList.items())
            ordered_list_widgets = OrderedDict(self.DroppedWidgetList.items())
            for lw_uuid, l_widget in ordered_list_widgets.items():
                cur_listwidget = l_widget[0]
                cur_propwidget = l_widget[1]
                cur_qmodel_index = self.DropListWidget.indexFromItem(cur_listwidget)
                row_index = cur_qmodel_index.row()
                print("Row Index: ", row_index)
                if lw_uuid in ordered_current_nodes.keys():
                    cur_listwidget.setHidden(False)
                    # self.DropListWidget.setRowHidden(row_index, False)
                else:
                    cur_listwidget.setHidden(True)
                    # self.DropListWidget.setRowHidden(row_index, True)

    """
    Info Dict of User Activity Handling
    """

    def PreShotDrop(self, ProjectDataInfo):
        shot_name, shot_parent_index = self.SceneWidgetInfo()
        cur_shot_nodes_info = ProjectDataInfo[shot_parent_index][2][shot_name]
        return cur_shot_nodes_info

    def MakeNodeHistory(self, node, id):
        """sent = False, cooked = False, present in scene = True"""
        self.NodeHistoryList[id] = [node, hou.hipFile.name(), False, False]

    def ReloadNodeHistory(self, id, node, hipfile, sent, cooked):
        """sent = False, cooked = False"""
        self.NodeHistoryList[id] = [
            node,
            hipfile,
            NumberMethods.IntToBool(sent),
            NumberMethods.IntToBool(cooked),
        ]

    """
    On Node Dropped/ Renamed Methods
    """

    def NodeChangeCallback(self, node, event_type, **kwargs):
        args = ["remove", "rename"]
        node_uuid = node.userData("uuid")
        stored_node_history = self.Database.FetchAllJobHistory()

        if len(stored_node_history) >= 1:
            for jh_t in stored_node_history:
                if node_uuid == jh_t[1]:

                    if event_type == hou.nodeEventType.BeingDeleted:

                        self.NodeHistoryList[node_uuid][4] = False
                        self.UpdateProjectDataInfo(
                            self.ProjectDataInfo, self.NodeHistoryList, args[0]
                        )

                    elif event_type == hou.nodeEventType.NameChanged:
                        # check if widgets exist and window is open
                        self.NodeHistoryList[node_uuid][0] = node.path()
                        self.UpdateProjectDataInfo(
                            self.ProjectDataInfo, self.NodeHistoryList, args[1]
                        )
                        self.ChangeLabelName(
                            node, self.NodePropertyWidgets[node_uuid][0]
                        )
                        # self.MakePropsTabVisible()

                        self.Database.ChangeJobNameByUUID(node.path(), node_uuid)
                        self.Database.ChangeJobHistoryNameByUUID(node.path(), node_uuid)

    def ChangeLabelName(self, node, widget):
        widget.setText(node.name())

    def AddIdToNode(self, dropped_node, uuid):
        node = hou.node(dropped_node)
        node.setUserData("uuid", str(uuid))

    def UpdateProjectDataInfo(self, ProjectDataInfo, NodeHistoryList, event_type):

        for seq in ProjectDataInfo:
            if len(seq[2]) > 0:
                for shot in seq[2]:
                    nodes_dict = seq[2][shot][1]
                    ordered_cur_nodes = OrderedDict(nodes_dict.items())
                    ordered_nodes_history = OrderedDict(NodeHistoryList.items())
                    if len(nodes_dict) >= 1:
                        for cur_uuid, node_path in ordered_cur_nodes.items():
                            for stored_uuid, shot_info in ordered_nodes_history.items():
                                if cur_uuid == stored_uuid:
                                    if event_type == "remove":
                                        del nodes_dict[cur_uuid]
                                    elif event_type == "rename":
                                        nodes_dict[cur_uuid][1] = shot_info[0]
        print(ProjectDataInfo)
        return ProjectDataInfo

    def UpdateMaxJobID(self):
        self.max_nodes = self.Database.GetJobMaxId()

    def UpdateMaxHistoryID(self):
        self.max_history = self.Database.GetJobHistoryMaxId()

    """
    Id per Dropped Node Handling
    """

    def CreateIdOnDrop(self, ProjectDataInfo, dropped_node):
        cur_shot_id = self.PreShotDrop(ProjectDataInfo)[0]
        cur_shot_nodes_info = self.PreShotDrop(ProjectDataInfo)[1]

        cur_dropped_node = dropped_node

        stored_node_history = self.Database.FetchAllJobHistory()

        sdn = self.Database.FetchAllJobs()
        sdn_ps = [(job[1], job[-1]) for job in sdn]

        dropped_tuple = (hou.node(cur_dropped_node).userData("uuid"), cur_shot_id)
        # cur_max_node = self.Database.GetJobMaxId() + 1

        for seq in ProjectDataInfo:
            if len(seq[2]) > 0:
                for shot in seq[2]:
                    # nodes_dict = seq[2][shot]

                    if (
                        hou.node(cur_dropped_node).userData("uuid")
                        and len(self.NodeHistoryList) >= 1
                    ):

                        """
                        If something gets dropped that is inside the node history.
                        Just add the old information to the cur_shot_nodes_info dict
                        To be processed later by the visibility handler
                        """

                        ordered_list_of_all_nodes = OrderedDict(
                            self.NodeHistoryList.items()
                        )
                        for old_uuid_tuple in stored_node_history:
                            old_uuid = old_uuid_tuple[1]
                            if old_uuid == hou.node(dropped_node).userData("uuid"):
                                cur_dropped_node = dropped_node
                                cur_dropped_id = old_uuid

                                cur_shot_nodes_info[cur_dropped_id] = [
                                    cur_shot_id,
                                    cur_dropped_node,
                                ]

                                # add to the nodes db
                                return old_uuid

                            elif self.CompareTupleInList(dropped_tuple, sdn_ps):

                                cur_dropped_node = dropped_node
                                new_old_uuid = hou.node(cur_dropped_node).userData(
                                    "uuid"
                                )

                                self.MakeNodeHistory(cur_dropped_node, new_old_uuid)

                                hou.node(cur_dropped_node).addEventCallback(
                                    (
                                        hou.nodeEventType.NameChanged,
                                        hou.nodeEventType.BeingDeleted,
                                    ),
                                    self.NodeChangeCallback,
                                )

                                cur_shot_nodes_info[new_old_uuid] = [
                                    cur_shot_id,
                                    cur_dropped_node,
                                ]

                                self.DropWidgetCreation(new_old_uuid, cur_dropped_node)

                                return new_old_uuid

                    elif (
                        hou.node(cur_dropped_node).userData("uuid")
                        and len(stored_node_history) == 0
                    ):
                        print("UNIQUE EVENT HAPPENING")
                        cur_dropped_node = dropped_node
                        new_old_uuid = hou.node(cur_dropped_node).userData("uuid")

                        self.MakeNodeHistory(cur_dropped_node, new_old_uuid)

                        hou.node(cur_dropped_node).addEventCallback(
                            (
                                hou.nodeEventType.NameChanged,
                                hou.nodeEventType.BeingDeleted,
                            ),
                            self.NodeChangeCallback,
                        )

                        cur_shot_nodes_info[new_old_uuid] = [
                            cur_shot_id,
                            cur_dropped_node,
                        ]

                        self.DropWidgetCreation(new_old_uuid, cur_dropped_node)

                        return new_old_uuid

                    else:

                        """
                        Else, create a new ID on the node and add it as a new key to the
                        cur_shot_node_info dict.
                        """
                        new_uuid = str(uuid4())
                        cur_dropped_id = new_uuid

                        self.MakeNodeHistory(cur_dropped_node, cur_dropped_id)
                        # print(hou.node(cur_dropped_node).userData("uuid"))

                        self.AddIdToNode(cur_dropped_node, cur_dropped_id)
                        hou.node(cur_dropped_node).addEventCallback(
                            (
                                hou.nodeEventType.NameChanged,
                                hou.nodeEventType.BeingDeleted,
                            ),
                            self.NodeChangeCallback,
                        )
                        self.DropWidgetCreation(cur_dropped_id, cur_dropped_node)

                        # TODO: Here is the mistake this is missing the shot_id
                        cur_shot_nodes_info[cur_dropped_id] = [
                            cur_shot_id,
                            cur_dropped_node,
                        ]

                        """
                        TODO: If a sequence or shot gets deleted. List has to be checked for existance of uuid >> node
                        if that node uuid doesnt exist anymore delete it from the userData property on the Node
                        """

                        return new_uuid

    """
    Databse Connection and Handling
    """

    def AddNodeToDB(self, cur_dropped_id, cur_dropped_node, shot_id):
        # only insert into Database if cur_dropped_id is not already with shot_id

        print(f"Max Nodes BEFORE Dropping No Reload:{self.max_nodes}")
        self.max_nodes = self.Database.GetJobMaxId()
        print(f"Max Nodes Before Dropping Reload:{self.max_nodes}")
        if cur_dropped_id:
            if self.max_nodes:
                try:
                    jobs = self.Database.FetchAllJobs()
                    print(f"These are currently all stored jobs: {jobs}")
                    nid_p_s = [(job[1], job[-1]) for job in jobs]
                    d_nid_p_s = dict(nid_p_s)
                    print(d_nid_p_s)

                    if cur_dropped_id in d_nid_p_s.keys():
                        if len(jobs) >= 1 and self.CompareTupleInList(
                            (cur_dropped_id, shot_id), nid_p_s
                        ):

                            self.max_nodes = self.Database.GetJobMaxId() + 1
                            self.NodeDBAddition(
                                self.max_nodes,
                                cur_dropped_id,
                                cur_dropped_node,
                                shot_id,
                            )

                        else:
                            print(
                                "node need to store info of this node being dropped here, \n"
                                "since already got dropped here and is stored motherfuckaaa."
                            )
                            pass
                    else:
                        self.max_nodes = self.Database.GetJobMaxId() + 1
                        self.max_history = self.Database.GetJobHistoryMaxId() + 1
                        self.NodeDBAddition(
                            self.max_nodes, cur_dropped_id, cur_dropped_node, shot_id
                        )
                        self.NodeDBHistoryAddition(
                            self.max_history, cur_dropped_id, cur_dropped_node
                        )

                except ValueError as ve:
                    print(ve)
                    pass

            else:
                self.NodeDBAddition(1, cur_dropped_id, cur_dropped_node, shot_id)
                self.NodeDBHistoryAddition(1, cur_dropped_id, cur_dropped_node)
        else:
            print("The Node doesn't need to be stored in the DB")
            pass

    """
    Node Per Shot Drop Handling
    """

    def NodeDBAddition(self, node_id, cur_dropped_id, cur_dropped_node, shot_id):
        print(f"Max Nodes AFTER Dropping: {node_id}")

        nodes_tuple = (
            node_id,
            cur_dropped_id,
            cur_dropped_node,
            shot_id,
        )
        print(nodes_tuple)
        self.Database.InsertJobDB(nodes_tuple)

    """
    Node ID And Information History Handling
    """

    def NodeDBHistoryAddition(self, history_id, node_uuid, cur_dropped_node):
        node_history_tuple = (
            history_id,
            node_uuid,
            cur_dropped_node,
            hou.hipFile.name(),
            hou.node(cur_dropped_node).type().name(),
            0,
            0,
        )
        self.Database.InsertJobHistoryDB(node_history_tuple)

    def CompareTupleInList(self, res: tuple, trgt_list: list):
        for tup in trgt_list:
            if tup[0] == res[0] and tup[1] == res[1]:
                return False
        return True

    def RetrieveNodesFromDB(self, shot_id):
        nodes_list = self.Database.FetchAllJobsByShot(shot_id)
        return nodes_list

    """
    Property Tab Creation Methods
    """

    def CreatePropertyTab(self, node_type):
        if node_type == "unknown":
            submission_tab = QtWidgets.QWidget()
            pass
        else:
            submission_tab = QtWidgets.QWidget()
            sub_tab = self.SubmissionTab(node_type)
            submission_tab.setLayout(sub_tab)
            # self.tab_container.addTab(self.submission_tab, "SUBMISSION PROPERTIES")
            # self.submission_tab.setHidden(True)

        return submission_tab

    def MakePropsTabVisible(self):
        cur_shot_nodes_info = self.PreShotDrop(self.ProjectDataInfo)[1]
        ordered_dwList = OrderedDict(self.DroppedWidgetList.items())
        print("These are DroppedWidgetList Items: ", ordered_dwList)

        for uuid, dropped_node_widgets in ordered_dwList.items():
            try:
                if dropped_node_widgets[0].isSelected() and dropped_node_widgets[1]:
                    print(cur_shot_nodes_info[uuid])
                    node_path = cur_shot_nodes_info[uuid][1]
                    node_name = node_path.split("/")[-1]
                    label = "{} Properties".format(node_name)
                    self.tab_container.addTab(dropped_node_widgets[1], label)
                    dropped_node_widgets[1].setHidden(False)

                elif dropped_node_widgets[1] == None:
                    pass
                else:
                    tab_to_remove = self.tab_container.indexOf(dropped_node_widgets[1])
                    self.tab_container.removeTab(tab_to_remove)
                    dropped_node_widgets[1].setHidden(True)
            except KeyError as ke:
                print(ke)
                raise

    def SubmissionTab(self, node_type):

        left = QtCore.Qt.AlignLeft
        right = QtCore.Qt.AlignRight
        up = QtCore.Qt.AlignTop
        down = QtCore.Qt.AlignRight
        center = QtCore.Qt.AlignCenter

        # cleanup_scripts = [
        #     os.path.join(self.cleanup_scripts_path, cl_script)
        #     for cl_script in os.listdir(self.cleanup_scripts_path)
        # ]

        # cmd_scripts = [
        #     os.path.join(self.cmd_scripts_path, cmd_script)
        #     for cmd_script in os.listdir(self.cmd_scripts_path)
        # ]
        self.formbox = QtWidgets.QFormLayout()

        self.submission_box = QtWidgets.QVBoxLayout()

        ########  ########  ########  ########
        #### PUBLIC VARIABLES, USER INPUT ####
        ########  ########  ########  ########
        input_fields_grid = QtWidgets.QGridLayout()
        input_fields = {"Crews", "Tags", "Envkey"}
        input_of_fields = []

        if node_type in ExportTypes():

            for i, field in enumerate(input_fields):
                field_name = QtWidgets.QLabel("{}:".format(field))
                field_name.setAlignment(right)
                field_line = QtWidgets.QLineEdit()
                field_line.setMaximumWidth(500)
                field_line.setAlignment(left)
                input_fields_grid.addWidget(field_name, i, 0)
                input_fields_grid.addWidget(field_line, i, 1)
                input_of_fields.append(field_line)

            # self.formbox.setFormAlignment(right)
            # self.submission_box.addLayout(input_fields_grid)
            zipObj = zip(input_fields, input_of_fields)
            self.dict_of_fields = dict(zipObj)

            # Priority and Start Time
            # Priority
            combogrid = QtWidgets.QGridLayout()

            self.priority = QtWidgets.QComboBox()
            priority_opt = [
                "Very Low",
                "Low",
                "Medium",
                "High",
                "Very High",
                "Critical",
            ]
            for opt in priority_opt:
                self.priority.addItem(opt)
            self.priority.setCurrentIndex(2)

            self.pro_lbl = QtWidgets.QLabel("Priority")
            self.pro_lbl.setAlignment(right)

            combogrid.addWidget(self.pro_lbl, 0, 0)
            combogrid.addWidget(self.priority, 0, 1)

            # Hardware Spool
            self.blades = QtWidgets.QComboBox()
            # self.blades.setStyleSheet(widget_stylesheet)
            blade_opts = ["All GPUs", "D300 GPUs", "D500 GPUs", "Linux"]

            for opt in blade_opts:
                self.blades.addItem(opt)
            self.blades.setCurrentIndex(0)

            self.blades_lbl = QtWidgets.QLabel("Hardware Spool")
            self.blades_lbl.setAlignment(right)

            combogrid.addWidget(self.blades_lbl, 0, 2)
            combogrid.addWidget(self.blades, 0, 3)

            # Frames per Unit Spinbox
            self.fpu_spin = QtWidgets.QSpinBox()
            self.fpu_spin.setMinimum(1)

            self.fpu_lbl = QtWidgets.QLabel("Frames per Unit:")
            self.fpu_lbl.setAlignment(right)

            combogrid.addWidget(self.fpu_lbl, 0, 4)
            combogrid.addWidget(self.fpu_spin, 0, 5)
            # self.fpu_spin.setFixedSize((main_W / 10),(main_H / 15))

            empty = QtWidgets.QHBoxLayout()
            self.formbox.setFormAlignment(center)
            self.formbox.addRow(input_fields_grid)
            self.formbox.addRow(empty)
            self.formbox.addRow(combogrid)

            return self.formbox

    def InitiateSpoolAndSend(self, SubmissionObj, nodelist):
        ######## INITIATE SUBMISSION CLASS FEEDING IN ALL PARAMETERS #########
        Submission = HoudiniSubmissionMethods(
            self.blades,
            self.fpu_spin,
            self.priority,
            self.dict_of_fields,
            self.ProjectDataInfo,
        )
        SubmissionObj.SpoolJob(nodelist)
