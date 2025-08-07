# Windows PowerShell Entrypoint for BrainClipper
param(
    [string]$ModelName = "granite3-moe:3b"
)

# Pull the model (if Ollama CLI is available)
ollama pull $ModelName

# Start Ollama server in background
Start-Process -NoNewWindow -FilePath "ollama" -ArgumentList "serve"
Start-Sleep -Seconds 5

# Run the workflow (transcribe and refine)
python transcribe.py
python refine.py
