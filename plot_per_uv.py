import os
import numpy as np
import scipy
import matplotlib.pyplot as plt

import pandas as pd
import seaborn as sns
sns.set_style('ticks')

import utils

df = pd.read_csv('table.csv')

# First, count orbits per cycle on different instruments. To this end, plot one histogram per cycle:
cycles = [29, 30, 31]#df['Cycle'].unique().sort()
element = 'UV'
configurations = df[element].unique()
index = np.arange(len(configurations))
counts = np.zeros(len(configurations))

offset = {}
offset[29] = -0.1
offset[30] = 0.0
offset[31] = 0.1
for cycle in cycles:

    df_cycle = df[df['Cycle']==cycle]
    k = 0
    total = 0
    for configuration in configurations:
        
        dfc = df_cycle[ df_cycle[element]==configuration ]
        counts[k] = dfc['Prime Orbits'].sum()
        total += counts[k]
        k += 1

    print('Total for cycle',cycle,':',total)
    plt.bar(index+offset[cycle], counts, label = 'Cycle '+str(cycle), width=0.1)

plt.xticks(index, configurations, fontsize = 15)
plt.yticks(fontsize = 15)
plt.ylabel('Total Orbits', fontsize = 17)
plt.xlabel('UV Science?', fontsize = 17)
plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", mode="expand", fontsize = 15, ncol = 3)
plt.show()
