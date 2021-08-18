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

        ##### Cable Group #####
        self.open_cable_button.clicked.connect(self.cable_gui)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        ##### XYZ Locator Section #####
        locator_group = QGroupBox("Locators")
        locator_layout = QGridLayout()
        locator_layout.addWidget(self.choose_locator_button, 0, 0)
        locator_layout.addWidget(self.choose_locator_edit, 0, 1, 1, 2)
        locator_layout.addWidget(self.load_locator_button, 1, 0, 1, 3)
        locator_group.setLayout(locator_layout)

        ##### Cable GUI #####
        cable_group = QGroupBox("Cable GUI")
        cable_layout = QVBoxLayout()
        cable_layout.addWidget(self.open_cable_button)
        cable_group.setLayout(cable_layout)

        #Add groups to tab
        self.layout.addWidget(locator_group)
        self.layout.addWidget(cable_group)

    #Functions
    def choose_locator(self):
        # Set locator Path
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "Text Files (*.txt);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_locator_edit.setText(file_path)

    def load_locator(self):
        #load xyz file
        filename = self.choose_locator_edit.text()
        f = open(filename, 'r')
        full = f.readlines()
        for i in range(0,len(full)):
            full[i] = full[i].rstrip()
            if i == 0:
                headers = full[i].split('\t')
                for i in range(0, len(headers)):
                    headers[i] = headers[i].lower()
                x_loc = headers.index('x')
                y_loc = headers.index('y')
                z_loc = headers.index('z')
            else:
                xyz = full[i].split('\t')
                x = xyz[x_loc]
                y = xyz[y_loc]
                z = xyz[z_loc]
                cmds.spaceLocator(p=[x,y,z])

        f.close()

        self.choose_locator_edit.setText('')

    def cable_gui(self):
        #Opens GUI for easy cable creation
        if cmds.window("Cable Maker", exists =True):
            cmds.deleteUI("Cable Maker")
        cmds.workspaceControl("Cable Maker", retain=False, floating=True)
        createCustomWorkspaceControlCable()
