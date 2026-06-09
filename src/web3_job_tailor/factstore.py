"""Fact store persistence + the anti-hallucination traceability guardrail.

The fact store (ResumeProfile JSON) is the single source of truth. The tailoring
loop may only restate facts found here. `verify_traceability` is a deterministic
backstop that flags metrics/percentages appearing in a tailored output that are
NOT present in the store (i.e. potentially invented) — complementary to the LLM
critic in tailor.py.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .models import ResumeProfile
from .settings import settings

# Match template tokens like [SEU_USER] or [Your Name] but NOT JSON arrays
# (which serialize as ["..." , [{...} , or []), so the char after '[' must be a letter.
PLACEHOLDER_RE = re.compile(r"\[[A-Za-z][A-Za-z0-9 _./-]*\]|SEU_USER|YOUR_[A-Z_]+|X{4,}")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?%?")


def save(profile: ResumeProfile, path: Optional[str | Path] = None) -> Path:
    path = Path(path or settings.fact_store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    return path


def load(path: Optional[str | Path] = None) -> ResumeProfile:
    path = Path(path or settings.fact_store_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Fact store not found at {path}. Run `build-store` on your CV PDF first."
        )
    return ResumeProfile.model_validate_json(path.read_text(encoding="utf-8"))


def detect_placeholders(profile: ResumeProfile) -> list[str]:
    """Catch unfilled template tokens (e.g. github.com/[SEU_USER]) before export."""
    blob = profile.model_dump_json()
    return sorted(set(PLACEHOLDER_RE.findall(blob)))


def extract_facts(profile: ResumeProfile) -> dict:
    """Build the allowed-fact sets for the traceability guardrail."""
    skills: set[str] = set()
    numbers: set[str] = set()
    companies: set[str] = set()
    titles: set[str] = set()

    skills.update(s.strip().lower() for s in profile.skills if s.strip())
    texts: list[str] = [profile.summary or "", profile.headline or ""]
    for exp in profile.experiences:
        companies.add(exp.company.strip().lower())
        titles.add(exp.title.strip().lower())
        skills.update(t.strip().lower() for t in exp.tech if t.strip())
        texts.extend(exp.bullets)
    for txt in texts:
        for num in NUM_RE.findall(txt):
            numbers.add(num.replace(",", "."))
    return {"skills": skills, "numbers": numbers, "companies": companies, "titles": titles}


def _is_year(token: str) -> bool:
    t = token.rstrip("%")
    return t.isdigit() and 1900 <= int(t) <= 2100


def verify_traceability(markdown: str, facts: dict, jd_text: str = "") -> list[str]:
    """Flag percentage metrics in the output not backed by the fact store or the JD."""
    jd_nums = {n.replace(",", ".") for n in NUM_RE.findall(jd_text)}
    allowed = facts["numbers"] | jd_nums
    violations: list[str] = []
    for tok in NUM_RE.findall(markdown):
        norm = tok.replace(",", ".")
        if "%" in tok and norm not in allowed and not _is_year(tok):
            violations.append(f"Unverified metric '{tok}' not found in fact store")
    return sorted(set(violations))
