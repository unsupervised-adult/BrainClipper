#!/bin/bash
# Entrypoint for BrainClipper container
# Starts Ollama server, then runs the audio/text workflow

ollama serve &
OLLAMA_PID=$!
# Wait for Ollama to start
sleep 5

# Start the main workflow loop
/app/process_audio.sh

wait $OLLAMA_PID
