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
    toolKitName = 'Tab Name'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()

    #Buttons
    def create_controls(self):
        self.test_button = QPushButton('test button')

    #Connections
    def make_connections(self):
        self.test_button.clicked.connect(self.myFunc)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        group = QGroupBox("Test Group")
        subLayout = QVBoxLayout()
        subLayout.addWidget(self.test_button)
        group.setLayout(subLayout)

        #Add groups to tab
        self.layout.addWidget(group)

    #Functions
    def myFunc(self):
        print('hello world')
