import fileinput, os, sys, glob, re, math, shutil
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
    toolKitName = 'Character Rigging'

    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()
        self.dialogs = list()

    #Buttons
    def create_controls(self):
        ##### File Load #####
        self.chooseCharacterData_edit = QLineEdit()
        self.chooseCharacterData_edit.setPlaceholderText("Character Data File")
        self.chooseCharacterData_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.chooseCharacterData_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.chooseCharacterData_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Import Character Locators #####
        self.tPoseLocators_button = QPushButton('Import T/A Pose Locators')
        self.tPoseLocators_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.importCharacter_button = QPushButton('Import Animation Locators')
        self.importCharacter_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Skele Rig File #####
        self.popUp_button = QPushButton('Create Rig Pairing Template')

        self.chooseSkeleRig_edit = QLineEdit()
        self.chooseSkeleRig_edit.setPlaceholderText("Rig File")
        self.chooseSkeleRig_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.chooseSkeleRig_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.chooseSkeleRig_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.refreshCharAssets_button = QPushButton('Load/Refresh SKEL Assets')

        ##### Load Character #####
        self.loadCharacter_button = QPushButton('Load Character')
        self.loadCharacter_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Active Assets #####
        self.charLoc_label = QLabel()
        self.charLoc_label.setText('Animation Locator Group: ')
        self.activeCharLocs_dropdown = QComboBox()
        charLocs = cmds.ls('*Animation_Locators*')
        for cLoc in charLocs:
            self.activeCharLocs_dropdown.addItem(cLoc)
        self.activeCharLocs_dropdown.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.idleLocs_label = QLabel()
        self.idleLocs_label.setText('Idle Locator Group: ')
        self.idleLocs_dropdown = QComboBox()
        idleLocs = cmds.ls('*idle_Locators*')
        for iLoc in idleLocs:
            self.idleLocs_dropdown.addItem(iLoc)
        self.idleLocs_dropdown.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.activeChar_label = QLabel()
        self.activeChar_label.setText('Active Character: ')
        self.activeCharacter_edit = QLineEdit()
        self.activeCharacter_edit.setPlaceholderText('Character Joint Hierarchy - Top Node')
        self.activeCharacter_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

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

        ##### Rig DropDown #####
        self.skeleRig_label = QLabel()
        self.skeleRig_label.setText('Character Rig Type: ')
        self.skeleRig_dropdown = QComboBox()
        skel_list = []
        self.skelePath_list = []
        for file in glob.glob(skeleton_dir + '/*'): #Finds all spellbooks and creates dropdown
            skel_match = re.search('skelFiles(.*).SKEL', file)
            skel_name = skel_match.group(1)
            skel_list.append(skel_name[1:])
            self.skelePath_list.append(file)
        for item in skel_list:
            self.skeleRig_dropdown.addItem(item)

        ##### Alignment Confirmation #####
        self.alignment_checkbox = QCheckBox('Alignment Complete')

        ##### Pair to Locators #####
        self.charRig2Loc_button = QPushButton('Pair Character to Locators')
        self.charRig2Loc_button.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.add_motion_button = QPushButton('Pair Idle Locators to Animated Locators')
        self.add_motion_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### General Export #####
        self.generalExport_button = QPushButton('Non-Metahuman Export')

        ##### Export Metahuman #####
        self.metahumanFBXName = QLineEdit()
        self.metahumanFBXName.setPlaceholderText('FBX File Name')

        self.metaStartLabel = QLabel('Bake Start: ')
        self.metahumanBakeStart = QLineEdit()
        self.metahumanBakeStart.setPlaceholderText('Start Frame')

        self.metaEndLabel = QLabel('Bake Start: ')
        self.metahumanBakeEnd = QLineEdit()
        self.metahumanBakeEnd.setPlaceholderText('End Frame')

        self.bodyJoints_label = QLabel('Control Rig: ')
        self.bodyJoints_dropdown = QComboBox()
        bodyJoints = cmds.ls('*Body_joints*')
        self.activeJoints = []
        for joint in bodyJoints:
            self.bodyJoints_dropdown.addItem(joint)
            self.activeJoints.append(joint)
        self.bodyJoints_dropdown.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.selectControlRig_button = QPushButton('Select Control Rig')
        self.exportControlRig_button = QPushButton('Export Control Rig')

    #Connections
    def make_connections(self):
        ##### Charcater Import #####
        self.chooseCharacterData_button.clicked.connect(self.choose_character_data)
        self.tPoseLocators_button.clicked.connect(self.load_idle_locs)
        self.importCharacter_button.clicked.connect(self.load_animated_locators)
        self.chooseSkeleRig_button.clicked.connect(self.choose_char_rig)
        self.loadCharacter_button.clicked.connect(self.load_char_rig)

        ##### SKEL Files #####
        self.popUp_button.clicked.connect(self.popUp)
        self.refreshCharAssets_button.clicked.connect(self.refreshCharAssets)

        ##### Character Rigging #####
        self.charRig2Loc_button.clicked.connect(self.pair_char_2_locs)
        self.add_motion_button.clicked.connect(self.add_motion)

        ##### General Export #####
        self.generalExport_button.clicked.connect(self.exportPopUp)

        ##### Metahuman Export #####
        self.selectControlRig_button.clicked.connect(self.selectControRig)
        self.exportControlRig_button.clicked.connect(self.metahumanExport)

    #Layout
    def create_layout(self):
        self.layout = QVBoxLayout()
        ##### File Management #####
        fileGroup = QGroupBox("File Management")
        fileLayout = QGridLayout()

        fileLayout.addWidget(self.chooseCharacterData_button, 0,0)
        fileLayout.addWidget(self.chooseCharacterData_edit, 0,1,1,3)
        fileLayout.addWidget(self.tPoseLocators_button, 1,0,1,2)
        fileLayout.addWidget(self.importCharacter_button, 1,2,1,2)
        fileLayout.addWidget(self.chooseSkeleRig_button, 2,0)
        fileLayout.addWidget(self.chooseSkeleRig_edit, 2,1,1,3)
        fileLayout.addWidget(self.loadCharacter_button, 3,0,1,4)

        fileGroup.setLayout(fileLayout)
        self.layout.addWidget(fileGroup)

        ##### Char Rigging #####
        charRig_group = QGroupBox("Character Rigging")
        charRig_layout = QGridLayout()

        charRig_layout.addWidget(self.popUp_button, 0,0,1,2)
        charRig_layout.addWidget(self.refreshCharAssets_button, 0,2,1,2)
        charRig_layout.addWidget(self.idleLocs_label, 1,0,1,1)
        charRig_layout.addWidget(self.idleLocs_dropdown, 1,1,1,3)

        charRig_layout.addWidget(self.activeChar_label, 2,0,1,1)
        charRig_layout.addWidget(self.activeCharacter_edit, 2,1,1,3)

        charRig_layout.addWidget(self.skeleRig_label, 3,0,1,1)
        charRig_layout.addWidget(self.skeleRig_dropdown, 3,1,1,3)

        charRig_layout.addWidget(self.alignment_checkbox, 4,0,1,1)
        charRig_layout.addWidget(self.charRig2Loc_button, 4,1,1,3)

        charRig_layout.addWidget(self.charLoc_label, 5,0,1,1)
        charRig_layout.addWidget(self.activeCharLocs_dropdown, 5,1,1,3)
        charRig_layout.addWidget(self.add_motion_button, 6,0,1,4)

        charRig_group.setLayout(charRig_layout)
        self.layout.addWidget(charRig_group)

        ##### Metahuman Export #####
        mhExport_group = QGroupBox("Metahuman Export")
        mhExport_layout = QGridLayout()

        mhExport_layout.addWidget(self.bodyJoints_label, 0,0)
        mhExport_layout.addWidget(self.bodyJoints_dropdown, 0,1,1,3)
        mhExport_layout.addWidget(self.selectControlRig_button, 1,0,1,4)
        mhExport_layout.addWidget(self.metaStartLabel, 2,0)
        mhExport_layout.addWidget(self.metahumanBakeStart, 2,1)
        mhExport_layout.addWidget(self.metaEndLabel, 2,2)
        mhExport_layout.addWidget(self.metahumanBakeEnd, 2,3)
        mhExport_layout.addWidget(self.unreal_checkbox, 3,0)
        mhExport_layout.addWidget(self.unrealProjList_dropdown, 3,1,1,3)
        mhExport_layout.addWidget(self.metahumanFBXName, 4,0,1,2)
        mhExport_layout.addWidget(self.exportControlRig_button, 4,2,1,2)
        mhExport_layout.addWidget(self.generalExport_button, 5,0,1,4)

        mhExport_group.setLayout(mhExport_layout)
        self.layout.addWidget(mhExport_group)

    #Functions
    def choose_character_data(self):
        #Set path to character data
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "CSV Files (*.csv);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.chooseCharacterData_edit.setText(file_path)

    def choose_char_rig(self):
        #Set path to character data
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "Char Files (*.ma *.mb);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.chooseSkeleRig_edit.setText(file_path)

    def load_char_rig(self):
        filename = self.chooseSkeleRig_edit.text()

        cmds.file(filename, i=True)
        joints = cmds.ls('*Body_joints*')
        for joint in joints:
            if joint not in self.activeJoints:
                self.bodyJoints_dropdown.addItem(joint)
                self.activeJoints.append(joint)

        self.chooseSkeleRig_edit.setText('')

    def load_animated_locators(self):
        #Load data from set character path
        filename = self.chooseCharacterData_edit.text()
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        #Clean CSV
        lines = [line.split(',') for line in lines]
        for i in range(0,len(lines)):
            lines[i] = [item.strip() for item in lines[i] if item != '' and item != '\n']

        #Get joint list
        parts = []
        partIndices = []
        partStrings = ['femur', 'foot', 'head', 'hip', 'arm', 'leg', 'neck', 'torso']
        for i in range(0,len(lines)):
            if len(lines[i]) == 15:
                lines[i].pop(8) #if steer data included, exclude it
            for part in partStrings:
                if len(lines[i]) == 1:
                    if part in lines[i][0]:
                        parts.append(lines[i][0])
                        partIndices.append(i)

        frameTotal = partIndices[1] - partIndices[0]

        #Create MOV Files
        jointFiles = []
        for i in range(0,len(parts)):
            name = str(parts[i])
            name = name.split(' ')
            new_name = ''
            for n in range(0,len(name)):
                new_name += name[n]
            name = new_name
            f = open(desktop_dir + '/' + name + '.mov', 'w')
            jointFiles.append(desktop_dir + '/' + name + '.mov')
            for j in range(2, frameTotal):
                for k in range(0,len(lines[partIndices[i] + j])):
                    f.write(lines[partIndices[i] + j][k] + ' ')
                f.write('\n')

        f.close()

        charList = cmds.ls('Animation_Locators*')
        charNum = len(charList)

        locators = []
        colors = [(1,1,0),(1,1,0),(.2,1,.6),(.2,1,.6),(1,0,0),(1,.502,0),(1,.6,.6),(1,0,.498),(.502,1,0),(.502,1,0),(.498,0,1),(1,.6,.6),(1,0,.498),(0,0,1)]
        i = 0
        cmds.currentTime(0)

        for joint in jointFiles:
            locator = cmds.spaceLocator(p=(0,0,0), n=f'anim{str(charNum)}_{parts[i]}')
            locName = locator[0]
            locators.append(locName)
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
            cmds.addAttr(ln='steer', at='float')
            cmds.setAttr(locator[0]+'.steer', k=True)
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

            cmds.movIn(locName + '.Time', locName + '.Distance', locName + '.Velocity', locName + '.rotateX', locName + '.rotateY', locName + '.rotateZ', locName + '.vni', locName + '.vnz', locName + '.translateX', locName + '.translateY', locName + '.translateZ', locName + ".Xrad", locName + '.Yrad', locName + '.Zrad', f=joint)
            cmds.setAttr(f'{locName}Shape.overrideEnabled', 1)
            cmds.setAttr(f'{locName}Shape.overrideRGBColors', 1)
            cmds.setAttr(f'{locName}Shape.overrideColorR',colors[i][0])
            cmds.setAttr(f'{locName}Shape.overrideColorG',colors[i][1])
            cmds.setAttr(f'{locName}Shape.overrideColorB',colors[i][2])
            cmds.setAttr(f'{locName}.scaleX', .2)
            cmds.setAttr(f'{locName}.scaleY', .2)
            cmds.setAttr(f'{locName}.scaleZ', .2)
            i += 1

        #Add to group
        grp = cmds.group(locators, n='Animation_Locators')
        self.activeCharLocs_dropdown.addItem(grp)
        cmds.rotate('-90deg',0,0,grp,pivot=(0,0,0))
        self.chooseCharacterData_edit.setText('')

    def load_idle_locs(self):
        #Load data from set character path
        filename = self.chooseCharacterData_edit.text()
        f = open(filename, "r")
        lines = f.readlines()
        f.close()

        #Clean CSV
        lines = [line.split(',') for line in lines]
        for i in range(0,len(lines)):
            lines[i] = [item.strip() for item in lines[i] if item != '' and item != '\n']

        #Get joint list
        parts = []
        partDicts = []
        partIndices = []
        partStrings = ['femur', 'foot', 'head', 'hip', 'arm', 'leg', 'neck', 'torso']
        colors = [(1,1,0),(1,1,0),(.2,1,.6),(.2,1,.6),(1,0,0),(1,.502,0),(1,.6,.6),(1,0,.498),(.502,1,0),(.502,1,0),(.498,0,1),(1,.6,.6),(1,0,.498),(0,0,1)]
        for i in range(0,len(lines)):
            if len(lines[i]) == 15:
                lines[i].pop(8) #if steer data included, exclude it
            for part in partStrings:
                if len(lines[i]) == 1:
                    if part in lines[i][0]:
                        parts.append(lines[i][0])
                        partIndices.append(i)

        #Create Locators
        charList = cmds.ls('idle_Locators*')
        charNum = len(charList)
        locators = []
        for i in range(0,len(parts)):
            name = parts[i]
            index = partIndices[i]
            firstLine = lines[index+2]
            pos = (firstLine[8],firstLine[9],firstLine[10])
            rot = (firstLine[3],firstLine[4],firstLine[5])
            loc = cmds.spaceLocator(p=(0,0,0), n=f'idle{str(charNum)}_{name}')
            locName = loc[0]
            locators.append(locName)
            cmds.setAttr(f'{locName}.translateX', float(pos[0]))
            cmds.setAttr(f'{locName}.translateY', float(pos[1]))
            cmds.setAttr(f'{locName}.translateZ', float(pos[2]))
            cmds.setAttr(f'{locName}.rotateX', float(rot[0]))
            cmds.setAttr(f'{locName}.rotateY', float(rot[1]))
            cmds.setAttr(f'{locName}.rotateZ', float(rot[2]))
            cmds.setAttr(f'{locName}.scaleX', .2)
            cmds.setAttr(f'{locName}.scaleY', .2)
            cmds.setAttr(f'{locName}.scaleZ', .2)
            cmds.setAttr(f'{locName}Shape.overrideEnabled', 1)
            cmds.setAttr(f'{locName}Shape.overrideRGBColors', 1)
            cmds.setAttr(f'{locName}Shape.overrideColorR',colors[i][0])
            cmds.setAttr(f'{locName}Shape.overrideColorG',colors[i][1])
            cmds.setAttr(f'{locName}Shape.overrideColorB',colors[i][2])

        #Group Locators
        grp = cmds.group(locators, n='idle_Locators')
        cmds.rotate('-90deg',0,0,grp,pivot=(0,0,0))
        self.idleLocs_dropdown.addItem(grp)
        self.chooseCharacterData_edit.setText('')

    def pair_char_2_locs(self):
        if self.alignment_checkbox.checkState():
            #Get Active Assets
            actLocs = self.idleLocs_dropdown.currentText()
            cmds.select(actLocs, hi=True)
            locs = cmds.ls(sl=True)
            locs = [x for x in locs if ('Character' not in x) and 'Shape' not in x]
            cmds.select(deselect=True)

            skelSelection = self.skeleRig_dropdown.currentText()
            for file in glob.glob(skeleton_dir + '/*'):
                if skelSelection in file:
                    f = open(file, 'r')
                    skelJoints = f.readlines()
                    f.close()

            for i in range(0,len(skelJoints)):
                skelJoints[i] = skelJoints[i].strip()
                skelJoints[i] = skelJoints[i].split(',')

            actChar = self.activeCharacter_edit.text()
            cmds.select(actChar, hi=True)
            charItems = cmds.ls(sl=True)
            cmds.select(deselect=True)
            jointInfo = []
            for skel in skelJoints:
                for loc in locs:
                    if skel[0] in loc:
                        skel[0] = loc
                for item in charItems:
                    if skel[1] in item:
                        skel[1] = item
                if (skel[2]=='False') and (skel[3]=='True'):
                    const = cmds.parentConstraint(skel[0], skel[1], mo=True, st=['x','y','z'])
                elif (skel[2]=='False') and (skel[3]=='False'):
                    const = cmds.parentConstraint(skel[0], skel[1], mo=True, st=['x','y','z'], sr=['x','y','z'])
                elif (skel[2]=='True') and (skel[3]=='False'):
                    const = cmds.parentConstraint(skel[0], skel[1], mo=True, sr=['x','y','z'])
                else:
                    const = cmds.parentConstraint(skel[0], skel[1], mo=True)

            self.activeCharacter_edit.setText('')

        else:
            warning_box = QMessageBox(QMessageBox.Warning, "Check Alignment", "Please confirm Joint and Locator alignment before pairing.")
            warning_box.exec_()

    def add_motion(self):
        #Get Groups
        idleGroup = self.idleLocs_dropdown.currentText()
        animGroup = self.activeCharLocs_dropdown.currentText()

        #Get Individual Locators
        cmds.select(idleGroup, hi=True)
        idleLocs = cmds.ls(sl=True)
        idleLocs = [x for x in idleLocs if ('Locators' not in x) and ('Shape' not in x)]
        cmds.select(deselect=True)

        cmds.select(animGroup, hi=True)
        animLocs = cmds.ls(sl=True)
        animLocs = [x for x in animLocs if ('Locators' not in x) and ('Shape' not in x)]
        cmds.select(deselect=True)

        #Pair Locators
        for i in range(0,len(animLocs)):
            cmds.parentConstraint(animLocs[i],idleLocs[i],mo=False)

    def selectControRig(self):
        rig = self.bodyJoints_dropdown.currentText()
        cmds.select(rig, r=True)

    def metahumanExport(self):
        if self.metahumanFBXName.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check File Name", "Please enter a valid FBX file name.")
            warning_box.exec_()
        elif self.metahumanBakeStart.text() == '' or self.metahumanBakeEnd.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check Bake Frames", "Please enter a valid for Start/Stop frames.")
            warning_box.exec_()

        else:
            #get variables
            filename = self.metahumanFBXName.text()
            exportLocation = desktop_dir + '/' + filename
            bakeStart = int(self.metahumanBakeStart.text())
            bakeEnd = int(self.metahumanBakeEnd.text())
            #fix unicode error
            exportLocation = exportLocation.replace('\\','/')
            #export with metahuman settings
            mel.eval('FBXResetExport')
            mel.eval('FBXExportInputConnections -v 0')
            mel.eval('FBXExportBakeComplexAnimation -v 1')
            mel.eval(f'FBXExportBakeComplexStart -v {bakeStart}')
            mel.eval(f'FBXExportBakeComplexEnd -v {bakeEnd}')
            mel.eval(f'FBXExport -f "{exportLocation}.fbx" -s')

            self.unrealExport(self.metahumanFBXName.text(), 'MHControlRig')
            self.metahumanFBXName.setText('')
            self.metahumanBakeStart.setText('')
            self.metahumanBakeEnd.setText('')

    def popUp(self):
        dialog = skelePopUp()
        self.dialogs.append(dialog)
        dialog.show()

    def exportPopUp(self):
        dialog = rigExportPopUp(calledBy=self)
        self.dialogs.append(dialog)
        dialog.show()

    def refreshCharAssets(self):
        #Clear Dropdowns
        self.skelePath_list.clear()
        self.idleLocs_dropdown.clear()
        self.skeleRig_dropdown.clear()
        self.activeCharLocs_dropdown.clear()
        skel_list = []
        #Get new dropdown items
        for file in glob.glob(skeleton_dir + '/*'): #Finds all spellbooks and creates dropdown
            skel_match = re.search('skelFiles(.*).SKEL', file)
            skel_name = skel_match.group(1)
            skel_list.append(skel_name[1:])
            self.skelePath_list.append(file)

        idleLocs = cmds.ls('*idle_Locators*')
        charLocs = cmds.ls('*Animation_Locators*')
        #Add items to dropdown
        for iLoc in idleLocs:
            self.idleLocs_dropdown.addItem(iLoc)
        for cLoc in charLocs:
            self.activeCharLocs_dropdown.addItem(cLoc)
        for item in skel_list:
            self.skeleRig_dropdown.addItem(item)

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

        self.create_ur_reference_file(assetName,assetType,targetFolder,projFolder)

    def create_ur_reference_file(self,assetName,assetType,assetPath,projFolder):
        #fix unicode error
        projFolder = projFolder.replace('\\','/')
        assetPath = projFolder.replace('\\','/')
        file = 'REFERENCES.txt'
        newLine = f'{assetName},{assetType},{assetPath}/{assetName}'
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

