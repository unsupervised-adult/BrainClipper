import whisper
model = whisper.load_model("small.en", device="cuda")
result = model.transcribe("/tmp/input.wav")
with open("/tmp/transcript.txt", "w") as f:
    f.write(result["text"])
