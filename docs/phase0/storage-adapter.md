# Storage adapter (Phase 0 design, for gate approval)

## Access verified on 2 Nov 2026

This Claude Code session has both tools:
- **Artifact** (read): the Causal Identifier page read successfully (owned by the owner; live version 1793257870-2097, 262,328 bytes).
- **ArtifactData** (list/get/query/set/update/batch/delete, writes pinned with `if_version`): all six Causal Identifier collections listed, read only.

Causal Identifier databank as read (documents and versions):

| Collection | Docs | Versions | Notes |
| --- | --- | --- | --- |
| po | 11 (2016–2026) | all v3 | {year, cols[17], rows, source, loadedAt}; 3,978 rows (each line twice); po/2025 = 255,189 bytes vs 262,144 cap |
| ext | 8 | benzene v2, brent v4, cpl v2, freight v3, haiyang v1, pama v1, usdcny v2, usdpkr v1 | tag counts match the brief exactly |
| events | 53 | 21 at v2, 32 at v1 | 48 relevant, 31 with a source link |
| comp | 1 (public-research) | v3 | 7 financials, 2 leads, 0 import unit values |
| config | 1 (settings) | v2 | collector daily 08:00 Asia/Karachi; structural shares as stated; triggerId present |
| news | 6 (2026-10-28 … 2026-11-02) | 2026-10-29 at v3, others v1 | the collector keeps adding one per day |

Python in this container cannot reach the artifact database; the shell's outbound network is also restricted (see coverage.md). Claude is the carrier.

## Data flow

1. **Sourcing adapters** (Python, one per source) write schema-checked **batch files** under `out/batches/` (JSON, ≤ 50 writes each, ≤ 1 MiB). They never touch a database.
2. **Claude applies batches** to the analyzer's database with ArtifactData `batch`: each write pinned with `if_version` to the version read; creates carry no pin. On a version conflict the batch writes nothing; Claude re-reads, regenerates and retries. Each applied batch is logged to `out/applied/` with result versions.
3. **Snapshot export before a run**: Claude reads the analyzer's collections, plus the Causal Identifier collections the run needs, with `out_dir`, into `snapshots/<UTC timestamp>/<db>/<collection>/<doc>.json`, and writes `manifest.json` (doc ids, versions, sha256 per file) and `snapshot.sha256` (hash of the manifest).
4. **The analyzer reads only the snapshot**, through `AsOfView(store, purchase_date)`:
   - refuses (raises) any record whose `applies_on`/`period_start` is after the purchase date;
   - logs every read (series_id, period_start, vintage);
   - the point-in-time test asserts no logged read is later than its purchase date;
   - every output carries the snapshot hash as `databank_snapshot`.

## Source adapters

One adapter per source behind a common `SourceAdapter` interface, with slots reserved for the company-licensed platforms (ChemAnalyst, GlobalWits, Volza) whose logins come later. A licensed adapter without credentials reports `pending_credentials` and is skipped, and the skip is logged. Details in sources.md.

## Python classes (Phase 1)

| Class | Role |
| --- | --- |
| `Databank` (Protocol) | `get(collection, id)`, `list(collection)`, `query(collection, where)`; read-only interface the engine sees |
| `SnapshotStore(Databank)` | loads a snapshot directory, verifies the manifest hash, exposes records |
| `MemoryStore(Databank)` | in-memory store for tests and golden files |
| `BatchWriter` | validates records against the six schemas, splits into ≤ 50-write / ≤ 1 MiB batch files, records `if_version` from the snapshot it was built against |
| `AsOfView` | point-in-time guard around any `Databank`, with read log |

## Analyzer database collections

Names mirror the Causal Identifier where they exist, for compatibility only. The analyzer never writes to the Causal Identifier (standing rule, 3 Nov 2026).

| Collection | Doc id | Content | Expected docs |
| --- | --- | --- | --- |
| po | `<year>` (split `<year>-<n>` if a doc nears 200 KiB) | purchase records for the year, one per line, file dates, full precision | 11–20 |
| ext | `<series_id>` (split by year if large) | factor value series, records per the factor_value schema | ~20–60 |
| events | `<event_id>` | global events | ~60–150 |
| comp | `<competitor_id>-<year>` | competitor records | ~20–80 |
| config | `settings`, `competitors`, `changelog` | run parameters (config version), competitor registry with aliases, config changelog | 3 |
| factor_defs | `<material slug>` (840D-2 …) | factor definitions for one material | 6 |
| breakdowns | `<config_version>-<YYYY-MM>` | breakdown outputs per config version and month | ~121 per config version |
| event_types | `<event_type>` | learned impacts per type (as_of, value, n_cases) | 9 |
| coverage | `<series_id>` or `summary` | coverage by source and year, attempts | ~20 |

Limits: 25,000 documents per database; 256 KiB (262,144 bytes) per document. Expected total under 1,000 per config version. Size guard: any doc over 200 KiB is split before writing (the Causal Identifier's po/2025 at 255,189 bytes is the warning case). Breakdowns: ~16 lines per month on average; the busiest month must be checked against the cap in Phase 2, splitting to `<config>-<YYYY-MM>-<n>` if needed.

## Access rules

- Causal Identifier: no writes, no rule changes (it uses default rules: anyone at Contributor can write).
- Analyzer database: only Editors write; viewers read. Set when the artifact is created (Phase 1), via the `db` capability rules.

## Open design points

- Doc ids cannot contain `/`, so material keys use a slug (`840D/2` → `840D-2`).
- `breakdowns` per config version and month means a re-run under a new config version adds docs; old versions are kept for comparison and pruned only on the owner's word.