class skelePopUp(QDialog):
    #--------------------------------------------------------------------------------------------------------------
    #                                            Create GUI Window
    #--------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window()):
        super(skelePopUp, self).__init__(parent)

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.setFixedWidth(600)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(250, -1)
        self.setWindowTitle('SKEL File Creator')
        self.setWindowIcon(QIcon(icon_dir + "/RedlineLogo.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout
        self.make_connections()

        #ADV Options Set Up
        self.widgetCount = 2
        self.widgetList = []
        self.addBone()

    #--------------------------------------------------------------------------------------------------------------
    #                                             Create Widgets
    #--------------------------------------------------------------------------------------------------------------
    def create_controls(self):
        UI_ELEMENT_HEIGHT = 30

        ##### Tab Bar #####
        self.tabWidget = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabWidget.addTab(self.tab1, 'Basic Set Up')
        self.tabWidget.addTab(self.tab2, 'Advanced Set Up')
        ##### ADV Options #####
        self.advAddBone_button = QPushButton('Add Bone')
        self.advRigName_edit = QLineEdit()
        self.advRigName_edit.setPlaceholderText('Rig Name')
        self.advComplete_button = QPushButton('Create File')
        self.advLoc_label = QLabel()
        self.advLoc_label.setText('Locator:')
        self.advBone_label = QLabel()
        self.advBone_label.setText('Bone:')
        self.advConstraint_label = QLabel()
        self.advConstraint_label.setText('Constraint Options:')
        ##### New File Name Line #####
        self.newFileName = QLineEdit()
        self.newFileName.setPlaceholderText('Rig Name')
        self.newFileName.setMinimumHeight(UI_ELEMENT_HEIGHT)
        ##### Simple Layout #####
        self.headLabel = QLabel()
        self.headLabel.setText('Head Joint: ')
        self.head_edit = QLineEdit()
        self.head_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.neckLabel = QLabel()
        self.neckLabel.setText('Neck Joint: ')
        self.neck_edit = QLineEdit()
        self.neck_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.torsoJointLabel = QLabel()
        self.torsoJointLabel.setText('Torso Joint: ')
        self.torsoJoint_edit = QLineEdit()
        self.torsoJoint_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rightUpperArmLabel = QLabel()
        self.rightUpperArmLabel.setText('Right Upper Arm Joint: ')
        self.rightUpperArm_edit = QLineEdit()
        self.rightUpperArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rightLowerArmLabel = QLabel()
        self.rightLowerArmLabel.setText('Right Lower Arm Joint: ')
        self.rightLowerArm_edit = QLineEdit()
        self.rightLowerArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.leftUpperArmLabel = QLabel()
        self.leftUpperArmLabel.setText('Left Upper Arm Joint: ')
        self.leftUpperArm_edit = QLineEdit()
        self.leftUpperArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.leftLowerArmLabel = QLabel()
        self.leftLowerArmLabel.setText('Left Lower Arm Joint: ')
        self.leftLowerArm_edit = QLineEdit()
        self.leftLowerArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.hipLabel = QLabel()
        self.hipLabel.setText('Hip Joint: ')
        self.hip_edit = QLineEdit()
        self.hip_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rightFemurLabel = QLabel()
        self.rightFemurLabel.setText('Right Femur Joint: ')
        self.rightFemur_edit = QLineEdit()
        self.rightFemur_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rightLowerLegLabel = QLabel()
        self.rightLowerLegLabel.setText('Right Lower Leg Joint: ')
        self.rightLowerLeg_edit = QLineEdit()
        self.rightLowerLeg_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.rightFootLabel = QLabel()
        self.rightFootLabel.setText('Right Foot Joint: ')
        self.rightFoot_edit = QLineEdit()
        self.rightFoot_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.LeftFemurLabel = QLabel()
        self.LeftFemurLabel.setText('Left Femur Joint: ')
        self.LeftFemur_edit = QLineEdit()
        self.LeftFemur_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.leftLowerLegLabel = QLabel()
        self.leftLowerLegLabel.setText('Left Lower Leg Joint: ')
        self.leftLowerLeg_edit = QLineEdit()
        self.leftLowerLeg_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
        self.leftFootLabel = QLabel()
        self.leftFootLabel.setText('Left Foot Joint: ')
        self.leftFoot_edit = QLineEdit()
        self.leftFoot_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.all_edits = [self.LeftFemur_edit, self.rightFemur_edit, self.leftFoot_edit, self.rightFoot_edit,
        self.head_edit, self.hip_edit, self.leftLowerArm_edit, self.leftUpperArm_edit, self.leftLowerLeg_edit,
        self.rightLowerLeg_edit, self.neck_edit,  self.rightLowerArm_edit, self.rightUpperArm_edit, self.torsoJoint_edit, self.newFileName]

        ##### Create SKEL File #####
        self.createSkel_button = QPushButton('Create SKEL File')

    #--------------------------------------------------------------------------------------------------------------
    #                                              Make Layout
    #--------------------------------------------------------------------------------------------------------------
    def create_layout(self):
        self.mainLayout = QVBoxLayout()
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        #### Simple Layout ####
        simple_group = QGroupBox()
        self.simpleLayout = QGridLayout()

        #self.simpleLayout.addWidget(self.advOption_checkbox, 0,0)
        self.simpleLayout.addWidget(self.headLabel, 1,0)
        self.simpleLayout.addWidget(self.head_edit, 1,1,1,3)
        self.simpleLayout.addWidget(self.neckLabel, 2,0)
        self.simpleLayout.addWidget(self.neck_edit, 2,1,1,3)
        self.simpleLayout.addWidget(self.torsoJointLabel, 3,0)
        self.simpleLayout.addWidget(self.torsoJoint_edit, 3,1,1,3)
        self.simpleLayout.addWidget(self.rightUpperArmLabel, 4,0)
        self.simpleLayout.addWidget(self.rightUpperArm_edit, 4,1,1,3)
        self.simpleLayout.addWidget(self.rightLowerArmLabel, 5,0)
        self.simpleLayout.addWidget(self.rightLowerArm_edit, 5,1,1,3)
        self.simpleLayout.addWidget(self.leftUpperArmLabel, 6,0)
        self.simpleLayout.addWidget(self.leftUpperArm_edit, 6,1,1,3)
        self.simpleLayout.addWidget(self.leftLowerArmLabel, 7,0)
        self.simpleLayout.addWidget(self.leftLowerArm_edit, 7,1,1,3)
        self.simpleLayout.addWidget(self.hipLabel, 8,0)
        self.simpleLayout.addWidget(self.hip_edit, 8,1,1,3)
        self.simpleLayout.addWidget(self.rightFemurLabel, 9,0)
        self.simpleLayout.addWidget(self.rightFemur_edit, 9,1,1,3)
        self.simpleLayout.addWidget(self.rightLowerLegLabel, 10,0)
        self.simpleLayout.addWidget(self.rightLowerLeg_edit, 10,1,1,3)
        self.simpleLayout.addWidget(self.rightFootLabel, 11,0)
        self.simpleLayout.addWidget(self.rightFoot_edit, 11,1,1,3)
        self.simpleLayout.addWidget(self.LeftFemurLabel, 12,0)
        self.simpleLayout.addWidget(self.LeftFemur_edit, 12,1,1,3)
        self.simpleLayout.addWidget(self.leftLowerLegLabel, 13,0)
        self.simpleLayout.addWidget(self.leftLowerLeg_edit, 13,1,1,3)
        self.simpleLayout.addWidget(self.leftFootLabel, 14,0)
        self.simpleLayout.addWidget(self.leftFoot_edit, 14,1,1,3)
        self.simpleLayout.addWidget(self.newFileName, 15,0,1,2)
        self.simpleLayout.addWidget(self.createSkel_button, 15,2,1,2)


        simple_group.setLayout(self.simpleLayout)
        self.layout1.addWidget(simple_group)

        ##### ADV Layout #####
        advGroup = QGroupBox()
        self.advLayout = QGridLayout()

        self.advLayout.addWidget(self.advAddBone_button, 0,0,1,2)
        self.advLayout.addWidget(self.advRigName_edit, 0,2,1,2)
        self.advLayout.addWidget(self.advComplete_button, 0,4)

        self.advLayout.addWidget(self.advLoc_label, 1,0)
        self.advLayout.addWidget(self.advBone_label, 1,1)
        self.advLayout.addWidget(self.advConstraint_label, 1,3)

        advGroup.setLayout(self.advLayout)
        self.layout2.addWidget(advGroup)

        #Set Tabs
        self.tab1.setLayout(self.layout1)
        self.tab2.setLayout(self.layout2)
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)

    #--------------------------------------------------------------------------------------------------------------
    #                                             Make Connections
    #--------------------------------------------------------------------------------------------------------------
    def make_connections(self):
        self.createSkel_button.clicked.connect(self.basicCreateSKEL)
        self.advAddBone_button.clicked.connect(self.addBone)
        self.advComplete_button.clicked.connect(self.advCreateSKEL)

    #--------------------------------------------------------------------------------------------------------------
    #                                                 Functions
    #--------------------------------------------------------------------------------------------------------------
    def basicCreateSKEL(self):
        missing_joint = False
        for edit in self.all_edits:
            if edit.text() == '':
                missing_joint = True

        if missing_joint:
            warning_box = QMessageBox(QMessageBox.Warning, "Check Joints", "Please enter a joint name for all joints.")
            warning_box.exec_()

        else:
            #Get Variables
            locs = ['femur_left','femur_right','foot_left','foot_right','head','hip','left_lower_arm','left_upper_arm',
                    'lower_leg_left','lower_leg_right','neck','right_lower_arm','right_upper_arm','torso']
            joints = [self.LeftFemur_edit.text(), self.rightFemur_edit.text(), self.leftFoot_edit.text(), self.rightFoot_edit.text(),
            self.head_edit.text(), self.hip_edit.text(), self.leftLowerArm_edit.text(), self.leftUpperArm_edit.text(), self.leftLowerLeg_edit.text(),
            self.rightLowerLeg_edit.text(), self.neck_edit.text(),  self.rightLowerArm_edit.text(), self.rightUpperArm_edit.text(), self.torsoJoint_edit.text()]

            newFile = f'{skeleton_dir}/{self.newFileName.text()}'

            #Create File
            f = open(f'{newFile}.SKEL', 'w')
            for i in range(0,len(joints)):
                f.write(f'{locs[i]},{joints[i]},True,True\n')
            f.close()

            #Clear inputs
            for edit in self.all_edits:
                edit.setText('')

    def advCreateSKEL(self):
        locLabels = ['L Femur','R Femur','L Foot','R Foot','Head','Hip','L Lower Arm','L Upper Arm','L Lower Leg',
                    'R Lower Leg','Neck','R Lower Arm','R Upper Arm','Torso']
        locs = ['femur_left','femur_right','foot_left','foot_right','head','hip','left_lower_arm','left_upper_arm',
                'lower_leg_left','lower_leg_right','neck','right_lower_arm','right_upper_arm','torso']
        #Get Variables
        vars = []
        newFile = f'{skeleton_dir}/{self.advRigName_edit.text()}'
        for i in range(0,len(self.widgetList)):
            #Get info from widgets
            loc = self.widgetList[i][0].currentText()
            bone = self.widgetList[i][1].text()
            tranBool = self.widgetList[i][2].checkState()
            rotBool = self.widgetList[i][3].checkState()
            #Get correct loc name
            loc = locs[locLabels.index(loc)]
            #Get Booleans
            if tranBool:
                tranBool = 'True'
            if not tranBool:
                tranBool = 'False'
            if rotBool:
                rotBool = 'True'
            if not rotBool:
                rotBool = 'False'
            vars.append((loc,bone,tranBool,rotBool))
        #Create File
        f = open(f'{newFile}.SKEL', 'w')
        for i in range(0,len(vars)):
            f.write(f'{vars[i][0]},{vars[i][1]},{vars[i][2]},{vars[i][3]}\n')
        f.close()
        #Clear inputs
        self.advRigName_edit.setText('')
        for i in range(0,len(self.widgetList)):
            self.widgetList[i][1].setText('')
            self.widgetList[i][2].setChecked(1)
            self.widgetList[i][3].setChecked(1)

    def addBone(self):
        #Create Widgets
        locs = ['Head','Neck','Torso','R Upper Arm', 'R Lower Arm', 'L Upper Arm', 'L Lower Arm',
                'Hip','R Femur','R Lower Leg','R Foot','L Femur','L Lower Leg','L Foot']

        comboBox = QComboBox()
        for loc in locs:
            comboBox.addItem(loc)

        boneName = QLineEdit()
        boneName.setPlaceholderText('Bone Name')
        translationBox = QCheckBox('Translation')
        translationBox.setChecked(1)
        rotationBox = QCheckBox('Rotation')
        rotationBox.setChecked(1)

        #Add Widgets to layout
        row = self.widgetCount
        self.advLayout.addWidget(comboBox, row,0)
        self.advLayout.addWidget(boneName, row,1,1,2)
        self.advLayout.addWidget(translationBox, row,3)
        self.advLayout.addWidget(rotationBox, row,4)

        #Track Widgets
        self.widgetCount += 1
        self.widgetList.append((comboBox,boneName,translationBox,rotationBox))

class rigExportPopUp(QDialog):
    #--------------------------------------------------------------------------------------------------------------
    #                                            Create GUI Window
    #--------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window(), calledBy=None):
        super(rigExportPopUp, self).__init__(parent)

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.calledBy = calledBy
        if self.calledBy.unreal_checkbox.checkState():
            self.get_project()
        self.setFixedWidth(600)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(250, -1)
        self.setWindowTitle('Character Export')
        self.setWindowIcon(QIcon(icon_dir + "/RedlineLogo.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout
        self.make_connections()

    def create_controls(self):
        ##### Skeleton Export #####
        self.skeleStep1_label = QLabel('Step 1: Select Mesh and Joints')
        self.skeleStep2_label = QLabel('Step 2: Confirm Selection')
        self.skeleStep3_label = QLabel('Step 3: Name and Export FBX')
        self.skeleConfirmation_checkbox = QCheckBox('Mesh and Joints Selected')
        self.skeleFileName_label = QLabel('File Name:')
        self.skeleFileName_edit = QLineEdit()
        self.skeleFileName_edit.setPlaceholderText('FBX File Name')
        self.exportSkele_button = QPushButton('Export Skeleton')

        ##### Animation Export #####
        self.animStep1_label = QLabel('Step 1: Set Desired Start/Stop Frames')
        self.animStep2_label = QLabel('Step 2: Select Joint Hierarchy')
        self.animStep3_label = QLabel('Step 3: Confirm Selection')
        self.animStep4_label = QLabel('Step 4: Name and Export Animation')
        self.animStart_edit = QLineEdit()
        self.animStart_edit.setPlaceholderText('Start Frame')
        self.animStop_edit = QLineEdit()
        self.animStop_edit.setPlaceholderText('Stop Frame')
        self.anim_checkbox = QCheckBox('Joints Selected')
        self.animFBX_label = QLabel('File Name: ')
        self.animFBX_edit = QLineEdit()
        self.animSkelPair_label = QLabel('Skeleton:')
        self.animSkelPair_dropdown = QComboBox()
        self.animSkelPair_dropdown.addItem('None')
        if self.calledBy.unreal_checkbox.checkState():
            if self.calledBy.unrealProjList_dropdown.currentText() == '':
                warningBox = QMessageBox(QMessageBox.Warning, "Check File Name", "Please enter Unreal Project name or uncheck Unreal Project checkbox.")
                warningBox.exec_()
                self.calledBy.dialogs.pop(-1) #######THIS JUST THROWS ERROR TO STOP POP UP########
            else:
                file = f"{UNREAL_PROJECT_DIR}/mayaProjects/{self.calledBy.unrealProjList_dropdown.currentText()}.txt"
                f = open(file,'r')
                lines = f.readlines()
                f.close()
                for i in range(0,len(lines)):
                    lines[i] = lines[i].strip()
                    lines[i] = lines[i].split(',')
                skels = [line[0] for line in lines if line[1]=='skeleton']
                for skel in skels:
                    self.animSkelPair_dropdown.addItem(skel[:-4])
        self.animFBX_edit.setPlaceholderText('FBX Name')
        self.animExport_button = QPushButton('Export Animation')

    def create_layout(self):
        self.mainLayout = QHBoxLayout()

        skeleton_group = QGroupBox('Skeleton Export')
        skeleton_layout = QGridLayout()
        skeleton_layout.addWidget(self.skeleStep1_label,0,0,1,2)
        skeleton_layout.addWidget(self.skeleStep2_label,1,0,1,2)
        skeleton_layout.addWidget(self.skeleStep3_label,2,0,1,2)
        skeleton_layout.addWidget(self.skeleConfirmation_checkbox,3,0,1,3)
        skeleton_layout.addWidget(self.skeleFileName_label,4,0)
        skeleton_layout.addWidget(self.skeleFileName_edit,4,1,1,2)
        skeleton_layout.addWidget(self.exportSkele_button,5,0,1,3)
        skeleton_group.setLayout(skeleton_layout)

        animExport_group = QGroupBox('Animation Export')
        animExport_layout = QGridLayout()
        animExport_layout.addWidget(self.animStep1_label,0,0,1,4)
        animExport_layout.addWidget(self.animStep2_label,1,0,1,4)
        animExport_layout.addWidget(self.animStep3_label,2,0,1,4)
        animExport_layout.addWidget(self.animStep4_label,3,0,1,4)
        animExport_layout.addWidget(self.anim_checkbox,4,0,1,4)
        animExport_layout.addWidget(self.animStart_edit,5,0,1,2)
        animExport_layout.addWidget(self.animStop_edit,5,2,1,2)
        animExport_layout.addWidget(self.animFBX_label,6,0,1,1)
        animExport_layout.addWidget(self.animFBX_edit,6,1,1,3)
        if self.calledBy.unreal_checkbox.checkState():
            animExport_layout.addWidget(self.animSkelPair_label, 7,0,1,1)
            animExport_layout.addWidget(self.animSkelPair_dropdown, 7,1,1,3)
            animExport_layout.addWidget(self.animExport_button,8,0,1,4)
        else:
            animExport_layout.addWidget(self.animExport_button,7,0,1,4)
        animExport_group.setLayout(animExport_layout)

        self.mainLayout.addWidget(skeleton_group)
        self.mainLayout.addWidget(animExport_group)
        self.setLayout(self.mainLayout)

    def make_connections(self):
        self.exportSkele_button.clicked.connect(self.exportSkeleton)
        self.animExport_button.clicked.connect(self.exportAnimation)

    def exportSkeleton(self):
        if self.skeleFileName_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check File Name", "Please enter a valid FBX file name.")

        elif self.skeleConfirmation_checkbox.checkState():
            #get variables
            filename = f'SKEL_{self.skeleFileName_edit.text()}'
            exportLocation = f"{desktop_dir}/{filename}"
            #fix unicode error
            exportLocation = exportLocation.replace('\\','/')
            #export with metahuman settings
            mel.eval('FBXResetExport')
            mel.eval('FBXExportTangents -v 1')
            mel.eval('FBXExportSmoothingGroups -v 1')
            mel.eval('FBXExportSmoothMesh -v 1')
            mel.eval('FBXExportSkins -v 1')
            mel.eval('FBXExportShapes -v 1')
            mel.eval('FBXExportConstraints -v 1')
            mel.eval('FBXExportSkeletonDefinitions -v 1')
            mel.eval(f'FBXExport -f "{exportLocation}.fbx" -s')

            self.calledBy.unrealExport(filename,'skeleton',f"{exportLocation}.fbx")
            self.animSkelPair_dropdown.addItem(filename)
            self.skeleFileName_edit.setText('')

        else:
            warning_box = QMessageBox(QMessageBox.Warning, "Confirm Selection", "Please confirm Joint and Mesh are selected.")
            warning_box.exec_()

    def exportAnimation(self):
        #Warning Boxes
        if self.animFBX_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check File Name", "Please enter a valid FBX file name.")
            warning_box.exec_()
        elif self.animSkelPair_dropdown.currentText() == 'None':
            warning_box = QMessageBox(QMessageBox.Warning, "Skeleton Required", "Please select the skeleton for this animation.\nIf none are listed please create one, or check your Unreal Project name.")
            warning_box.exec_()
        elif self.animStart_edit.text() == '' or self.animStop_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check Bake Frames", "Please enter a valid input for Start/Stop frames.")
            warning_box.exec_()
        elif not self.anim_checkbox.checkState():
            warning_box = QMessageBox(QMessageBox.Warning, "Confirm Selection", "Please confirm Joint Hierarchy is selected.")
            warning_box.exec_()
        #Export Func
        else:
            #get all bones below
            selected = cmds.ls(sl=1)
            cmds.select(selected, hi=1)
            #get variables
            filename = f'ANIM_{self.animFBX_edit.text()}'
            exportLocation = desktop_dir + '/' + filename
            bakeStart = int(self.animStart_edit.text())
            bakeEnd = int(self.animStop_edit.text())
            #fix unicode error
            exportLocation = exportLocation.replace('\\','/')
            #export with metahuman settings
            mel.eval('FBXResetExport')
            mel.eval('FBXExportInputConnections -v 0')
            mel.eval('FBXExportBakeComplexAnimation -v 1')
            mel.eval(f'FBXExportBakeComplexStart -v {bakeStart}')
            mel.eval(f'FBXExportBakeComplexEnd -v {bakeEnd}')
            mel.eval(f'FBXExport -f "{exportLocation}.fbx" -s')
            self.calledBy.unrealExport(filename,f'animation__FROMSKEL__{self.animSkelPair_dropdown.currentText()}.fbx',f"{exportLocation}.fbx")
            #clear selection
            cmds.select(deselect=True)
            self.animFBX_edit.setText('')
            self.animStart_edit.setText('')
            self.animStop_edit.setText('')

    def get_project(self):
        projName = self.calledBy.unrealProjList_dropdown.currentText()
        error = False
        if projName == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Check Project Name", "Please enter a valid Project name or uncheck the Unreal Project checkbox.")
            warning_box.exec_()
            self.calledBy.dialogs.pop(-1) #######THIS JUST THROWS ERROR TO STOP POP UP########
            error = True
        if not error:
            currentProjects = []
            for file in glob.glob(UNREAL_PROJECT_DIR + '/mayaProjects/*'): #finds all projects and creates dropdown
                try:
                    projectMatch = re.search('/mayaProjects(.*).txt', file)
                    proj = projectMatch.group(1)[1:]
                    currentProjects.append(proj)
                except:
                    pass
            if projName not in currentProjects:
                qBox = QMessageBox(QMessageBox.Question, "Check File Name", f"Project {projName} not found.\nCreate new project?")
                qBox.addButton(QMessageBox.Yes)
                qBox.addButton(QMessageBox.No)
                reply = qBox.exec_()
                if reply == QMessageBox.Yes:
                    f = open(f'{UNREAL_PROJECT_DIR}/mayaProjects/{projName}.txt', 'w')
                    f.close()
                else:
                    self.calledBy.dialogs.pop(-1) #######THIS JUST THROWS ERROR TO STOP POP UP########
            else: #comment above wouldn't collapse and annoyed me
                pass
