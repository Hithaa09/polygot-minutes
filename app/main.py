from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn
import tempfile
import whisper

app = FastAPI(title="Polyglot Minutes API", version="0.0.1")

# Load Whisper once at startup (small = good balance on laptop)
whisper_model = whisper.load_model("small")

# ----- Request Models -----
class SummarizeRequest(BaseModel):
    transcript: str
    target_lang: str = "en"

class ActionRequest(BaseModel):
    transcript: str

# ----- Endpoints -----
@app.get("/")
def health():
    return {"status": "ok", "service": "polyglot-minutes"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Whisper transcribes English/Hindi/Hinglish automatically
    result = whisper_model.transcribe(tmp_path)
    transcript_text = result.get("text", "")
    segments = result.get("segments", []) or []

    return {
        "transcript": transcript_text,
        "segments": [
            {"start": s.get("start"), "end": s.get("end"), "text": s.get("text")}
            for s in segments
        ]
    }

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    # Kiran will replace this with real models
    return {
        "summary_short": ["Dummy bullet point 1", "Dummy bullet point 2"],
        "summary_detailed": "This is a dummy detailed summary."
    }

@app.post("/actions")
async def actions(request: ActionRequest):
    # Akshaya will replace this with real extractor
    return {
        "actions": [
            {"item": "Prepare budget report", "priority": "High"},
            {"item": "Share design mockups", "priority": "Medium"}
        ]
    }

@app.post("/notes")
async def notes(file: UploadFile = File(...)):
    # 1) Transcribe
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    tr = whisper_model.transcribe(tmp_path)
    transcript = tr.get("text", "")

    # 2) Summaries (placeholder until Kiran plugs in)
    summary_short = ["Dummy bullet point 1", "Dummy bullet point 2"]
    summary_detailed = "This is a dummy detailed summary."

    # 3) Actions (placeholder until Akshaya plugs in)
    actions = [
        {"item": "Prepare report", "priority": "High"},
        {"item": "Schedule review", "priority": "Medium"}
    ]

    return {
        "transcript": transcript,
        "summary_short": summary_short,
        "summary_detailed": summary_detailed,
        "actions": actions
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
