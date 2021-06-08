import pandas as pd
import os


user_profile = os.environ['USERPROFILE']
desktop_dir = user_profile + '\\Desktop'

filename = desktop_dir + '\\' + 'text4u.xyz'
f = open(filename, 'r')
full = f.readlines()
for i in range(0,len(full)):
    full[i] = full[i].rstrip()
    full[i] = full[i].split(' ')

f.close()

df = pd.DataFrame(full)

df.to_csv(desktop_dir + '\\' + 'testcsv.csv')
