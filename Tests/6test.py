import os

user_profile = os.environ['USERPROFILE']
DOCUMENTS_DIR = user_profile + '/Documents'
UNREAL_PROJECT_DIR = DOCUMENTS_DIR + '/Unreal Projects'
file = 'testFile.txt'
if not os.path.exists(UNREAL_PROJECT_DIR+'/Maya2Unreal'):
    os.makedirs(UNREAL_PROJECT_DIR+'/Maya2Unreal')

if not os.path.exists(UNREAL_PROJECT_DIR+'/Maya2Unreal/'+file):
    f=open(UNREAL_PROJECT_DIR+'/Maya2Unreal/'+file,'w')
    f.close()
f = open(UNREAL_PROJECT_DIR+'/Maya2Unreal/testFile.txt','r+')
current = f.readlines()
current = [line.strip().split(',') for line in current]
f.close()

f = open(UNREAL_PROJECT_DIR+'/Maya2Unreal/testFile.txt','a+')
line = 'file.fbx,option1,option2'
line2 = 'another line'
lines = [line, line2]
lines = [l.strip().split(',') for l in lines]


print(f'current: {current}')
print(f'lines: {lines}')

for l in lines:
    if l not in current:
        f.write(l+'\n')
f.close()
