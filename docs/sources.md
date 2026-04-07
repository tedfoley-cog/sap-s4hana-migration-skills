# Source attribution

This document is the master attribution list for the repo. Every skill cites its sources inline; this file is the union of those citations.

## SAP official documentation

- **SAP Custom Code Migration Guide for S/4HANA 2025 FPS01** — `help.sap.com` (PDF). The canonical runbook for ABAP custom code migration.
- **SAP Help Portal**: `https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE` and the conversion-specific guides.
- **SAP Notes** (cited by note number throughout the skills). Selected key notes:
  - 2185390 — Custom Code Migration Worklist
  - 2241080 — Simplification Database overview
  - 2399707 — Conversion Pre-Checks
  - 2436688 — ATC checks for ABAP custom code migration
  - 1912445 — Recommended ABAP Test Cockpit check variants
  - 1976487 — S/4HANA Simplification List
  - 2265093 — S/4HANA Business Partner Approach
  - 2270333 — Material Number Field Length Extension
  - 2270407 — Universal Journal
  - 2227764 — MATDOC Material Documents
  - 1973241 — SPDD/SPAU adjustments
  - 2882748 — SUM 2.0 SP* Central Note
  - 2393060 — Downtime-Optimized DMO
  - 2351294 — DMO with System Move
  - 2546430 — Migration Cockpit Central Note
  - 1685257 — Fiori Central Note
  - 2659151 — Spaces and Pages in Fiori Launchpad
- **Simplification Item Catalog** — `https://launchpad.support.sap.com/#/sic`
- **SAP Fiori Apps Reference Library** — `https://fioriappslibrary.hana.ondemand.com/`
- **SAP API Business Hub** — `https://api.sap.com/`
- **Maintenance Planner** — `https://maintenanceplanner.cloud.sap`

## SAP open-source code

- [`SAP-samples/abap-cheat-sheets`](https://github.com/SAP-samples/abap-cheat-sheets) — Apache-2.0. Modern ABAP / RAP / CDS reference snippets. Cited from `sap-modern-abap-rewrite` and `sap-hana-performance`.
- [`SAP/abap-cleaner`](https://github.com/SAP/abap-cleaner) — Apache-2.0. 100+ cleanup rules. Cited from `sap-modern-abap-rewrite`.
- [`SAP/abap-atc-cr-cv-s4hc-tools`](https://github.com/SAP/abap-atc-cr-cv-s4hc-tools) — Apache-2.0. Official Clean Core / Exemption Migration Tool. Cited from `sap-atc-readiness` and `sap-clean-core-extensibility`.

## Community sources

Used sparingly and only when authored by SAP employees or recognized SAP MVPs. Always cited with author name and publication date. Examples:

- Olga Dolinskaja — SAP Community blog series on Custom Code Migration and Joule for Developers.
- Karl Kessler — SAP Community blog series on Clean Core extensibility.
- Sergio Guerrero — SAP Community blog series on Fiori activation.

## Fair use policy

- No verbatim copying of SAP-copyrighted documentation longer than ~3 sentences.
- All paraphrased material is clearly attributed.
- The repository does not bundle the SAP Custom Code Migration Guide PDF or any other SAP-licensed document.
- Code snippets adapted from `SAP-samples/abap-cheat-sheets` carry an attribution comment naming the source file and license.

If you are an SAP rights holder and believe a citation here exceeds fair use, please open an issue and we will adjust within 24 hours.
