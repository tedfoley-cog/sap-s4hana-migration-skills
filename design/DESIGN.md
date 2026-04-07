# sap-s4hana-migration-skills — Design

A multi-harness skills repository for SAP ECC → S/4HANA migration projects.

**Primary target**: Devin (`.agents/skills/<name>/SKILL.md`, flat, single-level).
**Secondary target**: Claude Code / Factory Droid (`plugins/<name>/skills/<name>/SKILL.md` + `.claude-plugin/marketplace.json`), generated automatically from the Devin layout via a sync script.

This document is the contract every contributor (human or child Devin session) must follow.

---

## 1. Goals and non-goals

### Goals
1. Provide context-aware, runbook-style skills covering the full custom-code & functional path of an ECC → S/4HANA system conversion.
2. Be **drop-in usable by Devin** with no shim: the agent can `skill list` at the repo root and immediately discover all skills.
3. Be **drop-in usable by Claude Code / Factory Droid** via a generated `plugins/` mirror, so a single source of truth feeds both ecosystems.
4. Source content from authoritative material: SAP's Custom Code Migration Guide, official SAP-samples repos, SAP/abap-cleaner, the Simplification Item Catalog, and reputable SAP Community blogs. Cite everything.
5. Each skill is independently invocable. Skills cross-reference each other but never depend on shared mutable state.

### Non-goals
- We do **not** ship Claude Code slash commands, sub-agents, or hooks. Devin has no equivalent and we want zero divergence between targets. If Claude-Code-only consumers want commands, they can layer them on downstream.
- We do **not** ship code that connects to a live SAP system. These are reference / runbook skills, not tooling.
- We do **not** redistribute SAP proprietary documentation verbatim. Quote sparingly with attribution under fair use; link out for the rest.
- We do **not** try to replace SAP Joule for Developers. We complement it for users on Devin / Claude Code / other harnesses.

---

## 2. Repository layout

```
sap-s4hana-migration-skills/
├── README.md                          # Top-level pitch + install instructions for both harnesses
├── LICENSE                            # Apache-2.0 (skill content) - see §6
├── CONTRIBUTING.md                    # How to author a new skill (links to AUTHORING.md)
├── AUTHORING.md                       # Strict rules for SKILL.md format and content
├── CHANGELOG.md
│
├── .agents/
│   └── skills/                        # ⭐ Devin-native location (canonical source of truth)
│       ├── sap-scoping/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── scmon-workflow.md
│       │       └── susg-aggregation.md
│       ├── sap-atc-readiness/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── s4hana-readiness-variants.md
│       ├── sap-simplification-database/
│       │   └── SKILL.md
│       ├── sap-spdd-spau/
│       │   └── SKILL.md
│       ├── sap-sum-dmo/
│       │   └── SKILL.md
│       ├── sap-functional-simplifications/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── business-partner.md
│       │       ├── matnr-extension.md
│       │       ├── matdoc.md
│       │       └── new-gl-finance.md
│       ├── sap-hana-performance/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── sqlm-workflow.md
│       │       └── srtcm-checks.md
│       ├── sap-modern-abap-rewrite/
│       │   └── SKILL.md
│       ├── sap-clean-core-extensibility/
│       │   └── SKILL.md
│       ├── sap-data-migration-cockpit/
│       │   └── SKILL.md
│       ├── sap-fiori-activation/
│       │   └── SKILL.md
│       └── sap-migration-testing/
│           └── SKILL.md
│
├── plugins/                            # 🤖 Generated mirror for Claude Code / Factory Droid
│   └── ... (do NOT edit by hand; produced by scripts/sync-to-plugins.sh)
│
├── .claude-plugin/                     # Generated marketplace manifest
│   └── marketplace.json
│
├── scripts/
│   ├── sync-to-plugins.sh              # .agents/skills → plugins/ + marketplace.json
│   ├── validate-skills.sh              # Lint SKILL.md frontmatter, link checks
│   └── new-skill.sh                    # Scaffold a new skill from template
│
├── docs/
│   ├── installation-devin.md
│   ├── installation-claude-code.md
│   ├── skill-catalog.md                # Auto-generated index of all skills
│   └── sources.md                      # Master attribution list
│
└── .github/
    └── workflows/
        ├── validate.yml                # Run validate-skills.sh on PRs
        └── sync-plugins.yml            # Auto-regenerate plugins/ on push to main
```

### Why Devin-native is canonical (not Claude Code)

- Devin's skill scanner is **non-recursive** at `.agents/skills/`. The Claude Code layout is two levels deeper (`plugins/<x>/skills/<y>/`). Going Devin → plugins is a flatten-then-wrap operation; the reverse would require collision resolution.
- Devin format is the strict subset (no commands, agents, hooks). Generating the strict subset from a richer source is lossy in the wrong direction.
- One canonical source = one authoring workflow = no drift.

