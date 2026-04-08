---
name: sap-cli-toolbelt
description: |
  Use when determining which SAP command-line tools are available in a Devin
  sandbox for an S/4HANA migration project: selecting the right CLI for a
  given task (sapcli for ABAP/ADT operations, hdbsql for HANA queries, btp/cf
  for BTP provisioning, cds for CAP development, ui5 for Fiori builds),
  installing and authenticating CLIs, understanding which tools do NOT work
  in a headless Linux environment (SAP GUI, Eclipse ADT, SUM), or looking up
  the standardized Devin secret names for SAP system credentials.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025, 2025 FPS01"
  sources:
    - "sapcli — ADT command-line client (https://github.com/jfilak/sapcli)"
    - "SAP BTP CLI documentation (https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-sap-btp-command-line-interface-btp-cli)"
    - "Cloud Foundry CLI (https://docs.cloudfoundry.org/cf-cli/)"
    - "SAP CAP cds-dk (https://cap.cloud.sap/docs/tools/cds-cli)"
    - "SAP UI5 Tooling (https://sap.github.io/ui5-tooling/)"
    - "SAP Cloud MTA Build Tool mbt (https://sap.github.io/cloud-mta-build-tool/)"
    - "SAP HANA Client hdbsql (https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)"
    - "Project Piper (https://www.project-piper.io/)"
    - "SAP/abap-cleaner (https://github.com/SAP/abap-cleaner)"
    - "abapGit (https://github.com/abapGit/abapGit)"
    - "SAP Cloud SDK generator (https://sap.github.io/cloud-sdk/)"
    - "SAP Fiori Tools @sap/generator-fiori (https://help.sap.com/docs/SAP_FIORI_tools)"
related_skills:
  - sap-atc-readiness
  - sap-clean-core-extensibility
  - sap-data-migration-cockpit
  - sap-fiori-activation
  - sap-functional-simplifications
  - sap-hana-performance
  - sap-migration-testing
  - sap-modern-abap-rewrite
  - sap-scoping
  - sap-simplification-database
  - sap-spdd-spau
  - sap-sum-dmo
---

## When to use this skill

Invoke this skill when you need to:

- **Determine which CLI to use** for a given SAP migration task (e.g., "I need to run ATC checks from the command line" → `sapcli`).
- **Install and authenticate** an SAP CLI in a Devin sandbox session.
- **Look up standardized secret names** for SAP system credentials (`SAP_USER`, `BTP_USERNAME`, `HANA_HOST`, etc.).
- **Understand what does NOT work** in a headless Linux sandbox (SAP GUI, Eclipse ADT, SUM/DMO).
- **Find the right CLI combination** for a specific migration phase (pre-conversion, conversion, post-conversion, BTP extensibility).
- **Configure network prerequisites** — which endpoints and ports each CLI needs to reach.

This skill is a **cross-cutting reference**. Each migration-specific skill (e.g., `sap-atc-readiness`, `sap-hana-performance`) contains a `### CLI usage` subsection with task-specific examples. This skill provides the full catalog, install procedures, and auth patterns in one place.

## Prerequisites

1. **Node.js 18+** — required for `cds`, `ui5`, `mbt`, and `@sap/generator-fiori`. Pre-installed in Devin sandbox.
2. **Python 3.8+** — required for `sapcli`. Pre-installed in Devin sandbox.
3. **Java 11+** — required for `abap-cleaner` headless mode. Install via `sudo apt install -y default-jre` if not present.
4. **Network access** — each CLI requires outbound HTTPS to the target SAP system or BTP endpoint (see Procedure §5).
5. **Devin secrets** — credentials must be configured as org-level or repo-scoped Devin secrets (see Procedure §4).

## Quick decision tree

```
What do you need to do?
│
├── Work with ABAP source code on an on-prem SAP system?
│   └── sapcli  (download, write, ATC, aunit, transports)
│
├── Run SQL against SAP HANA?
│   └── hdbsql  (performance queries, data validation, DDL)
│
├── Manage BTP subaccounts, entitlements, or services?
│   └── btp CLI
│
├── Deploy apps to BTP Cloud Foundry?
│   └── cf CLI  (+plugins: multiapps, html5-plugin)
│
├── Build a CAP (Cloud Application Programming) project?
│   └── cds CLI  (@sap/cds-dk)
│
├── Build or serve a Fiori / UI5 application?
│   └── ui5 CLI  (+@sap/generator-fiori for scaffolding)
│
├── Package an MTA archive for BTP deployment?
│   └── mbt  (Multi-Target Application Build Tool)
│
├── Modernize ABAP source style (clean ABAP)?
│   └── abap-cleaner  (headless Java JAR)
│
├── Orchestrate CI/CD steps for SAP projects?
│   └── piper  (Project Piper CLI)
│
└── Drive SAP GUI transactions or Eclipse ADT?
    └── NOT POSSIBLE in Devin sandbox — use sapcli instead
```

