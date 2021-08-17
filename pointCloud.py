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
    toolKitName = 'Point Cloud Tools'
    def __init__(self):
        self.create_controls()
        self.make_connections()
        self.create_layout()

    #Buttons
    def create_controls(self):
        ##### Point CLoud Text Bar #####
        self.choose_xyzfile_edit = QLineEdit()
        self.choose_xyzfile_edit.setPlaceholderText("XYZ File")
        self.choose_xyzfile_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Point CLoud Folder Button #####
        self.choose_xyzfile_button = QPushButton(QIcon(icon_dir + "/open.png"), "")
        self.choose_xyzfile_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Load Point CLoud Button #####
        self.load_xyzfile_button = QPushButton(QIcon(icon_dir + "/load.png"), "Load Point Cloud")
        self.load_xyzfile_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        ##### Density Dropdown #####
        self.choose_density_button = QComboBox()
        self.density_list = ['Entire File','High','Medium','Low','Very Low']
        for item in self.density_list:
            self.choose_density_button.addItem(item)
        self.density_label = QLabel()
        self.density_label.setText('Density Settings:')
        self.density_label.setAlignment(Qt.AlignCenter)
        self.density_current = self.density_list[self.choose_density_button.currentIndex()]

    #Connections
    def make_connections(self):
        ##### Load Group #####
        self.choose_xyzfile_button.clicked.connect(self.choose_xyzfile)
        self.load_xyzfile_button.clicked.connect(self.load_xyzfile)
    #Layout
    def create_layout(self):
        #Layout for entire tab
        #DONT CHANGE NAME
        self.layout = QVBoxLayout()

        #Layouts for groups inside of tab
        ##### Load Section #####
        pcload_group = QGroupBox("Load Point Cloud")
        pcload_layout = QGridLayout()
        pcload_layout.addWidget(self.choose_xyzfile_button, 0, 0)
        pcload_layout.addWidget(self.choose_xyzfile_edit, 0, 1, 1, 2)
        pcload_layout.addWidget(self.density_label, 1, 0)
        pcload_layout.addWidget(self.choose_density_button, 1, 1, 1, 2)
        pcload_layout.addWidget(self.load_xyzfile_button, 2, 0, 1, 3)
        pcload_group.setLayout(pcload_layout)

        #Add groups to tab
        self.layout.addWidget(pcload_group)

    #Functions
    def choose_xyzfile(self):
        # Set locator Path
        file_path = QFileDialog.getOpenFileName(None, "", desktop_dir, "XYZ Files (*.xyz);;Text Files (*.txt);;All Files (*.*)")[0]
        if file_path == "": # If they cancel the dialog
            return # Then just don't open anything
        self.choose_xyzfile_edit.setText(file_path)

    def load_xyzfile(self):
        #Make Load Bar appear
        progress_group = QGroupBox("Loading Bar")
        progressBox = QVBoxLayout()
        load_label = QLabel()
        self.progress = QProgressBar()

        progressBox.addWidget(load_label)
        progressBox.addWidget(self.progress)
        progress_group.setLayout(progressBox)
        self.layout.addWidget(progress_group)

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
            clouds = cmds.ls('*_PointCloud*')
            if asset in clouds:
                nameTaken=True
                i=1
                while nameTaken:
                    temp = asset+str(i)
                    if temp not in clouds:
                        asset = temp
                        nameTaken = False
                    else:
                        i += 1
        except:
            print("Couldn't retrieve asset name")
            asset = 'PointCloud'
            clouds = cmds.ls('*PointCloud*')
            if asset in clouds:
                nameTaken=True
                i=1
                while nameTaken:
                    temp = asset+str(i)
                    if temp not in clouds:
                        asset = temp
                        nameTaken = False
                    else:
                        i += 1


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
