#!/bin/bash
# Ensure user is in audio group
[ "$(id -gn)" != "audio" ] && sudo usermod -aG audio $USER
podman run --gpus all \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp:/tmp \
    -e DISPLAY=$DISPLAY \
    --device /dev/snd:/dev/snd \
    --group-add $(getent group audio | cut -d: -f3) \
    --workdir /app \
    braindumper
notify-send "Text copied to clipboard"
