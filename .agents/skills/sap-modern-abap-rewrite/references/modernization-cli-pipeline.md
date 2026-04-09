# Modernization CLI Pipeline: sapcli → abap-cleaner → aunit

> **Sources**: [sapcli](https://github.com/jfilak/sapcli), [SAP/abap-cleaner](https://github.com/SAP/abap-cleaner) (Apache-2.0).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Environment variables](#environment-variables)
- [Network prerequisites](#network-prerequisites)
- [Full pipeline](#full-pipeline)
- [Notes](#notes)

## Environment variables

- `SAP_URL`, `SAP_CLIENT`, `SAP_USER`, `SAP_PASSWORD`

## Network prerequisites

SAP HTTPS port (typically 443 or 44300).

## Full pipeline

```bash
# Step 1: Download the source of the class to modernize
sapcli checkout class zcl_invoice_builder ./rewrite

# Step 2: Run abap-cleaner in headless mode to apply modernization rules
java -jar abap-cleaner.jar \
  --sourcefile ./rewrite/zcl_invoice_builder.clas.abap \
  --targetfile ./rewrite/zcl_invoice_builder_cleaned.clas.abap \
  --profile profiles/team-profile.cfg

# Step 3: Review the diff
diff -u ./rewrite/zcl_invoice_builder.clas.abap \
        ./rewrite/zcl_invoice_builder_cleaned.clas.abap

# Step 4: Write the cleaned source back to the SAP system and activate
sapcli class write zcl_invoice_builder \
  ./rewrite/zcl_invoice_builder_cleaned.clas.abap --activate

# Step 5: Run ABAP Unit tests to verify nothing broke
sapcli aunit run class zcl_invoice_builder --output junit4 > aunit_results.xml
```

## Notes

- This pipeline lets Devin iterate on ABAP modernization without SAP GUI or ADT.
- The `--output junit4` flag produces standard JUnit XML for CI integration.
- Always review the abap-cleaner diff before writing back — it cannot detect dynamic call sites.
