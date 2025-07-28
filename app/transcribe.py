import whisper # type: ignore
from ollama import Client # type: ignore

model = whisper.load_model("small.en", device="cuda")
result = model.transcribe("/tmp/input.wav")
with open("/tmp/transcript.txt", "w") as f:
    f.write(result["text"])

# Example prompt using the transcript
prompt = f"Summarize the following transcript:\n{result['text']}"
client = Client()
response = client.generate(model="granite3-moe:3b", prompt=prompt)
