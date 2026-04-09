# Worked Example: Scoping `Z_OLD_SALES_RPT` at Meridian Industries

> **Sources**: [SAP Note 2185390](https://me.sap.com/notes/2185390) — Custom Code Migration Worklist,
> [SAP Note 2399707](https://me.sap.com/notes/2399707) — Custom Code Migration Pre-Checks,
> [SAP Custom Code Migration Guide for S/4HANA 2025](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — SCMON data review](#step-1--scmon-data-review)
- [Step 2 — SUSG confirmation](#step-2--susg-confirmation)
- [Step 3 — Cross-validation](#step-3--cross-validation)
- [Step 4 — CCLM / Custom Code Migration app](#step-4--cclm--custom-code-migration-app)
- [Step 5 — Scope decision](#step-5--scope-decision)
- [Step 6 — Deletion transport](#step-6--deletion-transport)
- [Step 7 — Result](#step-7--result)

## Scenario

Fictitious company *Meridian Industries* is converting their ECC 6.0 EHP8 system to S/4HANA 2025. They have 4,200 custom ABAP objects (Z/Y namespace).

### Object under review: `Z_OLD_SALES_RPT`

`Z_OLD_SALES_RPT` is a custom ALV report program in package `ZFICA_LEGACY` that was originally built in 2011 to display open sales orders by region.

## Step 1 — SCMON data review

The Basis team activated SCMON 14 months ago. Querying `/SDF/SCMON_DATA` via `SE16`:

```
Table: /SDF/SCMON_DATA
Selection: OBJECT_NAME = 'Z_OLD_SALES_RPT'
           RECORDING_DATE between '20250201' and '20260401'
Result:    0 records
```

SCMON recorded zero calls to `Z_OLD_SALES_RPT` over 14 months — covering two fiscal year-end closes and four quarter-ends.

## Step 2 — SUSG confirmation

Running SUSG aggregation and checking the aggregated data:

```
Transaction: SUSG
Object:      Z_OLD_SALES_RPT
Total calls: 0
Batch refs:  0
Dialog refs: 0
RFC refs:    0
```

No batch jobs, dialog sessions, or RFC calls reference this report.

## Step 3 — Cross-validation

- **SM37** (batch jobs): No active or released jobs reference `Z_OLD_SALES_RPT`.
- **SE80** (where-used): No cross-references from other custom objects.
- **RFCDES** (SM59): Not registered as an RFC-enabled function module (it is a report, not an FM).
- **Dynamic call search**: In `SE38` → *Find in Source Code*, search pattern `'Z_OLD_SALES_RPT'` across all Z/Y programs — no dynamic `SUBMIT Z_OLD_SALES_RPT` or `CALL TRANSACTION` references found.

## Step 4 — CCLM / Custom Code Migration app

The Custom Code Migration app marks `Z_OLD_SALES_RPT` as a **deletion candidate** with status "Unused — 0 calls in 14 months."

## Step 5 — Scope decision

Decision: **Delete**. The report has zero usage across all channels for 14 months, no dynamic references, and no cross-references.

## Step 6 — Deletion transport

In the development system:

```
Transaction: SE38
Program:     Z_OLD_SALES_RPT
Action:      Delete → Assign to transport DEVK900042
```

Transport `DEVK900042` is parked (not released) and documented in the SUM conversion stack.

## Step 7 — Result

During the S/4HANA conversion, SUM processes transport `DEVK900042`. `Z_OLD_SALES_RPT` is deleted from the target system. It never needs ATC remediation, saving approximately 2–4 hours of developer effort.

Across all 4,200 objects, Meridian identifies 1,890 objects (45%) as unused. By deleting them before conversion, they reduce the ATC remediation worklist from 2,310 findings to 1,400 — a 39% reduction in remediation effort.
