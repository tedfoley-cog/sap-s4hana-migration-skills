---
name: sap-migration-testing
description: |
  Use when planning, executing, or automating testing for an SAP ECC to S/4HANA
  system conversion: building a test strategy for brownfield migration, running
  cutover dry-run rehearsals with SUM/DMO, executing Order-to-Cash or
  Procure-to-Pay regression tests after SPDD/SPAU adjustments, validating
  Business Partner (BP) migration or MATDOC material-document changes, setting
  up ABAP Unit tests for custom code touched by simplification items, scoping
  User Acceptance Testing (UAT) with business process owners, configuring
  SAP Solution Manager Test Suite or SAP Cloud ALM for test orchestration,
  refreshing sandbox systems with production-like data via SAP TDMS or
  SAP Landscape Transformation, diagnosing post-go-live hypercare defects
  during the first month-end close, or evaluating third-party test automation
  tools such as Tricentis Tosca or Worksoft Certify for SAP regression packs.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025"
  sources:
    - "SAP Activate Methodology — Roadmap Viewer (roadmapviewer.cloud.sap)"
    - "SAP Help Portal — Testing in SAP S/4HANA Cloud Public Edition"
    - "SAP Help Portal — Conversion Guide for SAP S/4HANA"
    - "SAP Note 2399707 — SAP S/4HANA Conversion Pre-Checks"
    - "SAP Note 1912445 — Recommended ABAP Test Cockpit Check Variants"
    - "SAP Note 2129147 — Test Automation Tool for S/4HANA Cloud"
    - "SAP Note 2436688 — ATC Checks for Custom Code Migration"
    - "SAP Note 2265093 — S/4HANA Business Partner Approach"
    - "SAP Note 2270333 — Material Number Field Length Extension"
    - "SAP Community — SAP Project Manager's Guide to SAP Project Cutover (Greg Baus, 2021)"
    - "SAP Community — Running your System Conversion to SAP S/4HANA Cloud (2025)"
    - "SAP Press — Testing SAP Solutions (2nd Edition)"
    - "SAP Community — Test Automation Tool for SAP S/4HANA Cloud (Aniruddh, November 2022)"
related_skills:
  - sap-sum-dmo
  - sap-spdd-spau
  - sap-functional-simplifications
  - sap-hana-performance
  - sap-atc-readiness
---

## When to use this skill

Invoke this skill when you need to:

- **Plan a test strategy** for a brownfield ECC-to-S/4HANA system conversion, covering all test levels from ABAP Unit through UAT.
- **Prepare cutover dry runs** — deciding how many rehearsals to run, what to validate, and how to measure cutover duration.
- **Build regression test packs** for core business processes (Order-to-Cash, Procure-to-Pay, Record-to-Report) affected by simplification items.
- **Validate functional simplifications** — confirm that Business Partner migration (CVI), MATDOC material documents, ACDOCA Universal Journal, and MATNR length changes work correctly in converted custom code.
- **Set up test automation** using SAP Solution Manager Test Suite, SAP Cloud ALM test orchestration, or third-party tools (Tricentis Tosca, Worksoft Certify, Panaya).
- **Scope and run UAT** with business process owners after each SUM dry run.
- **Manage test data** — refresh sandbox environments with production-like data using SAP Test Data Migration Server (TDMS) or SAP Landscape Transformation (SLT).
- **Plan hypercare** — define monitoring patterns, defect triage, and success criteria for the first month-end close after go-live.

This skill cross-references `sap-atc-readiness` for static analysis (ATC is a prerequisite, not a substitute for functional testing) and `sap-hana-performance` for performance test guidance on HANA.

## Prerequisites

