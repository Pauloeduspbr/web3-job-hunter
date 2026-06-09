"""Stage 4 (lightweight) — parse a pasted job description into requirements.

LinkedIn note: per project policy, job descriptions arrive via email job-alerts
or manual paste — NEVER by scraping LinkedIn. This module takes the raw JD text;
how you obtained it is upstream and must be ToS-compliant.
"""

from __future__ import annotations

from typing import Optional

from . import llm
from .models import JobRequirements
from .settings import settings

SYSTEM = (
    "You analyze a job description and extract its requirements into the schema. "
    "Detect target_language as 'en' or 'pt' from the posting's language. "
    "Separate hard_skills/tools from soft_skills. Capture knockouts (work "
    "authorization/visa, required language, mandatory certifications, on-call). "
    "In 'keywords', list the exact phrases an ATS or recruiter would search "
    "(job title, tool names). Do not invent requirements not in the text."
)


def parse_job(jd_text: str, *, model: Optional[str] = None) -> JobRequirements:
    messages = [
        {
            "role": "user",
            "content": f"Extract requirements from this posting.\n\n<job_posting>\n{jd_text}\n</job_posting>",
        }
    ]
    return llm.parse(messages, JobRequirements, model=model or settings.model_extract, system=SYSTEM, max_tokens=4000)
