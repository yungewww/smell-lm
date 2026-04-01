from openai import OpenAI
from pydub import AudioSegment
import os

OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

audio = AudioSegment.from_file("janice.m4a")
chunk_length_ms = 5 * 60 * 1000

chunks = []
for i in range(0, len(audio), chunk_length_ms):
    chunk = audio[i:i + chunk_length_ms]
    chunk_name = f"chunk_{i}.m4a"
    chunk.export(chunk_name, format="mp4")
    chunks.append(chunk_name)

full_text = ""

for chunk_file in chunks:
    with open(chunk_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f
        )
        full_text += transcript.text + "\n"

for chunk_file in chunks:
    os.remove(chunk_file)

with open("output.txt", "w", encoding="utf-8") as out:
    out.write(full_text)

print("完成，输出到 output.txt")