1. **SAP Solution Manager 7.2 SP10+** or **SAP Cloud ALM** configured with a connection to the managed system landscape ([SAP Help: SAP Cloud ALM for Test Management](https://help.sap.com/docs/cloud-alm/setup-administration/test-management)).
2. **ATC checks completed** on custom code — see `sap-atc-readiness`. ATC provides static analysis but does not exercise runtime behavior ([SAP Note 2436688](https://me.sap.com/notes/2436688)).
3. **Simplification Database reviewed** — the list of in-scope simplification items determines which business processes require regression testing ([SAP Note 1976487](https://me.sap.com/notes/1976487)).
4. **Sandbox system** refreshed with production-like data. Data volume must be representative of production to catch performance regressions. Anonymize personal data per GDPR requirements using SAP TDMS scrambling or SAP Data Privacy Management.
5. **Test management tool** configured — either SAP Solution Manager Test Suite (transaction `STWB_WORK` for test workbench) or a third-party tool integrated via eCATT/CBTA interfaces.
6. **SUM/DMO technical prerequisites met** — see `sap-sum-dmo` for the conversion tooling setup that the dry runs will exercise.

## Quick decision tree

```
Is this a greenfield (new implementation)?
├── YES → This skill does not apply. Use standard SAP Activate test deliverables.
└── NO (brownfield system conversion) →
    ├── Has ATC been run on all in-scope custom code?
    │   ├── NO → Run ATC first (see sap-atc-readiness). ATC clean ≠ tested.
    │   └── YES →
    │       ├── Is the sandbox refreshed with production-like data?
    │       │   ├── NO → Refresh sandbox (see Procedure Step 1).
    │       │   └── YES →
    │       │       ├── Are regression test scripts built for core processes?
    │       │       │   ├── NO → Build them (see Procedure Step 2).
    │       │       │   └── YES →
    │       │       │       ├── Has at least 1 SUM dry run been completed?
    │       │       │       │   ├── NO → Run dry run #1 (see Procedure Step 4).
    │       │       │       │   └── YES →
    │       │       │       │       ├── All regression tests passing?
    │       │       │       │       │   ├── NO → Fix and re-run (Step 5).
    │       │       │       │       │   └── YES → Schedule UAT (Step 6).
    │       │       │       │       └── 3+ dry runs completed with stable timing?
    │       │       │       │           ├── NO → Run more dry runs.
    │       │       │       │           └── YES → Ready for production cutover.
```

## Procedure

### Step 1 — Refresh sandbox with production-like data

The test environment must mirror production in data volume and complexity. Small datasets mask performance regressions that only appear at production scale.

1. Use **SAP Test Data Migration Server (TDMS)** to copy a time-slice or full-copy of production data to the sandbox. TDMS supports selective data extraction with referential integrity across dependent tables ([SAP Help: SAP TDMS](https://help.sap.com/docs/SAP_TDMS)).
2. Alternatively, use **SAP Landscape Transformation (SLT)** for real-time or periodic replication if ongoing data freshness is required.
3. **Anonymize sensitive data**: scramble fields containing personal data (names, addresses, bank accounts) using TDMS scrambling rules. Map scrambling profiles to data domains (e.g., `DOMAIN = AD_NAMEFIR` → randomize). This is mandatory for GDPR compliance in non-production systems.
4. **Target data freshness**: T-3 months before go-live is a common baseline. Refresh again at T-4 weeks for final dry run.
5. Validate data completeness post-refresh by running key report transactions (e.g., `SE16N` spot-checks on tables `VBAK`, `EKKO`, `BKPF`, `MARA`) and comparing record counts to production.

### Step 2 — Build regression test scripts for core business processes

Focus test effort on the business processes most affected by S/4HANA simplification items. The SAP Activate methodology prescribes building test scripts during the Realize phase, parameterized to cover process variants ([SAP Activate Roadmap Viewer](https://go.support.sap.com/roadmapviewer/)).

**Priority processes for brownfield conversion:**

| Process area | Key transactions | Simplification impact |
|---|---|---|
| Order-to-Cash (OTC) | `VA01`, `VL01N`, `VF01` | BP migration (CVI), credit management changes ([SAP Note 2265093](https://me.sap.com/notes/2265093)) |
| Procure-to-Pay (PTP) | `ME21N`, `MIGO`, `MIRO` | MATDOC replaces MKPF/MSEG ([SAP Note 2227764](https://me.sap.com/notes/2227764)), BP for vendors |
| Record-to-Report (RTR) | `FB01`, `F-02`, `FAGL_FCV` | ACDOCA Universal Journal replaces FAGLFLEXA+BSEG ([SAP Note 2270407](https://me.sap.com/notes/2270407)) |
| Warehouse/Inventory | `MIGO`, `MI01`, `LT01` | Material document in MATDOC, possible EWM migration |
| Master data | `BP`, `MM01`, `XK01` | Customer/vendor → BP, MATNR length extension ([SAP Note 2270333](https://me.sap.com/notes/2270333)) |

For each process area:

1. Identify **process variants** — e.g., for OTC: standard sale, returns (RE), intercompany (IC), third-party drop-ship, consignment.
2. Write **parameterized test scripts** in SAP Solution Manager Test Suite using `STWB_WORK` (Test Workbench) or in SAP Cloud ALM test management. Parameterize by sales organization, plant, material type, and customer account group.
3. Include both **happy path** and **exception path** tests. Exception handling is where simplification items cause the most breakage — e.g., a custom BAPI reading from `MKPF` that no longer exists in S/4HANA.
4. Map each test script to the **simplification item** it validates. This traceability is critical for defect root-cause analysis.

### Step 3 — Set up ABAP Unit tests for affected custom code

ABAP Unit tests are the lowest-cost, highest-frequency layer of the test pyramid. They catch regressions in custom code before expensive integration tests run.

1. Identify custom code objects flagged by ATC with S/4HANA-relevant findings (check variant `/SDF/S4_HANA_READINESS` per [SAP Note 1912445](https://me.sap.com/notes/1912445)).
2. For each remediated object, write or update ABAP Unit test classes. Use `CL_ABAP_UNIT_ASSERT` for assertions. Prefer **test doubles** (via `CL_OSQL_TEST_ENVIRONMENT` for CDS views, or `CL_ABAP_TESTDOUBLE` for interfaces) to isolate unit behavior from database dependencies.
3. Run ABAP Unit tests via transaction `SE80` → Run As → ABAP Unit Test, or programmatically via `ABAP_UNIT_RUNNER`.
4. Integrate ABAP Unit execution into the ATC check variant so that unit test failures are surfaced alongside static analysis findings ([SAP Help: ABAP Unit Integration in ATC](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abenabap_unit.htm)).
5. Target: every custom function module, class, or report that was modified for S/4HANA compatibility should have at least one ABAP Unit test covering the changed logic path.

### Step 4 — Execute SUM/DMO dry run #1 and run regression tests

The first cutover dry run is a learning exercise. Expect failures — the goal is to identify them early.

1. Execute the SUM/DMO conversion in the sandbox system (see `sap-sum-dmo` for the technical procedure). Record the total downtime duration.
2. After the SUM run completes, immediately execute the full regression test pack from Step 2.
3. Capture all test results in the test management tool. Classify failures:
   - **Custom code defects**: e.g., a Z-report reading from `BSEG` instead of `ACDOCA` — route to ABAP remediation (see `sap-functional-simplifications`).
   - **Data migration issues**: e.g., customer/vendor master not correctly migrated to BP — check CVI synchronization cockpit (`CVIMC`).
   - **Configuration gaps**: e.g., output determination not reconfigured for the new output management framework.
   - **Performance regressions**: queries taking significantly longer on HANA — route to `sap-hana-performance`.
4. Run ABAP Unit tests (Step 3) to validate that unit-level custom code is sound.
5. Document the cutover duration, number of test failures, and blocking issues. This baseline is essential for measuring improvement in subsequent dry runs.

### Step 5 — Fix, re-run dry run #2 and #3

Each subsequent dry run should show measurable improvement in both cutover duration and test pass rate.

1. **Fix all blocking defects** identified in dry run #1. Prioritize by business impact — a broken OTC flow blocks revenue, a broken MI01 flow is lower priority.
2. Re-run the SUM/DMO conversion in a freshly refreshed sandbox (do NOT re-run on the same already-converted system).
3. Re-execute the full regression test pack. Compare results to dry run #1.
4. **Dry run #2 success criteria**: all critical and high-priority test scripts pass. Cutover duration is within 10% of target.
5. **Dry run #3** is the final dress rehearsal. It should mirror production cutover as closely as possible:
   - Use the actual cutover plan and runbook (task sequence, responsible persons, communication plan).
   - Execute during a realistic time window (e.g., the same weekend slot planned for production).
   - Include the go/no-go decision point.
   - All regression tests must pass. Cutover duration must meet the target downtime window.

SAP and industry best practice recommend a minimum of **3 dry runs** before production go-live. Complex landscapes or regulated industries may require 4-5 ([SAP Community: SAP Project Manager's Guide to SAP Project Cutover](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-project-manager-s-guide-to-sap-project-cutover/ba-p/13510809)).

### Step 6 — Scope and execute User Acceptance Testing (UAT)

UAT validates that business processes work correctly from the end-user perspective. It is NOT a substitute for technical regression testing — it is an additional layer.

1. **Scope UAT** based on the simplification items that affect each business area. The test lead and business process owners jointly define the UAT scope.
2. **UAT participants**: business process owners and key users — not IT staff. They execute tests using familiar transactions and Fiori apps.
3. **UAT environment**: use the system produced by dry run #3 (or a dedicated UAT system converted in parallel).
4. **Defect tracking**: use a single defect management tool (e.g., SAP Solution Manager Incident Management, Jira, or ServiceNow). Classify defects by severity (S1-blocker through S4-cosmetic) and assign to the responsible remediation team.
5. **UAT sign-off criteria**: all S1 and S2 defects resolved, no open S1 defects, S3/S4 defects tracked with a remediation timeline. Business process owners formally sign off before the go/no-go decision.

### Step 7 — Performance testing

Performance testing validates that business-critical transactions and batch jobs execute within acceptable time on the target HANA database at production data volumes.

1. **Identify critical transactions**: focus on high-frequency online transactions (e.g., `VA01`, `ME21N`, `FB01`) and long-running batch jobs (e.g., MRP run `MD01`, billing due list `VF04`, payment run `F110`).
2. **Benchmark on ECC**: record baseline response times for critical transactions on the source ECC system before conversion.
3. **Run on converted sandbox**: execute the same transactions/jobs on the converted S/4HANA sandbox with production-volume data. Compare response times.
4. **Acceptable thresholds**: online transactions should not degrade by more than 20% versus ECC baseline. Most should improve on HANA. Batch jobs should show significant improvement due to HANA in-memory processing.
5. If performance regressions are found, route to `sap-hana-performance` for SQL optimization, CDS view tuning, and HANA-specific profiling (transaction `ST05`, `SQLM`, or HANA SQL Analyzer).
6. See the reference file `references/performance-test-checklist.md` for a detailed checklist.

### Step 8 — Hypercare planning (first 30 days post-go-live)

Hypercare is the stabilization period immediately after production go-live. Plan it before cutover, not after.

1. **Staff a war room** for the first 2 weeks: functional consultants, ABAP developers, Basis administrators, and business key users available during business hours.
2. **Monitoring checklist** — check daily:
   - System logs: transaction `SM21` for system log, `ST22` for ABAP dumps (short dumps spike post-conversion due to unconverted custom code paths hit for the first time in production).
   - Background jobs: transaction `SM37` — verify all critical batch jobs completed successfully.
   - Application monitors: transaction `SLG1` for application logs, check for CVI synchronization errors if BP migration is active.
   - HANA alerts: HANA Studio or `DBACOCKPIT` for memory, CPU, and disk alerts.
3. **First month-end close** is the highest-risk event in hypercare. Plan a dedicated support window. Common issues:
   - Financial closing cockpit (`FAGL_FCV`) behavior changes with Universal Journal ([SAP Note 2270407](https://me.sap.com/notes/2270407)).
   - Asset depreciation run (`AFAB`) — validate posting to ACDOCA.
   - Intercompany elimination and consolidation — verify IC reconciliation reports.
4. **Defect triage SLA**: S1 (system-down) = 2-hour response, S2 (critical business process blocked) = 4-hour response, S3 = next business day, S4 = backlog.
5. **Hypercare exit criteria**: 2 consecutive weeks with zero S1/S2 defects, first month-end close completed successfully, all batch jobs stable, key user confidence survey > 80% satisfaction.

## Worked example

**Scenario**: Acme Retail, a mid-sized retailer, is performing a brownfield ECC 6.0 EHP8 → S/4HANA 2024 conversion. The OTC process is the highest-priority business area.

### Identify in-scope process variants

The test lead reviews the simplification database and identifies these OTC impacts:

- Customer master → Business Partner (CVI) ([SAP Note 2265093](https://me.sap.com/notes/2265093))
- Credit management → SAP Credit Management (new) replaces classic FI credit management
- Output determination → Output Management (OM) replaces NACE-based output
- Material documents now in `MATDOC` instead of `MKPF`/`MSEG` ([SAP Note 2227764](https://me.sap.com/notes/2227764))

Four OTC variants are in scope:

| Variant | Sales Org | Material Type | Notes |
|---|---|---|---|
| Standard domestic sale | `1000` | `FERT` | Happy path |
| Returns processing | `1000` | `FERT` | Return order type `RE` |
| Intercompany sale | `1000` → `2000` | `FERT` | IC billing, elimination |
| Third-party drop-ship | `1000` | `HAWA` | PO auto-created from SO |

### Build 12 test scripts in Solution Manager

The test lead creates test scripts in `STWB_WORK`:

```
Test Plan: ACME_OTC_S4_REGRESSION
├── TP_OTC_001: Standard sale (1000/FERT) — VA01 → VL01N → VF01
├── TP_OTC_002: Standard sale (1000/HAWA) — VA01 → VL01N → VF01
├── TP_OTC_003: Returns (1000/FERT) — VA01 type RE → VL01N → VF01 credit memo
├── TP_OTC_004: Intercompany (1000→2000/FERT) — VA01 → VL01N → VF01 → VFIC
├── TP_OTC_005: Third-party (1000/HAWA) — VA01 → ME21N auto-PO → MIGO → VF01
├── TP_OTC_006: Credit check block — VA01 with exceeded credit limit
├── TP_OTC_007: Output — invoice print via new Output Management
├── TP_OTC_008: Pricing with custom condition type ZABC
├── TP_OTC_009: BP validation — customer created via BP, check KNVV/KNVP populated
├── TP_OTC_010: Availability check — VA01 with ATP check on batch-managed material
├── TP_OTC_011: Billing due list — VF04 mass billing run (500 orders)
├── TP_OTC_012: Revenue recognition — post billing, check ACDOCA entries
```

### Refresh sandbox

TDMS time-slice copy of production data from 3 months prior. Scramble `KNA1-NAME1`, `KNA1-STRAS`, `ADRC-*` fields. Validate: `SE16N` shows 1.2M records in `VBAK` (matches production ± 5%).

### Run SUM dry run #1

SUM DMO conversion completes in 14 hours. Run regression:

- **5 failures** detected:
  1. `TP_OTC_005` (third-party): custom function module `Z_SD_CREATE_PO` reads `LFA1-LIFNR` via vendor number — fails because vendor master is now BP. **Root cause**: CVI not synchronized for this vendor account group. **Fix**: run `CVIMC` for vendor account group `LIEF`.
  2. `TP_OTC_007` (output): invoice output not generated — NACE condition records not migrated to Output Management. **Fix**: configure OM channel and template.
  3. `TP_OTC_008` (pricing): custom condition type `ZABC` calculation routine dumps with `CX_SY_OPEN_SQL_DB` in class `ZCL_PRICING_CALC`. **Root cause**: SELECT from `KONV` which is now a compatibility view with changed behavior. **Fix**: rewrite to use pricing API.
  4. `TP_OTC_009` (BP): `KNVP` partner function records missing for some converted customers. **Root cause**: partner determination procedure not assigned in CVI mapping. **Fix**: correct CVI customizing in `SPRO`.
  5. `TP_OTC_012` (revenue): ACDOCA entries missing company code field mapping for custom fields. **Root cause**: BAdI `FINS_ACDOC_CUSTFLD` not implemented. **Fix**: implement the BAdI.

### Fix and re-run dry run #2

All 5 fixes applied. SUM re-run on freshly refreshed sandbox completes in 12.5 hours (11% improvement). Regression: **all 12 tests pass**. ABAP Unit: 47/47 tests pass including new tests for `ZCL_PRICING_CALC`.

### Schedule UAT

UAT scheduled for the week following dry run #3. Sales operations team to execute OTC variants in converted system. Defect tracking via Jira project `ACME-S4`. Sign-off required from VP Sales Operations.

## Anti-patterns

### 1. Skipping cutover rehearsals to "save time"

Without dry runs, the production cutover becomes the first full rehearsal. Cutover timing is unpredictable, defects are discovered in production, and the go/no-go decision has no empirical basis. SAP Activate methodology mandates cutover simulation in the Deploy phase before production cutover ([SAP Community: SAP Project Manager's Guide to SAP Project Cutover](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-project-manager-s-guide-to-sap-project-cutover/ba-p/13510809)). A minimum of 3 dry runs is industry standard for brownfield conversions.

### 2. Relying on UAT alone without automated regression

UAT is manual, slow, and non-repeatable. Each SUM dry run produces a new converted system that must be regression-tested. Without automation, the team cannot realistically re-test after every dry run. Invest in automated regression for processes that will be tested 5+ times across dry runs. Manual UAT is additive — for final validation by business users — not a replacement for automated regression ([SAP Help: Testing in SAP S/4HANA Cloud](https://help.sap.com/docs/SAP_S4HANA_CLOUD/b249d650b15e4b3d9fc2077ee921abd0/a231ac4439e24935b0447bc49e75995c.html)).

### 3. Testing only happy paths

Exception handling and error paths are where simplification items cause the most breakage. A custom error handler that reads from `MKPF` will work on the happy path (where `MATDOC` compatibility views function) but fail on edge cases where the view has different locking or authorization behavior. Always include negative tests: invalid input, authorization failures, exceeded credit limits, missing master data.

### 4. Testing on too-small a data set

Performance regressions only surface at production data volumes. A sandbox with 1,000 sales orders will not reveal that a custom report scanning `VBAP` takes 45 minutes on 5 million rows because an index was dropped during conversion. Always test with production-volume data ([SAP Note 2399707](https://me.sap.com/notes/2399707) — conversion pre-checks emphasize representative data volumes for validation).

### 5. Treating "ATC clean" as "tested"

ATC is static analysis — it checks code syntax and known incompatible patterns. It does NOT exercise runtime behavior. A function module can pass ATC with zero findings yet fail at runtime because of changed database content, authorization behavior, or implicit dependencies on table structures that were restructured. ATC clean is a prerequisite for testing, not a substitute ([SAP Note 2436688](https://me.sap.com/notes/2436688)).

### 6. No defect classification or triage process

Without severity classification (S1-S4) and triage SLAs, all defects are treated equally. This leads to critical blockers sitting in a backlog while cosmetic issues consume developer time. Define triage rules before testing begins, not after the first defect avalanche.

## References

- [SAP Activate Methodology — Roadmap Viewer](https://go.support.sap.com/roadmapviewer/) — test phase deliverables for system conversion projects.
- [SAP Help: Testing in SAP S/4HANA Cloud Public Edition](https://help.sap.com/docs/SAP_S4HANA_CLOUD/b249d650b15e4b3d9fc2077ee921abd0/a231ac4439e24935b0447bc49e75995c.html) — covers Test Automation Tool, Test Data Container, Intelligent Test Scoper, and Post-Upgrade Tests.
- [SAP Help: SAP Cloud ALM for Test Management](https://help.sap.com/docs/cloud-alm/setup-administration/test-management) — test orchestration for SAP Cloud ALM.
- [SAP Help: SAP TDMS](https://help.sap.com/docs/SAP_TDMS) — Test Data Migration Server for sandbox refresh and data anonymization.
- [SAP Note 2399707](https://me.sap.com/notes/2399707) — SAP S/4HANA conversion pre-checks, including data volume validation requirements.
- [SAP Note 1912445](https://me.sap.com/notes/1912445) — Recommended ABAP Test Cockpit (ATC) check variants, including ABAP Unit integration.
- [SAP Note 2436688](https://me.sap.com/notes/2436688) — ATC checks for ABAP custom code migration to S/4HANA.
- [SAP Note 2129147](https://me.sap.com/notes/2129147) — Test Automation Tool for SAP S/4HANA Cloud, Central Note.
- [SAP Note 2265093](https://me.sap.com/notes/2265093) — S/4HANA Business Partner Approach (CVI migration).
- [SAP Note 2270333](https://me.sap.com/notes/2270333) — Material Number Field Length Extension to 40 characters.
- [SAP Note 2270407](https://me.sap.com/notes/2270407) — Universal Journal (ACDOCA) in S/4HANA.
- [SAP Note 2227764](https://me.sap.com/notes/2227764) — Material Documents in MATDOC.
- [SAP Note 1976487](https://me.sap.com/notes/1976487) — S/4HANA Simplification List.
- [SAP Community: SAP Project Manager's Guide to SAP Project Cutover](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-project-manager-s-guide-to-sap-project-cutover/ba-p/13510809) — Greg Baus, October 2021. Covers cutover strategy, simulation, and dress rehearsal aligned to SAP Activate phases.
- [SAP Community: Test Automation Tool for SAP S/4HANA Cloud, Public Edition](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/test-automation-tool-for-sap-s-4hana-cloud-public-edition-a-game-changer-in/ba-p/13566733) — Aniruddh, November 2022. Overview of built-in test automation capabilities.
- [SAP Press: Testing SAP Solutions, 2nd Edition](https://www.sap-press.com/testing-sap-solutions_4950/) — Chapters 3-5 cover test planning, execution, and automation for SAP projects.
- [SAP Help: ABAP Unit](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abenabap_unit.htm) — ABAP Unit framework reference for writing and running unit tests.
