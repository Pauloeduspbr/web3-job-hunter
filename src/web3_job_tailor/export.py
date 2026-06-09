"""Stage 8 — export ATS-safe outputs + lightweight QA.

Renders the tailored markdown to a single-column DOCX (legacy ATS parse DOCX
best) and writes the markdown alongside. QA warns on tables/images that scramble
ATS parsers. PDF export is optional (WeasyPrint) and left to the caller.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import JobRequirements

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"\*(.+?)\*")
_CODE = re.compile(r"`(.+?)`")
_LINK = re.compile(r"\[(.+?)\]\((.+?)\)")


def _strip_md(text: str) -> str:
    text = _LINK.sub(r"\1 (\2)", text)
    text = _BOLD.sub(r"\1", text)
    text = _ITALIC.sub(r"\1", text)
    text = _CODE.sub(r"\1", text)
    return text


def to_markdown_file(markdown: str, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    return out


def to_docx(markdown: str, out_path: str | Path) -> Path:
    from docx import Document  # python-docx

    doc = Document()
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("# "):
            doc.add_heading(_strip_md(line[2:].strip()), level=0)
        elif line.startswith("## "):
            doc.add_heading(_strip_md(line[3:].strip()), level=1)
        elif line.startswith("### "):
            doc.add_heading(_strip_md(line[4:].strip()), level=2)
        elif line.startswith(("- ", "* ")):
            doc.add_paragraph(_strip_md(line[2:].strip()), style="List Bullet")
        else:
            doc.add_paragraph(_strip_md(line))
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def qa(markdown: str, requirements: JobRequirements) -> list[str]:
    """ATS hygiene checks on the generated markdown."""
    warnings: list[str] = []
    if re.search(r"\|.+\|", markdown):
        warnings.append("Possible table detected — ATS parsers may scramble it; use single-column text.")
    if "![" in markdown:
        warnings.append("Image detected — remove it; ATS cannot read images.")
    low = markdown.lower()
    missing = [s for s in requirements.hard_skills if s and s.lower() not in low]
    if missing:
        warnings.append(
            "Hard skills required by the job and absent from the output (real gaps, do not fabricate): "
            + ", ".join(missing)
        )
    return warnings
