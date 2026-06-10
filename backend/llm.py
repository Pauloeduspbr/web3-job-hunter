"""Hybrid CV generation.

- mode "api"    — ANTHROPIC_API_KEY present: calls Claude (claude-opus-4-8) and
                  returns the tailored resume Markdown. Used when the app runs
                  online/autonomously.
- mode "manual" — no key: the endpoint returns the brief path and the user
                  generates the CV in a Claude Code session (zero extra cost).
"""
from __future__ import annotations

import os

SYSTEM_PROMPT = """You are an expert resume writer specialized in ATS-optimized \
resumes for senior data engineering roles.

INVIOLABLE TRUTHFULNESS RULES:
1. Never claim a skill, tool, company, title, date or number that is not present \
in the BASE RESUME or the CANDIDATE PROFILE provided.
2. Quantified results must be copied exactly as written (99.9%, 40%, 60%, 50%, 70%).
3. Gap skills are mitigated ONLY via adjacent experience or portfolio projects, \
never fabricated.
4. English level is B2 upper-intermediate — never inflate to advanced/fluent.

ATS FORMAT RULES:
- Single column Markdown, standard headers (Professional Summary, Skills, \
Work Experience, Education, Certifications, Languages).
- Mirror the job's ATS keywords verbatim (from the brief) in summary, skills and \
experience bullets.
- Contact info in the body. Dates as "Mon YYYY". Max 2 pages. No tables/images.
- ~60% of bullets quantified, action verbs first.

Output ONLY the final resume in Markdown — no preamble, no commentary."""


def get_mode() -> str:
    return "api" if os.getenv("ANTHROPIC_API_KEY") else "manual"


def generate_cv_via_api(brief_md: str, base_resume_md: str, profile_yaml: str) -> str:
    """Generate the tailored resume with Claude. Raises on API errors."""
    import anthropic

    client = anthropic.Anthropic()
    user_content = (
        "Generate the tailored resume for this job.\n\n"
        f"## TAILORING BRIEF (job requirements + ATS keywords + gaps)\n\n{brief_md}\n\n"
        f"## BASE RESUME\n\n{base_resume_md}\n\n"
        f"## CANDIDATE PROFILE (source of truth — do not exceed it)\n\n{profile_yaml}"
    )
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        message = stream.get_final_message()

    text = next((b.text for b in message.content if b.type == "text"), None)
    if not text:
        raise RuntimeError(f"No text in Claude response (stop_reason={message.stop_reason})")
    return text
