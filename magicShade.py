import fileinput, os, sys, glob, re, math
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
from Settings import *

class ToolKit():
    #Set Up
    toolKitName = 'Magic Shade'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()
        self.dont_shrink = False
        self.asset = None

    #Buttons
    def create_controls(self):
        ##### Studio Dropdown #####
        self.choose_studio_button = QComboBox()
        studio_list = []
        self.studio_paths = []
        for file in glob.glob(studio_dir + '/*'): #finds all studios and creates dropdown
            studio_match = re.search('/studios(.*).mb', file)
            studio_name = studio_match.group(1)
            studio_list.append(studio_name[1:])
            self.studio_paths.append(file)
        for item in studio_list:
            self.choose_studio_button.addItem(item)
        self.studio_current = self.studio_paths[self.choose_studio_button.currentIndex()]

        ##### Studio Load Button #####
        self.load_studio_button = QPushButton(QIcon(icon_dir + "/template.png"), "Load Studio")
        self.load_studio_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_studio_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Text Bar #####
        self.choose_vehicle_edit = QLineEdit()
        self.choose_vehicle_edit.setPlaceholderText("Vehicle File")
        self.choose_vehicle_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.choose_vehicle_edit.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Folder Button #####
        self.choose_vehicle_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.choose_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Vehicle Button #####
        self.load_vehicle_button = QPushButton(QIcon(icon_dir + "/load.png"), "Load Vehicle")
        self.load_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_vehicle_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Specs Image #####
        self.specs_icon = QLabel()
        self.specsmap = QPixmap(icon_dir + '/dxf.png')
        self.specsmap = self.specsmap.scaled(70, 90, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.specs_icon.setPixmap(self.specsmap)

        ##### Vehicle Specs Text Bar #####
        self.choose_vehiclespec_edit = QLineEdit()
        self.choose_vehiclespec_edit.setPlaceholderText("Vehicle Specs")
        self.choose_vehiclespec_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.choose_vehiclespec_edit.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Vehicle Specs Folder Button #####
        self.choose_vehiclespec_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.choose_vehiclespec_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        #self.choose_vehiclespec_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Do Everything Button #####
        self.do_everything_button = QPushButton(QIcon(icon_dir + "/wizzardHat.png"),"Magic VC Button")
        self.do_everything_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Specs Button #####
        self.load_vehiclespec_button = QPushButton(QIcon(icon_dir + "/load.png"), "Load Vehicle Specs")
        self.load_vehiclespec_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.load_vehiclespec_button.setMinimumWidth(UI_ELEMENT_WIDTH)

        ##### Don't Scale Switch #####
        self.post_arnold_button = QCheckBox('No Scaling')

        ##### Spellbook Dropdown #####
        self.choose_spellbook_button = QComboBox()
        spellbook_list = []
        self.path_list = []
        for file in glob.glob(spellbook_dir + '/*'): #Finds all spellbooks and creates dropdown
            spell_match = re.search('/spellbooks(.*).spb', file)
            spell_name = spell_match.group(1)
            spellbook_list.append(spell_name[1:])
            self.path_list.append(file)
        for item in spellbook_list:
            self.choose_spellbook_button.addItem(item)
        self.spellbook_current = self.path_list[self.choose_spellbook_button.currentIndex()]

        ##### Apply Spellbook Button #####
        self.apply_spellbook_button = QPushButton(QIcon(icon_dir + "/cast_all.png"), "Apply Spellbook")
        self.apply_spellbook_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Rotation Buttons #####
        self.xyz_selection = QComboBox()
        direction_list = ['X','Y','Z']
        for dir in direction_list:
            self.xyz_selection.addItem(dir)
        self.left_arrow_button = QPushButton(QIcon(icon_dir + "/left"), "Rotate -90")
        self.left_arrow_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.right_arrow_button = QPushButton(QIcon(icon_dir + "/right"), "Rotate +90")
        self.right_arrow_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.quick_rotate_button = QPushButton("Quick VC Rotate")
        self.quick_rotate_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.hv_rotate_button = QPushButton("Quick HV Rotate")
        self.hv_rotate_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Scale Button #####
        self.autoScale_button = QPushButton("Auto Scale")
        self.autoScale_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Remove Tires Button #####
        self.remove_tires_button = QPushButton(QIcon(icon_dir + "/tire.png"), "Remove Tires")
        self.remove_tires_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Remove License Plate Button #####
        self.remove_license_plate_button = QPushButton(QIcon(icon_dir + "/license_plate.png"), "Remove License Plates")
        self.remove_license_plate_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Make Windows Transparent Button #####
        self.make_windows_transparent_button = QPushButton(QIcon(icon_dir + "/window.png"), "Transparent Windows (Arnold Only)")
        self.make_windows_transparent_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Export Button #####
        self.export_obj = QPushButton(QIcon(icon_dir + "/export.png"),"Export OBJ")
        self.export_obj.setMinimumHeight(UI_ELEMENT_HEIGHT)

    #Connections
    def make_connections(self):
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
        self.autoScale_button.clicked.connect(self.autoScale)
        self.remove_tires_button.clicked.connect(self.remove_tires)
        self.remove_license_plate_button.clicked.connect(self.remove_license_plate)
        self.make_windows_transparent_button.clicked.connect(self.make_windows_transparent)
        ##### Export Group #####
        self.export_obj.clicked.connect(self.export)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        ##### Studio GUI Section #####
        studio_group = QGroupBox("Studio")
        studio_layout = QVBoxLayout()
        studio_layout.addWidget(self.choose_studio_button)
        studio_layout.addWidget(self.load_studio_button)
        studio_group.setLayout(studio_layout)


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


        ##### Spellbook GUI Section #####
        spell_group = QGroupBox("Spellbook")
        spell_layout = QVBoxLayout()
        spell_layout.addWidget(self.choose_spellbook_button)
        spell_layout.addWidget(self.apply_spellbook_button)
        spell_group.setLayout(spell_layout)

        ##### Rotation GUI Section #####
        rotation_group = QGroupBox("Rotation")
        rotation_layout = QGridLayout()
        rotation_layout.addWidget(self.xyz_selection, 2, 0)
        rotation_layout.addWidget(self.left_arrow_button, 2, 1)
        rotation_layout.addWidget(self.right_arrow_button, 2, 2)
        rotation_layout.addWidget(self.quick_rotate_button, 0, 0, 1, 3)
        rotation_layout.addWidget(self.hv_rotate_button, 1, 0, 1, 3)
        rotation_group.setLayout(rotation_layout)

        ##### Extra Tools GUI Section #####
        tools_group = QGroupBox("Extra Tools")
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.autoScale_button)
        tools_layout.addWidget(self.remove_tires_button)
        tools_layout.addWidget(self.remove_license_plate_button)
        tools_layout.addWidget(self.make_windows_transparent_button)
        tools_layout.addWidget(self.export_obj)
        tools_group.setLayout(tools_layout)

        ##### Add to main layout
        self.layout.addWidget(studio_group)
        self.layout.addWidget(load_group)
        self.layout.addWidget(spell_group)
        self.layout.addWidget(rotation_group)
        self.layout.addWidget(tools_group)

    #Functions
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
        file_path = QFileDialog.getOpenFileName(None, "", vehicle_library_dir, "Vehicles (*.mb *.obj *.fbx);;All Files (*.*)")[0]
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
            cmds.file(vehicle_path, i=True)
            cmds.select(allDagObjects=True)
            new_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            diff = [x for x in new_all_objects if x not in prev_all_objects]
            cmds.group(diff, name="Vehicle")
            if self.dont_shrink == False:
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
        file_path = QFileDialog.getOpenFileName(None, "", vehiclespec_library_dir, "Vehicles (*.mb *.obj *.fbx *.ma *dxf);;All Files (*.*)")[0]
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

            cmds.file(vehiclespec_path, i=True)
            cmds.select(allDagObjects=True)
            new_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)

            diff = [x for x in new_all_objects if x not in prev_all_objects]
            group = cmds.group(diff, name="Vehiclespecs")
            cmds.move(0,0,0,group,rpr=True)
            cmds.rotate(90,90,0)
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

    def neg_rotation(self):
        #Rotate in negative direction
        direction = self.xyz_selection.currentIndex()
        if direction == 0:
            cmds.select('Vehicle*')
            cmds.rotate(-90, 0, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
        if direction == 1:
            cmds.select('Vehicle*')
            cmds.rotate(0, -90, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
        if direction == 2:
            cmds.select('Vehicle*')
            cmds.rotate(0, 0, -90, relative=True, p=[0,0,0])
            cmds.select(deselect=True)

    def pos_rotation(self):
        #Rotate in positive direction
        direction = self.xyz_selection.currentIndex()
        if direction == 0:
            cmds.select('Vehicle*')
            cmds.rotate(90, 0, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
        if direction == 1:
            cmds.select('Vehicle*')
            cmds.rotate(0, 90, 0, relative=True, p=[0,0,0])
            cmds.select(deselect=True)
        if direction == 2:
            cmds.select('Vehicle*')
            cmds.rotate(0, 0, 90, relative=True, p=[0,0,0])
            cmds.select(deselect=True)

    def quick_rotate(self):
        #Rotates to a preset for Virtual Crash asset creation
        cmds.select('Vehicle*')
        cmds.rotate(90, 0, 90, a=True, p=[0,0,0])
        cmds.select(deselect=True)

    def hv_rotate(self):
        #Rotates for a preset for HV asset creation
        cmds.select('Vehicle*')
        cmds.rotate(-90, 0, -90, a=True, p=[0,0,0])
        cmds.select(deselect=True)

    def autoScale(self):
        #Scales vehicle to size of vehicle specs
        length = cmds.getAttr('curveShape4.maxValue')
        width = cmds.getAttr('curveShape1.maxValue')

        bumpers = cmds.ls('*bumper*', '*Bumper*','*Fender*','*fender*')
        bumper_group = cmds.group(bumpers)

        cmds.select(bumper_group)

        cmds.geomToBBox(n='tempBBox', single=True, keepOriginal=True)


        bbMinX = cmds.getAttr('tempBBox.boundingBoxMinX')
        bbMaxX = cmds.getAttr('tempBBox.boundingBoxMaxX')
        bbMinZ = cmds.getAttr('tempBBox.boundingBoxMinZ')
        bbMaxZ = cmds.getAttr('tempBBox.boundingBoxMaxZ')

        cmds.delete('tempBBox')

        bbLength = bbMaxZ - bbMinZ
        bbWidth = bbMaxX - bbMinX

        dxfArea = length*width

        bbArea = bbLength*bbWidth

        scaleZ = length/bbLength
        scaleX = width/bbWidth

        currentScale = cmds.getAttr('Vehicle.scale')
        vehicle = cmds.select('Vehicle')
        cmds.scale(scaleX*currentScale[0][0], 1*currentScale[0][1], scaleZ*currentScale[0][2], vehicle)

    def remove_tires(self):
        #removes tire objects
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, g=True)
        cmds.select(deselect=True)
        coordinateList = []
        tireBB = []
        tires = []
        #Get Bounding Box Coordinates for each item
        for item in items:
            cmds.select(item)
            cmds.geomToBBox(n='tempBBox', single=True, keepOriginal=True)
            minY = cmds.getAttr('tempBBox.boundingBoxMinY')
            maxY = cmds.getAttr('tempBBox.boundingBoxMaxY')
            minX = cmds.getAttr('tempBBox.boundingBoxMinX')
            maxX = cmds.getAttr('tempBBox.boundingBoxMaxX')
            minZ = cmds.getAttr('tempBBox.boundingBoxMinZ')
            maxZ = cmds.getAttr('tempBBox.boundingBoxMaxZ')
            coords = (minX,maxX,minY,maxY,minZ,maxZ)
            coordinateList.append(coords)
            if -0.05 < minY and minY < 0.05:
                tireBB.append(coords)
                tires.append(item)
            cmds.delete('tempBBox')

        #See if BBox is inside tire, delete if True
        i = 0
        for coord in coordinateList:
            itemMinX = coord[0]
            itemMaxX = coord[1]
            itemMinY = coord[2]
            itemMaxY = coord[3]
            itemMinZ = coord[4]
            itemMaxZ = coord[5]
            for tire in tireBB:
                inY = False
                inX = False
                inZ = False
                tireMinX = tire[0]
                tireMaxX = tire[1]
                tireMinY = tire[2]
                tireMaxY = tire[3]
                tireMinZ = tire[4]
                tireMaxZ = tire[5]
                if itemMinX > tireMinX and itemMaxX < tireMaxX:
                    inX = True
                if itemMinY > tireMinY and itemMaxY < tireMaxY:
                    inY = True
                if itemMinZ > tireMinZ and itemMaxZ < tireMaxZ:
                    inZ = True
                if (inY and inX) or (inY and inZ) or (inX and inZ):
                    cmds.delete(items[i])
                    break
            i += 1
        for tire in tires:
            cmds.delete(tire)

    def remove_license_plate(self):
        cmds.delete('LicPlate*')

    def make_windows_transparent(self):
        selection = cmds.ls(selection=True)

        cmds.select(deselect=True)
        cmds.hyperShade(objects='*Window*')
        windows = cmds.ls(selection=True)
        cmds.select(deselect=True)

        for window in windows:
            cmds.setAttr(window + '.aiOpaque', False)

        cmds.select(selection)

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

                    if spell_type == "Shader":
                        cmds.hyperShade(objects=original)
                    elif spell_type == "Object":
                        cmds.select(original, replace=True)
                    else:
                        print('Error applying spellbook')
                    cmds.hyperShade(assign=replacement)
                    cmds.select(deselect=True)
            cmds.select(selection)

    def auto_vc(self):
        #Do everything
        self.remove_tires()
        self.quick_rotate()
        self.auto_apply_spellbook()
        self.remove_license_plate()

    def save(self):
        cmds.SaveSceneAs(o=True)

    def export(self):
        cmds.select(all=True)
        cmds.file(desktop_dir + '\\' + self.asset + '_OBJ', type='OBJexport', es=True, sh=True, force=True)

    def save_last_file(self, last_file_path):
        line_found = False
        if os.path.isfile(pref_path):  # If the prefs file exists
            for line in fileinput.input(pref_path, inplace=True):
                if line.startswith(last_file_pref):
                    line_found = True
                    line = last_file_pref + "=" + last_file_path + "\n"
                sys.stdout.write(line)

        if not line_found:
            with open(pref_path, "a") as f:
                f.write(last_file_pref + "=%s\n" % last_file_path)
                f.close()
