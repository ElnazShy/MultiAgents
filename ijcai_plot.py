import matplotlib.pyplot as plt
from numpy import *
import os
import pickle

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

###
# DATA AND PLOT SETTINGS
###
SIZE = [20]
AGENTS = [1,3,5,7,10]
ITEMS = [20]
RADIUS = [5]

ROOT_DIR = './results/pickles/'
FIG_SIZE = [8,6]

###
# LOADING PICKLE FILES
###
mcts, pomcp = [], []
for s in SIZE:
	for a in AGENTS:
		for i in ITEMS:
			print('Reading file: s'+str(s)+'_a'+str(a)+'_i'+str(i))
			mcts_f = open(ROOT_DIR+'MCTS_s'+str(s)+\
				'_a'+str(a)+'_i'+str(i)+'_Pickle','r')
			mcts.append(pickle.load(mcts_f))
			mcts_f.close()

			for r in RADIUS:
				print('Reading file: s'+str(s)+'_a'+str(a)+'_i'+str(i)+'_r'+str(r))
				pomcp_f = open(ROOT_DIR+'POMCP_s'+str(s)+\
					'_a'+str(a)+'_i'+str(i)+'_r'+str(r)+'_Pickle','r')
				pomcp.append(pickle.load(pomcp_f))
print(mcts,pomcp)

###
# PERFORMANCE PLOT
###
fig, ax = plt.subplots(figsize=FIG_SIZE)

AGA, ABU, OEAT = [], [], []
AGA_ci, ABU_ci, OEAT_ci = [], [], []
for m in mcts:
    AGA.append(mean(m.AGA_timeSteps))
    AGA_ci.append(std(m.AGA_timeSteps))
    ABU.append(mean(m.ABU_timeSteps))
    ABU_ci.append(std(m.AGA_timeSteps))
    OEAT.append(mean(m.OGE_timeSteps))
    OEAT_ci.append(std(m.AGA_timeSteps))

POMCP, POMCP_ci = [], []
for p in pomcp:
    POMCP.append(mean(m.pomcp_timeSteps))
    POMCP_ci.append(std(m.pomcp_timeSteps))

ax.errorbar(AGENTS,OEAT,OEAT_ci,
             label='OEAT',
             color='#F66095',
             #linestyle='-.',
             marker ='o',
             markevery=10
             #linewidth=2
             )

ax.errorbar(AGENTS,AGA,AGA_ci,
	         label='AGA',
	         color='#3F5D7D',
	         #linestyle='-',
	         marker='^',
	         markevery=10
	         #linewidth=2
	          )

ax.errorbar(AGENTS,ABU,ABU_ci,
             label='ABU',
             color='#37AA9C',
             #linestyle='--',
             marker='v',
             markevery=10,
             #linewidth=2
             )

ax.errorbar(AGENTS,POMCP,POMCP_ci,
             label='POMCP',
             color='#CA8235',
             # linestyle='-.',
             marker='o',
             markevery=10
             # linewidth=2
             )

# 4. Saving the result
axis = plt.gca()
axis.set_ylabel('Number of Iterations',fontsize='x-large')
axis.set_xlabel('Number of Agents',fontsize='x-large')
axis.xaxis.set_tick_params(labelsize=14)
axis.yaxis.set_tick_params(labelsize=14)
axis.legend(loc="lower center", fontsize='x-large',\
			borderaxespad=0.1,borderpad=0.1,handletextpad=0.1,\
			fancybox=True,framealpha=0.8,ncol=4)
	
axins = inset_axes(ax, 4.5,2, loc='upper right') # zoom-factor: 2.5, location: upper-left
axins.errorbar(AGENTS,OEAT,OEAT_ci,
             label='OEAT',
             color='#F66095',
             #linestyle='-.',
             marker ='o',
             markevery=10
             #linewidth=2
             )

axins.errorbar(AGENTS,AGA,AGA_ci,
	         label='AGA',
	         color='#3F5D7D',
	         #linestyle='-',
	         marker='^',
	         markevery=10
	         #linewidth=2
	          )

axins.errorbar(AGENTS,ABU,ABU_ci,
             label='ABU',
             color='#37AA9C',
             #linestyle='--',
             marker='v',
             markevery=10,
             #linewidth=2
             )

axins.errorbar(AGENTS,POMCP,POMCP_ci,
             label='POMCP',
             color='#CA8235',
             # linestyle='-.',
             marker='o',
             markevery=10
             # linewidth=2
             )
x1, x2, y1, y2 = 3, 10, 50, 100 # specify the limits
axins.set_xlim(x1, x2) # apply the x-limits
axins.set_ylim(y1, y2) # apply the y-limits
#mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

#plt.savefig("./plots/"+plotname+'.pdf', bbox_inches = 'tight',pad_inches = 0)
#plt.close(fig)

plt.show()

