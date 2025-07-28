#!/bin/bash
# Entrypoint for BrainClipper container
# Pulls the correct model, starts Ollama server, then runs the audio/text workflow

ollama pull granite3-moe:3b
ollama serve &
OLLAMA_PID=$!
sleep 5

# Start the main workflow loop
/app/process_audio.sh

wait $OLLAMA_PID
