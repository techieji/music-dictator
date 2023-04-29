import pyaudio
import wave
import time

import numpy as np
import scipy.fft as fft

CHUNK = 1024
FORMAT = pyaudio.paInt16    # 2 bytes
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

if False:
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

_frames = b''.join(frames)
frames = np.fromiter(map(lambda a, b: a*2**8 + b, _frames[::2], _frames[1::2]), dtype=np.int32, count=int(RATE / CHUNK * RECORD_SECONDS))
# frames = np.fromiter(map(lambda a, b: int.from_bytes(bytes([a]) + bytes([b])), _frames[::2], _frames[1::2]), dtype=np.int32, count=int(RATE / CHUNK * RECORD_SECONDS))
transform = fft.fft(frames)
