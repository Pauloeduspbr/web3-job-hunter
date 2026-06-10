"""Export tailored resumes from Markdown to ATS-safe DOCX and PDF (single column).

DOCX parses best in strict ATS parsers (e.g. Workday); text-based PDF is the
safe format for Greenhouse/Lever/Ashby where a human also reads the document.
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Pt
from fpdf import FPDF

WIN_FONTS = Path("C:/Windows/Fonts")

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
CODE_RE = re.compile(r"`([^`]+)`")
NUMBERED_RE = re.compile(r"^\d+\.\s+")


def _clean_inline(text: str) -> str:
    """Strip markdown the DOCX renderer doesn't handle (links, italics, code)."""
    text = LINK_RE.sub(lambda m: f"{m.group(1)} ({m.group(2)})", text)
    text = CODE_RE.sub(r"\1", text)
    text = ITALIC_RE.sub(r"\1", text)
    return text


def _add_runs(paragraph, text: str) -> None:
    """Add text to a paragraph honoring **bold** markers."""
    text = _clean_inline(text)
    pos = 0
    for m in BOLD_RE.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        paragraph.add_run(m.group(1)).bold = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def markdown_to_docx(md_path: Path, out_path: Path) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for raw_line in md_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.strip() == "---":
            continue
        if line.startswith("# "):
            _add_runs(doc.add_heading("", level=0), line[2:].strip())
        elif line.startswith("## "):
            _add_runs(doc.add_heading("", level=1), line[3:].strip())
        elif line.startswith("### "):
            _add_runs(doc.add_heading("", level=2), line[4:].strip())
        elif line.startswith(("- ", "* ")):
            _add_runs(doc.add_paragraph(style="List Bullet"), line[2:].strip())
        elif NUMBERED_RE.match(line.strip()):
            _add_runs(doc.add_paragraph(style="List Number"),
                      NUMBERED_RE.sub("", line.strip()))
        else:
            _add_runs(doc.add_paragraph(), line.strip())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path


class _ResumePDF(FPDF):
    """Single-column, text-based PDF (Arial TTF for Unicode/accents)."""

    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(15, 12, 15)
        self.set_auto_page_break(auto=True, margin=12)
        self.add_font("Body", "", str(WIN_FONTS / "arial.ttf"))
        self.add_font("Body", "B", str(WIN_FONTS / "arialbd.ttf"))
        self.add_font("Body", "I", str(WIN_FONTS / "ariali.ttf"))
        self.add_page()

    def write_runs(self, text: str, size: float, bold_all: bool = False) -> None:
        """Write a line honoring **bold** markers, then line-break."""
        self.set_font("Body", "B" if bold_all else "", size)
        pos = 0
        for m in BOLD_RE.finditer(text):
            if m.start() > pos:
                self.write(size * 0.48, text[pos:m.start()])
            self.set_font("Body", "B", size)
            self.write(size * 0.48, m.group(1))
            self.set_font("Body", "B" if bold_all else "", size)
            pos = m.end()
        if pos < len(text):
            self.write(size * 0.48, text[pos:])
        self.ln(size * 0.55)


def markdown_to_pdf(md_path: Path, out_path: Path) -> Path:
    pdf = _ResumePDF()
    for raw_line in md_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.strip() == "---":
            pdf.ln(1.5)
            continue
        if line.startswith("# "):
            pdf.write_runs(_clean_inline(line[2:].strip()), 15.5, bold_all=True)
            pdf.ln(0.8)
        elif line.startswith("## "):
            pdf.ln(1.6)
            pdf.write_runs(_clean_inline(line[3:].strip()).upper(), 11.5, bold_all=True)
            pdf.ln(0.4)
        elif line.startswith("### "):
            pdf.ln(1.2)
            pdf.write_runs(_clean_inline(line[4:].strip()), 10.5, bold_all=True)
        elif line.startswith(("- ", "* ")):
            pdf.set_x(pdf.l_margin + 3.5)
            pdf.write_runs("• " + _clean_inline(line[2:].strip()), 9.3)
        elif NUMBERED_RE.match(line.strip()):
            pdf.set_x(pdf.l_margin + 3.5)
            pdf.write_runs("• " + _clean_inline(NUMBERED_RE.sub("", line.strip())), 9.3)
        else:
            pdf.write_runs(_clean_inline(line.strip()), 9.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path
