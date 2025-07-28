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

2. Reload systemd and enable the service:

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
