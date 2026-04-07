## Brief: sap-functional-simplifications

**Skill name**: `sap-functional-simplifications`
**Phase**: Functional design + post-conversion remediation
**Owner**: The major data-model simplifications that affect functional configuration and custom code.

### Scope of this skill

The handful of **big functional simplifications** in S/4HANA that nearly every ECC → S/4HANA project has to deal with, and how custom code typically needs to change to follow them.

Cover at least these five major simplifications (one section each):

1. **Business Partner approach** — `KNA1` / `LFA1` are no longer the master; `BUT000` is. Customer/Vendor Integration (CVI) keeps the legacy tables in sync but new code should use BP. Direction: read from BP, write via BP API.
2. **Material number length extension** — `MATNR` extended from 18 to 40 chars. Affects all field declarations, conversion exits (`MATN1`/`CONVERSION_EXIT_MATN1_*`), interface payloads, file formats.
3. **MATDOC consolidation** — material documents (`MKPF`, `MSEG`, etc.) consolidated into `MATDOC`. The legacy tables are now compatibility views. Stock and aggregate views (`S031`, `S032`, ...) are gone; use `MATDOC_EXTRACT` and CDS views instead.
4. **Universal Journal (ACDOCA) and New General Ledger** — `BSEG`, `BKPF`, `COEP`, `FAGLFLEXA`, `MLHD`, etc. now flow into `ACDOCA`. Many `BSEG` extensions need to be remodeled.
5. **MM-IM table changes** — beyond MATDOC: `EKPO`, `EKKO` schedule line storage changes; legacy aggregation transactions removed.

For each simplification, the skill should explain:
- Old object(s).
- New object(s) and where the data lives now.
- Read path for custom code (often a CDS view).
- Write path (always go through standard APIs; never write to compatibility views directly).
- Common ATC finding patterns and how to remediate.
- The relevant SAP Notes.

Mention briefly (without full sections) the other notable ones: **output management** (SAP Adobe Forms / BRF+), **credit management** (SAP Credit Management replaces FI-AR-CR), **APO → IBP**, **CRM → C/4HANA or in-app**.

### Key sources to consult

1. SAP Note **2265093** — "S/4HANA: Business Partner Approach".
2. SAP Note **2227764** — "MATDOC: Material Documents".
3. SAP Note **2270333** — "Material Number Field Length Extension".
4. SAP Note **2270407** — "Universal Journal".
5. SAP Note **1976487** — "S/4HANA Simplification List".
6. SAP S/4HANA Simplification Item Catalog (live).
7. SAP Help Portal: "Conversion Guide for SAP S/4HANA".

### Worked example

Show one detailed example for the **MATNR length extension**:
1. Custom report `Z_PRICE_LIST` declares `lv_matnr TYPE c LENGTH 18`.
2. After conversion the literal will silently truncate 40-char part numbers.
3. ATC quick fix replaces the declaration with `TYPE matnr` (which is now `c(40)`).
4. Report output template needs widening; ALV column width adjusted.
5. Downstream interface file format also needs widening — flag for the integration team.

### Anti-patterns

- Writing directly to compatibility views (e.g. INSERTing to `MKPF` post-conversion) — the inserts succeed but the data is not visible because MATDOC is the source of truth.
- Treating Customer/Vendor Integration as "BP migration done"; CVI is a sync layer, not a target. New custom code must use BP APIs.
- Hand-coding MATNR conversion logic with hard-coded `c(18)` — re-introduces the truncation bug.
- Continuing to use `BSEG` joins for FI reporting after Universal Journal — slow and incomplete; use `ACDOCA` CDS views.

### Related skills

`sap-simplification-database`, `sap-atc-readiness`, `sap-modern-abap-rewrite`, `sap-clean-core-extensibility`
