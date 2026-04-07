## Brief: sap-clean-core-extensibility

**Skill name**: `sap-clean-core-extensibility`
**Phase**: Strategy / architecture decisions
**Owner**: The decision tree for *how* to extend S/4HANA without dirtying the core.

### Scope of this skill

S/4HANA's **clean core** principle: keep the SAP standard untouched so future upgrades and Feature Pack Stack updates remain low-risk. This skill is the architect's decision tree for *where* to put a piece of custom logic.

Cover the three extensibility tiers:

1. **In-app extensibility** (a.k.a. **key user extensibility**): low-code, done by business users in Fiori apps (Custom Fields, Custom Logic in BAdIs via the in-app cockpit). For simple field additions and small business rules.
2. **Side-by-side extensibility on SAP BTP**: build a CAP / Node.js / Java / RAP application on BTP that consumes S/4HANA via OData/Events. For richer apps, integration logic, custom UIs.
3. **Developer extensibility** (a.k.a. **on-stack ABAP extensibility**): ABAP for Cloud Development inside the S/4HANA system itself. For deep, performance-sensitive logic that can't live off-stack but should still be clean-core compliant.

For each tier:
- Decision criteria (latency, data sensitivity, lifecycle, who owns it).
- Allowed APIs and tooling.
- Constraints (released objects only, no direct DB access to non-released tables, ATC Clean Core checks).
- Typical transition paths from a brownfield ECC custom object.

Include the **decision tree** as the centerpiece of the skill — a flowchart-as-prose the agent can walk through to recommend a tier for a given requirement.

Cover **Released APIs**: how to find them (SAP API Business Hub, SAP Help Portal, in-system via `SE80`'s released-objects browser), and the difference between **C1** (stable, public) and **C2** (released for key users) APIs.

Cover the **in-stack vs side-by-side decision** specifically because it's the most common mistake (people default to side-by-side when in-stack is fine, or vice versa).

### Key sources to consult

1. SAP Help Portal: "Extending SAP S/4HANA" — the canonical clean-core guide.
2. SAP Note **2570371** — "Released APIs and Extension Points in SAP S/4HANA".
3. SAP/abap-atc-cr-cv-s4hc-tools — the official tooling for Clean Core ATC checks.
4. SAP-samples/cloud-extension repos for canonical side-by-side examples.
5. SAP Community blog series on Clean Core (search by author "Karl Kessler" or "Jens Weiler").
6. SAP API Business Hub (`api.sap.com`) for the released API catalog.

### Worked example

Walk through a "custom approval workflow on a sales order" requirement and route it through the decision tree:
1. Latency requirement: must run inline before save → can't be side-by-side.
2. Data sensitivity: needs read access to credit master → in-app extensibility insufficient (no released BAdI for that join).
3. Performance: must read 10k rows per save → developer extensibility (in-stack ABAP Cloud).
4. Implementation: BAdI `ME_PROCESS_PO_CUST` (released) + ABAP Cloud class.
5. Counter-example: the same requirement but for a *post-save* notification → side-by-side BTP function listening to a business event is the clean-core answer.

### Anti-patterns

- "We've always done it in ABAP, so we'll do it in ABAP again" — defaulting to developer extensibility without checking if in-app suffices.
- Reaching for direct DB access ("just one SELECT on `BSEG`") → instantly violates clean core and trips ATC Clean Core checks.
- Building a side-by-side BTP app to do something the standard already does (most common waste).
- Treating BAdIs as universally allowed — only **released** BAdIs are clean-core compliant.

### Related skills

`sap-modern-abap-rewrite`, `sap-functional-simplifications`, `sap-atc-readiness`
