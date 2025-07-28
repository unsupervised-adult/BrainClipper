from ollama import Client # type: ignore
import os
import time
import subprocess

with open("/tmp/transcript.txt", "r") as f:
    transcript = f.read()
client = Client()
prompt = f"Rephrase the following into a concise, professional message:\n{transcript}"
response = client.generate(model="granite3-moe:3b", prompt=prompt)
polished_text = response["response"]

# Copy polished text to clipboard using xclip
proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
proc.communicate(polished_text.encode())
# Brief delay to ensure clipboard syncs
time.sleep(0.1)
