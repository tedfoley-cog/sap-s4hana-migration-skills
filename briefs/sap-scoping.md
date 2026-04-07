## Brief: sap-scoping

**Skill name**: `sap-scoping`
**Phase**: Pre-conversion
**Owner**: Custom code scoping and dead-code elimination prior to S/4HANA conversion.

### Scope of this skill

Procedures for collecting and analyzing custom ABAP code usage data in an ECC production system before a system conversion, with the goal of identifying dead code that can be deleted (and therefore never has to be remediated).

Cover:
- Activating and operating **ABAP Call Monitor (transaction SCMON)** in the production system: how long to collect (≥ 12 months recommended, to capture quarter-end and year-end), data retention, performance impact, security considerations.
- Aggregating SCMON data with **transaction SUSG** (Usage and Procedure Logging aggregator).
- Combining SCMON/SUSG with **Coverage Analyzer (SCOV)** and **Workload Statistics (ST03N)** for cross-validation.
- Loading aggregated usage data into the **Custom Code Migration app** (Fiori app on SAP BTP) or the legacy **SAP Custom Code Lifecycle Management (CCLM)** in Solution Manager.
- Producing a **scope decision** for each custom object: keep / delete / refactor.
- Building **deletion transports** for unused objects so SUM removes them during the conversion.
- Producing the **scoped worklist** that feeds into ATC readiness checks (sibling skill `sap-atc-readiness`).

### Key sources to consult

1. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — section "Custom Code Scoping".
2. SAP Note **2185390** — "Custom Code Migration Worklist".
3. SAP Help Portal: "ABAP Call Monitor (SCMON)" and "Usage and Procedure Logging".
4. SAP Community blog series by **Olga Dolinskaja** on custom code migration.
5. Fiori app: "Custom Code Migration" (BTP-side analysis).

### Key transaction codes / objects to mention

- `SCMON`, `SUSG`, `SCOV`, `ST03N`, `SE80`, `SE38`
- Tables: `/SDF/SCMON_DATA`, `/SDF/CCLM_*`
- Reports: `/SDF/SCMON_AGGREGATE_RUN`

### Worked example to include

Walk through the lifecycle of a fictitious custom report `Z_OLD_SALES_RPT`:
1. SCMON shows 0 calls over 14 months.
2. SUSG confirms no batch jobs reference it.
3. CCLM marks it as a deletion candidate.
4. A deletion transport `<system>K9XXXXX` is created and parked.
5. SUM picks it up during conversion; the report is gone in S/4HANA.

### Anti-patterns to call out

- Running SCMON for less than a full fiscal year (misses month-end/year-end programs).
- Treating SUSG counts of zero as proof of dead code without checking RFC and event-driven entry points.
- Letting SCMON tables grow unbounded (forgetting to schedule aggregation).
- Deleting objects that are referenced only via dynamic calls (`PERFORM ... IN PROGRAM`, `CALL FUNCTION ... DESTINATION`).

### Related skills

`sap-atc-readiness`, `sap-clean-core-extensibility`
