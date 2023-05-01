import pyaudio
import crepe
import numpy as np
import itertools as it
import keyboard as kb

import time

notes = 'a a# b c c# d d# e f f# g g#'.split()

def frequency_to_note(f, a4=440):
    if f != 0:
        s = 12 * np.log2(f/a4)
        octave_diff = int(s // 12)
        note_diff = int(s % 12)
        return notes[note_diff] + str(octave_diff + 4)
    return '00'

def autotune(f, a4=440):
    if f != 0:
        s = int(12 * np.log2(f/a4))
        return pow(2, s/12) * a4
    return 0

CHUNK = 1024
CHANNELS = 1
RATE = 48000    # 48 kHz
TIME = 0.10     # 10 ms

FREQ = 0
FREEZE = False
ADJUST = 1

def toggle_freeze():
    global FREEZE
    FREEZE = not FREEZE

def adjust_by(s):
    global ADJUST
    ADJUST *= pow(2, s/12)

def reset():
    global ADJUST
    global FREEZE
    global FREQ
    ADJUST = 1
    FREQ = 0
    FREEZE = False

def log():
    print()

kb.add_hotkey('f', toggle_freeze)
kb.add_hotkey('w', lambda: adjust_by(1))
kb.add_hotkey('s', lambda: adjust_by(-1))
kb.add_hotkey('i', lambda: adjust_by(0.25))
kb.add_hotkey('k', lambda: adjust_by(-0.25))
kb.add_hotkey('g', lambda: adjust_by(12))
kb.add_hotkey('t', lambda: adjust_by(-12))
kb.add_hotkey('r', reset)
kb.add_hotkey('space', log)

forever = it.cycle(range(2**32))

def get_freq(f, frame_count, volume=0.25, fs=RATE):
    # r = (volume * (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)).tobytes()
    x = np.fromiter(it.islice(forever, frame_count), dtype=np.float32)
    r = (volume * (np.sin(2 * np.pi * x * f / fs)).astype(np.float32)).tobytes()
    return r

def callback(in_data, frame_count, time_info, status_flags):
    return (get_freq(autotune(FREQ * ADJUST), frame_count), pyaudio.paContinue)

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
        if FREEZE:
            freq = FREQ
        if FREEZE:
            print('<f>', frequency_to_note(freq * ADJUST), freq, 100 * ' ', end='\r')
        elif conf > 0.3:
            print('<n>', frequency_to_note(freq * ADJUST), freq, 100 * ' ', end='\r')
            FREQ = freq
        else:
            print('<?>', frequency_to_note(FREQ * ADJUST), FREQ, 100 * ' ', end='\r')
except KeyboardInterrupt:
    pass
finally:
    stream.close()
    out.close()
    p.terminate()
