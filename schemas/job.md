# Job Schema

Standard data contract for a single job listing. All scan outputs are an **array** of these objects.

```json
{
  "name": "Senior Frontend Engineer",
  "url": "https://jobs.example.com/abc123",
  "company": "Chime",
  "id": "",
  "date_added": "2026-05-06T14:30:00Z"
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