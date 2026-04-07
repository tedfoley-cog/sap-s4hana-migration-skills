## Brief: sap-hana-performance

**Skill name**: `sap-hana-performance`
**Phase**: Post-conversion remediation
**Owner**: Performance analysis and code-pushdown patterns once running on SAP HANA.

### Scope of this skill

How to find and fix performance regressions in custom ABAP code after the database swap to SAP HANA, and how to push computation down to the database the way HANA expects.

Cover:
- **SQL Monitor (`SQLM`)**: how to enable in production, how long to collect, how to download results into the central ATC system.
- **Runtime Check Monitor (`SRTCM`)**: catches anti-patterns like `FOR ALL ENTRIES` without `ORDER BY` and `SELECT ... ENDSELECT` over large result sets that only become problems on HANA.
- **DBA Cockpit / `ST04`** for HANA-specific expensive statement analysis.
- **Code Inspector / ATC HANA-specific check variants** (`PERFORMANCE_DB`, `FUNCTIONAL_DB_SAP`, `PERFORMANCE_CHECKLIST`).
- The **code pushdown pyramid**: prefer **CDS views** > **AMDP (ABAP Managed Database Procedures)** > **Open SQL with WHERE clauses** > avoid `SELECT *` and ABAP-side loops.
- **Top 10 ABAP anti-patterns on HANA** with rewritten "good" examples for each:
  - Nested `SELECT` in a loop → `SELECT ... FOR ALL ENTRIES IN @itab` → CDS view.
  - `SELECT *` of wide tables → field list.
  - `SORT itab` on huge tables → push sort to DB.
  - Sequential reads of clustered tables (`BSEG`) → ACDOCA CDS view.
  - Implicit secondary index assumptions (HANA has no secondary indexes by default).
  - `SELECT SINGLE` without a fully-qualified key → returns nondeterministic row.
  - String concatenation in a loop → use string templates and `LET`.
- Migrating to **ABAP for Cloud Development** patterns where it makes sense (table buffering rules differ).

### Key sources to consult

1. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — section "Performance Optimization for SAP HANA".
2. SAP Note **2201632** — "SQL Monitor".
3. SAP Note **1885926** — "Runtime Check Monitor (SRTCM)".
4. SAP Note **1912445** — "ABAP custom code migration recommended check variants".
5. SAP-samples/abap-cheat-sheets — `03_ABAP_SQL.md`, `04_ABAP_Object_Orientation.md`.
6. `SAP/abap-cleaner` rule set — many of its rules align with HANA performance patterns.
7. SAP Press: "ABAP Performance Tuning" (cite by title and chapter only; do not paste text).

### Worked example

Walk through an order-history report:
1. Original code: `SELECT *` from `BSEG` in a loop over `KNA1` rows; takes 40 minutes on HANA.
2. SQL Monitor flags it as the #1 expensive statement.
3. SRTCM catches the `FOR ALL ENTRIES` without `ORDER BY`.
4. Refactor: build a CDS view `ZI_OrderHistory` joining `ACDOCA` to a customer dimension, expose actions via service definition.
5. Report consumes the CDS view directly with a single `SELECT`; runtime drops to 12 seconds.

### Anti-patterns

- Adding HANA secondary indexes "to fix slow queries" without first refactoring the SQL — usually doesn't help on column store and adds maintenance cost.
- Treating `FOR ALL ENTRIES` as always-bad — it's fine on HANA *with* `ORDER BY` and a non-empty driver table check.
- Pushing all logic into AMDP just because pushdown is good — AMDP is hard to test and to debug; CDS first, AMDP only when necessary.
- Believing `SE30` / `SAT` results from the source ECC system — performance characteristics change drastically on HANA.

### Related skills

`sap-modern-abap-rewrite`, `sap-functional-simplifications`, `sap-clean-core-extensibility`
