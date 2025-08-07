import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import sys
import psutil
import time

AUDIO_FILE = '/tmp/input.wav'
LOCK_FILE = '/tmp/record_and_send.lock'
SAMPLERATE = 16000
CHANNELS = 1

def kill_previous():
    try:
        with open(LOCK_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            p.terminate()
            print(f"Killed previous recording process (PID {pid})")
        os.remove(LOCK_FILE)
    except Exception as e:
        print(f"No previous recording found or error: {e}")

def record():
    print("Recording... (run again to stop)")
    frames = []
    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS) as stream:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        try:
            while True:
                data, _ = stream.read(1024)
                frames.append(data)
        except KeyboardInterrupt:
            print("Stopped by user.")
        except Exception as e:
            print(f"Recording interrupted: {e}")
    audio = np.concatenate(frames, axis=0)
    sf.write(AUDIO_FILE, audio, SAMPLERATE)
    print(f"Saved to {AUDIO_FILE}")
    os.system('notify-send "Audio sent for processing"')
    time.sleep(1)
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

if os.path.exists(LOCK_FILE):
    kill_previous()
    sys.exit(0)
else:
    record()
