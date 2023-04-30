import pyaudio
import crepe
import numpy as np
import itertools as it

import time

notes = 'a a# b c c# d d# e f f# g g#'.split()

def frequency_to_note(f, a4=440):
    s = 12 * np.log2(f/a4)
    octave_diff = int(s // 12)
    note_diff = int(s % 12)
    return notes[note_diff] + str(octave_diff + 4)

CHUNK = 1024
CHANNELS = 1
RATE = 48000    # 48 kHz
TIME = 0.10     # 10 ms

FREQ = 0

forever = it.cycle(range(2**32))

def get_freq(f, frame_count, volume=0.5, fs=RATE):
    # r = (volume * (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)).tobytes()
    x = np.fromiter(it.islice(forever, frame_count), dtype=np.float32)
    r = (volume * (np.sin(2 * np.pi * x * f / fs)).astype(np.float32)).tobytes()
    return r

def callback(in_data, frame_count, time_info, status_flags):
    return (get_freq(FREQ, frame_count), pyaudio.paContinue)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
out    = p.open(format=pyaudio.paFloat32, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=callback)
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
        if conf > 0.3:
            print(frequency_to_note(freq), freq, conf, end='\r')
            FREQ = freq
        else:
            print(FREQ, 100 * ' ', end='\r')
except KeyboardInterrupt:
    pass
finally:
    stream.close()
    out.close()
    p.terminate()
