---
name: sap-spdd-spau
description: |
  Use when handling modification adjustment transactions during or after an SAP ECC to S/4HANA
  system conversion: running SPDD to adjust ABAP Dictionary modifications before activation,
  running SPAU to adjust repository object modifications post-conversion, running SPAU_ENH to
  adjust enhancement framework objects, using SE95 (modification browser) to scope the
  modification worklist before SUM begins, resolving "Modification Adjustment" errors in SUM
  log, creating adjustment transports for DEV to QA to PRD propagation, or diagnosing
  performance issues with report RDDIT076 or RDDIT077 during large worklists.
license: Apache-2.0
metadata:
  version: "0.2.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "SAP Conversion Guide for SAP S/4HANA 2025 (help.sap.com)"
    - "SAP Note 1973241 - Adjustments using transactions SPDD/SPAU"
    - "SAP Note 2298737 - SPDD/SPAU performance issues"
    - "SAP Help Portal - Modification Adjustment During Upgrade"
    - "SAP Help Portal - Modification and Enhancement Adjustment Planning (SL Toolset)"
    - "SAP Community - Understanding the need of SPDD, SPAU & SPAU_ENH (patil477pavan, 2020)"
    - "SAP Community - SPDD and SPAU Phases during S/4 HANA Migration (Shakeel_Ahmed1, 2018)"
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
    - "SAP/abap-cleaner (https://github.com/SAP/abap-cleaner)"
related_skills:
  - sap-atc-readiness
  - sap-cli-toolbelt
  - sap-functional-simplifications
  - sap-migration-testing
  - sap-simplification-database
  - sap-sum-dmo
---

## When to use this skill

Invoke this skill when the agent encounters any of the following during an SAP ECC to S/4HANA brownfield system conversion:

- SUM (Software Update Manager) pauses at the **SPDD phase** and requires dictionary modification adjustments before the conversion can proceed.
- Post-conversion, the team must process the **SPAU worklist** to adjust repository object modifications (programs, function modules, screens, classes).
- Enhancement framework objects (BAdI implementations, enhancement spots, source-code plug-ins) need adjustment via **SPAU_ENH**.
- The project needs to **scope modification effort** before the SUM run using transaction **SE95** (Modification Browser).
- Adjustment transports must be created and propagated through the landscape (DEV -> QA -> PRD).
- Performance issues occur during SPDD/SPAU processing with large worklists (report `RDDIT076` or `RDDIT077` slow or timing out).
- The SUM log shows errors related to "Modification Adjustment" or the conversion halts waiting for SPDD completion.

This skill is **not** for custom code remediation (use `sap-atc-readiness` for ATC-based custom code fixes) or for functional simplification items (use `sap-functional-simplifications`). SPDD/SPAU adjusts modifications to *SAP standard* objects; ATC findings address *custom* objects.

## Prerequisites

