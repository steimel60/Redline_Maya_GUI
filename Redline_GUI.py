import fileinput, os, sys, glob, re, math
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
#change path to load local files
ms_dir = os.path.expanduser("~/maya/scripts/RedlineAutomationTools")
sys.path.append(ms_dir)
from Settings import *
import magicShade, pointCloud, siteTools, autoUACR, vcFileManager, vehicleRigging, characterRigging
#When adding new ToolKit also add to toolKitFiles in init function

SCRIPT_NAME = "Redline Forensic Studio - Maya Tools"

#Returns an instance of Maya's main window
def maya_main_window():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class MainUI(MayaQWidgetDockableMixin,QDialog):
    def __init__(self, parent=maya_main_window()):
        super(MainUI, self).__init__(parent)
        # Set up the window
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(250, -1)
        self.setWindowTitle(SCRIPT_NAME)
        self.setWindowIcon(QIcon(icon_dir + "/RedlineLogo.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.toolKitFiles = [magicShade, pointCloud, siteTools, autoUACR, vcFileManager, vehicleRigging, characterRigging]
        self.toolkits = [] #ToolKit instances will be saved here
        self.load_tool_kits()
        self.create_controls()
        self.create_layout()
        self.make_connections()

        # If we have a last-opened file saved in preferences, automatically open that file. Otherwise, just open
        # a new, empty file
        # region Open Last File
        found_last_file_path = False
        if os.path.isfile(pref_path):  # If the prefs file exists
            with open(pref_path) as f:
                data = f.read().splitlines()  # Read the prefs file
                found_last_file_path = False
                for line in data:
                    if line.startswith(last_file_pref + "="):  # If we find the last-opened file line in prefs
                        last_file_path = line[len(last_file_pref) + 1:]  # Get the last-opened file path
                        if os.path.isfile(last_file_path):  # If the path we get exists
                            #self.choose_spellbook_edit.setText(last_file_path)  # Open the last-opened file
                            found_last_file_path = True
                            break
                f.close()

        if not found_last_file_path:
            self.current_file = None
        pass

    #Create TookKit Instances
    def load_tool_kits(self):
        for toolKit in self.toolKitFiles:
            self.toolkits.append(toolKit.ToolKit())

    #Buttons
    def create_controls(self):
        ##### Banner #####
        self.banner = QLabel()
        self.pixmap = QPixmap(icon_dir + '/banner.jpg')
        self.pixmap = self.pixmap.scaled(600, 1000, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.banner.setPixmap(self.pixmap)
        self.banner.resize(self.pixmap.width(), self.pixmap.height())
        self.banner.setAlignment(Qt.AlignCenter)
        ##### Tab Bar #####
        self.tabWidget = QTabWidget()
        self.tabs = []
        for i in range(len(self.toolkits)):
            self.tabs.append(QWidget())
            self.tabWidget.addTab(self.tabs[i], self.toolkits[i].toolKitName)

        ##### Save Button #####
        self.save_button = QPushButton(QIcon(icon_dir + "/save_as.png"), "Save As...")

    #Layout
    def create_layout(self):
        main_layout = QVBoxLayout()

        self.setStyleSheet("""QTabWidget {background-color: rgb(100,102,117);}
                            QPushButton {background-color: rgb(87,87,87);}
                            QGroupBox {background-color: rgb(72,71,76);}
                            QComboBox {background-color: rgb(87,87,87); }
                            QComboBox QAbstractItemView {background-color: rgb(72,71,76); selection-background-color : rgb(100,102,117)}
                            """)

        ##### Load ToolKit Layouts #####
        for i in range(len(self.tabs)):
            self.tabs[i].setLayout(self.toolkits[i].layout)

        ##### Save Section #####
        save_group = QGroupBox("Save File")
        save_layout = QVBoxLayout()
        save_layout.addWidget(self.save_button)
        save_group.setLayout(save_layout)

        ##### Set Main Layout #####
        main_layout.addWidget(self.banner)
        main_layout.addWidget(self.tabWidget)
        main_layout.addWidget(save_group)
        self.setLayout(main_layout)

    #Connections
    def make_connections(self):
        ##### Save Group #####
        self.save_button.clicked.connect(self.save)

        ##### Cross Class Buttons #####
        #Refresh Asset Drop Downs on Load
        self.toolkits[4].loadRig_button.clicked.connect(self.toolkits[5].refreshAssets)
        self.toolkits[4].create_vLocator_button.clicked.connect(self.toolkits[5].refreshAssets)

    #Functions
    def save(self):
        cmds.SaveSceneAs(o=True)

# Dev code to automatically close old windows when running
try:
    ui.close()
except:
    pass

# Show a new instance of the UI
ui = MainUI()
ui.show(dockable=True)
