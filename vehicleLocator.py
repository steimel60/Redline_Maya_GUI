import maya.cmds as cmds
import os
user_profile = os.environ['USERPROFILE']
desktop_dir = user_profile + '\\Desktop'

def convertVCFile(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    lines = [line.split(',') for line in lines]
    for i in range(0,len(lines)):
        lines[i] = [item.strip() for item in lines[i] if item != '' and item != '\n']


    vehicles = []
    vehicleIndices = []
    for i in range(0,len(lines)-1):
        if 'time [ s]' in lines[i+1]:
            vehicles.append(lines[i][0])
            vehicleIndices.append(i)
    for i in range(0,10):
        print(lines[i])

    print(vehicles)

    for i in range(0,len(vehicles)-1):
        name = str(vehicles[i])
        f = open(desktop_dir + '/' + name + '.mov', 'w')
        for j in range(2, vehicleIndices[i+1] - vehicleIndices[i]):
            for k in range(0,len(lines[vehicleIndices[i] + j])):
                f.write(lines[vehicleIndices[i] + j][k] + ' ')
            f.write('\n')
        f.close()




def createVehicleLocator():
    locator = cmds.spaceLocator(p=(0,0,0), n='vehicleLocator')
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
    cmds.addAttr(ln='Steer', at='float')
    cmds.setAttr(locator[0]+'.Steer', k=True)
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
