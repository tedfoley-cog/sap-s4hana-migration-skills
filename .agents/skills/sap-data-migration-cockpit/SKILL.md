---
name: sap-data-migration-cockpit
description: |
  Use when migrating business data into SAP S/4HANA using the Migration Cockpit:
  loading master data or transactional data via the Migrate Your Data Fiori app (F3473),
  working with transaction LTMC (deprecated) or LTMOM for custom migration objects,
  creating file-based or staging-table migration projects, troubleshooting migration
  errors such as "No migration objects available" or "RFC connection failed",
  selecting and mapping migration objects for Business Partner, Material, Customer,
  Vendor, GL Account, Cost Center, Sales Order, or Purchase Order migration,
  or deciding between greenfield file-upload and brownfield direct-transfer approaches.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "SAP Help Portal: Data Migration (S/4HANA On-Premise 2025 FPS01)"
    - "SAP Note 2546430 - S/4HANA Migration Cockpit Central Note"
    - "SAP Note 2733253 - Migration Cockpit Fiori App"
    - "SAP Note 3043614 - System Settings for Migration Projects"
    - "SAP Fiori Apps Reference Library: Migrate Your Data (F3473)"
    - "SAP Community blog by Iliana Olvera: Part 1 Migrate your Data - Migration Cockpit (March 2021)"
    - "SAP Community blog by Mickael Quesnot: Tutorial — Using the SAP S/4HANA Migration Cockpit App (February 2025)"
    - "SAP-samples/s4hana-mc-xml-file-splitter (GitHub)"
    - "openSAP course: Data Migration to SAP S/4HANA"
    - "SAP CAP cds-dk (https://cap.cloud.sap/docs/tools/cds-cli)"
    - "SAP HANA Client hdbsql (https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)"
related_skills:
  - sap-cli-toolbelt
  - sap-functional-simplifications
  - sap-migration-testing
---

## When to use this skill

Invoke this skill when the task involves any of the following:

- **Greenfield data load**: A new S/4HANA system has been installed and business data (customers, vendors, materials, GL accounts, cost centers, etc.) must be loaded from legacy flat files or spreadsheets.
- **Brownfield data consolidation**: During an ECC-to-S/4HANA system conversion, some master data needs to be re-loaded, merged, or consolidated — for example, converting separate Customer/Vendor master records into Business Partner records.
- **Choosing a migration approach**: The project team needs to decide between **file-based (XML/staging tables)** and **direct transfer from SAP source system** approaches.
- **Migration Cockpit tooling questions**: Any question about transactions `LTMC` (deprecated), `LTMOM`, or the **Migrate Your Data** Fiori app (App ID `F3473`).
- **Custom migration objects**: The standard migration object catalog does not cover a specific data entity and a custom object must be created in `LTMOM`.
- **Migration error triage**: Errors during simulate or execute runs — missing customizing, mandatory field violations, RFC connection failures, or object-level conversion errors.

This skill is **not** for SUM/DMO technical conversion (see `sap-sum-dmo`) or for post-migration functional testing (see `sap-migration-testing`).

## Prerequisites

