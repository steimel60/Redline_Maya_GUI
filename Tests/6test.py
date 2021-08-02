#Scales vehicle to size of vehicle specs
vehicle = cmds.ls('Vehicle', hierarchy=True)
bumper_group = cmds.group(bumpers)

cmds.select(bumper_group)

cmds.geomToBBox(n='tempBBox', single=True, keepOriginal=True)


bbMinX = cmds.getAttr('tempBBox.boundingBoxMinX')
bbMaxX = cmds.getAttr('tempBBox.boundingBoxMaxX')
bbMinZ = cmds.getAttr('tempBBox.boundingBoxMinZ')
bbMaxZ = cmds.getAttr('tempBBox.boundingBoxMaxZ')

cmds.delete('tempBBox')

bbLength = bbMaxZ - bbMinZ
bbWidth = bbMaxX - bbMinX

dxfArea = length*width

bbArea = bbLength*bbWidth

scaleZ = length/bbLength
scaleX = width/bbWidth

print('DXF Length x Width')
print(f'{length} x {width}')
print('Bounding Box Length x Width')
print(f'{bbLength} x {bbWidth}')

currentScale = cmds.getAttr('Vehicle.scale')
vehicle = cmds.select('Vehicle')
cmds.scale(scaleX*currentScale[0][0], 1*currentScale[0][1], scaleZ*currentScale[0][2], vehicle)
