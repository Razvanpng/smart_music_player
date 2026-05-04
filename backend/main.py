import os
import tempfile
import whisper
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model("medium")

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path, word_timestamps=True)
    os.remove(tmp_path)

    segments = []
    for s in result.get("segments", []):
        words = s.get("words", [])
        
        if not words:
            segments.append({
                "start": s["start"], 
                "end": s["end"], 
                "text": s["text"].strip()
            })
            continue
            
        current_line = []
        start_time = words[0]["start"]
        
        for i, word_data in enumerate(words):
            word_text = word_data["word"].strip()
            current_line.append(word_text)
            
            is_punctuation = word_text.endswith((".", ",", "?", "!", ";"))
            is_long_enough = len(current_line) >= 6
            is_last_word = i == len(words) - 1
            
            if is_punctuation or is_long_enough or is_last_word:
                segments.append({
                    "start": start_time,
                    "end": word_data["end"],
                    "text": " ".join(current_line)
                })
                current_line = []
                if not is_last_word:
                    start_time = words[i+1]["start"]

    return {"segments": segments}