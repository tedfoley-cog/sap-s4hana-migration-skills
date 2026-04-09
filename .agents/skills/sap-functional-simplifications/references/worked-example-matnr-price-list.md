# Worked Example: MATNR Length Extension — Custom Report `Z_PRICE_LIST`

> **Sources**: [SAP Note 2270333](https://me.sap.com/notes/2270333) — Material Number Field Length Extension,
> [SAP Note 2179039](https://me.sap.com/notes/2179039) — MATNR Length Impact on Custom Code.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Identify the finding](#step-1--identify-the-finding)
- [Step 2 — Review the offending code](#step-2--review-the-offending-code)
- [Step 3 — Apply the fix](#step-3--apply-the-fix)
- [Step 4 — Fix the structure Z_PRICE_S](#step-4--fix-the-structure-z_price_s)
- [Step 5 — Adjust ALV column width](#step-5--adjust-alv-column-width)
- [Step 6 — Flag downstream interfaces](#step-6--flag-downstream-interfaces)
- [Step 7 — Rerun ATC](#step-7--rerun-atc)

## Scenario

A custom pricing report `Z_PRICE_LIST` was written in ECC and is flagged by ATC after running the `S4HANA_READINESS` check variant.

## Step 1 — Identify the finding

ATC reports the following finding in program `Z_PRICE_LIST`:

```
CHECK: S4HANA_READINESS / MATNR_LENGTH
Object: Z_PRICE_LIST  Line: 42
Message: Hard-coded material number length detected (c LENGTH 18).
         Use TYPE matnr instead.
```

## Step 2 — Review the offending code

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

## Step 3 — Apply the fix

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

## Step 4 — Fix the structure `Z_PRICE_S`

Check the DDIC structure `Z_PRICE_S`. If the `MATNR` component is typed as `c(18)`, change it to reference data element `MATNR`:

```
Component  Typing       Before         After
MATNR      Data element CHAR18    →    MATNR
MAKTX      Data element MAKTX         (unchanged)
NETPR      Data element NETPR         (unchanged)
```

## Step 5 — Adjust ALV column width

If the report uses a manual field catalog, update `outputlen` from `18` to `40`:

```abap
ls_fieldcat-fieldname = 'MATNR'.
ls_fieldcat-outputlen = 40.            " was 18
```

If using `i_structure_name`, ALV picks up the new width automatically from the DDIC.

## Step 6 — Flag downstream interfaces

The report's output is also consumed by a flat-file interface `Z_PRICE_EXPORT` that writes a fixed-width file with an 18-character MATNR column. Create a follow-up task for the integration team:

> **Action item**: Widen `Z_PRICE_EXPORT` flat-file layout from 18 to 40 characters for MATNR field. Coordinate with receiving system (external pricing tool) to accept the wider format. ([SAP Note 2179039](https://me.sap.com/notes/2179039))

## Step 7 — Rerun ATC

After applying all fixes, rerun ATC with the `S4HANA_READINESS` variant. The `MATNR_LENGTH` finding for `Z_PRICE_LIST` should be resolved.
