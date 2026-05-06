---
name: api-scan
model: claude-haiku-4-5-20251001
description: Fetch job listings from companies with scan_type: api. Supports Greenhouse, Lever, and Ashby public JSON APIs. Runs scripts/scan.py and returns a JSON array.
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

Run the script and capture **stdout** as the result. Stdout contains only the JSON array.

```bash
python .agents/skills/api-scan/scripts/scan.py
```

The script resolves the project root by searching for `config/portals.yml`, so it can be
run from any working directory.

## Output

Returns a flat JSON array of job listings printed to **stdout**. Each entry follows `schemas/job.md`.

```json
[
  { "name": "Senior Frontend Engineer", "url": "https://...", "company": "...", "date_added": "..." }
]
```

`description` is plain text (HTML stripped). May be empty string if the API
does not return content for listing endpoints.
