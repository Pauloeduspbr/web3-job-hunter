"""Orchestrator — ties the core stages together (1-2 build store; 4-6-7-8 tailor)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import export, factstore, jobparse, structure, translate as tr
from . import match as match_mod
from . import tailor as tailor_mod
from .models import ResumeProfile
from .settings import load_glossary


def build_fact_store(
    pdf_path: str | Path, *, use_vision: bool = False, out: Optional[str | Path] = None
) -> tuple[ResumeProfile, Path, list[str]]:
    """Stages 1-2: PDF -> reviewed fact store. Returns (profile, path, placeholders)."""
    profile = structure.structure_cv(pdf_path, use_vision=use_vision)
    path = factstore.save(profile, out)
    placeholders = factstore.detect_placeholders(profile)
    return profile, path, placeholders


def run(jd_text: str, *, profile: Optional[ResumeProfile] = None, out_dir: str | Path = "output") -> dict:
    """Stages 4-6-7-8: pasted JD -> match + tailored, translated, ATS-safe CV."""
    glossary = load_glossary()
    profile = profile or factstore.load()

    requirements = jobparse.parse_job(jd_text)
    match_result = match_mod.match(requirements, profile)
    markdown, critique, iterations = tailor_mod.tailor(
        requirements, profile, glossary, jd_text=jd_text
    )
    glossary_missing = tr.glossary_qa(markdown, glossary)
    ats_warnings = export.qa(markdown, requirements)

    out_dir = Path(out_dir)
    base = f"{(requirements.company or 'job').replace(' ', '_')}_{requirements.target_language}"
    md_path = export.to_markdown_file(markdown, out_dir / f"resume_{base}.md")
    docx_path = export.to_docx(markdown, out_dir / f"resume_{base}.docx")

    return {
        "requirements": requirements,
        "match": match_result,
        "critique": critique,
        "iterations": iterations,
        "markdown": markdown,
        "md_path": str(md_path),
        "docx_path": str(docx_path),
        "glossary_missing": glossary_missing,
        "ats_warnings": ats_warnings,
    }
