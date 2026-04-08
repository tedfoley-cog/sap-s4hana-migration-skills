# Worked Example: Order History Report Running 40 Minutes on HANA

> **Sources**: [SAP Note 2201632](https://me.sap.com/notes/2201632) — SQL Monitor,
> [SAP Note 2270407](https://me.sap.com/notes/2270407) — Universal Journal (ACDOCA),
> [SAP-samples/abap-cheat-sheets](https://github.com/SAP-samples/abap-cheat-sheets) (Apache-2.0).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Context](#context)
- [Step 1 — SQLM analysis](#step-1--sqlm-analysis)
- [Step 2 — ATC findings](#step-2--atc-findings)
- [Step 3 — SRTCM finding](#step-3--srtcm-finding)
- [Step 4 — Original code](#step-4--original-code)
- [Step 5 — Refactored solution](#step-5--refactored-solution)
- [Result](#result)

## Context

After migration from ECC 6.0 on Oracle to S/4HANA 2024 on HANA, report `ZFI_ORDER_HISTORY` takes 40 minutes to complete. On the source system it ran in 8 minutes.

## Step 1 — SQLM analysis

SQLM shows the following top statement (ranked #1 by total DB time):

| Program | Table | Executions | Total Rows | Total DB Time (s) |
|---|---|---|---|---|
| `ZFI_ORDER_HISTORY` | `BSEG` | 14,200 | 2,840,000 | 2,180 |

The report reads `BSEG` 14,200 times (once per customer in `KNA1`), returning ~200 rows each time. This is a classic N+1 pattern.

## Step 2 — ATC findings

ATC with variant `PERFORMANCE_DB` reports:
- `PERFORMANCE_DB-SELECT_STAR` on `BSEG` (300+ columns, only 6 used).
- `PERFORMANCE_DB-SELECT_IN_LOOP` in include `ZFI_ORDER_HISTORY_F01`, line 142.

## Step 3 — SRTCM finding

SRTCM flags the `FOR ALL ENTRIES` at line 185 — the driver table `lt_kna1` occasionally runs empty during delta processing, causing a full table scan of `BSEG`.

## Step 4 — Original code

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

## Step 5 — Refactored solution

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

## Result

Runtime drops from **40 minutes to 12 seconds**. SQLM shows 1 execution returning 18,400 rows in 0.3 seconds. The 14,200 individual `BSEG` round-trips are eliminated entirely.
