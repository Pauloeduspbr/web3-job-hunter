"""Hybrid CV generation.

Mode is resolved by environment, NOT hardcoded:
- "claude_code" — the `claude` CLI is on PATH (LOCAL DEV): generate via the
                  Claude Code subscription, no API token, no per-call cost.
- "api"         — production: ANTHROPIC_API_KEY set and no claude CLI; calls
                  Claude (claude-opus-4-8) directly.
- "manual"      — neither available: deterministic offline tailoring fallback.

Local dev uses the subscription; production uses the token.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile

SYSTEM_PROMPT = """You are an expert resume writer specialized in ATS-optimized \
resumes for senior data engineering roles.

INVIOLABLE TRUTHFULNESS RULES:
1. Never claim a skill, tool, company, title, date or number that is not present \
in the BASE RESUME or the CANDIDATE PROFILE provided.
2. Quantified results must be copied exactly as written (99.9%, 40%, 60%, 50%, 70%).
3. Gap skills are mitigated ONLY via adjacent experience or portfolio projects, \
never fabricated.
4. English level is B2 upper-intermediate — never inflate to advanced/fluent.

FIDELITY RULES (most important — do NOT gut the career history):
5. Keep EVERY company/role from the BASE RESUME and its key projects. NEVER drop a \
company, NEVER collapse roles into one-line summaries, NEVER invent new ones.
6. Tailoring = REORDER and EMPHASIZE: lead the summary and skills with what matches \
the job, reorder/surface the most relevant projects and bullets first, and improve \
wording. It must NOT remove experience or projects. The full history stays.
7. Preserve the BASE RESUME's structure (per-company projects as sub-sections). \
A senior CV of 2–3 pages is expected; do not force it to 2 pages by deleting content.

ATS & FORMAT RULES:
- Single column Markdown, standard headers (Professional Summary, Technical Skills, \
Professional Experience, Education, Certifications, Languages).
- Mirror the job's ATS keywords verbatim (from the brief) in summary, skills and \
experience bullets — without fabricating.
- Contact info in the body. Dates as "Mon YYYY". No tables/images. Action verbs first.
- Write in the LANGUAGE requested in the brief (English by default; Portuguese when \
the brief says the job is Brazilian/PT). Keep proper nouns and tech names as-is.

ATS MATCH LINE:
- Add, immediately under the name/title block (before the summary), one italic line: \
"*ATS Match: <N>% — <Role> @ <Company>*", taking <N> from the brief's match score. \
This is an internal indicator the candidate may remove before sending.

Output ONLY the final resume in Markdown — no preamble, no commentary."""


def get_mode() -> str:
    # Local dev → Claude Code subscription (claude CLI present, no token cost).
    # Production → ANTHROPIC_API_KEY. Offline deterministic fallback otherwise.
    if shutil.which("claude"):
        return "claude_code"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "api"
    return "manual"


def _user_content(brief_md: str, base_resume_md: str, profile_yaml: str) -> str:
    return (
        "Generate the tailored resume for this job.\n\n"
        f"## TAILORING BRIEF (job requirements + ATS keywords + gaps)\n\n{brief_md}\n\n"
        f"## BASE RESUME\n\n{base_resume_md}\n\n"
        f"## CANDIDATE PROFILE (source of truth — do not exceed it)\n\n{profile_yaml}"
    )


def generate_cv_via_claude_code(brief_md: str, base_resume_md: str, profile_yaml: str) -> str:
    """Generate the CV with the LOCAL Claude Code subscription (claude CLI) — no
    API token, no per-call billing. Runs headless from a temp dir so the project
    CLAUDE.md isn't pulled in. Raises on failure (caller falls back to offline)."""
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude CLI not found on PATH")
    proc = subprocess.run(
        [claude, "-p", "--output-format", "text", "--append-system-prompt", SYSTEM_PROMPT],
        input=_user_content(brief_md, base_resume_md, profile_yaml),
        capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {proc.returncode}): {proc.stderr[:400]}")
    text = proc.stdout.strip()
    if text.startswith("```"):  # strip an accidental code fence wrapper
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    if not text:
        raise RuntimeError("claude CLI returned empty output")
    return text


def generate_cv_via_api(brief_md: str, base_resume_md: str, profile_yaml: str) -> str:
    """Generate the tailored resume with Claude. Raises on API errors."""
    import anthropic

    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _user_content(brief_md, base_resume_md, profile_yaml)}],
    ) as stream:
        message = stream.get_final_message()

    text = next((b.text for b in message.content if b.type == "text"), None)
    if not text:
        raise RuntimeError(f"No text in Claude response (stop_reason={message.stop_reason})")
    return text
