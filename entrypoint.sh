#!/bin/bash
# Ensure cleanup on exit
trap 'rm -f /tmp/input.wav /tmp/transcript.txt; echo "Cleaned up temporary files"' EXIT

# Check disk space in /tmp (warn if < 100MB free)
if [ $(df -m /tmp | tail -1 | awk '{print $4}') -lt 100 ]; then
    echo "Warning: Low disk space in /tmp (< 100MB)"
    exit 1
fi

# Log ALSA devices for debugging
arecord -l > /tmp/alsa_devices.log 2>&1

# Try recording with multiple devices
for device in hw:0,0 hw:1,0 hw:2,0 hw:3,0; do
    echo "Trying device $device"
    timeout 6 arecord -D $device -c 2 -r 16000 -f S16_LE -d 5 /tmp/input.wav 2> /tmp/arecord_error.log
    if [ $? -eq 0 ] && [ -f /tmp/input.wav ] && [ -s /tmp/input.wav ]; then
        echo "Recording successful with device $device"
        break
    fi
    echo "Recording failed with device $device"
    cat /tmp/arecord_error.log
done

# Check if audio was recorded
if [ ! -f /tmp/input.wav ] || [ ! -s /tmp/input.wav ]; then
    echo "Error: Audio recording failed for all devices or empty file"
    cat /tmp/arecord_error.log
    cat /tmp/alsa_devices.log
    exit 1
fi

# Run transcription and refinement
python3 /app/transcribe.py 2> /tmp/transcribe_error.log
if [ $? -ne 0 ]; then
    echo "Error: Transcription failed"
    cat /tmp/transcribe_error.log
    exit 1
fi

# Check if transcript exists and is non-empty
if [ ! -f /tmp/transcript.txt ] || [ ! -s /tmp/transcript.txt ]; then
    echo "Error: Transcript file missing or empty"
    exit 1
fi

python3 /app/refine.py 2> /tmp/refine_error.log
if [ $? -ne 0 ]; then
    echo "Error: Refinement failed"
    cat /tmp/refine_error.log
    exit 1
fi

# Notify success
echo "Text copied to clipboard"
