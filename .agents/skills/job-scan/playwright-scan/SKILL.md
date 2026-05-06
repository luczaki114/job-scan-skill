---
name: playwright-scan
description: Scrape job listings from company careers pages using Playwright browser automation. Used for companies with scan_type: playwright where no API or search query is viable. Returns Job[] to job-scan.
---

# playwright-scan

Last-resort scan method. Navigates to `careers_url` in a real browser and extracts
job listings from the rendered page. Required when a company's job board is rendered
client-side and not indexed by search engines.

## When this runs

Companies land here when:
- No public API exists (`scan_type` is not `api`).
- No reliable `scan_query` can be constructed (`scan_type` is not `websearch`).
- The careers page requires JavaScript to render job listings.

## Execution

For each enabled company with `scan_type: playwright`:

1. Navigate to `careers_url` using the Playwright browser.
2. Wait for job listing elements to appear (look for `<a>` tags with job titles,
   common selectors: `.job-title`, `[data-job]`, `h3 a`, `li a`).
3. For each listing visible on the page:
   - Extract job title from link text or heading.
   - Extract href as `url` (resolve relative paths against the page origin).
   - Extract any visible description text near the listing.
4. Apply `title_filter` from config/portals.yml.
5. If pagination exists, follow next-page links until exhausted or 5 pages max.

## Output

```json
{ "name": "Senior Frontend Engineer", "url": "https://...", "description": "..." }
```

## Notes

- Slowest of the three scan types. Run last or in a separate pass.
- Some career pages require login or block headless browsers. If the listing count
  is 0 and the page loaded, log a warning and skip rather than failing silently.
