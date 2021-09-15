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
    toolKitName = 'Vehicle Rigging'
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
        self.activeLocator_dropdown.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Active Rig Dropdown #####
        self.RigLabel = QLabel()
        self.RigLabel.setText('Active Rig:')
        self.activeRig_dropdown = QComboBox()
        rigs = cmds.ls('*_TopNode*')
        rigs.extend(cmds.ls('*:*_TopNode*'))
        for rig in rigs:
            self.activeRig_dropdown.addItem(rig)
        self.activeRig_dropdown.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Unreal Option #####
        self.unreal_checkbox = QCheckBox('Unreal Project')
        self.unrealProjName_edit = QLineEdit()
        self.unrealProjName_edit.setPlaceholderText('New Project')
        self.unrealProjList_dropdown = QComboBox()
        self.unrealProjList_dropdown.setLineEdit(self.unrealProjName_edit)
        self.unrealProjList_dropdown.addItem('')
        for file in glob.glob(UNREAL_PROJECT_DIR + '/mayaProjects/*'): #finds all projects and creates dropdown
            try:
                projectMatch = re.search('/mayaProjects(.*).txt', file)
                proj = projectMatch.group(1)[1:]
                self.unrealProjList_dropdown.addItem(proj)
            except:
                pass
        self.unrealProjName_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Make Constraints #####
        self.pairRig2Locator_button = QPushButton('Pair Rig to Locator')
        self.pairRig2Locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Edit Constraint Rotation #####
        self.parentX = QLineEdit()
        self.parentX.setPlaceholderText("Rotate X")
        self.parentX.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.parentY = QLineEdit()
        self.parentY.setPlaceholderText("Rotate Y")
        self.parentY.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.parentZ = QLineEdit()
        self.parentZ.setPlaceholderText("Rotate Z")
        self.parentZ.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rotateOnConst_button = QPushButton('Rotate on Constraint')
        self.rotateOnConst_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Edit Constraint Translation #####
        self.cgHeight_edit = QLineEdit()
        self.cgHeight_edit.setPlaceholderText('CoG Height')
        self.cgHeight_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.cgXOffset_edit = QLineEdit()
        self.cgXOffset_edit.setPlaceholderText('CoG X Offset')
        self.cgXOffset_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.cgYOffset_edit = QLineEdit()
        self.cgYOffset_edit.setPlaceholderText('CoG Y Offset')
        self.cgYOffset_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.cgAdjust_button = QPushButton('Adjust CoG Offset')
        self.cgAdjust_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Light Rigging #####
        self.lightName_edit = QLineEdit()
        self.lightName_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.lightName_edit.setPlaceholderText('Light Name')
        self.lightIntensity = QLineEdit()
        self.lightIntensity.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.lightIntensity.setPlaceholderText('Intensity')
        self.pairLight_button = QPushButton('Pair Light to Locator')
        self.pairLight_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Save Pre-Bake #####
        self.preBakeSave_button = QPushButton('Save Pre-Baked File')
        self.preBakeSave_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Wheel Constraint #####
        self.siteName_edit = QLineEdit()
        self.siteName_edit.setPlaceholderText('Site Name')
        self.siteName_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.wheelConstr_button = QPushButton('Constrain wheels to mesh')
        self.wheelConstr_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Bake Button #####
        self.bakeButton = QPushButton('Bake Root Joint and Geometry')
        self.bakeButton.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Bake Settings #####
        self.bakeStart_label = QLabel()
        self.bakeStart_label.setText('Start Frame:')
        self.bakeStart_edit = QLineEdit()
        self.bakeStart_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.bakeStart_edit.setPlaceholderText('Ex:  0')
        self.bakeStop_label = QLabel()
        self.bakeStop_label.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.bakeStop_label.setText('Stop Frame:')
        self.bakeStop_edit = QLineEdit()
        self.bakeStop_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.bakeStop_edit.setPlaceholderText('Ex:  2500')
        self.vehicleFBX_label = QLabel('File Name: ')
        self.vehicleFBX = QLineEdit()
        self.vehicleFBX.setPlaceholderText('FBX File Name')

        ##### Export FBX #####
        self.exportFBX_button = QPushButton('Export Selected Root Joint Animation')
        self.exportFBX_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Blend Shapes #####
        self.blendNode_edit = QLineEdit()
        self.blendNode_edit.setPlaceholderText('Blend Node Name - Ex: Initial Impact')
        self.blendNode_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.blendGroupName_edit = QLineEdit()
        self.blendGroupName_edit.setPlaceholderText('Create Group Name')
        self.blendGroupName_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.createBlendGroup_button = QPushButton('Group Shapes')
        self.createBlendGroup_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

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
        self.exportFBX_button.clicked.connect(self.exportFBX)

        ##### Blend Shapes #####
        self.createBlendGroup_button.clicked.connect(self.createBlendGroup)

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

        ##### Blend Shapes #####
        blend_group = QGroupBox("Blend Shapes")
        blend_layout = QGridLayout()

        blend_layout.addWidget(self.blendNode_edit, 0,0)
        blend_layout.addWidget(self.blendGroupName_edit, 0,1)
        blend_layout.addWidget(self.createBlendGroup_button, 1,0,1,2)

        blend_group.setLayout(blend_layout)

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

        export_layout.addWidget(self.unreal_checkbox, 0,0)
        export_layout.addWidget(self.unrealProjList_dropdown, 0,1,1,3)
        export_layout.addWidget(self.vehicleFBX_label, 1,0)
        export_layout.addWidget(self.vehicleFBX, 1,1,1,3)
        export_layout.addWidget(self.exportFBX_button,4,0,1,4)

        export_group.setLayout(export_layout)
        #Add groups to tab
        self.layout.addWidget(activeItems_group)
        self.layout.addWidget(vLocator_group)
        self.layout.addWidget(blend_group)
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

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_ctrl'):
                root = item
            if item.endswith('driveControl'):
                dc = item
        rootconst = cmds.parentConstraint(locName, root)

        cmds.delete(rootconst)
        cmds.select(root)
        cmds.rotate(0,0,0)
        cmds.select(deselect=True)
        constraint = cmds.parentConstraint(locName, dc)
        self.parentX.setText('90')
        self.parentY.setText('0')
        self.parentZ.setText('90')

        cmds.connectAttr(locName+'.steer',dc+'.steer')

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                rootJoint = item

        cmds.select(rootJoint)
        cmds.addAttr(ln='brake', at='float', k=True)
        cmds.connectAttr(f'{locName}.brake',f'{rootJoint}.brake')
        cmds.select(deselect=True)

        self.rotateOnConst()

    def pairLight2Brakes(self):
        #Pair lights to MOV data
        rigName = self.activeRig_dropdown.currentText()
        locName = self.activeLocator_dropdown.currentText()

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                root = item

        light = self.lightName_edit.text()
        intensity = self.lightIntensity.text()

        cmds.expression(s=f'{light}.intensity = {root}.brake * {intensity};')
        self.lightName_edit.setText('')
        self.lightIntensity.setText('')

    def rotateOnConst(self):
        #Rotate rig on parent constraint
        rigName = self.activeRig_dropdown.currentText()

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('driveControl'):
                dc = item

        cmds.select(dc, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if 'parentConstraint' in item:
                const = item

        rotX = self.parentX.text()
        rotY = self.parentY.text()
        rotZ = self.parentZ.text()

        if rotX == '':
            rotX = cmds.getAttr(const + '.target[0].targetOffsetRotateX')
            self.parentX.setText(str(rotX))
        if rotY == '':
            rotY = cmds.getAttr(const + '.target[0].targetOffsetRotateY')
            self.parentY.setText(str(rotY))
        if rotZ == '':
            rotZ = cmds.getAttr(const + '.target[0].targetOffsetRotateZ')
            self.parentZ.setText(str(rotZ))

        rotX = float(rotX)
        rotY = float(rotY)
        rotZ = float(rotZ)

        if self.parentX.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateX', rotX)
        if self.parentY.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateY', rotY)
        if self.parentZ.text() != '':
            cmds.setAttr(const + '.target[0].targetOffsetRotateZ', rotZ)

    def cgAdjustOffset(self):
        #Adjust CoG offset
        rigName = self.activeRig_dropdown.currentText()

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('driveControl'):
                dc = item

        cmds.select(dc, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if 'parentConstraint' in item:
                const = item

        xOffset = self.cgXOffset_edit.text()
        yOffset = self.cgYOffset_edit.text()
        height = self.cgHeight_edit.text()

        if xOffset == '':
            xOffset = cmds.getAttr(const + '.target[0].targetOffsetTranslateX')
            self.cgXOffset_edit.setText(str(xOffset))
        if yOffset == '':
            yOffset = cmds.getAttr(const + '.target[0].targetOffsetTranslateY')
            self.cgYOffset_edit.setText(str(yOffset))
        if height == '':
            height = cmds.getAttr(const + '.target[0].targetOffsetTranslateZ')
            self.cgHeight_edit.setText(str(height))

        xOffset = float(xOffset)
        yOffset = float(yOffset)
        height = float(height)

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

        self.siteName_edit.setText('')

    def createBlendGroup(self):
        #Connect blend shape to root joint for Unreal export
        blendNode = self.blendNode_edit.text()
        groupName = self.blendGroupName_edit.text()
        rigName = self.activeRig_dropdown.currentText()

        cmds.select(rigName, hierarchy=True)
        groupList = cmds.ls(sl=True)
        cmds.select(deselect=True)
        for item in groupList:
            if item.endswith('root_jt'):
                rootJoint = item

        attrs = cmds.listAttr(blendNode, m=True)
        presets = ['message', 'caching', 'frozen', 'isHistoricallyInteresting', 'nodeState', 'binMembership', 'input', 'output', 'originalGeometry', 'envelopeWeightsList', 'envelope', 'function', 'fchild', 'map64BitIndices', 'topologyCheck', 'origin', 'baseOrigin', 'baseOriginX', 'baseOriginY', 'baseOriginZ', 'targetOrigin', 'targetOriginX', 'targetOriginY', 'targetOriginZ', 'parallelBlender', 'useTargetCompWeights', 'supportNegativeWeights', 'paintWeights', 'offsetDeformer', 'offsetX', 'offsetY', 'offsetZ', 'localVertexFrame', 'midLayerId', 'midLayerParent', 'nextNode', 'parentDirectory', 'targetDirectory', 'deformationOrder', 'attributeAliasList']

        cmds.select(rootJoint)
        cmds.addAttr(ln=groupName, dv=0, minValue=0, maxValue=1, k=True)

        for attr in attrs:
            is_preset = False
            for preset in presets:
                if preset in attr:
                    is_preset = True
            if not is_preset:
                shape = attr
                cmds.expression(s=f'{blendNode}.{shape} = {rootJoint}.{groupName}')

        self.blendNode_edit.setText('')
        self.blendGroupName_edit.setText('')

    def bake(self):
        if self.bakeStart_edit.text() == '' or self.bakeStop_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check Bake Frames", "Please enter a valid for Start/Stop frames.")
            warning_box.exec_()
        else:
            #Bake animation
            start = self.bakeStart_edit.text()
            stop = self.bakeStop_edit.text()
            rigName = self.activeRig_dropdown.currentText()

            cmds.select(rigName, hierarchy=True)
            groupList = cmds.ls(sl=True)
            cmds.select(deselect=True)
            for item in groupList:
                if item.endswith('root_jt'):
                    root = item
                if item.endswith('_Render'):
                    renderGroup = item
            root = cmds.ls(root)
            cmds.select(deselect=True)
            cmds.select(renderGroup, hi=True)
            cmds.select('*:*Chassis', hi=True, deselect=True)
            cmds.select('*:*ParentYourMeshHere', hi=True, deselect=True)
            cmds.select('*:*Render', hi=False, deselect=True)
            geo = cmds.ls(sl=True)
            blendShapes = cmds.ls('*blendShape*')

            bakeMe = geo + root + blendShapes

            cmds.select(bakeMe, hi=True)
            export = cmds.ls(sl=True)
            cmds.select(deselect=True)

            cmds.bakeResults(bakeMe, hi='below', shape=True, sm=True, time=(start,stop))

            self.bakeStart_edit.setText('')
            self.bakeStop_edit.setText('')

    def exportFBX(self):
        #Exports root joint for Unreal Engine
        rigName = self.activeRig_dropdown.currentText()
        #get variables
        filename = f"VEH_{self.vehicleFBX.text()}"
        exportLocation = desktop_dir + '/' + filename
        #do it
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

        export = root + geo

        colonIndex = 0
        for i in range(0,len(root)):
            if root[i] == ':':
                colonIndex = i + 1

        cmds.select(export)
        cmds.hyperShade("",smn = True)
        shaders = cmds.ls(sl = True)
        for shader in shaders:
            cmds.rename(shader,f'MAT_{filename[4:]}_{shader}')
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

        self.unrealExport(filename,'vehicle',f'{exportLocation}.fbx')
        self.vehicleFBX.setText('')

    def unrealExport(self, assetName, assetType, assetPath):
        #get variables
        projName = self.unrealProjList_dropdown.currentText()
        assetName = assetName+'.fbx'
        newLine = f'{assetName},{assetType},{assetPath}'
        #Make txt file
        if self.unreal_checkbox.checkState():
            file = projName+'.txt'
            if not os.path.exists(UNREAL_PROJECT_DIR+'/mayaProjects'):
                os.makedirs(UNREAL_PROJECT_DIR+'/mayaProjects')
            #Create File if none exists
            if not os.path.exists(UNREAL_PROJECT_DIR+'/mayaProjects/'+file):
                f=open(UNREAL_PROJECT_DIR+'/mayaProjects/'+file,'w')
                f.close()
            #Get lines currently in file
            f = open(UNREAL_PROJECT_DIR+'/mayaProjects/'+file,'r+')
            lines = f.readlines()
            lines = [line.strip().split(',') for line in lines]
            f.close()
            #Replace lines if overwriting, append if new asset
            f = open(UNREAL_PROJECT_DIR+'/mayaProjects/'+file,'w')
            written = False
            for i in range(len(lines)):
                if lines[i][0] == assetName:
                    lines[i] = newLine.split(',')
                    written = True
            if not written:
                lines.append(newLine.split(','))
            #Update File
            for line in lines:
                f.write(f"{line[0]},{line[1]},{line[2]}\n")
            f.close()

            self.get_unreal_export_folders(assetName,assetType,assetPath,projName)

            infoBox = QMessageBox(QMessageBox.Information, "Unreal Export Successful", f"{assetName} has been added to your {projName} Project File.\nUse Redline Unreal Engine script to load as {assetType} in Unreal Engine.")
            infoBox.exec_()

    def get_unreal_export_folders(self,assetName,assetType,assetPath,projName):
        projFolder = f'{MAYA_EXPORT_DIR}/{projName}'
        subFolders = [f'{projFolder}/SkeletalMeshes',f'{projFolder}/Animations',f'{projFolder}/Vehicles']
        #Check for project Folder
        if not os.path.exists(projFolder):
            os.makedirs(projFolder)
            for folder in subFolders:
                os.makedirs(folder)
        #Check for subFolders if project does exist
        else:
            for folder in subFolders:
                if not os.path.exists(folder):
                    os.makedirs(folder)
        #Find where to place fbx
        if 'skeleton' in assetType:
            targetFolder = subFolders[0]
        elif 'animation' in assetType:
            targetFolder = subFolders[1]
        elif 'vehicle' in assetType:
            targetFolder = subFolders[2]
        shutil.copy(assetPath,targetFolder)
        #create reference file
        self.create_ur_reference_file(assetName,assetType,targetFolder,projFolder)

    def create_ur_reference_file(self,assetName,assetType,targetFolder,projFolder):
        #fix unicode error
        projFolder = projFolder.replace('\\','/')
        assetPath = projFolder.replace('\\','/')
        file = 'REFERENCES.txt'
        newLine = f'{assetName},{assetType},{targetFolder}/{assetName}'
        #Create File if none exists
        if not os.path.exists(f'{projFolder}/{file}'):
            f=open(f'{projFolder}/{file}','w')
            f.close()
        #Get lines currently in file
        f = open(f'{projFolder}/{file}','r+')
        lines = f.readlines()
        lines = [line.strip().split(',') for line in lines]
        f.close()
        #Replace lines if overwriting, append if new asset
        f = open(f'{projFolder}/{file}','w')
        written = False
        for i in range(len(lines)):
            if lines[i][0] == assetName:
                lines[i] = newLine.split(',')
                written = True
        if not written:
            lines.append(newLine.split(','))
        #Update File
        for line in lines:
            f.write(f"{line[0]},{line[1]},{line[2]}\n")
        f.close()

    def save(self):
        cmds.SaveSceneAs(o=True)
