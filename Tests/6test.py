import fileinput, os, sys, glob, re, math
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

#--------------------------------------------------------------------------------------------------------------
#                                   Create GUI Window
#--------------------------------------------------------------------------------------------------------------
app = QApplication(sys.argv)
popUp = QWidget()
popUpLayout = QVBoxLayout()
popUp.setWindowTitle('AutoPy')
popUp.setFixedWidth(400)
qtRectangle = popUp.frameGeometry()
centerPoint = QDesktopWidget().availableGeometry().center()
qtRectangle.moveCenter(centerPoint)
popUp.move(qtRectangle.topLeft())
popUp.move(1200, 600)
UI_ELEMENT_HEIGHT = 50

#--------------------------------------------------------------------------------------------------------------
#                                   Create Widgets
#--------------------------------------------------------------------------------------------------------------
##### Joint Labels and Edits #####
headLabel = QLabel()
headLabel.setText('Head Joint: ')
head_edit = QLineEdit()
head_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
neckLabel = QLabel()
neckLabel.setText('Neck Joint: ')
neck_edit = QLineEdit()
neck_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
torsoJointLabel = QLabel()
torsoJointLabel.setText('Torso Joint: ')
torsoJoint_edit = QLineEdit()
torsoJoint_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
rightUpperArmLabel = QLabel()
rightUpperArmLabel.setText('Right Upper Arm Joint: ')
rightUpperArm_edit = QLineEdit()
rightUpperArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
rightLowerArmLabel = QLabel()
rightLowerArmLabel.setText('Right Lower Arm Joint: ')
rightLowerArm_edit = QLineEdit()
rightLowerArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
leftUpperArmLabel = QLabel()
leftUpperArmLabel.setText('Left Upper Arm Joint: ')
leftUpperArm_edit = QLineEdit()
leftUpperArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
leftLowerArmLabel = QLabel()
leftLowerArmLabel.setText('Left Lower Arm Joint: ')
leftLowerArm_edit = QLineEdit()
leftLowerArm_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
hipLabel = QLabel()
hipLabel.setText('Hip Joint: ')
hip_edit = QLineEdit()
hip_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
rightFemurLabel = QLabel()
rightFemurLabel.setText('Right Femur Joint: ')
rightFemur_edit = QLineEdit()
rightFemur_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
rightLowerLegLabel = QLabel()
rightLowerLegLabel.setText('Right Lower Leg Joint: ')
rightLowerLeg_edit = QLineEdit()
rightLowerLeg_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
rightFootLabel = QLabel()
rightFootLabel.setText('Right Foot Joint: ')
rightFoot_edit = QLineEdit()
rightFoot_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
LeftFemurLabel = QLabel()
LeftFemurLabel.setText('Left Femur Joint: ')
LeftFemur_edit = QLineEdit()
LeftFemur_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
leftLowerLegLabel = QLabel()
leftLowerLegLabel.setText('Left Lower Leg Joint: ')
leftLowerLeg_edit = QLineEdit()
leftLowerLeg_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)
leftFootLabel = QLabel()
leftFootLabel.setText('Left Foot Joint: ')
leftFoot_edit = QLineEdit()
leftFoot_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

#--------------------------------------------------------------------------------------------------------------
#                                   Make Layout
#--------------------------------------------------------------------------------------------------------------
popUpLayout.addWidget(headLabel)
popUpLayout.addWidget(head_edit)
popUpLayout.addWidget(neckLabel)
popUpLayout.addWidget(neck_edit)
popUpLayout.addWidget(torsoJointLabel)
popUpLayout.addWidget(torsoJoint_edit)
popUpLayout.addWidget(rightUpperArmLabel)
popUpLayout.addWidget(rightUpperArm_edit)
popUpLayout.addWidget(rightLowerArmLabel)
popUpLayout.addWidget(rightLowerArm_edit)
popUpLayout.addWidget(leftUpperArmLabel)
popUpLayout.addWidget(leftUpperArm_edit)
popUpLayout.addWidget(leftLowerArmLabel)
popUpLayout.addWidget(leftLowerArm_edit)
popUpLayout.addWidget(hipLabel)
popUpLayout.addWidget(hip_edit)
popUpLayout.addWidget(rightFemurLabel)

popUp.setLayout(popUpLayout)

popUp.show()
sys.exit(app.exec_())
