import sounddevice as sd
import soundfile as sf
import subprocess
import numpy as np
import os

AUDIO_FILE = "audio.wav"
SAMPLERATE = 16000
CHANNELS = 1
STATE_FILE = ".recording_state"

# Toggle state: if state file exists, stop recording and send; else, start recording
if os.path.exists(STATE_FILE):
    # Stop recording and send to Docker
    print("Stopping recording and sending audio to Docker...")
    # Remove state file
    os.remove(STATE_FILE)
    # Assume audio.wav was recorded by previous run
    subprocess.run([
        "docker", "run", "--rm", "--gpus", "all",
        "-v", f"{os.getcwd()}/{AUDIO_FILE}:/input/audio.wav",
        "-e", f"DISPLAY={os.environ.get('DISPLAY')}",
        "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
        "-u", f"{os.getuid()}:{os.getgid()}",
        "whisper-braindumper:latest",
        "/app/process_audio.sh", "/input/audio.wav"
    ])
else:
    # Start recording
    print("Recording... Press Win+C again to stop.")
    with open(STATE_FILE, "w") as f:
        f.write("recording")
    recording = []
    try:
        with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype='int16') as stream:
            while os.path.exists(STATE_FILE):
                data, _ = stream.read(1024)
                recording.append(data)
    except KeyboardInterrupt:
        pass
    audio = np.concatenate(recording, axis=0)
    sf.write(AUDIO_FILE, audio, SAMPLERATE)
    print("Recording stopped, saved to", AUDIO_FILE)
    # Keep state file for next toggle