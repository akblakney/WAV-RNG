# this script plots the even and odd bytes given a file as command line arg
# this is useful for verifying the fact that the even bytes look random
# while the odd bytes may not be

import matplotlib.pyplot as plt
import sys
inf = sys.argv[1]
file = open(inf,'rb')
_ = file.read(100)
byte = file.read(1) # start at 0th byte
i = 0
N = int(400)
even = []
odd = []

# x = file1 = even bytes
# y = file2 = odd bytes
while byte and i < N:

    even.append(ord(byte))
    byte = file.read(1)
    odd.append(ord(byte))
    byte = file.read(1)
    i += 1


fig,ax=plt.subplots(2)
ax[0].plot(even)
ax[0].set_title('even')
ax[1].plot(odd)
ax[1].set_title('odd')
plt.show()
