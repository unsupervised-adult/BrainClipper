FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    alsa-utils \
    xclip \
    curl \
    libportaudio2 \
    kbd \
    libasound2-plugins \
    libpulse0 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/* \
    && which arecord || (echo "ERROR: arecord not found" && exit 1) \
    && arecord --version \
    && echo "ALSA utils installed successfully"

# Install Python dependencies
RUN pip3 install --no-cache-dir openai-whisper torch torchaudio ollama sounddevice numpy soundfile keyboard
RUN curl -fsSL https://ollama.com/install.sh | sh

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY app/transcribe.py /app/transcribe.py
COPY app/refine.py /app/refine.py
COPY app/process_audio.sh /app/process_audio.sh
RUN chmod +x /app/process_audio.sh
ENTRYPOINT ["/app/entrypoint.sh"]

