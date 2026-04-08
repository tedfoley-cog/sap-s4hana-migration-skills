---
name: sap-functional-simplifications
description: |
  Use when remediating custom ABAP code or functional configuration affected by
  the major S/4HANA data-model simplifications: Business Partner (CVI, KNA1/LFA1
  to BUT000, SAP Note 2265093), material number length extension (MATNR 18→40,
  SAP Note 2270333, CONVERSION_EXIT_MATN1), MATDOC consolidation (MKPF/MSEG
  replaced by MATDOC, SAP Note 2227764), Universal Journal (ACDOCA replacing
  BSEG/BKPF/COEP/FAGLFLEXA, SAP Note 2270407), or MM Inventory Management
  table changes (NSDM, EKPO/EKKO schedule-line storage). Also covers output
  management (BRF+/Adobe Forms), credit management (FI-AR-CR to SAP Credit
  Management), and other notable simplifications.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2025"
  sources:
    - "SAP Note 2265093 — Business Partner Approach"
    - "SAP Note 2227764 — MATDOC Material Documents"
    - "SAP Note 2270333 — Material Number Field Length Extension"
    - "SAP Note 2270407 — Universal Journal"
    - "SAP Note 1976487 — S/4HANA Simplification List"
    - "SAP Help Portal — Simplification List for SAP S/4HANA 2023"
    - "SAP Help Portal — Conversion Guide for SAP S/4HANA"
    - "SAP Help Portal — CDS Views for Stock and Material Documents"
    - "SAP Community — SAP S/4HANA Inventory Management Tables (Sreekanth Surampally, 2021)"
    - "SAP Community — All you need to know about Universal Journal (2022)"
    - "SAP Community — Business Partner Concept in SAP S/4HANA (2023)"
    - "SAP HANA Client hdbsql (https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)"
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
related_skills:
  - sap-atc-readiness
  - sap-clean-core-extensibility
  - sap-cli-toolbelt
  - sap-data-migration-cockpit
  - sap-hana-performance
  - sap-migration-testing
  - sap-modern-abap-rewrite
  - sap-simplification-database
  - sap-spdd-spau
  - sap-sum-dmo
---

## When to use this skill

Use this skill when you encounter any of the following during an SAP ECC to S/4HANA migration:

- ATC findings referencing **KNA1**, **LFA1**, **KNB1**, **LFB1** direct access and the need to move to Business Partner (`BUT000`, `BP_CENTRALDATA`, CVI)
- Custom code that declares `MATNR` as `TYPE c LENGTH 18` or uses hard-coded 18-character material number fields
- Reports or interfaces that read from **MKPF**, **MSEG**, or stock aggregate tables (`S031`, `S032`, `S033`, `S039`)
- FI/CO custom reports that join **BSEG**, **BKPF**, **COEP**, **FAGLFLEXA**, or **MLHD/MLIT** directly
- ATC check variants `S4HANA_READINESS` or `FUNCTIONAL_DB_ADDITIONS` flagging simplification items
- Configuration or code changes related to **output management** (NAST to BRF+/Adobe Forms), **credit management** (FI-AR-CR to SAP Credit Management), or **APO/CRM** decommissioning
- Simplification Item Catalog entries for any of the above topics

This skill covers the five highest-impact functional simplifications and provides remediation guidance for each. For the full simplification item catalog, see the sibling skill `sap-simplification-database`.

## Prerequisites

