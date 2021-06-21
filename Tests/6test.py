import re

dir = r'C:\Users\DylanSteimel\Desktop\GMC.mov'

assetMatch = re.search('/*([a-zA-Z0-9-_]*)\.mov', dir)
asset = assetMatch.group(1)
print(asset)
print(assetMatch)
