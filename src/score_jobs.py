"""Score scraped jobs against the candidate profile (config/profile.yaml).

Deterministic matching: extracts skills demanded by the job description using a
canonical alias lexicon, then computes weighted coverage against the profile.
Outputs score (0-100), matched skills, gaps, and bonus/penalty evidence —
the gap analysis feeds the resume tailoring step.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone

from config import DATA_RAW, DATA_SCORED, ensure_dirs, load_profile

# canonical skill -> regex aliases found in job descriptions
SKILL_LEXICON: dict[str, list[str]] = {
    "python": [r"python"],
    "sql": [r"\bsql\b", r"\bt-sql\b", r"\bpl/?sql\b"],
    "pyspark": [r"pyspark", r"py-spark"],
    "spark": [r"\bspark\b", r"spark\s*sql", r"structured streaming"],
    "scala": [r"\bscala\b"],
    "shell": [r"shell script", r"\bbash\b"],
    "airflow": [r"airflow", r"\bmwaa\b", r"cloud composer"],
    "dbt": [r"\bdbt\b"],
    "kafka": [r"kafka", r"\bmsk\b", r"event streaming"],
    "nifi": [r"\bnifi\b"],
    "databricks": [r"databricks"],
    "hive": [r"\bhive\b"],
    "emr": [r"\bemr\b"],
    "emr_serverless": [r"emr serverless"],
    "hadoop": [r"hadoop", r"\bhdfs\b"],
    "trino": [r"\btrino\b", r"\bpresto\b"],
    "s3": [r"\bs3\b"],
    "glue": [r"\bglue\b"],
    "athena": [r"athena"],
    "redshift": [r"redshift"],
    "lambda": [r"\blambda\b"],
    "kinesis": [r"kinesis"],
    "lake_formation": [r"lake formation"],
    "step_functions": [r"step functions"],
    "aws": [r"\baws\b", r"amazon web services"],
    "azure": [r"\bazure\b"],
    "data_factory": [r"data factory", r"\badf\b"],
    "synapse": [r"synapse"],
    "fabric": [r"microsoft fabric"],
    "gcp": [r"\bgcp\b", r"google cloud"],
    "bigquery": [r"bigquery", r"big query"],
    "dataproc": [r"dataproc"],
    "dataflow": [r"dataflow"],
    "snowflake": [r"snowflake"],
    "postgresql": [r"postgres(?:ql)?"],
    "oracle": [r"\boracle\b"],
    "sql_server": [r"sql server"],
    "mysql": [r"mysql"],
    "teradata": [r"teradata"],
    "mongodb": [r"mongo\s?db"],
    "cassandra": [r"cassandra"],
    "dynamodb": [r"dynamo\s?db"],
    "delta_lake": [r"delta lake", r"delta tables?"],
    "iceberg": [r"iceberg"],
    "hudi": [r"\bhudi\b"],
    "parquet": [r"parquet"],
    "medallion": [r"medallion", r"bronze.{0,15}silver.{0,15}gold", r"lakehouse"],
    "data_lake": [r"data ?lake"],
    "data_warehouse": [r"data ?warehous", r"\bdwh?\b"],
    "dimensional_modeling": [r"dimensional model", r"star schema", r"kimball", r"data model(?:l?ing)?"],
    "data_mesh": [r"data mesh"],
    "data_vault": [r"data vault"],
    "cdc": [r"\bcdc\b", r"change data capture", r"debezium"],
    "event_driven": [r"event[- ]driven"],
    "docker": [r"docker", r"container"],
    "kubernetes": [r"kubernetes", r"\bk8s\b", r"\beks\b"],
    "terraform": [r"terraform", r"\biac\b", r"infrastructure as code"],
    "ansible": [r"ansible"],
    "ci_cd": [r"ci/?cd", r"github actions", r"gitlab ci", r"jenkins"],
    "git": [r"\bgit\b"],
    "data_quality": [r"data quality", r"great expectations", r"\bdeequ\b", r"quality checks?"],
    "data_governance": [r"governance", r"data catalog", r"lineage", r"unity catalog"],
    "lgpd_pii": [r"\bpii\b", r"\bgdpr\b", r"\blgpd\b", r"data privacy"],
    "power_bi": [r"power ?bi"],
    "tableau": [r"tableau"],
    "looker": [r"looker"],
    "grafana": [r"grafana"],
    "streaming": [r"streaming", r"real[- ]time", r"flink"],
    "etl": [r"\betl\b", r"\belt\b", r"data pipeline"],
    "machine_learning": [r"machine learning", r"\bml\b", r"mlops"],
    "api_integration": [r"rest(?:ful)? api", r"api integration"],
    # web3-specific (portfolio covers these even if profile weight is implicit)
    "blockchain_data": [r"blockchain", r"on[- ]chain", r"web3", r"crypto", r"defi",
                        r"smart contract data", r"\bevm\b", r"solana", r"ethereum", r"dune"],
}

WEB3_HINTS = re.compile(
    r"blockchain|web3|crypto|defi|digital assets?|exchange|on[- ]chain|token|stablecoin|fintech|payments?",
    re.I,
)
REMOTE_HINTS = re.compile(r"\bremote\b|\bremoto\b|work from home|anywhere|distributed team|home office", re.I)
HYBRID_HINTS = re.compile(r"\bhybrid\b|\bh[ií]brid[oa]\b", re.I)
ONSITE_HINTS = re.compile(r"\bon[- ]?site\b|in[- ]office|\bpresencial\b", re.I)


def classify_workplace(job: dict, text: str) -> str:
    """remote | hybrid | onsite | unknown — explicit field wins over text hints."""
    explicit = str(job.get("workplace") or "").lower()
    if explicit in ("remote", "hybrid", "onsite"):
        return explicit
    if HYBRID_HINTS.search(text):
        return "hybrid"
    if ONSITE_HINTS.search(text):
        return "onsite"
    if REMOTE_HINTS.search(text):
        return "remote"
    return "unknown"


def _flatten_profile_skills(profile: dict) -> dict[str, int]:
    flat: dict[str, int] = {}
    for _category, skills in profile.get("skills", {}).items():
        for name, meta in skills.items():
            flat[name] = int(meta.get("weight", 1)) if isinstance(meta, dict) else 1
    # blockchain knowledge is evidenced by the portfolio, not work history
    flat.setdefault("blockchain_data", 2)
    flat.setdefault("streaming", 2)
    flat.setdefault("etl", 3)
    flat.setdefault("api_integration", 2)
    flat.setdefault("dataflow", 1)
    flat.setdefault("machine_learning", 1)
    return flat


def extract_demanded_skills(text: str) -> list[str]:
    """Skills the job description actually mentions."""
    found = []
    lower = text.lower()
    for skill, patterns in SKILL_LEXICON.items():
        if any(re.search(p, lower, re.I) for p in patterns):
            found.append(skill)
    return found


def score_job(job: dict, profile: dict) -> dict:
    """Returns scoring record with match %, gaps and evidence."""
    description = str(job.get("description", "") or job.get("descriptionText", ""))
    text_parts = [
        str(job.get("title", "")),
        str(job.get("location", "") or ""),
        description,
        " ".join(map(str, job.get("skills", []) or [])),
    ]
    text = "\n".join(text_parts)
    workplace = classify_workplace(job, text)

    profile_skills = _flatten_profile_skills(profile)
    demanded = extract_demanded_skills(text)

    matched = [s for s in demanded if s in profile_skills]
    gaps = [s for s in demanded if s not in profile_skills]

    demanded_weight = sum(profile_skills.get(s, 2) for s in demanded) or 1
    matched_weight = sum(profile_skills[s] for s in matched)
    skill_score = 100.0 * matched_weight / demanded_weight

    bonuses, penalties = [], []
    score = skill_score * 0.8  # skills = 80% of final score

    title = str(job.get("title", "")).lower()
    target_roles = [r.lower() for r in profile["target"]["roles"]]
    if any(r in title for r in target_roles):
        score += 10
        bonuses.append("title matches target role (+10)")
    for excluded in profile["target"]["excluded_roles"]:
        if excluded.lower() in title:
            score -= 40
            penalties.append(f"excluded role '{excluded}' (-40)")

    if WEB3_HINTS.search(text):
        score += 5
        bonuses.append("web3/fintech domain (+5)")
    if workplace == "remote":
        score += 5
        bonuses.append("remote (+5)")
    elif workplace in ("hybrid", "onsite"):
        score -= 15
        penalties.append(f"{workplace} (-15)")

    return {
        "job_id": job.get("id") or job.get("jobId") or job.get("url", "unknown"),
        "title": job.get("title"),
        "company": job.get("companyName") or job.get("company"),
        "url": job.get("url") or job.get("link"),
        "location": job.get("location"),
        "salary": job.get("salary") or job.get("salaryInfo"),
        "score": round(max(0.0, min(100.0, score)), 1),
        "skill_score": round(skill_score, 1),
        "workplace": workplace,
        "needs_detail": not description.strip(),
        "demanded_skills": demanded,
        "matched_skills": matched,
        "gap_skills": gaps,
        "bonuses": bonuses,
        "penalties": penalties,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run(min_score: float = 60.0) -> list[dict]:
    ensure_dirs()
    profile = load_profile()
    results = []
    # mtime order, NOT name order: lexicographic puts linkedin_detail_* before
    # linkedin_search_* and a stale listing would overwrite fresh enriched detail
    for raw_file in sorted(DATA_RAW.glob("*.json"), key=lambda f: f.stat().st_mtime):
        jobs = json.loads(raw_file.read_text(encoding="utf-8"))
        if isinstance(jobs, dict):
            jobs = [jobs]
        for job in jobs:
            results.append(score_job(job, profile))

    # dedup: same job in multiple raw files — full detail beats listing-only;
    # among equals, the most recent (later file) wins
    best: dict[str, dict] = {}
    for r in results:
        key = str(r.get("job_id") or r.get("url"))
        cur = best.get(key)
        if cur is None or (not r.get("needs_detail")) or cur.get("needs_detail"):
            best[key] = r
    results = list(best.values())

    results.sort(key=lambda r: r["score"], reverse=True)
    out = DATA_SCORED / "scored_jobs.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)

    print(f"Scored {len(results)} job(s) -> {out}")
    for r in results:
        flag = "APPLY" if r["score"] >= min_score else "skip "
        print(f"  [{flag}] {r['score']:5.1f}  {r['title']} @ {r['company']}")
    return results


if __name__ == "__main__":
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    run(threshold)
