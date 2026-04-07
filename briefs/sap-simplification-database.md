## Brief: sap-simplification-database

**Skill name**: `sap-simplification-database`
**Phase**: Pre-conversion / planning
**Owner**: Querying and interpreting the Simplification Item Catalog and Simplification Database.

### Scope of this skill

How to navigate and query SAP's authoritative catalog of simplifications between SAP Business Suite (ECC) and S/4HANA — i.e., the list of every changed or removed object that custom code might depend on.

Cover:
- The difference between the **Simplification Item Catalog** (web-facing, on `support.sap.com`) and the **Simplification Database** (the in-system database table loaded into the ATC central system that powers `S4HANA_READINESS_*` checks).
- Loading the Simplification Database into the central ATC system using **SAP Note 2241080** (Simplification Database delivery note) and the matching release-specific notes.
- Querying simplification items by category: **functional**, **data-model**, **UI**, **integration**, **deprecated**.
- Mapping a simplification item to its **SAP Note(s)** for detailed remediation steps.
- Filtering simplifications by **target release** (2023 vs 2024 vs 2025) and by **deployment model** (Cloud Private Edition vs On-Premise vs Cloud Public Edition).
- Cross-referencing **Conversion Pre-Checks** (`/SDF/RC_START_CHECK`) with simplification items so the agent knows which items will block a SUM run.

### Key sources to consult

1. SAP Note **2241080** — "Simplification Database — overview".
2. SAP Note **2399707** — "Conversion Pre-Checks".
3. Simplification Item Catalog (`https://launchpad.support.sap.com/#/sic`) — describe how to navigate it.
4. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — section "Simplification Item Check".
5. SAP Help Portal: "Simplification Database".

### Worked example

Walk through researching the **Business Partner approach** simplification:
1. Search Simplification Item Catalog for "Business Partner".
2. Find the item "Customer/Vendor Integration" with target release S/4HANA 1610+.
3. Open the linked SAP Note (e.g., **2265093**).
4. Identify which custom objects in the worklist (from `sap-atc-readiness`) reference `KNA1` / `LFA1` and need to be repointed at `BUT000`.
5. Hand the worklist to a developer with the simplification context attached.

### Anti-patterns

- Trying to use the Simplification Item Catalog as a code-fix oracle — it tells you *what* changed, not *how* to fix every call site.
- Loading an outdated Simplification Database (gives a false-clear ATC run).
- Ignoring deployment-model filters — a simplification that applies in Cloud Public Edition may not apply in Private Edition.
- Treating the Simplification Database as a one-time load; it gets updated with every Feature Pack Stack and SAP Note.

### Related skills

`sap-atc-readiness`, `sap-functional-simplifications`, `sap-spdd-spau`
