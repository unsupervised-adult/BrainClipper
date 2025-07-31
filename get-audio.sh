#!/bin/bash
source ~/.venvs/brainclipper/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while true; do
    echo "Press [ENTER] or [SPACE] to start recording, [q/x] to quit."
    IFS= read -rsn1 INPUT

    if [[ "$INPUT" == "x" || "$INPUT" == "q" ]]; then
        echo "Exiting."
        break
    fi

    # Start the visualizer in idle mode (no audio input yet)
    python3 "$SCRIPT_DIR/app/waveform.py" --idle &
    VIS_PID=$!

    # Wait for trigger to start recording
    while true; do
        IFS= read -rsn1 START_INPUT
        if [[ "$START_INPUT" == "x" || "$START_INPUT" == "q" ]]; then
            kill $VIS_PID 2>/dev/null
            wait $VIS_PID 2>/dev/null
            echo "Exiting."
            exit 0
        elif [[ "$START_INPUT" == "" || "$START_INPUT" == " " ]]; then
            kill $VIS_PID 2>/dev/null
            wait $VIS_PID 2>/dev/null
            break
        fi
    done

    # Start recording with visualizer
    echo "Recording... Press [ENTER] or [SPACE] to stop & save, [r] to redo, [q/x] to quit."
    python3 "$SCRIPT_DIR/app/waveform.py" &
    PY_PID=$!

    IFS= read -rsn1 STOP_INPUT

    if [[ "$STOP_INPUT" == "x" || "$STOP_INPUT" == "q" ]]; then
        kill $PY_PID 2>/dev/null
        wait $PY_PID 2>/dev/null
        echo "Exiting."
        exit 0
    elif [[ "$STOP_INPUT" == "r" ]]; then
        kill $PY_PID 2>/dev/null
        wait $PY_PID 2>/dev/null
        echo "Redoing recording..."
        continue
    elif [[ "$STOP_INPUT" == "" || "$STOP_INPUT" == " " ]]; then
        kill $PY_PID 2>/dev/null
        wait $PY_PID 2>/dev/null
        echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
        # Loop back to idle visualizer
        continue
    else
        kill $PY_PID 2>/dev/null
        wait $PY_PID 2>/dev/null
        echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
        continue
    fi
done