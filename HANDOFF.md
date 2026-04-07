# Handoff: SAP S/4HANA Migration Skills Project

This bundle contains everything needed to author a Devin-native skills repo for ECC → S/4HANA migration. Hand it off to another Devin session (or a human) to execute.

## Contents

```
sap-skills-project/
├── HANDOFF.md                # this file
├── design/
│   ├── DESIGN.md             # full repo design (read first)
│   └── AUTHORING.md          # NORMATIVE rules every skill author must follow
├── briefs/
│   ├── _preamble.md          # shared instructions for every child session
│   └── sap-*.md              # 12 per-skill briefs
└── scaffold/
    └── sap-s4hana-migration-skills/   # working repo scaffold (1 commit on main)
        ├── README.md
        ├── LICENSE (Apache-2.0)
        ├── AUTHORING.md
        ├── .agents/skills/   # ⭐ canonical Devin-native location (empty, ready to fill)
        ├── scripts/
        │   ├── validate-skills.sh    # frontmatter + section validation
        │   └── new-skill.sh          # scaffold a new SKILL.md
        ├── docs/
        │   ├── installation-devin.md
        │   └── sources.md
        └── .github/workflows/validate.yml  # CI: validate + enforce mirror in sync
```

The scaffold has one commit on its local `main` branch. `.git` is included so the next session can push it.

## What still needs to happen

1. **Push the scaffold to GitHub.**
   - Target repo: `tedfoley-cog/sap-s4hana-migration-skills` (already created, empty).
   - The Devin GitHub App needs read/write access to that repo first — grant it at https://github.com/organizations/tedfoley-cog/settings/installations.
   - Push the existing `main` branch (or rename to a feature branch and PR if your workflow blocks direct pushes to main on a brand-new repo; main is currently empty on the remote so the first push is the bootstrap).

2. **Spawn 12 child sessions, one per skill**, each with this prompt template:
   ```
   <contents of briefs/_preamble.md>

   ---

   <contents of briefs/sap-<skill-name>.md>

   ---

   Repo: https://github.com/tedfoley-cog/sap-s4hana-migration-skills
   Base branch: main
   Branch name: add-skill-sap-<skill-name>
   ```
   The 12 skill names:
   1. sap-scoping
   2. sap-atc-readiness
   3. sap-simplification-database
   4. sap-spdd-spau
   5. sap-sum-dmo
   6. sap-functional-simplifications
   7. sap-hana-performance
   8. sap-modern-abap-rewrite
   9. sap-clean-core-extensibility
   10. sap-data-migration-cockpit
   11. sap-fiori-activation
   12. sap-migration-testing

   All 12 are independent and can run in parallel. Each child opens its own PR against `main`.

3. **Monitor and merge.** Each PR must pass `.github/workflows/validate.yml` (frontmatter validation). Merge PRs in any order — there are no dependencies between skills.

4. **Final pass.** After all 12 are merged, run `./scripts/validate-skills.sh` once more to confirm nothing drifted, and update `README.md` with the final skill catalog table if needed.

## Key design decisions (already locked in)

- **Devin-native layout**: `.agents/skills/<name>/SKILL.md`, single-level.
- **Apache-2.0 license** (not GPL like secondsky/sap-skills) for downstream reuse.
- **Strict frontmatter contract**: `name`, `description` (must start with "Use when"), `license`, `metadata.version`, `metadata.last_verified`, `metadata.s4hana_release`, `metadata.sources`, `related_skills`. Validated in CI.
- **7-section body structure** (in order): When to use → Prerequisites → Quick decision tree → Procedure → Worked example → Anti-patterns → References.
- **Citation-heavy**: minimum 5 inline citations per skill, all to authoritative SAP sources. No verbatim SAP material > 3 sentences. No `<!-- UNVERIFIED -->` markers in final.
- **Length cap**: ≤ 600 lines per SKILL.md (hard cap 1000).
- **Each skill is independently authored**: child sessions never edit sibling skills. Cross-references by relative path only.

## Verifying the scaffold locally before pushing

```bash
cd scaffold/sap-s4hana-migration-skills
./scripts/new-skill.sh sap-test-placeholder      # scaffold a dummy skill
./scripts/validate-skills.sh                      # should pass
rm -rf .agents/skills/sap-test-placeholder
```

All scripts have been tested in this exact way and work cleanly.

## Read order for the next session

1. `HANDOFF.md` (this file)
2. `design/DESIGN.md`
3. `design/AUTHORING.md` (normative — treat as a contract)
4. `briefs/_preamble.md`
5. One of the per-skill briefs to see the level of detail (e.g. `briefs/sap-scoping.md`)
6. `scaffold/sap-s4hana-migration-skills/README.md`