1. **ATC results available** — Run ATC with check variant `S4HANA_READINESS` or the remote check variant from SAP (see `sap-atc-readiness`). The findings feed directly into the remediation steps below.
2. **Simplification Item Catalog consulted** — Review the applicable simplification items for your target release at `https://launchpad.support.sap.com/#/sic` ([SAP Note 1976487](https://me.sap.com/notes/1976487)).
3. **Target S/4HANA release known** — Some simplifications (e.g., MATDOC phase-out of aggregate tables) were phased in across releases. Know your target: 2021, 2022, 2023, or 2025.
4. **Custom Code Migration Worklist** — Have the scoped custom code list from transaction `SCMON` / `SUSG` usage logging (see `sap-scoping`).
5. **Access to SAP Notes** — You will need to read the referenced SAP Notes for detailed field-mapping and compatibility information.

## Quick decision tree

```
Custom code touches master data tables?
├─ KNA1 / KNB1 / KNVV / LFA1 / LFB1 / LFM1
│  └─ Go to § 1 — Business Partner Approach
├─ MARA / MARC / MARD and uses MATNR field?
│  └─ Go to § 2 — Material Number Length Extension
├─ MKPF / MSEG / S031–S039 / MCHB / MCH1?
│  └─ Go to § 3 — MATDOC Consolidation
├─ BSEG / BKPF / COEP / COSP / FAGLFLEXA / MLHD / MLIT?
│  └─ Go to § 4 — Universal Journal (ACDOCA)
├─ EKPO / EKKO / EKET schedule-line or aggregate tables?
│  └─ Go to § 5 — MM-IM Table Changes
├─ NAST / output determination / SAPscript?
│  └─ Go to § 6 — Other Notable Simplifications (Output Management)
├─ KKBER / UKM* / FI-AR-CR credit tables?
│  └─ Go to § 6 — Other Notable Simplifications (Credit Management)
└─ None of the above → This skill does not apply.
```

## Procedure

### § 1 — Business Partner Approach

**Summary**: In S/4HANA, Business Partner (`BUT000`) is the leading master data object for customers and vendors. The traditional customer master (`KNA1`, `KNB1`, `KNVV`) and vendor master (`LFA1`, `LFB1`, `LFM1`) tables still exist but are maintained via a synchronization layer called Customer/Vendor Integration (CVI) ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

#### Old objects → New objects

| ECC table | Purpose | S/4HANA status |
|---|---|---|
| `KNA1` | Customer general data | Compatibility view — still readable, synchronized via CVI |
| `KNB1` | Customer company code | Compatibility view — synchronized via CVI |
| `LFA1` | Vendor general data | Compatibility view — synchronized via CVI |
| `LFB1` | Vendor company code | Compatibility view — synchronized via CVI |
| `BUT000` | BP general data | **Leading table** — single entry point for all partner data |
| `BUT0ID` | BP identification numbers | Leading table for tax numbers, DUNS, etc. |
| `CVI_CUST_LINK` | Customer ↔ BP mapping | Mapping table maintained by CVI |
| `CVI_VEND_LINK` | Vendor ↔ BP mapping | Mapping table maintained by CVI |

#### Read path for custom code

- **Preferred**: Use CDS views `I_Customer`, `I_Supplier`, `I_BusinessPartner`, or the released RAP APIs for read access ([SAP Help: Business Partner](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)).
- **Acceptable (short-term)**: Reading from `KNA1` / `LFA1` via `SELECT` still works because CVI keeps them synchronized. However, new custom code should not be written against these tables.
- The CVI synchronization is triggered by the BP transaction (or BAPI `BUPA_CENTRAL_CI_CREATE` / `BAPI_BUPA_CENTRAL_CHANGE`) and writes to both BP tables and the legacy customer/vendor tables simultaneously ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

#### Write path for custom code

- **Always** use the Business Partner API: transaction `BP`, BAPI `BUPA_CENTRAL_CI_CREATE`, or the RAP-based `I_BusinessPartner` API for creates/updates.
- **Never** use `XD01`/`XD02`/`XK01`/`XK02` or direct `INSERT`/`UPDATE` to `KNA1`/`LFA1` in new code. These transactions are disabled in S/4HANA ([SAP Note 2265093](https://me.sap.com/notes/2265093)).
- Custom BAPIs that write directly to `KNA1`/`LFA1` must be refactored to call BP APIs instead.

#### Common ATC findings and remediation

| ATC finding pattern | Remediation |
|---|---|
| Direct `SELECT` from `KNA1`/`LFA1` in new code | Replace with CDS view `I_Customer` / `I_Supplier` or BP API |
| `CALL FUNCTION 'CUSTOMER_CREATE'` or `'VENDOR_CREATE'` | Replace with `BUPA_CENTRAL_CI_CREATE` + role assignment |
| `XD01`/`XD02`/`XK01`/`XK02` call via `CALL TRANSACTION` | Replace with `BP` transaction or BP BAPI |
| Custom appends on `KNA1`/`LFA1` (CI includes) | Map to BP customer/vendor-specific data sets or extension fields on `BUT000` |

#### Relevant SAP Notes

- [SAP Note 2265093](https://me.sap.com/notes/2265093) — Business Partner Approach (central note)
- [SAP Note 2427300](https://me.sap.com/notes/2427300) — BP: Customer/Vendor Integration configuration
- [SAP Note 1905297](https://me.sap.com/notes/1905297) — CVI: Number range synchronization

---

### § 2 — Material Number Length Extension

**Summary**: The data element `MATNR` has been extended from `CHAR(18)` to `CHAR(40)` in S/4HANA. All custom code that hard-codes the old length will silently truncate material numbers longer than 18 characters ([SAP Note 2270333](https://me.sap.com/notes/2270333)).

#### What changed

- Data element `MATNR` is now `c(40)` in the ABAP Dictionary.
- The conversion exit `MATN1` (`CONVERSION_EXIT_MATN1_INPUT` / `CONVERSION_EXIT_MATN1_OUTPUT`) now handles 40-character formatting with leading-zero logic ([SAP Note 2270333](https://me.sap.com/notes/2270333)).
- All standard tables (`MARA`, `MARC`, `MARD`, `EKPO`, `LIPS`, `VBAP`, etc.) have been widened automatically during conversion.
- Custom tables, structures, interfaces, and file formats are **not** automatically widened — this is the migration team's responsibility.

#### Read / write path

- Declare material number fields using `TYPE matnr` (which resolves to `c(40)`) instead of `TYPE c LENGTH 18`.
- When using the embedded expression for conversion exits, use `|{ lv_matnr ALPHA = IN }|` for the ALPHA conversion or call `CONVERSION_EXIT_MATN1_INPUT` explicitly.
- For RFC/IDoc interfaces, ensure the external payload schema allows 40 characters for material number fields.

#### Common ATC findings and remediation

| ATC finding pattern | Remediation |
|---|---|
| `DATA lv_matnr TYPE c LENGTH 18` | Change to `DATA lv_matnr TYPE matnr` |
| `CONSTANTS: lc_len TYPE i VALUE 18` used for MATNR processing | Remove hard-coded length; use `DESCRIBE FIELD` or just `TYPE matnr` |
| Flat-file interface with fixed 18-char MATNR column | Widen field to 40 characters; coordinate with external systems |
| ALV field catalog with `outputlen = 18` for MATNR | Adjust to 40 or use dynamic column sizing |
| `CONCATENATE` / `OVERLAY` with hard-coded offsets for MATNR | Refactor to use string functions with `strlen( )` |

#### Relevant SAP Notes

- [SAP Note 2270333](https://me.sap.com/notes/2270333) — Material Number Field Length Extension (central note)
- [SAP Note 2179039](https://me.sap.com/notes/2179039) — MATNR length: impact on custom code
- [SAP Note 2217928](https://me.sap.com/notes/2217928) — Conversion exit MATN1 behavior changes

---

### § 3 — MATDOC Consolidation

**Summary**: Material document header (`MKPF`) and item (`MSEG`) tables have been consolidated into a single table `MATDOC`. The legacy tables `MKPF` and `MSEG` are now CDS compatibility views on top of `MATDOC`. Stock aggregate tables (`S031`, `S032`, `S033`, `S039`) have been removed entirely; stock is computed on-the-fly from `MATDOC` ([SAP Note 2227764](https://me.sap.com/notes/2227764)).

#### Old objects → New objects

| ECC table | Purpose | S/4HANA status |
|---|---|---|
| `MKPF` | Material document header | CDS compatibility view on `MATDOC` |
| `MSEG` | Material document item | CDS compatibility view on `MATDOC` |
| `S031`–`S039` | Stock aggregate / statistics tables | **Removed** — no replacement; use `MATDOC` aggregation |
| `MCHB` | Batch stock | Compatibility view; use CDS view `I_MaterialStockByBatch` |
| `MCH1` | Batch master | Still exists but check release notes |
| `MATDOC` | Unified material document table | **New leading table** |

#### Read path for custom code

- **Preferred**: Use CDS views for stock and material document queries. Key views include `I_MaterialDocumentItem`, `I_MaterialStockByBatch`, `I_MaterialStock`, and custom CDS views built on `MATDOC` ([SAP Help: CDS Views for Stock and Material Documents](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)).
- **Acceptable (short-term)**: `SELECT` from `MKPF` / `MSEG` still returns data because these are compatibility views. Performance may be slightly different since the underlying access is against `MATDOC`.
- **Prohibited**: Reading from `S031`–`S039`. These tables no longer exist; queries will return empty results or short dumps.
- For stock queries, use function module `MB_STOCK_ON_KEY_DATE` or the CDS view `I_MaterialStock` rather than aggregating from `MSEG` ([SAP Note 2227764](https://me.sap.com/notes/2227764)).

#### Write path for custom code

- **Always** use standard goods movement BAPIs: `BAPI_GOODSMVT_CREATE`, or transaction `MIGO` / `MB01`.
- **Never** write directly to `MATDOC` or the compatibility views `MKPF`/`MSEG`. Direct `INSERT` to compatibility views may appear to succeed but the data will be inconsistent with `MATDOC` indices.

#### Common ATC findings and remediation

| ATC finding pattern | Remediation |
|---|---|
| `SELECT FROM s031` / `s032` / `s039` | Remove; replace with `MATDOC` aggregation or `I_MaterialStock` CDS view |
| `SELECT FROM mkpf INNER JOIN mseg` | Still works via compatibility views but refactor to `I_MaterialDocumentItem` for performance |
| Direct `INSERT` to `MKPF` / `MSEG` | Replace with `BAPI_GOODSMVT_CREATE` |
| Custom appends on `MSEG` (CI includes) | Map to `MATDOC` customer fields or extension fields via BAdI |
| `CALL FUNCTION 'MB_CREATE_GOODS_MOVEMENT'` | Still available; verify compatibility with your release |

#### Relevant SAP Notes

- [SAP Note 2227764](https://me.sap.com/notes/2227764) — MATDOC: Material Documents (central note)
- [SAP Note 2267308](https://me.sap.com/notes/2267308) — NSDM: New Simplified Data Model for inventory
- [SAP Note 2253944](https://me.sap.com/notes/2253944) — Removal of stock aggregate tables

---

### § 4 — Universal Journal (ACDOCA)

**Summary**: In S/4HANA, all financial and controlling postings flow into a single table `ACDOCA` (Universal Journal). This replaces the separate storage in `BSEG` (FI line items), `COEP`/`COSP` (CO line items), `FAGLFLEXA` (New GL line items), and `MLHD`/`MLIT` (Material Ledger line items). The legacy tables become compatibility views ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

#### Old objects → New objects

| ECC table | Purpose | S/4HANA status |
|---|---|---|
| `BKPF` | FI document header | Still exists as a real table (headers are not merged) |
| `BSEG` | FI line items | CDS compatibility view on `ACDOCA` |
| `COEP` | CO line items (primary postings) | CDS compatibility view on `ACDOCA` |
| `COSP` | CO line items (secondary postings) | CDS compatibility view on `ACDOCA` |
| `FAGLFLEXA` | New GL line items | CDS compatibility view on `ACDOCA` |
| `MLHD` / `MLIT` | Material Ledger header/items | Merged into `ACDOCA` (actual costing) |
| `ACDOCA` | Universal Journal entry | **New leading table** — single source of truth for all postings |
| `ACDOCT` | Universal Journal totals | Replaces CO summary tables |

Important: `BKPF` remains a real table for document headers. Only the line-item tables are replaced by `ACDOCA` ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

#### Read path for custom code

- **Preferred**: Use CDS views `I_JournalEntry`, `I_JournalEntryItem`, `I_GLAccountLineItem`, `I_OperatingConcernLineItem` for financial reporting.
- **Acceptable (short-term)**: `SELECT` from `BSEG` still works via the compatibility view. However, `BSEG` no longer stores carry-forward or migration correction entries — only `ACDOCA` contains these ([SAP Community: All you need to know about Universal Journal, 2022](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/all-you-need-to-know-about-universal-journal-acdoca/ba-p/13531192)).
- Custom reports that `JOIN` `BSEG` with `BKPF` should be refactored to read from `ACDOCA` directly or from the appropriate CDS view for better performance and completeness.
- CO reports reading `COEP`/`COSP` should migrate to `ACDOCA`-based CDS views. CO internal postings now also write to `ACDOCA` ([SAP Community: What you should know about controlling in SAP S/4HANA, by SAP, 2020](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/what-you-should-know-about-controlling-in-sap-s-4hana/ba-p/13427058)).

#### Write path for custom code

- **Always** post via standard FI/CO posting BAPIs (`BAPI_ACC_DOCUMENT_POST`) or the new `ACDOCA`-aware APIs.
- **Never** write directly to `ACDOCA` or `BSEG`. The posting logic enforces business rules, validations, and consistent numbering.
- Cost element master data no longer exists as a separate object — cost elements are GL accounts with a cost element category. Custom code referencing table `CSKA`/`CSKB` must be adjusted ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

#### Common ATC findings and remediation

| ATC finding pattern | Remediation |
|---|---|
| `SELECT FROM bseg WHERE bukrs = ... AND belnr = ...` | Refactor to `I_JournalEntryItem` CDS view or `ACDOCA` direct access |
| `SELECT FROM coep` / `cosp` for cost center reports | Replace with `I_GLAccountLineItem` filtered by cost object |
| `SELECT FROM faglflexa` | Replace with `ACDOCA` or `I_JournalEntryItem` |
| References to `CSKA` / `CSKB` (cost element master) | Use GL account master (`SKA1`/`SKB1`) with cost element category |
| Custom `BSEG` appends (CI includes) | Remodel as `ACDOCA` extension fields or custom CDS view annotations |

#### Relevant SAP Notes

- [SAP Note 2270407](https://me.sap.com/notes/2270407) — Universal Journal (central note)
- [SAP Note 2332030](https://me.sap.com/notes/2332030) — ACDOCA: field mapping from legacy tables
- [SAP Note 2037301](https://me.sap.com/notes/2037301) — Cost element master replaced by GL account

---

### § 5 — MM-IM Table Changes

**Summary**: Beyond the MATDOC consolidation, additional inventory management table changes affect purchasing and logistics custom code. The New Simplified Data Model (NSDM) restructures how schedule lines and stock data are stored ([SAP Note 2267308](https://me.sap.com/notes/2267308)).

#### Key changes

- **Purchase order schedule lines**: `EKET` (schedule line data) storage logic changed. Confirmed quantities are now handled differently; custom code that manipulates `EKET` directly should use purchasing BAPIs.
- **Stock management**: Real-time stock is computed from `MATDOC` rather than stored in aggregate tables. The transactions `MC.1`, `MC.2`, `MC.9` (statistics updates) are removed ([SAP Community: SAP S/4HANA Inventory Management Tables, by Sreekanth Surampally, 2021](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/sap-s-4hana-inventory-management-tables-new-simplified-data-model/ba-p/13468936)).
- **Batch management**: `MCHB` (batch stock) is a compatibility view. Use CDS view `I_MaterialStockByBatch` for batch-level stock queries.
- **Reservation management**: `RESB` (reservation items) remains but some fields are deprecated. Use `I_Reservation` / `I_ReservationItem` CDS views.

#### Common ATC findings and remediation

| ATC finding pattern | Remediation |
|---|---|
| `SELECT FROM eket` with manual confirmed-qty logic | Use purchasing BAPI `BAPI_PO_CHANGE` for schedule line updates |
| `CALL FUNCTION 'MC_UPDATE_S031'` or similar | Remove — aggregate table updates are obsolete |
| Direct `SELECT FROM mchb` for batch stock | Replace with `I_MaterialStockByBatch` CDS view |
| Custom reports using `MC.1` / `MC.2` / `MC.9` output | Rebuild using `MATDOC`-based CDS views |

#### Relevant SAP Notes

- [SAP Note 2267308](https://me.sap.com/notes/2267308) — NSDM: New Simplified Data Model
- [SAP Note 2253944](https://me.sap.com/notes/2253944) — Removal of stock aggregate tables
- [SAP Note 1976487](https://me.sap.com/notes/1976487) — S/4HANA Simplification List (see MM-IM section)

---

### § 6 — Other Notable Simplifications

These simplifications do not require full sections but must be on the migration team's radar:

**Output Management** — The legacy output determination via condition technique (`NAST` table, `RSNAST00` processing) is replaced by SAP S/4HANA Output Management based on BRF+ and Adobe Forms. SAPscript forms should be migrated to Adobe Forms. Custom print programs using `WRITE` statements for output need redesign. See Simplification Item Catalog for details ([SAP Note 1976487](https://me.sap.com/notes/1976487)).

**Credit Management** — The classic FI-AR credit management (`KKBER`, `KNKK` tables, transactions `FD32`/`FD33`) is replaced by SAP Credit Management (also known as Financial Supply Chain Management Credit Management, `UKM_*` tables). Custom code accessing `KNKK` or calling `FD32` BAPIs must be refactored to use the new `UKM` APIs ([SAP Note 1976487](https://me.sap.com/notes/1976487)).

**APO → IBP** — SAP Advanced Planning and Optimization (APO) is not part of S/4HANA. Demand planning and supply network planning move to SAP Integrated Business Planning (IBP), which is a cloud solution. Custom APO interfaces (CIF, `/SAPAPO/` function modules) must be replaced. This is a separate project workstream, not an in-place code remediation ([SAP Note 1976487](https://me.sap.com/notes/1976487)).

**CRM → S/4HANA or C/4HANA** — SAP CRM is not part of S/4HANA. CRM functionality is either embedded in S/4HANA (basic sales/service) or provided by SAP CX (C/4HANA, now SAP Customer Experience). Custom CRM middleware interfaces need reassessment. Again, this is a separate migration workstream ([SAP Note 1976487](https://me.sap.com/notes/1976487)).


### CLI usage

Use `hdbsql` to validate table existence and data integrity after simplification, and `sapcli` for ABAP-level checks.

**Environment variables**:
- `HANA_HOST`, `HANA_USER`, `HANA_PASSWORD` (for hdbsql)
- `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD` (for sapcli)

**Network prerequisites**: HANA port 443 (Cloud) or 3\<sysnr\>15 (on-prem) + SAP HTTPS port.

```bash
# Verify MATDOC table exists and has data after conversion
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT COUNT(*) AS row_count FROM MATDOC"

# Verify ACDOCA Universal Journal has entries
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT COUNT(*) AS row_count FROM ACDOCA WHERE RLDNR = '0L' AND GJAHR = '2025'"

# Verify BP synchronization — check CVI link table
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT COUNT(*) FROM CVI_CUST_LINK"

# Download a custom object that touches deprecated tables for review
sapcli checkout class zcl_stock_report
```

These queries validate that the major simplification conversions (MATDOC, ACDOCA, BP/CVI) completed successfully. Discrepancies indicate data conversion issues that must be resolved before go-live ([SAP Help: hdbsql](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference), [sapcli](https://github.com/jfilak/sapcli)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

### MATNR Length Extension — Custom report `Z_PRICE_LIST`

**Scenario**: A custom pricing report `Z_PRICE_LIST` was written in ECC and is flagged by ATC after running the `S4HANA_READINESS` check variant.

#### Step 1 — Identify the finding

ATC reports the following finding in program `Z_PRICE_LIST`:

```
CHECK: S4HANA_READINESS / MATNR_LENGTH
Object: Z_PRICE_LIST  Line: 42
Message: Hard-coded material number length detected (c LENGTH 18).
         Use TYPE matnr instead.
```

#### Step 2 — Review the offending code

```abap
REPORT z_price_list.

TABLES: mara, a305.

DATA: lv_matnr   TYPE c LENGTH 18,       " << hard-coded length
      lt_output  TYPE TABLE OF z_price_s,
      ls_output  TYPE z_price_s,
      lt_makt    TYPE TABLE OF makt,
      ls_makt    TYPE makt.

SELECT matnr maktx FROM makt
  INTO TABLE lt_makt
  WHERE spras = sy-langu.

LOOP AT lt_makt INTO ls_makt.
  lv_matnr = ls_makt-matnr.              " truncation happens here
  " ... pricing lookup using lv_matnr ...
  ls_output-matnr = lv_matnr.
  ls_output-maktx = ls_makt-maktx.
  APPEND ls_output TO lt_output.
ENDLOOP.

CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
  EXPORTING
    i_structure_name = 'Z_PRICE_S'
  TABLES
    t_outtab         = lt_output.
```

**Problem**: After conversion, `MATNR` is `c(40)`. Material numbers exceeding 18 characters (e.g., `WPUMP-SUBMERSIBLE-100-SS316L`) are silently truncated when assigned to `lv_matnr`, producing wrong pricing lookups and incomplete output ([SAP Note 2270333](https://me.sap.com/notes/2270333)).

#### Step 3 — Apply the fix

```abap
REPORT z_price_list.

DATA: lv_matnr   TYPE matnr,             " << fixed: uses DDIC type (40 chars)
      lt_output  TYPE TABLE OF z_price_s,
      ls_output  TYPE z_price_s.

SELECT matnr, maktx FROM makt
  INTO TABLE @DATA(lt_makt)
  WHERE spras = @sy-langu.

LOOP AT lt_makt INTO DATA(ls_makt).
  lv_matnr = ls_makt-matnr.              " no truncation — both are c(40)
  " ... pricing lookup using lv_matnr ...
  ls_output-matnr = lv_matnr.
  ls_output-maktx = ls_makt-maktx.
  APPEND ls_output TO lt_output.
ENDLOOP.

CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
  EXPORTING
    i_structure_name = 'Z_PRICE_S'
  TABLES
    t_outtab         = lt_output.
```

#### Step 4 — Fix the structure `Z_PRICE_S`

Check the DDIC structure `Z_PRICE_S`. If the `MATNR` component is typed as `c(18)`, change it to reference data element `MATNR`:

```
Component  Typing       Before         After
MATNR      Data element CHAR18    →    MATNR
MAKTX      Data element MAKTX         (unchanged)
NETPR      Data element NETPR         (unchanged)
```

#### Step 5 — Adjust ALV column width

If the report uses a manual field catalog, update `outputlen` from `18` to `40`:

```abap
ls_fieldcat-fieldname = 'MATNR'.
ls_fieldcat-outputlen = 40.            " was 18
```

If using `i_structure_name`, ALV picks up the new width automatically from the DDIC.

#### Step 6 — Flag downstream interfaces

The report's output is also consumed by a flat-file interface `Z_PRICE_EXPORT` that writes a fixed-width file with an 18-character MATNR column. Create a follow-up task for the integration team:

> **Action item**: Widen `Z_PRICE_EXPORT` flat-file layout from 18 to 40 characters for MATNR field. Coordinate with receiving system (external pricing tool) to accept the wider format. ([SAP Note 2179039](https://me.sap.com/notes/2179039))

#### Step 7 — Rerun ATC

After applying all fixes, rerun ATC with the `S4HANA_READINESS` variant. The `MATNR_LENGTH` finding for `Z_PRICE_LIST` should be resolved.

## Anti-patterns

### 1. Writing directly to compatibility views

**Wrong**: Inserting material documents directly into `MKPF`/`MSEG` after conversion.

```abap
" ANTI-PATTERN — do not do this
INSERT mkpf FROM ls_mkpf.
INSERT mseg FROM TABLE lt_mseg.
```

**Why it fails**: In S/4HANA, `MKPF` and `MSEG` are CDS compatibility views on `MATDOC`. Direct inserts may appear to succeed in some circumstances but the data is not visible to standard transactions because `MATDOC` indices are not updated. The goods movement is effectively invisible to the system ([SAP Note 2227764](https://me.sap.com/notes/2227764)).

**Fix**: Use `BAPI_GOODSMVT_CREATE` or transaction `MIGO`.

### 2. Treating CVI as "BP migration done"

**Wrong**: Running the CVI synchronization to populate `BUT000` from `KNA1`/`LFA1` and then continuing to write new custom code against `KNA1`/`LFA1`.

**Why it fails**: CVI is a synchronization layer, not a migration endpoint. New code that writes to `KNA1` directly bypasses CVI and creates data inconsistencies between the BP and customer/vendor tables. The transactions `XD01`/`XK01` are disabled, but custom programs with direct SQL are not automatically blocked ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

**Fix**: All new custom code must use the BP APIs (`BUPA_CENTRAL_CI_CREATE`, transaction `BP`, or RAP API `I_BusinessPartner`).

### 3. Hard-coding MATNR conversion logic with `c(18)`

**Wrong**: Writing custom conversion-exit wrappers that assume 18-character material numbers.

```abap
" ANTI-PATTERN — hard-coded length re-introduces truncation
DATA(lv_formatted) = |{ lv_matnr(18) }|.
CALL FUNCTION 'CONVERSION_EXIT_MATN1_OUTPUT'
  EXPORTING input  = lv_formatted
  IMPORTING output = lv_display.
```

**Why it fails**: Any material number longer than 18 characters is truncated before the conversion exit even runs, producing a wrong or non-existent material number in the output ([SAP Note 2270333](https://me.sap.com/notes/2270333)).

**Fix**: Pass the full `TYPE matnr` variable (40 chars) to the conversion exit without substring operations.

### 4. Using BSEG joins for FI reporting after Universal Journal

**Wrong**: Continuing to join `BKPF` with `BSEG` for financial reporting in S/4HANA.

```abap
" ANTI-PATTERN — slow and incomplete in S/4HANA
SELECT bkpf~bukrs bkpf~belnr bseg~buzei bseg~dmbtr
  FROM bkpf INNER JOIN bseg
    ON bkpf~bukrs = bseg~bukrs
   AND bkpf~belnr = bseg~belnr
   AND bkpf~gjahr = bseg~gjahr
  WHERE bkpf~budat IN so_budat
  INTO TABLE lt_items.
```

**Why it fails**: `BSEG` is a compatibility view on `ACDOCA`. This query forces the database to read from `ACDOCA`, project into the `BSEG` compatibility structure, then join back to `BKPF`. This is slower than reading `ACDOCA` directly. Additionally, `BSEG` compatibility views do not contain carry-forward entries or migration correction items that exist only in `ACDOCA` — the report is incomplete ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

**Fix**: Use `ACDOCA` directly or the CDS view `I_JournalEntryItem`:

```abap
SELECT bukrs, belnr, buzei, dmbtr
  FROM acdoca
  WHERE rldnr  = '0L'
    AND budat  IN @so_budat
  INTO TABLE @DATA(lt_items).
```

### 5. Ignoring downstream interface impacts for MATNR

**Wrong**: Fixing the ABAP code to use `TYPE matnr` but not updating IDoc segments, RFC function module parameters, or flat-file layouts that exchange material numbers with external systems.

**Why it fails**: The external system continues to send/receive 18-character material numbers. New 40-character numbers are truncated at the interface boundary, causing lookup failures, duplicate materials, or rejected messages ([SAP Note 2179039](https://me.sap.com/notes/2179039)).

**Fix**: Audit all inbound and outbound interfaces for MATNR fields. Widen IDoc segments (or use the extended IDoc types), update RFC parameters, and coordinate file-format changes with partner systems.

## References

### SAP Notes (primary sources)

| Note | Topic |
|---|---|
| [2265093](https://me.sap.com/notes/2265093) | Business Partner Approach |
| [2427300](https://me.sap.com/notes/2427300) | CVI Configuration |
| [1905297](https://me.sap.com/notes/1905297) | CVI Number Range Synchronization |
| [2270333](https://me.sap.com/notes/2270333) | Material Number Field Length Extension |
| [2179039](https://me.sap.com/notes/2179039) | MATNR Length Impact on Custom Code |
| [2217928](https://me.sap.com/notes/2217928) | Conversion Exit MATN1 Changes |
| [2227764](https://me.sap.com/notes/2227764) | MATDOC: Material Documents |
| [2267308](https://me.sap.com/notes/2267308) | NSDM: New Simplified Data Model |
| [2253944](https://me.sap.com/notes/2253944) | Removal of Stock Aggregate Tables |
| [2270407](https://me.sap.com/notes/2270407) | Universal Journal (ACDOCA) |
| [2332030](https://me.sap.com/notes/2332030) | ACDOCA Field Mapping |
| [2037301](https://me.sap.com/notes/2037301) | Cost Element Master Replaced by GL Account |
| [1976487](https://me.sap.com/notes/1976487) | S/4HANA Simplification List |

### SAP Help Portal

- [Simplification List for SAP S/4HANA 2023](https://help.sap.com/doc/c34b5ef72430484cb4d889b5e265a4f4/2023/en-US/SIMPL_OP2023.pdf) — comprehensive list of all simplification items
- [Conversion Guide for SAP S/4HANA](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE) — master conversion guide
- [CDS Views for Stock and Material Documents](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE) — CDS view reference for MM-IM

### SAP Community

- [SAP S/4HANA: Inventory Management Tables New Simplified Data Model](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/sap-s-4hana-inventory-management-tables-new-simplified-data-model/ba-p/13468936) — Sreekanth Surampally, SAP, May 2021
- [All you need to know about Universal Journal (ACDOCA)](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/all-you-need-to-know-about-universal-journal-acdoca/ba-p/13531192) — SAP Community, Jan 2022
- [Business Partner Concept in SAP S/4HANA](https://community.sap.com/t5/technology-blog-posts-by-members/business-partner-concept-in-sap-s-4hana/ba-p/13560702) — SAP Community, Jul 2023
- [What you should know about controlling in SAP S/4HANA](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/what-you-should-know-about-controlling-in-sap-s-4hana/ba-p/13427058) — SAP, Apr 2020
