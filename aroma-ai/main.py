import base64
import io
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

# ─── Settings ────────────────────────────────────────────────────────────────


OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
SCENTS_PATH: Path = Path(os.getenv("SCENTS_JSON_PATH", PROJECT_ROOT / "scent_classification.json"))
PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"

TOTAL_DURATION: int = 60
SESSIONS_DIR: Path = PROJECT_ROOT / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# ─── In-memory session store ──────────────────────────────────────────────────

_sessions: Dict[str, Any] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _save_session(session_id: str) -> None:
    path = SESSIONS_DIR / f"{session_id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(_sessions[session_id], f, ensure_ascii=False, indent=2)

# ─── Module-level singletons ──────────────────────────────────────────────────

_client = OpenAI(api_key=OPENAI_API_KEY)
_scents_cache: Dict[str, Any] | None = None

# ─── Schemas ─────────────────────────────────────────────────────────────────

class ComposeRequest(BaseModel):
    sentence: str = Field(min_length=1)
    session_id: str | None = None
    modalities: List[str] = []
    input_timestamp: str | None = None


class ComposeResponse(BaseModel):
    scent_ratios: Dict[str, float]
    justification: str

    @field_validator("scent_ratios")
    @classmethod
    def validate_ratios(cls, value: Dict[str, float]):
        total = round(sum(value.values()), 2)
        if total != 1.0:
            raise ValueError(f"Ratios must sum to 1.0, got {total}")
        if any(v < 0 for v in value.values()):
            raise ValueError("All ratios must be >= 0")
        return value


class FeedbackRound(BaseModel):
    feedback_text: str
    changes_made: str
    resulting_ratios: Dict[str, float]


class FeedbackRequest(BaseModel):
    original_sentence: str = Field(min_length=1)
    original_ratios: Dict[str, float]
    prior_rounds: List[FeedbackRound] = []
    latest_feedback: str = Field(min_length=1)
    session_id: str | None = None
    modalities: List[str] = []
    input_timestamp: str | None = None


class FeedbackResponse(BaseModel):
    scent_ratios: Dict[str, float]
    justification: str
    changes_made: str

    @field_validator("scent_ratios")
    @classmethod
    def validate_ratios(cls, value: Dict[str, float]):
        total = round(sum(value.values()), 2)
        if total != 1.0:
            raise ValueError(f"Ratios must sum to 1.0, got {total}")
        if any(v < 0 for v in value.values()):
            raise ValueError("All ratios must be >= 0")
        return value


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_scents() -> Dict[str, Any]:
    global _scents_cache
    if _scents_cache is not None:
        return _scents_cache
    if not SCENTS_PATH.exists():
        raise FileNotFoundError(f"Scents JSON not found at {SCENTS_PATH}")
    with SCENTS_PATH.open("r", encoding="utf-8") as f:
        all_scents = json.load(f)
    _scents_cache = {
        name: info for name, info in all_scents.items()
        if 1 <= int(info.get("location", 0)) <= 12
    }
    return _scents_cache


def ratios_to_sequence(scent_ratios: Dict[str, float], scents: Dict[str, Any]) -> List[Dict]:
    """Convert ratio vector to duration sequence for hardware playback."""
    sequence = []
    for name, ratio in scent_ratios.items():
        if ratio <= 0:
            continue
        duration = max(1, round(ratio * TOTAL_DURATION))
        meta = scents.get(name, {})
        location = int(meta.get("location", 0))
        if 1 <= location <= 12:
            sequence.append({"scent_name": name, "scent_duration": duration, "scent_id": location})
    return sequence


def _render_prompt(template_name: str, scents: Dict[str, Any]) -> str:
    path = PROMPTS_DIR / template_name
    template = path.read_text(encoding="utf-8")
    return template.replace("{{ scents_json }}", json.dumps(scents, ensure_ascii=False, indent=4))


def _build_schema(scents: Dict[str, Any], include_changes_made: bool = False) -> Dict[str, Any]:
    scent_names = list(scents.keys())
    ratio_properties = {name: {"type": "number"} for name in scent_names}
    properties: Dict[str, Any] = {
        "scent_ratios": {
            "type": "object",
            "properties": ratio_properties,
            "required": scent_names,
            "additionalProperties": False,
        },
        "justification": {"type": "string"},
    }
    required = ["scent_ratios", "justification"]
    if include_changes_made:
        properties["changes_made"] = {"type": "string"}
        required.append("changes_made")
    return {"type": "object", "additionalProperties": False, "properties": properties, "required": required}


def _call_openai(system_prompt: str, user_message: str, response_model, schema_name: str, scents: Dict[str, Any], include_changes_made: bool = False):
    try:
        response = _client.responses.parse(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            text_format=response_model,
            max_output_tokens=4096,
        )
        if hasattr(response, "output_parsed") and response.output_parsed is not None:
            parsed = response.output_parsed
            return parsed if isinstance(parsed, response_model) else response_model.model_validate(parsed)
        if hasattr(response, "output_text") and response.output_text:
            return response_model.model_validate_json(response.output_text)
    except Exception:
        pass
    
    legacy = _client.responses.create(
        model=OPENAI_MODEL,
        instructions=system_prompt,
        input=user_message,
        text={
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": _build_schema(scents, include_changes_made=include_changes_made),
                "strict": True,
            }
        },
    )
    raw_text = getattr(legacy, "output_text", None)
    if not raw_text:
        try:
            raw_text = legacy.output[0].content[0].text
        except Exception:
            raw_text = str(legacy)
    return response_model.model_validate_json(raw_text)


