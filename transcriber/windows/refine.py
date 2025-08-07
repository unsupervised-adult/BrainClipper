import os
import time
import subprocess
import pyperclip
from ollama import Client # type: ignore

PROMPTS = {
    "direct": "Summarize the transcript as a professional workplace message under 80 words. Include one actionable request. Transcript: {transcript}",
    "empathetic": "Rewrite the transcript as a concise, empathetic workplace message under 120 words. Clarify technical details and include a specific action or request. Transcript: {transcript}",
    "email": "Rephrase the transcript as a brief, professional email or chat message under 150 words. Summarize technical details and suggest a next step. Transcript: {transcript}"
}

model = os.environ.get("MODEL_NAME", "granite3-moe:3b")
prompt_key = os.environ.get("PROMPT_STYLE", "direct")

with open("/tmp/transcript.txt", "r") as f:
    transcript = f.read()

prompt_template = PROMPTS.get(prompt_key, PROMPTS["direct"])
prompt = prompt_template.format(transcript=transcript)

client = Client()
response = client.generate(model=model, prompt=prompt)
print("LLM response:", response)
polished_text = response["response"]
# Remove all occurrences of the prompt from the response
polished_text = polished_text.replace(prompt, "").strip()
pyperclip.copy(polished_text)
