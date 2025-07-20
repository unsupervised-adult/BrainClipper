FROM python:3.11-slim

# Install Python dependencies
RUN pip install --no-cache-dir openai-whisper torch torchaudio ollama

WORKDIR /app

COPY transcribe.py /app/transcribe.py
COPY refine.py /app/refine.py

CMD ["powershell", "-Command", "python transcribe.py; python refine.py"]
