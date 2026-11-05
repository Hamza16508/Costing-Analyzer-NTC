# Gate 0 report (2 Nov 2026)

Phase 0 is **closed**: Hamza signed it off on 5 Nov 2026 ("Yes please close out phase 0"). Phase 1 runs in a new thread.

## What was built (design only, no application code)

| File | Content |
| --- | --- |
| `docs/phase0/schemas/*.schema.json` | the six contracts, JSON Schema 2020-12, draft 0.1: purchase_record, factor_definition, factor_value, global_event, competitor_record, breakdown_output |
| `docs/phase0/po-mapping.md` | column mapping, material keys, re-verified findings, flags applied at rebuild |
| `docs/phase0/decisions.md` | every decision of 2 Nov 2026 plus the v1 method and parameters |
| `docs/phase0/storage-adapter.md` | access check result, data flow, classes, analyzer collections, limits |
| `docs/phase0/ci-mapping.md` | causal-identifier/2 keys as read from the live page, field mapping, factor-to-cause links, event category mapping |
| `docs/phase0/coverage.md` | coverage by source and year 2016–2026, spot-verification log, gaps |
| `.gitignore` | `.env`, `.env.*`, `secrets/`, snapshots, outputs, Excel files |
| `scripts/` | read-only check scripts used below, plus the schema generator |

Nothing was written to any database, and no artifact was created.

## Checks run (no tests at this gate)

1. **Databank access: works.** This session has Artifact and ArtifactData. All six Causal Identifier collections were listed read only: po 11 docs (v3), ext 8, events 53, comp 1 (v3), config 1 (v2), news 6. Versions are recorded in storage-adapter.md. The Phase 0 blocker in the brief does not apply.
2. **Causal Identifier data vs the brief: all match.** ext tag counts per series are exactly as stated; events 53 / 48 relevant / 31 sourced; config shares and schedule as stated; po/2025 = 255,189 bytes.
3. **PO export vs the brief: matches, with five differences:**
   - LEGACE_CODE has 8 distinct codes, plus blank on 143 lines (the "9" counted blank).
   - The 2026 median price 745.5 holds for KGS nylon-cord lines; over all 2026 lines it is 728.9.
   - Burlytex receipt 103502 has **two** lines, not one: same item, 19,503 kg each, same PO, bilty and vehicle; one at 956,415,064 PKR/kg, the other at 956.415 PKR/kg (see Q1).
   - The two 2018 code/description conflicts are the same receipt, 41304 on 2018-08-27, where the two lines look swapped.
   - The two TEXTILE lines are a polyester 840D/2 and a nylon 1260D/3; both stay excluded by category.
   Everything else is confirmed: 36 columns, 1,989 lines, dates, counts, KGS 22,235,206.57 kg, Q_VALUE = qty × price on all lines, one freight value per receipt on 765 lines, receipt 132135 (26,278 kg at 1 PKR/kg), the 8 Service Long March zero-price lines, Hanif 28753, chafer 55748, identical lines 75257 and 146081, local tyre-maker suppliers, gaps in Dec 2018 and Jul 2020.
4. **Duplicate in the Causal Identifier's po: confirmed.** 3,978 rows: every file line appears once on its date and once a day earlier, nothing else. For the page owner; not fixed.
5. **causal-identifier/2 keys: confirmed** from the live page's data. One clarification: verdict, score and netPush sit inside `snapshot`.
6. **Schemas:** all six pass the 2020-12 metaschema; a sample factor definition validates, and one with an unknown field or a window_mean without a window is rejected.

## Coverage gaps (detail in coverage.md)

- **Caprolactam and benzene**, the two biggest factors, have no usable free history (4 and 6 verified points). SunSirs and 100ppi show a bot check; ChemAnalyst needs credentials. Until then those factors are missing in most months and their weight goes to the remainder.
- **USD/PKR**: 3 verified points. The SBP history file could not be opened from this session, so all USD figures stay approximate.
- **PBS CPI, Oct 2016 to Jun 2019, national 2015-16 base**: not confirmed from PBS. The only free file found is urban and commodity-wise.
- **Freight**: no China–Karachi lane exists. The NCFI overview lists no India or Pakistan lane at all, which corrects the survey note. The SCFI composite stands in, and its history comes from a third-party compilation.
- **Competitor raw-material prices**: none until GlobalWits or Volza credentials arrive.
- **Network**: this session's shell is blocked by the environment's network policy (403) for sbp.org.pk, fred.stlouisfed.org, api.eia.gov and every other source host. Pages can be read through the page-fetch tool, but Excel and CSV files cannot.

