"""Thin Anthropic SDK wrapper.

Two helpers grounded in the claude-api skill:
- parse(): structured output via client.messages.parse(output_format=PydanticModel)
           -> validated instance (response.parsed_output).
- complete(): plain text via client.messages.create().

No thinking/effort params are passed, so the same code is safe across Haiku,
Sonnet and Opus (effort 400s on Haiku 4.5 / Sonnet 4.5).
"""

from __future__ import annotations

from typing import Optional, Type, TypeVar

import anthropic
from pydantic import BaseModel

from .settings import settings

T = TypeVar("T", bound=BaseModel)

_client: Optional["anthropic.Anthropic"] = None


def client() -> "anthropic.Anthropic":
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def parse(
    messages: list,
    output_format: Type[T],
    *,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 8000,
) -> T:
    """Force a schema and return the validated Pydantic instance."""
    kwargs = dict(
        model=model or settings.model_extract,
        max_tokens=max_tokens,
        messages=messages,
        output_format=output_format,
    )
    if system:
        kwargs["system"] = system
    resp = client().messages.parse(**kwargs)
    parsed = getattr(resp, "parsed_output", None)
    if parsed is None:
        raise RuntimeError(
            f"structured parse returned no output (stop_reason={resp.stop_reason}); "
            "the model may have refused or hit max_tokens."
        )
    return parsed


def complete(
    messages: list,
    *,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 8000,
) -> str:
    """Return the concatenated text of the response."""
    kwargs = dict(model=model or settings.model_tailor, max_tokens=max_tokens, messages=messages)
    if system:
        kwargs["system"] = system
    resp = client().messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text")
