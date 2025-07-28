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

## BrainClipper Workflow Overview

BrainClipper is a containerized speech-to-clipboard automation tool for Linux. It uses Whisper for transcription and an LLM (via Ollama) for text refinement. The workflow is:

1. **Record audio** on the host (using `record_and_send.py` or a mapped hotkey).
2. **Audio is saved** as `/tmp/input.wav`.
3. **Start the container** using `./run_speech.sh` (handles GPU, clipboard, and audio device mounts).
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

---


## Project Overview

- **BrainClipper** is a containerized speech-to-clipboard workflow for Linux and Windows, using Whisper for transcription and an LLM (Gemma or Granite via Ollama) for text refinement.
- The main workflow: record audio → transcribe with Whisper → refine with LLM → copy result to clipboard (CopyQ).
- Designed for fast, accurate, and professional speech-to-clipboard automation.

## Architecture & Data Flow

- **Linux:**
  - Container built with Podman (or Docker), GPU-enabled (`nvidia/cuda` base image).
  - Entry point: `app/entrypoint.sh` starts Ollama server, then runs `process_audio.sh`.
  - Audio is recorded on host (e.g., via `record_and_send.py` or hotkey script), then passed to container as `/input/audio.wav`.
  - `process_audio.sh` runs `transcribe.py` (Whisper) and `refine.py` (LLM), then copies output to clipboard.

## Key Files & Patterns

- `app/entrypoint.sh`: Starts Ollama server, then runs workflow script.
- `app/process_audio.sh`: Handles audio file, runs transcription and refinement, manages clipboard.
- `app/transcribe.py`: Uses Whisper to transcribe `/input/audio.wav` to `/tmp/transcript.txt`.
- `app/refine.py`: Uses Ollama LLM to rephrase transcript, copies result to clipboard.
- `app/refine_clipboard.py`: Rephrases clipboard text using LLM.
- `linux/Dockerfile`: Installs all dependencies, sets up entrypoint.
- `linux/run_speech.sh`: Host script to run container with correct mounts/devices.

## Developer Workflows

- **Build:**
  - Linux: `podman build -t braindumper .` (from `linux/`)
  - Windows: `docker build -t braindumper .` (from `windows/`)
- **Run:**
  - Linux: `./run_speech.sh` (handles audio, clipboard, GPU, X11)
  - Windows: `./run_speech.ps1`
- **Hotkey Integration:**
  - Map `run_speech.sh` or host-side Python script to a global shortcut for instant recording/processing.
- **Clipboard Rephrase:**
  - Run `python3 app/refine_clipboard.py` to rephrase clipboard text.

## Conventions & Patterns

- All audio processing and LLM inference run inside the container for reproducibility and isolation.