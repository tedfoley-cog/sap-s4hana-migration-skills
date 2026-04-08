---
name: sap-scoping
description: |
  Use when scoping custom ABAP code prior to an SAP ECC to S/4HANA system
  conversion: collecting usage data with transaction SCMON or SUSG, identifying
  dead code in production, building deletion transports for unused custom
  objects, producing a scoped worklist before running ATC readiness checks,
  or operating the Custom Code Migration Fiori app on SAP BTP.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "SAP Custom Code Migration Guide for SAP S/4HANA 2025 FPS01 (help.sap.com PDF)"
    - "SAP Note 2185390 — Custom Code Migration Worklist"
    - "SAP Note 2436688 — Custom Code Check Variants for S/4HANA"
    - "SAP Help Portal — ABAP Call Monitor (SCMON) Usage Data Collection"
    - "SAP Help Portal — Aggregating Usage Data (SUSG)"
    - "SAP Help Portal — SAP Solution Manager Custom Code Management"
    - "SAP Community — Olga Dolinskaja, ABAP Call Monitor (SCMON) blog series"
    - "SAP Community — Olga Dolinskaja, Aggregate usage data blog"
    - "SAP Note 2399707 — Custom Code Migration Pre-Checks"
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
related_skills:
  - sap-atc-readiness
  - sap-clean-core-extensibility
  - sap-cli-toolbelt
  - sap-simplification-database
---

## When to use this skill

Invoke this skill when you need to:

- Plan or execute **custom code scoping** before an SAP ECC to S/4HANA system conversion.
- Activate, configure, or troubleshoot the **ABAP Call Monitor (SCMON)** in a production ECC system.
- Aggregate usage data with **transaction SUSG** (Usage and Procedure Logging).
- Cross-validate usage data with **Coverage Analyzer (SCOV)** or **Workload Statistics (ST03N)**.
- Load usage data into the **Custom Code Migration** Fiori app on SAP BTP or into **SAP Solution Manager CCLM**.
- Produce a **scope decision** (keep / delete / refactor) for each custom object.
- Build **deletion transports** that SUM will pick up during the technical conversion.
- Generate a **scoped worklist** to feed into ATC readiness checks (see sibling skill `sap-atc-readiness`).

This skill does **not** cover ATC check execution (use `sap-atc-readiness`), simplification item analysis (use `sap-simplification-database`), or clean-core extensibility strategy (use `sap-clean-core-extensibility`).

## Prerequisites

