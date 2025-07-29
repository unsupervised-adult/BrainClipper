# BrainClipper: Speech-to-Clipboard Workflow

BrainClipper is a containerized, GPU-accelerated speech-to-clipboard workflow for Linux and Windows. It uses Whisper for transcription and an LLM (Gemma, Granite, or other Ollama models) for text refinement, with seamless clipboard integration via xclip.

## Features

- **End-to-end speech-to-clipboard automation**: Record audio, transcribe with Whisper, refine with LLM, and copy to clipboard in one step.
- **Containerized for reproducibility**: All processing runs inside a Docker container.
- **GPU acceleration**: Uses CUDA for fast inference.
- **Hot-swappable LLM models**: Change the LLM model on the fly without rebuilding or restarting the container.
- **Persistent Ollama model cache**: Models are cached and can be symlinked for efficiency.
- **Clipboard integration**: Uses xclip for X11 clipboard access (Linux).

## Architecture & Data Flow

1. **Host records audio** (e.g., via `arecord` or a hotkey script), saves as `/tmp/input.wav`.
2. **Container starts** via `run_speech.sh`, with audio and model cache mounted.
3. **Entrypoint** (`entrypoint.sh`) pulls and serves the LLM model specified by `MODEL_NAME`.
4. **Workflow** (`process_audio.sh`):
    - Transcribes audio with Whisper (`transcribe.py`)
    - Refines text with LLM (`refine.py`)
    - Copies result to clipboard with xclip

## Quickstart (Linux)

### Build the Container

```shellscript
cd linux/
docker build -t braindumper .
```

### Run the Workflow

```shellscript
./run_speech.sh <model_name>
# Example:
./run_speech.sh gemma:2b
```

- `<model_name>` is any Ollama-supported model (e.g., `gemma:2b`, `granite:3b`)
- The script sets the `MODEL_NAME` environment variable for the container
- No rebuild/restart needed to change models

### Clipboard Rephrase

```shellscript
python3 app/refine_clipboard.py
```

- Rephrases current clipboard text using the selected LLM

## Host Requirements

- Docker
- NVIDIA GPU and drivers (for GPU acceleration)
- NVIDIA Container Toolkit (for Docker GPU passthrough)
- X11 (for clipboard access)
- Audio device (`/dev/snd`)
- xclip (for clipboard integration)

## NVIDIA GPU Setup & Troubleshooting

To enable GPU acceleration in Docker containers, you must install the NVIDIA Container Toolkit and ensure your drivers are up to date.

### 1. Install NVIDIA Drivers and Toolkit

```shellscript
sudo apt install nvidia-driver-535
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Test GPU Access in Docker

```shellscript
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

You should see your GPU listed. If not, check driver installation and Docker configuration.

### 3. Common Issues & Notes

- If you see `nvidia-container-cli: initialization error`, try rebooting or reinstalling the toolkit.
- Make sure your user is in the `docker` group: `sudo usermod -aG docker $USER`
- If you get X11 errors, run `xhost +local:docker` on the host before starting the container.
- For audio device issues, check permissions on `/dev/snd` and add your user to the `audio` group.
- If you use a custom kernel, ensure the NVIDIA kernel modules are loaded.

## Container Details

- **Base image**: `nvidia/cuda:12.2.0-devel-ubuntu22.04`
- **Dependencies**: Python 3, Whisper, Ollama, xclip, ffmpeg, ALSA utils, etc.
- **Entrypoint**: `/app/entrypoint.sh` (starts Ollama server, runs workflow)
- **Model cache**: Mount your host `.ollama` directory to `/root/.ollama` in the container for persistent models

## Model Cache & Symlinking

- Ollama model cache is persisted by mounting the host `.ollama` directory
- You can symlink system and user model directories for shared access
- Example:

```shellscript
  ln -s /var/lib/ollama/models /root/.ollama/models
```

## Hotkey Setup

- Map `run_speech.sh` or a host-side Python script to a global shortcut for instant recording/processing

## File Overview

- `app/entrypoint.sh`: Starts Ollama server, runs workflow
- `app/process_audio.sh`: Handles audio, runs transcription/refinement, manages clipboard
- `app/transcribe.py`: Transcribes `/input/audio.wav` to `/tmp/transcript.txt`
- `app/refine.py`: Refines transcript with LLM, copies to clipboard
- `app/refine_clipboard.py`: Rephrases clipboard text with LLM
- `linux/Dockerfile`: Installs dependencies, sets up entrypoint
- `linux/run_speech.sh`: Host script to run container with correct mounts/devices

## Troubleshooting

- **Clipboard not working?** Ensure X11 is available and xclip is installed on host and in container.
- **Model not found?** Make sure the model name is correct and your `.ollama` directory is mounted.
- **Audio device errors?** Check `/dev/snd` permissions and container device mapping.
- **Performance issues?** Ensure GPU drivers are installed and Docker is configured for GPU access.

## GPU Passthrough Instructions

- Ensure you have the NVIDIA Container Toolkit installed:

```shellscript
  sudo apt install nvidia-container-toolkit
  sudo systemctl restart docker
```

- Run containers with `--gpus all` (Docker).
- Verify GPU access inside the container:

```shellscript
  docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

- For X11 clipboard access, allow local connections:

```shellscript
  xhost +local:
```

## Requirements

- Docker with GPU support
- Audio input device (`/dev/snd` on Linux)
- X11 clipboard (xclip)
- Python 3.8+
- NVIDIA GPU and drivers (for GPU acceleration)

> **Note:** Clipboard integration uses xclip (not CopyQ). Make sure xclip is installed on both host and in the container, and X11 is available.

## Installation with pipx (Recommended)

1. Install pipx:

```shellscript
   sudo apt install pipx
   pipx ensurepath
```

2. Install CLI tools:

```shellscript
   pipx install openai-whisper
   pipx install ollama
```

## Python Environment Setup (Recommended)

1. Create and activate a virtual environment:

```shellscript
   python3 -m venv ~/.venvs/brainclipper
   source ~/.venvs/brainclipper/bin/activate
```

2. Install required packages:

```shellscript
   pip install sounddevice soundfile numpy psutil
```

3. Run the recording script:

```shellscript
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
    - `process_audio.sh` transcribes audio with Whisper, refines with LLM, and copies the result to the clipboard using xclip.
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

## Clipboard Rephrase (LLM)

- Run `python3 app/refine_clipboard.py` to rephrase clipboard text using the LLM.