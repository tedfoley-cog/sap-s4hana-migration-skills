# Worked Example: SPDD/SPAU Adjustment — Manufacturing ECC 6.0 EHP8 Conversion

> **Sources**: [SAP Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf),
> [SAP Note 1973241](https://me.sap.com/notes/1973241) — SPDD/SPAU Adjustments,
> [SAP Note 2270333](https://me.sap.com/notes/2270333) — Material Number Field Length Extension.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Pre-conversion scoping (SE95)](#step-1--pre-conversion-scoping-se95)
- [Step 2 — SPDD during SUM downtime](#step-2--spdd-during-sum-downtime)
- [Step 3 — SPAU post-conversion](#step-3--spau-post-conversion)
- [Step 4 — Transport propagation](#step-4--transport-propagation)

## Scenario

S/4HANA 2025 conversion of a manufacturing ECC 6.0 EHP8 system. The system has 47 DDIC modifications and 189 repository modifications identified via `SE95` before the conversion.

## Step 1 — Pre-conversion scoping (SE95)

The Basis team runs `SE95` and exports the modification list. Key findings:

| Object | Type | Modification Reason | Decision |
|---|---|---|---|
| `BSEG` (append structure `ZAFINBSEG`) | Table | Custom fields ZZ_COST_OBJ, ZZ_APPROVAL_ID | Preserve - fields still needed |
| `MARA` (append structure `ZAMMARA`) | Table | Custom field ZZ_SHELF_LIFE | Preserve - regulatory requirement |
| `DOMAIN` `MATNR` | Domain | Extended from 18 to 40 chars | Reset - S/4HANA extends MATNR natively ([SAP Note 2270333](https://me.sap.com/notes/2270333)) |
| Report `SAPMM06E` | Program | Modified PO validation logic | Preserve - custom business rule |
| Report `RFUMSV00` | Program | VAT report fix (SAP Note 1876432) | Reset - fix included in S/4HANA |
| BAdI impl `ZIM_ME_PROCESS_PO_CUST` | Enhancement | Custom PO processing | Preserve - review in SPAU_ENH |

## Step 2 — SPDD during SUM downtime

SUM pauses at the SPDD prompt. The Basis administrator opens `SPDD` in client 000.

**Object: Append structure `ZAFINBSEG` on table `BSEG`**
- Category: **With Modification Assistant**
- The Modification Assistant shows a three-way merge:
  - Original SAP `BSEG`: 85 fields
  - Customer-modified `BSEG`: 87 fields (ZZ_COST_OBJ, ZZ_APPROVAL_ID added via append)
  - New S/4HANA `BSEG`: 82 fields (3 fields removed by simplification, new fields added)
- The merge proposal correctly preserves `ZAFINBSEG` with both custom fields on the new structure.
- Action: **Accept** the automatic merge. Save to transport `S4HK900001`.

**Object: Domain `MATNR`**
- Category: **With Modification Assistant**
- The customer had extended `MATNR` from CHAR(18) to CHAR(40). In S/4HANA, SAP natively supports MATNR length extension ([SAP Note 2270333](https://me.sap.com/notes/2270333)).
- Action: **Reset to Original**. The S/4HANA standard domain handles the extended length. Save to transport `S4HK900001`.

The administrator processes all 47 DDIC objects (34 resets, 11 automatic merges accepted, 2 manual adjustments in `SE11`). Total SPDD time: 3 hours. Confirms completion in SUM. SUM resumes activation.

## Step 3 — SPAU post-conversion

After SUM completes, the development team opens `SPAU`. The worklist shows 189 modifications.

**Triage results:**

| Category | Count | Action |
|---|---|---|
| SAP Note resets (fix included in new release) | 94 | Reset to Original |
| Customer modifications auto-preserved by SAP | 56 | Adopt |
| Semi-automatic merge possible | 27 | Review and accept merge |
| Manual conflict | 12 | Manual adjustment in SE38/SE80 |

**Processing order:**
1. Batch-select the 94 SAP Note resets -> "Reset to Original" -> Save to transport `S4HK900002`.
2. Batch-select the 56 auto-preserved modifications -> "Adopt" -> Save to transport `S4HK900002`.
3. Process 27 semi-automatic merges one by one. 25 accepted as-is; 2 required minor manual edits. Save to `S4HK900002`.
4. Route the 12 manual conflicts to assigned developers:

**Example manual conflict: Report `SAPMM06E`**
- The customer modified form routine `CHECK_PO_HEADER` to add a custom approval check.
- In S/4HANA, SAP restructured the PO processing logic, and `CHECK_PO_HEADER` was refactored.
- The developer opens the three-way comparison, identifies the new location of the equivalent logic, and reapplies the custom approval check to the refactored routine.
- Estimated effort: 2 hours. Save to transport `S4HK900002`.

**Example manual conflict: BAdI implementation `ZIM_ME_PROCESS_PO_CUST`** (in SPAU_ENH)
- The BAdI interface `IF_EX_ME_PROCESS_PO_CUST` added a new parameter in S/4HANA.
- The developer updates the implementation to handle the new parameter. Save to transport `S4HK900003`.

## Step 4 — Transport propagation

Transports released in order:
1. `S4HK900001` (SPDD - dictionary adjustments)
2. `S4HK900002` (SPAU - repository adjustments)
3. `S4HK900003` (SPAU_ENH - enhancement adjustments)

Imported to QA system. Smoke test confirms all modified objects activate and function correctly.
