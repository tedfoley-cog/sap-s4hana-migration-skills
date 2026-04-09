# Performance Test Checklist for S/4HANA Conversion

> **Sources**: [SAP Note 2399707](https://me.sap.com/notes/2399707), [SAP Help: SAP HANA SQL Analyzer](https://help.sap.com/docs/SAP_HANA_PLATFORM/b5b9a5e7116d4286956ec7eb55e46a0d), [SAP Community: SAP Project Manager's Guide to SAP Project Cutover](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-project-manager-s-guide-to-sap-project-cutover/ba-p/13510809).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Contents

- [When to use](#when-to-use) — trigger criteria for this checklist
- [Pre-conversion baseline](#pre-conversion-baseline-capture-on-ecc) — ECC measurements to capture
- [Post-conversion performance tests](#post-conversion-performance-tests) — online, batch, and custom report checks
- [Tools reference](#tools-reference) — SAP transactions for performance analysis
- [Thresholds and escalation](#thresholds-and-escalation) — acceptable vs. warning vs. escalate criteria

## When to use

Use this checklist after each SUM/DMO dry run to validate that performance on the converted S/4HANA system meets or exceeds the ECC baseline.

## Pre-conversion baseline (capture on ECC)

- [ ] Record response times for top 20 online transactions by user frequency (use transaction `ST03N` workload analysis or `STAD` for individual transaction statistics).
- [ ] Record runtimes for top 10 batch jobs by duration (transaction `SM37`, sort by runtime).
- [ ] Record database query times for known long-running custom reports (use `ST05` SQL trace on the specific Z-transactions).
- [ ] Export the baseline measurements to a spreadsheet. Include: transaction code, average response time (ms), number of dialog steps, database time, and data volume processed.

## Post-conversion performance tests

### Online transactions

For each of the top 20 transactions:

- [ ] Execute the same business scenario used for the ECC baseline (same material, same customer, same document type).
- [ ] Record response time using `STAD` (transaction statistics) or wall-clock time.
- [ ] Compare to ECC baseline. Flag any transaction where response time degraded by >20%.
- [ ] For degraded transactions, run `ST05` SQL trace to identify slow SQL statements.
- [ ] Check if degraded SQL uses compatibility views (`BSEG`, `MKPF`, `MSEG`, `KONV`) that add overhead. If so, rewrite to use new tables (`ACDOCA`, `MATDOC`, etc.) per `sap-functional-simplifications`.

### Batch jobs

For each of the top 10 batch jobs:

- [ ] Schedule the job with the same parameters used on ECC.
- [ ] Record runtime and compare to ECC baseline.
- [ ] Batch jobs should generally improve on HANA. If a job is slower, investigate:
  - [ ] Check for table locks (`SM12`) that indicate serialization issues.
  - [ ] Check for excessive commits in custom code (HANA favors bulk operations over row-by-row processing).
  - [ ] Check for missing secondary indexes on HANA (some ECC indexes are not automatically created on HANA; use `DBACOCKPIT` → Diagnostics → Missing Indexes).

### Custom reports and programs

- [ ] Run all custom Z-reports that process large data volumes (>100K records).
- [ ] For reports using `SELECT *` from restructured tables, verify that field lists are explicit and necessary columns only are fetched.
- [ ] Check for `FOR ALL ENTRIES` patterns on large datasets — on HANA, `JOIN` patterns often perform better.
- [ ] Verify that any custom CDS views perform acceptably. Use `ST05` or HANA SQL Analyzer to check execution plans.

## Tools reference

| Tool | Transaction / Access | Purpose |
|---|---|---|
| Workload Monitor | `ST03N` | Aggregate transaction statistics |
| Transaction Statistics | `STAD` | Per-dialog-step response time breakdown |
| SQL Trace | `ST05` | Capture and analyze individual SQL statements |
| SQL Monitor | `SQLM` | Long-term SQL performance monitoring |
| HANA SQL Analyzer | HANA Studio or `DBACOCKPIT` | Execution plan analysis for HANA queries |
| Job Monitor | `SM37` | Batch job runtime and status |
| System Log | `SM21` | System-level errors and warnings |
| ABAP Dump Analysis | `ST22` | Short dump analysis for runtime errors |

## Thresholds and escalation

| Category | Acceptable | Warning | Escalate |
|---|---|---|---|
| Online transaction response | ≤ ECC baseline | 1-1.2x ECC baseline | > 1.2x ECC baseline |
| Batch job runtime | ≤ ECC baseline (most should improve) | 1-1.5x ECC baseline | > 1.5x ECC baseline |
| ABAP dumps (ST22) | 0 per day | < 5 per day | ≥ 5 per day |
| Database locks (SM12) | 0 persistent locks | Any persistent lock | Lock escalation affecting users |

If performance issues are found, see the `sap-hana-performance` skill for detailed remediation guidance.
