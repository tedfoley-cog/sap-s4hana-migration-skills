## Shared preamble for all child sessions

You are authoring a single skill in the new repository **`tedfoley-cog/sap-s4hana-migration-skills`**. The repo's purpose is to provide Devin-native skills for SAP ECC → S/4HANA migration projects.

### What you must do

1. **Clone the repo**:
   ```bash
   git clone https://github.com/tedfoley-cog/sap-s4hana-migration-skills.git
   cd sap-s4hana-migration-skills
   ```
2. **Read the design docs first**, in order:
   - `README.md`
   - `AUTHORING.md` — strict rules for SKILL.md format. Treat this as normative.
   - `docs/sources.md` — master source list.
3. **Create exactly one skill** at `.agents/skills/<skill-name>/SKILL.md` (see your task brief below for the exact name and scope).
   - Add reference files under `.agents/skills/<skill-name>/references/` if you need to push depth out of the main SKILL.md.
   - Do NOT edit any other skill, the scripts, or the design docs.
4. **Frontmatter rules** (must follow `AUTHORING.md` §2 exactly):
   - `name` must equal the directory name (kebab-case, prefixed `sap-`).
   - `description` MUST start with "Use when ..." and list at least 3 concrete trigger phrases (transaction codes, error symptoms, simplification names).
   - `license: Apache-2.0`.
   - `metadata.last_verified` is today's date.
   - `metadata.s4hana_release` lists the releases this skill applies to.
   - `metadata.sources` lists the upstream sources you actually consulted.
   - `related_skills` lists sibling skills in this repo (see catalog below) that are relevant.
5. **Body structure** must use exactly the 7 sections from `AUTHORING.md` §3:
   - `## When to use this skill`
   - `## Prerequisites`
   - `## Quick decision tree`
   - `## Procedure`
   - `## Worked example`
   - `## Anti-patterns`
   - `## References`
6. **Citation rules** (`AUTHORING.md` §4):
   - Every factual claim about SAP behavior gets an inline citation.
   - Prefer SAP Custom Code Migration Guide → SAP Notes → SAP Help Portal → SAP-samples GitHub → SAP Community blogs.
   - Never paste more than 3 sentences of SAP-copyrighted material verbatim.
7. **Length cap**: ≤ 600 lines for the SKILL.md body. Push depth into `references/`.
8. **Quality bar** (`AUTHORING.md` "Quality bar"):
   - At least 1 worked example with realistic object names.
   - At least 5 inline citations.
   - No `<!-- UNVERIFIED -->` markers in the final version.
9. **Validation**:
   ```bash
   ./scripts/validate-skills.sh
   ```
   Commit `.agents/skills/<your-skill>/`.
10. **PR**:
    - Branch: `add-skill-<skill-name>`
    - Title: `Add skill: <skill-name>`
    - Body: list every source you cited, target SAP releases, and any items you could not verify (which must be removed, not flagged).
    - Base branch: `main`.

### Catalog of sibling skills (for cross-references)

When filling in `related_skills` in your frontmatter, pick from this list. Other agents are authoring these in parallel; assume their directories will exist by the time the repo merges.

| Skill | Phase |
|---|---|
| sap-scoping | Pre-conversion |
| sap-atc-readiness | Pre-conversion |
| sap-simplification-database | Pre-conversion |
| sap-spdd-spau | Conversion |
| sap-sum-dmo | Conversion |
| sap-functional-simplifications | Functional |
| sap-hana-performance | Post-conversion |
| sap-modern-abap-rewrite | Post-conversion |
| sap-clean-core-extensibility | Strategy |
| sap-data-migration-cockpit | Data |
| sap-fiori-activation | UX |
| sap-migration-testing | Validation |

### Hard rules

- ❌ Do NOT edit sibling skills. If you spot a needed change, mention it in your PR description.
- ❌ Do NOT invent SAP behavior. If you can't cite it, don't write it.
- ❌ Do NOT embed images as base64. Put diagrams in `references/` and link to them.
- ❌ Do NOT use `gh` CLI to create the PR — use the standard PR creation flow.
- ❌ Do NOT push directly to `main`. Always go through a PR.
- ✅ DO include realistic ABAP / transaction-code / table-name examples.
- ✅ DO cite authoritative sources for every factual claim.
- ✅ DO run the validate script before committing.

### Definition of done

You are done when:
1. Your PR is open against `main` in `tedfoley-cog/sap-s4hana-migration-skills`.
2. CI is passing.
3. Your skill is fully self-contained and would be invocable by another Devin session today.

Report completion by sending a final `message_user` with:
- The PR URL.
- The list of citations you used.
- Any cross-skill cleanup you noticed (don't fix it, just flag it).

---

## Your specific task

(See the per-skill brief that follows this preamble.)
