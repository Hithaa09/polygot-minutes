from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import whisper
import re
from typing import List, Dict

app = FastAPI(title="Polyglot Minutes API", version="0.0.1")

# Enable CORS for the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper once at startup (small = good balance on laptop)
whisper_model = whisper.load_model("small")

# ----- Request Models -----
class SummarizeRequest(BaseModel):
    transcript: str
    target_lang: str = "en"

class ActionRequest(BaseModel):
    transcript: str

# ----- Helper Functions -----
def extract_actions(transcript: str) -> List[Dict]:
    """
    Extract actionable items from transcript using pattern matching and NLP heuristics.
    Looks for action verbs, deadlines, and assignees.
    """
    actions = []
    
    # Common action verbs and phrases
    action_patterns = [
        r'need to (.*?)(?:\.|$)',
        r'will (.*?)(?:\.|$)',
        r'should (.*?)(?:\.|$)',
        r'must (.*?)(?:\.|$)',
        r'let\'s (.*?)(?:\.|$)',
        r'can you (.*?)(?:\.|$)',
        r'please (.*?)(?:\.|$)',
        r'action item[:\s]+(.*?)(?:\.|$)',
        r'follow up on (.*?)(?:\.|$)',
        r'prepare (.*?)(?:\.|$)',
        r'schedule (.*?)(?:\.|$)',
        r'review (.*?)(?:\.|$)',
        r'create (.*?)(?:\.|$)',
        r'send (.*?)(?:\.|$)',
        r'update (.*?)(?:\.|$)',
        r'complete (.*?)(?:\.|$)',
    ]
    
    # Priority indicators
    high_priority_keywords = ['urgent', 'asap', 'immediately', 'critical', 'important', 'priority','Today','tomorrow',]
    medium_priority_keywords = ['this week', 'soon', 'next week']
    low_priority_keywords = ['when possible', 'eventually', 'nice to have']
    
    sentences = re.split(r'[.!?]\s+', transcript)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        for pattern in action_patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                action_text = match.group(1).strip()
                if len(action_text) < 10:  # Skip very short matches
                    continue
                
                # Determine priority
                priority = "Medium"
                sentence_lower = sentence.lower()
                
                if any(keyword in sentence_lower for keyword in high_priority_keywords):
                    priority = "High"
                elif any(keyword in sentence_lower for keyword in medium_priority_keywords):
                    priority = "Medium"
                elif any(keyword in sentence_lower for keyword in low_priority_keywords):
                    priority = "Low"
                
                # Extract assignee if mentioned
                assignee = None
                assignee_patterns = [
                    r'(?:\w+\s+will\s+)',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:should|will|needs)',
                ]
                
                # Clean up common prefixes
                action_text = re.sub(r'^(the|a|an)\s+', '', action_text, flags=re.IGNORECASE)
                
                actions.append({
                    "item": action_text,
                    "priority": priority
                })
                
                # Only keep first match per sentence
                break
    
    # Remove duplicates and keep unique actions
    seen = set()
    unique_actions = []
    for action in actions:
        item_key = action["item"].lower()
        if item_key not in seen and len(action["item"]) > 5:
            seen.add(item_key)
            unique_actions.append(action)
    
    # If no actions found, provide a default
    if not unique_actions:
        unique_actions.append({
            "item": "Review the meeting transcript for action items",
            "priority": "Medium"
        })
    
    return unique_actions[:5]  # Return top 5 actions

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
    """Extract actionable items from the transcript"""
    extracted_actions = extract_actions(request.transcript)
    return {"actions": extracted_actions}

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

    # 3) Actions (extracted using our logic)
    actions_list = extract_actions(transcript)

    return {
        "transcript": transcript,
        "summary_short": summary_short,
        "summary_detailed": summary_detailed,
        "actions": actions_list
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
