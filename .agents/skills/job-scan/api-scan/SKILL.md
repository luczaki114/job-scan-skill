---
name: api-scan
description: Fetch job listings from companies with scan_type: api. Supports Greenhouse, Lever, and Ashby public JSON APIs. Runs scripts/scan.py. Returns Job[] to job-scan.
---

# api-scan

Handles companies where a public JSON API is available. Dispatches to the correct
ATS fetcher based on the `ats:` field (or infers it from the `api:` URL pattern).

## Supported ATS providers

| ats        | API pattern                                                    |
|------------|----------------------------------------------------------------|
| greenhouse | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs`       |
| lever      | `https://api.lever.co/v0/postings/{slug}?mode=json`            |
| ashby      | `https://api.ashbyhq.com/posting-api/job-board/{slug}`         |

All three are public — no API key required. Lever companies can opt out; if the
endpoint returns 404, treat as a skip and report it.

## Prerequisites

1. Python 3 available (`python --version`).
2. pyyaml installed (`pip install pyyaml`).
3. `config/portals.yml` in the project root.

## Execution

```bash
python .agents/skills/job-scan/api-scan/scripts/scan.py
```

The script resolves the project root by searching for `config/portals.yml`, so it can be
run from any working directory.

## Output

Returns a flat array of job listings. Each entry:

```json
{ "name": "Senior Frontend Engineer", "url": "https://...", "description": "..." }
```

`description` is plain text (HTML stripped). May be empty string if the API
does not return content for listing endpoints.
