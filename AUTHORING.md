# Authoring rules for SAP S/4HANA migration skills

This document is normative. Every contributor (human or agent) must follow it.

## 1. File location

Skills live at `.agents/skills/<skill-name>/SKILL.md`. The directory name MUST match the `name` field in the frontmatter and MUST be kebab-case starting with `sap-`.

Supporting reference files go under `.agents/skills/<skill-name>/references/<topic>.md`.

## 2. Frontmatter schema (required)

```yaml
---
name: <kebab-case, must equal directory name>
description: |
  Use when <concrete trigger>: <list at least 3 specific situations,
  including SAP transaction codes, simplification item names, or
  error symptoms the agent might encounter>.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "<ISO date, must be within 14 days of PR creation>"
  s4hana_release: "<comma-separated releases this skill applies to>"
  sources:
    - "<authoritative source 1>"
    - "<authoritative source 2>"
related_skills:
  - <other skill name in this repo>
---
```

The `description` field is the most important field in the entire skill. It is what the agent's discovery layer matches against. Bad descriptions = skill never gets invoked.

**Good description** (specific, trigger-rich):
> Use when scoping custom ABAP code prior to an SAP ECC → S/4HANA system conversion: collecting usage data with transaction SCMON or SUSG, identifying dead code in production, building deletion transports for unused custom objects, or producing a scoped worklist before running ATC readiness checks.

**Bad description** (vague):
> A skill for SAP migration scoping.

## 3. Body structure

Use exactly these top-level sections, in this order:

1. `## When to use this skill`
2. `## Prerequisites`
3. `## Quick decision tree`
4. `## Procedure`
5. `## Worked example`
6. `## Anti-patterns`
7. `## References`

If a section is genuinely not applicable, keep the heading and write `_Not applicable for this skill._` so reviewers know it was considered.

## 4. Citation rules

- Every factual claim about SAP behavior, transaction code, table name, or simplification gets an inline citation. Format: `(SAP Note 2185390)` or `([SAP Help](https://help.sap.com/...))`.
- Stable URLs only. Prefer `help.sap.com` permalinks. Wayback Machine snapshots are acceptable for older blog material.
- Each `references/*.md` file starts with an attribution block listing upstream sources and licenses.
- Never paste more than ~3 sentences of SAP-copyrighted documentation verbatim. Paraphrase and link out.

## 5. Length

- Target: ≤ 600 lines per `SKILL.md`. Hard cap: 1000 lines.
- If a topic needs more depth, push it into `references/` and link from the body.
- The agent reads the whole `SKILL.md` when invoked. Keep it scannable.

## 6. Things you MUST NOT do

- ❌ Embed images as base64 data URIs.
- ❌ Include secrets, license keys, customer system IDs, or real client numbers. Use `<system-id>` and `<client-no>` placeholders.
- ❌ Add a `tools:` field to the frontmatter. Devin scopes tools at the harness level, not per skill.
- ❌ Edit sibling skills, even if you think they're wrong. File an issue or PR comment instead.
- ❌ Mark anything `<!-- UNVERIFIED -->` and then call the skill done. Either verify or remove the claim.

## 7. Validation

Before opening a PR, run:

```bash
./scripts/validate-skills.sh   # frontmatter + link checks
git add .agents/skills
```

PRs that fail `validate-skills.sh` will fail CI.

## 8. Source priorities

Use these sources, in order of preference:

1. **SAP Custom Code Migration Guide for S/4HANA 2025 FPS01** (PDF on help.sap.com) — the canonical runbook. Cite specific section numbers.
2. **SAP Notes** — cite by note number (e.g., "SAP Note 2185390").
3. **SAP Help Portal** (`help.sap.com`) — cite by stable URL.
4. **SAP-samples GitHub repos** (`SAP-samples/abap-cheat-sheets`, `SAP/abap-cleaner`, `SAP/abap-atc-cr-cv-s4hc-tools`) — cite by file path and commit SHA.
5. **SAP Community blog posts** (`community.sap.com`) — only blogs by SAP employees or recognized MVPs. Include author name and date.
6. **Press / consultancy whitepapers** — only as supporting material, never as the primary source for a procedural step.

If you can't find an authoritative source for a step, do not invent one. Mark the step as needing follow-up in the PR description and skip it.
