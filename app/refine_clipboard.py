from ollama import Client # type: ignore
import os
import time
import subprocess

# Read current clipboard content using xclip
clipboard_text = subprocess.check_output('xclip -selection clipboard -o', shell=True).decode().strip()
if not clipboard_text:
    print("Clipboard is empty. Please copy some text first.")
    exit(1)

client = Client()
prompt = f"Rephrase the following into a concise, professional message:\n{clipboard_text}"
response = client.generate(model="granite:3b", prompt=prompt)
polished_text = response["response"]

# Copy polished text to clipboard using xclip
proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
proc.communicate(polished_text.encode())
time.sleep(0.1)
print("Rephrased text copied to clipboard.")
