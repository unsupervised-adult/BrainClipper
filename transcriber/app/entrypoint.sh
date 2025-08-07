#!/bin/bash
# Entrypoint for BrainClipper container
# Pulls the correct model, starts Ollama server, then runs the audio/text workflow

MODEL_NAME="${MODEL_NAME:-granite3-moe:3b}"

ollama pull "$MODEL_NAME"
ollama serve &
OLLAMA_PID=$!
sleep 5

# Start the main workflow loop
export MODEL_NAME
/app/process_audio.sh

wait $OLLAMA_PID
