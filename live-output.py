import pyaudio
import crepe
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16   # 2 bytes
CHANNELS = 1
RATE = 48000    # 48 kHz
TIME = 0.05     # 10 ms

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
print('starting up...')

try:
    while True:
        frames = b''
        for i in range(0, int(RATE / CHUNK * TIME) + 1):
            frames += stream.read(CHUNK)
        arr = np.array(memoryview(frames).cast('H').tolist())
        time, frequency, confidence, activation = crepe.predict(arr, RATE, viterbi=True, verbose=0)
        print(frequency.mean(), confidence.mean(), end='\r')
except KeyboardInterrupt:
    pass
