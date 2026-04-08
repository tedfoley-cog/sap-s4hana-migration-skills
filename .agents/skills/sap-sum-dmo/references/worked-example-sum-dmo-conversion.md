# Worked Example: SUM/DMO Conversion — ECC 6.07 to S/4HANA 2025

> **Sources**: [SUM Guide](https://help.sap.com/doc/08e459b0d229498fb74efe7e3bb401a0/Latest/en-US/convsum20.latest.pdf),
> [DMO Guide](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf),
> [SAP Note 2882748](https://me.sap.com/notes/2882748) — SUM 2.0 Central Note.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Maintenance Planner](#step-1--maintenance-planner)
- [Step 2 — Pre-checks](#step-2--pre-checks)
- [Step 3 — DMO flavor selection](#step-3--dmo-flavor-selection)
- [Step 4 — SUM execution](#step-4--sum-execution)
- [Step 5 — Post-conversion verification](#step-5--post-conversion-verification)

## Scenario

Convert a fictional ECC 6.07 (EHP7) system `E01` on Oracle 19c to S/4HANA 2025 FPS01 on SAP HANA 2.0 SPS07. Source database size: 4.2 TB. Target downtime window: 16 hours.

## Step 1 — Maintenance Planner

The basis admin logs in to [Maintenance Planner](https://maintenanceplanner.cloud.sap), selects system `E01` (SID registered via SAP Solution Manager landscape data), and plans for target release **SAP S/4HANA 2025 FPS01**. Maintenance Planner detects installed add-ons (IS-OIL, HR-RENEWAL) and validates compatibility. The generated stack XML includes:

- SAP_BASIS 758, SAP_ABA 758, S4CORE 110, SAP_HR 608
- Target kernel: 758 (64-bit Unicode)
- DMO-specific archives for HANA client and R3load

## Step 2 — Pre-checks

```
/SDF/RC_START_CHECK
```

Results:
- **RED**: SPAM queue not empty — 2 pending Support Packages. *Resolution*: Apply or delete the pending SPs via SPAM.
- **RED**: Simplification item S4TWL-000123 requires pre-conversion data cleanup in table `KONV`. *Resolution*: Run report `/SDF/RC_CONV_PRECHECK_KONV` to archive obsolete condition records.
- **RED**: Custom code check variant `S4HANA_READINESS` not yet executed. *Resolution*: Run ATC with variant `S4HANA_READINESS` via `ATC` transaction (hand-off to `sap-atc-readiness`).
- **YELLOW**: Table BSEG has 890 million records — consider archiving before conversion to reduce downtime. *Decision*: Team archives FI documents older than 7 years, reducing BSEG to 340 million records.

## Step 3 — DMO flavor selection

With 4.2 TB source data (reduced to ~3.1 TB after archiving), the team estimates:
- Standard DMO data migration: ~28 hours (exceeds 16-hour window)
- dDMO: ~10 hours downtime (delta-only migration)

**Decision**: Use **standard DMO** (not dDMO) because a sandbox rehearsal showed that with 16 parallel R3load processes and table splitting on BSEG, ACDOCA, MSEG, and MATDOC, the data migration completes in ~11 hours, fitting within the 16-hour window. dDMO adds complexity (trigger overhead on the source Oracle DB) that is not justified when standard DMO fits the window.

## Step 4 — SUM execution

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

## Step 5 — Post-conversion verification

- Run `/SDF/RC_START_CHECK` in post-conversion mode: all checks GREEN.
- Execute `SE38` → `RSCMCNV_CHECK` to verify data conversion completeness.
- Hand off to `sap-migration-testing` for functional regression testing.
- Hand off to `sap-hana-performance` for SQL performance baseline.
