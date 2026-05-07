# Job Schema

Standard data contract for a single job listing. All scan outputs are an **array** of these objects.

**query-search**
```json
{
  "name": "Senior Frontend Engineer",
  "url": "https://jobs.example.com/abc123",
  "company": "Chime",
  "id": "",
  "date_added": "2026-05-06T14:30:00Z",
  "scan_source": "query-search",
  "scan_query": "site:boards.greenhouse.io OR site:job-boards.greenhouse.io \"Senior Frontend Engineer\" OR \"Senior React Engineer\" remote",
  "eval_signal": null
}
```

**api-scan**
```json
{
  "name": "Senior Frontend Engineer",
  "url": "https://boards.greenhouse.io/groupon/jobs/4795668101",
  "company": "Groupon",
  "id": "4795668101",
  "date_added": "2026-05-06T14:30:00Z",
  "scan_source": "api-scan",
  "scan_query": "",
  "eval_signal": null
}
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | **yes** | Job title (e.g. "Senior React Engineer", "Staff Frontend Engineer"). |
| `url` | `string` | **yes** | Direct link to the job posting. Used as the deduplication key. |
| `company` | `string` | **yes** | Company name (added by some scanners when known). |
| `id` | `string` | no - default is "" | External job ID from the ATS (Greenhouse `gh_jid`, Lever posting ID, etc.). |
| `date_added` | `string` | **yes** | ISO 8601 timestamp when the record was first seen (e.g. `2026-05-06T14:30:00Z`). |
| `scan_source` | `string` | **yes** | The skill name that produced this record. One of: `api-scan`, `websearch-scan`, `playwright-scan`, `query-search`. |
| `scan_query` | `string` | no - default is "" | The raw query string used to find this job. Only populated for `query-search` and `websearch-scan` results. Empty for `api-scan` and `playwright-scan`. |
| `eval_signal` | `string \| null` | no - default `null` | Evaluation result. One of: `recommended`, `rejected`, `inconclusive`, or `null` (not yet evaluated). |