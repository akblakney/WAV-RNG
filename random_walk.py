'''
Simple script for plotting a random walk based on a binary file
whose contents are random.

'''

import sys
import matplotlib.pyplot as plt
from x_from_bytes import binary_from_byte

# walks N steps from data in file, returns list containing
# points
# file should be opened beforehand
def walk(file, N):
    x = [0]
    byte = file.read(1)
    count = 0
    while byte and count < N:
        bstring = binary_from_byte(ord(byte))
        for i in range(len(bstring)):
            if bstring[i] == '1':
                x.append(x[-1] + 1)
            else:
                x.append(x[-1] - 1)
        byte = file.read(1)
        count += 8
    return x

file = open(sys.argv[1],'rb')
N = 2e6
walks = []
title = 'Title'
for i in range(1):
    walks.append(walk(file, N))

fig,ax=plt.subplots()
fig.suptitle(title)

for x in walks:
    ax.plot(x)

ax.set_facecolor('black')
plt.show()
file.close()
