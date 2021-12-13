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
    toolKitName = 'VC Data Tools'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()

    #Buttons
    def create_controls(self):
        ##### VC Data Buttons #####
        self.choose_vcData_button = QPushButton(QIcon(icon_dir + "/open.png"), "")

        self.choose_vcData_edit = QLineEdit()
        self.choose_vcData_edit.setPlaceholderText("Virtual Crash Data File")

        self.convert_vcData_button = QPushButton("Convert VC Data")

        ##### File Management Buttons #####
        self.choose_rig_button = QPushButton(QIcon(icon_dir + "/open.png"), "")

        self.choose_rig_edit = QLineEdit()
        self.choose_rig_edit.setPlaceholderText("Rig File")

        self.loadRig_button = QPushButton("Load Rig")

        self.choose_mesh_button = QPushButton(QIcon(icon_dir + "/open.png"), "")

        self.choose_mesh_edit = QLineEdit()
        self.choose_mesh_edit.setPlaceholderText("Ground Proxy File")

        self.loadMesh_button = QPushButton("Load Ground Proxy")

        ##### Vehicle Locator Buttons #####
        self.choose_vLocator_button = QPushButton(QIcon(icon_dir + "/open.png"), "")

        self.choose_vLocator_edit = QLineEdit()
        self.choose_vLocator_edit.setPlaceholderText("Vehicle Locator .MOV File")

        self.create_vLocator_button = QPushButton("Create Vehicle Locator")

        self.fps_edit = QLineEdit()
        self.fps_edit.setMaximumWidth(60)
        self.fps_label = QLabel()
        self.fps_label.setText('FPS:')
        self.fps_label.setMaximumWidth(35)

    #Connections
    def make_connections(self):
        ##### File Management #####
        self.choose_rig_button.clicked.connect(self.choose_rig)
        self.loadRig_button.clicked.connect(self.load_rig)
        self.choose_mesh_button.clicked.connect(self.choose_mesh)
        self.loadMesh_button.clicked.connect(self.load_mesh)
        self.choose_vcData_button.clicked.connect(self.choose_vc_data)
        self.choose_vLocator_button.clicked.connect(self.choose_v_locator)

        ##### Use Data #####
        self.convert_vcData_button.clicked.connect(self.convertVCData)
        self.create_vLocator_button.clicked.connect(self.vehicleLocator)

    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        ##### File Management #####
        files_group = QGroupBox("File Management")
        files_layout = QGridLayout()

        files_layout.addWidget(self.choose_vcData_button,0,0)
        files_layout.addWidget(self.choose_vcData_edit,0,1,1,4)
        files_layout.addWidget(self.convert_vcData_button,0,5,1,2)

        files_layout.addWidget(self.choose_mesh_button,1,0)
        files_layout.addWidget(self.choose_mesh_edit,1,1,1,4)
        files_layout.addWidget(self.loadMesh_button,1,5,1,2)

        files_layout.addWidget(self.choose_rig_button,2,0)
        files_layout.addWidget(self.choose_rig_edit,2,1,1,4)
        files_layout.addWidget(self.loadRig_button,2,5,1,2)

        files_layout.addWidget(self.choose_vLocator_button, 3, 0)
        files_layout.addWidget(self.choose_vLocator_edit, 3, 1, 1, 4)
        files_layout.addWidget(self.fps_label, 3, 5)
        files_layout.addWidget(self.fps_edit, 3, 6)
        files_layout.addWidget(self.create_vLocator_button, 4, 0, 1, 7)
        files_group.setLayout(files_layout)

        #Add groups to tab
        self.layout.addWidget(files_group)

    #Functions
    def choose_rig(self):
        # Set Rig Path
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "Maya Files (*.mb *.ma);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_rig_edit.setText(file_path)

    def load_rig(self):
        filename = self.choose_rig_edit.text()
        cmds.file(filename, i=True)
        try:
            assetMatch = re.search('/*([a-zA-Z0-9-_ ]*)\.m[ab]', filename)
            asset = assetMatch.group(1)
        except:
            print("Couldn't retrieve asset name")
            asset = 'asset'
        dc = cmds.ls('*drive_ctrl', r=True)
        dc = cmds.rename(dc, asset + '_driveControl')
        rig = cmds.ls('*:*_TopNode')
        rigName = cmds.rename(rig, asset + '_TopNode')

        self.choose_rig_edit.setText('')

    def choose_mesh(self):
        # Set Mesh Path
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "OBJ Files (*.obj, *.fbx);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_mesh_edit.setText(file_path)

    def load_mesh(self):
        #Import mesh from set path
        filename = self.choose_mesh_edit.text()
        cmds.file(filename, i=True)
        self.choose_mesh_edit.setText('')

    def choose_vc_data(self):
        #Set path for VC data
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "CSV Files (*.csv);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vcData_edit.setText(file_path)

    def choose_v_locator(self):
        #Load in MOV file
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "MOV Files (*.mov);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vLocator_edit.setText(file_path)

    def convertVCData(self):
        #Convert VC Data to individual MOV files
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
            if 'auto-ees' in lines[i+1]:
                vehicleIndices.append(i)

        frameTotal = vehicleIndices[1] - vehicleIndices[0]

        #Create MOV Files
        for i in range(0,len(vehicles)):
            name = str(vehicles[i])
            f = open(desktop_dir + '/' + name + '.mov', 'w')
            for j in range(2, frameTotal):
                for k in range(0,len(lines[vehicleIndices[i] + j])):
                    f.write(lines[vehicleIndices[i] + j][k] + ' ')
                f.write('\n')

            f.close()

        self.choose_vcData_edit.setText('')

    def vehicleLocator(self):
        if self.fps_edit.text() == '':
            warning_box = QMessageBox(QMessageBox.Warning, "Set FPS", "Please enter a valid FPS.")
            warning_box.exec_()
        else:
            #Create vehicle locator with MOV data
            filename = self.choose_vLocator_edit.text()

            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            frameTotal = len(lines) - 1
            #Init Scene
            fps = self.fps_edit.text()
            cmds.playbackOptions(min='0sec', max=frameTotal)
            cmds.playbackOptions(ast='0sec')
            cmds.playbackOptions(aet=str(frameTotal/int(fps))+'sec')
            cmds.currentUnit(time=fps+'fps')
            cmds.currentTime(0)

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
            cmds.movIn(locName + '.Time', locName + '.Distance', locName + '.Velocity', locName + '.Xrot', locName + '.Yrot', locName + '.Zrot', locName + '.vni', locName + '.vnz', locName + '.steer', locName + '.CGx', locName + '.CGy', locName + '.CGz', locName + ".Xrad", locName + '.Yrad', locName + '.Zrad', locName + '.lastV', locName + '.brake', f=filename)

            #Add to group
            grp = cmds.group(locName, n=locName+'_group')
            cmds.rotate('-90deg',0,0,grp,pivot=(0,0,0))

            self.fps_edit.setText('')
            self.choose_vLocator_edit.setText('')
