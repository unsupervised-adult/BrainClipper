# BrainClipper

**BrainClipper** converts spoken audio into concise, professional clipboard text using Whisper for transcription and Gemma LLM for refinement. Designed for fast, accurate speech-to-clipboard workflows in Linux environments.

## Features

- Records audio from your microphone
- Transcribes speech to text using Whisper
- Refines text with Gemma LLM (Ollama)
- Copies the final result to your clipboard

## Usage

1. Build the Docker image:

   ```bash
   docker build -t speech-to-clipboard .
   ```

2. Run the script:

   ```bash
   ./run_speech.sh
   ```

## Requirements

- Docker with GPU support
- Audio input device
- X11 clipboard (xclip, CopyQ)
