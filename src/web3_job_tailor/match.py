"""Stage 5 (lightweight) — explainable match score + gap analysis.

Core MVP weighting (semantic/embeddings omitted — see arquitetura §6):
    final = 0.4 * skill_coverage + 0.6 * llm_judge
- skill_coverage: deterministic, auditable (JD skills present in the fact store).
- llm_judge: nuance + rationale (never an autonomous decision).
To add the semantic layer, install sentence-transformers and blend a third term.
"""

from __future__ import annotations

from typing import Optional

from . import factstore, llm
from .models import JobRequirements, MatchResult, ResumeProfile
from .settings import settings

JUDGE_SYSTEM = (
    "You are a hiring-match judge. Given a candidate profile (facts only) and a "
    "job's requirements, score the fit 0-100 with a short rationale, the must-haves "
    "met, and the honest gaps. Do NOT inflate; reward only real, present evidence."
)


def skill_coverage(requirements: JobRequirements, profile: ResumeProfile) -> tuple[float, list[str]]:
    facts = factstore.extract_facts(profile)
    have = facts["skills"]
    req = [s.strip().lower() for s in (requirements.hard_skills + requirements.tools) if s.strip()]
    req = sorted(set(req))
    if not req:
        return 100.0, []
    present = [s for s in req if any(s in h or h in s for h in have)]
    missing = sorted(set(req) - set(present))
    pct = 100.0 * len(set(present)) / len(req)
    return pct, missing


def judge(requirements: JobRequirements, profile: ResumeProfile, *, model: Optional[str] = None) -> MatchResult:
    payload = (
        f"<requirements>\n{requirements.model_dump_json(indent=2)}\n</requirements>\n\n"
        f"<candidate_facts>\n{profile.model_dump_json(indent=2)}\n</candidate_facts>"
    )
    messages = [{"role": "user", "content": payload}]
    return llm.parse(messages, MatchResult, model=model or settings.model_judge, system=JUDGE_SYSTEM, max_tokens=3000)


def match(requirements: JobRequirements, profile: ResumeProfile) -> MatchResult:
    coverage, missing = skill_coverage(requirements, profile)
    verdict = judge(requirements, profile)
    final = round(0.4 * coverage + 0.6 * verdict.score)
    gaps = sorted(set(verdict.gaps) | set(missing))
    return MatchResult(
        score=final,
        must_haves_met=verdict.must_haves_met,
        gaps=gaps,
        rationale=(
            f"skill_coverage={coverage:.0f}% | judge={verdict.score} | combined={final}. "
            f"{verdict.rationale}"
        ),
    )
