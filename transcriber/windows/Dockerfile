# Windows Dockerfile for BrainClipper (best effort, for WSL2/Windows containers)
FROM python:3.11-slim

# Install dependencies
RUN pip install openai-whisper torch torchaudio ollama sounddevice numpy soundfile pyperclip

# Copy app scripts
COPY ../app/entrypoint.sh /app/entrypoint.sh
COPY ../app/transcribe.py /app/transcribe.py
COPY ../app/refine.py /app/refine.py
COPY ../app/process_audio.sh /app/process_audio.sh

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
