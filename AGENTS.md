## On Session Start
When this project is loaded, immediately:
1. Read this file in full
2. Read `TODO.md` and note all open items
3. Read the frontmatter only (stop at the second `---`) of every SKILL.md under `.agents/skills/`
4. Compare each skill's declared `requires`, `input`, and `output` fields against what exists on disk
5. Determine where the user is in the dependency pipeline (see Pipeline Overview below)
6. Send the user a message in this order: open TODOs → pipeline snapshot → what you would do next

---

## Pipeline Overview

```
config/portals.yml ──► job-scan ──► api-scan / websearch-scan / playwright-scan / query-search
                                        │
                                        ▼
                                  data/jobs.json
                                        │
                              ┌─────────┴──────────┐
                              ▼                    ▼
                       research-company      evaluate-job ◄── config/meta_profile.md
                              │                    │              │
                              ▼                    ▼              ▼
                  data/company-research/    data/evals/   data/scoring_rubric.md
                                                                  ▲
                                                         generate-scoring-rubric
                                                          (reads meta_profile.md)
```

---

## Skill Definitions

| Skill | Model | Context | Purpose | Inputs | Outputs | Trigger |
|-------|-------|---------|---------|--------|---------|---------|
| `job-scan` | Sonnet | **fork** | Router. Reads `config/portals.yml`, groups companies by `scan_type`, dispatches sub-skills, merges results, deduplicates by URL, writes to `data/jobs.json` | `config/portals.yml` | `data/jobs.json` (appended) | User asks to scan; `jobs.json` is empty or stale |
| `api-scan` | Haiku | root | Fetch listings from Greenhouse / Lever / Ashby public JSON APIs via `scripts/scan.py`. Returns flat JSON array. | `company`, `ats`, `api_url`, title filters | Flat JSON array of job objects | Called by `job-scan` for `scan_type: api` entries |
| `websearch-scan` | Haiku | root | Run one Google site-search per company, parse results, apply title filters. Returns flat JSON array. | `company_name`, `scan_query`, `careers_url`, title filters | Flat JSON array of job objects | Called by `job-scan` for `scan_type: websearch` entries |
| `playwright-scan` | Haiku | root | Scrape one company careers page via Playwright browser. Returns flat JSON array. | `company_name`, `careers_url`, title filters | Flat JSON array of job objects | Called by `job-scan` for `scan_type: playwright` entries |
| `query-search` | Haiku | root | Run one arbitrary web search query, parse results, apply filters. Returns flat JSON array. | `query`, `positive_filters`, `negative_filters` | Flat JSON array of job objects | Called by `job-scan` for `search_queries` entries |
| `generate-scoring-rubric` | — | root | Derive a weighted scoring rubric from `config/meta_profile.md` and write to `data/scoring_rubric.md`. | `config/meta_profile.md` | `data/scoring_rubric.md` | **Run when `meta_profile.md` changes.** Also run if `scoring_rubric.md` is missing. |
| `research-company` | Haiku | **fork** | Research one company and write a structured brief. | `config/meta_profile.md`, `company_name`, `company_url` | `data/company-research/{slug}.md` | User asks to research a company; called before deep evaluation |
| `evaluate-job` | Haiku | **fork** | Score one job listing against `meta_profile.md` and `scoring_rubric.md`. Write an eval report and return score + reason. | Job object (name + URL required), `config/meta_profile.md`, `data/scoring_rubric.md` | `data/evals/{title}-{company}-{mm-dd-yyyy}.md`; `job_score` written back to `data/jobs.json` | User asks to evaluate a job; called for each job in `data/jobs.json` where `job_score` is `null` |

**Context convention:**
- `root` — Skill may run in the root agent context or as a subagent.
- **`fork`** — Skill **must** run as a subagent (`Agent` tool). Never inline in root context.

**Orchestration rules for `fork` skills:**
- **Read inputs once.** The root agent reads each skill's declared `requires` / `input` files once, then passes them directly in the subagent prompt. Subagents do not re-read shared inputs from disk.
- **Batch subagents.** Spawn in parallel batches up to the background task limit.
- **Write per batch.** Collect returned results from the batch, then write to disk once (e.g. update `data/jobs.json` after all 4 subagents return, not after each individual job).
- Batching and input caching are the orchestrator's concern, not the individual skill's.

---

## Environment

This project runs on **Windows / PowerShell**. Do not use Bash or shell commands. Use the `Write` tool to create files and `WebFetch` to fetch URLs. Never attempt `curl`, `cat`, or other POSIX commands.

## File Ownership

### Config layer (`config/`)

The user is the source of truth for `config/`. Agents may write to `config/` only with explicit user permission (e.g., the user asks the agent to update the profile or rubric). Agents never modify config files autonomously.

| File | Purpose |
|------|---------|
| `config/meta_profile.md` | Canonical source of truth for identity, preferences, constraints, and domain tiers. All agent reasoning is grounded here. |
| `config/portals.yml` | List of companies and search queries the scan pipeline should target. |

### Data layer (`data/`)

The `data/` directory is entirely agent-managed. The user never edits files here — all contents are derived outputs from skills. Hand-editing will be overwritten on the next pipeline run.

| Path | Written by |
|------|-----------|
| `data/jobs.json` | `job-scan`, `api-scan`, `websearch-scan`, `playwright-scan`, `query-search` |
| `data/scoring_rubric.md` | `generate-scoring-rubric` |
| `data/evals/*.md` | `evaluate-job` |
| `data/company-research/*.md` | `research-company` |

---

## File Watch Triggers

When a config file changes, the following skills must be re-run before continuing downstream:

| File changed | Action required |
|--------------|-----------------|
| `config/meta_profile.md` | Re-run `generate-scoring-rubric` to update `data/scoring_rubric.md`. Flag to the user that existing `data/evals/` are stale against the new rubric and offer to re-evaluate. |
| `config/portals.yml` | Next `job-scan` run picks up changes automatically. No immediate action unless the user asks to scan now. |

---

## AGENTS.md Maintenance

This file documents the pipeline based on the skill frontmatters in `.agents/skills/`. When committing changes to any SKILL.md, check whether the corresponding row in the Skill Definitions table above needs to be updated. Stale documentation here will cause incorrect pipeline reasoning on session load.

Fields to verify on commit: `name`, `model`, `description`, `input`/`requires`, `output`, and the trigger condition.

---

## Pipeline Readiness Checklist

Use this during session start to determine what step the user is on:

| Step | Ready when | Blocked by |
|------|------------|------------|
| 1. Config | `config/meta_profile.md` exists and is populated | Nothing — user must create this |
| 2. Rubric | `data/scoring_rubric.md` exists and is current with `meta_profile.md` | Step 1; run `generate-scoring-rubric` if missing or if meta_profile changed |
| 3. Portals | `config/portals.yml` has at least one `enabled: true` entry | User must populate |
| 4. Jobs | `data/jobs.json` has entries | Step 3; run `job-scan` |
| 5. Evals | All jobs in `data/jobs.json` have non-null `job_score` | Steps 2 + 4; run `evaluate-job` per unscored job |
