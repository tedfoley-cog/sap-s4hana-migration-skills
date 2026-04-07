---
name: sap-fiori-activation
description: |
  Use when discovering and activating SAP Fiori apps after an S/4HANA system
  conversion: looking up apps in the SAP Fiori Apps Reference Library, running
  task list SAP_FIORI_CONTENT_ACTIVATION, activating OData services in
  /IWFND/MAINT_SERVICE, activating ICF nodes in SICF, assigning business
  catalogs and roles in PFCG, configuring Spaces and Pages in the Fiori
  Launchpad, troubleshooting "tile is empty" or "404 /sap/opu/" errors,
  invalidating client caches with /UI2/INVALIDATE_CLIENT_CACHES, or planning
  the post-conversion UX rollout from SAP GUI to Fiori.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "2026-04-07"
  s4hana_release: "2023, 2024, 2025"
  sources:
    - "SAP Note 1685257 — SAP Fiori Central Note"
    - "SAP Note 2659151 — Spaces and Pages in SAP Fiori Launchpad"
    - "SAP Note 3023853 — SAP Fiori Launchpad — Spaces and Pages — Central Note"
    - "SAP Note 2919182 — SAP Fiori Front-End Server 2020 for SAP S/4HANA"
    - "SAP Note 1948537 — SAP Fiori Activation — General Information"
    - "SAP Help Portal — SAP Fiori Overview"
    - "SAP Fiori Apps Reference Library"
    - "SAP Help Portal — Activating SAP Fiori Content for SAP S/4HANA"
    - "SAP Community — Sergio Guerrero blog series on Fiori activation"
related_skills:
  - sap-sum-dmo
  - sap-clean-core-extensibility
---

## When to use this skill

Use this skill when:

- You have completed an SAP ECC to S/4HANA system conversion (or a new S/4HANA install) and need to enable Fiori apps for end users.
- You need to discover which standard Fiori apps are available for specific S/4HANA releases and business roles.
- You are troubleshooting Fiori tiles that appear but do not launch (OData service inactive, ICF node inactive, missing role assignments).
- You are transitioning the Fiori Launchpad from the legacy Groups/Catalogs model to the modern Spaces and Pages layout (S/4HANA 2020+).
- You need to plan a phased UX rollout replacing SAP GUI transactions with Fiori apps post-conversion.
- Users report stale Launchpad content after role or catalog changes and you need to invalidate client-side caches.

This skill covers **standard SAP Fiori app activation only**. For building custom Fiori apps in SAP Business Application Studio or Fiori Tools, refer to the SAP Fiori development documentation.

## Prerequisites

