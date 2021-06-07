import os
import re

folder = 'C:\\Users\\DylanSteimel\\deltav\\Jason Young - Asset Library\\3D Vehicle Library'


user_profile = os.environ['USERPROFILE']
desktop_dir = user_profile + '\\Desktop'
studio_path = 'C:\\Users\\DylanSteimel\\Documents\\maya\\scripts\\magic-shade\\studios\\Blinn_Studio_V1.mb'
vehicle_file = 'Audi_Q7_2010.mb'
spellbook_dir = 'C:\\Users\\DylanSteimel\\Documents\\maya\\scripts\\magic-shade\\spellbooks'

def load_studio():
    #Choose which studio to work in
    cmds.file(new=True, force=True)
    cmds.file(studio_path, open=True)

def load_vehicle(path, sub, file):
    # Loads choosen vehicle
    vehicle_path = path + '\\' + sub + '\\' + file
    if os.path.isfile(vehicle_path):
        cmds.select(allDagObjects=True)
        prev_all_objects = cmds.ls(selection=True)
        cmds.select(deselect=True)
        # print(str(prev_all_objects))
        cmds.file(vehicle_path, i=True)
        cmds.select(allDagObjects=True)
        new_all_objects = cmds.ls(selection=True)
        cmds.select(deselect=True)
        # print(str(new_all_objects))
        diff = [x for x in new_all_objects if x not in prev_all_objects]
        # print(str(diff))
        cmds.group(diff, name="Vehicle")
        asset = file.split('.')
        cmds.file(rename= asset[0] + '_automated')
    else:
        warning_box = QMessageBox(QMessageBox.Warning, "No Vehicle Found", "No vehicle file found at " + vehicle_path)
        warning_box.exec_()

def apply_spellbook():
    # Applies choosen spellbook
    is_arnold = False
    arnold_list = cmds.ls('*Arnold*')
    if len(arnold_list) > 0:
        is_arnold = True

    if is_arnold:
        spellbook_path = spellbook_dir + '\\' + 'Arn2Blinn.spb'

    else:
        spellbook_path = spellbook_dir + '\\' + 'Hum2Blinn.spb'
        cmds.scale(0.0328, 0.0328, 0.0328, absolute=True, pivot=(0, 0, 0))
        cmds.select(deselect=True)

    #spellbook_path =
    if os.path.isfile(spellbook_path):
        selection = cmds.ls(selection=True)
        cmds.select(deselect=True)
        with open(spellbook_path) as f:
            data = f.read().splitlines()
            for spell in data:
                spell_split = spell.split(":")
                original = spell_split[0]
                replacement = spell_split[1]
                spell_type = spell_split[2]

                # print("Replacing " + original + " " + spell_type + " with " + replacement)
                if spell_type == "Shader":
                    cmds.hyperShade(objects=original)
                elif spell_type == "Object":
                    cmds.select(original, replace=True)
                else:
                    print('Error applying spellbook')
                cmds.hyperShade(assign=replacement)
                cmds.select(deselect=True)
        cmds.select(selection)

def quick_rotate():
    cmds.select(all=True)
    cmds.rotate(90, 0, 90, a=True, p=[0,0,0])

    is_arnold = False
    arnold_list = cmds.ls('*Arnold*')
    if len(arnold_list) > 0:
        is_arnold = True

    if is_arnold:
        spellbook_path = spellbook_dir + '\\' + 'Arn2Blinn.spb'

    else:
        spellbook_path = spellbook_dir + '\\' + 'Hum2Blinn.spb'
        cmds.rotate(0, 0, -90, r=True, pivot=(0, 0, 0))
        cmds.select(deselect=True)
    cmds.select(deselect=True)

def remove_tires():
    try:
        tires = cmds.ls('*Tire*', '*tire*', '*Tyre*', '*tyre*')
        for tire in tires:
            try:
                print(tire)
                cmds.delete(tire)
            except Exception as e:
                print(e)

        rims = cmds.ls('*Rim*', '*rim*')
        for rim in rims:
            if (rim == 'rimShader') or (rim == 'rimSG') or (rim == 'Rims') or ('primary' in rim) or ('Primary' in rim):
                continue
            else:
                try:
                    print(rim)
                    cmds.delete(rim)
                except Exception as e:
                    print(e)

        brakes = cmds.ls('*Brake*', '*brake*')
        for brake in brakes:
            if (brake == 'brakeShader') or (brake == 'brakeSG'):
                continue
            else:
                try:
                    print(brake)
                    cmds.delete(brake)
                except Exception as e:
                    print(e)

        bolts = cmds.ls('*Bolt*', '*bolt*', '*Nuts*', '*nuts*')
        for bolt in bolts:
            try:
                print(bolt)
                cmds.delete(bolt)
            except Exception as e:
                print(e)

        logos = cmds.ls('*Logo*')
        for logo in logos:
            try:
                print(logo)
                cmds.delete(logo)
            except Exception as e:
                print(e)

        wheels = cmds.ls('*Wheel*', '*wheel*', '*disk*', '*Disk*', '*cylinder*', '*Cylinder*')
        for wheel in wheels:
            try:
                print(wheel)
                cmds.delete(wheel)
            except Exception as e:
                print(e)

        axis = cmds.ls('*Axis*', '*axis*', '*axel*', '*Axel*')
        for axel in axis:
            try:
                print(axel)
                cmds.delete(axel)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    try:
        tires = cmds.ls('*Tire*', '*tire*', '*Tyre*', '*tyre*',s=True)
        for tire in tires:
            try:
                print(tire)
                cmds.delete(tire)
            except Exception as e:
                print(e)

        rims = cmds.ls('*Rim*', '*rim*', s=True)
        for rim in rims:
            if (rim == 'rimShader') or (rim == 'rimSG') or (rim == 'Rims') or ('primary' in rim) or ('Primary' in rim):
                continue
            else:
                try:
                    print(rim)
                    cmds.delete(rim)
                except Exception as e:
                    print(e)

        brakes = cmds.ls('*Brake*', '*brake*', s=True)
        for brake in brakes:
            if (brake == 'brakeShader') or (brake == 'brakeSG'):
                continue
            else:
                try:
                    print(brake)
                    cmds.delete(brake)
                except Exception as e:
                    print(e)

        bolts = cmds.ls('*Bolt*', '*bolt*', '*Nuts*', '*nuts*', s=True)
        for bolt in bolts:
            try:
                print(bolt)
                cmds.delete(bolt)
            except Exception as e:
                print(e)

        logos = cmds.ls('*Logo*')
        for logo in logos:
            try:
                print(logo)
                cmds.delete(logo)
            except Exception as e:
                print(e)

        wheels = cmds.ls('*Wheel*', '*wheel*', '*disk*', '*Disk*', '*cylinder*', '*Cylinder*', s=True)
        for wheel in wheels:
            try:
                print(wheel)
                cmds.delete(wheel)
            except Exception as e:
                print(e)

        axis = cmds.ls('*Axis*', '*axis*', '*axel*', '*Axel*', s=True)
        for axel in axis:
            try:
                print(axel)
                cmds.delete(axel)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

