"""Web3 Job Tailor — tailoring engine for Paulo's CV.

Core pipeline (stages 1-2 + 6-7-8 of docs/motor-cv-tailor-arquitetura.md):
ingest PDF -> structure into an immutable fact store -> match against a pasted
job description -> tailor (RAG-grounded + Self-Refine, never invents) ->
translate/localize -> export ATS-safe DOCX/Markdown.
"""

__version__ = "0.1.0"
