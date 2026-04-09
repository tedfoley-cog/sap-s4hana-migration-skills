# Worked Example: OTC Regression Testing — Acme Retail ECC → S/4HANA 2024

> **Sources**: [SAP Activate Methodology — Roadmap Viewer](https://go.support.sap.com/roadmapviewer/),
> [SAP Note 2265093](https://me.sap.com/notes/2265093) — Business Partner Approach,
> [SAP Note 2227764](https://me.sap.com/notes/2227764) — Material Documents in MATDOC.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Identify in-scope process variants](#identify-in-scope-process-variants)
- [Build 12 test scripts in Solution Manager](#build-12-test-scripts-in-solution-manager)
- [Refresh sandbox](#refresh-sandbox)
- [Run SUM dry run #1](#run-sum-dry-run-1)
- [Fix and re-run dry run #2](#fix-and-re-run-dry-run-2)
- [Schedule UAT](#schedule-uat)

## Scenario

Acme Retail, a mid-sized retailer, is performing a brownfield ECC 6.0 EHP8 → S/4HANA 2024 conversion. The OTC process is the highest-priority business area.

## Identify in-scope process variants

The test lead reviews the simplification database and identifies these OTC impacts:

- Customer master → Business Partner (CVI) ([SAP Note 2265093](https://me.sap.com/notes/2265093))
- Credit management → SAP Credit Management (new) replaces classic FI credit management
- Output determination → Output Management (OM) replaces NACE-based output
- Material documents now in `MATDOC` instead of `MKPF`/`MSEG` ([SAP Note 2227764](https://me.sap.com/notes/2227764))

Four OTC variants are in scope:

| Variant | Sales Org | Material Type | Notes |
|---|---|---|---|
| Standard domestic sale | `1000` | `FERT` | Happy path |
| Returns processing | `1000` | `FERT` | Return order type `RE` |
| Intercompany sale | `1000` → `2000` | `FERT` | IC billing, elimination |
| Third-party drop-ship | `1000` | `HAWA` | PO auto-created from SO |

## Build 12 test scripts in Solution Manager

The test lead creates test scripts in `STWB_WORK`:

```
Test Plan: ACME_OTC_S4_REGRESSION
├── TP_OTC_001: Standard sale (1000/FERT) — VA01 → VL01N → VF01
├── TP_OTC_002: Standard sale (1000/HAWA) — VA01 → VL01N → VF01
├── TP_OTC_003: Returns (1000/FERT) — VA01 type RE → VL01N → VF01 credit memo
├── TP_OTC_004: Intercompany (1000→2000/FERT) — VA01 → VL01N → VF01 → VFIC
├── TP_OTC_005: Third-party (1000/HAWA) — VA01 → ME21N auto-PO → MIGO → VF01
├── TP_OTC_006: Credit check block — VA01 with exceeded credit limit
├── TP_OTC_007: Output — invoice print via new Output Management
├── TP_OTC_008: Pricing with custom condition type ZABC
├── TP_OTC_009: BP validation — customer created via BP, check KNVV/KNVP populated
├── TP_OTC_010: Availability check — VA01 with ATP check on batch-managed material
├── TP_OTC_011: Billing due list — VF04 mass billing run (500 orders)
├── TP_OTC_012: Revenue recognition — post billing, check ACDOCA entries
```

## Refresh sandbox

TDMS time-slice copy of production data from 3 months prior. Scramble `KNA1-NAME1`, `KNA1-STRAS`, `ADRC-*` fields. Validate: `SE16N` shows 1.2M records in `VBAK` (matches production ± 5%).

## Run SUM dry run #1

SUM DMO conversion completes in 14 hours. Run regression:

- **5 failures** detected:
  1. `TP_OTC_005` (third-party): custom function module `Z_SD_CREATE_PO` reads `LFA1-LIFNR` via vendor number — fails because vendor master is now BP. **Root cause**: CVI not synchronized for this vendor account group. **Fix**: run `CVIMC` for vendor account group `LIEF`.
  2. `TP_OTC_007` (output): invoice output not generated — NACE condition records not migrated to Output Management. **Fix**: configure OM channel and template.
  3. `TP_OTC_008` (pricing): custom condition type `ZABC` calculation routine dumps with `CX_SY_OPEN_SQL_DB` in class `ZCL_PRICING_CALC`. **Root cause**: SELECT from `KONV` which is now a compatibility view with changed behavior. **Fix**: rewrite to use pricing API.
  4. `TP_OTC_009` (BP): `KNVP` partner function records missing for some converted customers. **Root cause**: partner determination procedure not assigned in CVI mapping. **Fix**: correct CVI customizing in `SPRO`.
  5. `TP_OTC_012` (revenue): ACDOCA entries missing company code field mapping for custom fields. **Root cause**: BAdI `FINS_ACDOC_CUSTFLD` not implemented. **Fix**: implement the BAdI.

## Fix and re-run dry run #2

All 5 fixes applied. SUM re-run on freshly refreshed sandbox completes in 12.5 hours (11% improvement). Regression: **all 12 tests pass**. ABAP Unit: 47/47 tests pass including new tests for `ZCL_PRICING_CALC`.

## Schedule UAT

UAT scheduled for the week following dry run #3. Sales operations team to execute OTC variants in converted system. Defect tracking via Jira project `ACME-S4`. Sign-off required from VP Sales Operations.
