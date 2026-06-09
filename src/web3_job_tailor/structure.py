"""Stage 2 — structure the CV text into the ResumeProfile fact store.

Two paths:
- structure_from_markdown(): text (from ingest) -> JSON (cheap, Haiku).
- structure_from_pdf_vision(): raw PDF document block -> JSON (robust, Sonnet).

The output is validated by Pydantic; it must be REVIEWED by a human before it
becomes the immutable fact store (the single source of truth for tailoring).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import llm
from .ingest import pdf_to_base64, pdf_to_markdown
from .models import ResumeProfile
from .settings import settings

SYSTEM = (
    "You extract a resume into structured JSON. Copy facts VERBATIM. "
    "NEVER invent, infer, or embellish: if a field is absent, leave it null/empty. "
    "Preserve every metric, percentage and number exactly as written. "
    "Keep technologies/tools in their original form."
)


def structure_from_markdown(markdown: str, *, model: Optional[str] = None) -> ResumeProfile:
    messages = [
        {
            "role": "user",
            "content": f"Extract this resume into the schema. Add nothing.\n\n<resume>\n{markdown}\n</resume>",
        }
    ]
    return llm.parse(messages, ResumeProfile, model=model or settings.model_extract, system=SYSTEM)


def structure_from_pdf_vision(pdf_path: str | Path, *, model: Optional[str] = None) -> ResumeProfile:
    b64 = pdf_to_base64(pdf_path)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
                },
                {"type": "text", "text": "Extract this resume into the schema. Add nothing."},
            ],
        }
    ]
    return llm.parse(messages, ResumeProfile, model=model or settings.model_tailor, system=SYSTEM)


def structure_cv(pdf_path: str | Path, *, use_vision: bool = False, model: Optional[str] = None) -> ResumeProfile:
    if use_vision:
        return structure_from_pdf_vision(pdf_path, model=model)
    return structure_from_markdown(pdf_to_markdown(pdf_path), model=model)
