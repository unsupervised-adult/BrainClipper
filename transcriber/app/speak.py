import os
import time
import subprocess
import tempfile
from ollama import Client # type: ignore

# Get the transcript and generate LLM reply
with open("/tmp/transcript.txt", "r") as f:
    transcript = f.read()

model = os.environ.get("MODEL_NAME", "granite3-moe:3b")

# Generate a conversational reply instead of reformatting
prompt = f"You are having a conversation. Respond naturally and helpfully to: {transcript}"

client = Client()
response = client.generate(model=model, prompt=prompt)
reply_text = response["response"]

# Log the full LLM response
with open("/tmp/llm_response.log", "a") as logf:
    logf.write(str(response) + "\n")

# Clean up the reply text
reply_text = reply_text.strip()

# Generate speech using espeak and save to temp file
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
    temp_audio_path = temp_audio.name

# Use espeak to generate speech
subprocess.run([
    "espeak", 
    "-w", temp_audio_path,
    "-s", "150",  # Speed
    "-p", "50",   # Pitch
    reply_text
], check=True)

# Copy the generated audio to standard location for waveform visualization
subprocess.run(["cp", temp_audio_path, "/tmp/llm_reply.wav"], check=True)

print(f"Speech generated: {reply_text}")

# Clean up temp file
os.unlink(temp_audio_path)
