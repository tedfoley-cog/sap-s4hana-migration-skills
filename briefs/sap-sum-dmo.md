## Brief: sap-sum-dmo

**Skill name**: `sap-sum-dmo`
**Phase**: Conversion (the actual cutover)
**Owner**: Software Update Manager + Database Migration Option playbook for ECC → S/4HANA system conversion.

### Scope of this skill

How to plan and execute the **SUM** (Software Update Manager) tool to perform a **system conversion** from ECC to S/4HANA, including the **DMO** (Database Migration Option) for the simultaneous database swap to SAP HANA.

Cover:
- The three S/4HANA transition paths and where SUM/DMO fits: **system conversion** (in-place, this skill's focus), **new implementation** (greenfield), **selective data transition** (bluefield).
- SUM phases at a high level: **PREPARE → CHECKS → ROADMAP → EXECUTE → POSTPROCESSING**.
- DMO flavors: **standard DMO**, **DMO with System Move**, **Downtime-Optimized DMO** (dDMO), and the newer **dDMO with System Move**.
- Pre-checks: **`/SDF/RC_START_CHECK`**, **maintenance planner** stack file generation, custom code worklist hand-off.
- Resource sizing: source vs target DB, downtime windows, memory for the **R3load** processes during DMO.
- Cutover timeline: typical phase durations, parallelization knobs (R3load processes, table splitter), how to monitor progress.
- Backup and rollback strategy. SUM has a documented rollback path before activation; after activation, only restore-from-backup.
- Hand-off points to the SPDD/SPAU skill (during the conversion) and to the post-conversion stabilization skills.

### Key sources to consult

1. **SUM Guide for S/4HANA** (DMO with System Move and standard DMO variants) on `help.sap.com`.
2. SAP Note **2882748** — "Software Update Manager 2.0 SP*: Central Note".
3. SAP Note **2393060** — "Downtime-Optimized DMO".
4. SAP Note **2351294** — "DMO with System Move".
5. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — appendix "Integration with SUM".
6. Maintenance Planner (`https://maintenanceplanner.cloud.sap`).

### Worked example

Walk through a fictional ECC 6.07 → S/4HANA 2025 conversion on Oracle → HANA:
1. Maintenance Planner generates the stack file for the target S/4HANA 2025 FPS01.
2. Pre-checks (`/SDF/RC_START_CHECK`) flag 4 must-fix items; team resolves them.
3. SUM is downloaded and started in **single-system DMO** mode.
4. PREPARE phase runs ~36 hours; CHECKS phase pauses for the SPDD prompt — admin opens SPDD, applies adjustments, releases transport, resumes SUM.
5. EXECUTE phase: data migration runs in parallel R3load streams; downtime window is 14 hours.
6. POSTPROCESSING includes SPAU (handed to developer team), conversion of BP, MATNR length extension, etc.

### Anti-patterns

- Running SUM without the Custom Code Migration worklist completed → expensive surprises during downtime.
- Sizing the target HANA DB based on the source DB size rather than the **simplification-adjusted** size (e.g., MATDOC consolidates many MM tables, often shrinks the footprint significantly).
- Not testing the SUM run in a sandbox first → first-time-in-PROD is the highest-risk path.
- Forgetting to run the Maintenance Planner each time the target stack changes; stack files have an expiry.
- Using standard DMO when downtime requirements actually need dDMO; deciding mid-cutover is too late.

### Related skills

`sap-spdd-spau`, `sap-atc-readiness`, `sap-functional-simplifications`, `sap-migration-testing`
