---
name: sap-clean-core-extensibility
description: |
  Use when deciding how to extend SAP S/4HANA without modifying the standard core:
  choosing between in-app (key user) extensibility, side-by-side extensibility on
  SAP BTP, or developer (on-stack ABAP Cloud) extensibility; evaluating whether a
  custom BAdI, enhancement spot, or direct table modification is clean-core compliant;
  migrating ECC custom code that uses non-released APIs (ATC check findings
  CL_CI_TEST_AMDP_HDB_USAGE, USE_OF_RELEASED_API); routing a new requirement through
  the extensibility decision tree; checking API release contracts C0, C1, C2 on
  api.sap.com or in ADT; or running Clean Core ATC check variant ABAP_CLOUD_READINESS.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025"
  sources:
    - "SAP Help Portal — Extending SAP S/4HANA"
    - "SAP Help Portal — Released APIs (ABAP Cloud)"
    - "SAP Note 2570371 — Released APIs and Extension Points in SAP S/4HANA"
    - "SAP Note 2436688 — ATC checks for ABAP custom code migration"
    - "SAP/abap-atc-cr-cv-s4hc-tools (GitHub)"
    - "SAP API Business Hub (api.sap.com)"
    - "Karl Kessler — SAP Community blog series on Clean Core"
    - "SAP Custom Code Migration Guide for S/4HANA 2025 FPS01"
    - "SAP BTP CLI btp (https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-sap-btp-command-line-interface-btp-cli)"
    - "Cloud Foundry CLI cf (https://docs.cloudfoundry.org/cf-cli/)"
    - "SAP CAP cds-dk (https://cap.cloud.sap/docs/tools/cds-cli)"
    - "SAP Cloud MTA Build Tool mbt (https://sap.github.io/cloud-mta-build-tool/)"
    - "SAP Cloud SDK generator (https://sap.github.io/cloud-sdk/)"
related_skills:
  - sap-atc-readiness
  - sap-cli-toolbelt
  - sap-fiori-activation
  - sap-functional-simplifications
  - sap-hana-performance
  - sap-modern-abap-rewrite
  - sap-scoping
---

## When to use this skill

Invoke this skill when you need to:

- **Route a new requirement** to the correct S/4HANA extensibility tier (in-app, side-by-side, or developer extensibility).
- **Assess clean-core compliance** of existing ECC custom code being migrated to S/4HANA.
- **Decide in-stack vs. side-by-side** for a given extension scenario.
- **Find released APIs** on the SAP API Business Hub (`api.sap.com`), in ABAP Development Tools (ADT), or via `SE80`.
- **Interpret ATC Clean Core check results** such as findings from check variant `ABAP_CLOUD_READINESS` or the custom code migration worklist.
- **Migrate ECC enhancements** (classic BAdIs, user exits, modifications) to clean-core-compliant patterns.
- **Evaluate whether a BAdI is released** for use in ABAP Cloud development.

This skill is the architect's decision tree. It does not cover the mechanics of writing ABAP Cloud code (see `sap-modern-abap-rewrite`) or running ATC checks (see `sap-atc-readiness`).

## Prerequisites

- Access to the target S/4HANA system (2023 or later recommended for full developer extensibility support).
- ABAP Development Tools for Eclipse (ADT) installed, connected to the S/4HANA system ([SAP Help: ADT Installation](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/about-abap-development-tools)).
- Familiarity with the SAP API Business Hub at `https://api.sap.com/` for browsing released APIs and business events.
- For side-by-side scenarios: an SAP BTP subaccount with entitlements for the target services (e.g., SAP Build Work Zone, SAP Integration Suite, SAP Cloud Application Programming Model).
- The ATC check variant `ABAP_CLOUD_READINESS` configured in the system for clean-core compliance scanning ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

## Quick decision tree

Use this flowchart-as-prose to route a requirement to the correct extensibility tier.

### Step 1 — Does the standard already cover it?

Before extending, confirm the requirement is not already delivered by SAP. Check:

