---
name: job-scan
description: Router skill. Reads config/portals.yml, groups enabled companies by scan_type, and dispatches each group to the correct sub-skill. Merge results, deduplicate by URL, write to data/jobs.json. Invoke when the user asks to scan for jobs or when jobs.json is empty or stale.
---

# job-scan

No scanning logic lives here. This skill reads config/portals.yml, splits companies by scan_type, and delegates to sub-skills.

## Prerequisites

1. `config/config/portals.yml` exists and is populated.
2. Sub-skills are present under `.agents/skills/`.

## Execution

### Step 1 — Read config/portals.yml

Load all entries under `tracked_companies`. Filter to `enabled: true`.

### Step 2 — Group by scan_type

Split the enabled company list into three groups:

| scan_type   | Sub-skill to invoke  |
|-------------|----------------------|
| api         | api-scan             |
| websearch   | websearch-scan       |
| playwright  | playwright-scan      |

### Step 3 — Dispatch

Invoke each sub-skill with its company group. Sub-skills may run in parallel.
Each returns a flat array of job listings: `[{ name, url, description }, ...]`

### Step 4 — Merge and deduplicate

Collect all results. Deduplicate by `url`. A URL seen more than once keeps the first occurrence.

### Step 5 — Write output

Write the deduplicated array to `data/jobs.json` (create `data/` if it does not exist).

## Output

```json
[
  {
    "name": "Senior Frontend Engineer",
    "url": "https://...",
    "description": "Plain text job description..."
  }
]
```
