"""The triage decision schema: every decision the agent makes must match it (Epic 1, story 1)."""

import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

Category = Literal["billing", "bug", "access", "performance", "how-to"]
Priority = Literal["P1", "P2", "P3", "P4"]
Route = Literal["billing-team", "bug-team", "access-team", "performance-team", "how-to-team"]

_SENTENCE_BREAK = re.compile(r"([.!?])(\s*)(\w)")
_SHORT_ABBREVIATIONS = {"e", "g", "i", "etc", "vs", "mr", "ms", "dr", "p", "no"}


class TriageDecision(BaseModel):
    """Where a support ticket goes, how urgent it is, and why."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: Category = Field(description="The ticket's category from the triage policy.")
    priority: Priority = Field(description="P1 is the most urgent, P4 the least.")
    route: Route = Field(description="The team that handles this category.")
    rationale: str = Field(description="One sentence naming the policy rule that was applied.")

    @field_validator("rationale")
    @classmethod
    def _one_sentence(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("rationale must not be empty")
        if not re.search(r"\w", text):
            raise ValueError("rationale must contain words")
        for match in _SENTENCE_BREAK.finditer(text):
            punctuation, whitespace, next_character = match.groups()
            preceding_word = re.search(r"([A-Za-z]+)$", text[: match.start()])
            preceding_word = preceding_word.group(1).lower() if preceding_word else ""
            abbreviated = punctuation == "." and preceding_word in _SHORT_ABBREVIATIONS
            adjacent_sentence = not whitespace and next_character.isalpha() and len(preceding_word) > 2
            spaced_sentence = bool(whitespace) and not abbreviated
            if punctuation in "!?" or adjacent_sentence or spaced_sentence:
                raise ValueError("rationale must be a single sentence")
        return text


class TriageValidationError(ValueError):
    """Raised when a decision does not match the schema. The message lists every problem."""


def validate_decision(payload: str | bytes | dict) -> TriageDecision:
    """Parse a decision from JSON text or a dict and validate it against the schema."""
    if isinstance(payload, (str, bytes)):
        try:
            payload = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise TriageValidationError(f"Decision is not valid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise TriageValidationError(f"Decision must be a JSON object, got {type(payload).__name__}")
    try:
        return TriageDecision.model_validate(payload)
    except ValidationError as error:
        problems = "; ".join(
            f"{'.'.join(map(str, e['loc'])) or 'decision'}: {e['msg']}" for e in error.errors()
        )
        raise TriageValidationError(f"Invalid triage decision: {problems}") from error
