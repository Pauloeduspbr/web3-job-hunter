"""CLI for the Web3 Job Tailor core.

    python -m web3_job_tailor.cli build-store <cv.pdf> [--vision] [--out path]
    python -m web3_job_tailor.cli tailor (--jd <file> | --jd-text "..." | stdin) [--store path] [--out-dir dir]

Outward-facing actions (applying to a job, pushing, etc.) are NOT done here —
the engine generates and shows the CV; submission is always manual.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import factstore, pipeline


def _read_jd(args) -> str:
    if args.jd:
        return Path(args.jd).read_text(encoding="utf-8")
    if args.jd_text:
        return args.jd_text
    sys.stderr.write(
        "Paste the job description, then send EOF "
        "(Windows: Ctrl+Z then Enter; Unix: Ctrl+D):\n"
    )
    return sys.stdin.read()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="web3-job-tailor", description="CV tailoring engine (Web3 Job Hunter)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build-store", help="Extract CV PDF -> fact store JSON (run once, then REVIEW it)")
    b.add_argument("pdf", help="Path to the CV PDF")
    b.add_argument("--vision", action="store_true", help="Send the PDF to the model directly (hard layouts)")
    b.add_argument("--out", default=None, help="Output path (default: data/cv_master.json)")

    t = sub.add_parser("tailor", help="Tailor the CV to a pasted job description")
    t.add_argument("--jd", help="Path to a file containing the job description")
    t.add_argument("--jd-text", help="Job description text inline")
    t.add_argument("--store", default=None, help="Fact store JSON path (default: data/cv_master.json)")
    t.add_argument("--out-dir", default="output", help="Directory for the tailored CV outputs")

    args = parser.parse_args(argv)

    if args.cmd == "build-store":
        profile, path, placeholders = pipeline.build_fact_store(
            args.pdf, use_vision=args.vision, out=args.out
        )
        print(f"Fact store written to {path}")
        print(f"  Experiences: {len(profile.experiences)} | Skills: {len(profile.skills)}")
        if placeholders:
            print("  WARNING — placeholders detected (fix before tailoring): " + ", ".join(placeholders))
        print("  REVIEW the JSON before tailoring — it is your single source of truth.")
        return 0

    if args.cmd == "tailor":
        jd = _read_jd(args)
        profile = factstore.load(args.store)
        result = pipeline.run(jd, profile=profile, out_dir=args.out_dir)

        m = result["match"]
        crit = result["critique"]
        print(f"Match score: {m.score}/100")
        print(f"  {m.rationale}")
        if m.gaps:
            print("  Gaps: " + ", ".join(m.gaps))
        print(
            f"Tailoring: {result['iterations']} iteration(s) | "
            f"approved={crit.approved} traceable={crit.traceable} "
            f"match_estimate={crit.match_estimate}"
        )
        if crit.issues:
            print("  Open critique issues: " + "; ".join(crit.issues))
        if result["glossary_missing"]:
            print("  WARNING — glossary terms altered in translation: " + ", ".join(result["glossary_missing"]))
        if result["ats_warnings"]:
            print("  ATS/QA: " + " | ".join(result["ats_warnings"]))
        print(f"\nOutputs:\n  {result['md_path']}\n  {result['docx_path']}")
        print("\nReview the CV; submission to the job is manual (project policy).")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
