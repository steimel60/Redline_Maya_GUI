import fileinput, os, sys, glob, re, math, shutil
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
    toolKitName = 'Vehicle Motion'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()

    #Buttons
    def create_controls(self):
        ##### Load Assets #####
        self.refresh_button = QPushButton('Load/Refresh Assets')

        ##### Active Locator Drop Down #####
        self.LocatorLabel = QLabel()
        self.LocatorLabel.setText('Active Locator:')
        self.activeLocator_dropdown = QComboBox()
        locators = cmds.ls('*_Locator')
        for locator in locators:
            self.activeLocator_dropdown.addItem(locator)

        ##### Active Rig Dropdown #####
        self.RigLabel = QLabel()
        self.RigLabel.setText('Active Rig:')
        self.activeRig_dropdown = QComboBox()
        rigs = cmds.ls('*_TopNode*')
        rigs.extend(cmds.ls('*:*_TopNode*'))
        for rig in rigs:
            self.activeRig_dropdown.addItem(rig)

        ##### Make Constraints #####
        self.pairRig2Locator_button = QPushButton('Pair Rig to Locator')

        ##### Edit Constraint Rotation #####
        self.parentX = QLineEdit()
        self.parentX.setPlaceholderText("Rotate X")
        self.parentY = QLineEdit()
        self.parentY.setPlaceholderText("Rotate Y")
        self.parentZ = QLineEdit()
        self.parentZ.setPlaceholderText("Rotate Z")
        self.rotateOnConst_button = QPushButton('Rotate on Constraint')

        ##### Edit Constraint Translation #####
        self.cgHeight_edit = QLineEdit()
        self.cgHeight_edit.setPlaceholderText('CoG Height')
        self.cgXOffset_edit = QLineEdit()
        self.cgXOffset_edit.setPlaceholderText('CoG X Offset')
        self.cgYOffset_edit = QLineEdit()
        self.cgYOffset_edit.setPlaceholderText('CoG Y Offset')
        self.cgAdjust_button = QPushButton('Adjust CoG Offset')

        ##### Light Rigging #####
        self.lightName_edit = QLineEdit()
        self.lightName_edit.setPlaceholderText('Light Name')
        self.lightIntensity = QLineEdit()
        self.lightIntensity.setPlaceholderText('Intensity')
        self.pairLight_button = QPushButton('Pair Light to Locator')

        ##### Save Pre-Bake #####
        self.preBakeSave_button = QPushButton('Save Pre-Baked File')

        ##### Wheel Constraint #####
        self.siteName_edit = QLineEdit()
        self.siteName_edit.setPlaceholderText('Site Name')
        self.wheelConstr_button = QPushButton('Constrain wheels to mesh')

        ##### Bake Button #####
        self.bakeButton = QPushButton('Bake Root Joint')

        ##### Bake Settings #####
        self.bakeStart_label = QLabel()
        self.bakeStart_label.setText('Start Frame:')
        self.bakeStart_edit = QLineEdit()
        self.bakeStart_edit.setPlaceholderText('Ex:  0')
        self.bakeStop_label = QLabel()
        self.bakeStop_label.setText('Stop Frame:')
        self.bakeStop_edit = QLineEdit()
        self.bakeStop_edit.setPlaceholderText('Ex:  2500')
        self.vehicleFBX_label = QLabel('File Name: ')
        self.vehicleFBX = QLineEdit()
        self.vehicleFBX.setPlaceholderText('FBX File Name')

        ##### Export FBX #####
        #skeleton
        self.vehicleSkeleton_label = QLabel('V_Skeleton Name: ')
        self.vehicleSkeletonName = QLineEdit()
        self.vehicleSkeletonName.setPlaceholderText('Skeleton Name')
        self.vehicleSkeletonExport_button = QPushButton('Export Skeleton')
        #animation
        #self.updateSkeletonList_button = QPushButton('Update Skeleton List')
        self.skeletonPair_label = QLabel('Skeleton')
        self.skeletonPair_dropdown = QComboBox()
        self.exportFBX_button = QPushButton('Export Selected Root Joint Animation')

        ##### Blend Shapes #####
        self.blendNode_edit = QLineEdit()
        self.blendNode_edit.setPlaceholderText('Blend Node Name - Ex: Initial Impact')
        self.blendGroupName_edit = QLineEdit()
        self.blendGroupName_edit.setPlaceholderText('Create Group Name')
        self.createBlendGroup_button = QPushButton('Group Shapes')

    #Connections
    def make_connections(self):
        ##### Refresh Section #####
        self.refresh_button.clicked.connect(self.refreshAssets)
        ##### Vehicle Rigging #####
        self.pairRig2Locator_button.clicked.connect(self.pairRig2Locator)
        self.rotateOnConst_button.clicked.connect(self.rotateOnConst)
        self.cgAdjust_button.clicked.connect(self.cgAdjustOffset)
        self.pairLight_button.clicked.connect(self.pairLight2Brakes)
        self.preBakeSave_button.clicked.connect(self.save)
        self.wheelConstr_button.clicked.connect(self.wheelConst)

        ##### Bake Joint #####
        self.bakeButton.clicked.connect(self.bake)

        ##### Export Buttons #####
        self.exportFBX_button.clicked.connect(self.exportFBX)
        self.vehicleSkeletonExport_button.clicked.connect(self.export_vehicle_skeleton)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        ##### Active Locator and Rig #####
        activeItems_group = QGroupBox("Active Locator and Rig")
        activeItems_Layout = QGridLayout()

        activeItems_Layout.addWidget(self.LocatorLabel,0,0)
        activeItems_Layout.addWidget(self.activeLocator_dropdown,0,1,1,2)
        activeItems_Layout.addWidget(self.RigLabel,1,0)
        activeItems_Layout.addWidget(self.activeRig_dropdown,1,1,1,2)
        activeItems_Layout.addWidget(self.refresh_button,3,0,1,3)

        activeItems_group.setLayout(activeItems_Layout)

        ##### Vehicle Rigging #####
        vLocator_group = QGroupBox("Vehicle Rigging")
        vLocator_layout = QGridLayout()

        vLocator_layout.addWidget(self.pairRig2Locator_button,0,0,1,4)

        vLocator_layout.addWidget(self.parentX,1,0)
        vLocator_layout.addWidget(self.parentY,1,1)
        vLocator_layout.addWidget(self.parentZ,1,2)
        vLocator_layout.addWidget(self.rotateOnConst_button,1,3)

        vLocator_layout.addWidget(self.cgXOffset_edit,2,0)
        vLocator_layout.addWidget(self.cgYOffset_edit,2,1)
        vLocator_layout.addWidget(self.cgHeight_edit,2,2)
        vLocator_layout.addWidget(self.cgAdjust_button,2,3)

        vLocator_layout.addWidget(self.lightName_edit,3,0,1,2)
        vLocator_layout.addWidget(self.lightIntensity,3,2)
        vLocator_layout.addWidget(self.pairLight_button,3,3)

        vLocator_layout.addWidget(self.preBakeSave_button, 4,0,1,4)

        vLocator_layout.addWidget(self.siteName_edit, 5,0,1,2)
        vLocator_layout.addWidget(self.wheelConstr_button, 5,2,1,2)
        vLocator_group.setLayout(vLocator_layout)

        ##### Skel Export #####
        skelExport_group = QGroupBox("Skeleton Export")
        skelExport_layout = QGridLayout()

        skelExport_layout.addWidget(self.vehicleSkeleton_label, 0,0)
        skelExport_layout.addWidget(self.vehicleSkeletonName, 0,1,1,2)
        skelExport_layout.addWidget(self.vehicleSkeletonExport_button, 1,0,1,3)

        skelExport_group.setLayout(skelExport_layout)

        ##### Bake Section #####
        bake_group = QGroupBox("Bake Animation")
        bake_layout = QGridLayout()

        bake_layout.addWidget(self.bakeStart_label,0,0)
        bake_layout.addWidget(self.bakeStart_edit,0,1)
        bake_layout.addWidget(self.bakeStop_label,0,2)
        bake_layout.addWidget(self.bakeStop_edit,0,3)
        bake_layout.addWidget(self.bakeButton,1,0,1,4)

        bake_group.setLayout(bake_layout)

        ##### Export Section #####
        export_group = QGroupBox("Export Group")
        export_layout = QGridLayout()

        export_layout.addWidget(self.vehicleFBX_label, 0,0)
        export_layout.addWidget(self.vehicleFBX, 0,1,1,3)
        export_layout.addWidget(self.exportFBX_button, 1,0,1,4)

        export_group.setLayout(export_layout)
        #Add groups to tab
        self.layout.addWidget(activeItems_group)
        self.layout.addWidget(vLocator_group)
        self.layout.addWidget(skelExport_group)
        self.layout.addWidget(bake_group)
        self.layout.addWidget(export_group)

    #Functions
    def refreshAssets(self):
        #Clear dropboxes
        self.activeRig_dropdown.clear()
        self.activeLocator_dropdown.clear()
        #Get all items in scene
        allRigs = cmds.ls('*_TopNode*')
        allRigs.extend(cmds.ls('*:*_TopNode*'))
        allLocs = cmds.ls('*_Locator')
        #Add items to dropdown
        for rig in allRigs:
            self.activeRig_dropdown.addItem(rig)
        for loc in allLocs:
            self.activeLocator_dropdown.addItem(loc)

    def pairRig2Locator(self):
        #Constrain rig to vehicle locator
        locName = self.activeLocator_dropdown.currentText()
        rigName = self.activeRig_dropdown.currentText()
        #Find root and drive control
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_ctrl'):
                root = item
            if item.endswith('driveControl'):
                dc = item
        #Constrain root control to locator for location
        rootconst = cmds.parentConstraint(locName, root)
        cmds.delete(rootconst) #delete constraint
        cmds.select(root)
        cmds.rotate(0,0,0) #set to 0 rotation
        cmds.select(deselect=True)
        #Constrain drive control to locator
        constraint = cmds.parentConstraint(locName, dc)
        self.parentX.setText('90')
        self.parentY.setText('0')
        self.parentZ.setText('90')
        #Match locator steer data to drivecontrol
        cmds.connectAttr(locName+'.steer',dc+'.steer')
        #Find root joint
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                rootJoint = item
        #Add brake data to root joint
        cmds.select(rootJoint)
        cmds.addAttr(ln='brake', at='float', k=True)
        cmds.connectAttr(f'{locName}.brake',f'{rootJoint}.brake')
        cmds.select(deselect=True)
        #rotate on constraint
        self.rotateOnConst()

    def pairLight2Brakes(self):
        #Pair lights to MOV data
        rigName = self.activeRig_dropdown.currentText()
        locName = self.activeLocator_dropdown.currentText()
        #Find root joint
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                root = item
        #light name and intensity
        light = self.lightName_edit.text()
        intensity = self.lightIntensity.text()
        #Pair light intensity to brake boolean
        cmds.expression(s=f'{light}.intensity = {root}.brake * {intensity};')
        #Reset textboxes
        self.lightName_edit.setText('')
        self.lightIntensity.setText('')

    def rotateOnConst(self):
        #Rotate rig on parent constraint
        rigName = self.activeRig_dropdown.currentText()
        #Find drive control
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('driveControl'):
                dc = item
        #Find parent constraint
        cmds.select(dc, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if 'parentConstraint' in item:
                const = item
        #Rotation Boxes
        rotX = self.parentX.text()
        rotY = self.parentY.text()
        rotZ = self.parentZ.text()
        #Empty box catch
        if rotX == '':
            rotX = cmds.getAttr(const + '.target[0].targetOffsetRotateX')
            self.parentX.setText(str(rotX))
        if rotY == '':
            rotY = cmds.getAttr(const + '.target[0].targetOffsetRotateY')
            self.parentY.setText(str(rotY))
        if rotZ == '':
            rotZ = cmds.getAttr(const + '.target[0].targetOffsetRotateZ')
            self.parentZ.setText(str(rotZ))
        #Str to Float
        rotX = float(rotX)
        rotY = float(rotY)
        rotZ = float(rotZ)
        #Adjust rotation
        if self.parentX.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateX', rotX)
        if self.parentY.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateY', rotY)
        if self.parentZ.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateZ', rotZ)

    def cgAdjustOffset(self):
        #Adjust CoG offset
        rigName = self.activeRig_dropdown.currentText()
        #Find drive control
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('driveControl'):
                dc = item
        #Find parent constraint
        cmds.select(dc, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if 'parentConstraint' in item:
                const = item
        #Offset Textboxes
        xOffset = self.cgXOffset_edit.text()
        yOffset = self.cgYOffset_edit.text()
        height = self.cgHeight_edit.text()
        #Catch blank boxes
        if xOffset == '':
            xOffset = cmds.getAttr(const + '.target[0].targetOffsetTranslateX')
            self.cgXOffset_edit.setText(str(xOffset))
        if yOffset == '':
            yOffset = cmds.getAttr(const + '.target[0].targetOffsetTranslateY')
            self.cgYOffset_edit.setText(str(yOffset))
        if height == '':
            height = cmds.getAttr(const + '.target[0].targetOffsetTranslateZ')
            self.cgHeight_edit.setText(str(height))
        #str to float
        xOffset = float(xOffset)
        yOffset = float(yOffset)
        height = float(height)
        #Adjust Offset
        cmds.setAttr(const + '.target[0].targetOffsetTranslateX', xOffset)
        cmds.setAttr(const + '.target[0].targetOffsetTranslateY', yOffset)
        cmds.setAttr(const + '.target[0].targetOffsetTranslateZ', height)

    def wheelConst(self):
        #constrain wheels to mesh
        site = self.siteName_edit.text()
        mesh = cmds.ls(site, r=True)
        wheelCtrls = cmds.ls('*wheel_ctrl', r=True)
        for ctrl in wheelCtrls:
            cmds.geometryConstraint(mesh[0],ctrl)
        #Reset textboxes
        self.siteName_edit.setText('')

    def bake(self):
        if self.bakeStart_edit.text() == '' or self.bakeStop_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check Bake Frames", "Please enter a valid for Start/Stop frames.")
            warning_box.exec_()
        else:
            #Bake animation
            start = self.bakeStart_edit.text()
            stop = self.bakeStop_edit.text()
            rigName = self.activeRig_dropdown.currentText()
            #Select Root Joint
            cmds.select(rigName, hierarchy=True)
            groupList = cmds.ls(sl=True)
            cmds.select(deselect=True)
            for item in groupList:
                if item.endswith('root_jt'):
                    root = item
            root = cmds.ls(root)
            cmds.select(deselect=True)
            cmds.select(root, hi=True)
            cmds.select(deselect=True)
            cmds.bakeResults(root, hi='below', shape=True, sm=True, time=(start,stop))
            #Reset textboxes
            self.bakeStart_edit.setText('')
            self.bakeStop_edit.setText('')

    def export_vehicle_skeleton(self):
        #Exports root joint for Unreal Engine
        rigName = self.activeRig_dropdown.currentText()
        #get variables
        filename = f"vSKEL_{self.vehicleSkeletonName.text()}"
        exportLocation = desktop_dir + '/' + filename
        #select root joint and mesh
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                root = item
        root = cmds.ls(root)
        cmds.select(deselect=True)
        cmds.select('*:*Render', hi=True)
        cmds.select('*:*Chassis', hi=True, deselect=True)
        cmds.select('*:*ParentYourMeshHere', hi=True, deselect=True)
        cmds.select('*:*Render', hi=False, deselect=True)
        geo = cmds.ls(sl=True)
        #what to export
        export = root + geo
        #ignore semicolon to avoid naming error
        colonIndex = 0
        for i in range(0,len(root)):
            if root[i] == ':':
                colonIndex = i + 1
        #rename shaders for unreal organization
        cmds.select(export)
        cmds.hyperShade("",smn = True)
        shaders = cmds.ls(sl = True)
        for shader in shaders:
            cmds.rename(shader,f'MAT_{filename[5:]}_{shader}')
        cmds.select(deselect=True)
        cmds.select(export)
        #fix unicode error
        exportLocation = exportLocation.replace('\\','/')
        #export with blendshape settings
        mel.eval('FBXResetExport')
        mel.eval('FBXExportTangents -v 1')
        mel.eval('FBXExportSmoothingGroups -v 1')
        mel.eval('FBXExportSmoothMesh -v 1')
        mel.eval('FBXExportSkins -v 1')
        mel.eval('FBXExportShapes -v 1')
        mel.eval('FBXExportConstraints -v 1')
        mel.eval('FBXExportSkeletonDefinitions -v 1')
        mel.eval(f'FBXExport -f "{exportLocation}.fbx" -s')
        #Check if unreal project
        #self.unrealExport2(filename,'v_skeleton',f'{exportLocation}.fbx')
        #reset text boxes
        self.vehicleSkeletonName.setText('')

    def exportFBX(self):
        #Exports root joint for Unreal Engine
        rigName = self.activeRig_dropdown.currentText()
        #get variables
        filename = f"vANIM_{self.vehicleFBX.text()}"
        exportLocation = desktop_dir + '/' + filename
        skeleton = self.skeletonPair_dropdown.currentText()
        #do it
        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                root = item
        root = cmds.ls(root)
        cmds.select(deselect=True)
        export = root
        #Catch colon in name
        colonIndex = 0
        for i in range(0,len(root)):
            if root[i] == ':':
                colonIndex = i + 1
        #rename shaders for unreal
        cmds.select(export)
        #fix unicode error
        exportLocation = exportLocation.replace('\\','/')
        #export with preset settings
        mel.eval('FBXResetExport')
        mel.eval('FBXExportConstraints -v 1')
        mel.eval('FBXExportSkeletonDefinitions -v 1')
        mel.eval(f'FBXExport -f "{exportLocation}.fbx" -s')
        #Reset textboxes
        self.vehicleFBX.setText('')

    def save(self):
        cmds.SaveSceneAs(o=True)
