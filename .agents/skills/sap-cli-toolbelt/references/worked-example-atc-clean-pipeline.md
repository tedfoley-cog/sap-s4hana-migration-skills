# Worked Example: End-to-End ATC → Clean → Verify Pipeline

> **Sources**: [sapcli (GitHub)](https://github.com/jfilak/sapcli) — Apache-2.0,
> [abap-cleaner (GitHub)](https://github.com/SAP/abap-cleaner) — Apache-2.0.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Install CLIs and authenticate](#step-1--install-clis-and-authenticate)
- [Step 2 — Run ATC readiness check](#step-2--run-atc-readiness-check)
- [Step 3 — Download, clean, push back](#step-3--download-clean-push-back)
- [Step 4 — Verify with ABAP Unit tests](#step-4--verify-with-abap-unit-tests)

## Scenario

A Devin session needs to run S/4HANA readiness checks against package `$Z_SALES` on an on-prem ECC system, download failing objects, clean them with abap-cleaner, push them back, and verify with unit tests.

## Step 1 — Install CLIs and authenticate

```bash
# Install sapcli and abap-cleaner
pipx install git+https://github.com/jfilak/sapcli.git
curl -L "https://github.com/SAP/abap-cleaner/releases/download/v1.20.0/abap-cleaner-headless.jar" \
  -o /usr/local/lib/abap-cleaner.jar

# Authenticate (secrets already configured)
export SAP_URL="${SAP_URL}" SAP_CLIENT="${SAP_CLIENT}"
export SAP_USER="${SAP_USER}" SAP_PASSWORD="${SAP_PASSWORD}"
```

## Step 2 — Run ATC readiness check

```bash
# Syntax: sapcli atc run {package,class,program} OBJECT_NAME [-r VARIANT] [-o {human,html,checkstyle}]
sapcli atc run package '$Z_SALES' -r S4HANA_READINESS_2025 -o checkstyle > findings.xml
python3 -c "
import xml.etree.ElementTree as ET
root = ET.parse('findings.xml').getroot()
for f in root.findall('.//file'):
    for e in f.findall('error'):
        print(f\"{e.get('severity')} | {f.get('name')} | {e.get('message')}\")
"
```

Output shows 3 findings in `ZCL_ORDER_HELPER` — deprecated BAPI calls.

## Step 3 — Download, clean, push back

```bash
# Download the source
sapcli checkout class zcl_order_helper ./fix

# Apply abap-cleaner modernization rules
java -jar /usr/local/lib/abap-cleaner.jar \
  --sourcefile ./fix/zcl_order_helper.clas.abap \
  --targetfile ./fix/zcl_order_helper_cleaned.clas.abap \
  --profile profiles/team-profile.cfg

# Review the diff
diff -u ./fix/zcl_order_helper.clas.abap ./fix/zcl_order_helper_cleaned.clas.abap

# Write the cleaned source back and activate
sapcli class write zcl_order_helper ./fix/zcl_order_helper_cleaned.clas.abap --activate
```

## Step 4 — Verify with ABAP Unit tests

```bash
sapcli aunit run class zcl_order_helper --output junit4 > aunit.xml
python3 -c "
import xml.etree.ElementTree as ET
root = ET.parse('aunit.xml').getroot()
for s in root.findall('.//testsuite'):
    print(f\"{s.get('name')}: {s.get('tests')} tests, {s.get('failures')} failures\")
"
```

All tests pass. The full pipeline — `sapcli atc` → download → `abap-cleaner` → write → `sapcli aunit` — completed without SAP GUI or Eclipse.
