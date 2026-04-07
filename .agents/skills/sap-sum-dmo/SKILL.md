---
name: sap-sum-dmo
description: |
  Use when planning or executing an SAP ECC to S/4HANA system conversion
  using the Software Update Manager (SUM) with Database Migration Option (DMO):
  running transaction /SDF/RC_START_CHECK for pre-conversion readiness,
  generating a Maintenance Planner stack file for S/4HANA target releases,
  choosing between standard DMO, DMO with System Move, or downtime-optimized
  DMO (dDMO), sizing the target HANA database and R3load parallelism,
  troubleshooting SUM roadmap phases (EXTRACTION, CHECKS, PRE-PROCESSING,
  EXECUTION, POST-PROCESSING), resolving SPDD/SPAU prompts during SUM,
  or planning cutover downtime windows for brownfield S/4HANA conversions.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025 FPS01"
  sources:
    - "SUM Guide: Conversion to SAP S/4HANA or SAP BW/4HANA using SUM (help.sap.com)"
    - "Conversion Guide for SAP S/4HANA 2025 (help.sap.com)"
    - "SAP Note 2882748 — SUM 2.0 Central Note"
    - "SAP Note 2393060 — Downtime-Optimized DMO"
    - "SAP Note 2351294 — DMO with System Move"
    - "SAP Note 2399707 — Conversion Pre-Checks"
    - "SAP Note 1976487 — S/4HANA Simplification List"
    - "SAP Custom Code Migration Guide for S/4HANA 2025 FPS01"
    - "Database Migration Option: Target Database SAP HANA (SUM DMO Guide, help.sap.com)"
    - "Maintenance Planner (maintenanceplanner.cloud.sap)"
related_skills:
  - sap-atc-readiness
  - sap-cli-toolbelt
  - sap-fiori-activation
  - sap-functional-simplifications
  - sap-migration-testing
  - sap-spdd-spau
---

# SUM/DMO System Conversion Playbook

## When to use this skill

- You need to **convert an SAP ECC system to S/4HANA** using the brownfield (system conversion) approach with SUM.
- You are choosing between **standard DMO**, **DMO with System Move**, **downtime-optimized DMO (dDMO)**, or **dDMO with System Move** for a simultaneous database migration to SAP HANA.
- You must generate or validate a **Maintenance Planner stack file** for a target S/4HANA release (2023, 2024, or 2025).
- You are running **`/SDF/RC_START_CHECK`** pre-conversion checks and need to interpret or resolve the findings.
- You need to plan **cutover downtime windows**, size the target HANA database, or tune **R3load parallelism** for the data migration phase.
- SUM has stopped at a **roadmap phase** (EXTRACTION, CHECKS, PRE-PROCESSING, EXECUTION, POST-PROCESSING) and you need to diagnose and resume.
- You need to coordinate the **SPDD/SPAU prompt** that SUM raises during the conversion with the SPDD/SPAU adjustment team.
- You are planning the **rollback strategy** for a system conversion: understanding the point-of-no-return (activation phase) and backup requirements.

## Prerequisites

