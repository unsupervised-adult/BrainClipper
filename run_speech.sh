#!/bin/bash
# Run speech workflow with mode support
# Usage: ./run_speech.sh [model_name] [mode]
# model_name: LLM model (default: granite3-moe:3b)
# mode: transcribe|speak (default: transcribe)

MODEL_NAME="${1:-granite3-moe:3b}"
MODE="${2:-transcribe}"

# Stop and remove any running braindumper container
RUNNING_ID=$(docker ps -q --filter ancestor=braindumper)
if [ -n "$RUNNING_ID" ]; then
    echo "Stopping running braindumper container: $RUNNING_ID"
    docker stop $RUNNING_ID
fi

echo "Starting BrainClipper in $MODE mode with model $MODEL_NAME"

docker run --rm \
    --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -v ~/.ollama:/root/.ollama \
    -e DISPLAY=$DISPLAY \
    -e MODEL_NAME="$MODEL_NAME" \
    -e MODE="$MODE" \
    --device /dev/snd:/dev/snd \
    --group-add $(getent group audio | cut -d: -f3) \
    --workdir /app \
    braindumper
