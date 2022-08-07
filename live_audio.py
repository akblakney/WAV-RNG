import wave
import time
import pyaudio
from x_from_bytes import hex_from_bytes, ascii_from_bytes
from hashlib import sha256
from generator import bytes_from_block

# setup pyaudio and constants
p = pyaudio .PyAudio()
MIN_READ = 2048
#BLOCK_SIZE = 4096 # note: BLOCK_SIZE in bytes, but audio stream in 16-bit ints.
BLOCK_SIZE = 8192 * 4 # = 2^15 = approx. 32kb
chunk = 1024
sample_format = pyaudio.paInt16
channels = 1
rate = 48000
fpb=1024
N = 2000


# init stream
stream = p.open(format=sample_format,
  channels=channels,
  rate=rate,
  output=True,
  input=True,
  frames_per__buffer=fpb)

stream.start_stream()

# wait before starting
time.sleep(1)

# main loop
i = 0
#while stream.is_active():
_buffer = bytearray()
while i < N:

  # read in available bytes
  available = stream.get_read_available()
  if available == 0:
    time.sleep(.2)
    continue

  #print('available: {}'.format(available))
  _buffer.extend(stream.read(available))
  #print('in _buffer: {}'.format(len(_buffer)))

  # if enough to feed a block to RNG, do so
  if len(_buffer) > BLOCK_SIZE:
    curr_wav_bytes = _buffer[:BLOCK_SIZE]
    _buffer = _buffer[BLOCK_SIZE:]

    rand_bytes = bytes_from_block(curr_wav_bytes, no_hash=True)
    print('{}: {}'.format(i, ascii_from_bytes(rand_bytes)[:20]))
    i += 1

stream.stop_stream()
print('here')
