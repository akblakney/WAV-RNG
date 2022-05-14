from verify_methods import normalize_dist_to_list
import sys
import matplotlib.pyplot as plt


f = open(sys.argv[1], 'rb')

b = f.read(2)
ind = 0
N = 1e7
raw_signal = []
while b and ind < N:
    raw_signal.append(int.from_bytes(b, byteorder='little', signed=True))
    b = f.read(2)
    ind += 1

print('h')

fig, ax = plt.subplots(1)
ax.plot(raw_signal)
plt.show()
