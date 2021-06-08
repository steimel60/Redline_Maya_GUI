import maya.cmds as cmds
import os

xyz_list = []
user_profile = os.environ['USERPROFILE']
desktop_dir = user_profile + '\\Desktop'

filename = desktop_dir + '\\' + 'text4u.xyz'
f = open(filename, 'r')
full = f.readlines()

pointTotal = len(full)
goalTotal = 15000
stepSize = pointTotal // goalTotal

for i in range(0,goalTotal):
    full[i*stepSize] = full[i*stepSize].rstrip()
    full[i*stepSize] = full[i*stepSize].split(' ')

    x = full[i*stepSize][0]
    y = full[i*stepSize][1]
    z = full[i*stepSize][2]

    r = float(full[i*stepSize][3])/255
    g = float(full[i*stepSize][4])/255
    b = float(full[i*stepSize][5])/255

    particleName = 'particle' + str(i)
    particleColor = [r,g,b]

    print('Loading particle ' + str(i) + ' of ' + str(goalTotal))
    cmds.particle(n=particleName, p=[x, y, z])

    cmds.select(particleName + 'Shape')
    cmds.addAttr(k=True, ln='colorRed', dv=r, at='float')
    cmds.addAttr(k=True, ln='colorGreen', dv=g, at='float')
    cmds.addAttr(k=True, ln='colorBlue', dv=b, at='float')

f.close()
