import sys
import whisper
import os

def main():
    audio_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/input.wav'
    model = whisper.load_model('small')
    result = model.transcribe(audio_file)
    with open('/tmp/transcript.txt', 'w') as f:
        f.write(result['text'])
    print("Transcript written to /tmp/transcript.txt")

if __name__ == "__main__":
    main()
