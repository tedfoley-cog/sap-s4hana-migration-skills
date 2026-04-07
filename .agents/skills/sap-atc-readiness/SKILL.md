---
name: sap-atc-readiness
description: |
  Use when running ABAP Test Cockpit (ATC) checks to assess custom ABAP code
  readiness before an SAP ECC to S/4HANA system conversion: selecting and
  configuring S4HANA_READINESS check variants (S4HANA_READINESS_2023,
  S4HANA_READINESS_2025_FPS01, etc.), setting up a central ATC system for
  remote analysis of ECC source systems, interpreting ATC findings in
  transaction ATC or report SATC_AC_RUN_VIA_DELTA, applying Quick Fixes in
  ADT for Eclipse to remediate MATNR field-length extensions or removed
  function modules, managing ATC exemptions and migrating them to Clean Core
  checks, or producing delta worklists to track remediation progress across
  successive readiness runs.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "SAP Custom Code Migration Guide for S/4HANA 2025 FPS01"
    - "SAP Note 2436688 - ABAP Test Cockpit checks for ABAP custom code migration"
    - "SAP Note 1912445 - Recommended ABAP Test Cockpit check variants"
    - "SAP Note 2364916 - Remote Code Analysis via RFC"
    - "SAP Note 2270689 - Simplification Database loading"
    - "SAP Help Portal - ABAP Test Cockpit"
    - "SAP/abap-atc-cr-cv-s4hc-tools on GitHub"
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
related_skills:
  - sap-clean-core-extensibility
  - sap-cli-toolbelt
  - sap-functional-simplifications
  - sap-hana-performance
  - sap-migration-testing
  - sap-modern-abap-rewrite
  - sap-scoping
  - sap-simplification-database
  - sap-spdd-spau
  - sap-sum-dmo
---

## When to use this skill

Invoke this skill when:

- You need to **assess custom ABAP code** in an ECC system for S/4HANA compatibility before starting a system conversion.
- A project is selecting between **S4HANA_READINESS check variants** (e.g., `S4HANA_READINESS_2023` vs. `S4HANA_READINESS_2025_FPS01`) and needs guidance on which variant matches the target release.
- You are **setting up a central ATC system** (typically an S/4HANA sandbox or NetWeaver 7.52+ system) to run remote readiness checks against one or more ECC source systems.
- ATC findings need to be **triaged, remediated with Quick Fixes in ADT**, or suppressed via exemptions.
- You need to **track remediation progress** using delta worklists between successive ATC runs.
- Existing ATC exemptions for the Cloud Readiness check need to be **migrated to Clean Core checks** using the SAP Exemption Migration Tool.

Do **not** use this skill for:

- Scoping which custom objects to analyze — see `sap-scoping`.
- Looking up individual simplification items — see `sap-simplification-database`.
- SPDD/SPAU dictionary and modification adjustments during conversion — see `sap-spdd-spau`.
- Rewriting ABAP code to modern syntax after conversion — see `sap-modern-abap-rewrite`.

## Prerequisites

