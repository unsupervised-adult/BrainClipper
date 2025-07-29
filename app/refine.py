from ollama import Client # type: ignore
import os
import time
import subprocess

PROMPTS = {
    "direct": """Rephrase the transcript into a professional workplace message:
- Use a direct, neutral tone with no excessive politeness.
- Summarize technical details clearly in simple terms.
- Include one specific action or request to move forward.
- Remove all slang, frustration, or informal language.
- Keep it under 80 words.
Transcript: {transcript}
""",
    "empathetic": """Rephrase the following transcript into a professional, concise workplace message:
- Acknowledge the recipient’s context or concerns empathetically.
- Clarify technical details (e.g., system issues, tasks, or instructions) in simple, precise language.
- Provide a specific action or request to advance the task or resolve the issue.
- Eliminate informal language, slang, or frustration, maintaining a calm and constructive tone.
- Adapt to language-specific nuances for clarity and cultural appropriateness.
- Keep the output under 120 words for efficiency.
Transcript: {transcript}
""",
    "email": """Given the following transcript, rephrase it into a concise, professional message suitable for a workplace email or chat:
- Acknowledge the issue empathetically, showing understanding of the user's frustration.
- Summarize any technical details (e.g., system specs, troubleshooting steps) clearly and accurately.
- Suggest a specific, actionable next step or request precise information to move forward.
- Remove all informal language, slang, or emotional venting, ensuring a calm and constructive tone.
- Keep the output under 150 words for brevity.
Transcript: {transcript}
"""
}

model = os.environ.get("MODEL_NAME", "granite3-moe:3b")
prompt_key = os.environ.get("PROMPT_STYLE", "direct")

with open("/tmp/transcript.txt", "r") as f:
    transcript = f.read()

prompt_template = PROMPTS.get(prompt_key, PROMPTS["direct"])
prompt = prompt_template.format(transcript=transcript)

client = Client()
response = client.generate(model=model, prompt=prompt)
polished_text = response["response"]

# Copy polished text to clipboard using xclip
proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
proc.communicate(polished_text.encode())
time.sleep(0.1)