1. **SUM version**: SUM 2.0 SP 18 or higher installed on the source system. Verify with `SPAM` version display ([SAP Note 2882748](https://me.sap.com/notes/2882748)).
2. **Transport connection**: RFC connection between DEV and the transport domain controller is active. Adjustment transports must be releasable.
3. **Authorization profiles**: The Basis administrator running SPDD needs `S_CTS_ADMI` and `S_TRANSPRT` authorizations. Developers running SPAU need `S_DEVELOP` with change authorization for the relevant packages.
4. **SE95 pre-analysis**: Run transaction `SE95` (Modification Browser) in the source system before starting SUM to inventory all modifications. This gives the team a head count and allows assignment of responsible developers ([SAP Note 1973241](https://me.sap.com/notes/1973241)).
5. **Modification documentation**: Ensure the team has documentation of *why* each modification was made. Without this context, deciding between "Reset to Original" and "Adopt" during SPAU is guesswork.
6. **Performance note applied**: If the system has more than 200 modifications, apply [SAP Note 2298737](https://me.sap.com/notes/2298737) before starting the conversion to avoid SPDD/SPAU performance degradation.

## Quick decision tree

```
Start: SUM conversion running
|
+-- SUM pauses at "SPDD - Modification Adjustment (Dictionary)"?
|   |
|   +-- YES --> Open SPDD in the conversion client
|   |   |
|   |   +-- Object shows "With Modification Assistant"?
|   |   |   +-- YES --> Review the three-way merge proposal
|   |   |   |   +-- Merge correct? --> Accept, save to adjustment transport
|   |   |   |   +-- Merge incorrect? --> Manually edit in SE11, save to transport
|   |   |   +-- NO ("Without Modification Assistant")
|   |   |       +-- Compare old/new versions manually in SE11
|   |   |       +-- Reapply customer change to new SAP version
|   |   |       +-- Save to adjustment transport
|   |   |
|   |   +-- All SPDD objects processed? --> Confirm in SUM --> SUM resumes
|   |
|   +-- NO --> SUM proceeds to activation and import phases
|
+-- SUM completes technical conversion
|
+-- Open SPAU in converted system
|   |
|   +-- Object is an SAP Note reset?
|   |   +-- YES --> "Reset to Original" (SAP Note already applied to new release)
|   |
|   +-- Object is a customer modification still needed?
|   |   +-- YES --> "Adopt" the modification (keep customer version)
|   |
|   +-- Object has a merge conflict?
|   |   +-- YES --> Manual adjustment required
|   |   |   +-- Simple conflict? --> Developer resolves inline
|   |   |   +-- Complex conflict? --> Route to senior developer / functional owner
|   |
|   +-- Object is an enhancement framework object?
|       +-- YES --> Process in SPAU_ENH instead
|
+-- All SPAU / SPAU_ENH objects processed?
    +-- YES --> Release adjustment transport --> Transport to QA --> Regression test
```

## Procedure

### Phase 1: Pre-conversion scoping with SE95

1. Open transaction `SE95` in the source ECC system.
2. Select **Display Modifications** and filter by object type (DDIC objects, programs, screens, etc.).
3. Export the worklist to a spreadsheet. For each modification, document:
   - Object name and type (e.g., table `BSEG`, report `SAPMM06E`)
   - Modification reason (bug fix, custom field, regulatory requirement)
   - Responsible developer
   - Whether the modification is still needed in S/4HANA
4. Classify modifications into categories:
   - **Can be removed**: The modification addressed a bug that SAP has since fixed, or the business process has changed. Plan to "Reset to Original" during SPAU.
   - **Must be preserved**: The modification implements a customer-specific requirement that has no S/4HANA equivalent. Plan to "Adopt" during SPAU.
   - **Needs redesign**: The modification touches objects that no longer exist in S/4HANA (e.g., tables removed by simplification items). These require custom code remediation *before* or *after* conversion, not SPDD/SPAU adjustment. Route to `sap-atc-readiness`.
5. Share the scoping spreadsheet with the Basis team (who will run SPDD) and the development team (who will run SPAU).

> **Tip**: Run report `RDDIT076` to generate the SPDD worklist preview and `RDDIT077` for the SPAU worklist preview. These reports show what SUM will present without actually starting the conversion ([SAP Note 1973241](https://me.sap.com/notes/1973241)).

### Phase 2: SPDD during the SUM conversion (downtime window)

SPDD runs **during** the SUM conversion, after the import phase but **before** dictionary activation. SUM pauses and displays a dialog requesting modification adjustment. This is a mandatory step; it cannot be skipped or deferred ([Conversion Guide for SAP S/4HANA 2025, Section "Modification Adjustment"](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf)).

**Who runs it**: Typically the Basis administrator, since this step occurs during the SUM downtime window. However, a developer familiar with the DDIC modifications should be available (on-call or co-present) to review merge proposals.

1. When SUM pauses, open transaction `SPDD` in the conversion client.
2. The worklist shows all modified ABAP Dictionary objects (domains, data elements, table types, structures, transparent tables, views).
3. For each object, SPDD indicates the adjustment category:

   | Category | Description | Action |
   |---|---|---|
   | **With Modification Assistant** | SAP can propose a three-way merge (original -> modified -> new SAP version). | Review the merge proposal. Accept if correct; manually adjust if not. |
   | **Without Modification Assistant** | No automatic merge possible (e.g., structural changes too large). | Open the object in `SE11`, compare old and new versions manually, reapply the customer modification to the new SAP version. |

4. Save each adjusted object to an **adjustment transport request**. Create a dedicated transport (e.g., `S4HK900001 - SPDD Adjustments Batch 1`) rather than mixing with other changes.
5. After processing all objects, confirm completion in the SUM dialog. SUM resumes dictionary activation ([SAP Note 1973241](https://me.sap.com/notes/1973241)).

> **Critical**: Do not leave SPDD objects unprocessed. SUM will not proceed past the SPDD phase until all objects are either adjusted or explicitly marked as "no adjustment needed." Attempting to skip SPDD and recreate dictionary modifications after activation is significantly harder because dependent objects will already have been activated against the new SAP standard version ([Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf)).

### Phase 3: SPAU after the SUM conversion (post-conversion stabilization)

SPAU runs **after** the technical conversion is complete. Unlike SPDD, SPAU is not a blocking step in SUM; it is a post-conversion activity that can be performed over several days during the stabilization period.

**Who runs it**: Developers, since SPAU adjustments require understanding of ABAP code, screens, and function modules.

1. Open transaction `SPAU` in the converted S/4HANA system.
2. The worklist shows all modified repository objects (reports, function modules, screens, classes, includes, type pools).
3. For each object, determine the appropriate action:

   | Action | When to use | How |
   |---|---|---|
   | **Reset to Original** | The modification was an SAP Note correction that is now part of the new release, or the modification is no longer needed. | Select the object, choose "Reset to Original." The object reverts to the new SAP standard version. |
   | **Adopt** | SAP has automatically preserved the customer modification because it does not conflict with the new version. | Select the object, choose "Adopt." No manual merge is needed. |
   | **Semi-automatic adjustment** | The Modification Assistant can propose a merge. | Review the three-way diff. Accept or adjust the merge result. |
   | **Manual adjustment** | No automatic merge is possible; the modifications conflict with changes SAP made in the new release. | Open the object in `SE38` / `SE80`, compare versions, and manually reapply the customer logic to the new SAP code. |

4. Save all adjustments to an adjustment transport request. Use a separate transport from the SPDD adjustment transport (e.g., `S4HK900002 - SPAU Adjustments Batch 1`).

> **Tip**: Process "Reset to Original" objects first (fastest), then "Adopt" objects, then semi-automatic, and finally manual adjustments. This clears the worklist quickly and lets the team focus effort on the genuinely difficult merges ([SAP Community: "Understanding the need of SPDD, SPAU & SPAU_ENH," patil477pavan, 2020](https://community.sap.com/t5/technology-blog-posts-by-members/understanding-the-need-of-spdd-spau-amp-spau-enh-in-upgrade/ba-p/13540328)).

### Phase 4: SPAU_ENH for enhancement framework objects

SPAU_ENH handles adjustment of enhancement framework objects that are not covered by standard SPAU. This includes:

- BAdI implementations (classic and new BAdIs)
- Enhancement spots and enhancement implementations
- Source-code plug-ins (implicit and explicit enhancements)

1. Open transaction `SPAU_ENH` in the converted system.
2. Review each enhancement object. The adjustment logic is similar to SPAU:
   - If the enhancement hook point has changed in the new release, the implementation must be adapted.
   - If the enhancement is no longer relevant (e.g., the enhanced program was replaced by a new S/4HANA application), mark it for removal.
3. Save adjustments to the same or a separate adjustment transport.

> **Note**: SPAU_ENH was introduced to address a gap where classic SPAU did not properly handle enhancement framework objects. Always check SPAU_ENH even if SPAU shows zero items; there may be enhancement-only adjustments ([Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf)).

### Phase 5: Adjustment transport propagation

1. After all SPDD, SPAU, and SPAU_ENH adjustments are saved to transport requests, **release** the transports in the development system.
2. Import the adjustment transports into QA in the correct order:
   - SPDD transport first (dictionary objects must be activated before dependent repository objects).
   - SPAU transport second.
   - SPAU_ENH transport third (if separate).
3. In QA, verify that the adjustments are correctly applied. Run a basic smoke test of the modified objects.
4. After QA validation, import the transports into PRD during the production conversion.

> **Critical**: If adjustment transports are not created, the adjustments exist only in the development system and will be lost on the next system refresh or copy. Always create and release adjustment transports ([SAP Note 1973241](https://me.sap.com/notes/1973241)).

### Phase 6: Handling performance issues

For systems with a large number of modifications (500+), SPDD and SPAU processing can be slow. Apply the following mitigations:

1. Apply [SAP Note 2298737](https://me.sap.com/notes/2298737) before starting the conversion. This note contains performance optimizations for reports `RDDIT076` and `RDDIT077`.
2. Increase the dialog work process timeout (`rdisp/max_wprun_time`) temporarily during the SPDD phase if adjustments take longer than the default timeout.
3. Process SPAU objects in batches by filtering on package or object type rather than loading the entire worklist at once.
4. If `RDDIT076` or `RDDIT077` time out during pre-conversion scoping, run them in background mode (`SM37`) with a spool output.


### CLI usage

Use `sapcli` to download modified objects for offline review and `abap-cleaner` for post-adjustment cleanup.

**Environment variables**:
- `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD` (for sapcli)

**Network prerequisites**: SAP HTTPS port (typically 443 or 44300).

```bash
# Download a modified program for offline diff / review
sapcli checkout program sapmm06e ./spau-review

# After SPAU adjustment, clean up the adjusted source with abap-cleaner
java -jar abap-cleaner.jar \
  --sourcefile ./spau-review/sapmm06e.abap \
  --targetfile ./spau-review/sapmm06e_cleaned.abap \
  --profile profiles/team-profile.cfg

# Compare the cleaned output against the adjusted version
diff -u ./spau-review/sapmm06e.abap ./spau-review/sapmm06e_cleaned.abap
```

This workflow lets Devin assist with SPAU review by downloading, cleaning, and diffing objects without requiring SAP GUI access ([sapcli README](https://github.com/jfilak/sapcli), [abap-cleaner](https://github.com/SAP/abap-cleaner)).

> **Cross-reference**: For a full catalog of CLIs available in the Devin sandbox, see skill `sap-cli-toolbelt`.

## Worked example

**Scenario**: S/4HANA 2025 conversion of a manufacturing ECC 6.0 EHP8 system with 47 DDIC modifications and 189 repository modifications identified via `SE95`.

See [worked-example-spdd-spau-manufacturing.md](references/worked-example-spdd-spau-manufacturing.md) for the full 4-step walkthrough covering SE95 scoping, SPDD processing during SUM downtime, SPAU triage (including manual conflict examples), and transport propagation.

**Key outcome**: 47 DDIC objects processed in 3 hours (34 resets, 11 auto-merges, 2 manual). 189 SPAU objects triaged: 94 resets, 56 adopts, 27 semi-auto merges, 12 manual conflicts routed to developers.

## Anti-patterns

### 1. Skipping SPDD because "we'll do it later"

SUM will **not** proceed past the SPDD phase until all dictionary modifications are processed. There is no "skip and come back" option. If the Basis team is unprepared, the entire conversion stalls during the downtime window. Furthermore, attempting to recreate dictionary modifications after activation is significantly harder because dependent objects (programs, views, lock objects) will have been activated against the new SAP standard structure. Always complete SPDD scoping via SE95 *before* starting SUM ([Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf)).

### 2. Not creating adjustment transports

If SPDD/SPAU adjustments are saved without assigning them to a transport request, they exist only in the development client. On the next system refresh, client copy, or production conversion, these adjustments are lost and must be redone. Always create dedicated adjustment transports and release them promptly ([SAP Note 1973241](https://me.sap.com/notes/1973241)).

### 3. Marking everything in SPAU as "Adopt" without reviewing

"Adopt" tells the system to keep the customer's modified version of the object. If the modification was a workaround for a bug that SAP has fixed in the new release, adopting it silently preserves obsolete or potentially broken code. Always check whether the modification reason still applies before choosing "Adopt." Prefer "Reset to Original" when the original modification reason is no longer valid.

### 4. Confusing SPAU with the Custom Code Migration worklist

SPAU adjusts modifications to **SAP standard** objects (objects in SAP namespaces that the customer modified via access keys). The Custom Code Migration worklist (driven by ATC checks) addresses **customer-developed** objects (objects in Z/Y namespaces or customer namespaces). These are orthogonal workflows. A modification to `SAPMM06E` (SAP program) goes through SPAU; a custom report `ZMM_PURCHASE_REPORT` goes through ATC. Mixing them up causes objects to be missed or double-processed. See `sap-atc-readiness` for the custom code workflow.

### 5. Running SPDD without a developer on standby

The Basis administrator running SPDD during the SUM downtime window may not have the functional knowledge to evaluate merge proposals for complex DDIC objects. If a merge proposal is incorrect and accepted anyway, the resulting data structure mismatch can cause activation errors or data corruption downstream. Always have a developer familiar with the modifications available during the SPDD window, even if they are on-call rather than physically co-present.

### 6. Ignoring SPAU_ENH

Teams often process SPDD and SPAU but forget to check `SPAU_ENH`. Enhancement framework objects (BAdI implementations, enhancement spots) are not shown in standard SPAU. If SPAU_ENH is skipped, these enhancements may silently fail or produce incorrect results in the converted system ([Conversion Guide for SAP S/4HANA 2025](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf)).

## References

1. **SAP Conversion Guide for SAP S/4HANA 2025** - Section "Modification Adjustment": Describes SPDD, SPAU, and SPAU_ENH as the standard adjustment transactions during system conversion. Confirms SPDD is mandatory during conversion; SPAU/SPAU_ENH are post-conversion. ([PDF on help.sap.com](https://help.sap.com/doc/2b87656c4eee4284a5eb89ab84fa8ca4/2025.000/en-US/ConversionGuide_S4HANA.pdf))

2. **[SAP Note 1973241](https://me.sap.com/notes/1973241)** - "Adjustments using transactions SPDD/SPAU": Central note covering the modification adjustment process, including worklist generation via `RDDIT076`/`RDDIT077`, transport handling, and recommended workflow order.

3. **[SAP Note 2298737](https://me.sap.com/notes/2298737)** - "SPDD/SPAU performance issues": Contains performance fixes for `RDDIT076` and `RDDIT077` reports. Apply before conversion if the system has a large number of modifications.

4. **[SAP Note 2882748](https://me.sap.com/notes/2882748)** - "SUM 2.0 Central Note": Documents SUM phases including the SPDD modification adjustment phase timing within the overall conversion sequence.

5. **[SAP Help Portal: Modification Adjustment During Upgrade](https://help.sap.com/docs/SUPPORT_CONTENT/sl/3354980603.html)** - SAP Support Content wiki page explaining the SPDD/SPAU process in the context of SUM-based upgrades and conversions.

6. **[SAP Help Portal: Modification and Enhancement Adjustment Planning](https://help.sap.com/docs/SLTOOLSET)** - SL Toolset documentation covering pre-conversion planning for modification adjustments, including SE95 usage and worklist estimation.

7. **[SAP Note 2270333](https://me.sap.com/notes/2270333)** - "Material Number Field Length Extension": Documents native MATNR length extension in S/4HANA, relevant for SPDD adjustment of customer MATNR domain modifications.

8. **SAP Community: "Understanding the need of SPDD, SPAU & SPAU_ENH in SAP Upgrade Project"** (patil477pavan, September 2020) - Community blog explaining the three transactions, their sequencing, and practical tips for processing order. ([community.sap.com](https://community.sap.com/t5/technology-blog-posts-by-members/understanding-the-need-of-spdd-spau-amp-spau-enh-in-upgrade/ba-p/13540328))

9. **SAP Community: "SPDD and SPAU Phases during S/4 HANA Migration"** (Shakeel_Ahmed1, January 2018) - Community blog on SPDD/SPAU sequencing specific to S/4HANA conversion scenarios. ([community.sap.com](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/spdd-and-spau-phases-during-s-4-hana-migration/ba-p/13364097))

10. **[SAP Note 2399707](https://me.sap.com/notes/2399707)** - "Conversion Pre-Checks": Documents pre-checks that should be run before starting SUM, including modification inventory validation.