## Procedure

### 1 — CLI catalog: what works in a Devin sandbox

The following 9 CLIs install and run cleanly in the Devin Linux sandbox. They are pure HTTP/stdio tools with no GUI dependencies.

| CLI | Install | Primary use in migration |
|---|---|---|
| **sapcli** | `pipx install git+https://github.com/jfilak/sapcli.git` | ABAP source download/write, ATC checks, aunit, transports ([GitHub](https://github.com/jfilak/sapcli)) |
| **hdbsql** | HANA Client tarball → `hdbinst --batch` | SQL queries against HANA (performance, validation) ([SAP Help](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference)) |
| **btp** | Binary from `tools.hana.ondemand.com` | BTP account/subaccount/entitlement management ([SAP Help](https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-sap-btp-command-line-interface-btp-cli)) |
| **cf** | `sudo apt install cf8-cli` | Cloud Foundry app deployment, service binding ([CF docs](https://docs.cloudfoundry.org/cf-cli/)) |
| **cds** | `npm i -g @sap/cds-dk` | CAP project scaffold, build, deploy ([CAP docs](https://cap.cloud.sap/docs/tools/cds-cli)) |
| **ui5** | `npm i -g @ui5/cli` | UI5/Fiori app build and local serve ([UI5 Tooling](https://sap.github.io/ui5-tooling/)) |
| **mbt** | `npm i -g mbt` | MTA archive packaging for BTP deploy ([MBT docs](https://sap.github.io/cloud-mta-build-tool/)) |
| **piper** | Binary from GitHub releases | CI/CD step orchestration ([Project Piper](https://www.project-piper.io/)) |
| **abap-cleaner** | JAR from GitHub releases | Headless ABAP source modernization ([GitHub](https://github.com/SAP/abap-cleaner)) |

**Additional tools** (not standalone CLIs but usable):

| Tool | Install | Notes |
|---|---|---|
| **@sap-cloud-sdk/generator** | `npm i -g @sap-cloud-sdk/generator` | OData/OpenAPI client generator for S/4HANA APIs |
| **@sap/generator-fiori** | `npm i -g @sap/generator-fiori yo` | Fiori app scaffolding (Yeoman-based) |
| **cf plugins** | `cf install-plugin multiapps` / `cf install-plugin -r CF-Community html5-plugin` | MTA deploy and HTML5 app repo management |

### 2 — Install commands

```bash
# ── On-prem ABAP tools ───────────────────────────────────────────────────
pipx install git+https://github.com/jfilak/sapcli.git

# abap-cleaner (headless mode)
curl -L "https://github.com/SAP/abap-cleaner/releases/download/v1.20.0/abap-cleaner-headless.jar" \
  -o /usr/local/lib/abap-cleaner.jar
alias abap-cleaner='java -jar /usr/local/lib/abap-cleaner.jar'

# ── HANA tools ────────────────────────────────────────────────────────────
curl -L "https://tools.hana.ondemand.com/additional/hanaclient-latest-linux-x64.tar.gz" -o hanaclient.tgz
tar -xzf hanaclient.tgz && cd client && ./hdbinst --batch --path=/opt/sap/hdbclient
export PATH="/opt/sap/hdbclient:$PATH"

# ── BTP / Cloud Foundry tools ────────────────────────────────────────────
# btp CLI
curl -L "https://tools.hana.ondemand.com/additional/btp-cli-linux-amd64-LATEST.tar.gz" -o btp.tgz
tar -xzf btp.tgz && sudo mv linux-amd64/btp /usr/local/bin/

# cf CLI
curl -fsSL "https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key" \
  | sudo gpg --dearmor -o /usr/share/keyrings/cli.cloudfoundry.org.gpg
echo "deb [signed-by=/usr/share/keyrings/cli.cloudfoundry.org.gpg] https://packages.cloudfoundry.org/debian stable main" \
  | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
sudo apt update && sudo apt install -y cf8-cli

# cf plugins
cf install-plugin multiapps -f
cf install-plugin -r CF-Community "html5-plugin" -f

# ── Node.js-based tools ──────────────────────────────────────────────────
npm i -g @sap/cds-dk @ui5/cli mbt @sap-cloud-sdk/generator @sap/generator-fiori yo

# ── CI/CD orchestration ──────────────────────────────────────────────────
curl -L "https://github.com/SAP/jenkins-library/releases/latest/download/piper_master" -o piper
chmod +x piper && sudo mv piper /usr/local/bin/
```

### 3 — Tools that do NOT work in a Devin sandbox

Do not attempt to install these. Use `sapcli` (ADT HTTP) or `hdbsql` as programmatic alternatives.

| Tool | Why it fails | Alternative |
|---|---|---|
| SAP GUI for Windows | Windows-only thick client, no Linux build | `sapcli` for ABAP operations |
| Eclipse + ADT | IDE-only, no headless mode | `sapcli` covers the same ADT HTTP protocol |
| SUM / DMO | Runs on the SAP host as `<sid>adm`, interactive web UI | Advisory only — document the runbook |
| SAP Build Code / Joule | Closed Eclipse-based, no CLI | N/A |
| SAP Solution Manager | ABAP-stack server, browser UI only | RFC via `sapcli` for limited operations |
| SAP Fiori Launchpad Designer | Browser-only configuration | Document the procedure steps |
| SAP Data Services Designer | Windows desktop client | `cds` for BTP-side ETL |
| SNC/Kerberos SSO tools | Require domain-joined machines | Use username/password auth patterns |

### 4 — Authentication patterns and Devin secret names

Store all credentials as Devin org-level or repo-scoped secrets. Reference them via `${VAR}` in skill examples. Never inline actual values.

**On-prem SAP system (sapcli):**

| Secret | Description |
|---|---|
| `SAP_URL` | SAP system HTTPS endpoint, e.g. `https://s4.example.com:44300` |
| `SAP_CLIENT` | SAP client number, e.g. `100` |
| `SAP_USER` | SAP system username |
| `SAP_PASSWORD` | SAP system password |

```bash
# sapcli authentication
export SAP_URL="${SAP_URL}"
export SAP_CLIENT="${SAP_CLIENT}"
export SAP_USER="${SAP_USER}"
export SAP_PASSWORD="${SAP_PASSWORD}"
sapcli package list '$Z_CUSTOM_PKG'
```

**SAP HANA (hdbsql):**

| Secret | Description |
|---|---|
| `HANA_HOST` | HANA endpoint, e.g. `mydb.hana.trial.us10.hanacloud.ondemand.com` |
| `HANA_USER` | HANA database user |
| `HANA_PASSWORD` | HANA database password |

```bash
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT * FROM M_SYSTEM_OVERVIEW"
```

**BTP / Cloud Foundry:**

| Secret | Description |
|---|---|
| `BTP_USERNAME` | BTP global account user |
| `BTP_PASSWORD` | BTP global account password |
| `BTP_SUBDOMAIN` | Subaccount subdomain for `btp login` |
| `CF_API_ENDPOINT` | CF API URL, e.g. `https://api.cf.us10-001.hana.ondemand.com` |
| `CF_ORG` | Cloud Foundry org name |
| `CF_SPACE` | Cloud Foundry space name |

```bash
# BTP login
btp login --url https://cli.btp.cloud.sap --subdomain "${BTP_SUBDOMAIN}" \
  --user "${BTP_USERNAME}" --password "${BTP_PASSWORD}"

# CF login
cf login -a "${CF_API_ENDPOINT}" -u "${BTP_USERNAME}" -p "${BTP_PASSWORD}" \
  -o "${CF_ORG}" -s "${CF_SPACE}"
```

### 5 — Network requirements

Each CLI requires outbound HTTPS from the Devin sandbox to the target system. Document these in your session's network prerequisites.

| CLI | Endpoint | Port |
|---|---|---|
| `sapcli` (ADT) | SAP system HTTPS | 443 or 44300 |
| `hdbsql` (Cloud) | HANA Cloud instance | 443 |
| `hdbsql` (on-prem) | HANA DB | 3\<sysnr\>15 (e.g. 30015) |
| `btp` | `cli.btp.cloud.sap` | 443 |
| `cf` | BTP CF API endpoint | 443 |
| `cds deploy` | HANA Cloud instance | 443 |
| `piper` | Inherits from underlying step | Varies |

If the Devin sandbox cannot reach the SAP system, request VPN configuration from the user (see Devin VPN setup documentation).

### 6 — Recommended CLI combinations per migration phase

| Phase | Skill | Primary CLIs |
|---|---|---|
| Pre-conversion scoping | `sap-scoping` | `sapcli` (package export for analysis) |
| Pre-conversion ATC | `sap-atc-readiness` | `sapcli atc run` (checkstyle XML output for automated triage) |
| Pre-conversion simplifications | `sap-simplification-database` | `sapcli` (source diff), `hdbsql` (table checks) |
| Conversion adjustments | `sap-spdd-spau` | `sapcli` (object download), `abap-cleaner` (cleanup) |
| Cutover | `sap-sum-dmo` | None — SUM is advisory only |
| Functional validation | `sap-functional-simplifications` | `hdbsql` (MATDOC/ACDOCA/BP validation) |
| Performance tuning | `sap-hana-performance` | `hdbsql` (M_EXPENSIVE_STATEMENTS, EXPLAIN PLAN) |
| Code modernization | `sap-modern-abap-rewrite` | `sapcli` → `abap-cleaner` → `sapcli` → `sapcli aunit` |
| BTP extensibility | `sap-clean-core-extensibility` | `btp`, `cf`, `cds`, `mbt`, `@sap-cloud-sdk/generator` |
| Data migration | `sap-data-migration-cockpit` | `cds` (ETL), `hdbsql` (validation) |
| Fiori activation | `sap-fiori-activation` | `ui5`, `cf` (html5-plugin), `@sap/generator-fiori` |
| Testing | `sap-migration-testing` | `sapcli aunit`, `piper`, `hdbsql` (reconciliation) |

## Worked example

**Scenario**: A Devin session needs to run S/4HANA readiness checks against package `$Z_SALES` on an on-prem ECC system, download failing objects, clean them with abap-cleaner, push them back, and verify with unit tests.

**Step 1 — Install CLIs and authenticate:**

```bash
# Install sapcli and abap-cleaner
pipx install git+https://github.com/jfilak/sapcli.git
curl -L "https://github.com/SAP/abap-cleaner/releases/download/v1.20.0/abap-cleaner-headless.jar" \
  -o /usr/local/lib/abap-cleaner.jar

# Authenticate (secrets already configured)
export SAP_URL="${SAP_URL}" SAP_CLIENT="${SAP_CLIENT}"
export SAP_USER="${SAP_USER}" SAP_PASSWORD="${SAP_PASSWORD}"
```

**Step 2 — Run ATC readiness check:**

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

**Step 3 — Download, clean, push back:**

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

**Step 4 — Verify with ABAP Unit tests:**

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

## Anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Attempting to install SAP GUI or Eclipse ADT | No Linux build; thick-client only | Use `sapcli` which speaks the same ADT HTTP protocol |
| Hardcoding SAP credentials in skill examples | Credentials leak into version control | Reference `${VAR}` Devin secrets |
| Using `sapcli` RFC mode when HTTPS/ADT is available | RFC requires additional network ports (33xx) | Prefer HTTPS/ADT mode via `SAP_URL` |
| Running SUM/DMO from a Devin session | SUM requires OS-level `<sid>adm` access on the SAP host | Document the runbook; Devin's role is advisory |
| Installing `hdbsql` via `npm` or `pip` | `hdbsql` is a native binary in the HANA Client package | Download the HANA Client tarball from `tools.hana.ondemand.com` |
| Skipping `--encrypt` flag with `hdbsql` for HANA Cloud | HANA Cloud requires TLS; connections fail without encryption | Always use `-encrypt` (or `-e`) for Cloud endpoints |
| Using `cf push` without `mbt build` for MTA projects | Multi-module apps need MTA packaging | Run `mbt build` first, then `cf deploy *.mtar` |

## References

1. sapcli — ADT command-line client. GitHub: [jfilak/sapcli](https://github.com/jfilak/sapcli). Apache-2.0.
2. SAP BTP CLI. SAP Help: [Account Administration Using the SAP BTP CLI](https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-sap-btp-command-line-interface-btp-cli).
3. Cloud Foundry CLI. [docs.cloudfoundry.org/cf-cli](https://docs.cloudfoundry.org/cf-cli/).
4. SAP CAP CDS CLI (`@sap/cds-dk`). [cap.cloud.sap/docs/tools/cds-cli](https://cap.cloud.sap/docs/tools/cds-cli).
5. SAP UI5 Tooling. [sap.github.io/ui5-tooling](https://sap.github.io/ui5-tooling/).
6. SAP Cloud MTA Build Tool (`mbt`). [sap.github.io/cloud-mta-build-tool](https://sap.github.io/cloud-mta-build-tool/).
7. SAP HANA Client (`hdbsql`). SAP Help: [SAP HANA Client Interface Programming Reference](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference).
8. Project Piper. [project-piper.io](https://www.project-piper.io/). GitHub: [SAP/jenkins-library](https://github.com/SAP/jenkins-library). Apache-2.0.
9. abap-cleaner. GitHub: [SAP/abap-cleaner](https://github.com/SAP/abap-cleaner). Apache-2.0.
10. abapGit. GitHub: [abapGit/abapGit](https://github.com/abapGit/abapGit). MIT.
11. SAP Cloud SDK generator. [sap.github.io/cloud-sdk](https://sap.github.io/cloud-sdk/).
12. SAP Fiori Tools (`@sap/generator-fiori`). SAP Help: [SAP Fiori Tools](https://help.sap.com/docs/SAP_FIORI_tools).
