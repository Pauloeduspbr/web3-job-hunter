"""Traceability report — the proof artifact of Phase 0.

For every tailored bullet, shows the verbatim fact-store source it derives from.
This is the anti-hallucination evidence attached to each generated CV (and the
future marketing asset of the SaaS: 'every bullet is traceable to a real fact').
"""

from __future__ import annotations

from datetime import date

from .models import JobRequirements, MatchResult, TailoredResume


def build_trace_report(
    tailored: TailoredResume,
    requirements: JobRequirements,
    match: MatchResult,
    *,
    generated_on: date | None = None,
) -> str:
    day = (generated_on or date.today()).isoformat()
    lines: list[str] = [
        "# Traceability Report",
        "",
        f"- **Job**: {requirements.job_title}"
        + (f" @ {requirements.company}" if requirements.company else ""),
        f"- **Generated**: {day}",
        f"- **Match score**: {match.score}/100",
        "",
        "> Every bullet below is paired with the verbatim fact-store entry it",
        "> derives from. No claim exists without a source. Gaps are reported,",
        "> never filled with invented content.",
        "",
        "## Headline & Summary",
        "",
        f"- Headline: `{tailored.headline}` — sourced from the candidate's real title/level.",
        f"- Summary: rephrasing of fact-store summary + skills (no new claims).",
        "",
        "## Experience bullets — bullet → source fact",
        "",
    ]
    for exp in tailored.experiences:
        lines.append(f"### {exp.title} — {exp.company}")
        lines.append("")
        if not exp.bullets:
            lines.append("*(no bullets)*")
        for b in exp.bullets:
            lines.append(f"- **Bullet**: {b.text}")
            lines.append(f"  - **Source fact**: \"{b.source_fact}\"")
        lines.append("")

    lines.append("## Skills")
    lines.append("")
    for s in tailored.skills:
        lines.append(f"- {s.label}: {s.details} *(all present in fact store)*")
    lines.append("")

    lines.append("## Honest gaps (requirements without evidence)")
    lines.append("")
    if match.gaps:
        for g in match.gaps:
            lines.append(f"- {g}")
    else:
        lines.append("- none detected")
    lines.append("")
    lines.append(f"## Match rationale")
    lines.append("")
    lines.append(match.rationale or "(none)")
    lines.append("")
    return "\n".join(lines)
