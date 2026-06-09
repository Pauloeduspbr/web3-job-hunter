"""Orchestrator — ties the core stages together.

Phase 0 output per job: professional PDF (RenderCV/Typst, themed) + ATS-safe
DOCX + markdown + traceability report + ATS self-check, in PT or EN.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import export, factstore, jobparse, jsonresume, render, structure, translate as tr
from . import match as match_mod
from . import tailor as tailor_mod
from . import trace_report
from .models import ResumeProfile
from .settings import load_glossary


def build_fact_store(
    pdf_path: str | Path, *, use_vision: bool = False, out: Optional[str | Path] = None
) -> tuple[ResumeProfile, Path, list[str]]:
    """Stages 1-2: PDF -> reviewed fact store. Returns (profile, path, placeholders).
    Also exports the JSON Resume v1.0.0 view next to the fact store."""
    profile = structure.structure_cv(pdf_path, use_vision=use_vision)
    path = factstore.save(profile, out)
    jsonresume.export_jsonresume(profile, path.with_suffix(".jsonresume.json"))
    placeholders = factstore.detect_placeholders(profile)
    return profile, path, placeholders


def run(
    jd_text: str,
    *,
    profile: Optional[ResumeProfile] = None,
    out_dir: str | Path = "output",
    theme: str = "engineeringresumes",
) -> dict:
    """Stages 4-6-7-8: pasted JD -> match + tailored professional CV package."""
    glossary = load_glossary()
    profile = profile or factstore.load()

    requirements = jobparse.parse_job(jd_text)
    lang = requirements.target_language if requirements.target_language in ("en", "pt") else "en"
    match_result = match_mod.match(requirements, profile)
    tailored, critique, iterations = tailor_mod.tailor(
        requirements, profile, glossary, jd_text=jd_text
    )

    markdown = export.tailored_to_markdown(tailored, profile, lang)
    glossary_missing = tr.glossary_qa(markdown, glossary)
    ats_warnings = export.qa(markdown, requirements)

    out_dir = Path(out_dir)
    base = f"{(requirements.company or 'job').replace(' ', '_')}_{lang}"
    md_path = export.to_markdown_file(markdown, out_dir / f"resume_{base}.md")
    docx_path = export.to_docx(markdown, out_dir / f"resume_{base}.docx")

    # Professional PDF (RenderCV/Typst)
    pdf_path: Optional[str] = None
    pdf_error: Optional[str] = None
    ats_pdf_missing: list[str] = []
    try:
        data = render.build_rendercv_data(profile, tailored, theme=theme, lang=lang)
        pdf = render.render_pdf(data, out_dir, file_label=f"resume_{base}")
        pdf_path = str(pdf)
        must = [profile.contact.full_name] + [e.company for e in tailored.experiences]
        must += [s.label for s in tailored.skills]
        ats_pdf_missing = export.ats_selfcheck_pdf(pdf, must)
    except Exception as exc:  # render must never lose the tailoring work
        pdf_error = f"{type(exc).__name__}: {exc}"

    report_md = trace_report.build_trace_report(tailored, requirements, match_result)
    report_path = export.to_markdown_file(report_md, out_dir / f"trace_report_{base}.md")

    return {
        "requirements": requirements,
        "match": match_result,
        "tailored": tailored,
        "critique": critique,
        "iterations": iterations,
        "markdown": markdown,
        "md_path": str(md_path),
        "docx_path": str(docx_path),
        "pdf_path": pdf_path,
        "pdf_error": pdf_error,
        "trace_report_path": str(report_path),
        "glossary_missing": glossary_missing,
        "ats_warnings": ats_warnings,
        "ats_pdf_missing": ats_pdf_missing,
        "theme": theme,
    }
