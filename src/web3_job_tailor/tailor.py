"""Stage 6 — tailoring (RAG-grounded + Self-Refine). The anti-hallucination core.

Phase 0 design: the generator emits a STRUCTURED TailoredResume where every
experience bullet carries `source_fact` — a verbatim quote of the fact-store
item it derives from. Traceability is native, not an afterthought.
Education/certifications/languages never pass through the LLM (copied verbatim
from the fact store at render time).

Loop: generate -> (deterministic guardrails + LLM critique) -> refine.
"""

from __future__ import annotations

from typing import Optional

from . import factstore, llm
from .export import tailored_to_markdown
from .models import Critique, JobRequirements, ResumeProfile, TailoredResume
from .settings import settings

GEN_SYSTEM = (
    "You are an expert resume writer optimizing a CV for one specific job, for both "
    "ATS parsing and human recruiters. You output a structured TailoredResume.\n"
    "INVIOLABLE RULES:\n"
    "1. Use ONLY facts from the provided <fact_store>. NEVER invent or add skills, "
    "employers, titles, dates, or metrics.\n"
    "2. Every bullet MUST include source_fact: a VERBATIM quote of the fact-store "
    "bullet/metric it derives from. A bullet you cannot source must not exist.\n"
    "3. You MAY reorder, emphasize, rephrase, and mirror the job's exact terminology "
    "onto facts that already exist (e.g. 'PySpark' -> 'Apache Spark' if the job uses "
    "that term). If a required skill is NOT in the fact store, do NOT add it — it is "
    "a gap, not content.\n"
    "4. Each bullet = action verb + task + quantified result (only real metrics).\n"
    "5. headline mirrors the job title ONLY if the candidate truly held that level.\n"
    "6. skills: 2-4 grouped lines (label + comma-separated details), most relevant "
    "to the job first, containing only skills present in the fact store.\n"
    "7. experiences: reverse-chronological, keep company/title/dates/location "
    "EXACTLY as in the fact store; most relevant bullets first; drop bullets "
    "irrelevant to this job rather than padding.\n"
    "8. No keyword stuffing (a term at most 2-3 times across the resume).\n"
    "9. Write ALL text in {lang}. Do NOT translate terms on this DO-NOT-TRANSLATE "
    "list: {dnt}."
)

CRIT_SYSTEM = (
    "You are an adversarial reviewer of a tailored resume (structured JSON).\n"
    "Set traceable=false if ANY claim (skill, employer, title, date, metric) is not "
    "supported by the <fact_store>, or if any bullet's source_fact does not actually "
    "support its text.\n"
    "Estimate the match 0-100 against <job_requirements>.\n"
    "List concrete, actionable issues.\n"
    "Set approved=true ONLY if: traceable AND match_estimate >= {target} AND bullets "
    "follow action+task+result AND there is no keyword stuffing or invented content."
)


def _generate(
    requirements: JobRequirements,
    profile: ResumeProfile,
    glossary: dict,
    feedback: Optional[str],
    model: Optional[str],
) -> TailoredResume:
    dnt = ", ".join(glossary.get("do_not_translate", []))
    system = GEN_SYSTEM.format(lang=requirements.target_language, dnt=dnt)
    parts = [
        f"<fact_store>\n{profile.model_dump_json(indent=2)}\n</fact_store>",
        f"<job_requirements>\n{requirements.model_dump_json(indent=2)}\n</job_requirements>",
    ]
    if feedback:
        parts.append(f"<critique_to_address>\n{feedback}\n</critique_to_address>")
    parts.append("Produce the TailoredResume now.")
    messages = [{"role": "user", "content": "\n\n".join(parts)}]
    return llm.parse(
        messages, TailoredResume, model=model or settings.model_tailor, system=system
    )


def _critique(
    tailored: TailoredResume,
    requirements: JobRequirements,
    profile: ResumeProfile,
    model: Optional[str],
) -> Critique:
    system = CRIT_SYSTEM.format(target=settings.match_target)
    payload = (
        f"<fact_store>\n{profile.model_dump_json(indent=2)}\n</fact_store>\n\n"
        f"<job_requirements>\n{requirements.model_dump_json(indent=2)}\n</job_requirements>\n\n"
        f"<tailored_resume>\n{tailored.model_dump_json(indent=2)}\n</tailored_resume>"
    )
    messages = [{"role": "user", "content": payload}]
    return llm.parse(messages, Critique, model=model or settings.model_judge, system=system, max_tokens=3000)


def deterministic_guardrails(
    tailored: TailoredResume, profile: ResumeProfile, jd_text: str = ""
) -> list[str]:
    """Code-level backstop, independent of any LLM judgment."""
    facts = factstore.extract_facts(profile)
    violations: list[str] = []

    fact_companies = facts["companies"]
    for exp in tailored.experiences:
        if exp.company.strip().lower() not in fact_companies and not any(
            exp.company.strip().lower() in c or c in exp.company.strip().lower()
            for c in fact_companies
        ):
            violations.append(f"Employer '{exp.company}' not found in fact store")
        for b in exp.bullets:
            if not b.source_fact.strip():
                violations.append(f"Bullet without source_fact: '{b.text[:60]}...'")

    markdown = tailored_to_markdown(tailored, profile)
    violations.extend(factstore.verify_traceability(markdown, facts, jd_text))
    return sorted(set(violations))


def tailor(
    requirements: JobRequirements,
    profile: ResumeProfile,
    glossary: dict,
    *,
    jd_text: str = "",
    max_iters: Optional[int] = None,
    model: Optional[str] = None,
) -> tuple[TailoredResume, Critique, int]:
    """Return (tailored_resume, last_critique, iterations_used)."""
    max_iters = max_iters or settings.max_refine_iters
    feedback: Optional[str] = None
    tailored: Optional[TailoredResume] = None
    critique: Optional[Critique] = None

    for i in range(max_iters):
        tailored = _generate(requirements, profile, glossary, feedback, model)
        guardrail = deterministic_guardrails(tailored, profile, jd_text)
        critique = _critique(tailored, requirements, profile, model)
        if critique.approved and not guardrail:
            return tailored, critique, i + 1
        issues = list(critique.issues) + [f"[guardrail] {v}" for v in guardrail]
        feedback = "\n".join(f"- {x}" for x in issues) or "Improve match and traceability."

    # Not approved within budget — return best effort + the open critique honestly.
    return tailored, critique, max_iters  # type: ignore[return-value]
