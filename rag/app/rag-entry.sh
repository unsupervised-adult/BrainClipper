#!/bin/bash
set -e

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "[ERROR] NVIDIA GPU not detected. GPU features will not be available."
else
    echo "[INFO] NVIDIA GPU detected:"
    nvidia-smi
fi

echo "[RAG] Starting Ollama server in container..."
ollama serve &
sleep 5

echo "[RAG] Converting MTA files..."
python3 convert_mta.py

echo "[RAG] Converting EVTX files..."
python3 convert_evtx.py

echo "EVTX conversion complete."
echo "[RAG] MTA conversion complete."

echo "[RAG] Running RAG analysis (this may take a while)..."
python3 rag.py
python3 -i rag_cli.py
