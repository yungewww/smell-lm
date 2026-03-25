from __future__ import annotations

import io
import json
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from openai import OpenAI

from .schemas import ComposeResponse, FeedbackRequest, FeedbackResponse, ScentItem
from .settings import settings


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio using OpenAI Whisper API."""
    client = OpenAI(api_key=settings.openai_api_key)
    file_like = io.BytesIO(audio_bytes)
    file_like.name = filename
    response = client.audio.transcriptions.create(model="whisper-1", file=file_like)
    return response.text


def _render_prompt(template_name: str, scents: Dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(settings.prompts_dir),
        autoescape=select_autoescape(enabled_extensions=("j2",)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    scents_json = json.dumps(scents, ensure_ascii=False, indent=4)
    return template.render(scents_json=scents_json)


def _build_schema(scents: Dict[str, Any]) -> Dict[str, Any]:
    # Kept for reference if switching back to json_schema; not used by parse()
    scent_names = list(scents.keys())
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "scent_sequence": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "scent_name": {"type": "string", "enum": scent_names},
                        "scent_duration": {"type": "integer", "minimum": 1, "maximum": 30},
                    },
                    "required": ["scent_name", "scent_duration"],
                },
            },
            "justification": {"type": "string"},
        },
        "required": ["scent_sequence", "justification"],
    }


def compose_with_openai(sentence: str, scents: Dict[str, Any]) -> ComposeResponse:
    system_prompt = _render_prompt("system_prompt.j2", scents)
    client = OpenAI(api_key=settings.openai_api_key)

    # Use Responses API structured parsing into a Pydantic model
    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": sentence},
            ],
            text_format=ComposeResponse,
        )
        # New SDKs expose the parsed object directly
        if hasattr(response, "output_parsed") and response.output_parsed is not None:
            parsed = response.output_parsed
            # Ensure it's a Pydantic model instance
            if isinstance(parsed, ComposeResponse):
                return parsed
            # If SDK returns dict instead
            return ComposeResponse.model_validate(parsed)
        # Fallback: try output_text
        if hasattr(response, "output_text") and response.output_text:
            return ComposeResponse.model_validate_json(response.output_text)
    except Exception:
        # Fall back to a json_schema flow for older SDKs
        schema = _build_schema(scents)
        legacy = client.responses.create(
            model=settings.openai_model,
            instructions=system_prompt,
            input=sentence,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ScentSequence",
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        raw_text = getattr(legacy, "output_text", None)
        if not raw_text:
            try:
                raw_text = legacy.output[0].content[0].text  # type: ignore[index]
            except Exception:
                raw_text = str(legacy)
        return ComposeResponse.model_validate_json(raw_text)


def _build_feedback_user_message(request: FeedbackRequest) -> str:
    """Format a structured user message for the feedback/revision flow."""
    current_seq = [
        {"scent_name": s.scent_name, "scent_duration": s.scent_duration}
        for s in request.original_sequence
    ]
    # If there are prior rounds, the "current" sequence is the last round's result
    if request.prior_rounds:
        last = request.prior_rounds[-1]
        current_seq = [
            {"scent_name": s.scent_name, "scent_duration": s.scent_duration}
            for s in last.resulting_sequence
        ]

    seq_json = json.dumps(current_seq, indent=2)

    history_lines: List[str] = []
    for i, r in enumerate(request.prior_rounds, 1):
        history_lines.append(f"  Round {i}: \"{r.feedback_text}\" → {r.changes_made}")
    history_section = "\n".join(history_lines) if history_lines else "(none)"

    return (
        f"ORIGINAL REQUEST:\n{request.original_sentence}\n\n"
        f"CURRENT SEQUENCE:\n```json\n{seq_json}\n```\n\n"
        f"PRIOR FEEDBACK HISTORY:\n{history_section}\n\n"
        f">>> LATEST FEEDBACK <<<\n{request.latest_feedback}"
    )


def _build_feedback_schema(scents: Dict[str, Any]) -> Dict[str, Any]:
    """JSON schema for feedback response (includes changes_made)."""
    scent_names = list(scents.keys())
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "scent_sequence": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "scent_name": {"type": "string", "enum": scent_names},
                        "scent_duration": {"type": "integer", "minimum": 1, "maximum": 30},
                    },
                    "required": ["scent_name", "scent_duration"],
                },
            },
            "justification": {"type": "string"},
            "changes_made": {"type": "string"},
        },
        "required": ["scent_sequence", "justification", "changes_made"],
    }


def refine_with_openai(request: FeedbackRequest, scents: Dict[str, Any]) -> FeedbackResponse:
    """Refine an existing scent composition based on user feedback."""
    system_prompt = _render_prompt("feedback_prompt.j2", scents)
    user_message = _build_feedback_user_message(request)
    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            text_format=FeedbackResponse,
            max_output_tokens=4096,
        )
        if hasattr(response, "output_parsed") and response.output_parsed is not None:
            parsed = response.output_parsed
            if isinstance(parsed, FeedbackResponse):
                return parsed
            return FeedbackResponse.model_validate(parsed)
        if hasattr(response, "output_text") and response.output_text:
            return FeedbackResponse.model_validate_json(response.output_text)
    except Exception:
        schema = _build_feedback_schema(scents)
        legacy = client.responses.create(
            model=settings.openai_model,
            instructions=system_prompt,
            input=user_message,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ScentRevision",
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        raw_text = getattr(legacy, "output_text", None)
        if not raw_text:
            try:
                raw_text = legacy.output[0].content[0].text  # type: ignore[index]
            except Exception:
                raw_text = str(legacy)
        return FeedbackResponse.model_validate_json(raw_text)

