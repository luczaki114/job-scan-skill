---
name: job-scan
description: Router skill. Reads config/portals.yml, groups enabled companies by scan_type and enabled search queries, and dispatches each group to the correct sub-skill or subagent. Merges results, deduplicates by URL, and updates data/jobs.json. Invoke when the user asks to scan for jobs or when jobs.json is empty or stale.
---

# job-scan

No scanning logic lives here. This skill reads `config/portals.yml`, splits companies by `scan_type`, handles `search_queries` directly, and delegates to sub-skills / subagents.

## Prerequisites

1. `config/portals.yml` exists and is populated.
2. Sub-skills are present under `.agents/skills/`.

## Execution

### Step 1 — Read config/portals.yml

Load all entries under `tracked_companies`. Filter to `enabled: true`.
Load all entries under `search_queries`. Filter to `enabled: true`.
Also extract:
- `title_filter.positive`
- `title_filter.negative`

### Step 2 — Group by scan_type

Split the enabled tracked companies into three groups:

| scan_type | Sub-skill to invoke | Payload |
|-----------|---------------------|---------|
| api       | api-scan            | List of tracked companies with `scan_type: api` |
| websearch | websearch-scan      | One subagent **per** company with `scan_type: websearch` |
| playwright| playwright-scan     | One subagent **per** company with `scan_type: playwright` |

### Step 3 — Dispatch `api-scan`

Invoke `api-scan` once with the full list of API companies. This is the only
programmatic bulk handler — it runs a Python script that fetches all companies
in one pass.

Capture its stdout output and parse it as a JSON array of job listings. See `schemas/job.md` for the full object contract.

### Step 4 — Dispatch `query-search` subagents

For each enabled search query entry (`{ name, query }`):

1. Spawn a subagent using the `query-search` skill.
2. Pass exactly this context in the prompt:
   - `query`: the query string
   - `positive_filters`: the `title_filter.positive` array
   - `negative_filters`: the `title_filter.negative` array
3. Instruct the subagent to return **only** a JSON array of job objects.

Dispatch as many subagents in parallel as the system allows.

### Step 5 — Dispatch `websearch-scan` subagents

For each enabled company with `scan_type: websearch`:

1. Spawn a subagent using the `websearch-scan` skill.
2. Pass exactly this context in the prompt:
   - `company_name`: the company name
   - `scan_query`: the company's `scan_query` string
   - `careers_url`: the company's `careers_url`
   - `positive_filters`: the `title_filter.positive` array
   - `negative_filters`: the `title_filter.negative` array
3. Instruct the subagent to return **only** a JSON array of job objects.

Dispatch as many subagents in parallel as the system allows.

### Step 6 — Dispatch `playwright-scan` subagents

For each enabled company with `scan_type: playwright`:

1. Spawn a subagent using the `playwright-scan` skill.
2. Pass exactly this context in the prompt:
   - `company_name`: the company name
   - `careers_url`: the company's `careers_url`
   - `positive_filters`: the `title_filter.positive` array
   - `negative_filters`: the `title_filter.negative` array
3. Instruct the subagent to return **only** a JSON array of job objects.

Dispatch as many subagents in parallel as the system allows.

### Step 7 — Collect all results

Gather the JSON arrays from:
- `api-scan`
- All `query-search` subagents
- All `websearch-scan` subagents
- All `playwright-scan` subagents

Concatenate into one flat array.

### Step 8 — Deduplicate

Drop duplicate entries by `url` (keep the first occurrence).

### Step 9 — Merge into data/jobs.json

1. Load the existing `data/jobs.json` (or start with an empty array if it does not exist).
2. Build a lookup of existing jobs by `url`.
3. For each job in the deduplicated result set:
   - If the `url` already exists in the lookup, **update** the record:
     - Overwrite `name`, `company`, `id`, and `description` with the latest values.
     - **Preserve** the existing `date_added`.
   - If the `url` is new, **add** it to the array with `date_added` set to the current ISO 8601 timestamp.
4. Write the merged array back to `data/jobs.json` (create `data/` if it does not exist).

This approach ensures existing jobs are never blindly overwritten and stale records are preserved unless explicitly updated.

## Output

A flat JSON array of job objects. See `schemas/job.md` for the field contract.

```json
[
  {
    "name": "Senior Frontend Engineer",
    "url": "https://...",
    "description": "Plain text job description..."
  }
]
```
