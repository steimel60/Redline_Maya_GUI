from Settings import *


path = r"C:\Users\DylanSteimel\Documents\Unreal Projects\mayaProjects"
contents = os.listdir(path)
folders = [entry for entry in contents if os.path.isdir(f"{path}/{entry}")]
print(contents, folders)
