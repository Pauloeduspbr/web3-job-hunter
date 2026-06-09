"""Stage 1 — ingest a CV PDF.

Default path: PyMuPDF4LLM -> layout-aware markdown (best read-order for multi-column).
Fallback: pdfplumber (MIT) if PyMuPDF4LLM is not installed.
Vision path: structure.py can send the raw PDF to the model as a base64 document
block (robust for hard layouts / scanned CVs).
"""

from __future__ import annotations

import base64
from pathlib import Path


def pdf_to_markdown(pdf_path: str | Path) -> str:
    """Extract text preserving reading order, as markdown."""
    pdf_path = str(pdf_path)
    try:
        import pymupdf4llm  # type: ignore

        return pymupdf4llm.to_markdown(pdf_path)
    except ImportError:
        pass
    try:
        import pdfplumber  # type: ignore

        parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text(layout=True) or "")
        return "\n\n".join(parts)
    except ImportError as exc:
        raise RuntimeError(
            "No PDF extractor available. Install pymupdf4llm (recommended) or "
            "pdfplumber, or use the --vision path which sends the PDF to the model."
        ) from exc


def pdf_to_base64(pdf_path: str | Path) -> str:
    """Base64-encode a PDF for an Anthropic document content block."""
    return base64.standard_b64encode(Path(pdf_path).read_bytes()).decode("utf-8")