def remove_license_plate():
    cmds.delete("LicPlate*")

def save():
    cmds.file(save=True, type='mayaBinary')
    cmds.select(all=True)
    cmds.file(force=True, type='OBJexport', es=True)

def auto_vc(path, sub, file):
    quick_rotate()
    apply_spellbook()
    remove_tires()
    remove_license_plate()

def search_folder(path):
    asset_match = re.search('.*/([a-zA-Z_0-9\(\)]*)', path)
    if asset_match != None:
        asset = asset_match.group(1)
        cmds.file(rename=asset)
        #print('\nGoing in to ' + asset)
    for file in os.listdir(path):
        #print('\n' + path + '\\' + file)
        run = True
        folder = True
        Render = False
        Smooth = False
        Unsmooth = False
        VC = False
        parent = False

        extensions = ['.mayaswatches', '.ma', '.mb','.ico', '.png', '.zip', '.vc4', '.mtl', '.obj', '.vc5', '.mel', '.jpg', '.rar', '.txt', '.fbx']

        if not os.path.isdir(path + '\\' + file):
            folder = False
            continue

        for sub in os.listdir(path + '\\' + file):
            if '.mayaswatches' in sub.lower():
                continue
            if not os.path.isdir(path + '\\' + file + '\\' + sub):
                folder = False
                continue
            if 'render' in sub.lower():
                print('Render folder found: ' + file)
                renderFolder = path + '\\' + file + '\\' + sub
                Render = True
                run = False
            if 'smooth' in sub.lower() and 'unsmooth' not in sub.lower():
                print('Smooth folder found: ' + file)
                smoothFolder = path + '\\' + file + '\\'  + sub
                Smooth = True
                run = False
            if 'unsmooth' in sub.lower():
                print('Unsmooth folder found: ' + file)
                unsmoothFolder = path + '\\' + file + '\\' + sub
                unsmoothSubName = sub
                Unsmooth = True
                run = False
            if 'vc' in sub.lower():
                print('VC folder found: ' + file)
                vcFolder = path + '\\' + file + '\\' + sub
                VC = True
                run = False
            if 'virtualcrash' in sub.lower():
                print('VC folder found: ' + file)
                vcFolder = path + '\\' + file + '\\' + sub
                VC = True
                run = False
        if run == True:
            parent = True
            search_folder(path + '\\' + file)

        if not parent:
            contains = [Render, Smooth, Unsmooth, VC]
            contains_str = ['Render', 'Smooth', 'Unsmooth', 'VC']
            if contains[3]:
                print('VC folder exists for ' + file)
                vc_exists = False
                for vcFile in os.listdir(vcFolder):
                    if '.obj' in vcFile:
                        vc_exists = True
                if vc_exists:
                    print('VC assest already exists for ' + file)
                else:
                    print('No .obj file for ' + file)
            if contains[2] and not vc_exists:
                print('Creating VC asset for ' + file)
                #os.mkdir(path + '\\' + file + '\\' + 'VirtualCrash')
                unsmooth_exists = False
                for mFile in os.listdir(unsmoothFolder):
                    if'.mb' in mFile:
                        vehicle_file = mFile
                        unsmooth_exists = True
                        break
                if unsmooth_exists:
                    print('Found unsmooth asset - starting job ' + unsmoothFolder)
                    auto_vc(path + '\\' + file, unsmoothSubName, vehicle_file)
                else:
                    print('No unsmooth asset found for ' + unsmoothFolder)
            elif contains[1] and not contains[2] and not vc_exists:
                print('No VC folder found for ' + file)
                print('Creating VC folder')
                #os.mkdir(path + '\\' + file + '\\' + 'VirtualCrash')
                smooth_exists = False
                for mFile in os.listdir(smoothFolder):
                    if '.ma' in mFile or '.mb' in mFile:
                        smooth_exists = True
                        break
                if smooth_exists:
                    print('Found smooth asset - starting job ' + smoothFolder)
                else:
                    print('No smooth or unsmooth asset found for ' + smoothFolder)
            elif not contains[1] and not contains[2]:
                print('Creating VC folder')
                #os.mkdir(path + '\\' + file + '\\' + 'VirtualCrash')
                print('No maya file found for ' + file)

        else:
            print(file + ' is a parent folder')
            pass

        print('Next, leaving folder: ' + file + '\n')

search_folder(folder)
