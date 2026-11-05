# Decisions and v1 method (taken 2 Nov 2026; do not reopen without the owner)

Status: for Gate 0 sign-off by the owner and the host team.

## Scope and placement

> **Standing rule (Hamza, 3 Nov 2026): the analyzer is a separate, new artifact.** The existing Causal Identifier artifact (https://claude.ai/artifact/Nor2zMiP5j1HREuKg6BtFJ) is never updated: not its page, not its database, not its access rules. It is read only, as a reference and data source. Nothing in these docs plans a change to it. Any future integration happens only on Hamza's explicit command, and the form it takes is decided then.


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
- ~~Price basis unknown: Phase 3 tests "supplier invoice only" against "landed cost" and reports which fits.~~ Superseded 3 Nov 2026: PO_UNIT_PRICE is landed cost (confirmed by Hamza).

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

Only on Hamza's explicit command; nothing is planned. The analyzer stays a separate artifact with its own database. The two forms below are kept as options and prepared as exports in the analyzer's own codebase. Neither is applied to the Causal Identifier unless Hamza commands it:
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

## Answers to the Phase 0 open questions (Hamza, 2 Nov 2026)

| # | Question | Answer |
| --- | --- | --- |
| Q1 | Burlytex receipt 103502 (two identical lines, one at 956,415,064 PKR/kg) | The 956,415,064 line is a duplicate entry: excluded from pricing **and** volume, flags `duplicate_entry`, `excluded_from_pricing`, `excluded_from_volume`. The 956.415 PKR/kg line is priced normally. This replaces "exclude receipt 103502 from pricing". |
| Q2 | Mill country for traders | Set `origin_region` from the vendor name where the name states the mill's country (`origin_basis = vendor_name`). Traders and local agents are `unknown`: Altek, Burlytex, Stalwart, GPS London, Yusheng HK, Crypto Trade, HL Group, Easy Tech, MB & Company, Trade Impex, Qaisar Traders, Bond & Built, Hanif. The owner may name a mill country for any of them later (`origin_basis = confirmed_table`). |
| Q3 | Code repository | github.com/Hamza16508/Costing-Analyzer-NTC (private). |
| Q4 | Linking factors to Causal Identifier causes | Optional `host_cause` on the factor definition: a `causes[].id` or `delivered:<name>`. Freight and USD/PKR map to `delivered:`. |
| Q5 | Event types for OPEC decisions and the caprolactam glut | Two types added: `supply_policy` (OPEC/OPEC+ cuts and unwinds) and `capacity_cycle` (caprolactam glut). Eleven types in all. |
| Q6 | Network for Phase 1 | The owner will allow www.sbp.org.pk, fred.stlouisfed.org, api.eia.gov, www.pbs.gov.pk, data.gdeltproject.org, comtradeapi.un.org and static.cninfo.com.cn in the project's cloud environment. |
| Q7 | PBS CPI national, 2015-16 base, Oct 2016 – Jun 2019 | **Settled 3 Nov 2026 (4A): keep the third-party copy, no re-ask.** Earlier text: **Provisional.** Use a third-party copy for now, stored with `source_tier = third_party`. **Ask the owner again at Gate 1**, with options: keep the copy, or request the official back series from PBS's data centre and replace it. |

## Addendum (Hamza, 3 Nov 2026): licensed and free sources

- **ChemAnalyst, GlobalWits and Volza** are platforms the company already has login access to. The logins will be provided later. The design reserves an adapter slot for each (sources.md), with credentials read from `.env` only. Until then each one is recorded as `pending_credentials`, and nothing that depends on them blocks Phase 1.
- **SunSirs** is an approved source, alongside other free, public, verified sources that Claude finds. Sources found so far: NBS 10-day benzene prices (official, from Nov 2016), China Customs and UN Comtrade unit values, Haiyang filings, and FRED US PPI aromatics as a cross-check.
- When a licensed series arrives, it is placed in the factor definitions' ordered `data_source` lists under a new config version. Free series stay as cross-checks.

## Phase 0 clearing round (Hamza, 3 Nov 2026)

Hamza's wording governs. Where an answer changes an earlier decision, the earlier one is superseded.

| # | Issue | Answer | What it means for the build |
| --- | --- | --- | --- |
| 1 | Caprolactam history from 2016 | **1A + 1C.** Use the free sources (SunSirs, China Customs and UN Comtrade unit values, Haiyang filings), shown as verified and **linked as footnotes**. Also use the official customs import unit values (1C). Wait for the logins for the licensed sources, with room left to add them. | Every value is stored with its link. Reports and docs cite sources as footnotes. Customs unit values form their own series, ranked as a cross-check. ChemAnalyst's slot stays reserved (sources.md). |
| 2 | SunSirs blocks automated access | **2A.** Phase 1 tests access from the new environment first. If that fails, **ask Hamza for a login automatically**. If no login is available, ask permission for 2B (manual export or upload) in a later phase. | Phase 1 tests SunSirs first; on failure Claude asks Hamza for a login. |
| 3 | USD/PKR | **Ask Hamza first for the bank's LC rates** (his input); if he can't provide them, **3A**: SBP's daily file. | Phase 1 opens with a request to Hamza for the LC rates. SBP is the fallback. USD stays `usd_approximate` until one of them covers a date. |
| 4 | PBS CPI, Oct 2016 – Jun 2019 | **4A.** Keep the third-party copy, tagged `third_party`. | Replaces the earlier "provisional, re-ask at Gate 1": settled, no re-ask. |
| 5 | Mill country for traders | **5B** (procurement fills a table), **plus an extensive search by Claude from verified sources.** | origin-table.md drafted. One finding so far (Yusheng → China, provisional, linked). The search continues in Phase 1 (company registries, then Volza/GlobalWits shipper data once connected). |
| 6 | Starting weights per factor | **6A and 6C, both.** Draft v0.1 weights from the Causal Identifier's settings, **and** run the no-prior-weights path that waits for learned weights. **Ask Hamza in Phase 3 which to keep.** | Two config variants: `v0.1-ci` (caprolactam 0.55, freight 0.056, rest untracked; for Hamza and the host team to sign) and `v0.1-learned` (weights from Phase 3 calibration). Phase 3 gate question: which one. |
| 7 | Base month under the full-coverage rule | **7A, figure it out.** Keep the rule; Claude determines each construction's base month from the coverage data. | Base month per construction is computed in Phase 1 from loaded coverage and reported at Gate 1; it may be later than Oct 2016. |
| 8 | Invoice price or landed cost | **ERP PO_UNIT_PRICE is landed cost (confirmed by Hamza).** | Supersedes "price basis unknown; Phase 3 tests both". Factor definitions for v0.1 cover landed-cost parts: material (caprolactam, benzene, conversion), sea freight, FX, and duties and clearing inside the untracked share until a duty series exists. The Phase 3 basis test is dropped. |
| 9 | Freight | **Custom, revisit in Phase 1.** Claude asks Hamza for attachments. Hamza will work out CFR cost by comparing the company's FOB and CFR purchases from China and look for documents that answer it. Claude also looks in the PO history for China shipments. | Phase 1 task: request the FOB/CFR comparison and documents from Hamza, and check PO history (PAYMENT terms, LC, vendor) for freight evidence. SCFI stays as the interim series. |
| 10 | Causal Identifier data issues (duplicate po, shifted dates) | **10C.** Fix at integration time. | **Superseded by the standing rule above:** the Causal Identifier is never changed. The issues are only reported. The analyzer's own database holds the clean, deduplicated PO copy. If Hamza ever commands an integration, he decides then what happens to that page. |

## Network and access remedies (Hamza, 3 Nov 2026)

| # | Problem | Answer | Action |
| --- | --- | --- | --- |
| 1 | This thread's sandbox predates the new allowlist, so every source host returns 403 and Excel/CSV files can't be read | **1A** | Phase 1 runs in a **new thread** on the new environment and tests every source host on day one; results go into coverage.md. |
| 2 | SunSirs and 100ppi show a bot check | **2A** | Both are on the allowlist and tested from the new thread. If they still block, ask Hamza for a SunSirs login (rule 2A of the clearing round). |
| 3 | ChemAnalyst, GlobalWits and Volza need logins | **3A** | Wait for the logins; they go in `.env` only. Slots are reserved (sources.md). |
| 4 | China customs statistics refuse automated tools | **4A** | Use UN Comtrade's API for the same China import data instead. |
| 5 | UN Comtrade needs a free API key | **5A and 5E** | Hamza registers a free key at comtradeplus.un.org (stored as `COMTRADE_API_KEY` in `.env`). **Meanwhile, use the public preview API and other public information.** Every value is linked and tagged with its source. |
| 6 | Hosts missing from the allowlist | **6A** | Hamza adds all 18 hosts himself: sunsirs.com, www.sunsirs.com, www.100ppi.com, www.stats.gov.cn, www.cs.com.cn, stats.customs.gov.cn, english.customs.gov.cn, comtradeplus.un.org, api.stlouisfed.org, archive.sbp.org.pk, easydata.sbp.org.pk, api.gdeltproject.org, en.sse.net.cn, www.cninfo.com.cn, raw.githubusercontent.com, www.chemanalyst.com, www.volza.com, www.globalwits.com (the last two to be checked against the company's login addresses). |

## PO questionnaire answers (Mohsin Ali, 3 Nov 2026; recorded 4 Nov 2026)

Recorded in full in po-knowledge.md and built into the system as `config/po_knowledge.json` (Hamza, 4 Nov: the questionnaire is the knowledge used to train the analyzer on the company's POs; no documents exist to attach; no further PO questions).

Changes to earlier decisions:
- **Identical lines (75257, 146081)** are real deliveries. The `identical_line` flag stays, but is informational only.
- **Mill country (Q5)**: the commercial table is confirmed. Every trader is China except G.T. Trading (Thailand).
- **New flags**: `provisional_price` (16 whole-number import prices, kept in volume and excluded from pricing), `efs_import` (93 Export Facilitation Scheme lines, 2025–26; Phase 3 tests their effect), `freight_in_price` (FREIGHT_CHARGES blank).
- **Import lead time of 40–45 days** sets the starting lag for imported-cord factors.
- **EPI** becomes a material sub-key within each construction.
- Payment terms (TERM_NAME) affect price, and Phase 3 tests the effect.

## Follow-ups to the PO questionnaire (4 Nov 2026)

- **Q3, exchange gain or loss** (Hamza): it applies to landed cost when the LC or import payment is on 30, 60 or 90 days' credit. New flag `usance_fx` (PK-32).
- **Q1, freight**: answered by Mohsin's LC cost sheet. Port-to-factory freight is a line inside PO cost, so FREIGHT_CHARGES is never added again (PK-35).
- **Q2, duties**: partly answered. The sample sheet shows only the Sindh Infrastructure Cess (~1.86%) and no customs, additional or regulatory duty, but it is for HS 3812, not 5902.10.
- **Still open**: Q2 for nylon cord and EFS lines, Q4 corrections, Q5 receipt 89481, Q6 the direction of payment-term pricing, Q7 CFR since 2016.

## Period Cost (5 Nov 2026)

FX gain or loss on credit-term payments is booked after the PO price is final, as Period Cost, so it is outside PO_UNIT_PRICE (PK-42, replacing PK-32). All import lines are converted at the rate near receipt.
