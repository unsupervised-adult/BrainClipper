FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    alsa-utils \
    xclip \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && which arecord || (echo "ERROR: arecord not found" && exit 1) \
    && arecord --version \
    && echo "ALSA utils installed successfully"

# Install Python dependencies
RUN pip3 install --no-cache-dir openai-whisper torch torchaudio

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server and pull Gemma 2B model
RUN ollama serve & \
    sleep 5 && \
    ollama pull gemma:2b

# Set working directory
WORKDIR /app

# Copy Python scripts
COPY transcribe.py /app/transcribe.py
COPY refine.py /app/refine.py
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose X11 for clipboard
ENV DISPLAY=:0

# Entry point
ENTRYPOINT ["/app/entrypoint.sh"]
