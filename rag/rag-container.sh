#!/bin/bash
# Run RAG analysis container for log files
# Usage: ./rag-container.sh [model_name]
MODEL_NAME="${1:-granite3-moe:3b}"

# Stop and remove any running rag container
RUNNING_ID=$(docker ps -q --filter ancestor=braindumper)
if [ -n "$RUNNING_ID" ]; then
    echo "Stopping running braindumper container: $RUNNING_ID"
    docker stop $RUNNING_ID
fi

echo "Starting RAG analysis with model $MODEL_NAME"

docker run --rm \
    --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -v ~/.ollama:/root/.ollama \
    -v $(pwd)/log:/log \
    -e DISPLAY=$DISPLAY \
    -e MODEL_NAME="$MODEL_NAME" \
    --workdir /app \
    braindumper python3 /app/rag.py
