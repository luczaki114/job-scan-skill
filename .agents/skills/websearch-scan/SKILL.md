---
name: websearch-scan
model: claude-haiku-4-5-20251001
description: Execute one web-search scan for a single company. Takes a scan_query and title filters, runs WebSearch, parses results, applies filtering, and returns only a flat JSON array of job listings.
---

# websearch-scan

Executes exactly **one** company search and returns filtered job listings.

## Input (passed by the parent agent)

- `company_name`: Company name (for logging / context)
- `scan_query`: The pre-written Google site: search string for this company
- `careers_url`: The company's careers page URL (for context / validation)
- `positive_filters`: Array of strings — at least one must appear in the job title (case-insensitive)
- `negative_filters`: Array of strings — none may appear in the job title (case-insensitive)

## Execution

1. **Search**: Run `WebSearch` with the provided `scan_query`.
2. **Parse**: For each result, create a candidate object matching `schemas/job.md`:
   - `name` → job title from the result title or snippet heading
   - `url` → result URL
   - `description` → snippet text (or empty string if unavailable)
   - Skip results that are clearly not job postings (e.g. generic homepages without title context).
3. **Filter**: Apply the title filter to each candidate:
   - **Positive**: `name` must contain at least one string from `positive_filters`.
   - **Negative**: `name` must not contain any string from `negative_filters`.
   - Matching is case-insensitive.
4. **Return**: Output **only** a JSON array. No prose, no markdown fences, no explanations.

## Output

A flat JSON array of job objects. See `schemas/job.md` for the field contract.

```json
[
  { "name": "Senior Frontend Engineer", "url": "https://...", "description": "..." }
]
```

If no results pass the filter, return an empty array `[]`.

## Notes

- Results may be stale (Google index lag). Treat as leads, not confirmed openings.
- LinkedIn results require a logged-in session; expect blocked or truncated snippets.
