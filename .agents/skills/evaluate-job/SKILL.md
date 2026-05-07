---
name: evaluate-job
model: claude-sonnet-4-6
description: Evaluates a single job against the user's scoring rubric and meta profile. Runs a pre-eval on job fit first; if it clears the threshold, runs a full-eval incorporating company research. Writes an eval report and returns a structured result to the orchestrator.
input:
  - job: job listing of type schema/job.md
  - scoring_rubric: data/scoring_rubric.md
  - meta_profile: config/meta_profile.md
output: A eval report at data/evals/{job-title}-{company}-{timestamp}.md
returns:
  signal: recommended | rejected | inconclusive
  phase: pre-eval | full-eval
  reason: why this signal was assigned
  report: path to written eval report (present if full-eval ran)
  company_brief: path to company-research file (present if research ran)
depends_on:
  - research-company
---
