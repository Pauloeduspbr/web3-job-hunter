"""Stage 7 — translation + glossary QA.

The tailor already writes in the job's target language, so the pipeline mainly
needs `glossary_qa` (verify DO-NOT-TRANSLATE terms survived). `translate` is a
standalone path for "just translate this CV" with deterministic placeholder
protection of protected terms (not relying on prompt instruction alone).
"""

from __future__ import annotations

import re
from typing import Optional

from . import llm
from .settings import settings

_OPEN, _CLOSE = "⟪", "⟫"  # ⟪ ⟫ — unlikely to appear in a CV


def _protect(text: str, terms: list[str]) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    out = text
    # longest-first so 'Apache Spark' is protected before 'Spark'
    for i, term in enumerate(sorted({t for t in terms if t}, key=len, reverse=True)):
        pattern = re.compile(re.escape(term))
        if pattern.search(out):
            placeholder = f"{_OPEN}T{i}{_CLOSE}"
            out = pattern.sub(placeholder, out)
            mapping[placeholder] = term
    return out, mapping


def _restore(text: str, mapping: dict[str, str]) -> str:
    for placeholder, term in mapping.items():
        text = text.replace(placeholder, term)
    return text


_TR_SYSTEM = (
    "You are a professional resume translator. Translate the document to {lang} "
    "while preserving Markdown structure. Do NOT translate placeholder tokens of the "
    f"form {_OPEN}T...{_CLOSE} — keep them verbatim. Use natural professional "
    "terminology (not literal word-for-word). Keep proper nouns intact."
)


def translate(markdown: str, target_lang: str, glossary: dict, *, model: Optional[str] = None) -> str:
    protected, mapping = _protect(markdown, glossary.get("do_not_translate", []))
    lang = "English" if target_lang == "en" else "Portuguese"
    system = _TR_SYSTEM.format(lang=lang)
    messages = [{"role": "user", "content": protected}]
    out = llm.complete(messages, model=model or settings.model_translate, system=system, max_tokens=8000)
    return _restore(out, mapping)


def glossary_qa(markdown: str, glossary: dict) -> list[str]:
    """Return DO-NOT-TRANSLATE terms that did NOT survive intact in the output."""
    return [t for t in glossary.get("do_not_translate", []) if t and t not in markdown]
