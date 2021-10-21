import fileinput, os, sys, glob, re, math
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
from Settings import *
from CableMaker import *

class ToolKit():
    #Set Up
    toolKitName = 'Site Tools'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()

    #Buttons
    def create_controls(self):
        ##### XYZ Text Bar #####
        self.choose_locator_edit = QLineEdit()
        self.choose_locator_edit.setPlaceholderText("Locator File")
        self.choose_locator_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### XYZ Folder Button #####
        self.choose_locator_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.choose_locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Settings Buttons #####
        self.headersIncludedCheckBox = QCheckBox('Headers Included')
        self.headersIncludedCheckBox.setChecked(1)
        self.delimiterLabel = QLabel('Delimiter: ')
        self.delimiterDict = {
                            'Comma' : ',',
                            'Tab' : '\t',
                            'Semicolon' : ';',
                            'BackSlash "\\"' : '\\',
                            'FrontSlash "/"' : '/',
                            'Double Space' : '  '}
        self.delimiterDropDown = QComboBox()
        for key in self.delimiterDict:
            self.delimiterDropDown.addItem(key)
        self.xLabel = QLabel('X Column: ')
        self.yLabel = QLabel('Y Column: ')
        self.zLabel = QLabel('Z Column: ')
        self.idLabel = QCheckBox('ID # Column: ')
        self.idLabel.setChecked(1)
        self.nameLabel = QCheckBox('Name Column: ')
        self.nameLabel.setChecked(1)
        self.xEdit = QLineEdit()
        self.yEdit = QLineEdit()
        self.zEdit = QLineEdit()
        self.idEdit = QLineEdit()
        self.nameEdit = QLineEdit()

        ##### CSV Export #####
        self.locatorGroupNameEdit = QLineEdit()
        self.locatorGroupNameEdit.setPlaceholderText('Locator Group Name')
        self.newFileNameEdit = QLineEdit()
        self.newFileNameEdit.setPlaceholderText('New File Name')
        self.exportCSVButton = QPushButton('Export Locator Data')


        ##### Load XYZ Button #####
        self.load_locator_button = QPushButton(QIcon(icon_dir + "/load.png"), "Load Locators")
        self.load_locator_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Cable Creation Buttons #####
        self.open_cable_button = QPushButton("Open Cable Creator")
        self.open_cable_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

    #Connections
    def make_connections(self):
        ##### Locator Group #####
        self.choose_locator_button.clicked.connect(self.choose_locator)
        self.load_locator_button.clicked.connect(self.load_locator)
        self.exportCSVButton.clicked.connect(self.export_unreal_csv)

        ##### Cable Group #####
        self.open_cable_button.clicked.connect(self.cable_gui)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        ##### XYZ Locator Section #####
        locator_group = QGroupBox("Site Locators")
        locator_layout = QGridLayout()
        locator_layout.addWidget(self.choose_locator_button, 0, 0)
        locator_layout.addWidget(self.choose_locator_edit, 0, 1, 1, 3)
        locator_layout.addWidget(self.headersIncludedCheckBox, 1,0)
        locator_layout.addWidget(self.delimiterLabel, 1,1)
        locator_layout.addWidget(self.delimiterDropDown, 1,2,1,2)
        locator_layout.addWidget(self.idLabel, 2,0)
        locator_layout.addWidget(self.idEdit, 2,1,1,3)
        locator_layout.addWidget(self.nameLabel, 3,0)
        locator_layout.addWidget(self.nameEdit, 3,1,1,3)
        locator_layout.addWidget(self.xLabel, 4,0)
        locator_layout.addWidget(self.xEdit, 4,1,1,3)
        locator_layout.addWidget(self.yLabel, 5,0)
        locator_layout.addWidget(self.yEdit, 5,1,1,3)
        locator_layout.addWidget(self.zLabel, 6,0)
        locator_layout.addWidget(self.zEdit, 6,1,1,3)
        locator_layout.addWidget(self.load_locator_button, 7,0,1,4)
        locator_group.setLayout(locator_layout)

        ##### Export Locator Data #####
        export_group = QGroupBox("Export")
        export_layout = QGridLayout()
        export_layout.addWidget(self.locatorGroupNameEdit, 0,0)
        export_layout.addWidget(self.newFileNameEdit, 0,1)
        export_layout.addWidget(self.exportCSVButton, 1,0,1,2)
        export_group.setLayout(export_layout)

        ##### Cable GUI #####
        cable_group = QGroupBox("Cable GUI")
        cable_layout = QVBoxLayout()
        cable_layout.addWidget(self.open_cable_button)
        cable_group.setLayout(cable_layout)

        #Add groups to tab
        self.layout.addWidget(locator_group)
        self.layout.addWidget(export_group)
        self.layout.addWidget(cable_group)

    #Functions
    def choose_locator(self):
        # Set locator Path
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "Text Files (*.txt);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_locator_edit.setText(file_path)

    def load_locator(self):
        #List for locs to add to group
        all_locs = []
        #load xyz file
        filename = self.choose_locator_edit.text()
        #Read Settings
        delimiter = self.delimiterDict[self.delimiterDropDown.currentText()]
        x_loc = int(self.xEdit.text())-1
        y_loc = int(self.yEdit.text())-1
        z_loc = int(self.zEdit.text())-1
        if self.idLabel.checkState():
            id_loc = int(self.idEdit.text())-1
        if self.nameLabel.checkState():
            name_loc = int(self.nameEdit.text())-1
        f = open(filename, 'r')
        #Read File and make locators
        full = f.readlines()
        if self.headersIncludedCheckBox.checkState():
            full.pop(0)
        for i in range(0,len(full)):
            full[i] = full[i].rstrip()
            line = full[i].split(delimiter)
            x = float(line[x_loc])
            y = float(line[y_loc])
            z = float(line[z_loc])
            if self.idLabel.checkState():
                id = line[id_loc]
            else:
                id = i
            if self.nameLabel.checkState():
                name = line[name_loc]
            else:
                name = 'TARGET'
            loc = cmds.spaceLocator(p=[x,y,z], n=f'{name}_{id}')
            all_locs.append(loc[0])
        f.close()
        #Rotate Locators
        grp = cmds.group(all_locs,n='Site Locators')
        cmds.rotate(-90,0,0,grp)
        self.choose_locator_edit.setText('')

    def export_unreal_csv(self):
        group_name = self.locatorGroupNameEdit.text()
        file_name = self.newFileNameEdit.text()
        #Get Translation and Rotation
        x = cmds.getAttr(f'{group_name}.translateX')
        y = cmds.getAttr(f'{group_name}.translateY')
        z = cmds.getAttr(f'{group_name}.translateZ')
        x_rot = cmds.getAttr(f'{group_name}.rotateX') + 90 #when brought in it is rotated to -90
        y_rot = cmds.getAttr(f'{group_name}.rotateY')
        z_rot = cmds.getAttr(f'{group_name}.rotateZ')
        #Move to Z-Up Location
        cmds.setAttr(f'{group_name}.translateX',x)
        cmds.setAttr(f'{group_name}.translateY',-z)
        cmds.setAttr(f'{group_name}.translateZ',y)
        cmds.setAttr(f'{group_name}.rotateX',x_rot)
        cmds.setAttr(f'{group_name}.rotateY',-z_rot)
        cmds.setAttr(f'{group_name}.rotateZ',y_rot)
        #Export new location
        cmds.select(deselect=True)
        cmds.select(group_name, hierarchy=True)
        locators = cmds.ls(sl=True)
        locators.pop(0) #remove group name
        locators = [locator for locator in locators if 'Shape' in locator]
        cmds.select(deselect=True)
        f = open(f'{desktop_dir}/{file_name}.txt','w')
        for locator in locators:
            position = cmds.getAttr(f'{locator}.worldPosition')
            position = position[0]
            loc_x = position[0]
            loc_y = position[1]
            loc_z = position[2]
            line = f'{locator[:-5]},{loc_x},{loc_y},{loc_z}\n'
            f.write(line)
        f.close()
        #Set original location
        cmds.setAttr(f'{group_name}.translateX',x)
        cmds.setAttr(f'{group_name}.translateY',y)
        cmds.setAttr(f'{group_name}.translateZ',z)
        cmds.setAttr(f'{group_name}.rotateX',x_rot-90)
        cmds.setAttr(f'{group_name}.rotateY',y_rot)
        cmds.setAttr(f'{group_name}.rotateZ',z_rot)
        #Clear text boxes
        self.newFileNameEdit.setText('')
        self.locatorGroupNameEdit.setText('')

    def cable_gui(self):
        #Opens GUI for easy cable creation
        if cmds.window("Cable Maker", exists =True):
            cmds.deleteUI("Cable Maker")
        cmds.workspaceControl("Cable Maker", retain=False, floating=True)
        createCustomWorkspaceControlCable()
