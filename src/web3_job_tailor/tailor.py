"""Stage 6 — tailoring (RAG-grounded + Self-Refine). The anti-hallucination core.

Loop: generate -> (deterministic traceability backstop + LLM critique) -> refine.
The generator is grounded ONLY in the fact store: it may reorder, emphasize,
rephrase and mirror the job's terminology onto REAL facts, but never invent a
skill, employer, date or metric. Writes directly in the job's target language.
"""

from __future__ import annotations

from typing import Optional

from . import factstore, llm
from .models import Critique, JobRequirements, ResumeProfile
from .settings import settings

GEN_SYSTEM = (
    "You are an expert resume writer optimizing a CV for one specific job, for both "
    "ATS parsing and human recruiters.\n"
    "INVIOLABLE RULES:\n"
    "1. Use ONLY facts from the provided <fact_store>. NEVER invent or add skills, "
    "employers, titles, dates, or metrics.\n"
    "2. You MAY reorder, emphasize, rephrase, and mirror the job's exact terminology "
    "onto facts that already exist (e.g. 'PySpark' -> 'Apache Spark' if the job uses "
    "that term). If a required skill is NOT in the fact store, do NOT add it — leave "
    "it as a gap.\n"
    "3. Each experience bullet = action verb + task + quantified result, using ONLY "
    "real metrics from the fact store.\n"
    "4. No keyword stuffing (a term at most 2-3 times, always in context). No white "
    "text. Mirror the exact job title only if the candidate truly held that level.\n"
    "5. Single-column Markdown. Sections: Summary, Skills, Experience, Education "
    "(+ Certifications/Languages if present). No tables, columns, images or icons.\n"
    "6. Write the ENTIRE resume in {lang}. Do NOT translate terms on this "
    "DO-NOT-TRANSLATE list: {dnt}."
)

CRIT_SYSTEM = (
    "You are an adversarial reviewer of a tailored resume.\n"
    "Set traceable=false if ANY claim (skill, employer, title, metric) is not "
    "supported by the <fact_store>.\n"
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
) -> str:
    dnt = ", ".join(glossary.get("do_not_translate", []))
    system = GEN_SYSTEM.format(lang=requirements.target_language, dnt=dnt)
    parts = [
        f"<fact_store>\n{profile.model_dump_json(indent=2)}\n</fact_store>",
        f"<job_requirements>\n{requirements.model_dump_json(indent=2)}\n</job_requirements>",
    ]
    if feedback:
        parts.append(f"<critique_to_address>\n{feedback}\n</critique_to_address>")
    parts.append("Produce the tailored resume in Markdown now.")
    messages = [{"role": "user", "content": "\n\n".join(parts)}]
    return llm.complete(messages, model=model or settings.model_tailor, system=system, max_tokens=8000)


def _critique(
    markdown: str,
    requirements: JobRequirements,
    profile: ResumeProfile,
    model: Optional[str],
) -> Critique:
    system = CRIT_SYSTEM.format(target=settings.match_target)
    payload = (
        f"<fact_store>\n{profile.model_dump_json(indent=2)}\n</fact_store>\n\n"
        f"<job_requirements>\n{requirements.model_dump_json(indent=2)}\n</job_requirements>\n\n"
        f"<tailored_resume>\n{markdown}\n</tailored_resume>"
    )
    messages = [{"role": "user", "content": payload}]
    return llm.parse(messages, Critique, model=model or settings.model_judge, system=system, max_tokens=3000)


def tailor(
    requirements: JobRequirements,
    profile: ResumeProfile,
    glossary: dict,
    *,
    jd_text: str = "",
    max_iters: Optional[int] = None,
    model: Optional[str] = None,
) -> tuple[str, Critique, int]:
    """Return (tailored_markdown, last_critique, iterations_used)."""
    max_iters = max_iters or settings.max_refine_iters
    facts = factstore.extract_facts(profile)
    feedback: Optional[str] = None
    markdown = ""
    critique: Optional[Critique] = None

    for i in range(max_iters):
        markdown = _generate(requirements, profile, glossary, feedback, model)
        guardrail = factstore.verify_traceability(markdown, facts, jd_text)
        critique = _critique(markdown, requirements, profile, model)
        if critique.approved and not guardrail:
            return markdown, critique, i + 1
        issues = list(critique.issues) + [f"[guardrail] {v}" for v in guardrail]
        feedback = "\n".join(f"- {x}" for x in issues) or "Improve match and traceability."

    # Not approved within budget — return best effort + the open critique honestly.
    return markdown, critique, max_iters  # type: ignore[return-value]
