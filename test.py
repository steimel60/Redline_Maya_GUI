import os
import re

folder = 'C:\\Users\\DylanSteimel\\deltav\\Jason Young - Asset Library\\3D Vehicle Library'



#for item in Categories:
#    print('\n' + item)
#    for asset in os.listdir(folder + '\\' + item):
#        print('\n'+ asset)
#        try:
#            for file in os.listdir(folder + '\\' + item + '\\' + asset):
#                if '.mayaSwatches' in file:
#                    break
#                print(file)
#        except:
#            pass

def search_folder(path):
    asset_match = re.search('.*/([a-zA-Z_0-9\(\)]*)', path)
    if asset_match != None:
        asset = asset_match.group(1)
        cmds.file(rename=asset)
        print('\nGoing in to ' + asset)
    for file in os.listdir(path):
        print('\n' + path + file)
        run = True
        folder = True
        Render = False
        Smooth = False
        Unsmooth = False

        extensions = ['.mayaswatches', '.ma', '.mb','.ico', '.png', '.zip', '.vc4', '.mtl', '.obj', '.vc5', '.mel', '.jpg', '.rar']
        for ext in extensions:
            if ext in file.lower():
                print('Not a folder')
                folder = False
        if folder == False:
            break

        for sub in os.listdir(path + '\\' + file):
            #print(sub)
            if 'Render' in sub:
                Render = True
                run = False
            if 'Smooth' in sub:
                Smooth = True
                run = False
            if 'Unsmooth' in sub:
                Unsmooth = True
                run = False
            elif '.mayaSwatches' in sub:
                run = False
            elif '.ma' in sub:
                run = False
            elif '.mb' in sub:
                run = False
            elif '.ico' in sub:
                run = False
            elif '.png' in sub:
                run = False
            elif '.zip' in sub:
                run = False
            elif '.vc4' in sub:
                run = False
            if run == True:
                search_folder(path + '\\' + file)

        contains = [Render, Smooth, Unsmooth]
        contains_str = ['Render', 'Smooth', 'Unsmooth']
        for i in range(0, len(contains)):
            if contains[i] == True:
                print(file + ' contains ' + contains_str[i])
            if contains[i] == False:
                print(file + ' needs ' + contains_str[i])


search_folder(folder)
