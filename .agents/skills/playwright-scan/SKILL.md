---
name: playwright-scan
model: claude-haiku-4-5-20251001
description: Scrape job listings from one company careers page using Playwright browser automation. Takes a careers_url and title filters, extracts listings, applies filtering, and returns only a flat JSON array of job listings.
---

# playwright-scan

Executes exactly **one** company scrape and returns filtered job listings.

## Input (passed by the parent agent)

- `company_name`: Company name (for logging / context)
- `careers_url`: The company's careers page URL to navigate
- `positive_filters`: Array of strings — at least one must appear in the job title (case-insensitive)
- `negative_filters`: Array of strings — none may appear in the job title (case-insensitive)

## Execution

1. **Navigate**: Open `careers_url` using the Playwright browser.
2. **Extract**: Wait for job listing elements to appear (look for `<a>` tags with job titles,
   common selectors: `.job-title`, `[data-job]`, `h3 a`, `li a`).
   For each listing visible on the page:
   - Extract job title from link text or heading → `name`
   - Extract href as `url` (resolve relative paths against the page origin)
   - Extract any visible description text near the listing → `description`
   - Build objects matching `schemas/job.md`.
3. **Paginate**: If pagination exists, follow next-page links until exhausted or 5 pages max.
4. **Filter**: Apply the title filter to each candidate:
   - **Positive**: `name` must contain at least one string from `positive_filters`.
   - **Negative**: `name` must not contain any string from `negative_filters`.
   - Matching is case-insensitive.
5. **Return**: Output **only** a JSON array. No prose, no markdown fences, no explanations.

## Output

A flat JSON array of job objects. See `schemas/job.md` for the field contract.

```json
[
  { "name": "Senior Frontend Engineer", "url": "https://...", "description": "..." }
]
```

If no results pass the filter, return an empty array `[]`.

## Notes

- Slowest scan method. Run last or in a separate pass.
- Some career pages require login or block headless browsers. If the listing count
  is 0 and the page loaded, return `[]` rather than failing.
