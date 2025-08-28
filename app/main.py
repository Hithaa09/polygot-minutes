from fastapi import FastAPI, UploadFile, File
import uvicorn

app = FastAPI(title="Polyglot Minutes API", version="0.0.1")

@app.get("/")
def health():
    return {"status": "ok", "service": "polyglot-minutes"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "language": "en",            # placeholder
        "transcript": "dummy text",  # placeholder
        "timestamps": []             # placeholder
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

print("hello")