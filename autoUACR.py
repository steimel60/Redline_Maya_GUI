import fileinput, os, sys, glob, re, math
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
from Settings import *

def maya_main_window():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class ToolKit():
    #Set Up
    toolKitName = 'Vehicle Rigging'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()
        self.dialogs = list()

    #Buttons
    def create_controls(self):
        self.instructionsButton = QPushButton('Open Instructions')
        #Load Vehicle
        self.chooseVehicleEdit = QLineEdit()
        self.chooseVehicleEdit.setPlaceholderText("Vehicle File")
        self.chooseVehicleEdit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.chooseVehicleEdit.setMinimumWidth(UI_ELEMENT_WIDTH)

        self.chooseVehicleButton = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.chooseVehicleButton.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.loadVehicleButton = QPushButton(QIcon(icon_dir + "/load.png"), "Load Vehicle")
        self.loadVehicleButton.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.loadVehicleButton.setMinimumWidth(UI_ELEMENT_WIDTH)

        self.shrinkCheck = QCheckBox('Shrink Vehicle')
        self.shrinkCheck.setChecked(True)

        #Input Section
        self.axleCountLabel = QLabel('Axle Count: ')
        self.axleCountEdit = QLineEdit()
        self.axleCountEdit.setPlaceholderText('# of Axles')
        self.steeringWheelEdit = QLineEdit()
        self.steeringWheelEdit.setPlaceholderText('Steering Wheel Name')
        self.FLBrakeLabel = QLabel('Front Left: ')
        self.FLBrakeEdit = QLineEdit()
        self.FLBrakeEdit.setPlaceholderText('Brake Caliper 1 Name')
        self.FRBrakeLabel = QLabel('Front Right: ')
        self.FRBrakeEdit = QLineEdit()
        self.FRBrakeEdit.setPlaceholderText('Brake Caliper 2 Name')
        self.RLBrakeLabel = QLabel('Rear Left: ')
        self.RLBrakeEdit = QLineEdit()
        self.RLBrakeEdit.setPlaceholderText('Brake Caliper 3 Name')
        self.RRBrakeLabel = QLabel('Rear Right: ')
        self.RRBrakeEdit = QLineEdit()
        self.RRBrakeEdit.setPlaceholderText('Brake Caliper 4 Name')
        self.brakeBoxes = [self.FLBrakeEdit, self.FRBrakeEdit, self.RLBrakeEdit, self.RRBrakeEdit]

        #Do Stuff Buttons
        self.autoAlignButton = QPushButton('Align Wheels')
        self.alignSteeringWheelButton = QPushButton('Align Steering Wheel')
        self.selectRimsButton = QPushButton('Select Wheel Components')
        self.selectTiresButton = QPushButton('Select and Combine Tires')
        self.selectSWButton = QPushButton('Select Steering Wheel')
        self.selectBrakeCalipersButton = QPushButton('Select Brake Calipers')
        self.selectBodyButton = QPushButton('Select Body')

    #Connections
    def make_connections(self):
        #Instructions
        self.instructionsButton.clicked.connect(self.open_instructions)
        #Load Vehicle
        self.chooseVehicleButton.clicked.connect(self.choose_vehicle)
        self.loadVehicleButton.clicked.connect(self.load_vehicle)
        #Alignment
        self.autoAlignButton.clicked.connect(self.auto_align_tires)
        self.alignSteeringWheelButton.clicked.connect(self.auto_align_steeringwheel)
        #Select and skin
        self.selectTiresButton.clicked.connect(self.combine_and_select_tires)
        self.selectRimsButton.clicked.connect(self.select_all_wheel_components)
        self.selectBrakeCalipersButton.clicked.connect(self.select_brake_calipers)
        self.selectSWButton.clicked.connect(self.select_steering_wheel)
        self.selectBodyButton.clicked.connect(self.select_body)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        group1 = QGroupBox("Set Up")
        setUpGroup = QGridLayout()
        setUpGroup.addWidget(self.instructionsButton, 0,0,1,5)
        setUpGroup.addWidget(self.chooseVehicleButton, 1,0)
        setUpGroup.addWidget(self.chooseVehicleEdit, 1,1,1,2)
        setUpGroup.addWidget(self.shrinkCheck, 1,3)
        setUpGroup.addWidget(self.loadVehicleButton, 1,4)
        setUpGroup.addWidget(self.axleCountLabel, 2,0)
        setUpGroup.addWidget(self.axleCountEdit, 2,1)
        setUpGroup.addWidget(self.autoAlignButton, 2,2,1,3)
        group1.setLayout(setUpGroup)

        group2 = QGroupBox("Optional Accessories")
        accessoryGroup = QGridLayout()
        accessoryGroup.addWidget(self.steeringWheelEdit, 0,0)
        accessoryGroup.addWidget(self.alignSteeringWheelButton, 0,1)
        accessoryGroup.addWidget(self.FLBrakeEdit, 1,0,1,2)
        accessoryGroup.addWidget(self.FRBrakeEdit, 2,0,1,2)
        accessoryGroup.addWidget(self.RLBrakeEdit, 3,0,1,2)
        accessoryGroup.addWidget(self.RRBrakeEdit, 4,0,1,2)
        group2.setLayout(accessoryGroup)

        group3 = QGroupBox("Selection Tools")
        selectionGroup = QVBoxLayout()
        selectionGroup.addWidget(self.selectBrakeCalipersButton)
        selectionGroup.addWidget(self.selectSWButton)
        selectionGroup.addWidget(self.selectRimsButton)
        selectionGroup.addWidget(self.selectTiresButton)
        selectionGroup.addWidget(self.selectBodyButton)
        group3.setLayout(selectionGroup)

        #Add groups to tab
        self.layout.addWidget(group1)
        self.layout.addWidget(group2)
        self.layout.addWidget(group3)

    #Functions
    def combine_meshes(self, meshes, name):
        cmds.polyUnite(meshes, n=name)

    def select_all_tires(self):
        #Get rid of current selection
        cmds.select(deselect=True)
        #Get Tires
        tires = self.get_all_tires()
        #Select Tires
        cmds.select(tires)

        return tires

    def get_all_tires(self, forward_axis='z', axle_count = 2):
        #Returns tire names as list in order: FL, FR, RL, RR
        tire_list = [None for i in range(0,axle_count)]
        #Check all objects in car list
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, v=True)
        items = [x for x in items if 'shape' not in x.lower()]
        cmds.select(deselect=True)
        minHeights = [None for i in range(0,axle_count*2)]
        tires = [None for i in range(0,axle_count*2)]
        tireBB = [None for i in range(0,axle_count*2)]
        #Get Bounding Box Coordinates for each item
        for item in items:
            minY = cmds.getAttr(f'{item}.boundingBoxMinY')
            maxY = cmds.getAttr(f'{item}.boundingBoxMaxY')
            minX = cmds.getAttr(f'{item}.boundingBoxMinX')
            maxX = cmds.getAttr(f'{item}.boundingBoxMaxX')
            minZ = cmds.getAttr(f'{item}.boundingBoxMinZ')
            maxZ = cmds.getAttr(f'{item}.boundingBoxMaxZ')
            coords = (minX,maxX,minY,maxY,minZ,maxZ)
            #find lowest points of vehicle
            if None in minHeights:
                i = minHeights.index(None)
                minHeights[i] = minY
                tires[i] = item
                tireBB[i] = coords
            elif minY < max(minHeights):
                i = minHeights.index(max(minHeights))
                minHeights[i] = minY
                tires[i] = item
                tireBB[i] = coords
        #Return Tires
        return tires

    def combine_and_select_tires(self):
        tires = self.select_all_tires()
        self.combine_meshes(tires, 'tires')

    def auto_align_tires(self):
        try:
            tires = self.get_left_tires(axle_count=int(self.axleCountEdit.text()))
        except:
            print('\nAXLE COUNT NOT VALID - ASSUMING 2 AXLE VEHICLE\n')
            tires = self.get_left_tires()
        row = 0
        for tire in tires:
            rim = self.get_rim(tire)
            if row == 0:
                self.align_to_tire(tire, rim, 'UACR_fmd_ctrl')
            elif row != len(tires) - 1:
                self.align_to_tire(tire, rim, f'UACR_mmd{row}_ctrl')
            else:
                self.align_to_tire(tire,rim,'UACR_rmd_ctrl')
            row += 1

    def auto_align_steeringwheel(self):
        wheel = self.steeringWheelEdit.text()
        wheel_ctrl = 'UACR_swa_ctrl'
        #Wheel box
        maxX = cmds.getAttr(f'{wheel}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
        minX = cmds.getAttr(f'{wheel}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
        minY = cmds.getAttr(f'{wheel}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
        maxY = cmds.getAttr(f'{wheel}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
        minZ = cmds.getAttr(f'{wheel}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
        maxZ = cmds.getAttr(f'{wheel}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
        #get wheel center
        centerX = (minX + maxX)/2
        centerY = (minY + maxY)/2
        centerZ = (minZ + maxZ)/2
        #move wheel ctrl
        cmds.move(centerX,centerY,centerZ,wheel_ctrl)

    def get_rim(self, tire):
        #returns the widest object that is inside a tire - hopefully that's the rim
        #Get tire box
        tireMinX = cmds.getAttr(f'{tire}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
        tireMaxX = cmds.getAttr(f'{tire}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
        tireMinY = cmds.getAttr(f'{tire}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
        tireMaxY = cmds.getAttr(f'{tire}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
        tireMinZ = cmds.getAttr(f'{tire}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
        tireMaxZ = cmds.getAttr(f'{tire}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
        #Check all objects in car list
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, v=True)
        items = [x for x in items if 'shape' not in x.lower()]
        cmds.select(deselect=True)
        #Track max height
        maxY = None
        rim = None
        #Get Bounding Box Coordinates for each item
        for item in items:
            inY = False
            inX = False
            inZ = False
            inTire = False
            #get item bounds
            itemMinY = cmds.getAttr(f'{item}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
            itemMaxY = cmds.getAttr(f'{item}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
            itemCenterY = (itemMinY+itemMaxY)/2
            itemMinX = cmds.getAttr(f'{item}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
            itemMaxX = cmds.getAttr(f'{item}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
            itemCenterX = (itemMinX+itemMaxX)/2
            itemMinZ = cmds.getAttr(f'{item}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
            itemMaxZ = cmds.getAttr(f'{item}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
            itemCenterZ = (itemMinZ+itemMaxZ)/2
            #Check if item bounds are in tire bounds
            if itemCenterX > tireMinX and itemCenterX < tireMaxX:
                inX = True
            if itemCenterY > tireMinY and itemCenterY < tireMaxY:
                inY = True
            if itemCenterZ > tireMinZ and itemCenterZ < tireMaxZ:
                inZ = True
            if inX and inY and inZ:
                inTire = True
            if inTire:
                if maxY == None:
                    maxY = itemMaxY
                    rim = item
                elif maxY < itemMaxY:
                    maxY = itemMaxY
                    rim = item
        return rim

    def align_to_tire(self, tire, rim, ctrl):
        #Get tire box
        maxX = cmds.getAttr(f'{tire}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
        minX = cmds.getAttr(f'{tire}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
        minY = cmds.getAttr(f'{tire}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
        maxY = cmds.getAttr(f'{tire}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
        minZ = cmds.getAttr(f'{tire}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
        maxZ = cmds.getAttr(f'{tire}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
        #get tire center
        centerY = (minY + maxY)/2
        centerZ = (minZ + maxZ)/2
        #get ctrl location
        ctrlLoc = (maxX, centerY, centerZ)
        #Tire width
        width = (maxX - minX)/cmds.getAttr('UACR_root_ctrl.globalScale')
        #Get Wheel Box
        maxXRim = cmds.getAttr(f'{rim}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
        minXRim = cmds.getAttr(f'{rim}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
        minYRim = cmds.getAttr(f'{rim}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
        maxYRim = cmds.getAttr(f'{rim}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
        minZRim = cmds.getAttr(f'{rim}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
        maxZRim = cmds.getAttr(f'{rim}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
        #get tire wall
        wall = (maxY - maxYRim)/cmds.getAttr('UACR_root_ctrl.globalScale')
        #Set Ctrl Settings
        cmds.move(maxX, centerY, centerZ, f'{ctrl}', ws=True)
        cmds.setAttr(f'{ctrl}.tireWidth',width)
        cmds.setAttr(f'{ctrl}.tireSideWall',wall)

    def get_left_tires(self, axle_count = 2):
        #Returns tire names as list in order: FL, FR, RL, RR
        tire_list = [None for i in range(0,axle_count)]
        #Check all objects in car list
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, v=True)
        items = [x for x in items if 'shape' not in x.lower()]
        cmds.select(deselect=True)
        minHeights = [None for i in range(0,axle_count*2)]
        tires = [None for i in range(0,axle_count*2)]
        tireBB = [None for i in range(0,axle_count*2)]
        #Get Bounding Box Coordinates for each item
        for item in items:
            minY = cmds.getAttr(f'{item}.boundingBoxMinY')
            maxY = cmds.getAttr(f'{item}.boundingBoxMaxY')
            minX = cmds.getAttr(f'{item}.boundingBoxMinX')
            maxX = cmds.getAttr(f'{item}.boundingBoxMaxX')
            minZ = cmds.getAttr(f'{item}.boundingBoxMinZ')
            maxZ = cmds.getAttr(f'{item}.boundingBoxMaxZ')
            coords = (minX,maxX,minY,maxY,minZ,maxZ)
            #find lowest points of vehicle
            if None in minHeights:
                i = minHeights.index(None)
                minHeights[i] = minY
                tires[i] = item
                tireBB[i] = coords
            elif minY < max(minHeights):
                i = minHeights.index(max(minHeights))
                minHeights[i] = minY
                tires[i] = item
                tireBB[i] = coords
        #Get tire positions
        counter = 0
        for coords in tireBB:
            current_tire = tires[counter]
            #Counters, will count number of tires behind or to right of current tire
            forward_count = 0
            left_count = 0
            #track if tire is on left side
            is_left_tire = False
            #compare to other tires
            counter2 = 0
            for other_coords in tireBB:
                if coords[5] > other_coords[5]:
                    forward_count += 1
                if coords[1] > other_coords[1]:
                    left_count += 1
                counter2 += 1
            #get tire loc
            if left_count >= axle_count:
                is_left_tire = True
            axle_row = axle_count - (forward_count//2)
            axle_index = (axle_row - 1)
            if is_left_tire:
                #put left tires in wheel list
                tire_list[axle_index] = current_tire
            counter += 1

        return tire_list

    def get_all_wheel_components(self, tire):
        #returns all parts within the bounds of the wheels
        components = []
        #Get tire box
        tireMinX = cmds.getAttr(f'{tire}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
        tireMaxX = cmds.getAttr(f'{tire}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
        tireMinY = cmds.getAttr(f'{tire}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
        tireMaxY = cmds.getAttr(f'{tire}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
        tireMinZ = cmds.getAttr(f'{tire}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
        tireMaxZ = cmds.getAttr(f'{tire}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
        #Check all objects in car list
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, v=True)
        items = [x for x in items if 'shape' not in x.lower()]
        cmds.select(deselect=True)
        #Get Bounding Box Coordinates for each item
        for item in items:
            if item == tire:
                continue
            inY = False
            inX = False
            inZ = False
            inTire = False
            #get item bounds
            itemMinY = cmds.getAttr(f'{item}.boundingBoxMinY')*cmds.getAttr('Vehicle.scaleY')
            itemMaxY = cmds.getAttr(f'{item}.boundingBoxMaxY')*cmds.getAttr('Vehicle.scaleY')
            itemCenterY = (itemMinY+itemMaxY)/2
            itemMinX = cmds.getAttr(f'{item}.boundingBoxMinX')*cmds.getAttr('Vehicle.scaleX')
            itemMaxX = cmds.getAttr(f'{item}.boundingBoxMaxX')*cmds.getAttr('Vehicle.scaleX')
            itemCenterX = (itemMinX+itemMaxX)/2
            itemMinZ = cmds.getAttr(f'{item}.boundingBoxMinZ')*cmds.getAttr('Vehicle.scaleZ')
            itemMaxZ = cmds.getAttr(f'{item}.boundingBoxMaxZ')*cmds.getAttr('Vehicle.scaleZ')
            itemCenterZ = (itemMinZ+itemMaxZ)/2
            #Check if item bounds are in tire bounds
            if itemCenterX > tireMinX and itemCenterX < tireMaxX:
                inX = True
            if itemCenterY > tireMinY and itemCenterY < tireMaxY:
                inY = True
            if itemCenterZ > tireMinZ and itemCenterZ < tireMaxZ:
                inZ = True
            if inX and inY and inZ:
                inTire = True
            if inTire:
                components.append(item)

        return components

    def select_all_wheel_components(self):
        all_wheel_components = []
        #Get tires
        tires = self.get_all_tires()
        #Get everything in tire bounds
        for tire in tires:
            individual_components = self.get_all_wheel_components(tire)
            for component in individual_components:
                all_wheel_components.append(component)
        #Clear selection
        cmds.select(deselect = True)
        #Select components
        cmds.select(all_wheel_components)

    def select_brake_calipers(self):
        #Get brakes
        brakes = [brakeBox.text() for brakeBox in self.brakeBoxes if brakeBox.text() != '']
        #Clear selection
        cmds.select(deselect=True)
        #select brakes
        cmds.select(brakes)

    def select_steering_wheel(self):
        #Clear selection
        cmds.select(deselect=True)
        #Select steering wheel
        if self.steeringWheelEdit.text() != '':
            cmds.select(self.steeringWheelEdit.text())

    def select_body(self):
        cmds.select('Vehicle*', hierarchy=True)
        cmds.select('Vehicle*', deselect=True, hierarchy=False)
        items = cmds.ls(sl=True, v=True)
        items = [x for x in items if 'shape' not in x.lower()]
        cmds.select(deselect=True)
        cmds.select(items)

    def open_instructions(self):
        dialog = InstructionsPopUp()
        self.dialogs.append(dialog)
        dialog.show()

    def choose_vehicle(self):
        #Sets vehicle path
        file_path = QFileDialog.getOpenFileName(None, "", vehicle_library_dir, "Vehicles (*.mb *.obj *.fbx);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.chooseVehicleEdit.setText(file_path)

    def load_vehicle(self):
        # Loads choosen vehicle
        vehicle_path = self.chooseVehicleEdit.text()
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
            if self.shrinkCheck.checkState():
                cmds.scale(0.0328, 0.0328, 0.0328, absolute=True, pivot=(0, 0, 0))
            cmds.select(deselect=True)
            asset_match = re.search('.*/([a-zA-Z_0-9\(\)]*).*\.m[ab]', vehicle_path)
            if asset_match != None:
                self.asset = asset_match.group(1)
                cmds.file(rename=self.asset)
        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Vehicle Found", "No vehicle file found at the specified path.")
            warning_box.exec_()

class InstructionsPopUp(QDialog):
    #--------------------------------------------------------------------------------------------------------------
    #                                            Create GUI Window
    #--------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window()):
        super(InstructionsPopUp, self).__init__(parent)

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('UACR Automation Instructions')
        self.setWindowIcon(QIcon(icon_dir + "/RedlineLogo.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.label_list = []
        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout


    def create_controls(self):
        self.main_label = QLabel('UACR Automation Instructions')
        self.main_label.setAlignment(Qt.AlignCenter)
        self.label_list.append(self.main_label)
        self.steps = QLabel('''
        1. Open UACR window, choose wheels number, and click load
        2. Change UACR_root_ctrl "Global Scale" to 0.0328 or to match vehicle scale
        3. Hide the chassis by clicking "CHASSIS" button on UACR window
        4. Import your vehicle
        5. Make sure vehicle is facing positive Z direction and wheels are on the ground
        6. Enter the number of axles your vehicle has into the axle count text box
        7. Click "Align Wheels" button

        OPTIONAL

            STEERING WHEEL SET UP
            - Seperate mesh if needed
            - If seperated, move meshes out of transform/sub-group into Vehicle group and hide the transform
            - Copy name of steering wheel mesh into "Steering Wheel" Name text box
            - Click "Align Steering Wheel" button
            - Rotate UACR_swa_ctrl to align with steering wheel mesh

            BRAKE CALIPER SET UP
            - Copy names of brake calipers in to Brake Name text boxes

            SKINNING SET UP
            - Choose which method you want for skinning, leave setting on SK for FBX export

        8. Hide the UACR rig with the ctrl+H hotkey
        9. Move any meshes located in a transform/sub-group into the vehicle group, hide any transforms/sub-groups
        10a. If your model has brake calipers, click "Select Brake Calipers" on Redline window
        10b. Click "CALIPER" button on UACR window
        11a. If you have you steering wheel set up, click "Select Steering Wheel" on Redline window
        11b. Click "STEERING WHEEL" button on UACR window
        12a. Click "Select Wheel Components" button on Redline window
        12b. Click "WHEEL" button on UACR window
        13a. Click "Select and Combine Tires" button on Redline window
        13b. Click "TIRE" button on UACR window
        14a. Click "Select Body" button on Redline window
        14b. Click "BODY" button in UACR window
        15. Unhide UACR rig, delete empty vehicle group
        ''')
        self.label_list.append(self.steps)

    def create_layout(self):
        mainLayout = QVBoxLayout()
        for step in self.label_list:
            mainLayout.addWidget(step)

        self.setLayout(mainLayout)
