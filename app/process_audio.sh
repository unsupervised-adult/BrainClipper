#!/bin/bash

# Enable debug mode if DEBUG=1 or --debug is passed
if [[ "$DEBUG" == "1" ]] || [[ "$1" == "--debug" ]]; then
    set -x
    DEBUG_MODE=1
    echo "[DEBUG] Debug mode enabled"
else
    DEBUG_MODE=0
fi

# Get mode from environment variable (default: transcribe)
MODE="${MODE:-transcribe}"

# Example usage: ./process_audio.sh [--debug] <audio_file>
AUDIO_FILE="/tmp/input.wav"

while true; do
    if [ -f "$AUDIO_FILE" ]; then
        if [[ $DEBUG_MODE -eq 1 ]]; then
            echo "[DEBUG] Using audio file: $AUDIO_FILE"
            echo "[DEBUG] Mode: $MODE"
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

        if [[ "$MODE" == "speak" ]]; then
            # Speech mode: Generate TTS reply and visualize it
            if [[ $DEBUG_MODE -eq 1 ]]; then
                echo "[DEBUG] Running speak.py for TTS generation"
            fi
            python3 /app/speak.py

            if [[ $DEBUG_MODE -eq 1 ]]; then
                echo "[DEBUG] Playing and visualizing LLM speech output"
            fi
            
            # Play the generated speech with visualization
            if [ -f "/tmp/llm_reply.wav" ]; then
                echo "Playing LLM response..."
                python3 /app/waveform.py --input /tmp/llm_reply.wav &
                WAVE_PID=$!
                aplay /tmp/llm_reply.wav
                kill $WAVE_PID 2>/dev/null
                wait $WAVE_PID 2>/dev/null
            fi
        else
            # Transcribe mode: Run refinement and copy to clipboard
            if [[ $DEBUG_MODE -eq 1 ]]; then
                echo "[DEBUG] Running refine.py"
            fi
            python3 /app/refine.py

            if [[ $DEBUG_MODE -eq 1 ]]; then
                echo "[DEBUG] Done. Output copied to clipboard."
            fi
        fi
        fi

        # Optionally, remove or archive the processed audio file
        rm -f "$AUDIO_FILE"
    else
        sleep 1
    fi

done