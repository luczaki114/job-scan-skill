---
name: websearch-scan
description: Find job listings for companies with scan_type: websearch. Uses each company's scan_query with the WebSearch tool. Returns Job[] to job-scan.
---

# websearch-scan

Handles companies where no public JSON API is available or has been discovered.
Each company carries a `scan_query` — a pre-written Google site: search string
targeting that company's ATS domain.

## When this runs

Companies land here when:
- Their ATS (Workday, LinkedIn, ApplyToJob, custom portal) has no public JSON API.
- Their ATS has an API but it is disabled for that company (e.g. Lever opt-out).
- The ATS is unknown and the scan_query is a broad discovery search.

## Execution

For each enabled company with `scan_type: websearch`:

1. Read `scan_query` from the company entry in config/portals.yml.
2. Run the query through WebSearch.
3. For each result URL that matches the company's ATS domain:
   - Extract job title from the page title or result snippet.
   - Set `url` to the result URL.
   - Set `description` to the result snippet (or empty string if unavailable).
4. Apply `title_filter` from config/portals.yml: at least one positive must match,
   zero negatives must match (case-insensitive).

## Output

```json
{ "name": "Senior Frontend Engineer", "url": "https://...", "description": "..." }
```

`description` will often be a snippet rather than a full job description.
A follow-up fetch of the URL is required for the full text.

## Notes

- Results may be stale (Google index lag). Treat as leads, not confirmed openings.
- LinkedIn results require a logged-in session; expect blocked or truncated snippets.
