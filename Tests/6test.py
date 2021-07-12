
locator = 
lights = cmds.ls(sl=True)
for light in lights:
    cmds.expression(s=f'if {locator}.brake == 1:\n\t{light}.intensity = 10\n\t{light}.exposure = 5\nelse:\n\t{light}.intensity = 0\n\t{light}.exposure = 0', ae=True)
