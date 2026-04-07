## Brief: sap-modern-abap-rewrite

**Skill name**: `sap-modern-abap-rewrite`
**Phase**: Post-conversion remediation / clean-core upgrades
**Owner**: Bringing legacy ABAP code up to modern (7.4+ / ABAP Cloud) syntax.

### Scope of this skill

How to refactor older ABAP code (typically 4.6 / 6.0 / 7.0 era) into modern ABAP, focused on the patterns that SAP/abap-cleaner rules and the ABAP Cheat Sheets cover. This is **complementary** to `sap-hana-performance` (which focuses on database-side patterns) — this skill focuses on language-level cleanups that improve readability, testability, and clean-core compliance.

Cover the major modernization moves:

1. **Inline data declarations**: `DATA(lv_x) = ...` instead of `DATA: lv_x TYPE i. lv_x = ...`.
2. **Table expressions**: `lt_tab[ key = value ]` instead of `READ TABLE lt_tab WITH KEY ... INTO ...`.
3. **Constructor expressions**: `VALUE`, `NEW`, `REF`, `CONV`, `EXACT`, `CORRESPONDING`, `REDUCE`, `FILTER`.
4. **String templates**: `|Hello { lv_name }|` instead of `CONCATENATE`.
5. **`COND` and `SWITCH`** in expressions instead of multi-line `IF`/`CASE` blocks for assignment.
6. **`FOR` iteration in expressions**: `VALUE #( FOR ls IN lt ( ... ) )`.
7. **New iteration patterns**: `LOOP AT lt_tab REFERENCE INTO`, parallel `LINE_INDEX`.
8. **`@`-escaped host variables in Open SQL** (mandatory in ABAP Cloud).
9. **Strict mode SQL** (`SELECT ... INTO @DATA(...)`).
10. **OO over procedural**: replacing function modules with classes; replacing `INCLUDE` includes with class methods.
11. **Exception classes** (`CX_*`) over `SY-SUBRC` checks.
12. **Unit tests with ABAP Unit** (`CL_AUNIT_*`).

For each pattern, give a **before / after** snippet using realistic identifiers.

Cover **ABAP Cloud restrictions**: which classic patterns are forbidden in ABAP for Cloud Development (e.g. direct DB access to non-released tables, dynamic SQL, classic function modules) and what to use instead. Link to SAP/abap-atc-cr-cv-s4hc-tools.

Make it explicit that this skill is meant to be used **after** ATC findings have been triaged — i.e., once you know an object stays, this is how you make it modern.

### Key sources to consult

1. **SAP-samples/abap-cheat-sheets** — primary source for syntax examples.
2. **SAP/abap-cleaner** — the 100+ cleanup rules. Cite by rule name.
3. SAP Help Portal: "ABAP — Keyword Documentation" (latest release).
4. SAP Press: "ABAP to the Future" (cite by title and chapter only).
5. SAP Note **2436688** — Clean Core ATC checks.

### Worked example

Walk through modernizing a fictional `Z_BUILD_INVOICE_LIST` form routine into a class method:
1. Original: 80-line `FORM` with nested `LOOPs`, `CONCATENATE`, `READ TABLE WITH KEY`, no unit tests.
2. Step 1: extract to a static method on `ZCL_INVOICE_BUILDER`.
3. Step 2: replace `READ TABLE` with table expressions.
4. Step 3: build the result table with `VALUE #( FOR ... )`.
5. Step 4: replace `CONCATENATE` with string templates.
6. Step 5: add an ABAP Unit test class with two cases.
7. Result is half the line count, type-safe, and unit-tested.

### Anti-patterns

- Modernizing syntax in code that ATC said to delete (waste of time).
- Mass-applying abap-cleaner rules across the whole codebase without per-file review (changes can break dynamic call sites).
- Mixing ABAP Cloud restrictions with classic ABAP in the same package (the toolchain will fight you).
- Over-using `REDUCE` until the code becomes unreadable — clarity beats cleverness.
- Removing `SY-SUBRC` checks without confirming the exception path is tested.

### Related skills

`sap-hana-performance`, `sap-clean-core-extensibility`, `sap-atc-readiness`
