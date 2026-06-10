"""Generate a tailoring brief for a scored job.

The brief (output/analysis/) contains everything needed to produce a
job-aligned resume: demanded skills, matches, gaps, ATS keywords and the
candidate evidence (achievements/projects) most relevant to the posting.

The final resume text is produced by the LLM step (Claude Code) reading the
brief + base resume — see README_PIPELINE.md. This keeps generation quality
high without hardcoding an extra API dependency.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone

from config import DATA_SCORED, OUTPUT_ANALYSIS, PROJECT_ROOT, ensure_dirs, load_profile

BASE_RESUME = PROJECT_ROOT / "Resume_Paulo_Eduardo_Web3_v2.md"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")[:60]


def _relevant_evidence(profile: dict, matched_skills: list[str]) -> dict:
    """Pick achievements/projects whose text mentions any matched skill."""
    matched_terms = [s.replace("_", " ") for s in matched_skills]

    def hits(text: str) -> int:
        lower = text.lower()
        return sum(1 for t in matched_terms if t in lower)

    achievements = sorted(profile.get("achievements", []), key=hits, reverse=True)
    projects = sorted(
        profile.get("portfolio", []),
        key=lambda p: hits(json.dumps(p).lower()),
        reverse=True,
    )
    return {"achievements": achievements[:6], "projects": projects}


def build_brief(scored_job: dict, raw_job: dict | None = None) -> str:
    profile = load_profile()
    evidence = _relevant_evidence(profile, scored_job.get("matched_skills", []))
    description = ""
    if raw_job:
        description = str(
            raw_job.get("description") or raw_job.get("descriptionText") or ""
        )

    lines = [
        f"# Tailoring Brief — {scored_job.get('title')} @ {scored_job.get('company')}",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Job URL: {scored_job.get('url')}",
        f"- Match score: {scored_job.get('score')} (skills: {scored_job.get('skill_score')})",
        f"- Location/Salary: {scored_job.get('location')} | {scored_job.get('salary')}",
        "",
        "## ATS keywords to mirror verbatim in the resume",
        "",
    ]
    lines += [f"- {s.replace('_', ' ')}" for s in scored_job.get("demanded_skills", [])]
    lines += [
        "",
        "## Matched skills (lead with these — candidate has proof)",
        "",
    ]
    lines += [f"- {s.replace('_', ' ')}" for s in scored_job.get("matched_skills", [])]
    lines += [
        "",
        "## Gap skills (do NOT fabricate; mitigate via adjacent experience or portfolio)",
        "",
    ]
    lines += [f"- {s.replace('_', ' ')}" for s in scored_job.get("gap_skills", []) or ["(none)"]]
    lines += [
        "",
        "## Most relevant candidate evidence",
        "",
        "### Achievements (quantified)",
    ]
    lines += [f"- {a}" for a in evidence["achievements"]]
    lines += ["", "### Portfolio projects"]
    for p in evidence["projects"]:
        lines.append(f"- **{p['name']}** ({p['url']}): {p['proof']}")
    lines += [
        "",
        "## Generation instructions (for the LLM step)",
        "",
        f"1. Base resume: `{BASE_RESUME.name}` — keep structure, contacts and truthfulness.",
        "2. Rewrite PROFESSIONAL SUMMARY mirroring the job title and top 5 demanded skills.",
        "3. Reorder TECHNICAL SKILLS so matched/demanded skills appear first, using the",
        "   job's exact terminology (ATS keyword mirroring).",
        "4. In each experience entry, surface bullets that prove the demanded skills;",
        "   keep quantified results. Never invent experience for gap skills.",
        "5. For gap skills, reference the closest adjacent experience or portfolio project.",
        "6. Output: single-column Markdown, standard section headers, max 2 pages,",
        "   en-US, ATS-safe (no tables/images/columns).",
        "",
        "## Full job description (reference)",
        "",
        description[:8000] if description else "(rescrape or open the job URL)",
    ]
    return "\n".join(lines)


def run(job_index: int = 0) -> str:
    """Build brief for the Nth best scored job."""
    ensure_dirs()
    scored_file = DATA_SCORED / "scored_jobs.json"
    if not scored_file.exists():
        raise ValueError("No scored jobs. Run score_jobs.py first.")
    scored = json.loads(scored_file.read_text(encoding="utf-8"))
    if not scored:
        raise ValueError("No scored jobs. Run score_jobs.py first.")
    if not 0 <= job_index < len(scored):
        raise ValueError(f"job_index {job_index} out of range (0-{len(scored) - 1})")
    job = scored[job_index]

    raw_job = None
    from config import DATA_RAW
    for raw_file in DATA_RAW.glob("*.json"):
        items = json.loads(raw_file.read_text(encoding="utf-8"))
        if isinstance(items, dict):
            items = [items]
        for item in items:
            if (item.get("url") or item.get("link")) == job.get("url"):
                raw_job = item
                break

    brief = build_brief(job, raw_job)
    out = OUTPUT_ANALYSIS / f"brief_{_slug(job.get('company') or 'job')}_{_slug(job.get('title') or '')}.md"
    out.write_text(brief, encoding="utf-8")
    print(f"Brief -> {out}")
    return str(out)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
