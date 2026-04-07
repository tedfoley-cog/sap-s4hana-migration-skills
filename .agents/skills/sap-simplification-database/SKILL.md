---
name: sap-simplification-database
description: |
  Use when querying or interpreting the SAP Simplification Item Catalog
  or Simplification Database during an ECC-to-S/4HANA migration: loading
  the Simplification Database via transaction SYCM and SAP Note 2241080,
  filtering simplification items by target release or deployment model,
  cross-referencing ATC S4HANA_READINESS check findings with their
  originating simplification items, running the Simplification Item Check
  report /SDF/RC_START_CHECK (SAP Note 2399707), or mapping a
  simplification item to its remediation SAP Note (e.g., SAP Note 2265093
  for Business Partner).
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025"
  sources:
    - "SAP Note 2241080 — Simplification Database overview"
    - "SAP Note 2399707 — Simplification Item Check"
    - "SAP Note 2265093 — S/4HANA Business Partner Approach"
    - "SAP Note 1976487 — S/4HANA Simplification List"
    - "SAP Note 2436688 — ATC checks for ABAP custom code migration"
    - "SAP Note 2502552 — Simplification Item check class refinements"
    - "SAP Note 1668882 — SCI/ATC prerequisite note"
    - "SAP Custom Code Migration Guide for S/4HANA 2025"
    - "Conversion Guide for SAP S/4HANA 2025"
    - "SAP Help Portal — Setting Up and Performing SAP S/4HANA Custom Code Checks"
    - "Simplification Item Catalog (launchpad.support.sap.com/#/sic)"
    - "SAP Community — Olga Dolinskaja, Custom code adaptation for SAP S/4HANA FAQ"
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
    - "SAP HANA Client hdbsql (https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)"
related_skills:
  - sap-atc-readiness
  - sap-cli-toolbelt
  - sap-functional-simplifications
  - sap-spdd-spau
---

## When to use this skill

Use this skill when you need to:

- **Understand what changed** between SAP ECC and S/4HANA at the data-model, functional, UI, or integration level before planning custom-code remediation.
- **Load or refresh the Simplification Database** on the central ATC check system so that `S4HANA_READINESS_*` remote checks return accurate findings.
- **Research a specific simplification item** — for example, "Customer/Vendor Integration (Business Partner)" — to determine which custom objects are affected and what the remediation path is.
- **Filter simplifications by target release** (2023 / 2024 / 2025) and **deployment model** (On-Premise, Cloud Private Edition, Cloud Public Edition) to scope the work correctly.
- **Cross-reference Conversion Pre-Check results** from report `/SDF/RC_START_CHECK` with simplification items to identify which items will block a SUM/DMO run.
- **Map an ATC finding** back to its originating simplification item and then to the remediation SAP Note.

This skill is typically invoked *after* the scoping phase (`sap-scoping`) and *before or during* ATC readiness checks (`sap-atc-readiness`).

## Prerequisites

