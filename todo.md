# TODO

## Sub-skills to implement

- [ ] **websearch-scan** — scan tracked companies with `scan_type: websearch` using each company's `scan_query`. SKILL.md exists, needs script.
- [ ] **playwright-scan** — scrape tracked companies with `scan_type: playwright` against `careers_url`. SKILL.md exists, needs script.
- [ ] **query-scan** — run the broad `search_queries` from `config/portals.yml` (site: searches across Ashby, Greenhouse, Lever, remote boards). New sub-skill, no SKILL.md yet.

## Router

- [ ] **job-scan** — wire the router to invoke all 4 sub-skills (api-scan ✅, websearch-scan, playwright-scan, query-scan), collect results, deduplicate, write to `data/jobs.json`.
