"""Scrape job postings via Apify actors.

Actors (validated against the live Apify API on 2026-06-10):
- apimaestro/linkedin-job-detail  — job detail by job_id (from /jobs/view/<ID>/ URLs).
  PAY_PER_EVENT $0.005/result, no cookies. Batch up to 100 IDs.
- viralanalyzer/linkedin-jobs-multi-country — own-account actor, anonymous keyword
  search (keywords + location + maxJobs + publishedWithin). Costs compute units only.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone

from apify_client import ApifyClient

from config import DATA_RAW, LINKS_DIR, ensure_dirs, get_apify_token

ACTOR_JOB_DETAIL = "apimaestro/linkedin-job-detail"
ACTOR_JOB_SEARCH = "viralanalyzer/linkedin-jobs-multi-country"

LINKEDIN_JOB_ID = re.compile(r"linkedin\.com/jobs/view/(\d+)")


def _client() -> ApifyClient:
    return ApifyClient(get_apify_token())


def _normalize(item: dict) -> dict:
    """Map actor output fields into the pipeline's canonical job schema."""
    # apimaestro/linkedin-job-detail nests data under job_info/company_info/apply_details
    if "job_info" in item:
        ji = item.get("job_info") or {}
        ci = item.get("company_info") or {}
        ad = item.get("apply_details") or {}
        location = ji.get("location") or ""
        if ji.get("is_remote_allowed"):
            location = f"Remote | {location}"
        wt = ji.get("workplace_types") or []
        if isinstance(wt, str):
            wt = [wt]
        wt = [str(w).upper() for w in wt]
        if "REMOTE" in wt or ji.get("is_remote_allowed"):
            workplace = "remote"
        elif "HYBRID" in wt:
            workplace = "hybrid"
        elif "ON_SITE" in wt or "ONSITE" in wt:
            workplace = "onsite"
        else:
            workplace = "unknown"
        return {
            "workplace": workplace,
            "id": ji.get("job_posting_id"),
            "title": ji.get("title"),
            "company": ci.get("name"),
            "companyName": ci.get("name"),
            "location": location,
            "salary": None,
            "description": ji.get("description", ""),
            "url": ji.get("job_url"),
            "postedAt": ji.get("listed_at"),
            "applicants": ad.get("total_applies"),
            "scrapedAt": datetime.now(timezone.utc).isoformat(),
            "source": "linkedin/apify",
            "_raw": item,
        }

    def first(*keys, default=None):
        for k in keys:
            v = item.get(k)
            if v:
                return v
        return default

    job_id = first("id", "job_id", "jobId")
    url = first("url", "link", "job_url", "jobUrl")
    if not url and job_id:
        url = f"https://www.linkedin.com/jobs/view/{job_id}/"

    company = first("companyName", "company_name", "company")
    if isinstance(company, dict):
        company = company.get("name")

    salary = first("salary", "salary_info", "salaryInfo", "compensation")
    if isinstance(salary, (dict, list)):
        salary = json.dumps(salary, ensure_ascii=False)

    return {
        "id": job_id,
        "title": first("title", "job_title", "jobTitle"),
        "company": company,
        "companyName": company,
        "location": first("location", "job_location", "place"),
        "workplace": "unknown",  # listing-level data has no workplace info — enrich to find out
        "salary": salary,
        "description": first("description", "descriptionText", "description_text",
                             "job_description", "descriptionHtml", default=""),
        "url": url,
        "postedAt": first("postedAt", "posted_at", "listedAt", "published_at", "date_posted"),
        "applicants": first("applicantsCount", "applicants", "num_applicants"),
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
        "source": "linkedin/apify",
        "_raw": item,
    }


def _save(jobs: list[dict], prefix: str) -> None:
    ensure_dirs()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = DATA_RAW / f"{prefix}_{stamp}.json"
    out.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(jobs)} job(s) -> {out}")


def collect_job_ids() -> list[str]:
    """LinkedIn job IDs from every Links_Empregos/*.txt line."""
    ids: list[str] = []
    for f in LINKS_DIR.glob("*.txt"):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = LINKEDIN_JOB_ID.search(line.strip())
            if m and m.group(1) not in ids:
                ids.append(m.group(1))
    return ids


def scrape_links() -> list[dict]:
    """Scrape full detail of each job URL listed in Links_Empregos/."""
    job_ids = collect_job_ids()
    if not job_ids:
        print("No LinkedIn job URLs found in Links_Empregos/*.txt")
        return []
    return enrich_jobs(job_ids)


def enrich_jobs(job_ids: list[str]) -> list[dict]:
    """Full detail (description + remote/hybrid + salary) for LinkedIn job IDs.

    Uses apimaestro/linkedin-job-detail (~$0.005/job, batches of up to 100).
    """
    job_ids = [str(j) for j in job_ids if str(j).isdigit()]
    if not job_ids:
        print("No valid LinkedIn job IDs to enrich")
        return []
    jobs: list[dict] = []
    for start in range(0, len(job_ids), 100):
        batch = job_ids[start:start + 100]
        print(f"Enriching {len(batch)} job(s) via {ACTOR_JOB_DETAIL}")
        run = _client().actor(ACTOR_JOB_DETAIL).call(run_input={"job_id": batch})
        items = _client().dataset(run["defaultDatasetId"]).list_items().items
        jobs.extend(_normalize(i) for i in items)
    _save(jobs, "linkedin_detail")
    return jobs


def search_jobs(keywords: str = "data engineer", location: str = "United States",
                max_jobs: int = 50, published_within: str = "week") -> list[dict]:
    """Keyword search using the account's own actor (compute units only)."""
    print(f"Searching '{keywords}' in '{location}' via {ACTOR_JOB_SEARCH}")
    run = _client().actor(ACTOR_JOB_SEARCH).call(run_input={
        "keywords": keywords,
        "location": location,
        "maxJobs": max_jobs,
        "publishedWithin": published_within,
    })
    items = _client().dataset(run["defaultDatasetId"]).list_items().items
    jobs = [_normalize(i) for i in items]
    _save(jobs, "linkedin_search")
    return jobs


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        kw = sys.argv[2] if len(sys.argv) > 2 else "data engineer"
        loc = sys.argv[3] if len(sys.argv) > 3 else "United States"
        search_jobs(kw, loc)
    else:
        scrape_links()
