## Brief: sap-atc-readiness

**Skill name**: `sap-atc-readiness`
**Phase**: Pre-conversion
**Owner**: ABAP Test Cockpit checks against the S/4HANA readiness variants, with quick-fix workflow.

### Scope of this skill

Operating the **ABAP Test Cockpit (ATC)** to assess custom ABAP code against S/4HANA simplifications **before** the system conversion, and applying SAP-supplied quick fixes to remediate findings.

Cover:
- Setting up a **central ATC system** running the highest available ABAP release (typically a sandbox S/4HANA system or NetWeaver 7.52+) and registering source systems for **remote ATC**.
- Selecting the right check variant: **`S4HANA_READINESS_2023`**, **`S4HANA_READINESS_2024`**, **`S4HANA_READINESS_2025`** (and the FPS variants like `S4HANA_READINESS_2025_FPS01`).
- Loading the **Simplification Database** content and ensuring it matches the target S/4HANA release.
- Running the check (transaction `ATC` or report `SATC_AC_RUN_VIA_DELTA`) and interpreting the worklist.
- Working through findings in **ABAP Development Tools (ADT) for Eclipse** with **Quick Fixes** (semi-automated corrections) — e.g., field length adjustments, replacing removed function modules.
- Suppressing irrelevant findings via **exemptions** (and the new **Clean Core checks** exemption migration tool — see `SAP/abap-atc-cr-cv-s4hc-tools`).
- Producing a **delta worklist** between two readiness check runs to track remediation progress.

### Key sources to consult

1. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — section "ATC-based Custom Code Migration".
2. SAP Note **2436688** — "ABAP Test Cockpit checks for ABAP custom code migration".
3. SAP Note **1912445** — "Recommended ABAP Test Cockpit check variants".
4. `SAP/abap-atc-cr-cv-s4hc-tools` on GitHub — the official Exemption Migration Tool.
5. SAP Help Portal: "Static Checks with the ABAP Test Cockpit".

### Key transactions / objects

- `ATC`, `ATC_OPS`, `SATC_AC_RUN_VIA_DELTA`, `SE80`, `STC01`
- Programs: `SATC_AC_DOWNLOAD_RESULT`
- Variants: `S4HANA_READINESS_<release>` and `S4HANA_READINESS_<release>_FPS<n>`

### Worked example

Walk through running readiness checks against a fictional `ZCL_CUSTOMER_HELPER`:
1. Central ATC system on S/4HANA 2025 sandbox; source ECC system registered as `ECC_PRD`.
2. Run `S4HANA_READINESS_2025_FPS01` against the development system after loading the latest Simplification Database.
3. Get 7 findings: 3 MATNR length extensions, 2 BP-related function module removals, 2 obsolete data declarations.
4. Open in ADT, apply quick fixes for the 3 MATNR findings automatically; manual rewrite for the BP ones.
5. Re-run delta to confirm 5 findings cleared, 2 remaining for manual remediation.

### Anti-patterns

- Running ATC against the wrong target release (e.g., `S4HANA_READINESS_2023` for a 2025 conversion).
- Forgetting to update the Simplification Database before each run (findings drift silently).
- Mass-suppressing findings via exemptions to "clear the worklist" without remediation.
- Running ATC only locally on the source ECC system without a central ATC on the target release — misses simplifications introduced in newer releases.
- Treating ATC findings as exhaustive: ATC is a static check, dynamic call sites (RTTI, generated code) need separate analysis.

### Related skills

`sap-scoping`, `sap-simplification-database`, `sap-spdd-spau`, `sap-modern-abap-rewrite`
