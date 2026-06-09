"""Stage 8 (Phase 0) — professional PDF rendering via RenderCV/Typst.

Maps the fact store + TailoredResume onto the RenderCV data model (field names
verified against the installed rendercv 2.8 source: schema/sample_content.yaml
and schema/models/*) and compiles a Tagged PDF with the bundled Typst.

Windows note: rendercv's bundled Typst package imports @preview/fontawesome,
which Typst would try to download (and the cache move fails on some Windows
setups). We vendor that package in vendor/typst_packages/ and pre-populate the
compiler's package_path before rendering.

Requires Python >= 3.12 (rendercv constraint) — use the project .venv (3.13).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Optional

import yaml

from .models import ResumeProfile, TailoredResume
from .settings import ROOT

THEMES = (
    "engineeringresumes",  # tech-dense, strict single column (default)
    "classic",
    "harvard",
    "engineeringclassic",
    "sb2nov",
    "moderncv",
    "ink",
    "opal",
    "ember",
)

SECTION_TITLES = {
    "en": {
        "summary": "summary",
        "skills": "skills",
        "experience": "experience",
        "education": "education",
        "certifications": "certifications",
        "languages": "languages",
    },
    "pt": {
        "summary": "resumo",
        "skills": "competências",
        "experience": "experiência profissional",
        "education": "formação acadêmica",
        "certifications": "certificações",
        "languages": "idiomas",
    },
}

_MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "sept": "09", "oct": "10", "nov": "11",
    "dec": "12",
}


def _ensure_typst_packages() -> None:
    """Copy vendored Typst packages into the package_path rendercv's compiler uses."""
    from rendercv.renderer import pdf_png

    pkg_root = pdf_png.get_package_path()  # lru_cached — same dir the compiler sees
    vendor = ROOT / "vendor" / "typst_packages"
    if not vendor.exists():
        return
    for pkg_dir in vendor.iterdir():
        for version_dir in pkg_dir.iterdir():
            dst = pkg_root / "preview" / pkg_dir.name / version_dir.name
            if not dst.exists():
                shutil.copytree(version_dir, dst)


def to_rendercv_date(value: Optional[str]) -> Optional[str]:
    """Convert fact-store dates (MM/YYYY, YYYY, 'Present', 'July 2025') to
    RenderCV format (YYYY-MM, YYYY, 'present'). Returns None if unparseable."""
    if not value:
        return None
    v = value.strip()
    if v.lower() in ("present", "atual", "current", "now"):
        return "present"
    if re.fullmatch(r"\d{4}-\d{2}", v):
        return v
    m = re.fullmatch(r"(\d{2})/(\d{4})", v)
    if m:
        return f"{m.group(2)}-{m.group(1)}"
    if re.fullmatch(r"\d{4}", v):
        return v
    m = re.fullmatch(r"([A-Za-z]+)\.?\s+(\d{4})", v)
    if m:
        month = _MONTHS.get(m.group(1).lower()[:4]) or _MONTHS.get(m.group(1).lower()[:3])
        if month:
            return f"{m.group(2)}-{month}"
    return None


def _social_username(url: Optional[str], host: str) -> Optional[str]:
    if not url:
        return None
    m = re.search(rf"{host}/(?:in/)?([A-Za-z0-9._-]+)", url)
    return m.group(1) if m else None


