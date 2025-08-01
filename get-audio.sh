#!/bin/bash
source ~/.venvs/brainclipper/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for mode argument
MODE="${1:-transcribe}"
if [[ "$MODE" != "transcribe" && "$MODE" != "speak" ]]; then
    echo "Usage: $0 [transcribe|speak]"
    echo "  transcribe: Speech-to-text with clipboard output (default)"
    echo "  speak: Speech-to-speech conversation mode"
    exit 1
fi

clear  # Clear console at script start

echo "Mode: $MODE"
if [[ "$MODE" == "speak" ]]; then
    echo "Speech conversation mode - LLM will reply with audio"
else
    echo "Transcription mode - output will be copied to clipboard"
fi

while true; do
    echo "Press [ENTER] or [SPACE] to start recording, [q/x] to quit."
    # Wait for valid key to start recording
    while true; do
        IFS= read -rsn1 INPUT
        if [[ "$INPUT" == "x" || "$INPUT" == "q" ]]; then
            echo "Exiting."
            exit 0
        elif [[ "$INPUT" == "" || "$INPUT" == " " ]]; then
            break
        fi
        # Ignore all other keys
    done

    clear  # Clear console before each recording

    # Start recording with visualizer and show red "Recording..."
    echo -e "\033[1;31mRecording...\033[0m Press [ENTER] or [SPACE] to stop & save, [r] to redo, [q/x] to quit."
    python3 "$SCRIPT_DIR/app/waveform.py" &
    PY_PID=$!

    # Wait for valid key to stop/redo/quit recording
    while true; do
        IFS= read -rsn1 STOP_INPUT
        if [[ "$STOP_INPUT" == "x" || "$STOP_INPUT" == "q" ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            echo "Exiting."
            exit 0
        elif [[ "$STOP_INPUT" == "r" ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            clear
            echo -e "\033[1;31mRedoing recording...\033[0m"
            echo -e "\033[1;31mRecording...\033[0m Press [ENTER] or [SPACE] to stop & save, [r] to redo, [q/x] to quit."
            python3 "$SCRIPT_DIR/app/waveform.py" &
            PY_PID=$!
            continue
        elif [[ "$STOP_INPUT" == "" || "$STOP_INPUT" == " " ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            if [[ "$MODE" == "speak" ]]; then
                echo "Recording stopped. Processing for speech conversation..."
            else
                echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
            fi
            
            # Set MODE environment variable for container
            export MODE
            sleep 1
            clear
            break
        fi
        # Ignore all other keys
    done
done