# BrainClipper

**BrainClipper** converts spoken audio into concise, professional clipboard text using Whisper for transcription and an LLM (Gemma or Granite via Ollama) for refinement. Designed for fast, accurate speech-to-clipboard workflows in Linux environments.

## Features

- Records audio from your microphone (host-side)
- Transcribes speech to text using Whisper (container, GPU-accelerated)
- Refines text with Gemma/Granite LLM via Ollama (container, GPU-accelerated)
- Copies the final result to your clipboard using CopyQ (container, X11 clipboard)
- Hotkey integration for instant recording and processing

## Project Structure

- `linux/` — Linux container files and scripts
- `app/` — Core processing scripts (transcribe, refine, entrypoint, etc.)

## Usage

### Linux

1. **Build the Podman image (with GPU support):**

   ```bash
   cd linux
   podman build -t braindumper .
   ```

   - For Docker, use:

     ```bash
     docker build -t braindumper .
     ```

2. **Run the container with GPU and audio passthrough:**

   ```bash
   ./run_speech.sh
   ```

   - This script mounts your audio device (`/dev/snd`), X11 socket, and clipboard, and passes the recorded audio file to the container.
   - Ensure you have permissions for `/dev/snd` and X11 access (e.g., `xhost +local:`).
   - For manual Podman/Docker run:

     ```bash
     podman run --rm \
       --device /dev/snd \
       -e DISPLAY=$DISPLAY \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       -v /path/to/input.wav:/input/audio.wav \
       --gpus all \
       braindumper
     ```

     - Replace `/path/to/input.wav` with your recorded audio file.

3. **Map to a hotkey:**
   - Go to your OS keyboard shortcuts settings (e.g., GNOME/KDE: System Settings → Keyboard → Shortcuts)
   - Add a custom shortcut to run `./run_speech.sh` for instant speech-to-clipboard

4. **Rephrase highlighted/clipboard text:**
   - Copy any text you want to rephrase to your clipboard
   - Run the following command:

     ```bash
     python3 app/refine_clipboard.py
     ```

   - The rephrased text will be copied back to your clipboard
   - (Optional) Map this command to a hotkey for instant rephrasing

## Starting the Container

To run the container so it continuously waits for audio files:

```bash
./run_speech.sh
```

Or manually:

```bash
podman run --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -e DISPLAY=$DISPLAY \
    --device /dev/snd:/dev/snd \
    --group-add $(getent group audio | cut -d: -f3) \
    --workdir /app \
    braindumper
```

## Running as a Service (Optional)

You can run the container as a background service using systemd:

1. Create a systemd unit file (e.g., `/etc/systemd/system/braindumper.service`):

```ini
[Unit]
Description=BrainClipper Speech-to-Clipboard Container
After=network.target

[Service]
ExecStart=/home/$USER/Documents/Project-Code/whisper-braindumper/linux/run_speech.sh
Restart=always
User=$USER

[Install]
WantedBy=default.target
```

1. Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now braindumper.service
```

This will keep the container running in the background, ready to process audio files as they appear.

## GPU Passthrough Instructions

### Linux (Podman/Docker)

- Ensure you have the NVIDIA Container Toolkit installed:

  ```bash
  sudo apt install nvidia-container-toolkit
  sudo systemctl restart docker
  ```

- Run containers with `--gpus all` (Docker) or Podman equivalent.
- Verify GPU access inside the container:

  ```bash
  podman run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
  ```

- For X11 clipboard access, allow local connections:

  ```bash
  xhost +local:
  ```

## Troubleshooting Podman GPU Access

If you get an error like:

```bash
Error: OCI runtime error: crun: error executing hook `/usr/bin/nvidia-container-toolkit` (exit code: 2)
```

Follow these steps to fix:

1. **Install NVIDIA Container Toolkit:**

   ```bash
   sudo apt update
   sudo apt install nvidia-container-toolkit
   ```

2. **Check for OCI hook config:**
   After installation, you should see a file like `/usr/share/containers/oci/hooks.d/nvidia-container-toolkit.json`.

3. **Copy the hook config if needed:**

   ```bash
   sudo cp /usr/share/containers/oci/hooks.d/nvidia-container-toolkit.json /etc/containers/oci/hooks.d/
   ```

4. **Restart Podman and reboot:**

   ```bash
   sudo systemctl restart podman
   sudo reboot
   ```

5. **Test GPU access in a container:**

   ```bash
   podman run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
   ```

   If you see your GPU info, Podman is set up correctly.

If you encounter any errors during installation or the hook file is still missing, check your Linux distribution and version for more targeted help.

## Requirements

- Podman or Docker with GPU support
- Audio input device (`/dev/snd` on Linux)
- X11 clipboard (CopyQ)
- Python 3.8+
- NVIDIA GPU and drivers (for GPU acceleration)

## Installation with pipx (Recommended)

1. Install pipx:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Install CLI tools:

   ```bash
   pipx install openai-whisper
   pipx install ollama
   ```

## Example End-to-End Flow

1. Start the container using `run_speech.sh` (container runs independently and waits for audio files).
2. On the host, record audio and save as `/tmp/input.wav` (e.g., using a Python script or `arecord`).

   ```bash
   arecord -f cd -t wav -d 5 -r 16000 /tmp/input.wav
   ```

3. The container detects `/input/audio.wav` (mounted from `/tmp/input.wav`), transcribes, refines, and copies the result to your clipboard.
4. Paste (Ctrl+V) anywhere to see the output.
5. Repeat: Each new `/tmp/input.wav` will be processed automatically.

---

### How It Works (Container Side)

- The container runs a loop in `process_audio.sh`:
  - Waits for `/input/audio.wav` to appear.
  - Runs `transcribe.py` to create `/tmp/transcript.txt`.
  - Runs `refine.py` to create `/tmp/refined.txt`.
  - Copies the result to clipboard using `xclip`.
  - Removes the processed audio file and waits for the next.
- Debug mode can be enabled by setting `DEBUG=1` or passing `--debug` to `process_audio.sh` for detailed logs.

---

## Typical Workflow: Hotkey Recording and Processing

1. **Press your assigned hotkey** to start recording audio (using your host-side script, e.g., `record_and_send.py`).
2. **Speak your message** into the microphone.
3. **Press the hotkey again** to stop recording and save the audio as `/tmp/input.wav`.
4. The container automatically detects `/tmp/input.wav`, transcribes and refines it, and copies the result to your clipboard.
5. **Paste (Ctrl+V)** anywhere to use the processed text.
6. Repeat the process for each new message.

### Hotkey Setup Example (KDE/GNOME)

- Map your host-side recording script (e.g., `record_and_send.py` or `record_and_send.sh`) to a global shortcut in your system settings.
- The script should:
  - Start recording on first press
  - Stop recording and save `/tmp/input.wav` on second press
  - Optionally, notify you when processing is complete

## Hotkey-Based Audio Recording (Python)

Use the provided `record_and_send.py` script to record audio with a hotkey (F9 by default):

1. **Install dependencies:**
   ```bash
   pipx install sounddevice soundfile keyboard numpy
   # or
   pip install sounddevice soundfile keyboard numpy
   ```

2. **Run the script:**
   ```bash
   python3 record_and_send.py
   ```
   - Press F9 to start recording.
   - Press F9 again to stop and send audio for processing.
   - The audio is saved as `/tmp/input.wav` and the container will process it automatically.

3. **Map to a hotkey:**
   - In KDE/GNOME, set a global shortcut to run:
     ```bash
     python3 /path/to/record_and_send.py
     ```
   - First press starts recording, second press stops and sends.

---

## Container Script Location

The main workflow script (`process_audio.sh`) is located at `/app/process_audio.sh` inside the container. For best practice, you can symlink or copy it to `/usr/local/sbin/` in your Dockerfile or container setup for easier access:

```dockerfile
RUN ln -s /app/process_audio.sh /usr/local/sbin/process_audio.sh
```

This allows you to run `process_audio.sh` from anywhere in the container shell.

---
