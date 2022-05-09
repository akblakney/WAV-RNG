# Measures autocorrelation of a signal.
# this is NOT my script. This is from reallyreallyrandom.com


import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sys

inf = sys.argv[1]

# randomStuff = np.random.randn(10_000)
# myData = np.loadtxt('/mnt/documents/RRR/engineering/calculations/zenerglass/raw-reads/010.data')
# myData = np.loadtxt('/tmp/zener-arduino.dat')
# myData = np.random.randint(256, size=100_000) - 127  # signal has to be AC (+ve and -ve)
myData = np.fromfile(inf, dtype='uint8')


signalData = myData.astype('float')
signalData -= np.mean(signalData)   # Need this to convert to AC waveform
correlation = signal.convolve(signalData, signalData[::-1], mode='full')

nc = correlation / max(correlation)   # normalise

fig, (ax_orig, ax_mag) = plt.subplots(2, 1)
ax_orig.plot(signalData, color='purple')
ax_orig.set_title('Raw Signal')
ax_mag.plot(np.arange(-len(signalData) + 1, len(signalData)), nc, color='purple')

ax_mag.set_title('Autocorrelation')
fig.canvas.set_window_title('Correlation Analysis')
fig.tight_layout()
fig.suptitle('Signal and Autocorrelation for Even Bytes')
plt.show()
