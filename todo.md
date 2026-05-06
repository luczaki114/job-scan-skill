# TODO

## Sub-skills to implement

- [ ] **websearch-scan** — scan tracked companies with `scan_type: websearch` using each company's `scan_query`. SKILL.md exists, needs script.
- [ ] **playwright-scan** — scrape tracked companies with `scan_type: playwright` against `careers_url`. SKILL.md exists, needs script.
- [x] **query-scan** — dispatcher skill that farms each `search_queries` entry to isolated `single-query-search` subagents. SKILL.md done.
- [x] **single-query-search** — micro-skill that executes one WebSearch, parses results, applies title filters, and returns a thin JSON array. SKILL.md done.

## Router

- [x] **job-scan** — wire the router to invoke all 4 sub-skills (api-scan ✅, websearch-scan, playwright-scan, query-search), collect results, deduplicate, and merge into `data/jobs.json`.

## Post-processing skills

- [ ] **validate-json** — validate each agent's returned JSON array against `schemas/job.md` (required fields, correct types, non-empty url). Called by the router after collecting subagent results, before dedup. Returns valid entries and logs/drops invalid ones.
- [ ] **dedup-jobs** — accept a flat array of job objects, deduplicate by `url`, and return the cleaned array. Replaces the ad-hoc dedup logic currently inlined in the router.
