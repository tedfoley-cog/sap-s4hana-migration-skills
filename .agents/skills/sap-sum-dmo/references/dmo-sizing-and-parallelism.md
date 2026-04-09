# DMO Sizing and R3load Parallelism Reference

> **Sources**: [DMO Guide](https://help.sap.com/doc/38301960cfe4484587f9ce5e8e3c4ea0/Latest/en-US/dmo_of_sum2_to_hana.pdf), [SAP Note 2882748](https://me.sap.com/notes/2882748), [SAP Note 1872170](https://me.sap.com/notes/1872170). Apache-2.0 license applies to this reference file; SAP content is paraphrased and cited.

## Contents

- [Target HANA Sizing](#target-hana-sizing) — memory estimation, disk space during DMO
- [R3load Parallelism Tuning](#r3load-parallelism-tuning) — key parameters, tuning guidelines, time estimation
- [Downtime-Optimized DMO (dDMO) Technical Details](#downtime-optimized-dmo-ddmo-technical-details) — trigger-based replication, prerequisites

## Target HANA Sizing

When sizing the target SAP HANA database for a DMO-based system conversion, do **not** use the raw source database size as the baseline. S/4HANA simplifications consolidate many tables, often reducing the data footprint significantly:

| Consolidation | Old tables | New table | Typical size reduction |
|---|---|---|---|
| Material documents | MKPF, MSEG | MATDOC | 10–30% smaller due to header/item merge |
| Financial documents | BKPF, BSEG, FAGLFLEXA, COEP | ACDOCA | Varies; Universal Journal may grow due to line-item detail |
| Condition records | KONV (partially) | PRCD_ELEMENTS | Depends on pricing complexity |
| Business Partner | KNA1, LFA1, KNB1, LFB1 | BUT000, BP_CENTRALDATA | Slight reduction from deduplication |

### Sizing methods

1. **SAP Quick Sizer** ([service.sap.com/sizing](https://service.sap.com/sizing)) — provides HANA memory and disk estimates based on workload benchmarks.
2. **`/SDF/HDB_SIZING` report** — run in the source system to estimate the HANA memory footprint based on actual table sizes after simplification adjustments ([SAP Note 1872170](https://me.sap.com/notes/1872170)).
3. **Rule of thumb**: Plan for HANA memory = **1.5–2x the net data volume** (after compression). HANA column-store compression typically achieves 3–5x compression on transactional data.

### Disk space during DMO

During the DMO migration, SUM requires significant temporary disk space on both source and target:

- **Source side**: Space for R3load export files ≈ 50–80% of the source DB size (uncompressed export).
- **Target side**: HANA data volume + HANA log volume + SUM working space.
- **SUM directory**: At least 50 GB free for SUM's own working files and logs.

## R3load Parallelism Tuning

R3load is the data migration engine used by DMO. Each R3load process handles one table (or one table split) at a time.

### Key parameters

| Parameter | Description | Typical range |
|---|---|---|
| `PARALLEL_JOBS_RLOAD` | Number of parallel R3load export/import processes | 8–32 |
| `TABLE_SPLITTING` | Enable splitting of large tables into parallel chunks | `TRUE` / `FALSE` |
| `MAX_SPLIT_PARTS` | Maximum number of splits per table | 4–16 |
| `MIGRATION_KEY` | The migration key from SAP (required for DMO) | From SAP Launchpad |

### Tuning guidelines

1. **Start with CPU cores / 2** as the parallel job count (e.g., 16 cores → 8 parallel R3load jobs). Monitor CPU and I/O utilization during rehearsal; increase if resources are underutilized.
2. **Enable table splitting** for tables larger than 10 GB. The top candidates for splitting in a typical ECC system:
   - `BSEG` — often the largest table; split by company code or fiscal year
   - `CDPOS` — change documents; split by object class
   - `MSEG` — material documents
   - `ACDOCA` — if Universal Journal is already partially populated
   - `NAST` — message status records
   - `EDIDS` — IDoc status records
3. **I/O bandwidth** is usually the bottleneck, not CPU. Place the R3load export directory on fast storage (SSD or high-throughput SAN). On the target side, ensure the HANA data and log volumes are on separate physical devices.
4. **Network bandwidth** (for DMO with System Move): The source-to-target network link must sustain the full R3load throughput. A 10 Gbps link is the minimum recommended for databases > 1 TB.

### Estimating migration time

A rough formula for R3load migration time:

```
Migration time (hours) ≈ Source DB size (TB) × 48 / parallel_jobs
```

The constant `48` represents the approximate hours a single R3load process needs per TB of data (including export, transfer, and import). This varies significantly with I/O performance.

Example: 4 TB source, 16 parallel jobs → 4 × 48 / 16 = **12 hours**.

This is a rough estimate. Actual times depend on:
- Source DB I/O performance (read throughput)
- Network latency and bandwidth (for System Move)
- HANA import throughput (write performance)
- Table size distribution (a few very large tables can become bottlenecks even with splitting)

## Downtime-Optimized DMO (dDMO) Technical Details

dDMO uses trigger-based replication to minimize downtime ([SAP Note 2393060](https://me.sap.com/notes/2393060)):

1. **Uptime phase**: SUM installs database triggers on the source tables. These triggers capture all DML changes (INSERT, UPDATE, DELETE) into shadow logging tables.
2. **Initial load**: R3load performs a full data migration to HANA while the source system is online. Users continue working normally.
3. **Delta synchronization**: SUM replays the accumulated trigger logs to bring the target HANA database up to date. Multiple delta cycles may run to reduce the remaining delta.
4. **Downtime phase**: SUM stops the application, applies the final delta, and performs the repository switch. Only the last delta + repository switch + data conversions occur during downtime.

### dDMO prerequisites

- Source database must support trigger-based change capture (Oracle, DB2, SQL Server, ASE — **not** MaxDB).
- Additional source DB storage for trigger logging tables: plan for 10–20% of the source DB size.
- SUM SP level must support dDMO for the target S/4HANA release (check [SAP Note 2393060](https://me.sap.com/notes/2393060) for the compatibility matrix).
- The source system must have sufficient CPU headroom for the trigger overhead during uptime migration (typically 5–15% additional CPU load).
