"""Central config: loads .env, profile.yaml and resolves project paths."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "jobs" / "raw"
DATA_SCORED = PROJECT_ROOT / "data" / "jobs" / "scored"
OUTPUT_RESUMES = PROJECT_ROOT / "output" / "resumes"
OUTPUT_ANALYSIS = PROJECT_ROOT / "output" / "analysis"
LINKS_DIR = PROJECT_ROOT / "Links_Empregos"
PROFILE_PATH = PROJECT_ROOT / "config" / "profile.yaml"

load_dotenv(PROJECT_ROOT / ".env")


def get_apify_token() -> str:
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN not found. Copy .env.example to .env and set your token."
        )
    return token


def load_profile() -> dict:
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dirs() -> None:
    for d in (DATA_RAW, DATA_SCORED, OUTPUT_RESUMES, OUTPUT_ANALYSIS):
        d.mkdir(parents=True, exist_ok=True)
