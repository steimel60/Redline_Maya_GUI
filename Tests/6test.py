from matplotlib import animation
import matplotlib.pyplot as plt
from coinDicts import *
from pycoingecko import CoinGeckoAPI
import datetime as dt
from IPython import display
from settings import *
cg = CoinGeckoAPI()
#Set Up
coins = [DOT,SOL,ADA,ETH,BTC]
#Edit Ticks
tickVals = [i*10 for i in range(0,5)]
tickLabels = ['0','10B','20B','30B','40B']
#Get Data
vols=[]
for coin in coins:
    info = cg.get_coin_market_chart_by_id(coin['id'],'usd',7,localization=False,interval='minutely')
    vols.append([info['total_volumes'][i][1]/1000000000 for i in range(0,len(info['total_volumes']))])
time = now
#Plot Graph
plt.style.use('cryptographs')
coinNames = [coin['name'] for coin in coins]
colors = [coin['color'] for coin in coins]
fig=plt.figure(figsize=(12,7), dpi=100)
n=len(vols[0]) #Number of frames
x=range(0,5)
def animate(i):
    #Calculate Date of Data
    hoursPrior = n - i
    change = dt.timedelta(hours=hoursPrior)
    history = time - change
    date = f"{monthStr[history.month-1]} {history.day}"
    #Reset Plot every frame
    plt.cla()
    plt.ylim(-.5,4.5)
    plt.xlim(0,45)
    heights = [val[i-1] for val in vols]
    plt.barh(coinNames,heights,color=colors)
    plt.xticks(tickVals,tickLabels)
    plt.tick_params(left=False)
    plt.title(f'24 Hour Rolling Volumes: {date}')
    plt.xlabel('USD Value (in Billions)')
    for u, v in enumerate(heights):
        ax = plt.gca()
        ax.text(v + 2, u, str(round(v,1))+'B', color=colors[u], va='center')
anim=animation.FuncAnimation(fig,animate,repeat=False,blit=False,frames=n,interval=125)
f = r"C:/Users/Dylan/Desktop/animation.gif"
writergif = animation.PillowWriter(fps=60)
anim.save(f, writer=writergif)
plt.show()
