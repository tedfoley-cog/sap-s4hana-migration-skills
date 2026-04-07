---
name: sap-hana-performance
description: |
  Use when diagnosing and fixing ABAP performance regressions after migrating
  to SAP HANA: analyzing SQL Monitor (SQLM) results, interpreting Runtime Check
  Monitor (SRTCM) findings, running ATC check variant PERFORMANCE_DB or
  FUNCTIONAL_DB_SAP, refactoring SELECT-in-loop anti-patterns, replacing
  SELECT * with field lists, pushing computation down via CDS views or AMDP,
  migrating BSEG reads to ACDOCA, or tuning FOR ALL ENTRIES usage on HANA.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "SAP Custom Code Migration Guide for S/4HANA 2025 FPS01"
    - "SAP Note 2201632 — SQL Monitor"
    - "SAP Note 1885926 — Runtime Check Monitor (SRTCM)"
    - "SAP Note 1912445 — Recommended ATC check variants"
    - "SAP Note 2436688 — ATC checks for ABAP custom code migration"
    - "SAP Help Portal — ABAP Platform Performance Notes"
    - "SAP-samples/abap-cheat-sheets — 03_ABAP_SQL.md, 12_AMDP.md, 15_CDS_View_Entities.md, 32_Performance_Notes.md"
    - "SAP/abap-cleaner rule set"
    - "SAP Help Portal — ABAP SQL, CDS View Entities"
related_skills:
  - sap-modern-abap-rewrite
  - sap-functional-simplifications
  - sap-clean-core-extensibility
  - sap-atc-readiness
---

## When to use this skill

Invoke this skill when you encounter any of the following situations after an SAP ECC to S/4HANA conversion where the target database is SAP HANA:

- Custom ABAP reports or programs run significantly slower on HANA than on the source database (Oracle, DB2, MSSQL, MaxDB).
- SQL Monitor (`SQLM`) data shows expensive custom SQL statements consuming excessive DB time.
- Runtime Check Monitor (`SRTCM`) flags anti-patterns like `SELECT ... ENDSELECT` over large result sets or `FOR ALL ENTRIES` without a preceding emptiness check.
- ATC findings from check variants `PERFORMANCE_DB`, `FUNCTIONAL_DB_SAP`, or `PERFORMANCE_CHECKLIST` require remediation.
- DBA Cockpit (`ST04`) or HANA SQL Analyzer shows custom Z/Y programs among the top expensive statements.
- You need to refactor legacy code that reads from cluster tables (`BSEG`, `BSID`, `BSAD`, `KONV`) that no longer exist as physical tables in S/4HANA.
- You need to push ABAP-side computation down to the database using CDS views or AMDP.

## Prerequisites

