#!/usr/bin/env python3
"""
api-scan — fetches job listings for all scan_type: api companies in portals.yml.
Supports Greenhouse, Lever, and Ashby public JSON APIs (no key required).
Writes results to data/jobs.json in the project root.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")


def find_project_root() -> Path:
    """Walk up from this file until we find config/portals.yml."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "config" / "portals.yml").exists():
            return parent
    raise FileNotFoundError("config/portals.yml not found in any parent directory")


PROJECT_ROOT = find_project_root()
PORTALS_FILE = PROJECT_ROOT / "config" / "portals.yml"
OUT_FILE = PROJECT_ROOT / "data" / "jobs.json"


def load_portals():
    with open(PORTALS_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def title_passes(title: str, title_filter: dict) -> bool:
    t = title.lower()
    if not any(p.lower() in t for p in title_filter["positive"]):
        return False
    if any(n.lower() in t for n in title_filter["negative"]):
        return False
    return True



def _get(url: str, company_name: str):
    """Fetch URL and return parsed JSON, or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "job-scan/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        print(f"  [WARN] {company_name}: {exc}")
        return None


def fetch_greenhouse(api_url: str, company_name: str, title_filter: dict) -> list[dict]:
    data = _get(api_url.rstrip("/") + "?content=true", company_name)
    if not data:
        return []
    results = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        if not title_passes(title, title_filter):
            continue
        results.append({
            "id": str(job.get("id", "")),
            "company": company_name,
            "name": title,
            "url": job.get("absolute_url", ""),
        })
    return results


def fetch_lever(api_url: str, company_name: str, title_filter: dict) -> list[dict]:
    # Lever returns a JSON array; each posting has `text` (title) and `hostedUrl`
    data = _get(api_url, company_name)
    if not data:
        return []
    results = []
    for job in data:
        title = job.get("text", "")
        if not title_passes(title, title_filter):
            continue
        results.append({
            "id": job.get("id", ""),
            "company": company_name,
            "name": title,
            "url": job.get("hostedUrl", ""),
        })
    return results


def fetch_ashby(api_url: str, company_name: str, title_filter: dict) -> list[dict]:
    # Ashby returns { jobPostings: [...] }; each has `title`, `jobUrl`, `descriptionHtml`
    data = _get(api_url, company_name)
    if not data:
        return []
    results = []
    for job in data.get("jobPostings", []):
        if not job.get("isListed", True):
            continue
        title = job.get("title", "")
        if not title_passes(title, title_filter):
            continue
        results.append({
            "id": job.get("id", ""),
            "company": company_name,
            "name": title,
            "url": job.get("jobUrl", ""),
        })
    return results


def detect_ats(company: dict) -> str:
    """Resolve ATS type from explicit `ats:` field, falling back to api URL pattern."""
    explicit = company.get("ats", "").lower()
    if explicit in ("greenhouse", "lever", "ashby"):
        return explicit
    api_url = company.get("api", "")
    if "greenhouse.io" in api_url:
        return "greenhouse"
    if "lever.co" in api_url:
        return "lever"
    if "ashbyhq.com" in api_url:
        return "ashby"
    return "unknown"


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
}


def main():
    config = load_portals()
    title_filter = config["title_filter"]
    companies = config.get("tracked_companies", [])

    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_jobs: list[dict] = []
    seen_urls: set[str] = set()
    skipped: list[str] = []

    for company in companies:
        if not company.get("enabled", True):
            continue

        name = company["name"]
        scan_type = company.get("scan_type", "playwright")

        if scan_type != "api":
            skipped.append(f"{name} ({scan_type})")
            continue

        api_url = company.get("api")
        if not api_url:
            skipped.append(f"{name} (api — missing api: url)")
            continue

        ats = detect_ats(company)
        fetcher = FETCHERS.get(ats)
        if not fetcher:
            skipped.append(f"{name} (api — unsupported ATS: {ats})")
            continue

        print(f"[{ats}] {name} ...")
        jobs = fetcher(api_url, name, title_filter)
        new = [j for j in jobs if j["url"] not in seen_urls]
        for j in new:
            j["date_added"] = run_ts
        seen_urls.update(j["url"] for j in new)
        all_jobs.extend(new)
        print(f"  {len(new)} match{'es' if len(new) != 1 else ''}")

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"\n--- {len(all_jobs)} jobs written to {OUT_FILE} ---")
    if skipped:
        print(f"Skipped ({len(skipped)} — route to websearch-scan or playwright-scan):")
        for s in skipped:
            print(f"  • {s}")


if __name__ == "__main__":
    main()
