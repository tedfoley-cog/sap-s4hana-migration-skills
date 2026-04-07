# sap-s4hana-migration-skills

Devin-native skills for **SAP ECC → S/4HANA migration** projects.

This repository is the canonical source of agent-readable runbooks for the major activities in a brownfield SAP system conversion: custom code scoping, ATC readiness, simplification database lookup, SPDD/SPAU adjustments, SUM/DMO cutover, functional simplifications (Business Partner, MATNR length, MATDOC, Universal Journal), HANA performance remediation, modern ABAP rewriting, clean-core extensibility, data migration cockpit, Fiori activation, and migration testing.

## Why this repo exists

[`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) is a great resource for **building new things** on modern SAP stacks (BTP, CAP, Fiori, RAP, CDS, HANA). It does **not** cover the brownfield ECC → S/4HANA migration path. This repo fills that gap.

These skills are intentionally narrow, runbook-style, and citation-heavy. Each skill is self-contained and immediately invocable by an AI agent without needing to read the rest of the repo.

## Supported harnesses

| Harness | Path scanned | Notes |
|---|---|---|
| **Devin** | `.agents/skills/<name>/SKILL.md` | Single source of truth. Devin's skill scanner is non-recursive at this path. |

## Skill catalog

| Skill | Phase |
|---|---|
| [`sap-scoping`](.agents/skills/sap-scoping/SKILL.md) | Pre-conversion |
| [`sap-atc-readiness`](.agents/skills/sap-atc-readiness/SKILL.md) | Pre-conversion |
| [`sap-simplification-database`](.agents/skills/sap-simplification-database/SKILL.md) | Pre-conversion |
| [`sap-spdd-spau`](.agents/skills/sap-spdd-spau/SKILL.md) | Conversion |
| [`sap-sum-dmo`](.agents/skills/sap-sum-dmo/SKILL.md) | Conversion |
| [`sap-functional-simplifications`](.agents/skills/sap-functional-simplifications/SKILL.md) | Functional |
| [`sap-hana-performance`](.agents/skills/sap-hana-performance/SKILL.md) | Post-conversion |
| [`sap-modern-abap-rewrite`](.agents/skills/sap-modern-abap-rewrite/SKILL.md) | Post-conversion |
| [`sap-clean-core-extensibility`](.agents/skills/sap-clean-core-extensibility/SKILL.md) | Strategy |
| [`sap-data-migration-cockpit`](.agents/skills/sap-data-migration-cockpit/SKILL.md) | Data |
| [`sap-fiori-activation`](.agents/skills/sap-fiori-activation/SKILL.md) | UX |
| [`sap-migration-testing`](.agents/skills/sap-migration-testing/SKILL.md) | Validation |

## Installation

### For Devin

Add this repo to your project as a submodule or copy the `.agents/skills/` directory into your project root. Devin will automatically pick up every skill on its next session.

```bash
git clone https://github.com/tedfoley-cog/sap-s4hana-migration-skills.git
cp -r sap-s4hana-migration-skills/.agents/skills/* /path/to/your/project/.agents/skills/
```

Or add a small symlink-style sync command to your project's environment config so the skills are kept in sync automatically. See [`docs/installation-devin.md`](docs/installation-devin.md).

## Authoring

If you're adding or improving a skill, read [`AUTHORING.md`](AUTHORING.md) first. It is normative.

Workflow:

```bash
./scripts/new-skill.sh sap-my-new-skill   # scaffolds the directory + SKILL.md template
# ... edit .agents/skills/sap-my-new-skill/SKILL.md ...
./scripts/validate-skills.sh              # frontmatter + link checks
git add .agents/skills
git commit -m "Add skill: sap-my-new-skill"
```

## License

Apache-2.0. See [`LICENSE`](LICENSE).

Sourced material from SAP documentation, SAP Notes, and SAP-samples GitHub repos is cited inline and never copied verbatim beyond fair-use limits. See [`docs/sources.md`](docs/sources.md) for the master attribution list.
