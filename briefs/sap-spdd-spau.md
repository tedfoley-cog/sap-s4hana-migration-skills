## Brief: sap-spdd-spau

**Skill name**: `sap-spdd-spau`
**Phase**: Conversion / post-technical-conversion
**Owner**: Modification adjustment workflows after a system conversion.

### Scope of this skill

How to handle the post-upgrade adjustment transactions that SUM hands you after a system conversion: **SPDD** (dictionary modifications), **SPAU** (repository modifications), and **SPAU_ENH** (enhancement adjustments).

Cover:
- The order in which these transactions run during a SUM run: SPDD is mandatory **during** the conversion (before activation); SPAU and SPAU_ENH are post-conversion.
- How to handle each category in **SPDD**: "with modification assistant" (semi-automatic) vs "without modification assistant" (manual adjustment in SE11).
- How to handle each category in **SPAU**: SAP Notes that reset modifications, customer adjustments, automatic adjustments, manual adjustments.
- **SPAU_ENH** for enhancement framework objects (BAdI implementations, enhancement spots, source-code plug-ins).
- Producing **adjustment transports** that travel forward through the landscape (DEV → QA → PRD).
- Using **modification browser (SE95)** to scope the work before SUM hands you the worklist.
- Collaboration model: who runs SPDD (typically a Basis admin during the SUM downtime) vs SPAU (a developer during the post-conversion stabilization).

### Key sources to consult

1. SAP Custom Code Migration Guide for S/4HANA 2025 FPS01 — section "Adjustment of Repository Objects".
2. SAP Note **1973241** — "Adjustments using transactions SPDD/SPAU".
3. SAP Note **2298737** — "SPDD/SPAU performance issues".
4. SAP Help Portal: "Modification Adjustment".
5. SAP Community: blog "SPDD/SPAU during S/4HANA conversion".

### Key transactions / objects

- `SPDD`, `SPAU`, `SPAU_ENH`, `SE95`, `SE11`, `SE38`
- Reports: `RDDIT076` (SPDD worklist), `RDDIT077` (SPAU worklist)

### Worked example

Walk through adjusting a custom append structure on `BSEG` and a modified standard report:
1. SUM pauses at the SPDD prompt; admin opens SPDD.
2. The append structure `ZAFINBSEG` shows up "with modification assistant"; agent applies the automatic merge and saves to a transport.
3. SUM resumes and finishes the conversion.
4. Post-conversion, developer opens SPAU; finds 12 modifications.
5. 8 are SAP-Note resets (`Reset to Original`), 3 are customer adjustments preserved by SAP (`Adopt`), 1 is a manual conflict in `MIRO` BAdI implementation that gets routed to a senior developer.
6. Adjustment transport released and transported forward.

### Anti-patterns

- Skipping SPDD because "we'll do it later" — SUM will not let you, and trying to recreate dictionary modifications after activation is much harder.
- Not creating adjustment transports → adjustments are lost on the next system refresh.
- Confusing SPAU (modifications) with the Custom Code Migration worklist (custom objects). They are orthogonal: SPAU adjusts modifications to *SAP* code; ATC findings adjust *custom* code.
- Marking everything in SPAU as "Adopt" without reviewing — silently keeps obsolete modifications.

### Related skills

`sap-sum-dmo`, `sap-atc-readiness`, `sap-functional-simplifications`