---

## 3. SKILL.md format

Every `SKILL.md` MUST start with YAML frontmatter, then a markdown body. The frontmatter is the only structured contract; everything else is human-readable runbook prose.

### Frontmatter schema

```yaml
---
name: sap-scoping                                    # kebab-case, matches directory
description: |                                       # MUST start with "Use when ..." so Devin's
  Use when scoping custom ABAP code prior to an     # discovery layer can match user intent.
  SAP ECC → S/4HANA system conversion: collecting   # Keep under ~600 chars. Mention concrete
  usage data with SCMON/SUSG, building deletion     # SAP transaction codes and product names.
  transports for unused objects, and producing a
  scoped worklist for ATC readiness checks.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"                       # ISO date you last validated content
  s4hana_release: "2023, 2024, 2025 FPS01"          # Releases this skill applies to
  sources:                                          # Free-form list of upstream references
    - "SAP Custom Code Migration Guide for S/4HANA 2025 FPS01"
    - "SAP Note 2185390"
related_skills:
  - sap-atc-readiness
  - sap-simplification-database
---
```

**Why "Use when ..." matters**: Devin's skill discovery uses the description field to decide whether to surface a skill for the current task. A description that starts with "Use when ..." and lists concrete trigger phrases (transaction codes, simplification names, error symptoms) dramatically improves recall. This convention is also what Anthropic recommends in the official Skill spec, so it works equally well in Claude Code.

### Body structure (recommended template)

```markdown
# <Skill Title>

## When to use this skill
Bullet list of concrete situations. Echo and expand the frontmatter description.

## Prerequisites
What the user / agent should already have done before invoking this skill.
Cross-link to other skills in this repo using relative paths.

## Quick decision tree
Tight flowchart-as-prose so the agent can pick the right sub-procedure
without reading the whole document.

## Procedure
Numbered steps. Each step:
- States the action ("Run transaction SCMON in the production system")
- States the expected outcome ("You should see usage data accumulating in /SDF/SCMON_DATA")
- Lists failure modes and how to recover
- Cites the SAP source (Note number, Help portal URL, blog link)

## Worked example
At least one concrete walked-through example with realistic object names.
This is what the agent will pattern-match against.

## Anti-patterns
Things the agent (or human) is likely to do wrong. Include the failure
symptom so the agent can self-correct mid-task.

## References
Link list. Use stable URLs (help.sap.com permalinks, archived blog versions
where possible). Each reference gets a one-line description so the agent
knows whether it's worth fetching.
```

### Hard rules

1. **No images embedded as base64.** If a diagram is essential, include it as a separate file in `references/` and link to it.
2. **No secrets, license keys, or customer-specific identifiers.** Use placeholders like `<system-id>` and `<client-no>`.
3. **No verbatim copying of SAP-copyrighted documentation longer than ~3 sentences.** Paraphrase and cite. Embedded SAP code samples must carry a comment with the upstream source.
4. **Length cap**: target ≤ 600 lines per SKILL.md. If a topic needs more, split into a sibling SKILL.md or push depth into `references/`.
5. **No external runtime dependencies.** Skills are pure markdown. No scripts that get executed by the harness.
6. **Verify recency**: every skill carries a `last_verified` date in frontmatter. If you can't verify a step, mark it `<!-- UNVERIFIED -->` inline.

---

## 4. Skill catalog (12 skills)

| # | Skill | Phase | Purpose |
|---|---|---|---|
| 1 | **sap-scoping** | Pre-conversion | SCMON / SUSG usage capture, dead-code identification, deletion transports |
| 2 | **sap-atc-readiness** | Pre-conversion | Remote & local ATC checks with `S4HANA_READINESS_*` variants; quick-fix workflow |
| 3 | **sap-simplification-database** | Pre-conversion | Querying the Simplification Item Catalog and Simplification Database; mapping items to SAP Notes |
| 4 | **sap-spdd-spau** | Conversion / post-conversion | SPDD (dictionary), SPAU (repository), SPAU_ENH (enhancement) adjustment workflows |
| 5 | **sap-sum-dmo** | Conversion | Software Update Manager + Database Migration Option playbook; downtime-optimized vs. standard |
| 6 | **sap-functional-simplifications** | Functional | BP for Customer/Vendor, MATNR length extension, MATDOC, New GL / Universal Journal, MM-IM table changes |
| 7 | **sap-hana-performance** | Post-conversion | SQLM, SRTCM, expensive-statement remediation, code-pushdown patterns (CDS / AMDP) |
| 8 | **sap-modern-abap-rewrite** | Post-conversion | Bringing legacy ABAP to modern syntax (inline declarations, table expressions, REDUCE, string templates) — pairs with abap-cleaner |
| 9 | **sap-clean-core-extensibility** | Strategy | In-app vs. side-by-side vs. developer extensibility decision tree; clean-core principles; ABAP Cloud readiness |
| 10 | **sap-data-migration-cockpit** | Data | LTMC / LTMOM / Migration Cockpit object selection, staging vs. file approach, custom migration object cookbook |
| 11 | **sap-fiori-activation** | UX | Post-conversion Fiori app discovery (Fiori App Library), activation steps, role assignment, launchpad setup |
| 12 | **sap-migration-testing** | Validation | Regression strategy, ATC unit tests, functional sanity test packs, cutover dry runs |

