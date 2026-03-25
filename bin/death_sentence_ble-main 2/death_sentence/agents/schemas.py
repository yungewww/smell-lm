from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError, field_validator


class ComposeRequest(BaseModel):
    sentence: str = Field(min_length=1)


def scent_name_literal(choices: list[str]):
    # Utility to create a Literal type dynamically for static tooling awareness isn't possible at runtime,
    # but we keep this for clarity; we will validate via enum in OpenAI schema and Pydantic validator.
    return Literal[tuple(choices)]  # type: ignore[misc]


class ScentItem(BaseModel):
    scent_name: str
    scent_duration: int = Field(ge=1, le=30)


class ComposeResponse(BaseModel):
    scent_sequence: List[ScentItem]
    justification: str

    @field_validator("scent_sequence")
    @classmethod
    def validate_total_duration(cls, value: List[ScentItem]):
        total = sum(item.scent_duration for item in value)
        if total != 60:
            raise ValueError(f"Total duration must equal 60, got {total}")
        return value


class FeedbackRound(BaseModel):
    feedback_text: str
    changes_made: str
    resulting_sequence: List[ScentItem]


class FeedbackRequest(BaseModel):
    original_sentence: str = Field(min_length=1)
    original_sequence: List[ScentItem]
    prior_rounds: List[FeedbackRound] = []
    latest_feedback: str = Field(min_length=1)


class FeedbackResponse(BaseModel):
    scent_sequence: List[ScentItem]
    justification: str
    changes_made: str

    @field_validator("scent_sequence")
    @classmethod
    def validate_total_duration(cls, value: List[ScentItem]):
        total = sum(item.scent_duration for item in value)
        if total != 60:
            raise ValueError(f"Total duration must equal 60, got {total}")
        return value