1. **SAP user with access to SAP for Me** (`me.sap.com`) — required to download the Simplification Database ZIP and browse SAP Notes.
2. **Central ATC check system** on at least SAP NetWeaver AS ABAP 7.52 or higher with the SCI/ATC infrastructure enabled ([SAP Note 1668882](https://me.sap.com/notes/1668882)).
3. **SAP Note 2436688** implemented on the central check system — delivers the `S4HANA_READINESS` ATC check variant and the SYCM transaction for Simplification Database import ([SAP Note 2436688](https://me.sap.com/notes/2436688)).
4. **SAP Note 2502552** implemented — delivers refined check classes that improve the accuracy of the simplification item relevance analysis ([SAP Note 2502552](https://me.sap.com/notes/2502552)).
5. **Simplification Database ZIP file** downloaded from the attachment of [SAP Note 2241080](https://me.sap.com/notes/2241080), matching the target S/4HANA release.
6. **Production-system usage data** (UPL/SCMON) loaded into the check system — strongly recommended so that findings can be filtered by actual usage. Without this, the check analyzes all custom code regardless of whether it is actively executed ([SAP Note 2399707](https://me.sap.com/notes/2399707)).

## Quick decision tree

```
START
  |
  v
Do you need to understand WHAT changed between ECC and S/4HANA?
  |--- YES --> Browse the Simplification Item Catalog (web UI) or
  |            the Simplification List PDF. Go to Step A below.
  |--- NO
  v
Do you need to run ATC S4HANA_READINESS checks against custom code?
  |--- YES --> Load the Simplification Database into the central
  |            check system via SYCM. Go to Step B below.
  |--- NO
  v
Do you need to interpret a specific ATC finding or pre-check error?
  |--- YES --> Map the finding to its simplification item and
  |            remediation SAP Note. Go to Step C below.
  |--- NO
  v
Do you need to run the Simplification Item Check before SUM/DMO?
  |--- YES --> Execute /SDF/RC_START_CHECK. Go to Step D below.
  |--- NO  --> This skill may not be relevant. Consider
               sap-functional-simplifications or sap-atc-readiness.
```

## Procedure

### Step A — Browse the Simplification Item Catalog

The **Simplification Item Catalog** is the web-facing search interface on the SAP Support Launchpad ([launchpad.support.sap.com/#/sic](https://launchpad.support.sap.com/#/sic)). It is the human-readable complement to the machine-readable Simplification Database loaded into ATC ([SAP Note 1976487](https://me.sap.com/notes/1976487)).

1. Open the Simplification Item Catalog at `https://launchpad.support.sap.com/#/sic`.
2. Use the **filter bar** to narrow results:
   - **Target Release**: select the S/4HANA version you are converting to (e.g., `SAP S/4HANA 2025`). Each release is cumulative — the 2025 catalog includes all items from earlier releases.
   - **Category**: filter by `Functional`, `Data Model`, `UI`, `Integration`, or `Deprecated` to focus on the area of interest.
   - **Deployment Model**: select `On-Premise`, `Cloud Private Edition`, or `Cloud Public Edition`. Some simplification items apply only to specific deployment models.
3. Each catalog entry shows:
   - A **title** and **description** summarizing the change.
   - The **affected objects** (tables, function modules, BAPIs, transaction codes).
   - Links to one or more **SAP Notes** that describe remediation steps.
   - Whether the item triggers a **Pre-Check** or **Custom Code Check** (or both).
4. Click through to the linked SAP Note(s) for detailed remediation guidance.

> **Key distinction**: The Simplification Item Catalog is a *read-only lookup tool*. It does not analyze your custom code. To analyze custom code, you need the Simplification Database loaded into ATC (Step B) or the Simplification Item Check (Step D).

### Step B — Load the Simplification Database into the central ATC system

The **Simplification Database** is a set of database tables imported into the central ATC check system. These tables power the `S4HANA_READINESS_*` remote ATC checks that identify custom-code incompatibilities ([SAP Note 2241080](https://me.sap.com/notes/2241080)).

1. **Download** the Simplification Database ZIP file:
   - Open [SAP Note 2241080](https://me.sap.com/notes/2241080).
   - In the *Attachments* section, download the ZIP file whose name matches your target release (e.g., `SDB_S4HANA_2025_FPS01.zip`).
   - Always take the **latest patch** — SAP updates the Simplification Database with every Feature Pack Stack (FPS) and correction note.

2. **Import** into the central check system using transaction `SYCM`:
   - Log on to the **central ATC check system** (not the managed system being converted).
   - Run transaction **SYCM** (Custom Code Migration Worklist).
   - Menu path: *Simplification Database → Import from ZIP file*.
   - Select the downloaded ZIP and confirm. The import typically completes in 1-5 minutes depending on system load.
   - After import, SYCM displays the loaded Simplification Database version and date ([SAP Community — Olga Dolinskaja, Custom code adaptation FAQ](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/sap-s-4hana-system-conversion-custom-code-adaptation-faq/ba-p/13364549)).

3. **Verify** the import:
   - In SYCM, navigate to *Simplification Database → Display* to confirm the version matches your target release.
   - The Simplification Database version string follows the pattern `<release>_<FPS>_<patch>` (e.g., `2025_FPS01_0002`).

4. **Configure UPL data access** (if using production usage data):
   - In SYCM, go to *Utilities → Configure UPL Data Access*.
   - Specify the RFC destination pointing to the production system where SCMON/UPL data was collected.
   - This enables ATC to filter findings by actual usage, significantly reducing false positives.

> **Important**: The Simplification Database must be refreshed whenever you change your target release or when SAP publishes a new patch to [SAP Note 2241080](https://me.sap.com/notes/2241080). Running ATC checks against an outdated Simplification Database produces misleading results — either false clears (missing new items) or false positives (items already resolved in a newer patch).

### Step C — Map an ATC finding to a simplification item and remediation note

When `sap-atc-readiness` produces findings with message class `S4HANA_READINESS`, each finding can be traced back to a specific simplification item:

1. **Open the ATC finding** in the ATC Results Browser (transaction `ATC`).
2. Note the **check ID** (e.g., `S4HANA_READINESS_SIMPL_0001`) and the **message text**, which typically names the affected object and the simplification item.
3. The finding's **long text** (F1 help or double-click) contains:
   - The simplification item title.
   - The linked **SAP Note number** for remediation.
   - The **category** (Functional, Data Model, etc.).
4. Look up the SAP Note in SAP for Me for the detailed remediation procedure.
5. In SYCM, use *Simplification Database → Search* to find the item by keyword or SAP Note number for additional context.

### Step D — Run the Simplification Item Check (Conversion Pre-Checks)

The **Simplification Item Check** is a standalone check report that validates whether simplification items are relevant and consistent *before* the SUM/DMO conversion run. It is distinct from ATC custom-code checks — it checks the *system state* rather than *custom code* ([SAP Note 2399707](https://me.sap.com/notes/2399707)).

1. **Implement prerequisite notes**:
   - [SAP Note 1668882](https://me.sap.com/notes/1668882) — SCI/ATC infrastructure.
   - [SAP Note 2399707](https://me.sap.com/notes/2399707) — delivers report `/SDF/RC_START_CHECK` and the simplification item catalog embedded in the check.
   - [SAP Note 2502552](https://me.sap.com/notes/2502552) — delivers refined check classes for more accurate relevance filtering.

2. **Execute the check**:
   - Run report `/SDF/RC_START_CHECK` via transaction `SA38`.
   - Select the target S/4HANA release.
   - Choose the check scope: *Relevance Check*, *Consistency Check*, or *Compatibility Scope Check*.
     - **Relevance Check**: determines which simplification items are relevant to your system based on installed components and active business functions.
     - **Consistency Check**: verifies that the system state is consistent with the simplification item requirements (e.g., required data migrations have been performed).
     - **Compatibility Scope Check**: validates the compatibility of your system scope with the target release.

3. **Interpret results**:
   - Items marked **red** (error) will block the SUM/DMO conversion. These must be resolved before cutover.
   - Items marked **yellow** (warning) should be reviewed but will not block conversion.
   - Items marked **green** (passed) require no action.

4. **Cross-reference with the Simplification Item Catalog** to understand the business context of each blocking item.

> **Critical**: SAP strongly recommends running the Simplification Item Check against a **copy of the production system**. Running against a non-production system that does not mirror production data and configuration produces incomplete or misleading results ([SAP Note 2399707](https://me.sap.com/notes/2399707)).

### Step E — Filter by deployment model

Not all simplification items apply to all deployment models. When planning the conversion:

1. In the Simplification Item Catalog, use the **Deployment Model** filter to select:
   - **On-Premise** — the broadest set; most items apply.
   - **Cloud Private Edition (PCE)** — same kernel as On-Premise but SAP-managed; some infrastructure-level simplifications do not apply.
   - **Cloud Public Edition** — the most restrictive; many customization-related items are replaced by clean-core extensibility patterns.
2. In `/SDF/RC_START_CHECK`, the deployment model is set automatically based on the system's license type, but verify this in the check parameters.
3. When mapping ATC findings, confirm the deployment model filter matches your project's target — a simplification item flagged "Cloud Public Edition only" is irrelevant for an On-Premise conversion.


### CLI usage

Use `sapcli` for source-level diffing and `hdbsql` for table existence checks when investigating simplification items.

**Environment variables**:
- `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD` (for sapcli)
- `HANA_HOST`, `HANA_USER`, `HANA_PASSWORD` (for hdbsql)

**Network prerequisites**: SAP HTTPS port + HANA port 443 (Cloud) or 3\<sysnr\>15 (on-prem).

```bash
# Download the source of a custom object that references a deprecated table
sapcli checkout class zcl_stock_report

# Diff the downloaded source against a previous version
diff -u ./zcl_stock_report_old.abap ./zcl_stock_report.abap

# Verify whether a table still exists on HANA (useful for S031-S039 checks)
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME='SAPHANADB' AND TABLE_NAME='S031'"
```

If the query returns zero rows, the aggregate table has been removed and custom code referencing it must be remediated per the simplification item ([SAP Help: hdbsql](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

**Scenario**: A customer is converting from SAP ECC 6.0 EHP 8 to SAP S/4HANA 2025 On-Premise. The `sap-atc-readiness` skill has produced a worklist with 47 findings in message class `S4HANA_READINESS`. Several findings reference tables `KNA1` and `LFA1`. The project team needs to understand the simplification context and plan remediation.

### 1. Search the Simplification Item Catalog

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

### 2. Confirm in the Simplification Database

On the central ATC check system, verify the Simplification Database is loaded and current:

```
Transaction: SYCM
Menu: Simplification Database → Display
Expected: Version 2025_FPS01_xxxx (latest patch)
```

If the version is outdated, re-import from [SAP Note 2241080](https://me.sap.com/notes/2241080).

### 3. Filter the ATC worklist

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

### 4. Open the remediation SAP Note

[SAP Note 2265093](https://me.sap.com/notes/2265093) describes:

- The synchronization mechanism between `KNA1`/`LFA1` and `BUT000` during and after conversion.
- Which BAPI calls (`BAPI_CUSTOMER_GETDETAIL`, `BAPI_VENDOR_GETDETAIL`) are replaced and by what.
- The CDS views available as stable interfaces: `I_Customer`, `I_Supplier`, `I_BusinessPartner`.
- The Business Partner configuration guide and the Customer/Vendor Integration (CVI) error-resolution process.

### 5. Hand off to developers

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

## Anti-patterns

1. **Using the Simplification Item Catalog as a code-fix oracle**
   The catalog tells you *what* changed (e.g., "KNA1 replaced by BUT000") but not *how* to fix every call site in your custom code. It links to remediation SAP Notes that describe the general approach, but applying that approach to specific custom programs requires developer judgment. Do not expect the catalog to provide line-by-line fix instructions.

2. **Loading an outdated Simplification Database**
   The Simplification Database is updated with every Feature Pack Stack and correction note. Running ATC checks against a stale database produces false clears — simplification items added in recent patches will not be flagged, giving a misleading "all clear" result. Always download the latest patch from [SAP Note 2241080](https://me.sap.com/notes/2241080) before each ATC run ([SAP Note 2241080](https://me.sap.com/notes/2241080)).

3. **Ignoring deployment-model filters**
   A simplification item that applies to Cloud Public Edition may not apply to On-Premise or Cloud Private Edition (and vice versa). Failing to filter by deployment model inflates the worklist with irrelevant items or — worse — omits items that do apply. Always confirm the deployment model in both the Simplification Item Catalog and the `/SDF/RC_START_CHECK` parameters.

4. **Treating the Simplification Database as a one-time load**
   The database must be refreshed whenever: (a) SAP publishes a new patch to [SAP Note 2241080](https://me.sap.com/notes/2241080), (b) you change your target S/4HANA release, or (c) a new FPS is released. Treating it as a set-and-forget artifact leads to drift between the checks and the actual target release requirements.

5. **Running Simplification Item Check on a non-production system**
   SAP Note 2399707 explicitly warns that results from non-production systems may be "incomplete or misleading." The check analyzes installed components, active business functions, and transactional data volumes — all of which may differ between sandbox and production. Always run against a recent copy of production ([SAP Note 2399707](https://me.sap.com/notes/2399707)).

6. **Confusing the Simplification Item Check with ATC custom-code checks**
   `/SDF/RC_START_CHECK` checks *system state and configuration* (e.g., "Has the BP data migration been completed?"). ATC `S4HANA_READINESS` checks analyze *custom ABAP code* for incompatibilities (e.g., "This program reads from KNA1"). They are complementary, not interchangeable. A green Simplification Item Check does not mean custom code is clean, and vice versa.

## References

- [SAP Note 2241080 — SAP S/4HANA: Content for checking customer-specific code (Simplification Database)](https://me.sap.com/notes/2241080) — Central note for downloading and importing the Simplification Database.
- [SAP Note 2399707 — Simplification Item Check](https://me.sap.com/notes/2399707) — Delivers report `/SDF/RC_START_CHECK` for pre-conversion relevance, consistency, and compatibility scope checks.
- [SAP Note 2265093 — S/4HANA: Business Partner Approach](https://me.sap.com/notes/2265093) — Remediation guidance for Customer/Vendor Integration simplification.
- [SAP Note 1976487 — S/4HANA Simplification List](https://me.sap.com/notes/1976487) — Master note linking to the Simplification List PDF for each release.
- [SAP Note 2436688 — ATC checks for ABAP custom code migration to S/4HANA](https://me.sap.com/notes/2436688) — Delivers the S4HANA_READINESS check variant and SYCM transaction.
- [SAP Note 2502552 — Simplification Item check class refinements](https://me.sap.com/notes/2502552) — Improved check classes for more accurate simplification item relevance analysis.
- [SAP Note 1668882 — SCI/ATC infrastructure prerequisite](https://me.sap.com/notes/1668882) — Prerequisite for enabling the ATC check infrastructure.
- [SAP Custom Code Migration Guide for S/4HANA 2025](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a4412900053/2025/en-US/CustomCodeMigration_Guide_S4HANA.pdf) — Canonical runbook, section "Simplification Item Check".
- [Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb8960f1a5f025/2025/en-US/Conversion_Guide_S4HANA.pdf) — System conversion procedure including pre-check requirements.
- [SAP Help Portal — Setting Up and Performing SAP S/4HANA Custom Code Checks](https://help.sap.com/docs/ABAP_PLATFORM_NEW/7bfe8cdcae274705876b07e0396817ba) — Step-by-step instructions for Simplification Database import and ATC configuration.
- [Simplification Item Catalog](https://launchpad.support.sap.com/#/sic) — Web-based search interface for browsing all simplification items by release, category, and deployment model.
- [SAP Community — Olga Dolinskaja, Custom code adaptation for SAP S/4HANA FAQ](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/sap-s-4hana-system-conversion-custom-code-adaptation-faq/ba-p/13364549) — Practical Q&A on SYCM usage and Simplification Database import.
