import sys
import matplotlib.pyplot as plt
from x_from_bytes import binary_from_byte

file = open(sys.argv[1],'rb')
byte = file.read(1)
x=[0]
y=[0]
ind = 0
N = 2e4
while byte and ind < N:

    bstring = binary_from_byte(ord(byte))
    for i in range(len(bstring) // 2):
        curr = bstring[i:i+2]
        if curr == '00':
            x.append(x[-1] + 1)
            y.append(y[-1])
        elif curr == '01':
            x.append(x[-1] - 1)
            y.append(y[-1])
        elif curr == '10':
            x.append(x[-1])
            y.append(y[-1] - 1)
        elif curr == '11':
            x.append(x[-1])
            y.append(y[-1] + 1)
    byte = file.read(1)
    ind += 1

fig,ax=plt.subplots()
fig.suptitle('2d random walk over two million steps')
ax.plot(x,y)
ax.set_facecolor('black')
plt.show()

