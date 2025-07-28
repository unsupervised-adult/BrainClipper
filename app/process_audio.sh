#!/bin/bash

# Enable debug mode if DEBUG=1 or --debug is passed
if [[ "$DEBUG" == "1" ]] || [[ "$1" == "--debug" ]]; then
    set -x
    DEBUG_MODE=1
    echo "[DEBUG] Debug mode enabled"
else
    DEBUG_MODE=0
fi

# Example usage: ./process_audio.sh [--debug] <audio_file>
AUDIO_FILE="/tmp/input.wav"

while true; do
    if [ -f "$AUDIO_FILE" ]; then
        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Using audio file: $AUDIO_FILE"
        fi

        # Run transcription
        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Running transcribe.py"
        fi
        python3 /app/transcribe.py "$AUDIO_FILE" > /tmp/transcript.txt

        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Transcript saved to /tmp/transcript.txt"
            cat /tmp/transcript.txt
        fi

        # Run refinement
        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Running refine.py"
        fi
        python3 /app/refine.py /tmp/transcript.txt > /tmp/refined.txt

        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Refined output saved to /tmp/refined.txt"
            cat /tmp/refined.txt
        fi

        # Copy to clipboard
        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Copying to clipboard"
        fi
        cat /tmp/refined.txt | xclip -selection clipboard

        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Done. Output copied to clipboard."
        fi

        # Optionally, remove or archive the processed audio file
        rm -f "$AUDIO_FILE"
    else
        sleep 1
    fi

done