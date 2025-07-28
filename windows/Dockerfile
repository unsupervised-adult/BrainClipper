FROM python:3.11-slim

# Install Python dependencies
RUN pip install --no-cache-dir openai-whisper torch torchaudio ollama sounddevice numpy soundfile keyboard

WORKDIR /app

COPY transcribe.py /app/transcribe.py
COPY refine.py /app/refine.py
COPY record_hotkey.py /app/record_hotkey.py
COPY entrypoint.sh /app/entrypoint.sh

CMD ["bash", "/app/entrypoint.sh"]