def build_rendercv_data(
    profile: ResumeProfile,
    tailored: Optional[TailoredResume] = None,
    *,
    theme: str = "engineeringresumes",
    lang: str = "en",
) -> dict:
    """Map fact store (+ optional tailored layer) onto the RenderCV schema dict.

    Tailored layer overrides headline/summary/skills/experiences; education,
    certifications and languages always come verbatim from the fact store.
    """
    if theme not in THEMES:
        raise ValueError(f"Unknown theme '{theme}'. Available: {', '.join(THEMES)}")
    titles = SECTION_TITLES.get(lang, SECTION_TITLES["en"])
    c = profile.contact

    cv: dict = {"name": c.full_name}
    headline = (tailored.headline if tailored else profile.headline) or None
    if headline:
        cv["headline"] = headline
    if c.location:
        cv["location"] = c.location
    if c.email:
        cv["email"] = c.email
    if c.phone:
        cv["phone"] = c.phone
    if c.website:
        cv["website"] = c.website

    socials = []
    li = _social_username(c.linkedin, "linkedin.com")
    gh = _social_username(c.github, "github.com")
    if li:
        socials.append({"network": "LinkedIn", "username": li})
    if gh:
        socials.append({"network": "GitHub", "username": gh})
    if socials:
        cv["social_networks"] = socials

    sections: dict = {}

    summary = (tailored.summary if tailored else profile.summary) or None
    if summary:
        sections[titles["summary"]] = [summary]

    if tailored and tailored.skills:
        sections[titles["skills"]] = [
            {"label": s.label, "details": s.details} for s in tailored.skills
        ]
    elif profile.skills:
        sections[titles["skills"]] = [
            {"label": "Skills", "details": ", ".join(profile.skills)}
        ]

    experiences = []
    if tailored:
        for exp in tailored.experiences:
            entry: dict = {"company": exp.company, "position": exp.title}
            if exp.location:
                entry["location"] = exp.location
            start, end = to_rendercv_date(exp.start), to_rendercv_date(exp.end)
            if start:
                entry["start_date"] = start
            if end:
                entry["end_date"] = end
            if exp.bullets:
                entry["highlights"] = [b.text for b in exp.bullets]
            experiences.append(entry)
    else:
        for exp in profile.experiences:
            entry = {"company": exp.company, "position": exp.title}
            if exp.location:
                entry["location"] = exp.location
            start, end = to_rendercv_date(exp.start), to_rendercv_date(exp.end)
            if start:
                entry["start_date"] = start
            if end:
                entry["end_date"] = end
            if exp.bullets:
                entry["highlights"] = list(exp.bullets)
            experiences.append(entry)
    if experiences:
        sections[titles["experience"]] = experiences

    education = []
    for edu in profile.education:
        # RenderCV requires institution + area; our 'degree' text carries the field
        entry = {"institution": edu.institution, "area": edu.degree}
        year = to_rendercv_date(edu.year)
        if year:
            # int year renders as "2006"; the string "2006" would render "Jan 2006"
            entry["date"] = int(year) if re.fullmatch(r"\d{4}", year) else year
        education.append(entry)
    if education:
        sections[titles["education"]] = education

    if profile.certifications:
        sections[titles["certifications"]] = list(profile.certifications)
    if profile.languages:
        sections[titles["languages"]] = list(profile.languages)

    cv["sections"] = sections
    return {"cv": cv, "design": {"theme": theme}}


def render_pdf(data: dict, out_dir: str | Path, file_label: str = "resume") -> Path:
    """Compile a RenderCV data dict to PDF. Returns the PDF path."""
    from rendercv.renderer.pdf_png import generate_pdf
    from rendercv.renderer.typst import generate_typst
    from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model

    _ensure_typst_packages()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    yaml_str = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    input_path = out_dir / f"{file_label}.rendercv.yaml"
    input_path.write_text(yaml_str, encoding="utf-8")

    _, model = build_rendercv_dictionary_and_model(
        yaml_str,
        input_file_path=input_path,
        output_folder=str(out_dir),
        pdf_path=str(out_dir / f"{file_label}.pdf"),
        dont_generate_html=True,
        dont_generate_markdown=True,
        dont_generate_png=True,
    )
    typst_path = generate_typst(model)
    pdf_path = generate_pdf(model, typst_path)
    if pdf_path is None or not Path(pdf_path).exists():
        raise RuntimeError("RenderCV/Typst did not produce a PDF")
    return Path(pdf_path)
