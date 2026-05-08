---
name: generate-scoring-rubric
model: claude-haiku-4-5-20251001
description: Reads the users meta_profile.md and generates a scoring rubric — a weighted scoring table used by the job evaluation pipeline. Run this skill when there is no data/scoring_rubric.md or when data/meta_profile.md changes.
input: config/meta_profile.md
output: A scoring rubric at data/scoring_rubric.md
---

# generate-scoring-rubric

Derive a structured scoring rubric from the user's meta profile and writes it to `data/scoring_rubric.md`.

## Input

- `config/meta_profile.md` — read directly from disk, no parameters required.

## Execution

Read `config/meta_profile.md`. The profile contains the signals relevant to this user's job search — priorities, preferences, hard constraints, and dealbreakers. Use those signals to derive a scoring rubric: what dimensions matter, how much each one weighs, and what conditions disqualify a job outright. Weights must sum to 100. Reasoning for each dimension should be grounded in the profile, not assumed generically.

Write `data/scoring_rubric.md` with the following structure:

```markdown
# Scoring Rubric

## Dimensions

| Dimension | Weight | Reasoning |
|-----------|--------|-----------|
| ...       | ...    | ...       |

**Total: 100**

## Hard Knockouts (score → 0)

- <condition>
- <condition>
```

## Output

`data/scoring_rubric.md` written to disk. No return value.
