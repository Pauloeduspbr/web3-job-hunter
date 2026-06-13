"""Web3 Job Hunter — FastAPI backend.

Wraps the existing pipeline (src/) with a REST API consumed by the React
frontend (frontend/). Run:

    python -m uvicorn backend.app:app --reload --port 8000
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import (  # noqa: E402
    DATA_RAW, DATA_SCORED, LINKS_DIR, OUTPUT_ANALYSIS, OUTPUT_RESUMES,
    PROFILE_PATH, ensure_dirs,
)
from backend import llm  # noqa: E402
from backend.exporters import markdown_to_docx, markdown_to_pdf  # noqa: E402

CURRICULO_DIR = PROJECT_ROOT / "Curriculo"
DEFAULT_BASE_RESUME = PROJECT_ROOT / "Resume_Paulo_Eduardo_Web3_v2.md"

app = FastAPI(title="Web3 Job Hunter", version="1.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# one Apify run at a time per stage — re-clicking must not start a second paid run
_stage_locks: dict[str, threading.Lock] = {}
_running_stages: set[str] = set()

# application tracking: job_id -> {status, updated_at}. Lives OUTSIDE
# scored_jobs.json because that file is rebuilt on every re-score.
STATUS_FILE = PROJECT_ROOT / "data" / "jobs" / "job_status.json"
_status_lock = threading.Lock()
VALID_STATUSES = ("new", "viewed", "applied")


def _load_statuses() -> dict:
    if not STATUS_FILE.exists():
        return {}
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_status(job_id: str, status: str) -> dict:
    with _status_lock:
        statuses = _load_statuses()
        if status == "new":
            statuses.pop(job_id, None)
        else:
            statuses[job_id] = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATUS_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(statuses, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(STATUS_FILE)
    return statuses


def _require_apify() -> None:
    """Apify-backed stages need a token — fail with a clear, actionable 400
    instead of a generic 500 deep inside the actor client."""
    if not os.getenv("APIFY_TOKEN"):
        raise HTTPException(
            400,
            "APIFY_TOKEN ausente. Copie .env.example para .env e defina seu token "
            "(console.apify.com/account/integrations) para buscar/detalhar vagas do LinkedIn.",
        )


def _run_stage(name: str, fn):
    lock = _stage_locks.setdefault(name, threading.Lock())
    if not lock.acquire(blocking=False):
        raise HTTPException(409, f"stage '{name}' is already running")
    _running_stages.add(name)
    try:
        return fn()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"stage '{name}' failed: {exc}")
    finally:
        _running_stages.discard(name)
        lock.release()


class SearchParams(BaseModel):
    keywords: str = "data engineer"
    location: str = "United States"
    max_jobs: int = 50
    published_within: str = "week"
    include_description: bool = True


class LinksPayload(BaseModel):
    urls: list[str]


class GeneratePayload(BaseModel):
    job_id: str | None = None
    job_index: int | None = None


def _safe_name(name: str) -> str:
    """Canonical basename only — no separators, drive prefixes or dot dirs."""
    clean = Path(name.replace("\\", "/")).name
    if not clean or ":" in clean or clean in (".", ".."):
        raise HTTPException(400, "invalid file name")
    return clean


def _load_scored() -> list[dict]:
    scored_file = DATA_SCORED / "scored_jobs.json"
    if not scored_file.exists():
        return []
    try:
        return json.loads(scored_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _base_resume_path() -> Path:
    """Most recent uploaded .md/.txt in Curriculo/ wins; fallback to Resume v2."""
    candidates = []
    if CURRICULO_DIR.exists():
        candidates = sorted(
            (f for f in CURRICULO_DIR.iterdir() if f.suffix.lower() in (".md", ".txt")),
            key=lambda f: f.stat().st_mtime, reverse=True,
        )
    return candidates[0] if candidates else DEFAULT_BASE_RESUME


# ---------- status / jobs ----------

@app.get("/api/status")
def status():
    return {
        "llm_mode": llm.get_mode(),
        "apify_ready": bool(os.getenv("APIFY_TOKEN")),
        "raw_files": len(list(DATA_RAW.glob("*.json"))),
        "scored_jobs": len(_load_scored()),
        "resumes": len(list(OUTPUT_RESUMES.glob("*.md"))),
        "briefs": len(list(OUTPUT_ANALYSIS.glob("brief_*.md"))),
        "links": sum(1 for f in LINKS_DIR.glob("*.txt") for line in f.read_text(encoding="utf-8").splitlines() if line.strip()),
        "running_stages": sorted(_running_stages),
        "base_resume": _base_resume_path().name,
    }


@app.get("/api/jobs")
def list_jobs():
    jobs = _load_scored()
    statuses = _load_statuses()
    for j in jobs:
        entry = statuses.get(str(j.get("job_id")))
        j["status"] = entry["status"] if entry else "new"
        j["status_updated_at"] = entry.get("updated_at") if entry else None
    return jobs


class StatusPayload(BaseModel):
    job_id: str
    status: str


@app.post("/api/jobs/status")
def set_job_status(payload: StatusPayload):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(400, f"status must be one of {VALID_STATUSES}")
    _save_status(str(payload.job_id), payload.status)
    return {"job_id": payload.job_id, "status": payload.status}


# ---------- pipeline stages ----------

def _auto_score() -> int:
    """Re-score after every collection so new jobs show up in the UI at once."""
    from score_jobs import run as score_run
    lock = _stage_locks.setdefault("score", threading.Lock())
    with lock:
        return len(score_run())


@app.post("/api/pipeline/scrape")
def run_scrape():
    _require_apify()
    from scrape_jobs import scrape_links
    jobs = _run_stage("scrape", scrape_links)
    return {"scraped": len(jobs), "scored": _auto_score()}


@app.post("/api/pipeline/search")
def run_search(params: SearchParams):
    _require_apify()
    from scrape_jobs import search_jobs
    jobs = _run_stage("search", lambda: search_jobs(
        params.keywords, params.location, params.max_jobs, params.published_within,
        include_description=params.include_description))
    return {"found": len(jobs), "scored": _auto_score()}


@app.post("/api/pipeline/boards")
def run_boards():
    from free_boards import run as boards_run
    jobs = _run_stage("boards", boards_run)
    return {"found": len(jobs), "scored": _auto_score()}


@app.post("/api/pipeline/score")
def run_score():
    from score_jobs import run as score_run
    results = _run_stage("score", score_run)
    return {"scored": len(results)}


class EnrichPayload(BaseModel):
    job_ids: list[str]


@app.post("/api/jobs/enrich")
def enrich(payload: EnrichPayload):
    """Detail-scrape LinkedIn jobs (description + remote/hybrid). ~$0.005/job."""
    _require_apify()
    valid = [str(j) for j in payload.job_ids if str(j).isdigit()]
    if not valid:
        raise HTTPException(400, "no valid LinkedIn job ids (numeric) to enrich")
    from scrape_jobs import enrich_jobs
    jobs = _run_stage("enrich", lambda: enrich_jobs(valid))
    return {"enriched": len(jobs), "scored": _auto_score()}


# ---------- inputs: links + resume upload ----------

@app.post("/api/links")
def add_links(payload: LinksPayload):
    ensure_dirs()
    LINKS_DIR.mkdir(exist_ok=True)
    target = LINKS_DIR / "from_app.txt"
    existing = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
    added = [u.strip() for u in payload.urls if u.strip() and u.strip() not in existing]
    if added:
        with open(target, "a", encoding="utf-8") as f:
            f.write("\n".join(added) + "\n")
    return {"added": len(added), "file": str(target)}


@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith((".pdf", ".md", ".docx", ".txt")):
        raise HTTPException(400, "Allowed: .pdf .md .docx .txt")
    CURRICULO_DIR.mkdir(exist_ok=True)
    dest = (CURRICULO_DIR / _safe_name(file.filename)).resolve()
    if CURRICULO_DIR.resolve() not in dest.parents:
        raise HTTPException(400, "invalid file name")
    dest.write_bytes(await file.read())
    return {"saved": dest.name, "size": dest.stat().st_size}


@app.get("/api/resume/files")
def list_resume_files():
    if not CURRICULO_DIR.exists():
        return []
    return [{"name": f.name, "size": f.stat().st_size} for f in CURRICULO_DIR.iterdir() if f.is_file()]


# ---------- briefs + CV generation ----------

@app.post("/api/cv/generate")
def generate_cv(payload: GeneratePayload):
    scored = _load_scored()
    if not scored:
        raise HTTPException(409, "No scored jobs — run the score stage first")

    # identity contract: job_id wins over positional index (list reorders on re-score)
    if payload.job_id:
        index = next((i for i, j in enumerate(scored)
                      if str(j.get("job_id")) == str(payload.job_id)), None)
        if index is None:
            raise HTTPException(404, "job not found — refresh the list and try again")
    else:
        index = payload.job_index or 0
        if not 0 <= index < len(scored):
            raise HTTPException(404, f"job index {index} out of range")

    from tailor_resume import run as brief_run
    try:
        brief_path = Path(brief_run(index))
    except ValueError as exc:
        raise HTTPException(409, str(exc))

    result = {"brief": brief_path.name, "mode": llm.get_mode(), "job": scored[index].get("title")}

    if llm.get_mode() == "manual":
        result["message"] = (
            "Brief gerado. Sem ANTHROPIC_API_KEY no .env: gere o CV no Claude Code com "
            f"'Gere o CV alinhado usando output/analysis/{brief_path.name}'."
        )
        return result

    base_resume = _base_resume_path()
    try:
        resume_md = llm.generate_cv_via_api(
            brief_path.read_text(encoding="utf-8"),
            base_resume.read_text(encoding="utf-8"),
            PROFILE_PATH.read_text(encoding="utf-8"),
        )
    except Exception as exc:
        raise HTTPException(502, f"Claude API error: {exc}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"^brief_|\.md$", "", brief_path.name)
    out = OUTPUT_RESUMES / f"Resume_{slug}_{stamp}.md"
    out.write_text(resume_md, encoding="utf-8")
    result["resume"] = out.name
    result["base_resume"] = base_resume.name
    result["message"] = f"CV gerado via Claude API (base: {base_resume.name})."
    return result


@app.get("/api/briefs")
def list_briefs():
    return [{"name": f.name, "modified": f.stat().st_mtime} for f in sorted(OUTPUT_ANALYSIS.glob("brief_*.md"))]


@app.get("/api/resumes")
def list_resumes():
    return [{"name": f.name, "modified": f.stat().st_mtime} for f in sorted(OUTPUT_RESUMES.glob("*.md"))]


# ---------- downloads ----------

@app.get("/api/download/resume/{name}")
def download_resume(name: str, fmt: str = "md"):
    md_path = OUTPUT_RESUMES / _safe_name(name)
    if not md_path.exists():
        raise HTTPException(404, "resume not found")
    if fmt == "md":
        return FileResponse(md_path, filename=md_path.name, media_type="text/markdown")
    if fmt == "docx":
        docx_path = md_path.with_suffix(".docx")
        # regenerate only when the markdown is newer (also avoids write/stream races)
        if not docx_path.exists() or docx_path.stat().st_mtime < md_path.stat().st_mtime:
            markdown_to_docx(md_path, docx_path)
        return FileResponse(
            docx_path, filename=docx_path.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    if fmt == "pdf":
        pdf_path = md_path.with_suffix(".pdf")
        if not pdf_path.exists() or pdf_path.stat().st_mtime < md_path.stat().st_mtime:
            markdown_to_pdf(md_path, pdf_path)
        return FileResponse(pdf_path, filename=pdf_path.name, media_type="application/pdf")
    raise HTTPException(400, "fmt must be md, docx or pdf")


@app.get("/api/download/brief/{name}")
def download_brief(name: str):
    path = OUTPUT_ANALYSIS / _safe_name(name)
    if not path.exists():
        raise HTTPException(404, "brief not found")
    return FileResponse(path, filename=path.name, media_type="text/markdown")


# ---------- static frontend (production build) ----------

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
