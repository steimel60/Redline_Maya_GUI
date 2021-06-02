from maya import cmds

def rotate_z_pos():
    cmds.select(all=True)
    cmds.rotate(0, 0, 90, relative=True, centerPivot=True)
    cmds.select(deselect=True)

def rotate_z_neg():
    cmds.select(all=True)
    cmds.rotate(0, 0, -90, relative=True, centerPivot=True)
    cmds.select(deselect=True)

def rotate_x_pos():
    cmds.select(all=True)
    cmds.rotate(90, 0, 0, relative=True, centerPivot=True)
    cmds.select(deselect=True)

def rotate_x_neg():
    cmds.select(all=True)
    cmds.rotate(-90, 0, -0, relative=True, centerPivot=True)
    cmds.select(deselect=True)

def rotate_y_pos():
    cmds.select(all=True)
    cmds.rotate(0, 90, 0, relative=True, centerPivot=True)
    cmds.select(deselect=True)

def rotate_y_neg():
    cmds.select(all=True)
    cmds.rotate(0, -90, 0, relative=True, centerPivot=True)
    cmds.select(deselect=True)
