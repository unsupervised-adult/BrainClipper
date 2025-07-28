import sounddevice as sd
import soundfile as sf
import keyboard
import numpy as np
import time
import os

AUDIO_FILE = '/tmp/input.wav'
SAMPLERATE = 16000
CHANNELS = 1

print("Press F9 to start recording. Press F9 again to stop.")

while True:
    keyboard.wait('F9')
    print("Recording...")
    frames = []
    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS) as stream:
        while True:
            data, _ = stream.read(1024)
            frames.append(data)
            if keyboard.is_pressed('F9'):
                print("Stopping...")
                break
    audio = np.concatenate(frames, axis=0)
    sf.write(AUDIO_FILE, audio, SAMPLERATE)
    print(f"Saved to {AUDIO_FILE}")
    # Optionally notify user
    os.system('notify-send "Audio sent for processing"')
    time.sleep(1)
    print("Ready for next recording.")
