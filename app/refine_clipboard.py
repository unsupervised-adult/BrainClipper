from ollama import Client # type: ignore
import os
import time

# Read current clipboard content using CopyQ
clipboard_text = os.popen("copyq read clipboard").read().strip()
if not clipboard_text:
    print("Clipboard is empty. Please copy some text first.")
    exit(1)

client = Client()
prompt = f"Rephrase the following into a concise, professional message:\n{clipboard_text}"
response = client.generate(model="granite:3b", prompt=prompt)
polished_text = response["response"]

# Copy rephrased text back to clipboard using CopyQ
os.system(f"copyq copy '{polished_text}'")
time.sleep(0.1)
print("Rephrased text copied to clipboard.")