def _build_feedback_user_message(request: FeedbackRequest) -> str:
    current_ratios = (
        request.prior_rounds[-1].resulting_ratios
        if request.prior_rounds
        else request.original_ratios
    )
    history_section = "\n".join(
        f'  Round {i}: "{r.feedback_text}" → {r.changes_made}'
        for i, r in enumerate(request.prior_rounds, 1)
    ) or "(none)"
    return (
        f"ORIGINAL REQUEST:\n{request.original_sentence}\n\n"
        f"CURRENT RATIOS:\n{json.dumps(current_ratios, indent=2)}\n\n"
        f"PRIOR FEEDBACK HISTORY:\n{history_section}\n\n"
        f">>> LATEST FEEDBACK <<<\n{request.latest_feedback}"
    )


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    file_like = io.BytesIO(audio_bytes)
    file_like.name = filename
    response = _client.audio.transcriptions.create(model="whisper-1", file=file_like)
    return response.text


def describe_image(image_bytes: bytes, media_type: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = _client.chat.completions.create(
        model="gpt-4o",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
                {"type": "text", "text": "Describe this image in 1–2 vivid, sensory sentences focusing on atmosphere, mood, and physical environment. No lists. Pure prose."},
            ],
        }],
    )
    return response.choices[0].message.content or ""


# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(title="Etherea Scent Composer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/compose")
def compose(request: ComposeRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    try:
        t_start = datetime.now(timezone.utc)
        scents = load_scents()
        system_prompt = _render_prompt("system_prompt.txt", scents)
        result: ComposeResponse = _call_openai(system_prompt, request.sentence, ComposeResponse, "ScentRatios", scents)
        sequence = ratios_to_sequence(result.scent_ratios, scents)
        t_end = datetime.now(timezone.utc)

        session_id = request.session_id or str(uuid.uuid4())
        _sessions[session_id] = {
            "session_id": session_id,
            "started_at": request.input_timestamp or t_start.isoformat(),
            "ended_at": None,
            "modalities_used": request.modalities,
            "compose": {
                "prompt": request.sentence,
                "timestamp": t_start.isoformat(),
                "response_time_ms": int((t_end - t_start).total_seconds() * 1000),
                "ratios": result.scent_ratios,
                "justification": result.justification,
            },
            "feedback_rounds": [],
            "played_on_device": False,
            "total_rounds": 0,
        }
        _save_session(session_id)

        return {
            "session_id": session_id,
            "scent_ratios": result.scent_ratios,
            "scent_sequence": sequence,
            "justification": result.justification,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    try:
        t_start = datetime.now(timezone.utc)
        scents = load_scents()
        system_prompt = _render_prompt("feedback_prompt.txt", scents)
        user_message = _build_feedback_user_message(request)
        result: FeedbackResponse = _call_openai(system_prompt, user_message, FeedbackResponse, "ScentRevision", scents, include_changes_made=True)
        sequence = ratios_to_sequence(result.scent_ratios, scents)
        t_end = datetime.now(timezone.utc)

        if request.session_id and request.session_id in _sessions:
            sess = _sessions[request.session_id]
            round_num = len(sess["feedback_rounds"]) + 1

            # compute ratio diff vs previous
            prev_ratios = (
                sess["feedback_rounds"][-1]["resulting_ratios"]
                if sess["feedback_rounds"]
                else sess["compose"]["ratios"]
            )
            all_keys = set(prev_ratios) | set(result.scent_ratios)
            ratio_diff = round(sum(abs(result.scent_ratios.get(k, 0) - prev_ratios.get(k, 0)) for k in all_keys), 4)

            sess["feedback_rounds"].append({
                "round": round_num,
                "timestamp": t_start.isoformat(),
                "modalities": request.modalities,
                "feedback_text": request.latest_feedback,
                "changes_made": result.changes_made,
                "resulting_ratios": result.scent_ratios,
                "ratio_diff": ratio_diff,
                "response_time_ms": int((t_end - t_start).total_seconds() * 1000),
            })
            sess["total_rounds"] = round_num
            sess["ended_at"] = t_end.isoformat()
            _save_session(request.session_id)

        return {
            "scent_ratios": result.scent_ratios,
            "scent_sequence": sequence,
            "justification": result.justification,
            "changes_made": result.changes_made,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/session/{session_id}/played")
def mark_played(session_id: str):
    if session_id in _sessions:
        _sessions[session_id]["played_on_device"] = True
        _sessions[session_id]["ended_at"] = _now()
        _save_session(session_id)
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> Dict[str, str]:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Expected an audio file")
    try:
        content = await audio.read()
        text = transcribe_audio(content, audio.filename or "audio.webm")
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/describe")
async def describe(image: UploadFile = File(...)) -> Dict[str, str]:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Expected an image file")
    try:
        content = await image.read()
        text = describe_image(content, image.content_type)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))