Each skill is owned by exactly one child session in the initial build. After v0.1, contributors update them independently.

---

## 5. Sync script (`scripts/sync-to-plugins.sh`)

The sync script reads `.agents/skills/*/SKILL.md`, parses the YAML frontmatter, and emits:

1. `plugins/<skill>/skills/<skill>/SKILL.md` — copy of the source.
2. `plugins/<skill>/skills/<skill>/README.md` — auto-generated keyword index from frontmatter.
3. `plugins/<skill>/.claude-plugin/plugin.json` — Claude Code plugin manifest derived from frontmatter (name, description, version, license, keywords, category=`sap-migration`).
4. `plugins/<skill>/skills/<skill>/references/*` — copy of references dir if present.
5. `.claude-plugin/marketplace.json` — top-level marketplace catalog listing all plugins.

The script is idempotent. CI runs it on every push to `main` and fails if `plugins/` is out of sync, forcing contributors to commit the regenerated mirror.

We will **not** publish a separate sync from `plugins/` back to `.agents/skills/`. The Devin layout is the only writable layout.

---

## 6. License

- **Repo content (SKILL.md, references, docs)**: Apache-2.0. Permissive, attribution-required, compatible with both commercial and open-source consumers, more practical than GPL-3.0 for downstream skill marketplaces. Differs deliberately from secondsky/sap-skills (GPL-3.0) — we want maximum reuse.
- **Sourced material**: Each reference file declares its upstream license at the top. Where SAP material is used, we paraphrase under fair use and link out; we never bundle the SAP guide PDF.
- **Code samples**: ABAP snippets adapted from SAP-samples/abap-cheat-sheets (Apache-2.0) keep an attribution comment.

---

## 7. Authoring workflow for child sessions

Each child session that owns a skill MUST:

1. Read this design doc (`design/DESIGN.md`) and the authoring rules (`AUTHORING.md`) first.
2. Create the directory `.agents/skills/<skill-name>/` and write `SKILL.md` following the frontmatter schema in §3.
3. Place supporting reference docs under `.agents/skills/<skill-name>/references/`.
4. Cite all sources inline. Every factual claim about SAP behavior gets a citation (Note number, Help portal URL, or blog link).
5. Run `scripts/validate-skills.sh` and `scripts/sync-to-plugins.sh` locally; commit both `.agents/skills/` and `plugins/` changes.
6. Open a PR to `main` titled `Add skill: <skill-name>`. Include in the PR body: source list, target SAP releases, and any `<!-- UNVERIFIED -->` flags that need human follow-up.
7. Do **not** edit other skills. Cross-reference them by relative path; if you spot a needed change in a sibling skill, leave a comment in the PR.

---

## 8. Quality bar (definition of done for v0.1)

A skill is ready to merge when:

- [ ] Frontmatter validates against the schema in §3.
- [ ] Description starts with "Use when ..." and lists at least 3 concrete trigger phrases.
- [ ] Body has all 7 sections from the recommended template.
- [ ] At least 1 worked example with realistic object names.
- [ ] At least 5 inline citations to authoritative sources.
- [ ] No SAP copyrighted material > 3 sentences verbatim.
- [ ] `last_verified` date is within the past 14 days.
- [ ] `validate-skills.sh` passes.
- [ ] Cross-links to related skills resolve.
- [ ] PR description lists every source and any unverified items.

---

## 9. Out of scope for v0.1

- A live MCP server that queries the actual Simplification Item Catalog (could be a v0.2 add-on).
- Automated PR generation that opens ATC findings as GitHub issues (also v0.2).
- Translations (English only for v0.1; SAP customer base is global but we'd rather get content right first).
- A playbook layer on top of the skills (Devin playbooks could orchestrate multiple skills into a full-migration runbook — v0.2).
