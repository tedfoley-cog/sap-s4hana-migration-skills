# Spaces and Pages in SAP Fiori Launchpad — Deep Dive

> **Sources**: [SAP Note 2659151](https://me.sap.com/notes/2659151), [SAP Note 3023853](https://me.sap.com/notes/3023853), [SAP Help: SAP Fiori Overview](https://help.sap.com/docs/SAP_FIORI_OVERVIEW)
> **License**: Content paraphrased from SAP documentation; original material © SAP SE, used under fair-use citation. This file is Apache-2.0.

## Background

Prior to S/4HANA 2020, the Fiori Launchpad organized content using **Catalogs** and **Groups**:

- A **Catalog** is a technical container bundling tiles, target mappings, and authorization defaults. Catalogs are assigned to roles in PFCG.
- A **Group** is a visual grouping of tiles on the Launchpad home page. Users see Groups as labeled sections on their home screen.

This model had limitations: users saw a flat list of all tiles from all assigned Groups, navigation was limited to scrolling, and personalization options were restricted.

## Spaces and Pages model (S/4HANA 2020+)

SAP introduced **Spaces and Pages** as a modern replacement:

- A **Space** is a top-level navigation entry in the Launchpad shell bar (the horizontal menu at the top). Each Space represents a work area or business role context (e.g., "Sales," "Procurement").
- A **Page** is the content area displayed when a user selects a Space. Pages contain **Sections**, and each Section contains tiles.
- A Space can reference one or more Pages.
- Spaces are assigned to roles in PFCG, similar to how catalogs were assigned.

### Key differences from Groups

| Aspect | Groups (legacy) | Spaces and Pages |
|---|---|---|
| Navigation | Flat scrolling on home page | Shell bar with top-level Space entries |
| Content organization | All tiles in one view | Hierarchical: Space → Page → Section → Tile |
| SAP delivery | SAP delivers Groups per role | SAP delivers Spaces and Pages per role |
| Personalization | Users can hide/show/reorder tiles | Users can reorder tiles within Sections |
| Admin tooling | Launchpad Designer (deprecated) | Manage Launchpad Spaces/Pages Fiori apps |

### Enabling Spaces and Pages

Configuration parameters in `/UI2/FLP_CUS_CONF` (or Manage Launchpad Settings app F3835):

| Parameter | Value | Effect |
|---|---|---|
| `SPACES_ENABLE` | `true` | Enables Spaces and Pages alongside classic home page |
| `SPACES_ONLY` | `true` | Disables classic home page entirely; only Spaces visible |
| `SPACES_ONLY` | `false` | Shows both Spaces navigation and classic home page |

### SAP-delivered content

SAP delivers Spaces and Pages aligned to standard business roles. Naming convention:
- Space: `SAP_<module>_BC_<function>_SP` (e.g., `SAP_SD_BC_SO_MANAGE_SP`)
- Page: `SAP_<module>_BC_<function>_PG` (e.g., `SAP_SD_BC_SO_MANAGE_PG`)

These are assigned to the corresponding SAP business roles (e.g., `SAP_BR_SALES_MANAGER`).

### Custom Spaces and Pages

To create custom content:

1. Use Fiori app **Manage Launchpad Spaces** (App ID `F4545`) to create a Space.
2. Use Fiori app **Manage Launchpad Pages** (App ID `F4546`) to create a Page with Sections and tiles.
3. Link the Page to the Space.
4. Assign the Space to a custom role in PFCG.

### Migration from Groups to Spaces

For existing deployments using Groups:

1. Run report `FLP_MIGRATE_GROUPS_TO_SPACES` or use the Fiori app **Migrate Groups to Spaces**.
2. First execute in **simulation mode** to preview the migration results.
3. Review the mapping: each Group becomes a Section within a Page; a new Space is created to contain the Page.
4. Execute the migration.
5. After migration, enable `SPACES_ONLY = true` to switch users to the new layout.

### Known issues and corrections

SAP Note 3023853 is the central note for Spaces and Pages issues. Common corrections include:

- Performance issues with large numbers of Spaces — addressed in recent SAP_UI component updates.
- Visibility issues where Spaces assigned in sub-roles are not displayed — ensure role aggregation is correct.
- Migration tool not handling dynamic tiles correctly — apply corrections from SAP Note 3023853.

## Catalogs still matter

Even with Spaces and Pages, **business catalogs remain the fundamental authorization and content unit**. Spaces and Pages are a presentation layer on top of catalogs:

- A tile can only appear in a Space/Page if the user's role includes the catalog that contains the tile's target mapping.
- Removing a catalog from a role removes access to those tiles, regardless of Space/Page assignments.
- The catalog-to-role assignment in PFCG still controls both the tile visibility and the underlying authorizations.
