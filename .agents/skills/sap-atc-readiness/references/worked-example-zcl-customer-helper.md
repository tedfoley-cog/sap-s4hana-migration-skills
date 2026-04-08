# Worked Example: ATC Readiness Check for `ZCL_CUSTOMER_HELPER`

> **Sources**: [SAP Note 2436688](https://me.sap.com/notes/2436688) — ATC checks for custom code migration,
> [SAP Note 2270333](https://me.sap.com/notes/2270333) — Material Number Field Length Extension,
> [SAP Note 2265093](https://me.sap.com/notes/2265093) — S/4HANA Business Partner Approach.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Setup](#setup)
- [Step 1 — Verify variant](#step-1--verify-variant)
- [Step 2 — Refresh SDB](#step-2--refresh-sdb)
- [Step 3 — Run check](#step-3--run-check)
- [Step 4 — Triage findings](#step-4--triage-findings)
- [Step 5 — Remediate in ADT](#step-5--remediate-in-adt)
- [Step 6 — Delta run](#step-6--delta-run)

## Setup

- Central ATC system: S/4HANA 2025 sandbox (`<system-id>`, client `<client-no>`)
- Source ECC system: ECC 6.0 EHP8 (`<system-id>`, client `<client-no>`), registered as RFC destination `<rfc-destination>`
- Target release: S/4HANA 2025 FPS01
- Object scope: Package `ZCUSTOMER` containing class `ZCL_CUSTOMER_HELPER` and related objects

## Step 1 — Verify variant

```
Transaction ATC → Check Variants → Search "S4HANA_READINESS"
→ Found: S4HANA_READINESS_2025_FPS01 ✓
```

## Step 2 — Refresh SDB

```
Transaction STC01 → Task List: SAP_BASIS_LOAD_SDB → Execute
→ SDB version: S/4HANA 2025 FPS01 (loaded 2026-04-05) ✓
```

## Step 3 — Run check

```
Transaction ATC → Run Check
  Object Set: Package ZCUSTOMER
  Check Variant: S4HANA_READINESS_2025_FPS01
  Source System: <rfc-destination>
→ Check completed: 7 findings
```

## Step 4 — Triage findings

| # | Object | Finding | Priority | Quick Fix? |
|---|---|---|---|---|
| 1 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR declared as CHAR(18), must be CHAR(40) | 1 - Error | Yes |
| 2 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR in local structure `LS_MAT` needs length extension | 1 - Error | Yes |
| 3 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR comparison with hard-coded 18-char value | 2 - Warning | Yes |
| 4 | `ZCL_CUSTOMER_HELPER=>CREATE_BP` | Call to `BAPI_CUSTOMER_CREATEFROMDATA1` — function module removed | 1 - Error | No |
| 5 | `ZCL_CUSTOMER_HELPER=>CREATE_BP` | Reference to table `KNA1` — replaced by BP tables | 2 - Warning | No |
| 6 | `ZCL_CUSTOMER_HELPER=>PRINT_DOC` | DATA declaration using obsolete type `SLIS_T_LISTHEADER` | 3 - Info | Yes |
| 7 | `ZCL_CUSTOMER_HELPER=>PRINT_DOC` | DATA declaration using obsolete type `SLIS_T_FIELDCAT_ALV` | 3 - Info | Yes |

## Step 5 — Remediate in ADT

Open `ZCL_CUSTOMER_HELPER` in ADT, connected to the central ATC system.

- **Findings 1-3** (MATNR length): Apply Quick Fixes via `Ctrl+1`. ADT adjusts the `DATA` declarations from `CHAR(18)` to `CHAR(40)` and updates the comparison logic. Review the changes in methods that pass MATNR to other objects — downstream callers may also need adjustment ([SAP Note 2270333](https://me.sap.com/notes/2270333)).
- **Findings 4-5** (BP migration): No Quick Fix available. The `BAPI_CUSTOMER_CREATEFROMDATA1` function module is removed in S/4HANA; replace with Business Partner API `CL_MD_BP_MAINTAIN` or the corresponding `I_BUSINESSPARTNER` OData service. References to `KNA1` must be replaced with `BUT000`/`BUT020` or CDS views `I_BusinessPartner` / `I_BPRelationship` ([SAP Note 2265093](https://me.sap.com/notes/2265093)). This requires manual rewriting — consult `sap-modern-abap-rewrite`.
- **Findings 6-7** (obsolete ALV types): Apply Quick Fixes to replace `SLIS_T_LISTHEADER` and `SLIS_T_FIELDCAT_ALV` with their successors.

Activate all changed objects.

## Step 6 — Delta run

```
Report SATC_AC_RUN_VIA_DELTA
  Variant: S4HANA_READINESS_2025_FPS01
  Object Set: Package ZCUSTOMER
  Delta mode: ON (compare with previous run)
→ Results: 5 cleared, 2 remaining (findings 4 and 5 — BP migration)
```

The 2 remaining findings require manual Business Partner migration work, tracked separately in the project plan.
