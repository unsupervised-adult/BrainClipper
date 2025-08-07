import os
import glob
from ollama import Client # type: ignore

LOG_DIR = "/log"
MAX_BYTES = 1000000  # 1MB limit for all files combined

# Find all .txt, .log, .evtx files in /log
files = glob.glob(os.path.join(LOG_DIR, "*.txt")) + \
        glob.glob(os.path.join(LOG_DIR, "*.log")) + \
        glob.glob(os.path.join(LOG_DIR, "*.evtx"))

contents = []
total_bytes = 0
for file in files:
    try:
        with open(file, "r", errors="ignore") as f:
            data = f.read(MAX_BYTES - total_bytes)
            total_bytes += len(data)
            contents.append(f"--- {os.path.basename(file)} ---\n{data}\n")
            if total_bytes >= MAX_BYTES:
                break
    except Exception as e:
        contents.append(f"--- {os.path.basename(file)} ---\n[Error reading file: {e}]\n")

all_logs = "\n".join(contents)

prompt = f"Analyze the following logs and files to find root causes for any issues. Summarize findings and suggest next steps.\n\n{all_logs}"

model = os.environ.get("MODEL_NAME", "granite3-moe:3b")
client = Client()
response = client.generate(model=model, prompt=prompt)
result = response["response"].strip()

# Output to clipboard and file
with open("/tmp/rag_result.txt", "w") as f:
    f.write(result)

try:
    import subprocess
    proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
    proc.communicate(result.encode())
except Exception:
    pass

print("RAG analysis complete. Results saved to /tmp/rag_result.txt and copied to clipboard.")
