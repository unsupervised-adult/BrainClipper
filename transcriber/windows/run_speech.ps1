# Windows PowerShell script to run BrainClipper container with audio, clipboard, and model cache integration
# Requires Docker Desktop with WSL2 backend and Windows audio/clipboard support

param(
    [string]$ModelName = "granite3-moe:3b"
)

# Set up paths (adjust as needed)
$HostAudio = "$env:TEMP\input.wav"
$HostTranscript = "$env:TEMP\transcript.txt"
$HostOllama = "$env:USERPROFILE\.ollama"

# Ensure Ollama model cache exists
if (!(Test-Path $HostOllama)) {
    New-Item -ItemType Directory -Path $HostOllama | Out-Null
}

# Run the container
# Note: --device and X11 clipboard are not available on Windows; use pyperclip for clipboard

docker run --rm `
    -v "$HostAudio:/tmp/input.wav" `
    -v "$HostTranscript:/tmp/transcript.txt" `
    -v "$HostOllama:/root/.ollama" `
    -e MODEL_NAME=$ModelName `
    --workdir /app `
    braindumper-windows
