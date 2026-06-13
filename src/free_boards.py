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
from html import unescape

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


def _html_to_text(fragment: str) -> str:
    """Strip an HTML fragment to readable text (lists/paragraphs become lines)."""
    fragment = re.sub(r"(?is)<(script|style|svg|noscript)\b.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?is)<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"(?is)</(p|li|h[1-6]|div|tr|ul|ol)>", "\n", fragment)
    text = re.sub(r"(?s)<[^>]+>", " ", fragment)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n[ \t]*\n+", "\n", text).strip()


# UUID (Lever/Ashby job id) and numeric Greenhouse job id patterns.
_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_LEVER_RE = re.compile(rf"jobs\.lever\.co/([^/?#]+)/({_UUID})", re.I)
_ASHBY_RE = re.compile(rf"jobs\.ashbyhq\.com/([^/?#]+)/({_UUID})", re.I)
_GREENHOUSE_RE = re.compile(r"(?:job-boards|boards)\.greenhouse\.io/([^/?#]+)/jobs/(\d+)", re.I)
_APPLY_RE = re.compile(r'<a[^>]+href=["\']?([^"\'>\s]+)[^>]*>\s*Apply now', re.I)


def _lever_description(org: str, uuid: str) -> str:
    r = requests.get(
        f"https://api.lever.co/v0/postings/{org}/{uuid}", params={"mode": "json"},
        headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    j = r.json()
    return (j.get("descriptionPlain") or "").strip() or _html_to_text(j.get("description", ""))


def _ashby_description(org: str, uuid: str) -> str:
    r = requests.get(
        f"https://api.ashbyhq.com/posting-api/job-board/{org}",
        headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    for job in r.json().get("jobs", []):
        if job.get("id") == uuid:
            return (job.get("descriptionPlain") or "").strip() or _html_to_text(
                job.get("descriptionHtml", "")
            )
    return ""


def _greenhouse_description(token: str, job_id: str) -> str:
    r = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{job_id}",
        headers=HEADERS, timeout=TIMEOUT,
    )
    r.raise_for_status()
    # Greenhouse single-job 'content' is HTML-escaped once (&lt;div&gt;...);
    # unescape it first so _html_to_text sees real tags to strip.
    return _html_to_text(unescape(r.json().get("content", "")))


def _ats_description(apply_url: str) -> str:
    """Follow a cryptocurrencyjobs 'Apply now' link to the destination ATS and
    pull the full JD via its public JSON API (Lever / Ashby / Greenhouse).
    Unknown hosts (Workday, custom sites, SPAs) return '' — we never strip a
    generic page (that would pollute scoring with nav/SPA boilerplate).
    Any network/parse failure also returns ''."""
    if not apply_url:
        return ""
    try:
        m = _LEVER_RE.search(apply_url)
        if m:
            return _lever_description(m.group(1), m.group(2))
        m = _ASHBY_RE.search(apply_url)
        if m:
            return _ashby_description(m.group(1), m.group(2))
        m = _GREENHOUSE_RE.search(apply_url)
        if m:
            return _greenhouse_description(m.group(1), m.group(2))
    except (requests.RequestException, ValueError, KeyError):
        return ""
    return ""


def _fetch_full_description(url: str) -> str:
    """cryptocurrencyjobs.co RSS only carries a one-line teaser — the real
    description (and its skills) lives on the posting page. Fetch + extract it.
    If that page itself only carries a stub (<500 chars), follow its 'Apply now'
    link to the destination ATS and use the richer JD when it is longer.
    Returns '' on any network/parse failure so the caller keeps the teaser."""
    if not url:
        return ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.RequestException:
        return ""
    page = r.text
    start = page.find("<h1")
    if start < 0:
        start = 0
    end = len(page)
    # text anchors (Tailwind classes are unstable) bound the job body
    for marker in ("Apply now", "Please let", "Share this", 'aria-label="Share', "<footer"):
        i = page.find(marker, start)
        if i != -1:
            end = min(end, i)
    description = _html_to_text(page[start:end])
    # Page already has the full JD (e.g. Braiins ~4k chars) — do NOT follow apply.
    if len(description) >= 500:
        return description
    # Stub teaser: try the destination ATS and keep it only if richer.
    apply_match = _APPLY_RE.search(page)
    if apply_match:
        ats = _ats_description(unescape(apply_match.group(1)))
        if len(ats) > len(description):
            return ats
    return description


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
            # cryptocurrencyjobs RSS gives only a teaser — fetch the full page
            # description for the (few) title-matched jobs so skills get scored.
            if fn is fetch_cryptocurrencyjobs_rss:
                for j in kept:
                    full = _fetch_full_description(j.get("url", ""))
                    if len(full) > len(j.get("description", "")):
                        j["description"] = full
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
