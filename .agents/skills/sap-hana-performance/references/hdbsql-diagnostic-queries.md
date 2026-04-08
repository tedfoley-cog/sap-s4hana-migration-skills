# hdbsql Diagnostic Queries for HANA Performance

> **Sources**: [SAP Help: hdbsql](https://help.sap.com/docs/hana/sap-hana-client-interface-programming-reference),
> [SAP Note 2201632](https://me.sap.com/notes/2201632) — SQL Monitor.
> Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

## Table of Contents

- [Environment variables](#environment-variables)
- [Network prerequisites](#network-prerequisites)
- [Queries](#queries)
  - [Top expensive custom SQL statements](#top-expensive-custom-sql-statements)
  - [Execution plan for a specific query](#execution-plan-for-a-specific-query)
  - [Column-store table memory consumption](#column-store-table-memory-consumption)
- [Usage notes](#usage-notes)

## Environment variables

- `HANA_HOST`, `HANA_USER`, `HANA_PASSWORD`

## Network prerequisites

HANA port 443 (Cloud) or 3\<sysnr\>15 (on-prem).

## Queries

### Top expensive custom SQL statements

```bash
# Top 20 most expensive custom SQL statements (by total execution time)
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT TOP 20 STATEMENT_HASH, USER_NAME, EXECUTION_COUNT,
          TOTAL_EXECUTION_TIME, AVG_EXECUTION_TIME,
          SUBSTR(STATEMENT_STRING, 1, 200) AS SQL_PREVIEW
   FROM M_EXPENSIVE_STATEMENTS
   WHERE USER_NAME LIKE 'SAP%' OR USER_NAME LIKE 'Z%'
   ORDER BY TOTAL_EXECUTION_TIME DESC"
```

### Execution plan for a specific query

```bash
# Replace <hash> with statement hash from the query above
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "EXPLAIN PLAN FOR SELECT ebeln, ebelp, matnr FROM ekpo WHERE ebeln = '4500000001'"
```

### Column-store table memory consumption

```bash
# Find largest custom tables by memory consumption
hdbsql -n "${HANA_HOST}:443" -u "${HANA_USER}" -p "${HANA_PASSWORD}" -encrypt \
  "SELECT TOP 20 SCHEMA_NAME, TABLE_NAME,
          ROUND(MEMORY_SIZE_IN_TOTAL / 1024 / 1024, 2) AS SIZE_MB
   FROM M_CS_TABLES
   ORDER BY MEMORY_SIZE_IN_TOTAL DESC"
```

## Usage notes

- Cross-reference `M_EXPENSIVE_STATEMENTS` results with SQLM findings (Step 1) to prioritize remediation.
- Large custom tables in `M_CS_TABLES` may need partitioning or archiving for optimal column-store performance.
