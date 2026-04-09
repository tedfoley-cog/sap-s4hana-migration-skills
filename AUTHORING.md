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

### 3a. Content ordering and the "Lost in the Middle" problem

Large Language Models reliably use information at the **start** and **end** of their context window but degrade sharply on content in the middle (Liu et al., "Lost in the Middle," 2023). This has direct consequences for skill authoring:

- **Put routing-critical content at the top**: The `## When to use this skill` and `## Quick decision tree` sections appear first precisely because they determine whether the agent continues using this skill or pivots.
- **Put corrective content at the end**: `## Anti-patterns` comes near the bottom so the agent sees "don't do X" warnings right before it starts generating output.
- **Push deep content to reference files**: Long worked examples and reference tables in the middle of the SKILL.md are the most likely to be under-attended. Extract them to `references/` and leave a 2–3 line summary + link in the body.

## 4. Citation rules

- Every factual claim about SAP behavior, transaction code, table name, or simplification gets an inline citation. Format: `(SAP Note 2185390)` or `([SAP Help](https://help.sap.com/...))`.
- Stable URLs only. Prefer `help.sap.com` permalinks. Wayback Machine snapshots are acceptable for older blog material.
- Each `references/*.md` file starts with an attribution block listing upstream sources and licenses.
- Never paste more than ~3 sentences of SAP-copyrighted documentation verbatim. Paraphrase and link out.

## 5. Length

- Target: ≤ 500 lines per `SKILL.md`. Warn at 500, hard cap: 600 lines.
- If a topic needs more depth, push it into `references/` and link from the body.
- The agent reads the whole `SKILL.md` when invoked. Every token competes with the conversation history — the context window is a public good.
- Worked examples are the primary extraction target. Keep a 2–3 line summary + link in the body; move the full walkthrough to `references/worked-example-*.md`.

### 5a. Progressive disclosure

Skills support three levels of progressive disclosure:

| Level | What loads | When | Budget |
|---|---|---|---|
| **1 — Metadata** | `name` + `description` from frontmatter | Session start (all skills) | ~50 tokens per skill |
| **2 — Body** | Full `SKILL.md` body | Agent decides skill is relevant | ≤ 500 lines |
| **3 — Reference files** | `references/*.md` or `references/*.sh` | Agent follows a link from the body | Unbounded |

- Level 1 is always loaded. Write descriptions as if they are the only thing the agent will ever see (because often they are).
- Level 2 should act like a "table of contents in an onboarding guide" — enough to execute the task, with links to deeper content.
- Level 3 files are read on demand. They can be as long as needed but should have a table of contents at the top if > 50 lines.
- Maximum nesting depth: 2 levels of file references from the body (body → reference file → no further links to other reference files).

### 5b. Degrees of freedom

Match the prescriptiveness of your prose to the fragility of the task:

- **High freedom** (advisory prose, options, trade-offs): Use for subjective tasks like architecture decisions, code review, scoping judgments. Example: the `## Quick decision tree` in `sap-clean-core-extensibility`.
- **Low freedom** (literal scripts, exact commands, step-by-step): Use for deterministic operations where deviation causes failure. Example: SUM phase commands, ATC variant setup, CLI install sequences.
- **Executable scripts**: For fully deterministic operations (e.g., installing CLIs), bundle a `references/*.sh` script that the agent can run directly instead of regenerating commands from prose. See `sap-cli-toolbelt/references/install-cli-tools.sh`.

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
