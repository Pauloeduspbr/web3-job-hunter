"""Export the fact store to JSON Resume v1.0.0 (https://jsonresume.org/schema).

Interoperability/no-lock-in deliverable of Phase 0: the canonical fact store
maps 1:1 onto the open schema (basics/work/education/skills/languages/
certificates). Dates converted to ISO (YYYY-MM / YYYY).
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import ResumeProfile
from .render import to_rendercv_date  # same ISO-ish conversion (YYYY-MM / YYYY)

SCHEMA_URL = "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"


def _iso(value: str | None) -> str | None:
    d = to_rendercv_date(value)
    return None if d in (None, "present") else d


def to_jsonresume(profile: ResumeProfile) -> dict:
    c = profile.contact
    basics: dict = {"name": c.full_name}
    if profile.headline:
        basics["label"] = profile.headline
    if c.email:
        basics["email"] = c.email
    if c.phone:
        basics["phone"] = c.phone
    if c.website:
        basics["url"] = c.website
    if profile.summary:
        basics["summary"] = profile.summary
    if c.location:
        basics["location"] = {"address": c.location}
    profiles = []
    if c.linkedin:
        profiles.append({"network": "LinkedIn", "url": c.linkedin})
    if c.github:
        profiles.append({"network": "GitHub", "url": c.github})
    if profiles:
        basics["profiles"] = profiles

    work = []
    for exp in profile.experiences:
        item: dict = {"name": exp.company, "position": exp.title}
        if exp.location:
            item["location"] = exp.location
        if _iso(exp.start):
            item["startDate"] = _iso(exp.start)
        if _iso(exp.end):
            item["endDate"] = _iso(exp.end)
        if exp.bullets:
            item["highlights"] = list(exp.bullets)
        if exp.tech:
            item["summary"] = "Tech: " + ", ".join(exp.tech)
        work.append(item)

    education = []
    for edu in profile.education:
        item = {"institution": edu.institution, "area": edu.degree}
        if _iso(edu.year):
            item["endDate"] = _iso(edu.year)
        education.append(item)

    doc: dict = {"$schema": SCHEMA_URL, "basics": basics}
    if work:
        doc["work"] = work
    if education:
        doc["education"] = education
    if profile.skills:
        doc["skills"] = [{"name": s} for s in profile.skills]
    if profile.languages:
        doc["languages"] = [{"language": lang} for lang in profile.languages]
    if profile.certifications:
        doc["certificates"] = [{"name": cert} for cert in profile.certifications]
    return doc


def export_jsonresume(profile: ResumeProfile, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(to_jsonresume(profile), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out