1. **Central ATC system** on the highest available ABAP release — ideally an S/4HANA sandbox at your target release (e.g., S/4HANA 2025). At minimum, a NetWeaver 7.52+ system is required for remote ATC capabilities ([SAP Note 2436688](https://me.sap.com/notes/2436688)).
2. **RFC connectivity** between the central ATC system and each ECC source system. The central system must be registered as an ATC server for the source systems via transaction `ATC` > *Administration* > *Central ATC System* ([SAP Note 2364916](https://me.sap.com/notes/2364916)).
3. **Simplification Database** loaded and up to date on the central ATC system, matching the target S/4HANA release. Use task list `SAP_BASIS_LOAD_SDB` via transaction `STC01` to load or refresh it ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Loading the Simplification Database").
4. **ABAP Development Tools (ADT) for Eclipse** installed on developer workstations — required for Quick Fix remediation of findings. ADT version should match or exceed the central ATC system's ABAP release.
5. **Authorization objects**: Users running ATC checks need `S_ATC_ADM` (administration), `S_ATC_EXE` (execution), and `S_DEVELOP` (display). Exemption approvers additionally need `S_Q_GOVERN` with activity 31 and `ATC_OTYPGO` 01 ([SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools/blob/b3d58db70a7c5c27467e856b31c7b42d2ad1bac6/docs/cloud-readiness-migration.md)).
6. **Check variant** `S4HANA_READINESS_<release>` must be available on the central system. SAP delivers these variants via SAP Notes; ensure the latest corrections are applied ([SAP Note 1912445](https://me.sap.com/notes/1912445)).

## Quick decision tree

```
Custom code needs S/4HANA readiness assessment?
 │
 ├─ Is a central ATC system available on the target release?
 │   ├─ YES → Go to Step 1 (Configure check variant)
 │   └─ NO  → Set up central ATC system first (see Prerequisites)
 │
 ├─ Which check variant to use?
 │   ├─ Target is S/4HANA 2023 → S4HANA_READINESS_2023
 │   ├─ Target is S/4HANA 2024 → S4HANA_READINESS_2024
 │   ├─ Target is S/4HANA 2025 → S4HANA_READINESS_2025
 │   └─ Target is S/4HANA 2025 FPS01 → S4HANA_READINESS_2025_FPS01
 │
 ├─ Is the Simplification Database current?
 │   ├─ YES → Run the check
 │   └─ NO  → Load/refresh via STC01 task SAP_BASIS_LOAD_SDB
 │
 ├─ Findings received — what next?
 │   ├─ Quick Fix available in ADT → Apply semi-automated correction
 │   ├─ Manual rewrite needed → Use sap-modern-abap-rewrite skill
 │   ├─ Finding is irrelevant (false positive / dead code) → Create exemption
 │   └─ Unsure → Check simplification item details (sap-simplification-database)
 │
 └─ Existing Cloud Readiness exemptions need migration to Clean Core?
     └─ Use SAP Exemption Migration Tool (zatc_cloud_rdnss_2_cln_core)
```

## Procedure

### Step 1 — Verify and select the check variant

The check variant must match your **target** S/4HANA release. SAP delivers release-specific variants that map to the Simplification Database content for that release ([SAP Note 1912445](https://me.sap.com/notes/1912445)).

| Target release | Check variant | Notes |
|---|---|---|
| S/4HANA 2023 | `S4HANA_READINESS_2023` | Also covers on-premise 2023 FPS releases |
| S/4HANA 2024 | `S4HANA_READINESS_2024` | Introduced additional BP and MATDOC checks |
| S/4HANA 2025 | `S4HANA_READINESS_2025` | Adds Universal Journal simplifications |
| S/4HANA 2025 FPS01 | `S4HANA_READINESS_2025_FPS01` | Latest variant; recommended for new projects |

Verify the variant exists on the central ATC system:
1. Open transaction `ATC`.
2. Navigate to *Check Variants* and search for `S4HANA_READINESS`.
3. If the variant is missing, apply the relevant SAP Note corrections ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

### Step 2 — Load or refresh the Simplification Database

The Simplification Database (SDB) provides the mapping between simplification items and the ATC checks. It must be loaded on the central ATC system and must match the target release ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Simplification Database").

1. Open transaction `STC01` on the central ATC system.
2. Execute task list `SAP_BASIS_LOAD_SDB`.
3. Verify the loaded SDB version in transaction `ATC` > *Administration* > *Simplification Database*.
4. The SDB version should correspond to the target S/4HANA release. If it does not, download the latest SDB content from SAP and re-run the task list.

> **Critical**: Failing to update the SDB before a check run means findings will be based on stale simplification data. New simplification items introduced in later support packages will be silently missed ([SAP Note 2270689](https://me.sap.com/notes/2270689)).

### Step 3 — Register source systems for remote ATC

Remote ATC allows the central system to analyze code that resides on ECC source systems without requiring code transport ([SAP Note 2364916](https://me.sap.com/notes/2364916)).

1. On the central ATC system, open transaction `ATC`.
2. Go to *Administration* > *Manage Systems*.
3. Register each ECC source system by providing:
   - System ID (e.g., `ECC_DEV`, `ECC_PRD`)
   - RFC destination pointing to the source system
   - Client number
4. Test the RFC connection to confirm connectivity.
5. On the source ECC system, configure the central ATC system as the remote ATC server via `ATC` > *Administration* > *Central ATC Settings*.

### Step 4 — Run the readiness check

You can run the check interactively or in batch:

**Interactive (transaction ATC)**:
1. Open transaction `ATC` on the central system.
2. Select *Run Check* > *Object Set*: choose packages, programs, or transport requests containing the scoped custom code.
3. Select the check variant (e.g., `S4HANA_READINESS_2025_FPS01`).
4. For remote checks, specify the source system RFC destination.
5. Execute the check run.

**Batch (report SATC_AC_RUN_VIA_DELTA)**:
1. Schedule report `SATC_AC_RUN_VIA_DELTA` as a background job on the central ATC system ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "ATC-based Custom Code Migration").
2. Parameters:
   - `P_VARIANT`: Check variant name (e.g., `S4HANA_READINESS_2025_FPS01`)
   - `P_OBJSET`: Object set or package scope
   - `P_RFCDEST`: RFC destination for the source system (for remote checks)
3. This report supports **delta mode** — it compares results against a previous run and produces only new or changed findings.

### Step 5 — Interpret the worklist

After the check completes, review findings in the ATC worklist:

1. In transaction `ATC`, open the results worklist.
2. Each finding includes:
   - **Priority**: 1 (error — must fix), 2 (warning — should fix), 3 (info)
   - **Check ID**: Identifies the specific check (e.g., `CL_CI_TEST_AMDP_HDB_MIGRATION`)
   - **Simplification Item**: Links to the relevant simplification item in the SDB
   - **Object name and line number**: Location of the finding in the source code
   - **Quick Fix availability**: Whether ADT can offer a semi-automated correction
3. Sort by priority to focus on errors first.
4. Group by simplification item to understand the migration theme (e.g., MATNR length extension, BP migration, MATDOC).

You can also download results using report `SATC_AC_DOWNLOAD_RESULT` for offline analysis or reporting ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Downloading Results").

### Step 6 — Remediate findings with ADT Quick Fixes

ABAP Development Tools for Eclipse provides semi-automated Quick Fixes for many common readiness findings ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

1. In ADT, open the *ATC Results* view.
2. Connect to the central ATC system and load the worklist.
3. Double-click a finding to navigate to the source code.
4. If a Quick Fix is available, a lightbulb icon appears. Press `Ctrl+1` to see available Quick Fixes.
5. Common Quick Fix categories:
   - **MATNR field-length extension**: Adjusts `CHAR(18)` declarations to `CHAR(40)` for material number fields ([SAP Note 2270333](https://me.sap.com/notes/2270333)).
   - **Removed function module replacement**: Replaces calls to deprecated BAPIs or function modules with their successors.
   - **Obsolete data type replacement**: Updates deprecated data element references.
6. Review each Quick Fix before applying — Quick Fixes are semi-automated and may require manual adjustment in complex call chains.
7. After applying fixes, activate the changed objects.

For findings without Quick Fixes (e.g., Business Partner migration logic, custom RTTI-based dynamic calls), manual rewriting is required. See the `sap-modern-abap-rewrite` skill for guidance.

### Step 7 — Manage exemptions

Findings that are false positives or apply to dead code should be exempted rather than remediated ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Exemptions").

1. In the ATC worklist, select the finding(s) to exempt.
2. Choose *Request Exemption* and provide:
   - **Justification**: Why the finding does not apply (e.g., "Dead code — object scheduled for deletion in transport `<transport-id>`").
   - **Validity period**: Set an end date; avoid open-ended exemptions.
3. An approver (configured in `ATC` > *Maintain Approvers*) must approve the exemption.
4. Approved exemptions suppress the finding in future check runs.

**Migrating exemptions to Clean Core checks**:

If you have existing exemptions for the Cloud Readiness check "Usage of Released APIs" and want to migrate them to the newer Clean Core check "Usage of APIs", use the SAP Exemption Migration Tool ([SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools)):

1. Install the tool via abapGit from `https://github.com/SAP/abap-atc-cr-cv-s4hc-tools`.
2. Requires SAP_BASIS 7.58 or higher.
3. Run program `zatc_cloud_rdnss_2_cln_core` in transaction `SE38`.
4. Choose to either display migration information or perform the migration.
5. Configuration option: choose whether to generate exemptions with no restrictions (all findings exempted) or to omit successor codes (findings with available successor objects will appear as new findings for review).
6. The migration can be undone, but modified exemptions will also be deleted.

Required authorizations: `S_DEVELOP` (ACTVT 03 and 16), `S_Q_GOVERN` (ACTVT 31, ATC_OTYPGO 01), and the user must be set as an approver in transaction `ATC` > *Maintain Approvers* ([SAP/abap-atc-cr-cv-s4hc-tools, docs/cloud-readiness-migration.md](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools/blob/b3d58db70a7c5c27467e856b31c7b42d2ad1bac6/docs/cloud-readiness-migration.md)).

### Step 8 — Produce delta worklists for progress tracking

Delta worklists compare two successive ATC runs to show remediation progress ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Delta Analysis").

1. After remediating findings and activating changes, re-run the check with the same variant and object scope.
2. Use report `SATC_AC_RUN_VIA_DELTA` with the delta option enabled.
3. The delta worklist shows:
   - **Cleared findings**: Previously reported findings that are now resolved.
   - **New findings**: Findings introduced by code changes since the last run.
   - **Remaining findings**: Findings that still require attention.
4. Use the cleared/remaining ratio to report progress to project stakeholders.


### CLI usage

`sapcli` can drive ATC check runs from the command line, enabling scripted readiness assessments without SAP GUI access.

**Environment variables**: `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD`

**Network prerequisites**: SAP system HTTPS port (typically 443 or 44300).

```bash
# Run the S/4HANA readiness check variant against a package
sapcli atc run --variant S4HANA_READINESS_2025 '$Z_CUSTOM_PKG' --output json > atc_results.json

# Parse the JSON results — count findings by priority
python3 -c "
import json, collections
data = json.load(open('atc_results.json'))
findings = data.get('findings', [])
counts = collections.Counter(f.get('priority', 'unknown') for f in findings)
for prio, count in sorted(counts.items()):
    print(f'Priority {prio}: {count} findings')
"

# Run against a specific object list (transport-based scope)
sapcli atc run --variant S4HANA_READINESS_2025 --objects zcl_customer_helper zcl_vendor_api --output json
```

This integrates directly with the delta worklist workflow (Step 8) — re-run after remediation to produce a diff of cleared vs. remaining findings ([sapcli README](https://github.com/jfilak/sapcli)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

### Scenario: Readiness check for `ZCL_CUSTOMER_HELPER` on S/4HANA 2025

**Setup**:
- Central ATC system: S/4HANA 2025 sandbox (`<system-id>`, client `<client-no>`)
- Source ECC system: ECC 6.0 EHP8 (`<system-id>`, client `<client-no>`), registered as RFC destination `<rfc-destination>`
- Target release: S/4HANA 2025 FPS01
- Object scope: Package `ZCUSTOMER` containing class `ZCL_CUSTOMER_HELPER` and related objects

**Step 1 — Verify variant**:
```
Transaction ATC → Check Variants → Search "S4HANA_READINESS"
→ Found: S4HANA_READINESS_2025_FPS01 ✓
```

**Step 2 — Refresh SDB**:
```
Transaction STC01 → Task List: SAP_BASIS_LOAD_SDB → Execute
→ SDB version: S/4HANA 2025 FPS01 (loaded 2026-04-05) ✓
```

**Step 3 — Run check**:
```
Transaction ATC → Run Check
  Object Set: Package ZCUSTOMER
  Check Variant: S4HANA_READINESS_2025_FPS01
  Source System: <rfc-destination>
→ Check completed: 7 findings
```

**Step 4 — Triage findings**:

| # | Object | Finding | Priority | Quick Fix? |
|---|---|---|---|---|
| 1 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR declared as CHAR(18), must be CHAR(40) | 1 - Error | Yes |
| 2 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR in local structure `LS_MAT` needs length extension | 1 - Error | Yes |
| 3 | `ZCL_CUSTOMER_HELPER=>GET_MATERIAL` | MATNR comparison with hard-coded 18-char value | 2 - Warning | Yes |
| 4 | `ZCL_CUSTOMER_HELPER=>CREATE_BP` | Call to `BAPI_CUSTOMER_CREATEFROMDATA1` — function module removed | 1 - Error | No |
| 5 | `ZCL_CUSTOMER_HELPER=>CREATE_BP` | Reference to table `KNA1` — replaced by BP tables | 2 - Warning | No |
| 6 | `ZCL_CUSTOMER_HELPER=>PRINT_DOC` | DATA declaration using obsolete type `SLIS_T_LISTHEADER` | 3 - Info | Yes |
| 7 | `ZCL_CUSTOMER_HELPER=>PRINT_DOC` | DATA declaration using obsolete type `SLIS_T_FIELDCAT_ALV` | 3 - Info | Yes |

**Step 5 — Remediate in ADT**:

Open `ZCL_CUSTOMER_HELPER` in ADT, connected to the central ATC system.

- **Findings 1-3** (MATNR length): Apply Quick Fixes via `Ctrl+1`. ADT adjusts the `DATA` declarations from `CHAR(18)` to `CHAR(40)` and updates the comparison logic. Review the changes in methods that pass MATNR to other objects — downstream callers may also need adjustment ([SAP Note 2270333](https://me.sap.com/notes/2270333)).
- **Findings 4-5** (BP migration): No Quick Fix available. The `BAPI_CUSTOMER_CREATEFROMDATA1` function module is removed in S/4HANA; replace with Business Partner API `CL_MD_BP_MAINTAIN` or the corresponding `I_BUSINESSPARTNER` OData service. References to `KNA1` must be replaced with `BUT000`/`BUT020` or CDS views `I_BusinessPartner` / `I_BPRelationship` ([SAP Note 2265093](https://me.sap.com/notes/2265093)). This requires manual rewriting — consult `sap-modern-abap-rewrite`.
- **Findings 6-7** (obsolete ALV types): Apply Quick Fixes to replace `SLIS_T_LISTHEADER` and `SLIS_T_FIELDCAT_ALV` with their successors.

Activate all changed objects.

**Step 6 — Delta run**:
```
Report SATC_AC_RUN_VIA_DELTA
  Variant: S4HANA_READINESS_2025_FPS01
  Object Set: Package ZCUSTOMER
  Delta mode: ON (compare with previous run)
→ Results: 5 cleared, 2 remaining (findings 4 and 5 — BP migration)
```

The 2 remaining findings require manual Business Partner migration work, tracked separately in the project plan.

## Anti-patterns

### 1. Running ATC against the wrong target release

Using `S4HANA_READINESS_2023` for a project targeting S/4HANA 2025 will **miss simplification items introduced in 2024 and 2025**. Each release adds new simplifications (e.g., additional material document changes in 2024, new finance simplifications in 2025). Always match the check variant to the exact target release and FPS level ([SAP Note 1912445](https://me.sap.com/notes/1912445)).

### 2. Forgetting to refresh the Simplification Database

The SDB content is updated by SAP with each support package. Running ATC against a stale SDB means new simplification items are **silently missing from the results** — the check completes without errors but reports an incomplete set of findings. Always refresh the SDB before each major check cycle via `STC01` task `SAP_BASIS_LOAD_SDB` ([SAP Note 2270689](https://me.sap.com/notes/2270689)).

### 3. Mass-suppressing findings via exemptions

Creating blanket exemptions to "clear the worklist" defeats the purpose of the readiness check. Exempted findings will not appear in delta worklists, hiding unresolved compatibility issues that will surface as runtime errors after conversion. Each exemption must have a specific justification and a bounded validity period ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Exemptions").

### 4. Running ATC only locally on the source ECC system

Running ATC on the ECC source system without a central ATC system on the target release means the checks execute against an **older Simplification Database version**. The source ECC system cannot load SDB content for a release newer than its own ABAP stack. Simplification items introduced in releases beyond the source system's level will be missed entirely. Always use a central ATC system at the target release ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

### 5. Treating ATC findings as exhaustive

ATC performs **static code analysis** only. It cannot detect compatibility issues in:
- Dynamic call sites using RTTI (`cl_abap_typedescr`, `cl_abap_structdescr`)
- Generated code (e.g., from SAPscript forms, SmartForms, or BRF+ rules)
- Dynamic SQL via `ADBC` or native SQL
- Code paths only reachable through complex runtime conditions

Supplement ATC with dynamic analysis (runtime monitoring, test execution in a sandbox) and manual code review for high-risk custom objects ([SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE), section "Limitations of Static Analysis").

### 6. Applying Quick Fixes without reviewing downstream impact

Quick Fixes for MATNR length extension change declarations from `CHAR(18)` to `CHAR(40)`, but downstream objects that receive these values (e.g., via `EXPORTING` parameters, shared memory, database operations) may still use the old length. Always trace the data flow after applying a Quick Fix and check calling/called objects for cascading impacts ([SAP Note 2270333](https://me.sap.com/notes/2270333)).

## References

### SAP Notes

- [SAP Note 2436688](https://me.sap.com/notes/2436688) — "ABAP Test Cockpit checks for ABAP custom code migration to SAP S/4HANA". Central note for ATC-based readiness checking; describes check variants, remote ATC setup, and finding categories.
- [SAP Note 1912445](https://me.sap.com/notes/1912445) — "Recommended ABAP Test Cockpit check variants". Lists all SAP-delivered check variants including the S4HANA_READINESS family.
- [SAP Note 2364916](https://me.sap.com/notes/2364916) — "Remote Code Analysis via RFC". Describes the remote ATC architecture and RFC configuration requirements.
- [SAP Note 2270689](https://me.sap.com/notes/2270689) — "Simplification Database loading in ATC". Covers the SDB loading process and version management.
- [SAP Note 2270333](https://me.sap.com/notes/2270333) — "Material Number Field Length Extension". Details the MATNR CHAR(18) to CHAR(40) change and its implications for custom code.
- [SAP Note 2265093](https://me.sap.com/notes/2265093) — "S/4HANA Business Partner Approach". Covers the migration from customer/vendor master to Business Partner.
- [SAP Note 3627152](https://me.sap.com/notes/3627152) — SAP Note Analyzer file for Clean Core checks required in ATC.

### SAP Documentation

- [SAP Custom Code Migration Guide for S/4HANA 2025 FPS01](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE) — Canonical runbook covering all aspects of ATC-based custom code migration, including central ATC setup, variant selection, SDB loading, finding interpretation, and exemption management.
- [SAP Help Portal: ABAP Test Cockpit](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b238a6e62bef4e56b18400c1945b8f09) — General ATC documentation covering check execution, result management, and configuration.

### SAP Open Source

- [SAP/abap-atc-cr-cv-s4hc-tools](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools/blob/b3d58db70a7c5c27467e856b31c7b42d2ad1bac6/docs/cloud-readiness-migration.md) — Apache-2.0. Official Exemption Migration Tool (`zatc_cloud_rdnss_2_cln_core`) for migrating Cloud Readiness check exemptions to Clean Core checks. Requires SAP_BASIS 7.58+.

### Key Transactions and Programs

| Transaction / Program | Purpose |
|---|---|
| `ATC` | ABAP Test Cockpit — main entry point for check execution, variant management, exemption approval, and administration |
| `ATC_OPS` | ATC Operations — monitoring and managing check runs |
| `STC01` | Task List Runner — used to execute `SAP_BASIS_LOAD_SDB` for Simplification Database loading |
| `SE38` | ABAP Editor — used to run the Exemption Migration Tool program `zatc_cloud_rdnss_2_cln_core` |
| `SATC_AC_RUN_VIA_DELTA` | Report for batch / delta ATC check runs |
| `SATC_AC_DOWNLOAD_RESULT` | Report for downloading ATC check results for offline analysis |
