from ollama import Client # type: ignore
import os
import time

with open("/tmp/transcript.txt", "r") as f:
    transcript = f.read()
client = Client()
prompt = f"Rephrase the following into a concise, professional message:\n{transcript}"
response = client.generate(model="gemma:2b", prompt=prompt)
polished_text = response["response"]

# Copy to clipboard with CopyQ
os.system(f"copyq copy '{polished_text}'")
# Brief delay to ensure CopyQ syncs
time.sleep(0.1)
# Optional: Verify clipboard content (for debugging)
# os.system(f"copyq read clipboard > /tmp/clipboard_verify.txt")
