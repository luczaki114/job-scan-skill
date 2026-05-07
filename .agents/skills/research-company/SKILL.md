---
name: research-company
model: claude-sonnet-4-6
description: Researches a single company and writes a structured profile to disk.
input:
  - meta_profile: config/meta_profile.md
  - company_name: string
  - company_url: string
output: a company brief at data/company-research/{company-slug}.md
returns:
  name: company name
  url: company url
  notes: string — key signals surfaced during research
---
