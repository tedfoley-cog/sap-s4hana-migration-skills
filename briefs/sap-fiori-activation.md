## Brief: sap-fiori-activation

**Skill name**: `sap-fiori-activation`
**Phase**: Post-conversion UX
**Owner**: Discovering and activating Fiori apps after a system conversion.

### Scope of this skill

After a conversion, the user-facing UX shifts from SAP GUI transactions to **Fiori apps**. This skill covers how to discover which Fiori apps are available for the new release, how to activate them, and how to assign them to roles and the Fiori Launchpad.

Cover:
- Using the **SAP Fiori Apps Reference Library** (`https://fioriappslibrary.hana.ondemand.com/`) to discover apps, with the right product version filter.
- The **app types**: **transactional apps**, **analytical apps** (often KPI tiles), **fact sheets**, **classic transactions exposed in WebGUI**.
- The **technical activation steps**: **task list `SAP_FIORI_CONTENT_ACTIVATION`**, OData service activation in `/IWFND/MAINT_SERVICE`, ICF node activation in `SICF`, role assignment in `PFCG`.
- **Spaces and Pages** (the modern Launchpad layout that replaced Groups/Catalogs in S/4HANA 2020+).
- **Cache management**: `/UI2/INVALIDATE_CLIENT_CACHES`, `/UI5/APP_INDEX_CALCULATE`.
- The relationship between **catalogs**, **groups (legacy)**, **spaces**, **pages**, and **launchpad roles**.
- **Custom Fiori apps**: brief mention of when you'd build one in BAS / Fiori Tools and link to the relevant skill in `secondsky/sap-skills` (or note that this skill assumes standard apps only).
- **Troubleshooting**: app shows up but tile is empty (OData service not active), 404 from `/sap/opu/...` (ICF not active), tile assigned but not visible (role / launchpad cache).

### Key sources to consult

1. SAP Fiori Apps Reference Library (interactive web tool).
2. SAP Help Portal: "Activating SAP Fiori for SAP S/4HANA".
3. SAP Note **1685257** — "Fiori — Central Note".
4. SAP Note **2659151** — "Spaces and Pages in SAP Fiori Launchpad".
5. SAP Community blog series by **Sergio Guerrero** on Fiori activation (cite specific posts).

### Worked example

Walk through activating the **Manage Sales Orders** app for a sales role:
1. Look up the app in the Fiori Apps Reference Library: app ID `F0095`, OData service `SD_F0095_SO_MANAGE_SRV_01`, ICF node `/sap/opu/odata/sap/SD_F0095_SO_MANAGE_SRV_01`.
2. Run task list `SAP_FIORI_CONTENT_ACTIVATION` for the relevant scope.
3. Verify the OData service is active in `/IWFND/MAINT_SERVICE`.
4. Verify the ICF node is active in `SICF`.
5. Assign the standard business catalog `SAP_SD_BC_SO_MANAGE_PC` to a custom role `Z_SD_SALES_REP`.
6. Add the role to a Fiori Space and Page.
7. Test login as a user with the role; tile appears, app launches, data flows.

### Anti-patterns

- Activating apps one by one instead of using the task list — slow and error-prone.
- Creating new Groups in S/4HANA 2020+ instead of using Spaces/Pages.
- Assigning the SAP-delivered catalogs directly to user roles without copying them first — future role updates clobber customizations.
- Forgetting to invalidate the client cache after assigning a new tile (users see "old" Launchpad).
- Treating Fiori activation as an afterthought; it's a multi-week activity for a real S/4HANA system.

### Related skills

`sap-sum-dmo`, `sap-clean-core-extensibility`
