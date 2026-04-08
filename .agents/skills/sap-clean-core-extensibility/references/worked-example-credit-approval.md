# Worked Example: Clean Core Credit Approval Workflow on Sales Order

> **Sources**: [SAP Help: Released APIs (ABAP Cloud)](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis),
> [SAP Note 2570371](https://me.sap.com/notes/2570371) — Released APIs and Extension Points.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Requirement](#requirement)
- [Walking the decision tree](#walking-the-decision-tree)
- [Implementation sketch (ABAP for Cloud Development)](#implementation-sketch-abap-for-cloud-development)
- [Counter-example — post-save notification via BTP](#counter-example--post-save-notification-via-btp)

## Requirement

A business requires that sales orders exceeding a credit limit threshold trigger an additional approval step. The approval must check the customer's credit master data and, if the order value exceeds the available credit, block the order before save until a manager approves.

## Walking the decision tree

**Step 1 — Does the standard cover it?**
S/4HANA includes standard credit management (transaction `UKM_CASE`), but the business wants a custom approval rule that joins credit master data with customer-specific risk categories not covered by the standard. Standard credit management does not support this join. Proceed to extension.

**Step 2 — Is it a simple field addition or small business rule?**
No. The logic requires reading from credit master data (table `UKM_ACCOUNT` / CDS view `I_CreditAccountManagement`), performing a multi-row calculation, and blocking the document. This exceeds in-app extensibility capabilities. Proceed to Step 3.

**Step 3 — Must the logic execute synchronously?**
Yes. The approval must fire **before save** — if the credit check fails, the sales order must not be posted. The validation must participate in the same LUW. This rules out side-by-side (Tier 2). -> **Tier 3: Developer Extensibility**.

**Step 4 — Verify released APIs exist.**
- BAdI: `BADI_SD_SLS_DOC_VALIDATION` (released, C0 contract) — fires during sales order validation.
- CDS view: `I_SalesDocument` (released, C1) — for reading order header data.
- CDS view: `I_CreditAccountManagement` (released, C1) — for reading credit master data.
- All required objects are released. Proceed with implementation.

## Implementation sketch (ABAP for Cloud Development)

```abap
CLASS zcl_sd_credit_approval DEFINITION
  PUBLIC FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_badi_sd_sls_doc_validation.
ENDCLASS.

CLASS zcl_sd_credit_approval IMPLEMENTATION.
  METHOD if_badi_sd_sls_doc_validation~validate.
    " Read sales order net value from importing parameter
    DATA(lv_net_value) = is_sales_document-net_value.
    DATA(lv_sold_to) = is_sales_document-sold_to_party.

    " Read credit master via released CDS view
    SELECT SINGLE credit_limit, credit_exposure
      FROM i_creditaccountmanagement
      WHERE businesspartner = @lv_sold_to
      INTO @DATA(ls_credit).

    IF sy-subrc = 0.
      DATA(lv_available) = ls_credit-credit_limit - ls_credit-credit_exposure.
      IF lv_net_value > lv_available.
        " Block the order — raise a validation message
        APPEND VALUE #(
          msgty = 'E'
          msgid = 'ZSD_CREDIT'
          msgno = '001'
          msgv1 = |{ lv_net_value DECIMALS = 2 }|
          msgv2 = |{ lv_available DECIMALS = 2 }|
        ) TO ct_messages.
      ENDIF.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

## Counter-example — post-save notification via BTP

If the business only needs a *notification* after save (not a blocking check), the clean-core answer is **Tier 2: Side-by-Side on BTP**:

1. S/4HANA publishes business event `sap.s4.beh.salesorder.created.v1` when a sales order is saved.
2. A CAP application on BTP subscribes to this event via SAP Event Mesh.
3. The CAP app calls the S/4HANA OData API `API_CREDIT_MANAGEMENT_SRV` (C2 contract) to read credit data.
4. If the threshold is exceeded, the app sends a notification to the approver via SAP Build Work Zone or email.

This keeps the S/4HANA core untouched and decouples the notification lifecycle from the S/4HANA upgrade cycle.
