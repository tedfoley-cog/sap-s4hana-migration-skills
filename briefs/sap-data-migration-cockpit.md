## Brief: sap-data-migration-cockpit

**Skill name**: `sap-data-migration-cockpit`
**Phase**: Data migration (typically for greenfield or selective-data-transition projects, but also relevant for brownfield when consolidating data)
**Owner**: SAP S/4HANA Migration Cockpit — `LTMC` / `LTMOM` and the modern Fiori-based Migration Cockpit.

### Scope of this skill

How to use SAP's standard data migration tooling to load business data into S/4HANA, both for greenfield projects and for the ECC → S/4HANA brownfield case where some master data needs to be re-loaded or consolidated.

Cover:
- The two migration approaches: **file-based (XML templates)** and **staging tables**. When to use which.
- The **transactions / Fiori apps** involved: **`LTMC`** (legacy, on-stack), **`LTMOM`** (Migration Object Modeler — for customizing migration objects), and the modern **Migration Cockpit Fiori app** (replaces LTMC in newer releases).
- The **migration object catalog**: how to discover existing standard objects (Business Partner, Material, Customer, Vendor, Sales Order, Purchase Order, GL Account, Cost Center, etc.).
- **Custom migration objects**: how to create one in LTMOM by copying a standard object, adding fields, and mapping to staging tables or XML.
- The **migration project** lifecycle: create project → select objects → upload templates / load staging → simulate → execute → review errors → repeat.
- **Field mapping** including value mapping (rules) and lookups against existing master data.
- **Error handling**: where errors land, how to download them, common error patterns (missing customizing, missing mandatory fields).
- Hand-off to **functional tests**: the migrated data should be verified end-to-end against business processes.

### Key sources to consult

1. SAP Help Portal: "SAP S/4HANA Migration Cockpit" (latest release).
2. SAP Note **2546430** — "S/4HANA Migration Cockpit: Central Note".
3. SAP Note **2733253** — "S/4HANA Migration Cockpit Fiori app".
4. openSAP course: "Data Migration to SAP S/4HANA" (cite by course title and unit).
5. SAP-samples migration cockpit examples (search GitHub).

### Worked example

Walk through migrating customer master from a legacy CSV file:
1. Create project `MIG_CUSTOMERS` in the Migration Cockpit, file-based.
2. Select migration object `Customer (with Business Partner)` — note that this is the BP-aware version.
3. Download the XML template, fill in 1000 customers from the legacy CSV, including BP role assignment.
4. Upload the template, run **Simulate** — 23 errors: missing country codes for 12 rows, missing tax classification for 11 rows.
5. Fix the source file, re-upload, simulate clean.
6. Execute the load; 1000 customers created with linked BP records.
7. Verify with `BP` transaction in the target system.

### Anti-patterns

- Building a custom load program with `BAPI_BUSPARTNER_*` calls instead of using the Migration Cockpit (you re-implement what SAP already gave you, including the error reporting).
- Using LTMC in a release where the Migration Cockpit Fiori app is the supported path (leftover muscle memory).
- Skipping simulation runs (`SIMULATE`) and going straight to `EXECUTE` — far slower feedback on data errors.
- Treating the migration object catalog as exhaustive — for some master data (e.g. complex pricing condition records), you may still need a custom approach.

### Related skills

`sap-functional-simplifications`, `sap-migration-testing`
