import fileinput, os, sys, glob, re, math

import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

ms_dir = os.path.expanduser("~/maya/scripts/magic-shade")
sys.path.append(ms_dir)
from CableMaker import *

SCRIPT_NAME = "Redline Forensic Studio - Maya Tools"

# ----------------------------------------------------------------------------------------------------------------------
# Returns an instance of Maya's main window
# ----------------------------------------------------------------------------------------------------------------------
def maya_main_window():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class MainUI(QDialog):
    # Set up file references
    ms_dir = os.path.expanduser("~/maya/scripts/magic-shade")
    icon_dir = os.path.expanduser("~/maya/scripts/magic-shade/resources/icons")
    spellbook_dir = os.path.expanduser("~/maya/scripts/magic-shade/spellbooks")
    studio_dir = os.path.expanduser("~/maya/scripts/magic-shade/studios")
    pref_path = os.path.expanduser("~/maya/scripts/magic-shade/prefs")
    arnold_studio_path = os.path.expanduser("~/maya/scripts/magic-shade/Arnold_Studio_V3.mb")
    thumbs_dir = os.path.expanduser("~/maya/projects/default/scenes/.mayaSwatches")
    save_path = os.path.expanduser("~/maya/projects/default/scenes/")
    user_profile = os.environ['USERPROFILE']
    desktop_dir = user_profile + '\\Desktop'
    last_file_pref = "last_vehicular_spellbook"
    vehicle_library_dir = user_profile + "/deltav/Jason Young - Asset Library/3D Vehicle Library/"
    vehiclespec_library_dir = user_profile + "/deltav/Jason Young - Asset Library/3D Vehicle Library/"

    # --------------------------------------------------------------------------------------------------------------
    # Initializes variables, window, and UI elements
    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window()):
        super(MainUI, self).__init__(parent)

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.setFixedWidth(600)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(250, -1)
        self.setWindowTitle(SCRIPT_NAME)
        self.setWindowIcon(QIcon(self.icon_dir + "/RedlineLogo.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout
        self.make_connections()
        self.dont_shrink = False
        self.asset = None

        # If we have a last-opened file saved in preferences, automatically open that file. Otherwise, just open
        # a new, empty file
        # region Open Last File
        found_last_file_path = False
        if os.path.isfile(self.pref_path):  # If the prefs file exists
            with open(self.pref_path) as f:
                data = f.read().splitlines()  # Read the prefs file
                found_last_file_path = False
                for line in data:
                    if line.startswith(self.last_file_pref + "="):  # If we find the last-opened file line in prefs
                        last_file_path = line[len(self.last_file_pref) + 1:]  # Get the last-opened file path
                        # print(last_file_path)
                        if os.path.isfile(last_file_path):  # If the path we get exists
                            # print("found last file: " + last_file_path)
                            #self.choose_spellbook_edit.setText(last_file_path)  # Open the last-opened file
                            found_last_file_path = True
                            break
                f.close()

        if not found_last_file_path:
            # print("no path in prefs")
            self.current_file = None
        pass  # I hate PyCharm
        # endregion

    #--------------------------------------------------------------------------------------------------------------
    #                                   Make the Buttons
    #--------------------------------------------------------------------------------------------------------------
    def create_controls(self):
        UI_ELEMENT_HEIGHT = 30
        UI_ELEMENT_WIDTH = 150

        ##### Banner #####
        self.banner = QLabel()
        self.pixmap = QPixmap(self.icon_dir + '/banner.jpg')
        self.pixmap = self.pixmap.scaled(600, 1000, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.banner.setPixmap(self.pixmap)
        self.banner.resize(self.pixmap.width(), self.pixmap.height())
        ##### Tab Bar #####
        self.tabWidget = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tabWidget.addTab(self.tab1, 'Vehicle Tools')
        self.tabWidget.addTab(self.tab2, 'Site Tools')
        self.tabWidget.addTab(self.tab3, 'Point Cloud Tools')
        self.tabWidget.addTab(self.tab4, 'Virtual Crash Tools')

        ################################################## VEHICLE TOOL BUTTONS ########################################################################
        ##### Studio Dropdown #####
        self.choose_studio_button = QComboBox(self)
        studio_list = []
        self.studio_paths = []
        for file in glob.glob(self.studio_dir + '/*'): #finds all studios and creates dropdown
            studio_match = re.search('/studios(.*).mb', file)
            studio_name = studio_match.group(1)
            studio_list.append(studio_name[1:])
            self.studio_paths.append(file)
        for item in studio_list:
            self.choose_studio_button.addItem(item)
        self.studio_current = self.studio_paths[self.choose_studio_button.currentIndex()]

        ##### Studio Load Button #####
        self.load_studio_button = QPushButton(QIcon(self.icon_dir + "/template.png"), "Load Studio")
        self.load_studio_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_studio_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Text Bar #####
        self.choose_vehicle_edit = QLineEdit()
        self.choose_vehicle_edit.setPlaceholderText("Vehicle File")
        self.choose_vehicle_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.choose_vehicle_edit.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Folder Button #####
        self.choose_vehicle_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Vehicle Button #####
        self.load_vehicle_button = QPushButton(QIcon(self.icon_dir + "/load.png"), "Load Vehicle")
        self.load_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_vehicle_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Specs Image #####
        self.specs_icon = QLabel()
        self.specsmap = QPixmap(self.icon_dir + '/dxf.png')
        self.specsmap = self.specsmap.scaled(70, 90, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.specs_icon.setPixmap(self.specsmap)

        ##### Vehicle Specs Text Bar #####
        self.choose_vehiclespec_edit = QLineEdit()
        self.choose_vehiclespec_edit.setPlaceholderText("Vehicle Specs")
        self.choose_vehiclespec_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.choose_vehiclespec_edit.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Specs Folder Button #####
        self.choose_vehiclespec_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_vehiclespec_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        #self.choose_vehiclespec_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Do Everything Button #####
        self.do_everything_button = QPushButton(QIcon(self.icon_dir + "/wizzardHat.png"),"Magic VC Button")
        self.do_everything_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Specs Button #####
        self.load_vehiclespec_button = QPushButton(QIcon(self.icon_dir + "/load.png"), "Load Vehicle Specs")
        self.load_vehiclespec_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_vehiclespec_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Don't Scale Switch #####
        self.post_arnold_button = QCheckBox('No Scaling', self)

        ##### Spellbook Dropdown #####
        self.choose_spellbook_button = QComboBox(self)
        spellbook_list = []
        self.path_list = []
        for file in glob.glob(self.spellbook_dir + '/*'): #Finds all spellbooks and creates dropdown
            spell_match = re.search('/spellbooks(.*).spb', file)
            spell_name = spell_match.group(1)
            spellbook_list.append(spell_name[1:])
            self.path_list.append(file)
        for item in spellbook_list:
            self.choose_spellbook_button.addItem(item)
        self.spellbook_current = self.path_list[self.choose_spellbook_button.currentIndex()]

        ##### Apply Spellbook Button #####
        self.apply_spellbook_button = QPushButton(QIcon(self.icon_dir + "/cast_all.png"), "Apply Spellbook")
        self.apply_spellbook_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Rotation Buttons #####
        self.xyz_selection = QComboBox(self)
        direction_list = ['X','Y','Z']
        for dir in direction_list:
            self.xyz_selection.addItem(dir)
        self.left_arrow_button = QPushButton(QIcon(self.icon_dir + "/left"), "Rotate -90")
        self.left_arrow_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.right_arrow_button = QPushButton(QIcon(self.icon_dir + "/right"), "Rotate +90")
        self.right_arrow_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.quick_rotate_button = QPushButton("Quick VC Rotate")
        self.hv_rotate_button = QPushButton("Quick HV Rotate")

        ##### Remove Tires Button #####
        self.remove_tires_button = QPushButton(QIcon(self.icon_dir + "/tire.png"), "Remove Tires")
        self.remove_tires_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Remove License Plate Button #####
        self.remove_license_plate_button = QPushButton(QIcon(self.icon_dir + "/license_plate.png"), "Remove License Plates")
        self.remove_license_plate_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Make Windows Transparent Button #####
        self.make_windows_transparent_button = QPushButton(QIcon(self.icon_dir + "/window.png"), "Transparent Windows (Arnold Only)")
        self.make_windows_transparent_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Save Button #####
        self.save_button = QPushButton(QIcon(self.icon_dir + "/save_as.png"), "Save As...")
        self.save_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Export Button #####
        self.export_obj = QPushButton(QIcon(self.icon_dir + "/export.png"),"Export OBJ")
        self.export_obj.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ################################################### SITE TOOL BUTTONS #######################################################################################
        ##### XYZ Text Bar #####
        self.choose_locator_edit = QLineEdit()
        self.choose_locator_edit.setPlaceholderText("Locator File")
        self.choose_locator_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### XYZ Folder Button #####
        self.choose_locator_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load XYZ Button #####
        self.load_locator_button = QPushButton(QIcon(self.icon_dir + "/load.png"), "Load Locators")
        self.load_locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.open_cable_button = QPushButton("Open Cable Creator")
        self.open_cable_button.setMinimumHeight(UI_ELEMENT_HEIGHT)



        ##################################################### Point Cloud Buttons ####################################################################################
        ##### Point CLoud Text Bar #####
        self.choose_xyzfile_edit = QLineEdit()
        self.choose_xyzfile_edit.setPlaceholderText("XYZ File")
        self.choose_xyzfile_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Point CLoud Folder Button #####
        self.choose_xyzfile_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_xyzfile_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Point CLoud Button #####
        self.load_xyzfile_button = QPushButton(QIcon(self.icon_dir + "/load.png"), "Load Point Cloud")
        self.load_xyzfile_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Density Dropdown #####
        self.choose_density_button = QComboBox(self)
        self.density_list = ['Entire File','High','Medium','Low','Very Low']
        for item in self.density_list:
            self.choose_density_button.addItem(item)
        self.density_label = QLabel()
        self.density_label.setText('Density Settings:')
        self.density_label.setAlignment(Qt.AlignCenter)
        self.density_current = self.density_list[self.choose_density_button.currentIndex()]

        ##################################################### VC and Rigging ####################################################################################
        ##### Rig Buttons #####
        self.choose_rig_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_rig_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_rig_edit = QLineEdit()
        self.choose_rig_edit.setPlaceholderText("Rig File")
        self.choose_rig_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.loadRig_button = QPushButton("Load Rig")
        self.loadRig_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_mesh_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_mesh_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_mesh_edit = QLineEdit()
        self.choose_mesh_edit.setPlaceholderText("Mesh File")
        self.choose_mesh_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.loadMesh_button = QPushButton("Load Mesh")
        self.loadMesh_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        ##### Vehicle Locator Buttons #####
        self.choose_vcData_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_vcData_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_vcData_edit = QLineEdit()
        self.choose_vcData_edit.setPlaceholderText("Virtual Crash Data File")
        self.choose_vcData_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.convert_vcData_button = QPushButton("Convert VC Data")
        self.convert_vcData_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_vLocator_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_vLocator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_vLocator_edit = QLineEdit()
        self.choose_vLocator_edit.setPlaceholderText("Vehicle Locator .MOV File")
        self.choose_vLocator_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.create_vLocator_button = QPushButton("Create Vehicle Locator")
        self.create_vLocator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.fps_edit = QComboBox(self)
        fps_list = ['24','30','100']
        for i in range(0,len(fps_list)):
            self.fps_edit.addItem(fps_list[i])
            if fps_list[i] == '100':
                hundredIndex = i
        self.fps_edit.setCurrentIndex(hundredIndex)
        self.fps_label = QLabel()
        self.fps_label.setText('FPS:')
        self.fps_label.setMaximumWidth(35)

        ##### Make Constraints #####
        self.rigMatch_dropdown = QComboBox(self)
        rigs = cmds.ls('*_driveControl', r=True)
        for rig in rigs:
            self.rigMatch_dropdown.addItem(rig)
        self.vLocatorMatch_dropdown = QComboBox(self)
        locators = cmds.ls('*_Locator')
        for locator in locators:
            self.vLocatorMatch_dropdown.addItem(locator)
        self.pairRig2Locator_button = QPushButton('Pair Rig to Locator')
        self.pairRig2Locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.constraintList_dropdown = QComboBox(self)
        constraints = cmds.ls('*driveControl_parentConstraint*', r=True)
        for constraint in constraints:
            self.constraintList_dropdown.addItem(constraint)

        self.parentX = QLineEdit()
        self.parentX.setPlaceholderText("X")
        self.parentX.setMaximumWidth(70)
        self.parentX.setMinimumWidth(70)
        self.parentX.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.parentY = QLineEdit()
        self.parentY.setPlaceholderText("Y")
        self.parentY.setMaximumWidth(70)
        self.parentY.setMinimumWidth(70)
        self.parentY.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.parentZ = QLineEdit()
        self.parentZ.setPlaceholderText("Z")
        self.parentZ.setMaximumWidth(70)
        self.parentZ.setMinimumWidth(70)
        self.parentZ.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rotateOnConst_button = QPushButton('Rotate on Constraint')
        self.rotateOnConst_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### CoG Height Adjustment #####
        self.cgHeight_dropdown = QComboBox(self)
        constraints = cmds.ls('*driveControl_parentConstraint*', r=True)
        for constraint in constraints:
            self.cgHeight_dropdown.addItem(constraint)
        self.cgHeight_edit = QLineEdit()
        self.cgHeight_edit.setPlaceholderText('CoG Height')
        self.cgHeight_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.cgHeight_button = QPushButton('Adjust Height')
        self.cgHeight_button.setMinimumHeight(UI_ELEMENT_HEIGHT)


        ##### Wheel Constraint #####
        self.wheelConstr_button = QPushButton('Constrain wheels to mesh')


    def create_layout(self):
        main_layout = QVBoxLayout()
        vehicleTool_layout = QVBoxLayout()
        siteTool_layout = QVBoxLayout()
        vCrashTool_layout = QVBoxLayout()
        self.pcTool_layout = QVBoxLayout()

        self.setStyleSheet("""QTabWidget {background-color: rgb(100,102,117);}
                            QPushButton {background-color: rgb(87,87,87);}
                            QGroupBox {background-color: rgb(72,71,76);}
                            QComboBox {background-color: rgb(87,87,87); }
                            QComboBox QAbstractItemView {background-color: rgb(72,71,76); selection-background-color : rgb(100,102,117)}
                            """)

        ##############################################
        ######       Vehicle Section            ######
        ##############################################

        ##### Studio GUI Section #####
        studio_group = QGroupBox("Studio")
        studio_layout = QVBoxLayout()
        studio_layout.addWidget(self.choose_studio_button)
        studio_layout.addWidget(self.load_studio_button)
        studio_group.setLayout(studio_layout)
        vehicleTool_layout.addWidget(studio_group)
        #vehicleTool_layout.insertSpacing(-1, 10)

        ##### Vehicle GUI Section #####
        load_group = QGroupBox("Vehicle")
        load_vehicle_layout = QGridLayout()
        load_vehicle_layout.addWidget(self.choose_vehicle_button, 0, 0)
        load_vehicle_layout.addWidget(self.choose_vehicle_edit, 0, 1, 1, 3)
        load_vehicle_layout.addWidget(self.post_arnold_button, 0, 4)
        load_vehicle_layout.addWidget(self.load_vehicle_button, 0, 5, 1, 3)
        load_vehicle_layout.addWidget(self.choose_vehiclespec_edit, 1, 1, 1, 3)
        load_vehicle_layout.addWidget(self.choose_vehiclespec_button, 1, 0)
        load_vehicle_layout.addWidget(self.specs_icon, 1, 4)
        load_vehicle_layout.addWidget(self.load_vehiclespec_button, 1, 5, 1, 3)
        load_vehicle_layout.addWidget(self.do_everything_button, 2, 0, 1, 8)
        load_group.setLayout(load_vehicle_layout)
        vehicleTool_layout.addWidget(load_group)

        ##### Spellbook GUI Section #####
        spell_group = QGroupBox("Spellbook")
        spell_layout = QVBoxLayout()
        spell_layout.addWidget(self.choose_spellbook_button)
        spell_layout.addWidget(self.apply_spellbook_button)
        spell_group.setLayout(spell_layout)
        vehicleTool_layout.addWidget(spell_group)

        ##### Rotation GUI Section #####
        rotation_group = QGroupBox("Rotation")
        rotation_layout = QGridLayout()
        rotation_layout.addWidget(self.xyz_selection, 2, 0)
        rotation_layout.addWidget(self.left_arrow_button, 2, 1)
        rotation_layout.addWidget(self.right_arrow_button, 2, 2)
        rotation_layout.addWidget(self.quick_rotate_button, 0, 0, 1, 3)
        rotation_layout.addWidget(self.hv_rotate_button, 1, 0, 1, 3)
        rotation_group.setLayout(rotation_layout)
        vehicleTool_layout.addWidget(rotation_group)
        #vehicleTool_layout.insertSpacing(-1, 10)

        ##### Extra Tools GUI Section #####
        tools_group = QGroupBox("Extra Tools")
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.remove_tires_button)
        tools_layout.addWidget(self.remove_license_plate_button)
        tools_layout.addWidget(self.make_windows_transparent_button)
        tools_group.setLayout(tools_layout)
        vehicleTool_layout.addWidget(tools_group)
        #vehicleTool_layout.insertSpacing(-1, 10)

        ##############################################
        ######          Site Section            ######
        ##############################################

        ##### XYZ Locator Section #####
        locator_group = QGroupBox("Locators")
        locator_layout = QGridLayout()
        locator_layout.addWidget(self.choose_locator_button, 0, 0)
        locator_layout.addWidget(self.choose_locator_edit, 0, 1, 1, 2)
        locator_layout.addWidget(self.load_locator_button, 1, 0, 1, 3)
        locator_group.setLayout(locator_layout)
        siteTool_layout.addWidget(locator_group)

        ##### Cable GUI #####
        cable_group = QGroupBox("Cable GUI")
        cable_layout = QVBoxLayout()
        cable_layout.addWidget(self.open_cable_button)
        cable_group.setLayout(cable_layout)
        siteTool_layout.addWidget(cable_group)



        ##############################################
        ######      Point Cloud Section         ######
        ##############################################

        ##### Load Section #####
        pcload_group = QGroupBox("Load Point Cloud")
        pcload_layout = QGridLayout()
        pcload_layout.addWidget(self.choose_xyzfile_button, 0, 0)
        pcload_layout.addWidget(self.choose_xyzfile_edit, 0, 1, 1, 2)
        pcload_layout.addWidget(self.density_label, 1, 0)
        pcload_layout.addWidget(self.choose_density_button, 1, 1, 1, 2)
        pcload_layout.addWidget(self.load_xyzfile_button, 2, 0, 1, 3)
        pcload_group.setLayout(pcload_layout)
        self.pcTool_layout.addWidget(pcload_group)

        ##############################################
        ######           VC Section             ######
        ##############################################

        ##### File Management #####
        files_group = QGroupBox("File Management")
        files_layout = QGridLayout()

        files_layout.addWidget(self.choose_rig_button,0,0)
        files_layout.addWidget(self.choose_rig_edit,0,1,1,4)
        files_layout.addWidget(self.loadRig_button,0,5,1,2)

        files_layout.addWidget(self.choose_mesh_button,1,0)
        files_layout.addWidget(self.choose_mesh_edit,1,1,1,4)
        files_layout.addWidget(self.loadMesh_button,1,5,1,2)

        files_layout.addWidget(self.choose_vcData_button,2,0)
        files_layout.addWidget(self.choose_vcData_edit,2,1,1,4)
        files_layout.addWidget(self.convert_vcData_button,2,5,1,2)

        files_layout.addWidget(self.choose_vLocator_button, 3, 0)
        files_layout.addWidget(self.choose_vLocator_edit, 3, 1, 1, 4)
        files_layout.addWidget(self.fps_label, 3, 5)
        files_layout.addWidget(self.fps_edit, 3, 6)
        files_layout.addWidget(self.create_vLocator_button, 4, 0, 1, 7)
        files_group.setLayout(files_layout)
        vCrashTool_layout.addWidget(files_group)

        ##### Vehicle Rigging #####
        vLocator_group = QGroupBox("Vehicle Rigging")
        vLocator_layout = QGridLayout()

        vLocator_layout.addWidget(self.vLocatorMatch_dropdown, 0,0,1,2)
        vLocator_layout.addWidget(self.rigMatch_dropdown, 0,2,1,2)
        vLocator_layout.addWidget(self.pairRig2Locator_button,0,4,1,3)

        vLocator_layout.addWidget(self.constraintList_dropdown,1,0,1,2)
        vLocator_layout.addWidget(self.parentX,1,2)
        vLocator_layout.addWidget(self.parentY,1,3)
        vLocator_layout.addWidget(self.parentZ,1,4)
        vLocator_layout.addWidget(self.rotateOnConst_button,1,5,1,2)

        vLocator_layout.addWidget(self.cgHeight_dropdown,2,0,1,2)
        vLocator_layout.addWidget(self.cgHeight_edit,2,2,1,3)
        vLocator_layout.addWidget(self.cgHeight_button,2,5,1,2)

        vLocator_layout.addWidget(self.wheelConstr_button, 3,0,1,7)
        vLocator_group.setLayout(vLocator_layout)
        vCrashTool_layout.addWidget(vLocator_group)



        ##############################################
        ######          Save Section            ######
        ##############################################

        ##### Save Section #####
        save_group = QGroupBox("File Management")
        save_layout = QVBoxLayout()
        save_layout.addWidget(self.save_button)
        save_layout.addWidget(self.export_obj)
        save_group.setLayout(save_layout)

        ##### Set Main Layout #####
        self.tab1.setLayout(vehicleTool_layout)
        self.tab2.setLayout(siteTool_layout)
        self.tab3.setLayout(self.pcTool_layout)
        self.tab4.setLayout(vCrashTool_layout)
        main_layout.addWidget(self.banner)
        main_layout.addWidget(self.tabWidget)
        main_layout.addWidget(save_group)
        self.setLayout(main_layout)

    #---------------------------------------------------------------------------------------------------------------
    # Connect button to button functions
    #---------------------------------------------------------------------------------------------------------------
    def make_connections(self):
        #--------------------------------- Vehicle Section -------------------------------------------------#
        ##### Studio Group #####
        self.load_studio_button.clicked.connect(self.load_studio)
        ##### Vehicle Group #####
        self.choose_vehicle_button.clicked.connect(self.choose_vehicle)
        self.load_vehicle_button.clicked.connect(self.load_vehicle)
        self.choose_vehiclespec_button.clicked.connect(self.choose_vehiclespec)
        self.load_vehiclespec_button.clicked.connect(self.load_vehiclespec)
        self.post_arnold_button.stateChanged.connect(self.dont_shrink_bool)
        self.do_everything_button.clicked.connect(self.auto_vc)
        ##### Spellbook Group #####
        self.apply_spellbook_button.clicked.connect(self.apply_spellbook)
        ##### Rotation Group #####
        self.left_arrow_button.clicked.connect(self.neg_rotation)
        self.right_arrow_button.clicked.connect(self.pos_rotation)
        self.quick_rotate_button.clicked.connect(self.quick_rotate)
        self.hv_rotate_button.clicked.connect(self.hv_rotate)
        ##### Extra Tools #####
        self.remove_tires_button.clicked.connect(self.remove_tires)
        self.remove_license_plate_button.clicked.connect(self.remove_license_plate)
        self.make_windows_transparent_button.clicked.connect(self.make_windows_transparent)
        ##### Save Group #####
        self.save_button.clicked.connect(self.save)
        self.export_obj.clicked.connect(self.export)

        #-------------------------------------- Site Section ------------------------------------------------#
        ##### Locator Group #####
        self.choose_locator_button.clicked.connect(self.choose_locator)
        self.load_locator_button.clicked.connect(self.load_locator)

        ##### Cable Group #####
        self.open_cable_button.clicked.connect(self.cable_gui)

        #------------------------------------- Point Cloud Section ------------------------------------------#
        ##### Load Group #####
        self.choose_xyzfile_button.clicked.connect(self.choose_xyzfile)
        self.load_xyzfile_button.clicked.connect(self.load_xyzfile)

        #--------------------------------------  VC Section  ------------------------------------------------#
        ##### Vechicle Locator #####
        self.choose_rig_button.clicked.connect(self.choose_rig)
        self.loadRig_button.clicked.connect(self.load_rig)
        self.choose_mesh_button.clicked.connect(self.choose_mesh)
        self.loadMesh_button.clicked.connect(self.load_mesh)
        self.choose_vcData_button.clicked.connect(self.loadVCData)
        self.convert_vcData_button.clicked.connect(self.convertVCData)
        self.choose_vLocator_button.clicked.connect(self.loadvLocator)
        self.create_vLocator_button.clicked.connect(self.vehicleLocator)
        self.pairRig2Locator_button.clicked.connect(self.pairRig2Locator)
        self.rotateOnConst_button.clicked.connect(self.rotateOnConst)
        self.cgHeight_button.clicked.connect(self.cgHeightAdjust)
        self.wheelConstr_button.clicked.connect(self.wheelConst)
    #---------------------------------------------------------------------------------------------------------------
    # Button Functions
    #---------------------------------------------------------------------------------------------------------------
    def dont_shrink_bool(self, state):
        # If project already scaled click to prevent scaling again
        if state == Qt.Checked:
            self.dont_shrink = True
        else:
            self.dont_shrink = False

    def load_studio(self):
        #Choose which studio to work in
        cmds.file(new=True, force=True)
        studio_path = self.studio_paths[self.choose_studio_button.currentIndex()]
        cmds.file(studio_path, open=True)

    def choose_vehicle(self):
        #Sets vehicle path
        file_path = QFileDialog.getOpenFileName(None, "", self.vehicle_library_dir, "Vehicles (*.mb *.obj *.fbx);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vehicle_edit.setText(file_path)

    def load_vehicle(self):
        # Loads choosen vehicle
        vehicle_path = self.choose_vehicle_edit.text()
        if os.path.isfile(vehicle_path):
            cmds.select(allDagObjects=True)
            prev_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(prev_all_objects))
            cmds.file(vehicle_path, i=True)
            cmds.select(allDagObjects=True)
            new_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(new_all_objects))
            diff = [x for x in new_all_objects if x not in prev_all_objects]
            # print(str(diff))
            cmds.group(diff, name="Vehicle")
            if self.dont_shrink == False:
                #print('shrink!')
                cmds.scale(0.0328, 0.0328, 0.0328, absolute=True, pivot=(0, 0, 0))
            cmds.select(deselect=True)
            asset_match = re.search('.*/([a-zA-Z_0-9\(\)]*).*\.m[ab]', vehicle_path)
            if asset_match != None:
                self.asset = asset_match.group(1)
                cmds.file(rename=self.asset)
        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Vehicle Found", "No vehicle file found at the specified path.")
            warning_box.exec_()

    def choose_vehiclespec(self):
        # Set Spec Path
        file_path = QFileDialog.getOpenFileName(None, "", self.vehiclespec_library_dir, "Vehicles (*.mb *.obj *.fbx *.ma *dxf);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_vehiclespec_edit.setText(file_path)

    def load_vehiclespec(self):
        #Load Specs From Choosen Path
        vehiclespec_path = self.choose_vehiclespec_edit.text()
        if os.path.isfile(vehiclespec_path):
            cmds.select(allDagObjects=True)
            prev_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(prev_all_objects))

            cmds.file(vehiclespec_path, i=True)
            cmds.select(allDagObjects=True)
            new_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(new_all_objects))
            diff = [x for x in new_all_objects if x not in prev_all_objects]
            # print(str(diff))
            cmds.group(diff, name="Vehiclespecs")
            cmds.xform (absolute=True, scale=(1, 1, 1),rotation=(90,90,0),translation=(-10.583,-4.333,0),)
            cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
            cmds.select(deselect=True)

        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Vehiclespecs Found", "No vehicle specs file found at the specified path.")
            warning_box.exec_()

    def choose_spellbook(self):
        # Sets spellbook path
        file_path = self.path_list[self.choose_spellbook_button.currentIndex()]
        #if file_path == "":
        #    return
        self.save_last_file(self.spellbook_current)

    def neg_rotation(self):
        direction = self.xyz_selection.currentIndex()
        if direction == 0:
            cmds.select(all=True)
            cmds.rotate(-90, 0, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')
        if direction == 1:
            cmds.select(all=True)
            cmds.rotate(0, -90, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')
        if direction == 2:
            cmds.select(all=True)
            cmds.rotate(0, 0, -90, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')

    def pos_rotation(self):
        direction = self.xyz_selection.currentIndex()
        if direction == 0:
            cmds.select(all=True)
            cmds.rotate(90, 0, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')
        if direction == 1:
            cmds.select(all=True)
            cmds.rotate(0, 90, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')
        if direction == 2:
            cmds.select(all=True)
            cmds.rotate(0, 0, 90, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
            print('rotate')

    def quick_rotate(self):
        cmds.select(all=True)
        cmds.rotate(90, 0, 90, a=True, p=[0,0,0])
        cmds.select(deselect=True)

    def hv_rotate(self):
        cmds.select(all=True)
        cmds.rotate(-90, 0, -90, a=True, p=[0,0,0])
        cmds.select(deselect=True)

    def remove_tires(self):
        try:
            tires = cmds.ls('*Tire*', '*tire*')
            for tire in tires:
                try:
                    print(tire)
                    cmds.delete(tire)
                except Exception as e:
                    print(e)

            rims = cmds.ls('*Rim*', '*rim*')
            for rim in rims:
                if (rim == 'rimShader') or (rim == 'rimSG') or (rim == 'Rims') or ('primary' in rim) or ('Primary' in rim):
                    continue
                else:
                    try:
                        print(rim)
                        cmds.delete(rim)
                    except Exception as e:
                        print(e)

            brakes = cmds.ls('*Brake*', '*brake*')
            for brake in brakes:
                if (brake == 'brakeShader') or (brake == 'brakeSG'):
                    continue
                else:
                    try:
                        print(brake)
                        cmds.delete(brake)
                    except Exception as e:
                        print(e)

            bolts = cmds.ls('*Bolt*', '*bolt*', '*Nuts*', '*nuts*')
            for bolt in bolts:
                try:
                    print(bolt)
                    cmds.delete(bolt)
                except Exception as e:
                    print(e)

            logos = cmds.ls('*Logo*')
            for logo in logos:
                try:
                    print(logo)
                    cmds.delete(logo)
                except Exception as e:
                    print(e)

            wheels = cmds.ls('*Wheel*', '*wheel*')
            for wheel in wheels:
                try:
                    print(wheel)
                    cmds.delete(wheel)
                except Exception as e:
                    print(e)

            axis = cmds.ls('*Axis*', '*axis*', '*axel*', '*Axel*')
            for axel in axis:
                try:
                    print(axel)
                    cmds.delete(axel)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

        try:
            tires = cmds.ls('*Tire*', '*tire*', s=True)
            for tire in tires:
                try:
                    print(tire)
                    cmds.delete(tire)
                except Exception as e:
                    print(e)

            rims = cmds.ls('*Rim*', '*rim*', s=True)
            for rim in rims:
                if (rim == 'rimShader') or (rim == 'rimSG') or (rim == 'Rims') or ('primary' in rim) or ('Primary' in rim):
                    continue
                else:
                    try:
                        print(rim)
                        cmds.delete(rim)
                    except Exception as e:
                        print(e)

            brakes = cmds.ls('*Brake*', '*brake*', s=True)
            for brake in brakes:
                if (brake == 'brakeShader') or (brake == 'brakeSG'):
                    continue
                else:
                    try:
                        print(brake)
                        cmds.delete(brake)
                    except Exception as e:
                        print(e)

            bolts = cmds.ls('*Bolt*', '*bolt*', '*Nuts*', '*nuts*', s=True)
            for bolt in bolts:
                try:
                    print(bolt)
                    cmds.delete(bolt)
                except Exception as e:
                    print(e)

            logos = cmds.ls('*Logo*')
            for logo in logos:
                try:
                    print(logo)
                    cmds.delete(logo)
                except Exception as e:
                    print(e)

            wheels = cmds.ls('*Wheel*', '*wheel*', s=True)
            for wheel in wheels:
                try:
                    print(wheel)
                    cmds.delete(wheel)
                except Exception as e:
                    print(e)

            axis = cmds.ls('*Axis*', '*axis*', '*axel*', '*Axel*', s=True)
            for axel in axis:
                try:
                    print(axel)
                    cmds.delete(axel)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

    def choose_locator(self):
        # Set locator Path
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "Text Files (*.txt);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_locator_edit.setText(file_path)

    def load_locator(self):
        filename = self.choose_locator_edit.text()
        f = open(filename, 'r')
        full = f.readlines()
        for i in range(0,len(full)):
            full[i] = full[i].rstrip()
            #print(full)
            if i == 0:
                headers = full[i].split('\t')
                #print(headers)
                for i in range(0, len(headers)):
                    headers[i] = headers[i].lower()
                #print(headers)
                x_loc = headers.index('x')
                y_loc = headers.index('y')
                z_loc = headers.index('z')
                #print(str(x_loc) + ' ' + str(y_loc) + ' ' + str(z_loc))

            else:
                xyz = full[i].split('\t')
                #print(xyz)
                x = xyz[x_loc]
                y = xyz[y_loc]
                z = xyz[z_loc]
                #print(z)
                cmds.spaceLocator(p=[x,y,z])

        f.close()

    def choose_xyzfile(self):
        # Set locator Path
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "XYZ Files (*.xyz);;Text Files (*.txt);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_xyzfile_edit.setText(file_path)

    def load_xyzfile(self):
        #Make Load Bar appear
        progress_group = QGroupBox("Loading Bar")
        progressBox = QVBoxLayout()
        load_label = QLabel()
        self.progress = QProgressBar(self)

        progressBox.addWidget(load_label)
        progressBox.addWidget(self.progress)
        progress_group.setLayout(progressBox)
        self.pcTool_layout.addWidget(progress_group)

        #Does nothing but updates load bar
        load_label.setText('Reading File')
        load_value = 0
        for i in range(0,5):
            load_value += 1
            self.progress.setValue(load_value)
            progress_group.setVisible(True)

        #Load file and get data
        filename = self.choose_xyzfile_edit.text()
        intensity = self.choose_density_button.currentIndex()
        stepSize = intensity*intensity + 1

        try:
            assetMatch = re.search('/*([a-zA-Z0-9-_ ]*)\.xyz', filename)
            asset = assetMatch.group(1) + '_PointCloud'
        except:
            print("Couldn't retrieve asset name")
            asset = 'PointCloud'

        f = open(filename, 'r')
        full = [line.rstrip().split(' ') for line in f.readlines()[::stepSize]]
        particleList, colorList = [(float(pos[0]), float(pos[1]), float(pos[2])) for pos in full], [(float(color[3])/255, float(color[4])/255, float(color[5])/255) for color in full]
        #xmin, ymin, zmin = min([float(x[0]) for x in particleList]), min([float(y[1]) for y in particleList]), min([float(z[2]) for z in particleList])
        f.close()

        #Disable Dynamics and create Point Cloud
        load_label.setText('Creating Point Cloud')
        load_value += 35
        self.progress.setValue(load_value)
        progress_group.setVisible(True)

        cmds.evaluator(n='dynamics', c='disablingNodes=dynamics')
        cmds.evaluator(n='dynamics', c='handledNodes=none')
        cmds.evaluator(n='dynamics', c='action=none')

        pointCloud, pointCloudShape = cmds.particle(n=asset)
        cmds.emit(object=pointCloud, pos=particleList)

        #Apply Colors
        load_label.setText('Applying Colors')
        load_value += 35
        self.progress.setValue(load_value)
        progress_group.setVisible(True)
        cmds.select(pointCloudShape)
        cmds.addAttr(ln='rgbPP', dt='vectorArray')

        cmds.setAttr(pointCloudShape+'.rgbPP', len(colorList), *colorList, type='vectorArray')
        cmds.setAttr(pointCloudShape+'.isDynamic', 0)
        cmds.setAttr(pointCloudShape+'.forcesInWorld',0)
        cmds.setAttr(pointCloudShape+'.emissionInWorld', 0)
        mel.eval('createRenderNodeCB -asUtility "" "particleSamplerInfo" ""')
        shader = cmds.shadingNode('lambert', asShader=True)
        cmds.connectAttr('particleSamplerInfo1.rgbPP', shader + '.color')
        cmds.connectAttr(shader + '.outColor','initialParticleSE.surfaceShader', f=True)

        load_value += 20
        self.progress.setValue(load_value)
        self.progress.setVisible(True)

        #rotate for Maya
        cmds.select(pointCloud)
        cmds.rotate(-90,0, 0, r=True, p=[0,0,0])
        cmds.select(deselect=True)
        load_value += 4
        self.progress.setValue(load_value)
        self.progress.setVisible(True)
        progress_group.setVisible(False)

    def auto_vc(self):
        #Do everything
        self.quick_rotate()
        self.auto_apply_spellbook()
        self.remove_tires()
        self.remove_license_plate()

    def export(self):
        cmds.select(all=True)
        cmds.file(self.desktop_dir + '\\' + self.asset + '_OBJ', type='OBJexport', es=True, sh=True, force=True)

    def cable_gui(self):
        #Opens GUI for easy cable creation
        if cmds.window("Cable Maker", exists =True):
            cmds.deleteUI("Cable Maker")
        cmds.workspaceControl("Cable Maker", retain=False, floating=True)
        createCustomWorkspaceControlCable()

    def choose_rig(self):
        # Set Rig Path
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "Maya Files (*.mb *.ma);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_rig_edit.setText(file_path)

    def load_rig(self):
        filename = self.choose_rig_edit.text()
        cmds.file(filename, i=True)
        try:
            assetMatch = re.search('/*([a-zA-Z0-9-_ ]*)\.m[ab]', filename)
            asset = assetMatch.group(1) + '_driveControl'
        except:
            print("Couldn't retrieve asset name")
            asset = 'driveControl'
        dc = cmds.ls('*drive_ctrl', r=True)
        cmds.rename(dc, asset)
        self.rigMatch_dropdown.addItem(asset)

    def choose_mesh(self):
        # Set Mesh Path
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "OBJ Files (*.obj);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_mesh_edit.setText(file_path)

    def load_mesh(self):
        filename = self.choose_mesh_edit.text()
        cmds.file(filename, i=True)

    def loadVCData(self):
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "CSV Files (*.csv);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vcData_edit.setText(file_path)

    def loadvLocator(self):
        file_path = QFileDialog.getOpenFileName(None, "", self.desktop_dir, "MOV Files (*.mov);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vLocator_edit.setText(file_path)

    def convertVCData(self):
        #Get File Path
        filename = self.choose_vcData_edit.text()
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        #Clean CSV
        lines = [line.split(',') for line in lines]
        for i in range(0,len(lines)):
            lines[i] = [item.strip() for item in lines[i] if item != '' and item != '\n']

        #Get Vehicle List
        vehicles = []
        vehicleIndices = []
        for i in range(0,len(lines)-1):
            if 'time [ s]' in lines[i+1]:
                vehicles.append(lines[i][0])
                vehicleIndices.append(i)

        frameTotal = vehicleIndices[1] - vehicleIndices[0]

        #Create MOV Files
        for i in range(0,len(vehicles)):
            name = str(vehicles[i])
            f = open(self.desktop_dir + '/' + name + '.mov', 'w')
            for j in range(2, frameTotal):
                for k in range(0,len(lines[vehicleIndices[i] + j])):
                    f.write(lines[vehicleIndices[i] + j][k] + ' ')
                f.write('\n')

            f.close()

    def vehicleLocator(self):
        #Init Scene
        fps = self.fps_edit.currentText()
        cmds.playbackOptions(min='0sec')
        cmds.playbackOptions(ast='0sec')
        cmds.currentUnit(time=fps+'fps')
        cmds.currentTime(0)

        filename = self.choose_vLocator_edit.text()

        #Get Asset Name for Locator
        try:
            assetMatch = re.search('/*([a-zA-Z0-9-_ ]*)\.mov', filename)
            asset = assetMatch.group(1) + '_Locator'
        except:
            print("Couldn't retrieve asset name")
            asset = 'vehicleLocator'

        #Set up locator with vehicle attributes
        locator = cmds.spaceLocator(p=(0,0,0), n=asset)
        cmds.addAttr(ln='Time', at='float')
        cmds.setAttr(locator[0]+'.Time', k=True)
        cmds.addAttr(ln='Distance', at='float')
        cmds.setAttr(locator[0]+'.Distance', k=True)
        cmds.addAttr(ln='Velocity', at='float')
        cmds.setAttr(locator[0]+'.Velocity', k=True)
        cmds.addAttr(ln='Xrot', at='float')
        cmds.setAttr(locator[0]+'.Xrot', k=True)
        cmds.addAttr(ln='Yrot', at='float')
        cmds.setAttr(locator[0]+'.Yrot', k=True)
        cmds.addAttr(ln='Zrot', at='float')
        cmds.setAttr(locator[0]+'.Zrot', k=True)
        cmds.addAttr(ln='vni', at='float')
        cmds.setAttr(locator[0]+'.vni', k=True)
        cmds.addAttr(ln='vnz', at='float')
        cmds.setAttr(locator[0]+'.vnz', k=True)
        cmds.addAttr(ln='Steer', at='float')
        cmds.setAttr(locator[0]+'.Steer', k=True)
        cmds.addAttr(ln='CGx', at='float')
        cmds.setAttr(locator[0]+'.CGx', k=True)
        cmds.addAttr(ln='CGy', at='float')
        cmds.setAttr(locator[0]+'.CGy', k=True)
        cmds.addAttr(ln='CGz', at='float')
        cmds.setAttr(locator[0]+'.CGz', k=True)
        cmds.addAttr(ln='Xrad', at='float')
        cmds.setAttr(locator[0]+'.Xrad', k=True)
        cmds.addAttr(ln='Yrad', at='float')
        cmds.setAttr(locator[0]+'.Yrad', k=True)
        cmds.addAttr(ln='Zrad', at='float')
        cmds.setAttr(locator[0]+'.Zrad', k=True)
        cmds.addAttr(ln='lastV', at='float')
        cmds.setAttr(locator[0]+'.lastV', k=True)
        cmds.addAttr(ln='brake', at='float')
        cmds.setAttr(locator[0]+'.brake', k=True)

        #Connect Attr to expressions
        locName = locator[0]

        cmds.expression(s=locator[0]+".translateX="+locator[0]+".CGx", o=locator[0], ae=True, n='translateX')
        cmds.expression(s=locator[0]+".translateY="+locator[0]+".CGy", o=locator[0], ae=True, n='translateY')
        cmds.expression(s=locator[0]+".translateZ="+locator[0]+".CGz", o=locator[0], ae=True, n='translateZ')

        cmds.expression(s=locator[0]+".rotateX="+locator[0]+".Xrot", o=locator[0], ae=True, n='rotX', uc='angularOnly')
        cmds.expression(s=locator[0]+".rotateY="+locator[0]+".Yrot", o=locator[0], ae=True, n='rotY', uc='angularOnly')
        cmds.expression(s=locator[0]+".rotateZ="+locator[0]+".Zrot", o=locator[0], ae=True, n='rotZ', uc='angularOnly')

        cmds.expression(s=locator[0]+f""".lastV=`getAttr -time (frame-1)  {locName}.Velocity`;
        float $diff =  {locName}.Velocity-{locName}.lastV ;
        if ($diff < 0)""" +'{'+f'{locName}.brake=1;'+
        '}'+f'else {locName}.brake = 0;', o=locator[0], ae=True, n='brakeAndVel')

        #Load Attr from MOV file
        cmds.movIn(locName + '.Time', locName + '.Distance', locName + '.Velocity', locName + '.Xrot', locName + '.Yrot', locName + '.Zrot', locName + '.vni', locName + '.vnz', locName + '.Steer', locName + '.CGx', locName + '.CGy', locName + '.CGz', locName + ".Xrad", locName + '.Yrad', locName + '.Zrad', locName + '.lastV', locName + '.brake', f=filename)

        #Add to group
        grp = cmds.group(locName, n=locName+'_group')
        cmds.rotate('-90deg',0,0,grp,pivot=(0,0,0))
        self.vLocatorMatch_dropdown.addItem(locName)

    def pairRig2Locator(self):
        locName = self.vLocatorMatch_dropdown.currentText()
        rigName = self.rigMatch_dropdown.currentText()
        constraint = cmds.parentConstraint(locName, rigName)
        self.constraintList_dropdown.addItem(constraint[0])
        self.cgHeight_dropdown.addItem(constraint[0])
        self.parentX.setText('90')
        self.parentY.setText('0')
        self.parentZ.setText('90')
        self.constraintList_dropdown.setCurrentIndex(self.constraintList_dropdown.count() - 1)
        self.cgHeight_dropdown.setCurrentIndex(self.constraintList_dropdown.count() - 1)
        self.rotateOnConst()

    def rotateOnConst(self):
        const = self.constraintList_dropdown.currentText()
        if self.parentX.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateX', int(self.parentX.text()))
        if self.parentY.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateY', int(self.parentY.text()))
        if self.parentZ.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateZ', int(self.parentZ.text()))

    def cgHeightAdjust(self):
        obj = self.cgHeight_dropdown.currentText()
        height = self.cgHeight_edit.text()
        height = float(height)

        cmds.setAttr(obj + '.target[0].targetOffsetTranslateZ', -height)

    def wheelConst(self):
        mesh = cmds.ls('*polySurf*',type='transform', r=True)
        wheelCtrls = cmds.ls('*wheel_ctrl', r=True)

        for ctrl in wheelCtrls:
            cmds.geometryConstraint(mesh[0],ctrl)

    # --------------------------------------------------------------------------------------------------------------
    # Writes the current file path to preferences
    # --------------------------------------------------------------------------------------------------------------
    def save_last_file(self, last_file_path):
        line_found = False
        if os.path.isfile(self.pref_path):  # If the prefs file exists
            for line in fileinput.input(self.pref_path, inplace=True):
                if line.startswith(self.last_file_pref):
                    line_found = True
                    line = self.last_file_pref + "=" + last_file_path + "\n"
                sys.stdout.write(line)

        if not line_found:
            with open(self.pref_path, "a") as f:
                f.write(self.last_file_pref + "=%s\n" % last_file_path)
                f.close()

    def apply_spellbook(self):
        # Applies choosen spellbook
        spellbook_path = self.path_list[self.choose_spellbook_button.currentIndex()]
        if os.path.isfile(spellbook_path):
            selection = cmds.ls(selection=True)
            cmds.select(deselect=True)
            with open(spellbook_path) as f:
                data = f.read().splitlines()
                for spell in data:
                    spell_split = spell.split(":")
                    original = spell_split[0]
                    replacement = spell_split[1]
                    spell_type = spell_split[2]

                    # print("Replacing " + original + " " + spell_type + " with " + replacement)
                    if spell_type == "Shader":
                        cmds.hyperShade(objects=original)
                    elif spell_type == "Object":
                        cmds.select(original, replace=True)
                    else:
                        raise ValueError(
                            "Spell type invalid. Should be one of the following: " + str(self.types_model.stringList()))
                    cmds.hyperShade(assign=replacement)
                    cmds.select(deselect=True)
            cmds.select(selection)
        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Spellbook Found",
                                      "No spellbook file (*.spb) found at the specified path.")
            warning_box.exec_()

    def remove_license_plate(self):
        cmds.delete("LicPlate*")

    def make_windows_transparent(self):
        selection = cmds.ls(selection=True)

        cmds.select(deselect=True)
        cmds.hyperShade(objects="*Window*")
        windows = cmds.ls(selection=True)
        cmds.select(deselect=True)

        for window in windows:
            cmds.setAttr(window + ".aiOpaque", False)

        cmds.select(selection)

    def save(self):
        cmds.SaveSceneAs(o=True)

    def auto_apply_spellbook(self):
        # Applies choosen spellbook
        is_arnold = False
        arnold_list = cmds.ls('*Arnold*')
        if len(arnold_list) > 0:
            is_arnold = True

        if is_arnold:
            spellbook_path = self.spellbook_dir + '\\' + 'Arn2Blinn.spb'
            cmds.select(all=True)
            cmds.rotate(0, 0, -90, r=True, p=[0,0,0])
            cmds.select(deselect=True)
            cmds.delete('*aiSkyDomeLight*')

        else:
            spellbook_path = self.spellbook_dir + '\\' + 'Hum2Blinn.spb'
            cmds.select(deselect=True)

        #spellbook_path =
        if os.path.isfile(spellbook_path):
            selection = cmds.ls(selection=True)
            cmds.select(deselect=True)
            with open(spellbook_path) as f:
                data = f.read().splitlines()
                for spell in data:
                    spell_split = spell.split(":")
                    original = spell_split[0]
                    replacement = spell_split[1]
                    spell_type = spell_split[2]

                    # print("Replacing " + original + " " + spell_type + " with " + replacement)
                    if spell_type == "Shader":
                        cmds.hyperShade(objects=original)
                    elif spell_type == "Object":
                        cmds.select(original, replace=True)
                    else:
                        print('Error applying spellbook')
                    cmds.hyperShade(assign=replacement)
                    cmds.select(deselect=True)
            cmds.select(selection)

# Dev code to automatically close old windows when running
try:
    ui.close()
except:
    pass

# Show a new instance of the UI
ui = MainUI()
ui.show()
