# Worked Example: Modernizing `Z_BUILD_INVOICE_LIST`

> **Sources**: [SAP-samples/abap-cheat-sheets](https://github.com/SAP-samples/abap-cheat-sheets) (Apache-2.0),
> [SAP/abap-cleaner](https://github.com/SAP/abap-cleaner) (Apache-2.0).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Context](#context)
- [Original code (80 lines, FORM-based)](#original-code-80-lines-form-based)
- [Step 1 — Extract to class method](#step-1--extract-to-class-method)
- [Step 2 — Replace READ TABLE with table expression](#step-2--replace-read-table-with-table-expression)
- [Step 3 — Build result with VALUE FOR](#step-3--build-result-with-value-for)
- [Step 4 — Replace CONCATENATE with string templates](#step-4--replace-concatenate-with-string-templates)
- [Step 5 — Compute total with REDUCE](#step-5--compute-total-with-reduce)
- [Step 6 — Add ABAP Unit tests](#step-6--add-abap-unit-tests)
- [Result](#result)

## Context

After S/4HANA conversion, ATC confirmed that program `Z_INVOICE_REPORT` and its form routine `BUILD_INVOICE_LIST` are actively used and must be retained. The code is 4.6C-era ABAP.

## Original code (80 lines, FORM-based)

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

## Step 1 — Extract to class method

Create class `ZCL_INVOICE_BUILDER` with a static method. Replace `USING`/`CHANGING` with `IMPORTING`/`RETURNING`. Move the customer lookup into a constructor-injected dependency for testability.

## Step 2 — Replace READ TABLE with table expression

```abap
" Before
READ TABLE it_customers WITH KEY customer_id = ls_order-customer_id
  INTO ls_customer.
IF sy-subrc = 0.

" After
DATA(ls_customer) = VALUE #( it_customers[ customer_id = ls_order-customer_id ] OPTIONAL ).
IF ls_customer IS NOT INITIAL.
```

## Step 3 — Build result with VALUE FOR

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

This uses `FOR` iteration, `LET` for intermediate values, `COND` for conditional assignment, and string templates — all in a single expression ([SAP-samples/abap-cheat-sheets: 05_Constructor_Expressions.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/a79310222d643d9a053a76bae3712e726fb6a880/05_Constructor_Expressions.md)).

## Step 4 — Replace CONCATENATE with string templates

Already done above: `|INV-{ ls_ord-order_id }|` and `|{ ls_cust-first_name } { ls_cust-last_name }|`.

## Step 5 — Compute total with REDUCE

```abap
DATA(lv_total) = REDUCE decfloat34(
  INIT sum = CONV decfloat34( 0 )
  FOR ls_inv IN rt_invoices
  NEXT sum = sum + ls_inv-gross_amount ).
```

## Step 6 — Add ABAP Unit tests

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

## Result

| Metric | Before | After |
|---|---|---|
| Lines of code | ~80 | ~40 (method) + ~45 (test) |
| Unit tests | 0 | 2 |
| Obsolete statements | 5 (CONCATENATE, READ TABLE, ADD, FORM, APPEND) | 0 |
| Type safety | Weak (global work areas, SY-SUBRC) | Strong (inline DATA, exceptions) |
| ABAP Cloud eligible | No (FORM) | Yes (class method) |