1. **SAP S/4HANA system** running on SAP HANA database (any supported release: 2023, 2024, 2025).
2. **Developer authorization** in the target system with access to transactions `SQLM`, `SRTCM`, `ST04`, `SE38`, `SE80`, or ADT (Eclipse).
3. **ATC configuration** with HANA-specific check variants imported. Ensure SAP Note [1912445](https://me.sap.com/notes/1912445) central note for recommended check variants is applied ([SAP Note 1912445](https://me.sap.com/notes/1912445)).
4. **SQL Monitor** enabled in the production system for at least 4 weeks of representative workload data collection ([SAP Note 2201632](https://me.sap.com/notes/2201632)).
5. **ABAP Development Tools (ADT)** for Eclipse installed for CDS view and AMDP development.
6. Familiarity with the `sap-atc-readiness` skill for ATC setup and the `sap-modern-abap-rewrite` skill for general ABAP modernization patterns.

## Quick decision tree

```
Is the performance issue in a custom SQL statement?
  YES -> Has SQLM data been collected?
           YES -> Go to Procedure Step 1 (Analyze SQLM).
           NO  -> Enable SQLM first (Procedure Step 0).
  NO  -> Is it ABAP application-layer processing (loops, string ops)?
           YES -> Profile with ABAP Profiler / SAT (out of scope;
                  see SAP Help "ABAP Profiling").
           NO  -> Is it a standard SAP program?
                    YES -> Open an SAP incident (component BC-DBA-HDB).
                    NO  -> Check ATC findings (Procedure Step 2).

For SQL-level issues, what is the root cause?
  SELECT * on wide table        -> Procedure Step 4a.
  Nested SELECT in loop         -> Procedure Step 4b.
  FOR ALL ENTRIES misuse        -> Procedure Step 4c.
  Cluster table read (BSEG)     -> Procedure Step 4d.
  SORT on huge internal table   -> Procedure Step 4e.
  SELECT SINGLE without full key -> Procedure Step 4f.
  Need full computation pushdown -> Procedure Step 5 (CDS / AMDP).
```

## Procedure

### Step 0: Enable SQL Monitor (SQLM) in production

SQL Monitor records which SQL statements are executed, how often, and their total runtime. It is the single most important data source for identifying custom code performance hotspots on HANA ([SAP Note 2201632](https://me.sap.com/notes/2201632)).

1. Transaction `SQLM` > **Start Recording**.
2. Set recording duration to **at least 4 weeks** to capture month-end, quarter-end, and batch job workloads. SAP recommends a full business cycle ([SAP Custom Code Migration Guide, Section "SQL Monitor"](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)).
3. The recording imposes negligible overhead on production; it hooks into the ABAP SQL interface at the DBI layer ([SAP Note 2201632](https://me.sap.com/notes/2201632)).
4. After recording, download results via `SQLM` > **Export** or transfer to the central ATC system using RFC connection for cross-system analysis.

### Step 1: Analyze SQLM results

1. Open `SQLM` > **Display Results**.
2. Sort by **Total DB Time (descending)** to find the most expensive custom statements.
3. For each top-N statement (start with top 20), note:
   - Program name and include.
   - Table(s) accessed.
   - Number of executions vs. total rows returned (high ratio = possible N+1 problem).
   - Whether the statement uses `SELECT *` on a wide table.
4. Cross-reference with ATC findings from Step 2 to prioritize.

### Step 2: Run ATC with HANA-specific check variants

Apply SAP Note [1912445](https://me.sap.com/notes/1912445) and SAP Note [2436688](https://me.sap.com/notes/2436688) to obtain the recommended check variants for ABAP custom code migration:

| Check Variant | Purpose |
|---|---|
| `PERFORMANCE_DB` | Detects SQL anti-patterns that are especially costly on HANA column store ([SAP Note 1912445](https://me.sap.com/notes/1912445)). |
| `FUNCTIONAL_DB_SAP` | Detects functional issues caused by database-dependent behavior changes on HANA ([SAP Note 1912445](https://me.sap.com/notes/1912445)). |
| `PERFORMANCE_CHECKLIST` | Broader performance checks including ABAP-layer patterns ([SAP Note 2436688](https://me.sap.com/notes/2436688)). |

Run ATC via ADT: **Right-click package > Run As > ABAP Test Cockpit (ATC) With... > select variant**.

Key ATC message IDs to watch for:
- `PERFORMANCE_DB-SELECT_STAR` — `SELECT *` on tables with > 50 columns.
- `PERFORMANCE_DB-SELECT_IN_LOOP` — `SELECT` inside a `LOOP` or `DO`/`WHILE`.
- `PERFORMANCE_DB-FAE_EMPTY_CHECK` — `FOR ALL ENTRIES` without emptiness guard.
- `FUNCTIONAL_DB-ORDER_BY` — Missing `ORDER BY` where result order matters.

### Step 3: Analyze expensive statements in DBA Cockpit (ST04)

Transaction `ST04` provides HANA-specific expensive statement analysis ([SAP Help: DBA Cockpit](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/48b5d6014f18307de10000000a42189b.html)):

1. `ST04` > **Performance** > **Expensive Statements**.
2. Filter by **Application User** or **Application Source** to isolate custom code.
3. Identify statements with high **Total Execution Time** or **Total Lock Wait Time**.
4. Use **SQL Plan Cache** to inspect execution plans and identify full table scans on column-store tables.

For deeper analysis, HANA SQL Analyzer in SAP HANA Studio can visualize execution plans, showing where the optimizer chose suboptimal join strategies or full column scans.

### Step 4: Remediate top anti-patterns

The following sub-steps address the most common ABAP anti-patterns that cause performance regressions on HANA. Each includes a "before" and "after" code pattern.

#### Step 4a: Replace SELECT * with explicit field list

HANA column store reads only requested columns. `SELECT *` on wide tables (e.g., `BSEG` with 300+ fields) forces the engine to materialize all columns, wasting memory and network bandwidth ([SAP-samples/abap-cheat-sheets, 32_Performance_Notes.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/32_Performance_Notes.md)).

```abap
" BEFORE — anti-pattern
SELECT * FROM ekpo
  INTO TABLE @DATA(lt_ekpo)
  WHERE ebeln IN @s_ebeln.

" AFTER — specify only needed fields
SELECT ebeln, ebelp, matnr, menge, netpr
  FROM ekpo
  INTO TABLE @DATA(lt_ekpo)
  WHERE ebeln IN @s_ebeln.
```

#### Step 4b: Eliminate nested SELECT in loops

Nested `SELECT` inside a loop causes N+1 database round-trips. On HANA this is especially harmful because each round-trip has higher latency than row-store databases, even though individual queries are fast ([SAP-samples/abap-cheat-sheets, 32_Performance_Notes.md — "Reducing Database Accesses"](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/32_Performance_Notes.md)).

```abap
" BEFORE — anti-pattern: SELECT in a LOOP
LOOP AT lt_orders ASSIGNING FIELD-SYMBOL(<order>).
  SELECT SINGLE vbeln, posnr, matnr
    FROM vbap
    WHERE vbeln = @<order>-vbeln
    INTO @DATA(ls_item).
  " ... process ls_item ...
ENDLOOP.

" AFTER — single bulk read, then in-memory lookup
IF lt_orders IS NOT INITIAL.
  SELECT vbeln, posnr, matnr
    FROM vbap
    FOR ALL ENTRIES IN @lt_orders
    WHERE vbeln = @lt_orders-vbeln
    INTO TABLE @DATA(lt_items).
ENDIF.

SORT lt_items BY vbeln.

LOOP AT lt_orders ASSIGNING FIELD-SYMBOL(<order>).
  READ TABLE lt_items WITH KEY vbeln = <order>-vbeln
    BINARY SEARCH TRANSPORTING NO FIELDS.
  " ... process matching entries ...
ENDLOOP.
```

For even better pushdown, use a CDS view with an association or a join:

```abap
" BEST — single JOIN, fully pushed to HANA
SELECT o~vbeln, i~posnr, i~matnr
  FROM @lt_orders AS o
  INNER JOIN vbap AS i ON i~vbeln = o~vbeln
  INTO TABLE @DATA(lt_result).
```

#### Step 4c: Fix FOR ALL ENTRIES misuse

`FOR ALL ENTRIES` (FAE) is not inherently bad on HANA, but it requires two safeguards ([SAP Note 1912445](https://me.sap.com/notes/1912445)):

1. **Emptiness check**: If the driver table is empty, FAE reads the entire target table.
2. **Duplicate elimination**: FAE implicitly applies `DISTINCT` to the driver table. Ensure you are aware of this behavior.

```abap
" BEFORE — anti-pattern: no emptiness check
SELECT ebeln, ebelp, matnr
  FROM ekpo
  FOR ALL ENTRIES IN @lt_eban
  WHERE ebeln = @lt_eban-ebeln
  INTO TABLE @DATA(lt_ekpo).

" AFTER — guarded FAE
IF lt_eban IS NOT INITIAL.
  SELECT ebeln, ebelp, matnr
    FROM ekpo
    FOR ALL ENTRIES IN @lt_eban
    WHERE ebeln = @lt_eban-ebeln
    INTO TABLE @DATA(lt_ekpo).
ENDIF.
```

In modern ABAP (7.50+), prefer joins with internal tables over FAE when possible, as the optimizer can handle them more efficiently on HANA ([SAP-samples/abap-cheat-sheets, 03_ABAP_SQL.md — "FROM Clause"](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/03_ABAP_SQL.md)):

```abap
" MODERN — join with internal table (ABAP 7.53+)
SELECT e~ebeln, e~ebelp, e~matnr
  FROM @lt_eban AS b
  INNER JOIN ekpo AS e ON e~ebeln = b~ebeln
  INTO TABLE @DATA(lt_ekpo).
```

#### Step 4d: Migrate cluster table reads (BSEG to ACDOCA)

In S/4HANA, the FI line item cluster table `BSEG` is replaced by the Universal Journal table `ACDOCA`. Direct reads from `BSEG` still work via a compatibility view, but they are significantly slower than reading `ACDOCA` directly because the compatibility view must reconstruct the cluster structure ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

```abap
" BEFORE — reads from BSEG compatibility view (very slow)
SELECT bukrs, belnr, gjahr, buzei, koart, dmbtr
  FROM bseg
  WHERE bukrs = @lv_bukrs
    AND gjahr = @lv_gjahr
  INTO TABLE @DATA(lt_bseg).

" AFTER — read from ACDOCA directly
SELECT rbukrs AS bukrs, belnr, gjahr, buzei, koart, hsl AS dmbtr
  FROM acdoca
  WHERE rbukrs = @lv_bukrs
    AND gjahr = @lv_gjahr
    AND rldnr = '0L'
  INTO TABLE @DATA(lt_items).
```

For reusable access, define a CDS view entity over `ACDOCA`:

```abap
@AbapCatalog.viewEnhancementCategory: [#NONE]
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'FI Line Items from Universal Journal'
define view entity ZI_FILineItem
  as select from acdoca
{
  key rbukrs as CompanyCode,
  key belnr  as AccountingDocument,
  key gjahr  as FiscalYear,
  key buzei  as LineItem,
      koart  as AccountType,
      racct  as GLAccount,
      hsl    as AmountInCompanyCodeCurrency,
      rhcur  as CompanyCodeCurrency
}
where rldnr = '0L'.
```

#### Step 4e: Push SORT to the database

Sorting large internal tables in ABAP (`SORT itab`) consumes application server memory and CPU. On HANA, the column store can sort at the database level with near-zero additional cost using `ORDER BY` ([SAP-samples/abap-cheat-sheets, 32_Performance_Notes.md — "Applying a Sort Key"](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/32_Performance_Notes.md)).

```abap
" BEFORE — sort in ABAP
SELECT matnr, werks, lgort, labst
  FROM mard
  INTO TABLE @DATA(lt_mard)
  WHERE werks = @lv_werks.
SORT lt_mard BY matnr werks lgort.

" AFTER — sort pushed to DB
SELECT matnr, werks, lgort, labst
  FROM mard
  WHERE werks = @lv_werks
  ORDER BY matnr, werks, lgort
  INTO TABLE @DATA(lt_mard).
```

#### Step 4f: Fix SELECT SINGLE without fully qualified key

`SELECT SINGLE` without specifying all primary key fields returns a nondeterministic row. The database may return different rows on different executions, which is a functional correctness issue, not just performance. ATC variant `FUNCTIONAL_DB_SAP` flags this ([SAP Note 1912445](https://me.sap.com/notes/1912445)).

```abap
" BEFORE — anti-pattern: partial key (mandt, bukrs are part of key but belnr is missing)
SELECT SINGLE dmbtr FROM bseg
  WHERE bukrs = '1000'
    AND gjahr = '2024'
  INTO @DATA(lv_amount).
" Returns unpredictable row

" AFTER — fully qualified key or use UP TO 1 ROWS with ORDER BY
SELECT hsl AS dmbtr FROM acdoca
  WHERE rbukrs = '1000'
    AND gjahr = '2024'
    AND rldnr = '0L'
  ORDER BY belnr, buzei
  INTO @DATA(lv_amount)
  UP TO 1 ROWS.
ENDSELECT.
```

#### Step 4g: Avoid implicit secondary index assumptions

HANA column store does not use traditional B-tree secondary indexes. Custom secondary indexes defined in ABAP Dictionary on row-store tables (e.g., on `VBAP`, `EKPO`) are not automatically created on HANA column store. Performance tuning through index creation is generally ineffective on HANA; instead, refactor the SQL to be column-store friendly ([SAP Help: ABAP Platform — Using Indexes](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/48b5d6014f18307de10000000a42189b.html)).

**Guideline**: Before requesting a HANA secondary index, first try:
1. Add missing `WHERE` clause predicates to reduce the result set.
2. Use `ORDER BY` to let the HANA optimizer choose the best access path.
3. Consider a CDS view with appropriate annotations for buffering.

### Step 5: Code pushdown — the decision pyramid

The code pushdown pyramid defines the preferred order for pushing computation from the ABAP application server down to the HANA database ([SAP Custom Code Migration Guide, Section "Code Pushdown"](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)):

```
Preference (highest to lowest):

  1. CDS view entities    — declarative, testable, reusable, RAP-ready
  2. AMDP                 — for complex procedural logic not expressible in CDS
  3. Open SQL with WHERE  — standard ABAP SQL with good filter pushdown
  4. Avoid SELECT * + ABAP loops — worst case, maximum data transfer
```

**When to use CDS views** ([SAP Help: CDS View Entities](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/a264a9abf98d4a7c8090c2db1b5c643e.html)):
- Joins, aggregations, calculated fields, currency/unit conversions.
- Replacing custom database views or ABAP Dictionary views.
- Exposing data for Fiori apps via OData service bindings.

**When to use AMDP** ([SAP-samples/abap-cheat-sheets, 12_AMDP.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/12_AMDP.md)):
- Complex imperative logic (e.g., iterative calculations, cursor-based processing).
- Graph or spatial processing available in SQLScript but not in CDS.
- Note: AMDP is harder to unit-test and debug than CDS. Prefer CDS when possible.

### Step 6: Enable Runtime Check Monitor (SRTCM)

SRTCM catches runtime anti-patterns that static ATC checks cannot detect, such as `FOR ALL ENTRIES` called with an empty driver table or `SELECT ... ENDSELECT` returning thousands of rows processed one-by-one ([SAP Note 1885926](https://me.sap.com/notes/1885926)).

1. Transaction `SRTCM` > **Activate Checks**.
2. Select check categories:
   - **DB access in loops** — detects dynamic N+1 patterns.
   - **FAE with empty table** — detects runtime emptiness violations.
   - **SELECT ENDSELECT** — detects row-by-row processing of large result sets.
3. Run for a representative period (1-2 days of batch processing).
4. Review findings under `SRTCM` > **Display Results**.

SRTCM findings complement SQLM data: SQLM tells you *which* statements are expensive, SRTCM tells you *why* the pattern is problematic.

### Step 7: Validate and regression-test

1. Run ATC with `PERFORMANCE_DB` and `FUNCTIONAL_DB_SAP` variants on all modified objects. Zero priority-1 findings required.
2. Compare SQLM metrics before and after remediation (total DB time, executions, rows).
3. Execute functional regression tests for affected business processes (see `sap-migration-testing` skill).
4. For CDS views: validate using CDS test doubles or ABAP Unit tests with `CL_CDS_TEST_ENVIRONMENT`.

## Worked example

### Scenario: Order history report running 40 minutes on HANA

**Context**: After migration from ECC 6.0 on Oracle to S/4HANA 2024 on HANA, report `ZFI_ORDER_HISTORY` takes 40 minutes to complete. On the source system it ran in 8 minutes.

**Step 1 — SQLM analysis**

SQLM shows the following top statement (ranked #1 by total DB time):

| Program | Table | Executions | Total Rows | Total DB Time (s) |
|---|---|---|---|---|
| `ZFI_ORDER_HISTORY` | `BSEG` | 14,200 | 2,840,000 | 2,180 |

The report reads `BSEG` 14,200 times (once per customer in `KNA1`), returning ~200 rows each time. This is a classic N+1 pattern.

**Step 2 — ATC findings**

ATC with variant `PERFORMANCE_DB` reports:
- `PERFORMANCE_DB-SELECT_STAR` on `BSEG` (300+ columns, only 6 used).
- `PERFORMANCE_DB-SELECT_IN_LOOP` in include `ZFI_ORDER_HISTORY_F01`, line 142.

**Step 3 — SRTCM finding**

SRTCM flags the `FOR ALL ENTRIES` at line 185 — the driver table `lt_kna1` occasionally runs empty during delta processing, causing a full table scan of `BSEG`.

**Step 4 — Original code**

```abap
" ZFI_ORDER_HISTORY_F01, line 130
SELECT * FROM kna1
  INTO TABLE @DATA(lt_kna1)
  WHERE land1 = @p_land1.

LOOP AT lt_kna1 ASSIGNING FIELD-SYMBOL(<kna1>).
  " Line 142 — SELECT in loop
  SELECT * FROM bseg
    WHERE bukrs = @p_bukrs
      AND kunnr = @<kna1>-kunnr
      AND gjahr = @p_gjahr
    INTO TABLE @DATA(lt_bseg).

  LOOP AT lt_bseg ASSIGNING FIELD-SYMBOL(<bseg>).
    APPEND VALUE #( kunnr = <kna1>-kunnr
                    belnr = <bseg>-belnr
                    dmbtr = <bseg>-dmbtr ) TO lt_report.
  ENDLOOP.
ENDLOOP.
```

**Step 5 — Refactored solution**

Create a CDS view entity joining `ACDOCA` to customer master:

```abap
@AbapCatalog.viewEnhancementCategory: [#NONE]
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Order History - Customer Line Items'
define view entity ZI_OrderHistory
  as select from acdoca as j
  inner join     kna1   as c on c.kunnr = j.kunnr
{
  key j.rbukrs  as CompanyCode,
  key j.belnr   as AccountingDocument,
  key j.gjahr   as FiscalYear,
  key j.buzei   as LineItem,
      c.kunnr   as Customer,
      c.name1   as CustomerName,
      c.land1   as Country,
      j.koart   as AccountType,
      j.racct   as GLAccount,
      j.hsl     as AmountInCompanyCodeCurrency,
      j.rhcur   as CompanyCodeCurrency,
      j.budat   as PostingDate
}
where j.rldnr = '0L'
  and j.koart = 'D'.
```

Refactored ABAP report:

```abap
" Single SELECT — fully pushed to HANA
SELECT CompanyCode, AccountingDocument, FiscalYear, LineItem,
       Customer, CustomerName, GLAccount,
       AmountInCompanyCodeCurrency, PostingDate
  FROM ZI_OrderHistory
  WHERE CompanyCode = @p_bukrs
    AND FiscalYear  = @p_gjahr
    AND Country     = @p_land1
  INTO TABLE @DATA(lt_report).
```

**Result**: Runtime drops from **40 minutes to 12 seconds**. SQLM shows 1 execution returning 18,400 rows in 0.3 seconds. The 14,200 individual `BSEG` round-trips are eliminated entirely.

## Anti-patterns

1. **Adding HANA secondary indexes to fix slow queries**.
   HANA column store does not benefit from traditional B-tree indexes the way row-store databases do. Adding indexes increases memory consumption and DDL complexity without addressing the root cause. Refactor the SQL first ([SAP Help: ABAP Platform — Using Indexes](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/48b5d6014f18307de10000000a42189b.html)).

2. **Treating FOR ALL ENTRIES as always bad**.
   FAE works well on HANA *when* the driver table is not empty and the result set is bounded. The kernel translates FAE into `IN` lists or temp-table joins depending on the driver table size. The anti-pattern is using FAE without the emptiness guard, not using FAE itself ([SAP Note 1912445](https://me.sap.com/notes/1912445)).

3. **Pushing all logic into AMDP because "pushdown is good"**.
   AMDP (SQLScript procedures) are harder to test with ABAP Unit, harder to debug in ADT, and not transportable via CTS in all scenarios. CDS view entities are declarative, testable with `CL_CDS_TEST_ENVIRONMENT`, and integrate with RAP. Use AMDP only when CDS cannot express the required logic ([SAP-samples/abap-cheat-sheets, 12_AMDP.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/12_AMDP.md)).

4. **Relying on SE30 / SAT results from the source ECC system**.
   Performance characteristics change drastically on HANA. Statements that were fast on row-store (e.g., indexed lookups on `BSEG`) may be slow on column-store, and vice versa. Always reprofile on the HANA target system using SQLM, SRTCM, and the ABAP Profiler in ADT ([SAP Note 2201632](https://me.sap.com/notes/2201632)).

5. **Using SELECT * "because we might need more fields later"**.
   On HANA column store, each additional column in the SELECT list costs memory for column materialization. Wide tables like `EKPO` (200+ fields), `BSEG` (300+ fields), or `VBAP` (150+ fields) are especially affected. Always specify the exact field list needed for the current use case ([SAP-samples/abap-cheat-sheets, 32_Performance_Notes.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/32_Performance_Notes.md)).

6. **String concatenation in loops without string templates**.
   Building strings character by character in a loop using `CONCATENATE` creates repeated memory allocations. Use ABAP string templates with `LET` expressions for bulk string construction ([SAP/abap-cleaner rule set](https://github.com/SAP/abap-cleaner/tree/952c68076fb0c5a258d947ca269e876d12603190)).

## References

- [SAP Note 2201632 — SQL Monitor for ABAP](https://me.sap.com/notes/2201632): How to enable, configure, and interpret SQL Monitor results for custom code performance analysis.
- [SAP Note 1885926 — Runtime Check Monitor (SRTCM)](https://me.sap.com/notes/1885926): Configuration and usage of SRTCM for detecting runtime anti-patterns.
- [SAP Note 1912445 — Recommended ATC check variants for ABAP custom code](https://me.sap.com/notes/1912445): Central note listing `PERFORMANCE_DB`, `FUNCTIONAL_DB_SAP`, and other recommended check variants.
- [SAP Note 2436688 — ATC checks for ABAP custom code migration to S/4HANA](https://me.sap.com/notes/2436688): Extended ATC checks for migration-specific performance patterns.
- [SAP Note 2270407 — Universal Journal (ACDOCA)](https://me.sap.com/notes/2270407): Details on the ACDOCA table replacing BSEG and other cluster tables.
- [SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE): Canonical runbook covering SQL Monitor, SRTCM, code pushdown, and performance optimization sections.
- [SAP Help: ABAP Platform — Performance Notes](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/4ec5f2306e391014adc9fffe56f91a3e.html): Official ABAP platform documentation on database access optimization.
- [SAP Help: CDS View Entities](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/a264a9abf98d4a7c8090c2db1b5c643e.html): Documentation on CDS view entity syntax and capabilities.
- [SAP Help: DBA Cockpit (ST04)](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/48b5d6014f18307de10000000a42189b.html): HANA-specific expensive statement analysis via DBA Cockpit.
- [SAP-samples/abap-cheat-sheets — 03_ABAP_SQL.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/03_ABAP_SQL.md): Modern ABAP SQL syntax patterns including joins with internal tables and typed literals (Apache-2.0).
- [SAP-samples/abap-cheat-sheets — 12_AMDP.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/12_AMDP.md): ABAP Managed Database Procedures reference and best practices (Apache-2.0).
- [SAP-samples/abap-cheat-sheets — 15_CDS_View_Entities.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/15_CDS_View_Entities.md): CDS view entity syntax, annotations, and associations (Apache-2.0).
- [SAP-samples/abap-cheat-sheets — 32_Performance_Notes.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/32_Performance_Notes.md): ABAP performance notes covering database access and internal table optimization (Apache-2.0).
- [SAP/abap-cleaner](https://github.com/SAP/abap-cleaner/tree/952c68076fb0c5a258d947ca269e876d12603190): Automated ABAP code cleanup rules, many aligned with HANA performance patterns (Apache-2.0).
