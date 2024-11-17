import matplotlib.pyplot as plt
import numpy as np

from matplotlib import colors
from matplotlib.ticker import PercentFormatter


data1 = []
with open("Out.txt") as f:
    for line in f:
        data1.append(([int(x) for x in line.split()]))

len = len(data1[0])

fig, axs = plt.subplots(1, 4, sharey=True, tight_layout=True)

axs[0].hist(data1[0], bins=20)
axs[1].hist(data1[1], bins=20)
axs[2].hist(data1[2], bins=20)
axs[3].hist(data1[3], bins=20)

plt.show()