1. **SAP Basis level**: The source ECC system must be on SAP NetWeaver 7.40 SP08 or higher to use SCMON. Earlier releases support only UPL (Usage and Procedure Logging) via transaction `SUSG` ([SAP Help: Usage Data Collection](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/616e28917b3c4f18a14e6e5fa0f6b104.html)).
2. **Authorization**: Users activating SCMON require authorization object `S_DEVELOP` with activity 02 (change) and the object type `PROG`. Aggregation via SUSG requires `S_SDF_CMON` ([SAP Help: Aggregating Usage Data](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/e5d2b36e86561014b652e368a2828b24.html)).
3. **Production system access**: SCMON must run in the production client where real business processes execute; sandbox or QA data is not representative ([SAP Custom Code Migration Guide for S/4HANA 2025, Section "Custom Code Scoping"](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf)).
4. **Sufficient collection period**: SAP recommends collecting usage data for **at least 12 months** to capture all periodic programs including month-end, quarter-end, and year-end jobs ([SAP Note 2185390](https://me.sap.com/notes/2185390)).
5. **BTP subaccount** (optional): If using the Custom Code Migration Fiori app, a BTP subaccount with the ABAP environment entitlement is needed. Alternatively, SAP Solution Manager 7.2 SP10+ with CCLM is supported for on-premise analysis.

## Quick decision tree

```
Is your ECC system on NW 7.40 SP08+?
├── YES → Activate SCMON in production (Step 1)
│         Has SCMON been running ≥ 12 months?
│         ├── YES → Aggregate with SUSG (Step 2) → Load into CCM app (Step 4)
│         └── NO  → Start SCMON now; use ST03N/UPL as interim data while SCMON collects
└── NO  → Use UPL via SUSG only (limited granularity)
          Cross-validate with ST03N workload statistics

Do you have SAP BTP access?
├── YES → Use Custom Code Migration Fiori app for analysis (Step 4a)
└── NO  → Use SAP Solution Manager CCLM (Step 4b) or manual SE16 analysis

For each custom object, decide:
├── SCMON calls = 0 AND SUSG calls = 0 AND no dynamic references → DELETE
├── SCMON calls > 0 but object has S/4HANA incompatibilities    → REFACTOR
└── SCMON calls > 0 and object is S/4HANA compatible            → KEEP
```

## Procedure

### Step 1 — Activate ABAP Call Monitor (SCMON) in production

SCMON records which ABAP programs or procedures are called by which transactions, programs, or services at runtime. It operates at the ABAP kernel level with minimal overhead ([SAP Help: Usage Data Collection](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/616e28917b3c4f18a14e6e5fa0f6b104.html)).

1. Log on to the **production** system client.
2. Execute transaction **`SCMON`**.
3. In the *Recording Settings* screen:
   - Set **Recording Scope** to `All Custom Code` (namespace `/Y*`, `/Z*`, and customer namespace).
   - Set **Granularity** to `Procedure Level` to capture individual function module, method, and form routine calls ([SAP Community: Olga Dolinskaja — ABAP Call Monitor (SCMON)](https://community.sap.com/t5/application-development-blog-posts/abap-call-monitor-scmon-analyze-usage-of-your-code/ba-p/13399804)).
   - Enable **Cross-Client Recording** if business processes run in multiple clients.
4. Click **Activate Recording**.
5. Verify activation via report `/SDF/SCMON_ADMIN` or by checking that table `/SDF/SCMON_DATA` is receiving entries.

**Performance impact**: SCMON runs at the ABAP kernel level and adds negligible overhead (typically < 1% CPU). However, the raw data table `/SDF/SCMON_DATA` can grow significantly in high-volume systems. Schedule regular aggregation (Step 2) to keep table sizes manageable ([SAP Note 2185390](https://me.sap.com/notes/2185390)).

**Security considerations**: SCMON does not record business data content — only the names of called ABAP objects and calling contexts. No personal data is captured. Still, restrict access to SCMON configuration to Basis administrators using authorization object `S_SDF_CMON`.

### Step 2 — Aggregate usage data with SUSG

Transaction SUSG aggregates raw SCMON recording data into summarized usage statistics, reducing data volume and making the data consumable by downstream tools ([SAP Help: Aggregating Usage Data](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/e5d2b36e86561014b652e368a2828b24.html)).

1. Execute transaction **`SUSG`** in the production system.
2. Select the time period to aggregate (e.g., last month).
3. Run the aggregation. This populates the `/SDF/CCLM_*` tables with summarized call counts per object.
4. **Schedule periodic aggregation**: Set up a background job to run report `/SDF/SCMON_AGGREGATE_RUN` monthly. This prevents the raw `/SDF/SCMON_DATA` table from growing unbounded ([SAP Community: Olga Dolinskaja — Aggregate usage data](https://community.sap.com/t5/application-development-blog-posts/aggregate-usage-data-in-your-production-system-with-transaction-susg/bc-p/13399026)).
5. After aggregation, the raw data can optionally be archived or deleted to free database space.

### Step 3 — Cross-validate with SCOV and ST03N

SCMON records online and batch calls, but some entry points may be missed — particularly RFC destinations called from external systems and event-driven calls. Cross-validation reduces false negatives.

- **Coverage Analyzer (SCOV)**: Run `SCOV` to perform static code coverage analysis. SCOV identifies code paths that are structurally unreachable, complementing SCMON's runtime data. Use `SCOV` results to confirm that objects with zero SCMON calls also have no reachable entry points ([SAP Help: ABAP Test and Analysis Tools](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/4ec3f2306e391014adc9fffe56f3f67d.html)).
- **Workload Statistics (ST03N)**: Check `ST03N` → *Expert Mode* → *Transaction Profile* for the time period matching your SCMON collection. Look for custom transactions (Z*/Y*) that show workload but might not appear in SCMON if recording was interrupted ([SAP Help: Workload Statistics](https://help.sap.com/docs/ABAP_PLATFORM_NEW/b5670aaaa2364a29935f40b16499972d/4fe11e3e3fbc7e6ce10000000a42189b.html)).
- **RFC usage**: Query table `RFCDES` (transaction `SM59`) to identify RFC destinations that call custom function modules. Cross-reference with SCMON data — if a function module has zero SCMON calls but is registered as an RFC destination, it may still be in use by external systems.
- **Batch job cross-check**: Use transaction `SM37` to list all active batch jobs. Check whether any reference custom programs (Z*/Y*) that SCMON reports as unused. Batch jobs that run less frequently than yearly (e.g., only during audits) may not appear in a 12-month SCMON window.

### Step 4 — Load data into analysis tools

#### Step 4a — Custom Code Migration Fiori app (BTP)

The Custom Code Migration app is a Fiori application running on SAP BTP that combines SCMON/SUSG usage data with ATC findings and simplification item checks to produce a unified migration worklist ([SAP Note 2185390](https://me.sap.com/notes/2185390)).

1. Set up a **communication arrangement** in BTP pointing to the source ECC system as the object provider.
2. Configure a second communication arrangement pointing to the system where custom code resides (may be the same system).
3. Upload aggregated SUSG data via the app's data import function.
4. The app automatically cross-references usage data with the S/4HANA simplification database and ATC check results.
5. Review the unified worklist: each custom object is tagged with usage count, S/4HANA compatibility status, and recommended action.

#### Step 4b — SAP Solution Manager CCLM (on-premise)

If BTP is not available, use Custom Code Lifecycle Management (CCLM) in SAP Solution Manager 7.2 SP10+ ([SAP Help: Custom Code Management](https://help.sap.com/docs/SAP_Solution_Manager/4fc8d03390c342da8a60f8ee387bca1a/1f97b4d3ecbe4a94b60b3e5f738e4a77.html)).

1. In Solution Manager, navigate to *Custom Code Management* → *Data Collection*.
2. Connect to the managed ECC system and pull SCMON/SUSG aggregated data.
3. CCLM merges usage data with ATC findings and simplification items.
4. Use the *Analysis* view to filter by usage status (used / unused / unclear).

### Step 5 — Produce scope decisions

For each custom object in the worklist, apply the following decision logic:

| Usage (SCMON+SUSG) | S/4HANA compatible? | Dynamic refs? | Decision |
|---|---|---|---|
| 0 calls, ≥ 12 months | N/A | None found | **Delete** |
| 0 calls, ≥ 12 months | N/A | Yes (RFC/dynamic CALL) | **Investigate** — do not delete until dynamic references are resolved |
| > 0 calls | Yes | N/A | **Keep** as-is |
| > 0 calls | No (ATC findings) | N/A | **Refactor** — feed to `sap-atc-readiness` |
| 0 calls, < 12 months | N/A | N/A | **Defer** — extend SCMON collection period |

Key checks before marking an object for deletion:

- Search for dynamic call patterns: `CALL FUNCTION <variable>`, `PERFORM <form> IN PROGRAM <variable>`, `CALL METHOD (<classname>)=>` ([SAP Note 2399707](https://me.sap.com/notes/2399707)).
- Check `WHERE-USED` list in `SE80` for cross-references from other custom objects.
- Search table `TRDIRT` for program descriptions that indicate periodic or event-driven use.
- Confirm the object is not referenced in any active **workflow** (transaction `SWI1`) or **BAdI implementation** (transaction `SE18`/`SE19`).

### Step 6 — Build deletion transports

1. In the development system, open transaction **`SE80`** or **`SE38`**.
2. For each object confirmed for deletion, delete the object and assign it to a **dedicated transport request** (e.g., `<system-id>K9XXXXX`). Use a single transport or a small set grouped by package.
3. **Important**: Do not release the transport yet. Park it so that SUM/DMO can pick it up during the conversion phase. The transport is imported into the target S/4HANA system as part of the SUM conversion process, ensuring deleted objects are never migrated ([SAP Custom Code Migration Guide for S/4HANA 2025, Section "Deletion Transports"](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf)).
4. Document the deletion transport numbers and include them in the SUM configuration stack XML.
5. Review the transport contents with transaction `SE09`/`SE10` before handoff to the Basis team.

### Step 7 — Produce the scoped worklist for ATC

The final output of scoping is a **worklist of custom objects that will be kept** and therefore must pass ATC readiness checks in the target S/4HANA release.

1. Export the "Keep" and "Refactor" objects from the Custom Code Migration app (or CCLM) as a CSV or transport-based object list.
2. This list becomes the input for the sibling skill `sap-atc-readiness`, which runs the S/4HANA-specific ATC check variant (e.g., `/SDF/S4_HANA_READINESS_2025`) against only the in-scope objects ([SAP Note 2436688](https://me.sap.com/notes/2436688)).
3. By scoping first, you dramatically reduce the ATC worklist — typically by 30–60% in systems with significant dead code — and avoid wasting remediation effort on objects that will be deleted.


### CLI usage

When Devin has network access to the SAP system, use `sapcli` to automate package-level source inspection during scoping.

**Environment variables** (must be configured as Devin secrets):
- `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD`

**Network prerequisites**: SAP system HTTPS port (typically 443 or 44300) must be reachable.

```bash
# List all objects in a custom package
sapcli package list '$Z_CUSTOM_PKG' --recursive

# Download a specific class for offline analysis
sapcli checkout class zcl_customer_helper

# Download an entire package tree for grep / static analysis
sapcli checkout package '$Z_CUSTOM_PKG' ./scoping-export --recursive
```

Use the exported source to build the scoped worklist before feeding it to ATC (see `sap-atc-readiness`). This avoids manual SE80 navigation and scales to thousands of objects ([sapcli README](https://github.com/jfilak/sapcli)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

**Scenario**: Fictitious company *Meridian Industries* scopes 4,200 custom ABAP objects for an ECC 6.0 EHP8 → S/4HANA 2025 conversion using SCMON, SUSG, and the Custom Code Migration app.

See [worked-example-meridian-scoping.md](references/worked-example-meridian-scoping.md) for the full 7-step walkthrough covering SCMON data review, SUSG confirmation, cross-validation, scope decision, and deletion transport.

**Key outcome**: Meridian identifies 1,890 objects (45%) as unused. Deleting them before conversion reduces the ATC remediation worklist by 39%.

## Anti-patterns

### 1. Running SCMON for less than a full fiscal year

**Why it is wrong**: Many custom programs execute only during specific fiscal periods — month-end closings (FAGLB03, F.01), year-end settlement runs (AJAB, AJRW), or annual audit reports. A 6-month SCMON window will miss programs that run only at year-end, leading to false deletion candidates. SAP explicitly recommends a minimum of 12 months of collection ([SAP Note 2185390](https://me.sap.com/notes/2185390)).

**Consequence**: Deleting a year-end report causes a production outage during the first fiscal year close on S/4HANA.

### 2. Treating zero SUSG counts as proof of dead code without checking dynamic entry points

**Why it is wrong**: SCMON and SUSG track static call chains — they record when program A calls subroutine B. But dynamic calls such as `PERFORM <form> IN PROGRAM (lv_progname)`, `CALL FUNCTION lv_funcname DESTINATION lv_rfc_dest`, or `SUBMIT (lv_report)` resolve the target at runtime and may not appear in SCMON data if the calling program was not executed during the collection period with those specific variable values ([SAP Note 2399707](https://me.sap.com/notes/2399707)).

**Consequence**: Deleting a dynamically-called function module breaks the calling program at runtime with a `CALL_FUNCTION_NOT_FOUND` short dump.

### 3. Letting SCMON tables grow unbounded

**Why it is wrong**: The raw data table `/SDF/SCMON_DATA` grows with every recorded call. In high-volume production systems (e.g., 10,000+ dialog users), this table can reach tens of gigabytes within months if aggregation is not scheduled. This degrades database performance and increases backup times ([SAP Community: Olga Dolinskaja — Aggregate usage data](https://community.sap.com/t5/application-development-blog-posts/aggregate-usage-data-in-your-production-system-with-transaction-susg/bc-p/13399026)).

**Mitigation**: Schedule report `/SDF/SCMON_AGGREGATE_RUN` as a monthly background job (via `SM36`). After aggregation, the raw data can be archived or deleted, while the aggregated statistics in `/SDF/CCLM_*` tables are retained.

### 4. Deleting objects referenced only via dynamic calls

**Why it is wrong**: Standard `WHERE-USED` in SE80 does not find dynamic references like `CALL FUNCTION variable`. Before deleting any function module or report with zero SCMON calls, search the entire custom code base for string patterns that could dynamically reference the object. Use ABAP search tools or `SE38` → `Find in Source Code` with pattern `'Z_<object_name>'` across all Z/Y programs ([SAP Custom Code Migration Guide for S/4HANA 2025](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf)).

**Consequence**: Runtime short dumps (`CALL_FUNCTION_NOT_FOUND`, `PERFORM_NOT_FOUND`, `SUBMIT_REPORT_NOT_FOUND`) in production.

### 5. Scoping in a non-production system

**Why it is wrong**: Usage data from QA, sandbox, or development systems does not reflect real business process execution patterns. Testers do not run year-end closes on the same schedule as production, and many custom programs are never executed in QA. Scoping decisions based on non-production data will identify actively-used programs as dead code ([SAP Custom Code Migration Guide for S/4HANA 2025, Section "Custom Code Scoping"](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf)).

### 6. Skipping the scoping step entirely

**Why it is wrong**: Without scoping, the ATC readiness check (sibling skill `sap-atc-readiness`) runs against all custom objects, including dead code. This inflates the remediation worklist, wastes developer effort on objects that will never execute in S/4HANA, and extends project timelines. Industry benchmarks show 30–60% of custom code in mature ECC systems is unused ([SAP Note 2185390](https://me.sap.com/notes/2185390)).

## References

### SAP Official Documentation

- [SAP Custom Code Migration Guide for SAP S/4HANA 2025 FPS01](https://help.sap.com/doc/9dcbc5e47ba54a5cbb509a82e0319406/2025.001/en-US/CustomCodeMigration_Guide_2025.pdf) — Canonical runbook for custom code scoping and migration. Sections on SCMON activation, SUSG aggregation, scope decisions, and deletion transports.
- [SAP Help: Usage Data Collection (SCMON)](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/616e28917b3c4f18a14e6e5fa0f6b104.html) — Official documentation for the ABAP Call Monitor transaction.
- [SAP Help: Aggregating Usage Data (SUSG)](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ba8d2f117c1c41a6b1ff35e42a7d33ee/e5d2b36e86561014b652e368a2828b24.html) — Official documentation for the Usage and Procedure Logging aggregator.
- [SAP Help: SAP Solution Manager — Custom Code Management](https://help.sap.com/docs/SAP_Solution_Manager/4fc8d03390c342da8a60f8ee387bca1a/1f97b4d3ecbe4a94b60b3e5f738e4a77.html) — CCLM documentation for on-premise analysis.

### SAP Notes

- [SAP Note 2185390](https://me.sap.com/notes/2185390) — Custom Code Migration Worklist. Defines the recommended scoping approach, minimum collection periods, and worklist structure.
- [SAP Note 2436688](https://me.sap.com/notes/2436688) — Custom Code Check Variants for S/4HANA. Defines the ATC check variants used after scoping.
- [SAP Note 2399707](https://me.sap.com/notes/2399707) — Custom Code Migration Pre-Checks. Covers dynamic call detection and pre-check procedures.

### SAP Community

- [Olga Dolinskaja — ABAP Call Monitor (SCMON) – Analyze usage of your code](https://community.sap.com/t5/application-development-blog-posts/abap-call-monitor-scmon-analyze-usage-of-your-code/ba-p/13399804) — Detailed walkthrough of SCMON activation and configuration.
- [Olga Dolinskaja — Aggregate usage data in your production system with transaction SUSG](https://community.sap.com/t5/application-development-blog-posts/aggregate-usage-data-in-your-production-system-with-transaction-susg/bc-p/13399026) — SUSG aggregation procedures and scheduling.

### Key Transaction Codes

| Transaction | Purpose |
|---|---|
| `SCMON` | ABAP Call Monitor — activate, configure, and review usage recordings |
| `SUSG` | Usage and Procedure Logging — aggregate SCMON data |
| `SCOV` | Coverage Analyzer — static code coverage analysis |
| `ST03N` | Workload Statistics — cross-validate transaction usage |
| `SE80` | Object Navigator — where-used lists and object management |
| `SE38` | ABAP Editor — program deletion and source code search |
| `SM37` | Background Job Overview — verify batch job references |
| `SM59` | RFC Destinations — check external system call references |
| `SE09`/`SE10` | Transport Organizer — manage deletion transports |

### Key Tables

| Table | Purpose |
|---|---|
| `/SDF/SCMON_DATA` | Raw SCMON recording data |
| `/SDF/CCLM_*` | Aggregated usage statistics from SUSG |
| `TADIR` | Object directory — all repository objects |
| `TRDIRT` | Program text descriptions |
| `RFCDES` | RFC destination definitions |