## Open questions: answered 2 Nov 2026

All seven are answered; details in decisions.md ("Answers to the Phase 0 open questions").

- Q1 Burlytex 103502: the 956,415,064 line is a duplicate entry, excluded from pricing and volume; the 956.415 line is priced.
- Q2 Origin: from vendor name where stated; traders and agents `unknown` until the owner names a mill country.
- Q3 Repository: Hamza16508/Costing-Analyzer-NTC.
- Q4 `host_cause` added to the factor definition.
- Q5 Event types `supply_policy` and `capacity_cycle` added.
- Q6 The owner will allow the seven source hosts in the cloud environment.
- Q7 **Provisional:** third-party PBS CPI copy for 2016–2019, tagged `third_party`. **Re-ask the owner at Gate 1.**

Schema changes from these answers (still draft 0.1): purchase flag `duplicate_entry`; factor_definition `host_cause`; factor_value `source_tier`; event types 9 → 11.

## Addendum, 3 Nov 2026: licensed and free sources

- ChemAnalyst, GlobalWits and Volza are recorded as company-licensed, with logins to follow. Adapter slots and `.env` variable names are reserved (sources.md, `.env.example`), and nothing is built for them yet.
- SunSirs is added. A search for free, verified sources found the NBS 10-day benzene price, read on the source page for Nov 2016 and Oct 2026, which closes the benzene gap. Caprolactam still has no free series confirmed readable from 2016; the candidates are listed in sources.md and get tested first in Phase 1.

## Clearing round, 3 Nov 2026

All ten remaining issues are answered; see decisions.md ("Phase 0 clearing round"). Summary:
1 free caprolactam sources plus customs unit values, cited as footnotes; licensed slots kept · 2 SunSirs tested first, then ask for a login · 3 ask Hamza for bank LC rates, SBP as fallback · 4 third-party CPI copy settled · 5 procurement table plus Claude search (origin-table.md) · 6 both CI-based and learned weights; Hamza chooses in Phase 3 · 7 base month computed from coverage in Phase 1 · 8 **PO price is landed cost** · 9 freight revisited in Phase 1 with Hamza's FOB/CFR data · 10 Causal Identifier data fixed at integration.

Carried into Phase 1 as tasks: ask for bank LC rates; ask for freight attachments and the FOB/CFR comparison; SunSirs access test; continued origin search; base month per construction.

## PO questionnaire, 4 Nov 2026

The filled questionnaire (Mohsin Ali) is recorded as po-knowledge.md and `config/po_knowledge.json`. New findings: 16 provisional whole-number prices, 93 Export Facilitation Scheme imports in 2025–26, blank FREIGHT_CHARGES meaning freight is already in the price, 68 import lines missing their LC number, and EPI affecting price. Blank items are listed in po-knowledge.md.

## Sign-off requested

From the owner and the host team: the six contracts, the v1 method (decisions.md) and the breakdown output record.

## Final answers, 5 Nov 2026

Mohsin's final answers are in po-knowledge.md section 10 (PK-39 to PK-41) and `config/po_knowledge.json` v1.2.0. Every PO follow-up is answered. Still open: the Period Cost note (cut off in the copy), caprolactam history before Jul 2025 (paid SunSirs purchase or free sources), permission to push the cost-sheet figures, and Gate 0 sign-off.

## Sign-off, 5 Nov 2026

Hamza closed Phase 0. Carried into Phase 1: the Period Cost note (PK-41), caprolactam history before Jul 2025, the 2017–2021 data Hamza said was coming, and permission to push the cost-sheet figures to GitHub.

Answers of 5 Nov 2026 to the carried points: push everything to GitHub, cost-sheet amounts included (3B). Caprolactam before Jul 2025: free public sources, footnoted, for now; buying SunSirs history is revisited in Phase 5 (2A). Period Cost: Mohsin is resubmitting his note.
No more data is coming (Hamza, 5 Nov): all caprolactam history before Jul 2025 comes from free public sources. Only Mohsin's Period Cost note is pending.