1. **Source system**: SAP ECC 6.0 (EHP 0–8) or SAP Business Suite on a supported source database (Oracle, DB2, SQL Server, MaxDB, or ASE). The source kernel must be at a level supported by the target SUM SP ([SAP Note 2882748](https://me.sap.com/notes/2882748)).
2. **Maintenance Planner access**: An S-user with the role *Maintenance Planner Administrator* on [maintenanceplanner.cloud.sap](https://maintenanceplanner.cloud.sap) to generate the stack XML file ([SAP Help: Maintenance Planner](https://help.sap.com/docs/maintenance-planner)).
3. **Custom code readiness**: The custom code migration worklist should be completed — ATC checks run, critical findings resolved, and a scoped list of objects handed off. See skill `sap-atc-readiness`.
4. **Simplification item review**: All applicable simplification items from the Simplification Item Catalog for the target release must be reviewed and pre-conversion actions completed ([SAP Note 1976487](https://me.sap.com/notes/1976487)). See skill `sap-functional-simplifications`.
5. **Target HANA infrastructure**: The target SAP HANA database server must be installed, sized, and network-accessible from the source application server. For DMO with System Move, a separate target application server is also required ([SAP Note 2351294](https://me.sap.com/notes/2351294)).
6. **SUM download**: Download the latest SUM 2.0 SP stack from SAP Software Download Center. Always use the latest SP to get current bug fixes ([SAP Note 2882748](https://me.sap.com/notes/2882748)).
7. **Backup**: A verified full backup of the source system (database + file system) must exist before starting SUM. This is your only rollback path after the activation phase.

## Quick decision tree

```
Is this a new SAP implementation (no existing data)?
  YES --> Greenfield / New Implementation (not this skill)
  NO  --> Is the goal to keep the existing SID and data in place?
            YES --> System Conversion (this skill)
                    --> Is the source DB already SAP HANA?
                          YES --> SUM without DMO (software-only update)
                          NO  --> SUM with DMO (this skill's primary scope)
                                  --> Will the target run on the SAME server?
                                        YES --> Standard DMO
                                        NO  --> DMO with System Move
                                              (SAP Note 2351294)
                                  --> Is downtime > 24h unacceptable?
                                        YES --> Downtime-Optimized DMO (dDMO)
                                              (SAP Note 2393060)
                                        NO  --> Standard DMO is simpler
            NO  --> Selective Data Transition / Shell Conversion
                    (not this skill — see landscape transformation tools)
```

**DMO flavor selection summary**:

| Flavor | Use case | Key characteristic |
|---|---|---|
| **Standard DMO** | Same-host conversion, downtime tolerance > 24h | Simplest; single SUM run migrates DB + software in one step ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)) |
| **DMO with System Move** | Target HANA on a different host/SID | SUM orchestrates export from source, import on target; requires target app server pre-installed ([SAP Note 2351294](https://me.sap.com/notes/2351294)) |
| **Downtime-Optimized DMO (dDMO)** | Tight downtime window; same host | Replicates data via trigger-based approach during uptime; only delta applied in downtime ([SAP Note 2393060](https://me.sap.com/notes/2393060)) |
| **dDMO with System Move** | Tight downtime + different target host | Combines trigger-based replication with system move ([SAP Note 2393060](https://me.sap.com/notes/2393060)) |

## Procedure

### Phase 0: Planning and Maintenance Planner

1. Log in to [Maintenance Planner](https://maintenanceplanner.cloud.sap) and select **Plan for SAP S/4HANA**. Choose the target release (e.g., S/4HANA 2025 FPS01) and enter your source system's product version and installed components ([SAP Help: Maintenance Planner](https://help.sap.com/docs/maintenance-planner)).
2. Maintenance Planner validates component compatibility and generates a **stack XML file** containing all required archives (SAP_BASIS, SAP_ABA, S4CORE, etc.). Download the stack file and place it in the SUM `download` directory.
3. **Regenerate the stack file** whenever the target release or add-on scope changes. Stack files have an implicit validity — always use a freshly generated file for each SUM cycle to avoid version mismatches ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)).

### Phase 1: Pre-checks (`/SDF/RC_START_CHECK`)

4. Run transaction **`/SDF/RC_START_CHECK`** in the source system. This report validates readiness across multiple dimensions: kernel version, SPAM/SAINT status, transport consistency, simplification item prerequisites, and database compatibility ([SAP Note 2399707](https://me.sap.com/notes/2399707)).
5. Resolve all **RED** findings before starting SUM. YELLOW findings are warnings — review them but they do not block the conversion. The report output can be downloaded as an XML file for tracking.
6. Verify that the custom code migration worklist from ATC is complete. SUM does not re-check custom code, but unresolved issues will cause runtime errors post-conversion (hand-off from skill `sap-atc-readiness`).

### Phase 2: SUM Download and Initialization

7. Extract the SUM archive on the source application server under `/usr/sap/<SID>/SUM` (or the equivalent OS-specific path). The SUM directory must be on a file system with sufficient space — plan for at least **2x the source database size** for working storage during DMO ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)).
8. Start SUM using `STARTUP` (on Linux: `./STARTUP confighostagent`). SUM opens a browser-based GUI on port **1128** (HTTP) or **1129** (HTTPS) of the application server.
9. In the SUM GUI, select the scenario: **System Conversion — SAP S/4HANA** and choose the DMO flavor (standard DMO, DMO with System Move, dDMO). Point SUM to the Maintenance Planner stack XML file.

### Phase 3: EXTRACTION (Uptime)

10. SUM reads the source repository and extracts software component metadata. This phase runs in **uptime** and does not affect end users. Duration depends on the number of software components — typically 2–8 hours for a standard ECC system.

### Phase 4: CHECKS (Uptime with Interactive Prompts)

11. SUM performs automated checks: DDIC consistency, transport request status, add-on compatibility, and target stack validation. Resolve any errors reported before proceeding.
12. **SPDD prompt**: SUM pauses and prompts the administrator to run transaction **SPDD** to adjust SAP dictionary objects modified by the conversion. The SPDD administrator must review each object, decide on adjustments, and release the transport. Resume SUM after SPDD is complete (hand-off to skill `sap-spdd-spau`) ([SAP Note 1973241](https://me.sap.com/notes/1973241)).

### Phase 5: PRE-PROCESSING (Uptime / Shadow Import)

13. SUM imports the target software into a **shadow repository** (shadow instance) while the productive system remains online. This is the longest uptime phase — typically 12–36 hours depending on the number of objects and I/O performance.
14. During this phase, SUM also performs **structure conversions** for DDIC changes that can be prepared in advance. Monitor progress via the SUM GUI's roadmap view.

### Phase 6: EXECUTION (Downtime)

15. **Downtime begins.** SUM locks users out by setting the system to maintenance mode. From this point, the source system is unavailable to end users.
16. **Database migration (DMO)**: SUM uses **R3load** processes to export data from the source database and import it into the target SAP HANA database. This is the most time-consuming downtime activity ([DMO Guide](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf)).
    - **R3load parallelism**: Configure the number of parallel R3load export and import processes via the SUM parameter `PARALLEL_JOBS_RLOAD`. A typical starting point is **8–16 parallel jobs**, tuned based on available CPU cores and I/O bandwidth on both source and target.
    - **Table splitting**: For very large tables (e.g., BSEG, ACDOCA, MSEG, MATDOC), SUM can split the export/import into multiple parallel streams using the **table splitter**. Configure via `TABLE_SPLITTING=TRUE` in the SUM configuration. This can reduce migration time for large tables by 50–70% ([DMO Guide](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf)).
17. **Repository switch and activation**: SUM switches the ABAP repository from the source to the target (shadow → productive). This is the **point of no return** — after activation, rollback is only possible by restoring from backup ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)).
18. **SPAU prompt**: SUM pauses for transaction **SPAU** adjustments — modifications to SAP objects that were overwritten. SPAU work can be parallelized across developers. Resume SUM after SPAU is complete (hand-off to skill `sap-spdd-spau`).
19. **Data conversions**: SUM executes mandatory S/4HANA data conversions during downtime. Key conversions include:
    - **Business Partner synchronization** (CVI — Customer/Vendor Integration) ([SAP Note 2265093](https://me.sap.com/notes/2265093))
    - **Material document migration** to MATDOC ([SAP Note 2227764](https://me.sap.com/notes/2227764))
    - **Universal Journal migration** to ACDOCA ([SAP Note 2270407](https://me.sap.com/notes/2270407))
    - **Material number length extension** if configured ([SAP Note 2270333](https://me.sap.com/notes/2270333))
    See skill `sap-functional-simplifications` for details on each conversion.

### Phase 7: POST-PROCESSING (Final Downtime)

20. SUM performs final cleanup: recompilation of ABAP programs, regeneration of screens, and activation of post-conversion tasks. The system is brought back online after this phase completes.
21. Run **`/SDF/RC_START_CHECK`** again in post-conversion mode to verify the converted system is consistent.
22. Hand off to post-conversion stabilization: HANA performance tuning (skill `sap-hana-performance`), functional verification (skill `sap-migration-testing`), and modern ABAP cleanup (skill `sap-modern-abap-rewrite`).

### Downtime-Optimized DMO (dDMO) — Additional Steps

23. If using dDMO, SUM creates **trigger-based replication** on the source tables during the uptime phases. Data is replicated to the target HANA database continuously while the source system remains online ([SAP Note 2393060](https://me.sap.com/notes/2393060)).
24. During downtime, only the **delta changes** accumulated since the last replication cycle need to be applied. This can reduce downtime from 24+ hours to 6–12 hours for large databases.
25. dDMO requires additional prerequisites: the source database must support trigger-based change capture, and additional temporary storage is needed for the replication logs. Consult [SAP Note 2393060](https://me.sap.com/notes/2393060) for database-specific requirements.

### Backup and Rollback Strategy

26. **Before SUM start**: Take a full database backup and file system backup of `/usr/sap/<SID>` and the SUM directory. This is your primary rollback path.
27. **Before downtime (Phase 6)**: Take another incremental backup. If the conversion fails during downtime but before activation, SUM provides a **controlled rollback** via the SUM GUI's "Reset" option that reverts the shadow import.
28. **After activation (step 17)**: Rollback is only possible by **restoring the full backup** taken before SUM start. The activation step is irreversible within SUM. Plan the backup/restore procedure and validate the restore time before the production cutover ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)).


### CLI usage

> **No CLI for SUM itself.** The Software Update Manager (SUM) runs as an interactive web-based tool on the target SAP host (port 1128/1129). It requires OS-level access to the SAP application server and cannot be driven from a remote Devin sandbox. The SUM binary (`STARTUP`) is executed locally on the server, not via a network CLI ([SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf)).

Devin's role for this skill is **advisory**: generating runbook steps, validating Maintenance Planner stack files, and documenting cutover plans. For CLI-assisted pre-checks and post-conversion validation, see the sibling skills:

- `sap-atc-readiness` — `sapcli atc run` for pre-conversion custom code checks
- `sap-hana-performance` — `hdbsql` for post-conversion performance queries
- `sap-migration-testing` — `sapcli aunit run` for post-conversion unit test execution

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

**Scenario**: Convert a fictional ECC 6.07 (EHP7) system `E01` on Oracle 19c to S/4HANA 2025 FPS01 on SAP HANA 2.0 SPS07. Source database size: 4.2 TB. Target downtime window: 16 hours.

### Step 1 — Maintenance Planner

The basis admin logs in to [Maintenance Planner](https://maintenanceplanner.cloud.sap), selects system `E01` (SID registered via SAP Solution Manager landscape data), and plans for target release **SAP S/4HANA 2025 FPS01**. Maintenance Planner detects installed add-ons (IS-OIL, HR-RENEWAL) and validates compatibility. The generated stack XML includes:

- SAP_BASIS 758, SAP_ABA 758, S4CORE 110, SAP_HR 608
- Target kernel: 758 (64-bit Unicode)
- DMO-specific archives for HANA client and R3load

### Step 2 — Pre-checks

```
/SDF/RC_START_CHECK
```

Results:
- **RED**: SPAM queue not empty — 2 pending Support Packages. *Resolution*: Apply or delete the pending SPs via SPAM.
- **RED**: Simplification item S4TWL-000123 requires pre-conversion data cleanup in table `KONV`. *Resolution*: Run report `/SDF/RC_CONV_PRECHECK_KONV` to archive obsolete condition records.
- **RED**: Custom code check variant `S4HANA_READINESS` not yet executed. *Resolution*: Run ATC with variant `S4HANA_READINESS` via `ATC` transaction (hand-off to `sap-atc-readiness`).
- **YELLOW**: Table BSEG has 890 million records — consider archiving before conversion to reduce downtime. *Decision*: Team archives FI documents older than 7 years, reducing BSEG to 340 million records.

### Step 3 — DMO flavor selection

With 4.2 TB source data (reduced to ~3.1 TB after archiving), the team estimates:
- Standard DMO data migration: ~28 hours (exceeds 16-hour window)
- dDMO: ~10 hours downtime (delta-only migration)

**Decision**: Use **standard DMO** (not dDMO) because a sandbox rehearsal showed that with 16 parallel R3load processes and table splitting on BSEG, ACDOCA, MSEG, and MATDOC, the data migration completes in ~11 hours, fitting within the 16-hour window. dDMO adds complexity (trigger overhead on the source Oracle DB) that is not justified when standard DMO fits the window.

### Step 4 — SUM execution

```bash
# On application server as <sid>adm
cd /usr/sap/E01/SUM
./STARTUP confighostagent
```

SUM GUI opens at `https://sapapp01:1129/lmsl/sumabap/E01`.

| Phase | Duration | Notes |
|---|---|---|
| EXTRACTION | 3 h | Uptime; read 48,000 repository objects |
| CHECKS | 1 h | SPDD prompt: admin opens `SPDD`, adjusts 12 dictionary objects (3 modified data elements, 9 modified domains), releases transport `E01K900123`, resumes SUM |
| PRE-PROCESSING | 28 h | Shadow import of S4CORE, SAP_HR; uptime throughout |
| **EXECUTION** | **14 h** | **Downtime window opens at Friday 20:00** |
| — R3load export/import | 11 h | 16 parallel R3load jobs; table splitter on BSEG (4 splits), ACDOCA (8 splits), MSEG (2 splits) |
| — Repository switch | 0.5 h | Point of no return |
| — SPAU | 1.5 h | 87 objects adjusted by 4 developers in parallel |
| — Data conversions | 1 h | BP sync (CVI), MATDOC migration, Universal Journal |
| POST-PROCESSING | 2 h | ABAP recompilation, screen regeneration |
| **Total downtime** | **16 h** | System online Saturday 12:00 |

### Step 5 — Post-conversion verification

- Run `/SDF/RC_START_CHECK` in post-conversion mode: all checks GREEN.
- Execute `SE38` → `RSCMCNV_CHECK` to verify data conversion completeness.
- Hand off to `sap-migration-testing` for functional regression testing.
- Hand off to `sap-hana-performance` for SQL performance baseline.

## Anti-patterns

1. **Running SUM without completing the custom code migration worklist.** Unresolved ATC findings (e.g., references to removed tables like BSEG views, KNA1/LFA1 direct access instead of BP) will cause ABAP short dumps post-conversion. Fix custom code *before* entering downtime, not during it ([SAP Custom Code Migration Guide](https://help.sap.com/doc/9dcbc5063b8b4b33a2e4fb5c09ee4550/Latest/en-US/CustomCodeMigration_Guide_PUBLIC.pdf), Section "Integration with SUM").

2. **Sizing the target HANA database based on raw source DB size.** S/4HANA simplifications consolidate many tables (e.g., MATDOC replaces MKPF/MSEG, ACDOCA replaces BSEG/BKPF/FAGLFLEXA/COEP). The converted HANA footprint is often **30–50% smaller** than the source. Use the SAP HANA Sizing Report (transaction `/SDF/HDB_SIZING`) or the Quick Sizer to get an accurate target estimate. Over-sizing wastes HANA license costs; under-sizing causes OOM during migration ([SAP Note 1872170](https://me.sap.com/notes/1872170)).

3. **Skipping the sandbox rehearsal.** Running SUM for the first time on the production system is the highest-risk approach. SAP strongly recommends at least **two full rehearsal cycles** on a sandbox copy: the first to identify issues, the second to validate fixes and measure actual phase durations. Production cutover should be the third or fourth run ([Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb8933c2a8e78f/Latest/en-US/ConversionGuide_S4HANA.pdf)).

4. **Forgetting to regenerate the Maintenance Planner stack file.** Stack files are generated for a specific combination of source components and target release. If the target release changes (e.g., from 2024 to 2025), or add-ons are added/removed, the old stack file becomes invalid. SUM will reject a stale stack file during the EXTRACTION phase. Always regenerate the stack file for each conversion cycle ([SAP Help: Maintenance Planner](https://help.sap.com/docs/maintenance-planner)).

5. **Choosing standard DMO when downtime requirements actually need dDMO.** Once SUM enters the EXECUTION phase with standard DMO, there is no way to switch to dDMO mid-run. If the data migration takes longer than expected (e.g., due to large tables or slow I/O), the downtime window overruns. Evaluate dDMO during planning based on rehearsal timings, not production hopes ([SAP Note 2393060](https://me.sap.com/notes/2393060)).

6. **Insufficient R3load parallelism.** The default R3load parallelism is often too low for large databases. Not tuning `PARALLEL_JOBS_RLOAD` and not enabling table splitting means the data migration runs serially on large tables, dramatically extending downtime. Conversely, setting parallelism too high can overwhelm source DB I/O. Use rehearsal runs to find the optimal setting ([DMO Guide](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf)).

7. **Not archiving data before the conversion.** Large historical data volumes in tables like BSEG, CDPOS, MSEG, and NAST directly increase both migration time and HANA memory requirements. Archiving or purging obsolete data before SUM start can reduce downtime by 30–60% and significantly lower HANA sizing requirements ([SAP Note 1872170](https://me.sap.com/notes/1872170)).

## References

- [SUM Guide: Conversion to SAP S/4HANA or SAP BW/4HANA using SUM](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf) — The primary technical guide for SUM-based system conversions, covering all phases and DMO variants.
- [DMO Guide: Database Migration Option — Target Database SAP HANA](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf) — Detailed DMO-specific procedures including R3load configuration, table splitting, and system move.
- [Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb8933c2a8e78f/Latest/en-US/ConversionGuide_S4HANA.pdf) — End-to-end conversion roadmap from SAP covering functional and technical preparation.
- [SAP Note 2882748 — SUM 2.0 SP Central Note](https://me.sap.com/notes/2882748) — Central note for SUM 2.0; lists current SP level, known issues, and required patches.
- [SAP Note 2393060 — Downtime-Optimized DMO](https://me.sap.com/notes/2393060) — Prerequisites, limitations, and configuration for dDMO and downtime-optimized conversion (doC).
- [SAP Note 2351294 — DMO with System Move](https://me.sap.com/notes/2351294) — Requirements for DMO with System Move, including target system preparation and network configuration.
- [SAP Note 2399707 — Conversion Pre-Checks](https://me.sap.com/notes/2399707) — Documentation for `/SDF/RC_START_CHECK` report and its check categories.
- [SAP Note 1976487 — S/4HANA Simplification List](https://me.sap.com/notes/1976487) — Master list of simplification items that must be reviewed before conversion.
- [SAP Note 1973241 — SPDD/SPAU Adjustments](https://me.sap.com/notes/1973241) — Guidance on SPDD/SPAU handling during SUM-driven upgrades and conversions.
- [SAP Note 1872170 — SAP HANA Sizing](https://me.sap.com/notes/1872170) — HANA memory and disk sizing guidelines for system conversions.
- [SAP Note 2265093 — Business Partner Approach](https://me.sap.com/notes/2265093) — CVI synchronization and BP migration during S/4HANA conversion.
- [SAP Note 2227764 — MATDOC Material Documents](https://me.sap.com/notes/2227764) — Migration of material documents to the new MATDOC table.
- [SAP Note 2270407 — Universal Journal](https://me.sap.com/notes/2270407) — ACDOCA migration and Universal Journal activation.
- [SAP Note 2270333 — Material Number Length Extension](https://me.sap.com/notes/2270333) — Optional MATNR field length extension during conversion.
- [SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/doc/9dcbc5063b8b4b33a2e4fb5c09ee4550/Latest/en-US/CustomCodeMigration_Guide_PUBLIC.pdf) — Integration with SUM appendix.
- [Maintenance Planner](https://maintenanceplanner.cloud.sap) — SAP tool for generating conversion stack files.
