#!/bin/bash
# Build and run RAG container with interactive CLI and GPU passthrough

# Build the image
DOCKERFILE_PATH="Dockerfile.rag" # Update this if your Dockerfile is in another directory
echo "Building RAG container..."
docker build -f "$DOCKERFILE_PATH" -t braindumper-rag .

# Run the container interactively with GPU, X11, clipboard, and Ollama model cache
# Use host networking and set OLLAMA_HOST to host's Ollama server

# Mount the logs folder as /log in the container
echo "Running RAG container..."
docker run -it --rm \
    --gpus all \
    --network host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -v ~/.ollama:/root/.ollama \
    -v $(pwd)/logs:/log \
    -e DISPLAY=$DISPLAY \
    -e MODEL_NAME="${MODEL_NAME:-granite3-moe:3b}" \
    -e OLLAMA_HOST="localhost:11434" \
    --workdir /app \
    braindumper-rag
