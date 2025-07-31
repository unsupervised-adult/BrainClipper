#!/bin/bash
source ~/.venvs/brainclipper/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while true; do
    echo "Press [ENTER] or [SPACE] to start recording, [q/x] to quit."
    while true; do
        IFS= read -rsn1 INPUT
        # Only respond to ENTER, SPACE, q, or x
        if [[ "$INPUT" == "x" || "$INPUT" == "q" ]]; then
            echo "Exiting."
            exit 0
        elif [[ "$INPUT" == "" || "$INPUT" == " " ]]; then
            break
        fi
        # Ignore all other keys (including clipboard paste)
    done

    # Start recording with visualizer and show red @REC
    echo -e "\033[1;31m@REC\033[0m Recording... Press [ENTER] or [SPACE] to stop & save, [r] to redo, [q/x] to quit."
    python3 "$SCRIPT_DIR/app/waveform.py" &
    PY_PID=$!

    while true; do
        IFS= read -rsn1 STOP_INPUT
        # Only respond to ENTER, SPACE, r, q, or x
        if [[ "$STOP_INPUT" == "x" || "$STOP_INPUT" == "q" ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            echo "Exiting."
            exit 0
        elif [[ "$STOP_INPUT" == "r" ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            echo -e "\033[1;31m@REC\033[0m Redoing recording..."
            echo -e "\033[1;31m@REC\033[0m Recording... Press [ENTER] or [SPACE] to stop & save, [r] to redo, [q/x] to quit."
            python3 "$SCRIPT_DIR/app/waveform.py" &
            PY_PID=$!
            continue
        elif [[ "$STOP_INPUT" == "" || "$STOP_INPUT" == " " ]]; then
            kill $PY_PID 2>/dev/null
            wait $PY_PID 2>/dev/null
            echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
            break
        fi
        # Ignore all other keys (including clipboard paste)
    done
done