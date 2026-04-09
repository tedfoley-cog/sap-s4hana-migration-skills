# Worked Example: Activating Manage Sales Orders (F0095) on S/4HANA 2023

> **Sources**: [SAP Note 1685257](https://me.sap.com/notes/1685257) — SAP Fiori Central Note,
> [SAP Note 2659151](https://me.sap.com/notes/2659151) — Spaces and Pages,
> [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/).
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Scenario](#scenario)
- [Step 1 — Look up the app](#step-1--look-up-the-app)
- [Step 2 — Run the task list](#step-2--run-the-task-list)
- [Step 3 — Verify OData service](#step-3--verify-odata-service)
- [Step 4 — Verify ICF node](#step-4--verify-icf-node)
- [Step 5 — Create a custom role with the business catalog](#step-5--create-a-custom-role-with-the-business-catalog)
- [Step 6 — Assign the role to a Space and Page](#step-6--assign-the-role-to-a-space-and-page)
- [Step 7 — Invalidate caches and test](#step-7--invalidate-caches-and-test)

## Scenario

Activate the **Manage Sales Orders** app (App ID `F0095`) for sales representatives after a system conversion to S/4HANA 2023.

## Step 1 — Look up the app

Open the SAP Fiori Apps Reference Library and search for `F0095`:

- **App name**: Manage Sales Orders
- **App type**: Transactional
- **OData service**: `API_SALES_ORDER_SRV` (back-end), registered as `API_SALES_ORDER_SRV` in the gateway
- **SAPUI5 component**: `cus.sd.salesorder.manage`
- **Required business catalog**: `SAP_SD_BC_SO_MANAGE_PC`
- **Required business role**: `SAP_BR_SALES_MANAGER`
- **ICF path**: `/sap/opu/odata/sap/API_SALES_ORDER_SRV`

## Step 2 — Run the task list

```
Transaction: STC01
Task list:   SAP_FIORI_CONTENT_ACTIVATION
Scope:       SD (Sales and Distribution)
Execute.
```

Review the log — confirm that the SD-related ICF nodes and OData services are activated. The log should show entries for `API_SALES_ORDER_SRV` activation.

## Step 3 — Verify OData service

```
Transaction: /IWFND/MAINT_SERVICE
Filter:      API_SALES_ORDER_SRV
Status:      Active (green)
Test:        Click "Call Browser" — metadata XML should load.
URL test:    /sap/opu/odata/sap/API_SALES_ORDER_SRV/$metadata
```

If the service is missing, add it:
- Click **Add Service** → System Alias = `LOCAL` → Technical Service Name = `API_SALES_ORDER_SRV` → select and register.

## Step 4 — Verify ICF node

```
Transaction: SICF
Path:        /sap/opu/odata/sap/API_SALES_ORDER_SRV
Status:      Active (icon is colored, not grey)
```

If inactive, right-click → **Activate Service**.

## Step 5 — Create a custom role with the business catalog

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

## Step 6 — Assign the role to a Space and Page

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

## Step 7 — Invalidate caches and test

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
