#!/bin/bash
# Start the container for LLM/audio processing only (no recording)
podman run --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -e DISPLAY=$DISPLAY \
    --device /dev/snd:/dev/snd \
    --group-add $(getent group audio | cut -d: -f3) \
    --workdir /app \
    braindumper
