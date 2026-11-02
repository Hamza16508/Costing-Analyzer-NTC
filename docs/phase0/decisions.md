# Decisions and v1 method (taken 2 Nov 2026; do not reopen without the owner)

Status: for Gate 0 sign-off by the owner and the host team.

## Scope and placement

- The analyzer is its own codebase (Python module, CLI, JSON contract) and its own private claude.ai artifact with its own database. Everything the analyzer writes goes to that database.
- The Causal Identifier (https://claude.ai/artifact/Nor2zMiP5j1HREuKg6BtFJ, schema causal-identifier/2) is the later host. Its database is read only to the analyzer. Integration happens only on the owner's command. Until then the analyzer's own database is the working databank.
- Runtime: Python run by Claude Code. Phase 5: a button on the analyzer's page fires a Claude Code Remote trigger; results are written to the page's database and shown there.
- Scope: nylon tyre cord first; other materials reuse the build later, each with its own Causal Identifier page.
- Login sources (ChemAnalyst, GlobalWits, Volza, more later) are "pending credentials". Credentials will come from a git-ignored `.env`. Phase 1 uses free sources only.
- Factor-contract sign-off: the owner plus the host team.

## Currency and real prices

- Every figure in both PKR and USD, labelled: PKR as paid; USD at the SBP rate for the delivery date; each also in real terms.
- Real-price base month: **Sep 2026**.
  - PKR is deflated with PBS CPI (national, 2015-16 base).
  - USD is converted first, then deflated with US CPI-U NSA (FRED CPIAUCNS).
  - Index, base month and vintage are recorded on every output row.
- USD outputs are flagged `usd_approximate` until USD/PKR is re-sourced from SBP.

## Material keys

- One key per cord construction, read from ITEM_DESCRIPTION: 840D/2 (1,194 lines), 1260D/2 (272), 840D/1 (144), 1890D/2 (129), 1260D/1 (127), chafer (79).
- Excluded: CLOTH (42) and TEXTILE (2).

## PO data

- Rebuilt from the original file into the analyzer's own database: one copy per line, the file's dates, full precision.
- Excluded from pricing and volume: the four 1 PKR/kg lines of receipt 132135 on 2025-03-12 (provisional entry, 26,278 kg).
- Excluded from pricing, kept in volume: the 8 Service Long March zero-price transfers (intercompany); Hanif receipt 28753; Burlytex receipt 103502.
- Kept and flagged: identical lines on receipts 75257 and 146081; the two 2018 code/description conflicts (classified by description).
- Price basis unknown: Phase 3 tests "supplier invoice only" against "landed cost" and reports which fits.

## Competitor records

- A competitor record is the price a competitor pays for its raw materials (e.g. customs import records).
- Tyre selling prices are out of scope.
- The owner's purchases from other tyre makers are not competitor records.
- Not competitors: Service Industries (owner) and Service Long March Tyres (subsidiary).

## Parameters (config v0.1)

| Parameter | Value |
| --- | --- |
| Remainder flag threshold | 10% of price; tune after the backfill |
| Missing-data tolerance | daily 7 days, weekly 14 days, monthly 1 month, quarterly 1 quarter |
| Minimum past cases per event type | 3 |
| Base month per material | first month with a purchase and full verified factor coverage, not earlier than Oct 2016 |
| Point-in-time | a value is visible only if its observation period starts on or before the purchase date; `published_at` is stored so a stricter "known by then" mode can be switched on later |

## Gates

- Phase 2 samples: five, chosen by Claude: one per main construction, spread across years, one flagged line.
- Phase 4 test points: Claude proposes dates where both the owner's purchases and competitors' raw-material prices exist; the owner confirms.

## Integration (decided at integration)

Phase 5 builds both forms; the owner chooses when giving the command:
- (a) analyzer values replace the Causal Identifier's estimated shares and weights, labelled;
- (b) analyzer values are written beside them in an `analyzer` object.

## Database access rules

- Change nothing on the Causal Identifier.
- On the analyzer's own database, only Editors write.

## v1 method: index-linked cost model

Each factor's weight is its share of the price in a base month; its contribution moves with that factor since then. Factor values are converted to the purchase's currency at the delivery date before the ratio.

```
P̂_t   = P_B × [ w_0 + Σ_i w_i × F_i,t / F_i,B ]
C_i,t = P_B × w_i × F_i,t / F_i,B
R_t   = P_t − P̂_t − E_t
```

- P_t: real price per kg. P_B: the material's average real price in its base month B.
- w_i: default weight from the factor definition. w_0 = 1 − Σ w_i: untracked conversion and margin, constant in real terms.
- E_t: event adjustment. R_t: unexplained remainder.
- Each breakdown is computed in real PKR and in real USD.

Rules:
- Event impact for type k = average remainder share in past months with k, minus the average in months without k, using only history before the purchase date. Fewer than 3 past cases: no adjustment, flag `thin_event_history`.
- A factor with no value within tolerance drops out of P̂_t; its share falls into R_t and the line is flagged `missing_factor`. No year is dropped.
- A remainder above 10% is flagged `remainder_above_threshold`.

## Working rules (all phases)

- Point-in-time only: no data dated after the purchase date is used in a run.
- Every sourced value is stored with source link, unit and retrieval timestamp.
- No fabricated or estimated numbers; a value that can't be found is recorded as missing, with the attempt.
- No secrets in the repository.
- A report at every gate: what was built, test results, coverage gaps, open questions.

## Notes added at Phase 0 (for sign-off; no decision changed)

- Real-price units: the base-month CPI index value is also stored (`index_value`) so a reader can recompute the deflation.
- Breakdown flags beyond the three named in the method: `stale_factor` (value used is inside tolerance but older than its declared lag), `usd_approximate`, `no_base_period`, and the purchase flags carried through. Listed in the breakdown schema.
- The w_0 amount is reported as `untracked` on the breakdown, so explained_total = Σ C_i + untracked + E.
