from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ComposeRequest, ComposeResponse, FeedbackRequest, FeedbackResponse
from .settings import settings
from .openai_client import compose_with_openai, refine_with_openai, transcribe_audio


def load_scents() -> Dict[str, Any]:
    path: Path = settings.scents_path
    if not path.exists():
        raise FileNotFoundError(f"Scents JSON not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        all_scents = json.load(f)
    # Only include scents with device locations 1-12
    return {
        name: info for name, info in all_scents.items()
        if 1 <= int(info.get("location", 0)) <= 12
    }


app = FastAPI(title="Etherea Scent Composer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/compose", response_model=ComposeResponse)
def compose(request: ComposeRequest) -> ComposeResponse:
    try:
        scents = load_scents()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        result = compose_with_openai(request.sentence, scents)
        return result
    except Exception as e:
        # Surface errors for debugging; in production, sanitize
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    try:
        scents = load_scents()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        result = refine_with_openai(request, scents)
        return result
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> Dict[str, str]:
    """Transcribe audio using OpenAI Whisper."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Expected an audio file")
    try:
        content = await audio.read()
        text = transcribe_audio(content, audio.filename or "audio.webm")
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


