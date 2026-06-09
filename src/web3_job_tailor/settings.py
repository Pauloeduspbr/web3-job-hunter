"""Configuration: model IDs per stage, paths, and tuning constants.

Model choice (decision D6 of the architecture doc): Haiku for cheap structured
extraction, Sonnet for nuance (tailoring / judge / translation). Override any of
them via env vars. Switch to claude-opus-4-8 for maximum quality at higher cost.
Model IDs are verified against the claude-api skill (cached 2026-05-26).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

# repo root = .../web3-job-hunter ; this file = src/web3_job_tailor/settings.py
ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = Path(os.environ.get("WJT_DATA_DIR", str(ROOT / "data")))


@dataclass(frozen=True)
class Settings:
    model_extract: str = os.environ.get("WJT_MODEL_EXTRACT", "claude-haiku-4-5")
    model_tailor: str = os.environ.get("WJT_MODEL_TAILOR", "claude-sonnet-4-6")
    model_judge: str = os.environ.get("WJT_MODEL_JUDGE", "claude-sonnet-4-6")
    model_translate: str = os.environ.get("WJT_MODEL_TRANSLATE", "claude-sonnet-4-6")
    fact_store_path: Path = DATA_DIR / "cv_master.json"
    match_target: int = 75          # Jobscan reference; tailoring aims for >= this
    max_refine_iters: int = 3       # Self-Refine loop cap


settings = Settings()


def load_glossary() -> dict:
    """Load the DO-NOT-TRANSLATE list and PT->EN role map."""
    path = CONFIG_DIR / "glossary.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