1. The SAP Fiori Apps Reference Library (`fioriappslibrary.hana.ondemand.com`) for standard apps ([SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)).
2. SAP Best Practices Explorer for pre-configured scope items.
3. The S/4HANA simplification list for functional changes that may have replaced the need ([SAP Note 1976487](https://me.sap.com/notes/1976487)).

If the standard covers the requirement, **stop** — no extension needed. The most common waste is building a side-by-side BTP app to do something the standard already does.

### Step 2 — Is it a simple field addition or small business rule?

**Yes** -> **Tier 1: In-App (Key User) Extensibility**

In-app extensibility is the lowest-effort option. Key users configure extensions directly in Fiori apps without developer involvement. Capabilities include:

- **Custom Fields**: add fields to standard business objects and their UIs via the *Custom Fields and Logic* app ([SAP Help: Custom Fields and Logic](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/9a281eac983f4f688d0deedc96b3c61c/95d496fad8bc4a5ebf6b6a77a9eb616d.html)).
- **Custom Logic**: attach small ABAP scripts to released BAdI spots exposed through the in-app cockpit. These execute within the ABAP language version *ABAP for Key Users* and can only reference objects released with contract **C1 — Use System-Internally** and visibility **Use in Key User Apps** ([SAP Help: Released APIs — Visibility](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis)).
- **Custom CDS Views**: create analytical views on top of released CDS entities.
- **Custom Business Objects**: lightweight data models with simple CRUD logic.

**Constraints**: no access to unreleased APIs, no complex joins across non-released tables, limited to the BAdI spots SAP has exposed for key users.

If the requirement exceeds these constraints, proceed to Step 3.

### Step 3 — Must the logic execute synchronously inside the S/4HANA transaction?

Evaluate these criteria:

| Criterion | In-Stack (Developer Extensibility) | Side-by-Side (BTP) |
|---|---|---|
| **Latency** | Synchronous, in-process. Required for validations that must fire before COMMIT WORK. | Asynchronous or near-real-time via events/APIs. Acceptable for post-save processing. |
| **Data sensitivity** | Direct access to released CDS views and ABAP APIs within the same system boundary. No data leaves the S/4HANA instance. | Data crosses the network to BTP. Requires API authentication (OAuth 2.0) and potentially data masking. |
| **Transaction integrity** | Participates in the same LUW (Logical Unit of Work). Can raise exceptions to abort the save. | Cannot abort an S/4HANA transaction. Can only react to events after the fact. |
| **Lifecycle / ownership** | Deployed within S/4HANA. Upgrade-tested alongside the core (if clean-core compliant). | Independent lifecycle on BTP. Decoupled from S/4HANA upgrade cycles. |
| **Who builds it** | ABAP developers using ADT with ABAP language version *ABAP for Cloud Development*. | Full-stack developers using CAP (Node.js/Java), SAP Build Apps, or SAPUI5. |

**If the logic MUST run synchronously before save** (e.g., a validation, pricing calculation, or data enrichment that feeds back into the transaction): -> **Tier 3: Developer Extensibility (On-Stack ABAP Cloud)**.

**If the logic can run after save or asynchronously** (e.g., a notification, approval workflow triggered by a business event, reporting dashboard, or external integration): -> **Tier 2: Side-by-Side Extensibility on SAP BTP**.

### Step 4 — Verify that released APIs exist for your scenario

Regardless of the tier chosen, the extension must only use **released** objects. An API or extension point is released when SAP has assigned it a release contract guaranteeing stability across upgrades ([SAP Note 2570371](https://me.sap.com/notes/2570371)).

**Release contracts** (from [SAP Help: Released APIs](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis)):

| Contract | Purpose | Who can use it |
|---|---|---|
| **C0 — Extend** | Stability at dedicated extension points (BAdIs, extension includes). | Developer extensibility |
| **C1 — Use System-Internally** | Stable public API for on-stack custom development in ADT or key user apps. | Developer extensibility, Key user extensibility |
| **C2 — Use as Remote API** | Stable public API for remote consumption (OData, RFC, SOAP). | Side-by-side extensibility |
| **C3 — Manage Configuration Content** | Stable persistence for configuration content. | Configuration tools |
| **C4 — Use in AMDP** | Stable API for ABAP-Managed Database Procedures. | Developer extensibility (HANA-specific logic) |

**How to find released APIs:**

1. **SAP API Business Hub** (`api.sap.com`): browse by product (S/4HANA) and filter by communication scenario or business object. This is the primary catalog for C2 (remote) APIs ([SAP API Business Hub](https://api.sap.com/)).
2. **ADT — Released Objects Browser**: in Eclipse, use *Project Explorer > Released Objects* to browse all C0/C1 objects available in the connected system.
3. **ADT — API State property view**: open any repository object and check the *API State* tab in the Properties view. The release state (`Released`, `Deprecated`, `Not Released`) and contract are displayed ([SAP Help: Released APIs](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis)).
4. **In-system via `SE80`**: for legacy navigation, use the *Released Objects* browser in SE80, though ADT is the recommended tool for ABAP Cloud development.

If no released API exists for the required data or behavior, you have three options:
- Request SAP to release the object (via SAP Influence / Customer Influence program).
- Use a **wrapper pattern**: create a released wrapper class (with C1 contract) around the unreleased object, accepting the risk that the unreleased object may change during upgrades. Document the wrapper as a technical debt item ([SAP Custom Code Migration Guide, Section "Wrapper Approach"](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)).
- Reconsider the architectural approach — perhaps the requirement can be met differently using released objects.

## Procedure

### Tier 1: In-App (Key User) Extensibility — implementation steps

1. Open the **Custom Fields and Logic** Fiori app (app ID `F1481`).
2. Navigate to the target business object (e.g., Sales Order, Purchase Order, Business Partner).
3. **Add a custom field**: define the field name, type, and label. The system generates the underlying database column, CDS view extension, and UI annotation automatically.
4. **Add custom logic**: navigate to the *Logic* tab, select a released BAdI spot (e.g., *Determination* or *Validation* on the business object), and write ABAP logic using the *ABAP for Key Users* language version. Only objects with visibility **C1 (Use in Key User Apps)** are accessible.
5. **Publish**: activate the field/logic. No transport required in SAP S/4HANA Cloud; in on-premise, a customizing transport is created automatically.
6. **Test**: verify the field appears in the UI and the logic fires correctly.

### Tier 2: Side-by-Side Extensibility on BTP — implementation steps

1. **Identify the integration pattern**:
   - *Event-driven*: S/4HANA publishes a business event (e.g., `sap.s4.beh.salesorder.changed.v1`); BTP app subscribes via SAP Event Mesh or SAP Integration Suite. Browse available events on [SAP API Business Hub — Events](https://api.sap.com/).
   - *API-driven*: BTP app calls S/4HANA OData/REST APIs (C2 contract) to read/write data.
   - *Extension via SAP Build Work Zone*: embed a custom UI tile alongside standard Fiori apps.

2. **Set up communication**: create a *Communication Arrangement* in S/4HANA linking to a *Communication Scenario* (e.g., `SAP_COM_0109` for Business Partner integration). Configure OAuth 2.0 credentials for the BTP app.

3. **Build the BTP application**: use SAP Cloud Application Programming Model (CAP) with Node.js or Java. Consume S/4HANA APIs via the SAP Cloud SDK. For canonical examples, see the [SAP-samples/cloud-cap-s4hana-side-by-side](https://github.com/SAP-samples) repositories.

4. **Deploy to BTP**: use the SAP BTP cockpit or Cloud Foundry CLI. Configure destinations pointing to the S/4HANA system.

5. **Test end-to-end**: trigger the event or API call from S/4HANA and verify the BTP app responds correctly.

### Tier 3: Developer Extensibility (On-Stack ABAP Cloud) — implementation steps

1. **Create a software component** of type *Development* in ADT with ABAP language version **ABAP for Cloud Development**. This restricts the code to using only released APIs ([SAP Help: ABAP Language Versions](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABENABAP_VERSION_GLOSRY.html)).

2. **Find the released BAdI or extension point**: use ADT's Released Objects Browser to search for BAdI definitions with contract C0. Example: BAdI `BADI_SD_SLS_DOC_VALIDATION` for sales order validation.

3. **Implement the BAdI**: create a class implementing the BAdI interface. All referenced objects must be released (C0 or C1). The ATC check variant `ABAP_CLOUD_READINESS` will flag any usage of non-released objects.

4. **Run ATC Clean Core checks**: execute ATC with the `ABAP_CLOUD_READINESS` check variant. Fix all findings before release. The check variant enforces the ABAP Cloud language version restrictions and flags direct access to non-released database tables, function modules, and classes ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

5. **Transport**: create a transport request and release. The extension is upgrade-safe because it only depends on released, contract-protected objects.

### Migrating ECC custom objects to clean-core patterns

When converting from ECC, custom objects typically fall into these categories:

| ECC pattern | Clean-core migration path |
|---|---|
| Classic BAdI (non-released) | Find the released successor BAdI (check ADT Released Objects Browser or [SAP Note 2570371](https://me.sap.com/notes/2570371)). Rewrite the implementation using ABAP for Cloud Development. |
| User exit / customer exit | Replace with released BAdI or, if no BAdI exists, use a wrapper around the unreleased object as a transitional measure. |
| Direct table modification (`MODIFY`, `INSERT` on SAP tables) | Replace with released API calls (BAPI, released class methods, or OData service). Direct DML on SAP tables is never clean-core compliant. |
| Append structures on SAP tables | Replace with custom fields via in-app extensibility (Tier 1) or released extension includes (C0 contract). |
| `SELECT` on non-released tables (e.g., `BSEG`, `VBAK` directly) | Replace with released CDS views (e.g., `I_JournalEntry`, `I_SalesDocument`). Use ADT to find the released CDS view corresponding to the legacy table. |
| RFC function module (non-released) | Replace with a released OData service (C2 contract) for remote consumption, or a released ABAP API (C1) for on-stack usage. |

Use the **Exemption Migration Tool** from `SAP/abap-atc-cr-cv-s4hc-tools` to migrate existing ATC exemptions from the legacy ABAP Cloud Readiness check to the new Clean Core checks ([SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools)).


### CLI usage

BTP-side extensibility uses several CLIs for provisioning, building, and deploying side-by-side applications.

**Environment variables**:
- `BTP_USERNAME`, `BTP_PASSWORD`, `BTP_SUBDOMAIN` (for btp CLI)
- `CF_API_ENDPOINT`, `CF_ORG`, `CF_SPACE` (for cf CLI)

**Network prerequisites**: `cli.btp.cloud.sap:443`, BTP CF API endpoint:443.

```bash
# Authenticate to BTP and target the subaccount
btp login --url https://cli.btp.cloud.sap --subdomain "${BTP_SUBDOMAIN}" \
  --user "${BTP_USERNAME}" --password "${BTP_PASSWORD}"

# Authenticate to Cloud Foundry
cf login -a "${CF_API_ENDPOINT}" -u "${BTP_USERNAME}" -p "${BTP_PASSWORD}" \
  -o "${CF_ORG}" -s "${CF_SPACE}"

# Initialize a new CAP project for a side-by-side extension
cds init my-s4-extension --add hana,approuter

# Import an S/4HANA OData service for consumption
cds import ./API_BUSINESS_PARTNER.edmx --as external-service

# Generate a typed OData client from EDMX metadata
generate-odata-client --inputDir ./edmx --outputDir ./generated

# Build an MTA archive for deployment
mbt build -t ./dist

# Deploy the MTA archive to Cloud Foundry
cf deploy ./dist/my-s4-extension_1.0.0.mtar
```

These CLIs cover the full lifecycle of a side-by-side BTP extension: scaffold → import → build → deploy ([btp CLI docs](https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-sap-btp-command-line-interface-btp-cli), [CAP docs](https://cap.cloud.sap/docs/tools/cds-cli), [Cloud SDK](https://sap.github.io/cloud-sdk/)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

### Requirement: custom approval workflow on a sales order

A business requires that sales orders exceeding a credit limit threshold trigger an additional approval step. The approval must check the customer's credit master data and, if the order value exceeds the available credit, block the order before save until a manager approves.

**Walking the decision tree:**

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

**Implementation sketch (ABAP for Cloud Development):**

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

**Counter-example — the same requirement but post-save notification:**
If the business only needs a *notification* after save (not a blocking check), the clean-core answer is **Tier 2: Side-by-Side on BTP**:

1. S/4HANA publishes business event `sap.s4.beh.salesorder.created.v1` when a sales order is saved.
2. A CAP application on BTP subscribes to this event via SAP Event Mesh.
3. The CAP app calls the S/4HANA OData API `API_CREDIT_MANAGEMENT_SRV` (C2 contract) to read credit data.
4. If the threshold is exceeded, the app sends a notification to the approver via SAP Build Work Zone or email.

This keeps the S/4HANA core untouched and decouples the notification lifecycle from the S/4HANA upgrade cycle.

## Anti-patterns

### 1. "We've always done it in ABAP, so we'll do it in ABAP again"

Defaulting to developer extensibility (Tier 3) without evaluating whether in-app extensibility (Tier 1) or standard functionality suffices. Many field additions and simple validations can be handled entirely by key users in the Custom Fields and Logic app, with zero ABAP development. Always start at Tier 1 and escalate only when constraints are hit ([SAP Help: Custom Fields and Logic](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/9a281eac983f4f688d0deedc96b3c61c/95d496fad8bc4a5ebf6b6a77a9eb616d.html)).

### 2. Direct database access to non-released tables

Writing `SELECT * FROM BSEG` or `MODIFY VBAK` in custom code. This instantly violates clean core and will be flagged by the `ABAP_CLOUD_READINESS` ATC check variant. In S/4HANA, `BSEG` is a compatibility view over the Universal Journal (`ACDOCA`); direct access is both a clean-core violation and a performance anti-pattern. Use the released CDS view `I_JournalEntry` instead ([SAP Note 2270407](https://me.sap.com/notes/2270407)).

### 3. Building a side-by-side BTP app for something the standard already does

The most common source of waste in S/4HANA projects. Before building any extension, exhaustively check the SAP Fiori Apps Reference Library and the SAP Best Practices Explorer. Many approval workflows, reporting dashboards, and integration scenarios are already delivered as standard Fiori apps with configuration options ([SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)).

### 4. Treating all BAdIs as clean-core compliant

Only BAdIs with a release contract (C0) are clean-core compliant. Many classic BAdIs from ECC exist in S/4HANA but are **not released** — using them ties your code to internal SAP objects that can change without notice during upgrades. Always verify the API state in ADT before implementing a BAdI. If the BAdI is not released, check whether a released successor exists ([SAP Note 2570371](https://me.sap.com/notes/2570371)).

### 5. Using side-by-side for synchronous, transaction-critical logic

Placing validation or pricing logic in a BTP app that S/4HANA must call synchronously before save introduces network latency, a hard dependency on BTP availability, and an inability to participate in the S/4HANA LUW. If the logic must run inline before COMMIT WORK, it belongs on-stack (Tier 3) ([SAP Help: Extending SAP S/4HANA](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)).

### 6. Skipping ATC Clean Core checks before transport

Releasing custom code without running the `ABAP_CLOUD_READINESS` check variant. Even if code compiles and runs, it may reference non-released objects that will break during future upgrades. Run ATC before every transport release. Use the Exemption Migration Tool from `SAP/abap-atc-cr-cv-s4hc-tools` to properly manage exemptions rather than suppressing findings ([SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools)).

## References

1. [SAP Help: Released APIs (ABAP Cloud)](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis) — Canonical documentation on release contracts C0, C1, C2, C3, C4, release states, and visibility settings.
2. [SAP Note 2570371 — Released APIs and Extension Points in SAP S/4HANA](https://me.sap.com/notes/2570371) — Master note listing released APIs and extension points by business area.
3. [SAP Note 2436688 — ATC checks for ABAP custom code migration](https://me.sap.com/notes/2436688) — Configuration of the `ABAP_CLOUD_READINESS` check variant.
4. [SAP Note 1976487 — S/4HANA Simplification List](https://me.sap.com/notes/1976487) — Functional simplifications that may eliminate the need for extensions.
5. [SAP Note 2270407 — Universal Journal in S/4HANA](https://me.sap.com/notes/2270407) — Why direct `BSEG` access is invalid; use `I_JournalEntry` CDS view.
6. [SAP API Business Hub](https://api.sap.com/) — Browse and test released S/4HANA APIs (OData, SOAP, events) with C2 contracts.
7. [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/) — Check whether standard apps already cover a requirement before building extensions.
8. [SAP/abap-atc-cr-cv-s4hc-tools (GitHub)](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools) — Exemption Migration Tool for clean core ATC checks. Apache-2.0 license.
9. [SAP Help: Custom Fields and Logic](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/9a281eac983f4f688d0deedc96b3c61c/95d496fad8bc4a5ebf6b6a77a9eb616d.html) — In-app extensibility guide for key users.
10. [SAP Help: ABAP Language Versions](https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/ABENABAP_VERSION_GLOSRY.html) — Differences between Standard ABAP, ABAP for Cloud Development, and ABAP for Key Users.
11. [SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE) — Canonical runbook for custom code migration, including the wrapper approach for non-released APIs.
12. Karl Kessler — SAP Community blog series on Clean Core extensibility (2023-2024). Overview of the three-tier extensibility model and clean core principles.
