# Worked Example: Simplification Database — Business Partner Remediation Worklist

> **Sources**: [SAP Note 2265093](https://me.sap.com/notes/2265093) — S/4HANA Business Partner Approach,
> [SAP Note 2241080](https://me.sap.com/notes/2241080) — Simplification Database Content,
> [SAP Note 2436688](https://me.sap.com/notes/2436688) — ATC checks for custom code migration.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Search the Simplification Item Catalog](#step-1--search-the-simplification-item-catalog)
- [Step 2 — Confirm in the Simplification Database](#step-2--confirm-in-the-simplification-database)
- [Step 3 — Filter the ATC worklist](#step-3--filter-the-atc-worklist)
- [Step 4 — Open the remediation SAP Note](#step-4--open-the-remediation-sap-note)
- [Step 5 — Hand off to developers](#step-5--hand-off-to-developers)

## Scenario

A customer is converting from SAP ECC 6.0 EHP 8 to SAP S/4HANA 2025 On-Premise. The `sap-atc-readiness` skill has produced a worklist with 47 findings in message class `S4HANA_READINESS`. Several findings reference tables `KNA1` and `LFA1`. The project team needs to understand the simplification context and plan remediation.

## Step 1 — Search the Simplification Item Catalog

Open `https://launchpad.support.sap.com/#/sic` and search for `Business Partner`.

The catalog returns the item **"Customer/Vendor Integration"** (also known as the Business Partner approach). Key details:

| Field | Value |
|---|---|
| Title | Customer/Vendor Integration |
| Category | Data Model |
| Target Release | S/4HANA 1610+ (applies to all subsequent releases) |
| Deployment Model | On-Premise, Cloud Private Edition, Cloud Public Edition |
| Linked SAP Note | [2265093](https://me.sap.com/notes/2265093) |

The description explains that customer master data (table `KNA1`) and vendor master data (table `LFA1`) are replaced by the Business Partner model (table `BUT000`). Custom code that reads from or writes to `KNA1` / `LFA1` directly must be refactored to use `BUT000` or the corresponding CDS views (`I_Customer`, `I_Supplier`, `I_BusinessPartner`) ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

## Step 2 — Confirm in the Simplification Database

On the central ATC check system, verify the Simplification Database is loaded and current:

```
Transaction: SYCM
Menu: Simplification Database → Display
Expected: Version 2025_FPS01_xxxx (latest patch)
```

If the version is outdated, re-import from [SAP Note 2241080](https://me.sap.com/notes/2241080).

## Step 3 — Filter the ATC worklist

In the ATC results for check variant `S4HANA_READINESS`, filter findings by the affected objects:

```abap
* Example ATC finding:
* Check:    S4HANA_READINESS_SIMPL
* Object:   Z_CUSTOMER_REPORT (Program)
* Message:  Access to table KNA1 — replaced by Business Partner
*           model (BUT000). See SAP Note 2265093.
* Priority: Error (must fix before conversion)
```

From the 47 total findings, 12 reference `KNA1` or `LFA1`. These 12 custom objects form the **Business Partner remediation worklist**.

## Step 4 — Open the remediation SAP Note

[SAP Note 2265093](https://me.sap.com/notes/2265093) describes:

- The synchronization mechanism between `KNA1`/`LFA1` and `BUT000` during and after conversion.
- Which BAPI calls (`BAPI_CUSTOMER_GETDETAIL`, `BAPI_VENDOR_GETDETAIL`) are replaced and by what.
- The CDS views available as stable interfaces: `I_Customer`, `I_Supplier`, `I_BusinessPartner`.
- The Business Partner configuration guide and the Customer/Vendor Integration (CVI) error-resolution process.

## Step 5 — Hand off to developers

Prepare a remediation ticket for each affected object:

```
Object:          Z_CUSTOMER_REPORT
Type:            Program
Simplification:  Customer/Vendor Integration (Business Partner)
SAP Note:        2265093
Action required: Replace SELECT FROM KNA1 with CDS view I_Customer
                 or table BUT000. Replace BAPI_CUSTOMER_GETDETAIL
                 with CDS-based read. Test with BP transaction.
Priority:        Must-fix (blocks conversion)
```

Repeat for each of the 12 objects. Hand the worklist to the development team with the simplification context attached so they can plan sprints.
