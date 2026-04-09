# Worked Example: Migrating 1,000 Customer Master Records

> **Sources**: [SAP Help: Migrate Your Data - Migration Cockpit](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/2f0dbe4111214bcf9b2d57eca26f0525.html),
> [SAP Note 2265093](https://me.sap.com/notes/2265093) — S/4HANA Business Partner Approach.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Create the migration project](#step-1--create-the-migration-project)
- [Step 2 — Download and fill the XML template](#step-2--download-and-fill-the-xml-template)
- [Step 3 — Upload and simulate](#step-3--upload-and-simulate)
- [Step 4 — Fix and re-simulate](#step-4--fix-and-re-simulate)
- [Step 5 — Execute](#step-5--execute)
- [Step 6 — Verify](#step-6--verify)

## Scenario

Migrate 1,000 customer master records from a legacy CSV file into a new S/4HANA system. Customers must be created as Business Partners with customer role (BP role `FLCU00`).

## Step 1 — Create the migration project

Open the **Migrate Your Data** Fiori app. Choose **Create** → **Migrate Data Using Staging Tables**.

- **Project name**: `MIG_CUSTOMERS`
- **Scenario**: SAP ERP to SAP S/4HANA
- **Staging tables**: Not used (simple file upload)
- **Migration object selected**: `Customer (with Business Partner)`

> The `Customer (with Business Partner)` object creates both a BP record and the linked customer record in one step, including CVI synchronization ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

## Step 2 — Download and fill the XML template

Download the XML template for `Customer (with Business Partner)`. The template contains multiple sections:

| Section | Key Fields |
|---------|-----------|
| Header | `BP_NUMBER`, `BP_CATEGORY`, `BP_GROUP`, `TITLE`, `NAME1`, `NAME2` |
| Address | `STREET`, `CITY`, `POSTAL_CODE`, `COUNTRY`, `REGION` |
| Customer General | `CUSTOMER_NUMBER`, `ACCOUNT_GROUP` |
| Company Code | `COMPANY_CODE`, `RECON_ACCOUNT`, `PAYMENT_TERMS` |
| Sales Area | `SALES_ORG`, `DIST_CHANNEL`, `DIVISION`, `CUST_PRICING_PROC` |

Map 1,000 rows from the legacy CSV into the template. Assign BP role `FLCU00` (Customer) to each record. Set `BP_CATEGORY` = `2` (Organization) for corporate customers, `1` (Person) for individuals.

## Step 3 — Upload and simulate

Upload the filled XML template in the cockpit. Choose **Simulate**.

**Result**: 23 errors out of 1,000 records:
- 12 rows: `Country code 'XX' does not exist` → Fix: correct invalid country codes in the source CSV.
- 11 rows: `Tax classification is mandatory for sales area data` → Fix: populate `TAX_CLASSIFICATION` field.

## Step 4 — Fix and re-simulate

Correct the 23 records in the CSV, regenerate the XML template, re-upload, and simulate again.

**Result**: 0 errors, 1,000 records ready for migration.

## Step 5 — Execute

Choose **Execute**. The cockpit creates 1,000 Business Partner records with linked Customer records. Monitor the migration project screen until status shows **Completed**.

## Step 6 — Verify

- Open transaction `BP`, search for the migrated BP number range → confirm 1,000 BP records exist with role `FLCU00`.
- Open `FD03` (Customer Display) → verify company code data, reconciliation accounts, and payment terms.
- Run a test sales order (`VA01`) against a migrated customer to confirm sales area data is complete.
