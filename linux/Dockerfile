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
    ffmpeg \
    libxtst6 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/* \
    && which arecord || (echo "ERROR: arecord not found" && exit 1) \
    && arecord --version \
    && echo "ALSA utils installed successfully"

# Install Python dependencies (increase timeout for large packages)
RUN pip3 install --default-timeout=300 --no-cache-dir openai-whisper torch torchaudio ollama sounddevice numpy soundfile keyboard
# Preload Whisper 'small' model to cache weights in the image
RUN python3 -c "import whisper; whisper.load_model('small')"
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ln -s /usr/local/bin/ollama /usr/bin/ollama

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY app/transcribe.py /app/transcribe.py
COPY app/refine.py /app/refine.py
COPY app/process_audio.sh /app/process_audio.sh
RUN chmod +x /app/process_audio.sh
RUN ln -s /app/process_audio.sh /usr/local/sbin/process_audio.sh \
    && ln -s /app/transcribe.py /usr/local/sbin/transcribe.py \
    && ln -s /app/refine.py /usr/local/sbin/refine.py \
    && ln -s /app/entrypoint.sh /usr/local/sbin/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

