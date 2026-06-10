"""Web3 Job Hunter — pipeline runner.

Stages (Anthropic 'Building Effective Agents' prompt-chaining pattern):
  1. scrape   — fetch job postings (links in Links_Empregos/ and/or keyword search)
  2. score    — match postings against config/profile.yaml
  3. brief    — build tailoring brief for the top job(s)
  4. (LLM)    — Claude Code generates the tailored resume from the brief

Usage:
  python main.py scrape            # scrape links from Links_Empregos/*.txt (Apify, ~$0.005/job)
  python main.py search            # keyword search via own Apify actor (compute units)
  python main.py boards            # free public sources: Greenhouse/Ashby/Lever/RemoteOK/RSS ($0)
  python main.py score [min]      # score raw jobs (default threshold 60)
  python main.py brief [index]    # brief for Nth best job (default 0)
  python main.py all               # scrape -> boards -> score -> brief
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd in ("scrape", "all"):
        from scrape_jobs import scrape_links
        scrape_links()
    if cmd == "search":
        from scrape_jobs import search_jobs
        search_jobs()
    if cmd in ("boards", "all"):
        from free_boards import run as boards_run
        boards_run()
    if cmd in ("score", "all"):
        from score_jobs import run as score_run
        score_run(float(arg) if cmd == "score" and arg else 60.0)
    if cmd in ("brief", "all"):
        from tailor_resume import run as brief_run
        brief_run(int(arg) if cmd == "brief" and arg else 0)


if __name__ == "__main__":
    main()
