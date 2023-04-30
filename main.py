import pyaudio
import wave
import time

import numpy as np
import scipy.fft as fft
from visdom import Visdom

CHUNK = 1024
FORMAT = pyaudio.paInt16    # 2 bytes
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

RECORD = False

if RECORD:
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames: list[bytes] = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
else:
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
    frames: bytes = wf.readframes(wf.getnframes())
    wf.close()

_frames: bytes = b''.join(frames) if type(frames) is list else frames
frames = np.fromiter(map(lambda a, b: a*2**8 + b, _frames[::2], _frames[1::2]), dtype=np.int32, count=int(RATE / CHUNK * RECORD_SECONDS))
transform = fft.fft(frames)[1:]
ind = abs(transform).argmax()
print(ind * RATE / len(frames), abs(transform)[ind])

vis = Visdom()

vis.line(abs(transform), np.array(range(1,len(transform)+1)) * RATE / len(transform))
