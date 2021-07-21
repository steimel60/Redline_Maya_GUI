filename = r'C:\Users\DylanSteimel\Desktop\fallstraightdown.csv'
f = open(filename, "r")
lines = f.readlines()
f.close()

#Clean CSV
lines = [line.split(',') for line in lines]
for i in range(0,len(lines)):
    lines[i] = [item.strip() for item in lines[i] if item != '' and item != '\n']

#Get joint list
parts = []
partIndices = []
for i in range(0,len(lines)-1):
    if 'time [ s]' in lines[i+1]:
        parts.append(lines[i][0])
        partIndices.append(i)

frameTotal = partIndices[1] - partIndices[0]

#Create MOV Files
jointFiles = []
for i in range(0,len(parts)):
    name = str(parts[i])
    name = name.split(' ')
    new_name = ''
    for i in range(0,len(name)):
        new_name += name[i]
    name = new_name
    f = open(r'C:\Users\DylanSteimel\Desktop' + '/' + name + '.mov', 'w')
    jointFiles.append(r'C:\Users\DylanSteimel\Desktop' + '/' + name + '.mov')
    for j in range(2, frameTotal):
        for k in range(0,len(lines[partIndices[i] + j])):
            f.write(lines[partIndices[i] + j][k] + ' ')
        f.write('\n')

f.close()

for file in jointFiles:
    print(file)
