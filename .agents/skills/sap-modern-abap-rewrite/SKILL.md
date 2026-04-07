---
name: "sap-modern-abap-rewrite"
description: |
  Use when modernizing legacy ABAP code (4.6C / 6.0 / 7.0 era) to ABAP 7.4+
  or ABAP Cloud syntax after an S/4HANA conversion: replacing READ TABLE with
  table expressions, replacing CONCATENATE with string templates, converting
  FORM routines to class methods, introducing inline DATA declarations,
  applying constructor expressions (VALUE, NEW, CORRESPONDING, REDUCE, FILTER),
  replacing CALL METHOD with functional calls, replacing CREATE OBJECT with NEW,
  adding ABAP Unit tests to untested custom code, or preparing custom objects
  for ABAP Cloud / clean core compliance by removing forbidden classic statements.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025"
  sources:
    - "SAP-samples/abap-cheat-sheets (GitHub, Apache-2.0)"
    - "SAP/abap-cleaner (GitHub, Apache-2.0)"
    - "SAP/abap-atc-cr-cv-s4hc-tools (GitHub, Apache-2.0)"
    - "SAP Note 2436688 - SAP S/4HANA Custom Code Checks"
    - "SAP Help Portal - ABAP Keyword Documentation"
    - "SAP Press - ABAP to the Future (3rd edition)"
    - "Clean ABAP Styleguide (SAP/styleguides)"
related_skills:
  - sap-hana-performance
  - sap-clean-core-extensibility
  - sap-atc-readiness
---

## When to use this skill

Use this skill **after** ATC readiness checks have been triaged (see `sap-atc-readiness`) and you know which custom objects will be retained in the converted S/4HANA system. This skill covers language-level modernization — making retained code readable, type-safe, testable, and (optionally) ABAP Cloud-compliant.

Typical triggers:

- ATC findings flagging obsolete statements (`MOVE ... TO`, `CALL METHOD`, `ADD ... TO`, `READ TABLE ... INTO`) that need replacement with modern equivalents.
- A project mandate to adopt ABAP 7.4+ syntax for all retained custom code.
- Preparing custom objects for Tier-1 (ABAP Cloud) software components under the clean core strategy.
- Legacy FORM routines or function modules that need conversion to OO class methods before they can be unit-tested.
- Code review feedback requesting constructor expressions, string templates, or inline declarations.

This skill is **complementary** to `sap-hana-performance` (which focuses on database-layer patterns such as code pushdown and CDS views). This skill focuses on the ABAP language layer.

## Prerequisites