1. **S/4HANA system is converted and operational** — the SUM/DMO conversion has completed and the system is in a usable state (see `sap-sum-dmo`).
2. **SAP Fiori front-end server (FES) is embedded** — starting with S/4HANA 1610, the FES is embedded in the ABAP application server; no separate hub deployment is needed for standard apps ([SAP Note 2919182](https://me.sap.com/notes/2919182)).
3. **ICM (Internet Communication Manager) is configured** — HTTP/HTTPS services are enabled at the system level.
4. **Basis authorizations** — you need access to transactions `SICF`, `/IWFND/MAINT_SERVICE`, `PFCG`, `STC01` (task list runner), and `/UI2/FLP` (Fiori Launchpad administration).
5. **SAP_BASIS and SAP_GWFND components are current** — apply the latest Support Package Stack; many Fiori activation issues trace back to missing corrections in these components ([SAP Note 1685257](https://me.sap.com/notes/1685257)).

## Quick decision tree

```
Start
  |
  v
Is this a new S/4HANA install or a system conversion?
  |                                  |
  New install                        System conversion
  |                                  |
  v                                  v
Run task list                    Run task list
SAP_FIORI_CONTENT_ACTIVATION     SAP_FIORI_CONTENT_ACTIVATION
for full scope                   for delta scope (post-conversion)
  |                                  |
  +----------------------------------+
  |
  v
Are you on S/4HANA 2020 or later?
  |                    |
  Yes                  No (1610–1909)
  |                    |
  v                    v
Use Spaces & Pages    Use Groups & Catalogs
(modern layout)       (legacy layout)
  |                    |
  +--------------------+
  |
  v
For each target app:
  1. Look up in Fiori Apps Reference Library
  2. Verify OData service active (/IWFND/MAINT_SERVICE)
  3. Verify ICF node active (SICF)
  4. Assign catalog to role (PFCG)
  5. Assign role to Space/Page or Group
  6. Invalidate caches
  7. Test
```

## Procedure

### Step 1: Discover apps in the SAP Fiori Apps Reference Library

The SAP Fiori Apps Reference Library (`https://fioriappslibrary.hana.ondemand.com/`) is the single authoritative source for which Fiori apps exist for each S/4HANA release ([SAP Note 1685257](https://me.sap.com/notes/1685257)).

1. Open the library and filter by **Product Version** (e.g., "SAP S/4HANA 2023") and **Line of Business** (e.g., "Sales").
2. For each app, the library shows:
   - **App ID** (e.g., `F0095` for Manage Sales Orders).
   - **App type**: transactional, analytical, fact sheet, or overview page.
   - **Required back-end OData service** and its technical name.
   - **Required front-end components** (SAPUI5 component ID).
   - **Required business catalog** (e.g., `SAP_SD_BC_SO_MANAGE_PC`).
   - **Required business role** (e.g., `SAP_BR_SALES_MANAGER`).
   - **Configuration information** including any app-specific customizing.
3. Record the OData service name and business catalog for each app you plan to activate.

**App types explained:**

| Type | Description | Typical use |
|---|---|---|
| **Transactional** | Full create/change/display apps replacing SAP GUI transactions | Core business processes (create sales order, post invoice) |
| **Analytical** | KPI tiles, dashboards, smart-business content | Management reporting, real-time KPIs |
| **Fact sheet** | Read-only detail views of business objects | Quick lookup of customer, material, sales order details |
| **Legacy GUI in Fiori** | Classic SAP GUI transactions wrapped in WebGUI or GUI for HTML | Transactions with no native Fiori equivalent yet |

([SAP Help: SAP Fiori App Types](https://help.sap.com/docs/SAP_FIORI_OVERVIEW/99c2b1d59dcc47968fbf44126aee6850/1ef1f8af3c1f4dfcad01f024afac0074.html))

### Step 2: Run the Fiori content activation task list

SAP delivers task list **`SAP_FIORI_CONTENT_ACTIVATION`** to automate the bulk activation of Fiori content (ICF services, OData services, business catalogs). This is the recommended approach rather than activating apps one by one ([SAP Note 1948537](https://me.sap.com/notes/1948537)).

1. Open transaction **`STC01`** (Task List Runner).
2. Search for task list `SAP_FIORI_CONTENT_ACTIVATION`.
3. Select the scope — you can activate all content or limit to specific application components (e.g., `SD` for Sales and Distribution).
4. Execute the task list. It will:
   - Activate the relevant **ICF nodes** under `/sap/bc/ui5_ui5/` and `/sap/opu/odata/`.
   - Register **OData services** in the local gateway.
   - Generate the **Fiori Launchpad catalogs and groups** (on releases before 2020) or **Spaces and Pages** content (2020+).
5. Review the task list log for errors. Common issues:
   - Missing authorizations for the executing user — the user needs `SAP_ALL` or equivalent during activation.
   - Component-specific prerequisites not met (e.g., analytics content requires BW-embedded activation).

Additional task lists you may need:

| Task list | Purpose |
|---|---|
| `SAP_FIORI_LAUNCHPAD_INIT_SETUP` | Initial Fiori Launchpad infrastructure setup |
| `SAP_FIORI_UPGRADE_CONTENT_ACTIVATION` | Delta activation after Support Package upgrades |
| `SAP_BASIS_CONTENT_ACTIVATION` | Basis-level ICF and service activation |

([SAP Help: Activating SAP Fiori Content](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/8308e6d301d54584a33cd04a9861bc52/a3a72440d8a0423fbfbf961e06b43a41.html))

### Step 3: Verify OData service activation

Each Fiori app consumes one or more OData services. These must be registered and active in the local SAP Gateway.

1. Open transaction **`/IWFND/MAINT_SERVICE`** (Activate and Maintain Services).
2. Search for the OData service name from the Fiori Apps Reference Library (e.g., `API_SALES_ORDER_SRV`).
3. If the service is listed and shows status **Active** (green), it is ready.
4. If the service is missing, click **Add Service** → select the system alias (typically `LOCAL`) → find and register the service from the back-end catalog.
5. After registration, test the service by clicking **Call Browser** or navigating to the service URL: `/sap/opu/odata/sap/<SERVICE_NAME>/$metadata`.

**Common issues:**
- Service appears but returns HTTP 500 → check the back-end service implementation is activated in transaction `/IWBEP/REG_SERVICE` ([SAP Note 1685257](https://me.sap.com/notes/1685257)).
- Service metadata loads but data returns empty → check the user has appropriate data authorizations (authorization objects like `V_VBAK_VKO` for sales).

### Step 4: Verify ICF node activation

Fiori apps are served through the Internet Communication Framework (ICF). Each app has an ICF node that must be active.

1. Open transaction **`SICF`**.
2. Navigate to the relevant ICF tree path. Key paths for Fiori:
   - `/sap/bc/ui5_ui5/sap/` — SAPUI5 application front-end components.
   - `/sap/opu/odata/sap/` — OData service endpoints.
   - `/sap/bc/ui2/` — Fiori Launchpad infrastructure (flp, start_up, page_builder, etc.).
   - `/sap/public/bc/ui5_ui5/` — SAPUI5 library resources.
3. Right-click the node and select **Activate Service** if it is inactive (shown in grey).
4. For bulk activation, the task list in Step 2 handles this; manual activation is a fallback for troubleshooting individual apps.

**Key ICF nodes that must always be active for Fiori Launchpad:**

| ICF path | Purpose |
|---|---|
| `/sap/bc/ui2/flp` | Fiori Launchpad shell |
| `/sap/bc/ui2/start_up` | Launchpad startup services |
| `/sap/bc/ui5_ui5/ui2/ushell` | Unified Shell (Launchpad runtime) |
| `/sap/public/bc/ui5_ui5/resources` | SAPUI5 library delivery |

([SAP Help: ICF Configuration for SAP Fiori](https://help.sap.com/docs/SAP_FIORI_OVERVIEW/9b4ee51ce91e4a9cadd5e6e5c7170527/b8fdf8016d3e4e4fa4be79bcda79a0f8.html))

### Step 5: Assign business catalogs and roles

SAP delivers **business catalogs** that bundle the tiles, target mappings, and authorizations for a logical set of apps. These catalogs are assigned to **business roles** which are then assigned to users.

1. Open transaction **`PFCG`** (Role Maintenance).
2. Create or copy a custom role (e.g., `Z_SD_SALES_REP` derived from `SAP_BR_SALES_MANAGER`).
   - **Never modify SAP-delivered roles directly** — copy them to the customer namespace (`Z*` or `Y*`) first. SAP role updates during SPs will overwrite direct changes ([SAP Note 1685257](https://me.sap.com/notes/1685257)).
3. In the **Menu** tab, add entries of type **SAP Fiori Launchpad: Catalog** and specify the business catalog ID (e.g., `SAP_SD_BC_SO_MANAGE_PC`).
4. Go to the **Authorizations** tab and generate the authorization profile. The catalog assignment automatically pulls in the required authorization objects.
5. Assign the role to users via the **User** tab or transaction `SU01`.

**Catalog vs. Group vs. Space/Page:**

| Concept | Purpose | Applies to |
|---|---|---|
| **Business Catalog** | Bundles tiles + target mappings + authorizations for a set of apps | All S/4HANA releases |
| **Group** (legacy) | Visual grouping of tiles on the Launchpad home page | S/4HANA 1610–1909 (deprecated from 2020) |
| **Space** | A top-level navigation entry in the Launchpad shell bar | S/4HANA 2020+ |
| **Page** | Content area within a Space containing sections with tiles | S/4HANA 2020+ |

([SAP Note 2659151](https://me.sap.com/notes/2659151))

### Step 6: Configure Spaces and Pages (S/4HANA 2020+)

Starting with S/4HANA 2020, **Spaces and Pages** replace the legacy Groups and Catalogs as the primary Launchpad layout model. SAP delivers pre-built Spaces and Pages aligned to business roles ([SAP Note 3023853](https://me.sap.com/notes/3023853)).

1. **Enable Spaces and Pages** in the Fiori Launchpad configuration:
   - Run transaction `/UI2/FLP_CUS_CONF` or use the Fiori app **Manage Launchpad Settings** (App ID `F3835`).
   - Set the parameter `SPACES_ENABLE` to `true`.
   - Optionally set `SPACES_ONLY` to `true` to disable the classic home page entirely.
2. **Assign SAP-delivered Spaces to roles**:
   - SAP delivers Spaces (e.g., `SAP_SD_BC_SO_MANAGE_SP`) aligned to business catalogs.
   - Assign these Spaces to your custom roles in PFCG, similar to how you assign catalogs.
3. **Create custom Pages** using the Fiori app **Manage Launchpad Pages** (App ID `F4546`):
   - Create Sections within Pages to organize tiles logically.
   - Add tiles from the available catalogs assigned to the user's roles.
4. **Create custom Spaces** using the Fiori app **Manage Launchpad Spaces** (App ID `F4545`):
   - Each Space references one or more Pages.
   - Assign Spaces to roles in PFCG.
5. After configuration, users see a navigation menu in the Launchpad shell bar with Spaces as top-level entries and Pages as the content within each Space.

**Migration from Groups to Spaces:**
- SAP provides a migration tool that converts existing Group-based layouts into Spaces and Pages.
- Access it via the Fiori app **Migrate Groups to Spaces** or report `FLP_MIGRATE_GROUPS_TO_SPACES`.
- Run in simulation mode first, then execute ([SAP Note 2659151](https://me.sap.com/notes/2659151)).

### Step 7: Invalidate caches and verify

After activating apps and assigning roles, you must invalidate the Launchpad client cache so users see the updated content.

1. **Invalidate client caches** — run report **`/UI2/INVALIDATE_CLIENT_CACHES`** via transaction `SA38`:
   - This clears the browser-side cache entries for all users.
   - Users will see updated Launchpad content on their next login.
   - Schedule this report after every batch of role or catalog changes ([SAP Note 1685257](https://me.sap.com/notes/1685257)).
2. **Recalculate the app index** — run report **`/UI5/APP_INDEX_CALCULATE`** via transaction `SA38`:
   - This rebuilds the SAPUI5 application index, which maps app IDs to their deployed BSP applications.
   - Required after deploying new apps or after system upgrades.
3. **Verify by testing**:
   - Log in as a user with the assigned role.
   - Open the Fiori Launchpad URL: `https://<host>:<port>/sap/bc/ui2/flp`.
   - Confirm the tile appears in the correct Space/Group.
   - Click the tile and verify the app launches and displays data.

### Step 8: Troubleshoot common issues

| Symptom | Likely cause | Resolution |
|---|---|---|
| Tile appears but is empty / shows error | OData service not active | Activate in `/IWFND/MAINT_SERVICE` (Step 3) |
| 404 from `/sap/opu/odata/...` | ICF node inactive | Activate in `SICF` (Step 4) |
| Tile assigned but not visible | Missing role assignment or stale cache | Check PFCG assignment; run `/UI2/INVALIDATE_CLIENT_CACHES` |
| App launches but shows "No data" | User lacks data-level authorizations | Check authorization trace via `ST01`; adjust auth objects in role |
| Launchpad shows old layout after Space/Page changes | Browser cache not cleared | Run `/UI2/INVALIDATE_CLIENT_CACHES`; user should clear browser cache |
| "Service ... is not available" popup | Gateway service not registered | Register in `/IWFND/MAINT_SERVICE` → Add Service |
| Analytical tile shows "KPI not found" | Smart Business KPI not configured | Activate KPI via app **Manage KPIs and Reports** (App ID `F1498`) |

([SAP Note 1685257](https://me.sap.com/notes/1685257))

## Worked example

**Scenario**: Activate the **Manage Sales Orders** app (App ID `F0095`) for sales representatives after a system conversion to S/4HANA 2023.

### 1. Look up the app

Open the SAP Fiori Apps Reference Library and search for `F0095`:

- **App name**: Manage Sales Orders
- **App type**: Transactional
- **OData service**: `API_SALES_ORDER_SRV` (back-end), registered as `API_SALES_ORDER_SRV` in the gateway
- **SAPUI5 component**: `cus.sd.salesorder.manage`
- **Required business catalog**: `SAP_SD_BC_SO_MANAGE_PC`
- **Required business role**: `SAP_BR_SALES_MANAGER`
- **ICF path**: `/sap/opu/odata/sap/API_SALES_ORDER_SRV`

### 2. Run the task list

```
Transaction: STC01
Task list:   SAP_FIORI_CONTENT_ACTIVATION
Scope:       SD (Sales and Distribution)
Execute.
```

Review the log — confirm that the SD-related ICF nodes and OData services are activated. The log should show entries for `API_SALES_ORDER_SRV` activation.

### 3. Verify OData service

```
Transaction: /IWFND/MAINT_SERVICE
Filter:      API_SALES_ORDER_SRV
Status:      Active (green)
Test:        Click "Call Browser" — metadata XML should load.
URL test:    /sap/opu/odata/sap/API_SALES_ORDER_SRV/$metadata
```

If the service is missing, add it:
- Click **Add Service** → System Alias = `LOCAL` → Technical Service Name = `API_SALES_ORDER_SRV` → select and register.

### 4. Verify ICF node

```
Transaction: SICF
Path:        /sap/opu/odata/sap/API_SALES_ORDER_SRV
Status:      Active (icon is colored, not grey)
```

If inactive, right-click → **Activate Service**.

### 5. Create a custom role with the business catalog

```
Transaction: PFCG
Action:      Copy role SAP_BR_SALES_MANAGER → Z_SD_SALES_REP
Menu tab:    Verify entry "SAP Fiori Launchpad: Catalog = SAP_SD_BC_SO_MANAGE_PC"
             If missing, add it: Other Node → SAP Fiori Launchpad: Catalog
             Enter catalog ID: SAP_SD_BC_SO_MANAGE_PC
Auth tab:    Generate authorization profile
User tab:    Assign user SALES_USER01
Save.
```

### 6. Assign the role to a Space and Page (S/4HANA 2023)

Since we are on S/4HANA 2023, we use Spaces and Pages:

```
App:         Manage Launchpad Spaces (F4545)
Action:      Find SAP-delivered Space "SAP_SD_BC_SO_MANAGE_SP"
             or create custom Space "Z_SD_SALES_SPACE"
Assign:      Add Page reference to "SAP_SD_BC_SO_MANAGE_PG"
             or create custom Page "Z_SD_SALES_PAGE"
             Add Section: "Sales Order Management"
             Add Tile: Manage Sales Orders (from catalog SAP_SD_BC_SO_MANAGE_PC)
```

In PFCG, assign the Space to role `Z_SD_SALES_REP`:
```
Transaction: PFCG → Z_SD_SALES_REP → Menu tab
Add:         SAP Fiori Launchpad: Space = SAP_SD_BC_SO_MANAGE_SP
             (or Z_SD_SALES_SPACE if custom)
Save and generate profile.
```

### 7. Invalidate caches and test

```
Transaction: SA38
Report:      /UI2/INVALIDATE_CLIENT_CACHES
Execute.

Report:      /UI5/APP_INDEX_CALCULATE
Execute.
```

Log in as user `SALES_USER01`:
```
URL: https://<host>:<port>/sap/bc/ui2/flp
```

Expected result:
- The "Sales" Space appears in the Launchpad navigation bar.
- The "Sales Order Management" section displays the "Manage Sales Orders" tile.
- Clicking the tile opens the app; sales orders are displayed based on the user's org-level authorizations (sales org, distribution channel, etc.).

## Anti-patterns

1. **Activating apps one by one instead of using the task list** — Manually activating individual ICF nodes and OData services is slow, error-prone, and misses dependency chains. SAP delivers task list `SAP_FIORI_CONTENT_ACTIVATION` specifically to automate bulk activation. Always start there and only fall back to manual activation for troubleshooting individual apps ([SAP Note 1948537](https://me.sap.com/notes/1948537)).

2. **Creating new Groups in S/4HANA 2020+ instead of using Spaces and Pages** — Groups are the legacy layout model deprecated from S/4HANA 2020. SAP's investment and new content delivery are focused on Spaces and Pages. Using Groups on 2020+ means you will not benefit from the improved navigation model and will need to migrate eventually. Start with Spaces and Pages for any new activation on 2020+ ([SAP Note 2659151](https://me.sap.com/notes/2659151)).

3. **Assigning SAP-delivered catalogs directly to user roles without copying them first** — SAP updates delivered catalogs during Support Package upgrades. If you modify a delivered catalog directly (e.g., adding custom tiles), those changes will be overwritten on the next upgrade. Always copy catalogs to the customer namespace (`Z*`) before customizing ([SAP Note 1685257](https://me.sap.com/notes/1685257)).

4. **Forgetting to invalidate the client cache after assigning a new tile** — The Fiori Launchpad aggressively caches content on the client side for performance. After any change to catalogs, role assignments, or Space/Page configurations, you must run `/UI2/INVALIDATE_CLIENT_CACHES`. Without this, users will continue to see the old Launchpad layout until the cache expires naturally, leading to confusion and support tickets ([SAP Note 1685257](https://me.sap.com/notes/1685257)).

5. **Treating Fiori activation as a day-one afterthought** — Fiori activation for a production S/4HANA system is a multi-week activity involving app discovery, role redesign, testing, and user training. It should be planned as a dedicated workstream in the migration project, not squeezed into the final weekend of go-live. A phased rollout (e.g., start with top-20 most-used transactions, expand over subsequent sprints) is the recommended approach.

6. **Skipping OData service testing before go-live** — An active OData service registration does not guarantee the service works end-to-end. Always test with a real user (not `SAP*` or `DDIC`) to validate both the service response and the data-level authorizations. Use transaction `ST01` (authorization trace) to diagnose missing authorization objects.

## References

1. [SAP Note 1685257 — SAP Fiori — Central Note](https://me.sap.com/notes/1685257) — Master note for Fiori deployment, configuration, and troubleshooting. Contains links to all component-specific Fiori notes.
2. [SAP Note 2659151 — Spaces and Pages in SAP Fiori Launchpad](https://me.sap.com/notes/2659151) — Covers the Spaces and Pages model introduced in S/4HANA 2020, migration from Groups, and configuration steps.
3. [SAP Note 3023853 — SAP Fiori Launchpad — Spaces and Pages — Central Note](https://me.sap.com/notes/3023853) — Central note for Spaces and Pages covering known issues, corrections, and best practices.
4. [SAP Note 2919182 — SAP Fiori Front-End Server 2020 for SAP S/4HANA](https://me.sap.com/notes/2919182) — Describes the embedded FES architecture and deployment changes.
5. [SAP Note 1948537 — SAP Fiori Activation — General Information](https://me.sap.com/notes/1948537) — Covers the task list approach for Fiori content activation and prerequisites.
6. [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/) — Interactive catalog of all SAP Fiori apps with technical details, required services, and configuration information.
7. [SAP Help: SAP Fiori Overview](https://help.sap.com/docs/SAP_FIORI_OVERVIEW) — Entry point to all Fiori planning, implementation, and operations documentation.
8. [SAP Help: Activating SAP Fiori Content for SAP S/4HANA](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/8308e6d301d54584a33cd04a9861bc52/a3a72440d8a0423fbfbf961e06b43a41.html) — Step-by-step activation guide for S/4HANA on-premise.
9. [SAP Help: ICF Configuration for SAP Fiori](https://help.sap.com/docs/SAP_FIORI_OVERVIEW/9b4ee51ce91e4a9cadd5e6e5c7170527/b8fdf8016d3e4e4fa4be79bcda79a0f8.html) — ICF node hierarchy and activation requirements.
10. Sergio Guerrero, "SAP Fiori Launchpad — Spaces and Pages — Step by Step Configuration Guide," SAP Community, 2020 — Practical walkthrough of Spaces/Pages setup in S/4HANA 2020.
11. [SAP Help: SAP Fiori App Types](https://help.sap.com/docs/SAP_FIORI_OVERVIEW/99c2b1d59dcc47968fbf44126aee6850/1ef1f8af3c1f4dfcad01f024afac0074.html) — Classification of transactional, analytical, fact sheet, and legacy GUI app types.
