#!/bin/bash
# Start the container for LLM/audio processing only (no recording)
# For SSH clipboard integration, use: ssh -X or ssh -Y
# Example: ssh -X user@host

# Stop and remove any running braindumper container
RUNNING_ID=$(docker ps -q --filter ancestor=braindumper)
if [ -n "$RUNNING_ID" ]; then
    echo "Stopping running braindumper container: $RUNNING_ID"
    docker stop $RUNNING_ID
fi

docker run --rm \
    --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -v ~/.ollama:/root/.ollama \
    -e DISPLAY=$DISPLAY \
    --device /dev/snd:/dev/snd \
    --group-add $(getent group audio | cut -d: -f3) \
    --workdir /app \
    braindumper
# xclip is used for clipboard integration in process_audio.sh and Python scripts
