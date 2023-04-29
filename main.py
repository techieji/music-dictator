import pyaudio
import wave
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
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

#t = time.time()
#rec = time.time()
#while time.time() - t < RECORD_SECONDS:
#    if time.time() - rec > 0.5:
#        print('.', end="", flush=True)
#        data1 = stream.read(CHUNK)
#        data2 = stream.read(CHUNK)
#        data3 = stream.read(CHUNK)
#        frames.extend([data1] * 7 + [data2] * 7 + [data3] * 7)
#        rec = time.time()

print("* done recording")

print(frames[0])

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
