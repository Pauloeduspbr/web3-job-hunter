"""Collect Data Engineer postings from FREE public sources ($0, no auth).

Sources verified live on 2026-06-10:
- Greenhouse Job Board API   (boards-api.greenhouse.io)
- Ashby Posting API          (api.ashbyhq.com)
- Lever Postings API         (api.lever.co)
- RemoteOK API               (remoteok.com/api — ToS requires linkback attribution)
- cryptocurrencyjobs.co RSS

Company slugs live in config/companies_watchlist.yaml.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests
import yaml

from config import DATA_RAW, PROJECT_ROOT, ensure_dirs

WATCHLIST = PROJECT_ROOT / "config" / "companies_watchlist.yaml"
HEADERS = {"User-Agent": "web3-job-hunter/1.0 (personal job search)"}
TIMEOUT = 30


def _load_watchlist() -> dict:
    with open(WATCHLIST, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _job(title, company, url, location="", description="", salary=None, source="") -> dict:
    return {
        "title": title, "company": company, "companyName": company,
        "url": url, "location": location, "description": description,
        "salary": salary, "source": source,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }


def fetch_greenhouse(slug: str) -> list[dict]:
    r = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
        params={"content": "true"}, headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    return [
        _job(j.get("title"), j.get("company_name") or slug, j.get("absolute_url"),
             (j.get("location") or {}).get("name", ""), j.get("content", ""),
             source=f"greenhouse/{slug}")
        for j in r.json().get("jobs", [])
    ]


def fetch_ashby(slug: str) -> list[dict]:
    r = requests.get(
        f"https://api.ashbyhq.com/posting-api/job-board/{slug}",
        headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    jobs = []
    for j in r.json().get("jobs", []):
        loc = j.get("location", "")
        if j.get("isRemote"):
            loc = f"Remote | {loc}"
        jobs.append(_job(j.get("title"), slug.split(".")[0].split("-")[0], j.get("jobUrl"),
                         loc, j.get("descriptionPlain", ""), source=f"ashby/{slug}"))
    return jobs


def fetch_lever(slug: str) -> list[dict]:
    r = requests.get(
        f"https://api.lever.co/v0/postings/{slug}", params={"mode": "json"},
        headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    return [
        _job(j.get("text"), slug, j.get("hostedUrl"),
             (j.get("categories") or {}).get("location", ""),
             j.get("descriptionPlain", ""),
             salary=j.get("salaryDescription"), source=f"lever/{slug}")
        for j in r.json()
    ]


def fetch_remoteok() -> list[dict]:
    r = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    jobs = []
    for j in r.json():
        if not isinstance(j, dict) or not j.get("position"):
            continue  # first element is the ToS/legal notice
        salary = None
        if j.get("salary_min"):
            salary = f"${j['salary_min']}-${j.get('salary_max', '?')}"
        jobs.append(_job(j.get("position"), j.get("company"), j.get("url"),
                         j.get("location", "Remote"),
                         f"{j.get('description', '')} tags: {' '.join(j.get('tags', []))}",
                         salary=salary, source="remoteok"))
    return jobs


def fetch_cryptocurrencyjobs_rss() -> list[dict]:
    r = requests.get("https://cryptocurrencyjobs.co/index.xml", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    jobs = []
    for item in ET.fromstring(r.content).iter("item"):
        title = (item.findtext("title") or "").strip()
        # RSS title format: "Role at Company"
        m = re.match(r"(.+?)\s+at\s+(.+)", title)
        role, company = (m.group(1), m.group(2)) if m else (title, "")
        jobs.append(_job(role, company, item.findtext("link"),
                         description=item.findtext("description") or "",
                         source="cryptocurrencyjobs.co"))
    return jobs


def run() -> list[dict]:
    ensure_dirs()
    wl = _load_watchlist()
    title_re = re.compile(wl.get("title_filter", "data engineer"), re.I)

    collected: list[dict] = []
    sources = (
        [(fetch_greenhouse, s) for s in wl.get("greenhouse", [])]
        + [(fetch_ashby, s) for s in wl.get("ashby", [])]
        + [(fetch_lever, s) for s in wl.get("lever", [])]
        + [(fetch_remoteok, None), (fetch_cryptocurrencyjobs_rss, None)]
    )
    for fn, arg in sources:
        label = f"{fn.__name__}({arg or ''})"
        try:
            batch = fn(arg) if arg else fn()
            kept = [j for j in batch if title_re.search(str(j.get("title", "")))]
            print(f"  {label}: {len(batch)} jobs, {len(kept)} match title filter")
            collected.extend(kept)
        except Exception as exc:  # one broken source must not kill the run
            print(f"  {label}: FAILED — {exc}")

    # dedup by URL
    seen, unique = set(), []
    for j in collected:
        if j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = DATA_RAW / f"free_boards_{stamp}.json"
    out.write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(unique)} unique job(s) -> {out}")
    return unique


if __name__ == "__main__":
    run()
