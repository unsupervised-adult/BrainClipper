#!/bin/bash
source ~/.venvs/brainclipper/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while true; do
    echo "Recording... "
    echo "Press [ENTER] or [SPACE] to stop & save, [r] to redo, [x/q] to quit without saving."

    python3 "$SCRIPT_DIR/app/waveform.py" &
    PY_PID=$!

    IFS= read -rsn1 INPUT

    kill $PY_PID 2>/dev/null
    wait $PY_PID 2>/dev/null  # Ensure process is fully terminated
    echo

    if [[ "$INPUT" == "x" || "$INPUT" == "q" ]]; then
        echo "Exiting without saving."
        break
    elif [[ "$INPUT" == "r" ]]; then
        echo "Redoing recording..."
        continue
    elif [[ "$INPUT" == "" || "$INPUT" == " " ]]; then
        echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
        break
    else
        echo "Recording stopped. Audio saved to /tmp/input.wav for processing."
        break
    fi
done