1. **SAP S/4HANA system** at release 2020 or later (the Fiori-based Migration Cockpit replaces `LTMC` from release 2020 onward) ([SAP Note 2733253](https://me.sap.com/notes/2733253)).
2. **Fiori Launchpad** configured with the **Migrate Your Data** app tile (Fiori App ID `F3473`) ([SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/sap/fix/externalViewer/?appId=F3473)).
3. **Authorization role** `SAP_CA_DMC_MC_USER` assigned to the migration user in the target S/4HANA system ([SAP Help: Roles and Authorizations](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/dabe2e6948b24e33a6e4dfa2bb4ed1a3.html)).
4. For **direct transfer from SAP system**: an RFC connection from the S/4HANA system to the source ECC system, with appropriate authorizations on both sides.
5. For **staging tables**: a remote SAP HANA schema connection configured in the S/4HANA system (see "Before You Start" in the SAP Help Portal) ([SAP Help: Before You Start](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/94f7b5a36db64633a4d49623f66e04c7.html)).
6. Migration projects can only be created in systems with specific settings (typically development systems, not productive or quality systems) ([SAP Note 3043614](https://me.sap.com/notes/3043614)).
7. **Business Partner** customizing must be complete before migrating customer/vendor data — BP number ranges, BP roles, and the Customer/Vendor Integration (CVI) synchronization must be configured ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

## Quick decision tree

```
Is this a greenfield (new) S/4HANA installation?
├─ YES
│   Is legacy data in a non-SAP system or flat files?
│   ├─ YES → Use "Migrate Data Using Staging Tables" (file/XML upload)
│   └─ NO (data is in an SAP ECC system)
│       → Use "Migrate Data Directly from SAP System" (RFC-based)
└─ NO (brownfield conversion / system already has data)
    Do you need to re-load or consolidate specific master data?
    ├─ YES
    │   Is the source an SAP system with RFC connectivity?
    │   ├─ YES → Use "Migrate Data Directly from SAP System"
    │   └─ NO → Use "Migrate Data Using Staging Tables"
    └─ NO → Data migration cockpit is not needed;
            data converts in place during SUM/DMO (see sap-sum-dmo)
```

**Key factors for choosing the approach:**

| Factor | Staging Tables (File/XML) | Direct Transfer (RFC) |
|--------|--------------------------|----------------------|
| Source system | Any (SAP or non-SAP) | SAP ECC only |
| Data format | XML templates downloaded from the cockpit | Automatic selection via RFC |
| Field mapping | Manual (fill XML template columns) | Semi-automatic (mapping UI) |
| Best for | Non-SAP legacy, spreadsheet data, small volumes | Large-volume SAP-to-SAP migration |
| Offline work | Yes (prepare XML offline) | No (online connection required) |

([SAP Help: Migrate Your Data - Migration Cockpit](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/2f0dbe4111214bcf9b2d57eca26f0525.html))

## Procedure

### Step 1: Understand the tooling landscape

The Migration Cockpit tooling has evolved across S/4HANA releases:

| Tool | Transaction / App | Status | Notes |
|------|------------------|--------|-------|
| Migration Cockpit (legacy) | `LTMC` | **Deprecated** from S/4HANA 2020 | Read-only access to old projects remains ([SAP Note 2733253](https://me.sap.com/notes/2733253)) |
| Migrate Your Data (Fiori) | App ID `F3473` | **Current** | Replaces LTMC; access via Fiori Launchpad ([SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/sap/fix/externalViewer/?appId=F3473)) |
| Migration Object Modeler | `LTMOM` | **Current** | For customizing/extending migration objects ([SAP Help: Migration Object Modeler](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/3732aa6c1acf4184812f0db7beb8e037.html)) |

> **Important**: If the target system is S/4HANA 2022 or later, `LTMC` can no longer be used to create new migration projects. Use the Migrate Your Data Fiori app exclusively ([SAP Note 2733253](https://me.sap.com/notes/2733253)).

### Step 2: Discover available migration objects

Before creating a project, review the **migration object catalog** to confirm that standard objects exist for your data entities.

- Access the catalog via **Explore Migration Objects** in the Data Migration section of SAP Help Portal ([SAP Help: Available Migration Objects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/8dd142b479f9481891fa8b3f86648df3.html)).
- Common standard objects include:

| Migration Object | Typical Use |
|-----------------|-------------|
| Business Partner (with Customer) | Customer master + BP integration |
| Business Partner (with Vendor) | Vendor master + BP integration |
| Material | Material master (all views) |
| G/L Account | General Ledger accounts |
| Cost Center | Controlling master data |
| Profit Center | Controlling master data |
| Sales Order | Open sales orders |
| Purchase Order | Open purchase orders |
| Fixed Asset | Asset master and balances |

- Objects are scenario-specific. When creating a project, the cockpit filters available objects by the selected migration scenario (e.g., "SAP ERP to SAP S/4HANA", "SAP CRM to SAP S/4HANA for Customer Management") ([SAP Help: Creating Migration Projects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/75be3f04d79d4bbc9727a234fce513b5.html)).

### Step 3: Create a migration project

1. Open the **Migrate Your Data** app from Fiori Launchpad.
2. Choose **Create** and select the migration approach:
   - **Migrate Data Directly from SAP System** — for RFC-based transfer from an SAP source system.
   - **Migrate Data Using Staging Tables** — for file/XML upload from any source.
3. Specify **General Data**:
   - **Project name** (e.g., `MIG_CUSTOMERS_WAVE1`).
   - **Migration scenario** (e.g., "SAP ERP to SAP S/4HANA").
   - **RFC connection** to source system (for direct transfer only).
4. Specify **organizational units** (e.g., company codes) that scope the data selection.
5. Optionally enable **staging tables** as intermediate storage (requires a remote HANA schema connection).
6. Select the relevant **migration objects** from the catalog.
7. Review settings and choose **Create Project**.

([SAP Help: Creating Migration Projects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/75be3f04d79d4bbc9727a234fce513b5.html))

> **Note**: If you need to migrate data from a different source system or client, you must create a new migration project or copy an existing one. Simply changing the RFC connection is not sufficient, because the cockpit creates ABAP dictionary and repository objects in the source system during project creation ([SAP Help: Creating Migration Projects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/75be3f04d79d4bbc9727a234fce513b5.html)).

### Step 4: Prepare data (staging tables / file approach)

For the **staging tables** approach:
1. Download the **XML template** for each selected migration object from the cockpit.
2. Fill in the template with legacy data. Each template contains multiple sheets/sections corresponding to the migration object's structures (header, items, addresses, etc.).
3. For large XML files, consider splitting them using the **SAP S/4HANA Migration Cockpit XML File Splitter** tool ([SAP-samples/s4hana-mc-xml-file-splitter](https://github.com/SAP-samples/s4hana-mc-xml-file-splitter)).
4. Upload the filled template back into the cockpit.

For the **direct transfer** approach:
1. The cockpit automatically selects data from the source system via RFC based on the organizational units specified in the project.
2. Review the selected data in the cockpit before proceeding ([SAP Help: Selecting Data from the Source System](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/625552df9dca47d58e0deaf5085b86c3.html)).

### Step 5: Configure field mapping and value mapping

- Open **Mapping Tasks** for each migration object in the cockpit.
- Map source fields to target fields. The cockpit provides a mapping UI with:
  - **Auto-mapping** for fields with matching names.
  - **Value mapping rules** for translating source values to target values (e.g., old company code → new company code).
  - **Fixed values** for fields that should receive a constant across all records.
  - **Lookups** against existing master data in the target system.
- Download and re-upload mapping values when iterating across test cycles to avoid re-entering them ([SAP Help: Mapping Tasks](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/44615b12b7954556993aac54637d65b6.html)).

### Step 6: Simulate the migration

1. Choose **Simulate** for each migration object.
2. The simulation runs the full migration logic **without committing data** to the database.
3. Review simulation results:
   - **Success count**: Records that would migrate cleanly.
   - **Error count**: Records with issues — download the error log for details.
   - Common error patterns:
     - Missing customizing entries (e.g., undefined country codes, tax categories).
     - Mandatory fields not populated in the source data.
     - Number range exhaustion.
     - Duplicate key violations (record already exists in target).
4. Fix source data or customizing, re-upload, and re-simulate until the error count reaches zero or an acceptable threshold.

([SAP Help: Simulating the Migration](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/0ee46d72aa734da6ba5d9285da4d7148.html))

> **Always simulate before executing.** Simulation is the cheapest feedback loop for identifying data quality issues. Skipping it leads to failed production loads and costly rollback efforts.

### Step 7: Execute the migration

1. Once simulation is clean, choose **Execute** (also called **Migrate**).
2. The cockpit creates the business objects in the target S/4HANA system using standard SAP APIs (BAPIs / business object processing).
3. Monitor progress in the **Migration Project Screen** — the cockpit shows object-level status (Completed, Errors, In Progress) ([SAP Help: The Migration Project Screen](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/4c7665f43a3644de8d354fbd9d277ae5.html)).
4. Review the **Transfer List** and **Migration Results** for detailed per-record outcomes ([SAP Help: Viewing the Migration Results](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/d2b04ea19dec4c4b9e0617b8f99912c0.html)).
5. Download error logs for any failed records, fix source data, and re-run for the failed subset.

### Step 8: Create custom migration objects (if needed)

When the standard catalog does not cover your data entity:

1. Open transaction `LTMOM` (Migration Object Modeler).
2. **Copy an existing standard object** as a starting point (recommended over creating from scratch).
3. Add or remove fields, adjust mappings, and configure staging table structures.
4. Activate the custom object — it will appear in the migration object selection when creating or editing a project.
5. Transport the custom object to test and production systems alongside the migration project ([SAP Help: SAP S/4HANA Migration Object Modeler](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/3732aa6c1acf4184812f0db7beb8e037.html)).

> Custom migration objects created in `LTMOM` must be transported separately. If you modify an object after the initial transport, re-transport it before the next test cycle ([SAP Help: Transporting Migration Objects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/898c9def31544ce487a034d9d7bdd87c.html)).

### Step 9: Verify migrated data

After execution completes:
1. Spot-check migrated records using the relevant transactions (e.g., `BP` for Business Partners, `MM03` for Materials, `XD03`/`XK03` for legacy customer/vendor views).
2. Run end-to-end business process tests against the migrated data (see `sap-migration-testing`).
3. Verify record counts match between source and target.
4. Check that dependent data relationships are intact (e.g., BP ↔ Customer/Vendor linkage via CVI).


### CLI usage

Use `cds` for BTP-side ETL extensions that feed the Migration Cockpit, and `hdbsql` for target-side data validation.

**Environment variables**:
- `HANA_HOST`, `HANA_USER`, `HANA_PASSWORD` (for hdbsql)

**Network prerequisites**: HANA port 443 (Cloud) or 3\<sysnr\>15 (on-prem).

```bash
# Initialize a CAP project for a migration data transformation service
cds init migration-etl --add hana

# Define a CDS entity for staging migration data
cat > db/schema.cds << 'EOF'
namespace migration;
entity StagedCustomers {
  key ID         : UUID;
      legacyID   : String(10);
      name       : String(80);
      country    : String(3);
      bpCategory : String(1);  // 1=Org, 2=Person
}
EOF

# Deploy the staging model to HANA
cds deploy --to hana

# After migration execution, validate record counts on the target
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT COUNT(*) AS bp_count FROM BUT000 WHERE BU_GROUP = 'Z001'"

# Spot-check CVI linkage integrity
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT COUNT(*) AS linked FROM CVI_CUST_LINK"
```

The CAP-based ETL approach lets Devin build transformation logic that feeds XML templates to the Migration Cockpit, while `hdbsql` queries validate that migrated data landed correctly ([CAP docs](https://cap.cloud.sap/docs/tools/cds-cli), [SAP Help: hdbsql](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

**Scenario**: Migrate 1,000 customer master records from a legacy CSV file into a new S/4HANA system. Customers must be created as Business Partners with customer role (BP role `FLCU00`).

### 1. Create the migration project

Open the **Migrate Your Data** Fiori app. Choose **Create** → **Migrate Data Using Staging Tables**.

- **Project name**: `MIG_CUSTOMERS`
- **Scenario**: SAP ERP to SAP S/4HANA
- **Staging tables**: Not used (simple file upload)
- **Migration object selected**: `Customer (with Business Partner)`

> The `Customer (with Business Partner)` object creates both a BP record and the linked customer record in one step, including CVI synchronization ([SAP Note 2265093](https://me.sap.com/notes/2265093)).

### 2. Download and fill the XML template

Download the XML template for `Customer (with Business Partner)`. The template contains multiple sections:

| Section | Key Fields |
|---------|-----------|
| Header | `BP_NUMBER`, `BP_CATEGORY`, `BP_GROUP`, `TITLE`, `NAME1`, `NAME2` |
| Address | `STREET`, `CITY`, `POSTAL_CODE`, `COUNTRY`, `REGION` |
| Customer General | `CUSTOMER_NUMBER`, `ACCOUNT_GROUP` |
| Company Code | `COMPANY_CODE`, `RECON_ACCOUNT`, `PAYMENT_TERMS` |
| Sales Area | `SALES_ORG`, `DIST_CHANNEL`, `DIVISION`, `CUST_PRICING_PROC` |

Map 1,000 rows from the legacy CSV into the template. Assign BP role `FLCU00` (Customer) to each record. Set `BP_CATEGORY` = `2` (Organization) for corporate customers, `1` (Person) for individuals.

### 3. Upload and simulate

Upload the filled XML template in the cockpit. Choose **Simulate**.

**Result**: 23 errors out of 1,000 records:
- 12 rows: `Country code 'XX' does not exist` → Fix: correct invalid country codes in the source CSV.
- 11 rows: `Tax classification is mandatory for sales area data` → Fix: populate `TAX_CLASSIFICATION` field.

### 4. Fix and re-simulate

Correct the 23 records in the CSV, regenerate the XML template, re-upload, and simulate again.

**Result**: 0 errors, 1,000 records ready for migration.

### 5. Execute

Choose **Execute**. The cockpit creates 1,000 Business Partner records with linked Customer records. Monitor the migration project screen until status shows **Completed**.

### 6. Verify

- Open transaction `BP`, search for the migrated BP number range → confirm 1,000 BP records exist with role `FLCU00`.
- Open `FD03` (Customer Display) → verify company code data, reconciliation accounts, and payment terms.
- Run a test sales order (`VA01`) against a migrated customer to confirm sales area data is complete.

## Anti-patterns

### 1. Building custom BAPI programs instead of using the Migration Cockpit

**What goes wrong**: Teams write custom ABAP programs calling `BAPI_BUPA_CREATE_FROM_DATA` or `BAPI_CUSTOMER_CREATEFROMDATA1` to load data, re-implementing error handling, logging, restart logic, and simulation that the Migration Cockpit already provides out of the box.

**Why it matters**: The Migration Cockpit uses SAP-validated business object APIs internally and provides built-in simulation, error reporting, and retry capabilities. Custom programs bypass these safeguards and create maintenance burden ([SAP Help: Migrate Your Data - Migration Cockpit](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/2f0dbe4111214bcf9b2d57eca26f0525.html)).

### 2. Using LTMC on S/4HANA 2022+ systems

**What goes wrong**: Consultants with experience from older releases attempt to use transaction `LTMC`, not realizing it is deprecated and read-only from S/4HANA 2020 onward. New migration projects cannot be created in `LTMC` ([SAP Note 2733253](https://me.sap.com/notes/2733253)).

**Fix**: Use the **Migrate Your Data** Fiori app (F3473) exclusively on S/4HANA 2020+ systems.

### 3. Skipping simulation runs

**What goes wrong**: Teams go straight from data upload to **Execute**, then discover hundreds of errors that could have been caught cheaply in simulation. Failed executions may leave partial data in the target system requiring manual cleanup.

**Why it matters**: Simulation runs the full migration logic without database commits — it is the fastest feedback loop for data quality issues. Always simulate before executing ([SAP Help: Simulating the Migration](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/0ee46d72aa734da6ba5d9285da4d7148.html)).

### 4. Treating the migration object catalog as exhaustive

**What goes wrong**: Teams assume every data entity has a standard migration object. For some complex or industry-specific data (e.g., complex pricing condition records, custom Z-tables, industry solution master data), no standard object exists.

**Fix**: Check the catalog early. If no standard object exists, evaluate whether `LTMOM` can be used to create a custom object by copying and extending a similar standard object, or whether a separate custom load program is genuinely needed.

### 5. Not transporting migration objects to the test system

**What goes wrong**: Custom migration objects or modified standard objects created in `LTMOM` on the development system are not transported to the test system. The test migration then uses outdated object definitions, producing different results than expected.

**Fix**: Always include `LTMOM` objects in the transport request alongside the migration project. Re-transport after every modification ([SAP Help: Transporting Migration Objects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/898c9def31544ce487a034d9d7bdd87c.html)).

## References

1. [SAP Help: Data Migration (S/4HANA On-Premise, 2025 FPS01)](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/a4d4119a2cc9448a98e5d17e6dd0eac4.html) — Landing page for all data migration documentation.
2. [SAP Help: Migrate Your Data - Migration Cockpit](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/2f0dbe4111214bcf9b2d57eca26f0525.html) — Fiori app overview, key features, and situation handling.
3. [SAP Help: Creating Migration Projects](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/75be3f04d79d4bbc9727a234fce513b5.html) — Step-by-step project creation guide.
4. [SAP Help: Roles and Authorizations](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/29193bf0ebdd4583930b2176cb993268/dabe2e6948b24e33a6e4dfa2bb4ed1a3.html) — Required roles for migration users.
5. [SAP Note 2546430](https://me.sap.com/notes/2546430) — S/4HANA Migration Cockpit Central Note (collects all relevant sub-notes).
6. [SAP Note 2733253](https://me.sap.com/notes/2733253) — Migration Cockpit Fiori App: deprecation of LTMC, transition to Fiori app.
7. [SAP Note 3043614](https://me.sap.com/notes/3043614) — System settings required to create migration projects.
8. [SAP Note 2265093](https://me.sap.com/notes/2265093) — S/4HANA Business Partner Approach (Customer/Vendor Integration).
9. [SAP Fiori Apps Reference Library: Migrate Your Data (F3473)](https://fioriappslibrary.hana.ondemand.com/sap/fix/externalViewer/?appId=F3473) — Official Fiori app documentation.
10. [SAP-samples/s4hana-mc-xml-file-splitter](https://github.com/SAP-samples/s4hana-mc-xml-file-splitter) — Python CLI tool for splitting large Migration Cockpit XML files (Apache-2.0).
11. [SAP Community: Part 1 — Migrate your Data - Migration Cockpit](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/part-1-migrate-your-data-migration-cockpit-sap-s-4hana-2020-and-higher-and/ba-p/13501516) — Blog by Iliana Olvera, SAP (March 2021) covering staging tables approach.
12. [SAP Community: Tutorial — Using the SAP S/4HANA Migration Cockpit App](https://community.sap.com/t5/technology-blog-posts-by-members/tutorial-using-the-sap-s-4hana-migration-cockpit-app-step-by-step/ba-p/14016874) — Blog by Mickael Quesnot (February 2025) step-by-step tutorial.
13. [openSAP: Data Migration to SAP S/4HANA](https://open.sap.com/courses/s4h17) — Free course covering migration cockpit concepts and hands-on exercises.
