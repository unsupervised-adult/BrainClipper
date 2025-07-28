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

### Linux (Docker Only)

1. **Build the Docker image (with GPU support):**

   ```bash
   docker build -f linux/Dockerfile -t braindumper .
   ```

2. **Run the container with GPU and audio passthrough:**

   ```bash
   ./run_speech.sh
   ```

   - This script mounts your audio device (`/dev/snd`), X11 socket, and clipboard, and passes the recorded audio file to the container.
   - Ensure you have permissions for `/dev/snd` and X11 access (e.g., `xhost +local:`).
   - For manual Docker run:

     ```bash
     docker run --rm \
       --gpus all \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       -v /tmp:/tmp \
       -e DISPLAY=$DISPLAY \
       --device /dev/snd:/dev/snd \
       --group-add $(getent group audio | cut -d: -f3) \
       --workdir /app \
       braindumper
     ```

3. **Map to a hotkey:**
   - Go to your OS keyboard shortcuts settings (e.g., GNOME/KDE: System Settings → Keyboard → Shortcuts)
   - Add a custom shortcut to run your host-side Python script (`record_and_send.py`) for instant speech-to-clipboard

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
docker run --rm \
    --gpus all \
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
ExecStart=/usr/bin/docker run --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /tmp:/tmp \
  -e DISPLAY=$DISPLAY \
  --device /dev/snd:/dev/snd \
  --group-add $(getent group audio | cut -d: -f3) \
  --workdir /app \
  braindumper
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

- Ensure you have the NVIDIA Container Toolkit installed:

  ```bash
  sudo apt install nvidia-container-toolkit
  sudo systemctl restart docker
  ```

- Run containers with `--gpus all` (Docker).
- Verify GPU access inside the container:

  ```bash
  docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
  ```

- For X11 clipboard access, allow local connections:

  ```bash
  xhost +local:
  ```

## Requirements

- Docker with GPU support
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

## Python Environment Setup (Recommended)

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv ~/.venvs/brainclipper
   source ~/.venvs/brainclipper/bin/activate
   ```

2. Install required packages:

   ```bash
   pip install sounddevice soundfile numpy psutil
   ```

3. Run the recording script:

   ```bash
   python3 /home/ficus/Documents/Project-Code/whisper-braindumper/record_and_send.py
   ```

- Map this activation and script run to your hotkey for reliable execution.

## BrainClipper Workflow Overview

BrainClipper is a containerized speech-to-clipboard automation tool for Linux. It uses Whisper for transcription and an LLM (via Ollama) for text refinement. The workflow is:

1. **Record audio** on the host (using `record_and_send.py` or a mapped hotkey).
2. **Audio is saved** as `/tmp/input.wav`.
3. **Start the container** using the Docker run command above (handles GPU, clipboard, and audio device mounts).
4. **Container processes audio**:
    - `entrypoint.sh` starts the Ollama server, then runs `process_audio.sh`.
    - `process_audio.sh` transcribes audio with Whisper, refines with LLM, and copies the result to the clipboard using CopyQ.
5. **Paste the result** anywhere on your host.

## Key Files

- `app/entrypoint.sh`: Starts Ollama server, then runs the workflow.
- `app/process_audio.sh`: Handles audio file, runs transcription and refinement, manages clipboard.
- `app/transcribe.py`: Transcribes `/input/audio.wav` to `/tmp/transcript.txt`.
- `app/refine.py`: Refines transcript with LLM, copies result to clipboard.
- `app/refine_clipboard.py`: Rephrases clipboard text using LLM.
- `linux/Dockerfile`: Installs dependencies, sets up entrypoint.
- `linux/run_speech.sh`: Host script to run container with correct mounts/devices.

## Hotkey Integration

- Map `record_and_send.py` to a global shortcut in KDE/GNOME for instant recording.
- The script toggles recording: first press starts, second press stops and sends audio to the container.

## Clipboard Rephrase

- Run `python3 app/refine_clipboard.py` to rephrase clipboard text using the LLM.

## Example End-to-End Flow

1. User triggers hotkey or runs `record_and_send.py`.
2. Host records audio, saves as `/tmp/input.wav`.
3. Container starts, runs `entrypoint.sh` → `process_audio.sh`.
4. Audio is transcribed, refined, and copied to clipboard.

## Manual Ollama Model Pull (Container)

If you need to manually pull the Ollama model inside the container:

1. Start the container as usual:

   ```bash
   ./run_speech.sh
   # or
   docker run --rm --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp:/tmp -e DISPLAY=$DISPLAY --device /dev/snd:/dev/snd --group-add $(getent group audio | cut -d: -f3) --workdir /app braindumper
   ```

2. Enter the running container:

   ```bash
   docker ps
   docker exec -it <container_id_or_name> /bin/bash
   ```

3. Inside the container, pull the model:

   ```bash
   ollama pull granite3-moe:3b
   ollama list
   ollama serve &
   ```

This ensures the LLM model is available for processing. If the model is already present, the pull will be fast and will not re-download unless needed.

## Ollama Model Persistence & Symlinking

Ollama stores downloaded LLM models in a `.ollama` directory. To avoid re-downloading models every time you start a new container, you should persist this directory and ensure the container always uses the correct cache.

### 1. Find Your Ollama Model Directory

On most systems, Ollama stores models in your home directory:

```bash
ls ~/.ollama
```

Sometimes, models may also be found in `/usr/share/ollama/.ollama`. To check all locations:

```bash
find / -type d -name ".ollama" 2>/dev/null
```

### 2. Symlink System Directory to User Directory (if needed)

If you find models in `/usr/share/ollama/.ollama` and want to use your user cache (`/home/<user>/.ollama`), copy the contents and create a symlink:

```bash
sudo cp -r /usr/share/ollama/.ollama/* ~/.ollama/
sudo rm -rf /usr/share/ollama/.ollama
sudo ln -s ~/.ollama /usr/share/ollama/.ollama
sudo chown -R $USER:$USER ~/.ollama
```

This ensures all models are stored in your user directory and the system path points to it.

### 3. Persist Models in Docker

Mount your `.ollama` directory when running the container:

```bash
docker run --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /tmp:/tmp \
  -v ~/.ollama:/root/.ollama \
  -e DISPLAY=$DISPLAY \
  --device /dev/snd:/dev/snd \
  --group-add $(getent group audio | cut -d: -f3) \
  --workdir /app \
  braindumper
```

This ensures models are cached and available for all future runs.

---

## Clipboard Integration (X11 Forwarding)

For clipboard operations (using `xclip`), your container needs access to your host’s X11 server:

1. **Allow X11 connections from Docker:**

   ```bash
   xhost +local:docker
   ```

2. **Run the container with X11 socket mounted:**

   ```bash
   -v /tmp/.X11-unix:/tmp/.X11-unix \
   -e DISPLAY=$DISPLAY
   ```

3. **SSH Forwarding (if running remotely):**

   - Use `ssh -X` or `ssh -Y` to forward X11 when connecting to your host.

---

## Quick Reference: End-to-End Workflow

1. **Record audio** on host (`record_and_send.py` or hotkey).
2. **Audio saved** as `/tmp/input.wav`.
3. **Start container** with GPU, audio, X11, and Ollama model mounts.
4. **Container processes audio**:
    - `entrypoint.sh` starts Ollama server, runs `process_audio.sh`.
    - `process_audio.sh` transcribes, refines, and copies result to clipboard using `xclip`.
5. **Paste result** anywhere on host.

---

> **Tip:** Always mount your `.ollama` directory and X11 socket for best performance and clipboard reliability.
