## Brief: sap-migration-testing

**Skill name**: `sap-migration-testing`
**Phase**: Validation (runs alongside every other phase)
**Owner**: Test strategy for an ECC → S/4HANA conversion.

### Scope of this skill

How to plan, execute, and automate testing for an ECC → S/4HANA conversion. This is the safety net under everything: scoping, ATC, SPDD/SPAU, SUM, functional simplifications, performance.

Cover:
- The **test pyramid** for an SAP migration:
  - **ABAP Unit tests** for custom code (low cost, high coverage).
  - **ATC checks** as static analysis (already covered in `sap-atc-readiness`, this skill cross-references).
  - **Functional process tests** — end-to-end business process validation (Order-to-Cash, Procure-to-Pay, Record-to-Report).
  - **Regression test packs** delivered by SAP via **SAP Application Interface Framework** or third-party (Tricentis Tosca, Worksoft, Panaya).
  - **Performance tests** with realistic data volumes on the target HANA database.
  - **Cutover dry runs** — full-rehearsal of the SUM cutover in a sandbox.
- **Test data management**: refreshing the sandbox with production-like data (using TDMS or third parties) and what to anonymize.
- **Cutover rehearsal**: typically 3 dry runs at minimum before go-live, each progressively more complete.
- **User Acceptance Testing (UAT)**: how to scope, who runs it, defect-tracking conventions.
- **Automated regression**: when it's worth investing (long brownfield projects), when it isn't (small landscapes).
- **Hypercare** post-go-live: monitoring patterns, defect triage, the first month-end close.

### Key sources to consult

1. SAP Help Portal: "Test Suite for SAP Solution Manager".
2. SAP Note **2298054** — "Test Automation for SAP S/4HANA".
3. openSAP course: "Testing SAP S/4HANA Conversion Projects" (cite course title and unit).
4. SAP Activate methodology — Test phase deliverables.
5. SAP Press: "Testing SAP Solutions" (cite by chapter only).

### Worked example

Walk through the Order-to-Cash regression validation for a fictional retailer's brownfield conversion:
1. Identify in-scope process variants: standard sale, returns, intercompany, third-party drop-ship.
2. Build 12 test scripts in Solution Manager Test Suite, parameterized by sales org and material type.
3. Refresh sandbox with anonymized production data (T-3 months).
4. Run scripts pre-conversion → baseline pass/fail.
5. Run SUM dry-run #1 → re-run scripts → 5 failures (3 due to BP-related custom code, 2 due to MATNR length truncation in an interface).
6. Fix, re-run SUM dry-run #2, scripts pass.
7. Schedule UAT with the sales operations team for the next dry run.

### Anti-patterns

- Skipping cutover rehearsals to "save time" — go-live then becomes the first full rehearsal (recipe for disaster).
- Relying on UAT alone without an automated regression layer for repeated dry runs.
- Testing only happy paths — exception handling and error paths are where simplifications bite hardest.
- Testing on too-small a data set; performance regressions only appear at production volume.
- Treating "ATC clean" as "tested" — ATC is static analysis and does not exercise behavior.

### Related skills

`sap-sum-dmo`, `sap-spdd-spau`, `sap-functional-simplifications`, `sap-hana-performance`
