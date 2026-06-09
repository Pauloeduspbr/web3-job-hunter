"""Pydantic models = the contract for structured outputs and the fact store.

Kept flat and simple so the schema stays within structured-output limits
(the SDK strips unsupported constraints automatically).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Fact store (the single source of truth — extracted once from the CV PDF)
# ---------------------------------------------------------------------------
class Contact(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class Experience(BaseModel):
    title: str
    company: str
    start: Optional[str] = None   # "MM/YYYY" or "YYYY"
    end: Optional[str] = None     # "MM/YYYY", "YYYY", or "Present"
    location: Optional[str] = None
    bullets: list[str] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None


class ResumeProfile(BaseModel):
    contact: Contact
    headline: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Job parsing + matching
# ---------------------------------------------------------------------------
class JobRequirements(BaseModel):
    job_title: str
    company: Optional[str] = None
    target_language: str = Field(description="'en' or 'pt' — the posting's language")
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    min_years_experience: Optional[int] = None
    knockouts: list[str] = Field(
        default_factory=list,
        description="hard gates: visa/work auth, language, certifications, on-call",
    )
    keywords: list[str] = Field(
        default_factory=list, description="exact phrases an ATS/recruiter would search"
    )
    summary: str = ""


class MatchResult(BaseModel):
    score: int = Field(description="0-100 combined match score")
    must_haves_met: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    rationale: str = ""


# ---------------------------------------------------------------------------
# Tailoring critic (Self-Refine)
# ---------------------------------------------------------------------------
class Critique(BaseModel):
    traceable: bool = Field(
        description="False if ANY claim is not supported by the fact store"
    )
    match_estimate: int = Field(description="0-100 estimated match of the tailored CV")
    issues: list[str] = Field(default_factory=list)
    approved: bool = Field(
        description="True only if traceable AND match_estimate >= target AND ATS rules met"
    )
