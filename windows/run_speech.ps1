# Windows PowerShell script to run BrainClipper container
# Assumes Docker Desktop or Podman Desktop is installed

# Set up volume mounts (adjust paths as needed)
$inputDir = "$env:TEMP"
$containerName = "braindumper"

# Run the container (no GPU/audio/X11 integration)
docker run -v $inputDir:/tmp --workdir /app $containerName

# Optional: Show notification (requires BurntToast module)
# Import-Module BurntToast
# New-BurntToastNotification -Text "Text copied to clipboard"
