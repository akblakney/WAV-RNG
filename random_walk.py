import sys
import matplotlib.pyplot as plt
from x_from_bytes import binary_from_byte

file = open(sys.argv[1],'rb')
byte = file.read(1)
x=[0]
count = 0
max_count = 1e6
while byte and count < max_count:

    bstring = binary_from_byte(ord(byte))
    for i in range(len(bstring)):
        if bstring[i] == '1':
            x.append(x[-1] + 1)
        else:
            x.append(x[-1] - 1)
    byte = file.read(1)
    count += 8

fig,ax=plt.subplots()
ax.plot(x)
ax.set_facecolor('black')
plt.show()
