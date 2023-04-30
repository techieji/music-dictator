import pyaudio
import crepe
import numpy as np

notes = 'a a# b c c# d d# e f f# g g#'.split()

def frequency_to_note(f, a4=440):
    s = 12 * np.log2(f/a4)
    octave_diff = int(s // 12)
    note_diff = int(s % 12)
    return notes[note_diff] + str(octave_diff + 4)

CHUNK = 1024
FORMAT = pyaudio.paInt16   # 2 bytes
CHANNELS = 1
RATE = 48000    # 48 kHz
TIME = 0.10     # 10 ms

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)
print('starting up...')

try:
    while True:
        frames = b''
        for i in range(0, int(RATE / CHUNK * TIME) + 1):
            frames += stream.read(CHUNK)
        arr = np.array(memoryview(frames).cast('H').tolist())
        time, frequency, confidence, activation = crepe.predict(arr, RATE, viterbi=True, verbose=0)
        freq = frequency.mean()
        conf = confidence.mean()
        if conf > 0.2:
            print(frequency_to_note(freq), conf, end='\r')
        else:
            print(100 * ' ', end='\r')
except KeyboardInterrupt:
    pass