1. **ABAP platform >= 7.40 SP08** — most syntax covered here requires this as a minimum. Some features (e.g., `FILTER`, `REDUCE`) require 7.50+. ABAP Cloud features require SAP BTP ABAP Environment or S/4HANA Cloud ([SAP Help: ABAP Release News](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abennews.htm)).
2. **ATC triage completed** — do not modernize code that ATC flagged for deletion. Check the `sap-atc-readiness` skill output first.
3. **ADT (ABAP Development Tools)** installed with the [ABAP cleaner plug-in](https://github.com/SAP/abap-cleaner) (v1.24+). This automates many of the patterns below at a single keystroke (`Ctrl+4`) ([SAP/abap-cleaner README](https://github.com/SAP/abap-cleaner)).
4. **ABAP Unit runner** available in the target system (transaction `SE80` or ADT).
5. If targeting ABAP Cloud compliance, the **ABAP Cloud Readiness ATC check variant** must be active in the system ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

## Quick decision tree

```
Is the object flagged for deletion by ATC / scoping?
  YES -> Do NOT modernize. Delete it. (See sap-atc-readiness.)
  NO  -> Continue.

Is the object a FORM routine or INCLUDE?
  YES -> Step 1: Extract to a class method first (see Procedure §1).
  NO  -> Continue.

Does the code contain obsolete statements (MOVE, ADD, CALL METHOD, etc.)?
  YES -> Run abap-cleaner with the "default" profile. It handles most of
         these automatically (see Procedure §2).
  NO  -> Continue.

Does the code use READ TABLE ... INTO / WITH KEY?
  YES -> Replace with table expressions (see Procedure §3).
  NO  -> Continue.

Does the code use CONCATENATE or WRITE ... TO for string assembly?
  YES -> Replace with string templates (see Procedure §4).
  NO  -> Continue.

Does the code lack unit tests?
  YES -> Add ABAP Unit test class (see Procedure §7).
  NO  -> Continue.

Is the target a Tier-1 (ABAP Cloud) software component?
  YES -> Check ABAP Cloud restrictions (see Procedure §8).
  NO  -> Done.
```

## Procedure

### 1. Extract FORM routines and INCLUDEs to class methods

FORM routines and INCLUDE programs cannot be unit-tested in isolation and are forbidden in ABAP Cloud ([SAP-samples/abap-cheat-sheets: 19_ABAP_for_Cloud_Development.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/19_ABAP_for_Cloud_Development.md)). Convert them to static or instance methods on a class.

**Before:**
```abap
FORM build_invoice_list USING it_orders TYPE zt_orders
                        CHANGING ct_invoices TYPE zt_invoices.
  DATA: ls_order   TYPE zs_order,
        ls_invoice TYPE zs_invoice,
        lv_text    TYPE string.
  LOOP AT it_orders INTO ls_order.
    CLEAR ls_invoice.
    ls_invoice-order_id = ls_order-order_id.
    CONCATENATE 'INV-' ls_order-order_id INTO lv_text.
    ls_invoice-invoice_no = lv_text.
    APPEND ls_invoice TO ct_invoices.
  ENDLOOP.
ENDFORM.
```

**After:**
```abap
CLASS zcl_invoice_builder DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES: zt_orders   TYPE STANDARD TABLE OF zs_order WITH DEFAULT KEY,
           zt_invoices TYPE STANDARD TABLE OF zs_invoice WITH DEFAULT KEY.
    CLASS-METHODS build_invoice_list
      IMPORTING it_orders          TYPE zt_orders
      RETURNING VALUE(rt_invoices) TYPE zt_invoices.
ENDCLASS.

CLASS zcl_invoice_builder IMPLEMENTATION.
  METHOD build_invoice_list.
    rt_invoices = VALUE #(
      FOR ls_order IN it_orders
      ( order_id   = ls_order-order_id
        invoice_no = |INV-{ ls_order-order_id }| ) ).
  ENDMETHOD.
ENDCLASS.
```

Key changes: `FORM` -> static `METHOD`; `CHANGING` -> `RETURNING`; loop + append -> `VALUE #( FOR ... )` constructor expression ([SAP-samples/abap-cheat-sheets: 05_Constructor_Expressions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/05_Constructor_Expressions.md)).

### 2. Run abap-cleaner for automated fixes

The [ABAP cleaner](https://github.com/SAP/abap-cleaner) tool automates ~100 cleanup rules. The most relevant rules for modernization are:

| abap-cleaner rule | What it does |
|---|---|
| Replace CALL METHOD with functional call | `CALL METHOD obj->meth EXPORTING a = b` -> `obj->meth( a = b )` |
| Replace CREATE OBJECT with NEW constructor | `CREATE OBJECT lo_obj TYPE zcl_foo` -> `lo_obj = NEW zcl_foo( )` |
| Replace obsolete MOVE ... TO with = | `MOVE lv_a TO lv_b` -> `lv_b = lv_a` |
| Replace obsolete ADD ... TO with += | `ADD 1 TO lv_count` -> `lv_count += 1` |
| Replace READ TABLE with table expression | `READ TABLE lt INTO ls WHERE k = v` -> `ls = lt[ k = v ]` |
| Use string templates to assemble text | `CONCATENATE a b INTO c` -> `c = \|{ a }{ b }\|` |
| Replace DESCRIBE TABLE ... LINES with lines( ) | `DESCRIBE TABLE lt LINES lv_n` -> `lv_n = lines( lt )` |
| Replace TRANSLATE with string functions | `TRANSLATE lv TO UPPER CASE` -> `lv = to_upper( lv )` |
| Replace CONDENSE with string function | `CONDENSE lv` -> `lv = condense( lv )` |
| Omit optional EXPORTING | Removes redundant `EXPORTING` keyword |
| Omit RECEIVING | Replaces `RECEIVING` with inline assignment |
| Use FINAL for immutable variables | `DATA(lv_x) = 5.` -> `FINAL(lv_x) = 5.` (ABAP 7.57+) |

([SAP/abap-cleaner: docs/rules.md](https://github.com/SAP/abap-cleaner/blob/main/docs/rules.md))

**Usage in ADT:** `Ctrl+Shift+4` (interactive) or `Ctrl+4` (automated). Always review the diff before saving — abap-cleaner cannot detect dynamic call sites that may break if signatures change.

### 3. Replace READ TABLE with table expressions

Table expressions (available since ABAP 7.40 SP05) are more concise and raise `CX_SY_ITAB_LINE_NOT_FOUND` instead of setting `SY-SUBRC` ([SAP-samples/abap-cheat-sheets: 01_Internal_Tables.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/01_Internal_Tables.md)).

**Before:**
```abap
DATA ls_partner TYPE zs_bp_data.
READ TABLE lt_partners WITH KEY partner_id = lv_id INTO ls_partner.
IF sy-subrc = 0.
  lv_name = ls_partner-name.
ENDIF.
```

**After (with existence check):**
```abap
IF line_exists( lt_partners[ partner_id = lv_id ] ).
  DATA(lv_name) = lt_partners[ partner_id = lv_id ]-name.
ENDIF.
```

**After (with exception handling):**
```abap
TRY.
    DATA(lv_name) = lt_partners[ partner_id = lv_id ]-name.
  CATCH cx_sy_itab_line_not_found.
    " handle missing entry
ENDTRY.
```

**After (with OPTIONAL for defaulting):**
```abap
DATA(ls_partner) = VALUE #( lt_partners[ partner_id = lv_id ] OPTIONAL ).
```

The `OPTIONAL` addition returns an initial structure if the line is not found, avoiding both `SY-SUBRC` and exceptions ([SAP-samples/abap-cheat-sheets: 05_Constructor_Expressions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/05_Constructor_Expressions.md)).

### 4. Use string templates instead of CONCATENATE

String templates (`|...|`) support embedded expressions and formatting options. They are available since ABAP 7.02 ([SAP-samples/abap-cheat-sheets: 07_String_Processing.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/07_String_Processing.md)).

**Before:**
```abap
DATA lv_msg TYPE string.
CONCATENATE 'Order' lv_order_id 'has' lv_count 'items, total:'
            lv_amount INTO lv_msg SEPARATED BY space.
```

**After:**
```abap
DATA(lv_msg) = |Order { lv_order_id } has { lv_count } items, total: { lv_amount CURRENCY = lv_waers }|.
```

The abap-cleaner rule "Use string templates to assemble text" automates this transformation ([SAP/abap-cleaner: docs/rules/StringTemplateRule.md](https://github.com/SAP/abap-cleaner/blob/main/docs/rules/StringTemplateRule.md)).

### 5. Use constructor expressions (VALUE, NEW, CORRESPONDING, REDUCE, FILTER)

Constructor expressions replace verbose multi-statement patterns with single expressions. They were introduced across ABAP 7.40–7.50 ([SAP-samples/abap-cheat-sheets: 05_Constructor_Expressions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/05_Constructor_Expressions.md)).

**VALUE — build structures and tables inline:**
```abap
" Before
DATA lt_status TYPE TABLE OF zs_status.
DATA ls_status TYPE zs_status.
ls_status-code = 'A'. ls_status-text = 'Active'. APPEND ls_status TO lt_status.
ls_status-code = 'I'. ls_status-text = 'Inactive'. APPEND ls_status TO lt_status.

" After
DATA(lt_status) = VALUE zt_status(
  ( code = 'A' text = 'Active' )
  ( code = 'I' text = 'Inactive' ) ).
```

**CORRESPONDING — map between structures with different field names:**
```abap
DATA(ls_target) = CORRESPONDING zs_target( ls_source MAPPING target_field = source_field ).
```

**REDUCE — aggregate values:**
```abap
DATA(lv_total) = REDUCE decfloat34(
  INIT sum = CONV decfloat34( 0 )
  FOR ls_item IN lt_items
  NEXT sum = sum + ls_item-amount ).
```

**FILTER — extract subset from sorted/hashed table:**
```abap
DATA(lt_active) = FILTER #( lt_partners WHERE status = 'A' ).
```
`FILTER` requires the source table to have a sorted or hashed key on the filtered field (ABAP 7.50+) ([SAP Help: ABAP Keyword Documentation — FILTER](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abenconstructor_expression_filter.htm)).

**COND / SWITCH — conditional value assignment:**
```abap
" Before
IF lv_status = 'A'.
  lv_text = 'Active'.
ELSEIF lv_status = 'I'.
  lv_text = 'Inactive'.
ELSE.
  lv_text = 'Unknown'.
ENDIF.

" After
DATA(lv_text) = SWITCH string( lv_status
  WHEN 'A' THEN 'Active'
  WHEN 'I' THEN 'Inactive'
  ELSE 'Unknown' ).
```

### 6. Use inline declarations and modern loop patterns

**Inline DATA declarations** (ABAP 7.40 SP02) eliminate the need to pre-declare local variables at method top ([SAP-samples/abap-cheat-sheets: 16_Data_Types_and_Objects.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/16_Data_Types_and_Objects.md)):

```abap
" Before
DATA lv_count TYPE i.
lv_count = lines( lt_items ).

" After
DATA(lv_count) = lines( lt_items ).
```

**FINAL declarations** (ABAP 7.57 / ABAP Cloud) mark variables as immutable after initial assignment. Use for values that should not change after initialization:

```abap
FINAL(lv_timestamp) = utclong_current( ).
```

The abap-cleaner rule "Use FINAL for immutable variables" can detect candidates automatically ([SAP/abap-cleaner: docs/rules.md](https://github.com/SAP/abap-cleaner/blob/main/docs/rules.md)).

**LOOP AT ... REFERENCE INTO** avoids copying large structures:
```abap
" Before
FIELD-SYMBOLS: <ls_item> TYPE zs_item.
LOOP AT lt_items ASSIGNING <ls_item>.

" After
LOOP AT lt_items REFERENCE INTO DATA(lr_item).
```

**FOR iteration expressions** build tables without explicit loops:
```abap
DATA(lt_ids) = VALUE zt_id_tab(
  FOR ls_partner IN lt_partners
  WHERE ( status = 'A' )
  ( ls_partner-partner_id ) ).
```

### 7. Add ABAP Unit tests

Every modernized class should have at least one ABAP Unit test class. ABAP Unit is the built-in xUnit framework available since NetWeaver 7.0 ([SAP-samples/abap-cheat-sheets: 14_ABAP_Unit_Tests.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md)).

```abap
CLASS ltcl_invoice_builder DEFINITION FINAL
  FOR TESTING RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    METHODS test_empty_input    FOR TESTING.
    METHODS test_single_order   FOR TESTING.
ENDCLASS.

CLASS ltcl_invoice_builder IMPLEMENTATION.
  METHOD test_empty_input.
    DATA(lt_result) = zcl_invoice_builder=>build_invoice_list(
      it_orders = VALUE #( ) ).
    cl_abap_unit_assert=>assert_initial( lt_result ).
  ENDMETHOD.

  METHOD test_single_order.
    DATA(lt_orders) = VALUE zcl_invoice_builder=>zt_orders(
      ( order_id = '1000' ) ).
    DATA(lt_result) = zcl_invoice_builder=>build_invoice_list(
      it_orders = lt_orders ).
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1 ).
    cl_abap_unit_assert=>assert_equals(
      act = lt_result[ 1 ]-invoice_no
      exp = |INV-1000| ).
  ENDMETHOD.
ENDCLASS.
```

Key assertion methods: `assert_equals`, `assert_initial`, `assert_not_initial`, `assert_true`, `assert_false`, `assert_subrc`, `fail` ([SAP-samples/abap-cheat-sheets: 14_ABAP_Unit_Tests.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md)).

For dependencies (database, RFC, authority checks), use **test doubles** via `CL_OSQL_TEST_ENVIRONMENT` (SQL), `CL_ABAP_TESTDOUBLE` (interfaces), or manual test seams.

### 8. ABAP Cloud restrictions

If the target software component uses **ABAP language version "ABAP for Cloud Development"**, additional restrictions apply. The ATC check variant from [SAP Note 2436688](https://me.sap.com/notes/2436688) enforces these. Key restrictions:

| Forbidden in ABAP Cloud | Replacement |
|---|---|
| Direct DB access to non-released tables (e.g., `SELECT FROM bkpf`) | Use released CDS views or APIs. Check released objects via `CL_ABAP_CLOUD` or in ADT under "Released Objects" ([SAP-samples/abap-cheat-sheets: 19_ABAP_for_Cloud_Development.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/19_ABAP_for_Cloud_Development.md)). |
| Classic function modules (`CALL FUNCTION`) | Use released APIs or wrapper classes. |
| Dynamic SQL (`GENERATE SUBROUTINE POOL`, native SQL via `EXEC SQL`) | Use ABAP SQL with `@`-escaped host variables exclusively. |
| `FORM` / `PERFORM` | Class methods. |
| Non-released SAP classes/interfaces | Check the released object list; use `IF_<released_interface>`. |
| Classic dynpro (`CALL SCREEN`, `MODULE ... INPUT/OUTPUT`) | SAP Fiori / RAP-based UIs. |
| Classic reports with `WRITE` / selection screens (`PARAMETERS`, `SELECT-OPTIONS`) | RAP-based apps or `CL_SALV_*` for display ([SAP-samples/abap-cheat-sheets: 20_Selection_Screens_Lists.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/20_Selection_Screens_Lists.md)). |

**`@`-escaped host variables** are mandatory in ABAP Cloud for all ABAP SQL statements. They are also best practice in standard ABAP from 7.40 SP05 onward (strict mode):

```abap
" Before (classic Open SQL)
SELECT matnr maktx FROM makt INTO TABLE lt_makt
  WHERE spras = sy-langu.

" After (ABAP SQL with host variable escaping)
SELECT matnr, maktx FROM makt INTO TABLE @DATA(lt_makt)
  WHERE spras = @sy-langu.
```

The `@` prefix disambiguates ABAP variables from SQL identifiers and is required when strict mode is enabled ([SAP Help: ABAP SQL — Host Variables](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abapselect_hostvar.htm)).

To migrate existing ATC exemptions from the classic ABAP Cloud Readiness check to the new Clean Core checks, use the [Exemption Migration Tool](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools) ([SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools)).

### 9. Replace exception handling with CX_* classes

Legacy code uses `SY-SUBRC` checks after every function call. Modern ABAP uses class-based exceptions (`CX_STATIC_CHECK`, `CX_DYNAMIC_CHECK`, `CX_NO_CHECK`) which propagate automatically and carry structured error information ([SAP-samples/abap-cheat-sheets: 27_Exceptions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/27_Exceptions.md)).

**Before:**
```abap
CALL FUNCTION 'BAPI_MATERIAL_GET_DETAIL'
  EXPORTING matnr = lv_matnr
  IMPORTING material_general_data = ls_data
  EXCEPTIONS OTHERS = 1.
IF sy-subrc <> 0.
  MESSAGE 'Material not found' TYPE 'E'.
ENDIF.
```

**After (using a wrapper class with exception):**
```abap
TRY.
    DATA(ls_data) = zcl_material_api=>get_detail( lv_matnr ).
  CATCH zcx_material_not_found INTO DATA(lx_err).
    " structured error with attributes: lx_err->matnr, lx_err->get_text( )
ENDTRY.
```

When wrapping existing function modules, create a custom exception class inheriting from `CX_STATIC_CHECK` (for expected errors callers must handle) or `CX_DYNAMIC_CHECK` (for programming errors).

## Worked example

### Modernizing `Z_BUILD_INVOICE_LIST`

**Context:** After S/4HANA conversion, ATC confirmed that program `Z_INVOICE_REPORT` and its form routine `BUILD_INVOICE_LIST` are actively used and must be retained. The code is 4.6C-era ABAP.

#### Original code (80 lines, FORM-based)

```abap
*&---------------------------------------------------------------------*
*& Form BUILD_INVOICE_LIST
*&---------------------------------------------------------------------*
FORM build_invoice_list USING it_orders TYPE zt_orders
                        CHANGING ct_invoices TYPE zt_invoices
                                 cv_total    TYPE p.
  DATA: ls_order    TYPE zs_order,
        ls_invoice  TYPE zs_invoice,
        lv_text     TYPE string,
        lv_idx      TYPE sy-tabix,
        ls_customer TYPE zs_customer.

  LOOP AT it_orders INTO ls_order.
    CLEAR ls_invoice.
    ls_invoice-order_id = ls_order-order_id.

    CONCATENATE 'INV-' ls_order-order_id INTO lv_text.
    ls_invoice-invoice_no = lv_text.

    READ TABLE gt_customers WITH KEY customer_id = ls_order-customer_id
      INTO ls_customer.
    IF sy-subrc = 0.
      CONCATENATE ls_customer-first_name ls_customer-last_name
        INTO ls_invoice-customer_name SEPARATED BY space.
    ENDIF.

    ls_invoice-net_amount = ls_order-quantity * ls_order-unit_price.
    ls_invoice-tax_amount = ls_invoice-net_amount * '0.19'.
    ls_invoice-gross_amount = ls_invoice-net_amount + ls_invoice-tax_amount.

    ADD ls_invoice-gross_amount TO cv_total.
    APPEND ls_invoice TO ct_invoices.
  ENDLOOP.
ENDFORM.
```

#### Step 1 — Extract to class method `ZCL_INVOICE_BUILDER=>BUILD_LIST`

Create class `ZCL_INVOICE_BUILDER` with a static method. Replace `USING`/`CHANGING` with `IMPORTING`/`RETURNING`. Move the customer lookup into a constructor-injected dependency for testability.

#### Step 2 — Replace READ TABLE with table expression

```abap
" Before
READ TABLE it_customers WITH KEY customer_id = ls_order-customer_id
  INTO ls_customer.
IF sy-subrc = 0.

" After
DATA(ls_customer) = VALUE #( it_customers[ customer_id = ls_order-customer_id ] OPTIONAL ).
IF ls_customer IS NOT INITIAL.
```

#### Step 3 — Build result with VALUE #( FOR ... )

```abap
rt_invoices = VALUE #(
  FOR ls_ord IN it_orders
  LET ls_cust = VALUE #( it_customers[ customer_id = ls_ord-customer_id ] OPTIONAL )
      lv_net  = ls_ord-quantity * ls_ord-unit_price
  IN
  ( order_id       = ls_ord-order_id
    invoice_no     = |INV-{ ls_ord-order_id }|
    customer_name  = COND #( WHEN ls_cust IS NOT INITIAL
                             THEN |{ ls_cust-first_name } { ls_cust-last_name }| )
    net_amount     = lv_net
    tax_amount     = lv_net * gc_tax_rate
    gross_amount   = lv_net * ( 1 + gc_tax_rate ) ) ).
```

This uses `FOR` iteration, `LET` for intermediate values, `COND` for conditional assignment, and string templates — all in a single expression ([SAP-samples/abap-cheat-sheets: 05_Constructor_Expressions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/05_Constructor_Expressions.md)).

#### Step 4 — Replace CONCATENATE with string templates

Already done above: `|INV-{ ls_ord-order_id }|` and `|{ ls_cust-first_name } { ls_cust-last_name }|`.

#### Step 5 — Compute total with REDUCE

```abap
DATA(lv_total) = REDUCE decfloat34(
  INIT sum = CONV decfloat34( 0 )
  FOR ls_inv IN rt_invoices
  NEXT sum = sum + ls_inv-gross_amount ).
```

#### Step 6 — Add ABAP Unit tests

```abap
CLASS ltcl_invoice_builder DEFINITION FINAL
  FOR TESTING RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    DATA mt_customers TYPE zcl_invoice_builder=>zt_customers.
    METHODS setup.
    METHODS test_empty_orders         FOR TESTING.
    METHODS test_invoice_calculation  FOR TESTING.
ENDCLASS.

CLASS ltcl_invoice_builder IMPLEMENTATION.
  METHOD setup.
    mt_customers = VALUE #(
      ( customer_id = 'C001' first_name = 'Jane' last_name = 'Smith' ) ).
  ENDMETHOD.

  METHOD test_empty_orders.
    DATA(lt_result) = zcl_invoice_builder=>build_list(
      it_orders    = VALUE #( )
      it_customers = mt_customers ).
    cl_abap_unit_assert=>assert_initial( lt_result ).
  ENDMETHOD.

  METHOD test_invoice_calculation.
    DATA(lt_orders) = VALUE zcl_invoice_builder=>zt_orders(
      ( order_id = '1000' customer_id = 'C001'
        quantity = 10 unit_price = '25.00' ) ).
    DATA(lt_result) = zcl_invoice_builder=>build_list(
      it_orders    = lt_orders
      it_customers = mt_customers ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals(
      act = lt_result[ 1 ]-invoice_no exp = |INV-1000| ).
    cl_abap_unit_assert=>assert_equals(
      act = lt_result[ 1 ]-net_amount exp = CONV decfloat34( '250.00' ) ).
    cl_abap_unit_assert=>assert_equals(
      act = lt_result[ 1 ]-customer_name exp = |Jane Smith| ).
  ENDMETHOD.
ENDCLASS.
```

#### Result

| Metric | Before | After |
|---|---|---|
| Lines of code | ~80 | ~40 (method) + ~45 (test) |
| Unit tests | 0 | 2 |
| Obsolete statements | 5 (CONCATENATE, READ TABLE, ADD, FORM, APPEND) | 0 |
| Type safety | Weak (global work areas, SY-SUBRC) | Strong (inline DATA, exceptions) |
| ABAP Cloud eligible | No (FORM) | Yes (class method) |

## Anti-patterns

1. **Modernizing code flagged for deletion.** If the `sap-atc-readiness` triage marked an object for removal, do not invest time rewriting it. Delete it instead. Wasted modernization effort is one of the most common project budget drains.

2. **Mass-applying abap-cleaner without per-file review.** The abap-cleaner tool is safe for most transformations, but it cannot detect dynamic call sites. For example, if code dynamically calls `CALL METHOD (lv_class_name)=>(lv_method_name)`, renaming or restructuring that method may break the caller silently. Always review changes in the interactive mode (`Ctrl+Shift+4`) before applying ([SAP/abap-cleaner README](https://github.com/SAP/abap-cleaner)).

3. **Mixing ABAP Cloud and classic ABAP in the same software component.** The ABAP language version is set at the software component level. If you assign Tier-1 (ABAP Cloud) to a component, all objects in it must comply with the restricted language scope. Do not partially modernize — either the entire component is ABAP Cloud or it is not ([SAP-samples/abap-cheat-sheets: 19_ABAP_for_Cloud_Development.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/19_ABAP_for_Cloud_Development.md)).

4. **Over-using REDUCE until the code becomes unreadable.** `REDUCE` is powerful but can produce deeply nested, hard-to-debug expressions. If a `REDUCE` expression exceeds ~5 lines or nests another `FOR`/`REDUCE` inside it, extract it into a named helper method. Clarity beats cleverness ("ABAP to the Future", Chapter 5: Constructor Expressions).

5. **Removing SY-SUBRC checks without confirming the exception path is tested.** When replacing `READ TABLE ... IF sy-subrc = 0` with a table expression, the error path changes from `SY-SUBRC <> 0` to either `CX_SY_ITAB_LINE_NOT_FOUND` or an initial structure (with `OPTIONAL`). Ensure the new error path is covered by a unit test before deploying.

6. **Replacing CALL FUNCTION with a direct class call without a wrapper.** Some BAPIs and standard function modules have side effects (e.g., buffer management, commit handling) that require the exact calling convention. Wrap them in an adapter class and write integration tests rather than blindly replacing the `CALL FUNCTION` statement.

## References

- [SAP-samples/abap-cheat-sheets](https://github.com/SAP-samples/abap-cheat-sheets) — Apache-2.0. Primary reference for modern ABAP syntax examples. Key cheat sheets: 01 (Internal Tables), 05 (Constructor Expressions), 07 (String Processing), 14 (ABAP Unit Tests), 16 (Data Types), 19 (ABAP for Cloud Development), 27 (Exceptions).
- [SAP/abap-cleaner](https://github.com/SAP/abap-cleaner) — Apache-2.0. Automated cleanup tool with 100+ rules. See [docs/rules.md](https://github.com/SAP/abap-cleaner/blob/main/docs/rules.md) for the full rule catalog.
- [SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools) — Apache-2.0. Exemption Migration Tool for Clean Core ATC checks.
- [SAP Note 2436688](https://me.sap.com/notes/2436688) — Custom Code Checks for SAP S/4HANA: defines the ATC check variant that enforces ABAP Cloud restrictions on custom code.
- [SAP Help: ABAP Keyword Documentation](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm) — Canonical reference for all ABAP statements and additions.
- [SAP Help: ABAP for Cloud Development](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/index.htm) — Restricted language scope documentation for ABAP Cloud.
- [Clean ABAP Styleguide](https://github.com/SAP/styleguides/blob/main/clean-abap/CleanABAP.md) — SAP's official style guide for modern ABAP code.
- "ABAP to the Future" (SAP Press, 3rd edition) — Chapters 2–5 cover inline declarations, constructor expressions, and modern iteration patterns.
- [SAP Note 1912445](https://me.sap.com/notes/1912445) — Recommended ABAP Test Cockpit check variants.
