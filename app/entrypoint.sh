#!/bin/bash

# Start Ollama server in the background
ollama serve &

# Wait for Ollama to warm up
sleep 5

echo "Ollama server started. Running audio workflow..."

# Run your audio processing workflow
/app/process_audio.sh "$@"
