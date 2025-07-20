# BrainClipper

**BrainClipper** converts spoken audio into concise, professional clipboard text using Whisper for transcription and Gemma LLM for refinement. Designed for fast, accurate speech-to-clipboard workflows in Linux environments.

## Features

- Records audio from your microphone
- Transcribes speech to text using Whisper
- Refines text with Gemma LLM (Ollama)
- Copies the final result to your clipboard using CopyQ

## Usage

1. Build the Docker image:

   ```bash
   docker build -t speech-to-clipboard .
   ```

2. Run the script:

   ```bash
   ./run_speech.sh
   ```

3. (Optional) Map to a hotkey:
   - Go to your OS keyboard shortcuts settings (e.g., GNOME/KDE: System Settings → Keyboard → Shortcuts)
   - Add a custom shortcut to run `./run_speech.sh` for instant speech-to-clipboard

4. Rephrase highlighted/clipboard text:
   - Copy any text you want to rephrase to your clipboard
   - Run the following command:

     ```bash
     python3 refine_clipboard.py
     ```

   - The rephrased text will be copied back to your clipboard
   - (Optional) Map this command to a hotkey for instant rephrasing

## Requirements

- Docker with GPU support
- Audio input device
- X11 clipboard (CopyQ)
