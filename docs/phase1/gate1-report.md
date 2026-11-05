# Gate 1 report: databank and base months

Date: 5 Nov 2026. Config `v0.1-ci`. PO file sha256 `195acf95…`.

The analyzer has its own artifact and database: https://claude.ai/artifact/742kXPXMJXT5vWkf7JtsLe
(118 documents: 27 purchase-record docs, 89 factor-series docs, `coverage/summary`, `config/settings`).
The Causal Identifier artifact was only read, never written.

## 1. What was built

- `analyzer/po.py` turns the ERP PO export into 1,989 purchase records (schema 0.2) with the Phase 0 flags and exclusions.
  1,960 lines are priced; 22.19 million kg delivered.
- `analyzer/sources/` fetches each factor with its source link, unit, retrieval time and tier on every value.
  A period with no value is stored as `missing` with the attempt recorded; nothing is estimated.
- `analyzer/coverage.py` applies the point-in-time and tolerance rules and finds each construction's base month.
- `scripts/build_db.py` validates every record against `schemas/`, splits the docs (< 200 KiB each) and writes the coverage summary the page shows.
- Tests: `tests/test_phase1.py`, 5 passed (`NTC_PO_XLSX=<path> python -m pytest tests`).

### Flags on the 1,989 PO lines

| Flag | Lines |
| --- | ---: |
| freight_in_price (blank FREIGHT_CHARGES) | 1,224 |
| efs_import | 93 |
| missing_lc_number | 68 |
| usance_fx (30/60/90-day terms) | 44 |
| excluded_from_pricing | 29 |
| provisional_price (PK-09, PK-10) | 15 |
| intercompany | 8 |
| excluded_from_volume | 5 |
| provisional_duplicate | 4 |
| identical_line | 4 |
| code_description_conflict | 2 |
| duplicate_entry | 1 |

### Purchases by construction

| Construction | Lines | kg | Priced | First | Last | Median 2026 import PKR/kg |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| 840D/2 | 1,194 | 15,790,425 | 1,176 | 2016-10-19 | 2026-10-24 | 751.3 |
| 1260D/2 | 272 | 2,541,963 | 269 | 2016-12-29 | 2026-10-24 | 760.6 |
| 840D/1 | 144 | 1,312,440 | 144 | 2016-10-19 | 2026-10-24 | 707.6 |
| 1890D/2 | 129 | 1,282,346 | 127 | 2017-06-24 | 2026-10-24 | 679.1 |
| 1260D/1 | 127 | 1,078,401 | 121 | 2022-04-21 | 2026-09-17 | 643.3 |
| chafer | 79 | 181,799 | 79 | 2016-12-29 | 2026-10-24 | 1,079.6 |

## 2. Factor series loaded

| Series | Unit | Tier | Periods with a value | From | To |
| --- | --- | --- | ---: | --- | --- |
| Caprolactam, China import unit value (UN Comtrade 293371) | USD/t | primary | 95 / 130 months | 2017-01 | 2024-12 |
| Caprolactam, China market (Hamza's SunSirs file) | CNY/t | company | 352 / 352 days | 2025-07-01 | 2026-11-04 |
| Caprolactam, Haiyang avg purchase price (SSE filings) | CNY/t ex VAT | primary | 7 quarters | 2024 Q3 | 2026 Q3 |
| Benzene, China 10-day market price (NBS) | CNY/t | primary | 172 / 172 | 2021-11 | 2026-10 |
| US PPI aromatics (benzene cross-check, FRED) | index | primary | 135 / 135 | 2015-07 | 2026-09 |
| Container freight, SCFI composite | index | third party + primary | 545 / 545 weeks | 2016-01-08 | 2026-10-30 |
| USD/PKR, SBP M2M (company file) | PKR per USD | company | 2,788 days | 2015-07-02 | 2026-11-03 |
| CNY/PKR, SBP M2M (company file) | PKR per CNY | company | 2,788 days | 2015-07-02 | 2026-11-03 |
| USD/CNY, FRED H.10 | CNY per USD | primary | 2,832 / 2,958 | 2015-07-01 | 2026-10-30 |
| Brent crude (FRED / EIA) | USD/bbl | primary | 2,881 / 2,960 | 2015-07-01 | 2026-11-03 |
| Pakistan national CPI (PBS, 2015-16 base) | index | primary | 112 / 130 months | 2017-07 | 2026-10 |
| US CPI-U NSA (FRED) | index | primary | 134 / 135 | 2015-07 | 2026-09 |
| Nylon tyre cord, China export unit value (Comtrade 590210) | USD/kg | primary | 96 / 130 | 2017-01 | 2024-12 |
| Nylon tyre cord, Pakistan import unit value (Comtrade 590210) | USD/kg | primary | 120 / 130 | 2016-01 | 2026-01 |

Notes:
- Comtrade's China rows for 2016 carry one flat value in every month (an annual figure spread over months), so 2016 is stored as missing. China has not reported 2025–26 yet.
- SCFI history comes from the GYUL91 compilation on GitHub (third party); the SSE site gives only the latest weeks without a login. The two agree on the overlapping weeks (3,687.35 and 3,681.34).
- The current NBS site lists releases from Nov 2021 only. Benzene is not in the v0.1-ci weights.
- The Haiyang values are dated by the announcement in which they were read. A comparative figure (for example 2025 Q1, read in the 2026 Q1 report) carries the later date.

## 3. Base month per construction

Rule: the first month at or after Oct 2016 in which every priced import line has a usable value for every factor (caprolactam, freight and USD/CNY at receipt minus 45 days; USD/PKR at receipt; PBS CPI and US CPI-U for the month).

| Construction | Base month (Comtrade caprolactam) | Lines in month | With the SunSirs file instead | What held it back |
| --- | --- | ---: | --- | --- |
| 840D/2 | **2017-07** | 11 | 2025-09 | PBS CPI and caprolactam missing before Jul 2017 |
| 1260D/2 | **2017-08** | 1 | 2025-09 | same |
| 840D/1 | **2017-07** | 2 | 2025-08 | same |
| 1890D/2 | **2017-07** | 1 | 2025-10 | PBS CPI (first purchase Jun 2017) |
| 1260D/1 | **2022-04** | 1 | 2025-09 | none: first purchase month |
| chafer | **2017-08** | 1 | 2025-08 | PBS CPI and caprolactam |

The binding gap for five constructions is PBS CPI before Jul 2017 (PBS's historical file starts there) together with Comtrade caprolactam before Jan 2017.

## 4. Freight check

- The PO export carries no FOB, CFR or CIF term in any field. Mohsin's questionnaire answer (Q11) is CFR throughout.
- FREIGHT_CHARGES holds inland freight only: its median share of the landed price is 0.8–1.7% a year. It is filled on ~95% of import lines in 2016–2020 and on ~2% in 2026, so blank lines are flagged `freight_in_price`.
- Comparison documents (a CFR invoice next to its freight bill, or a FOB quote) are needed to estimate the ocean-freight share. Asked from Hamza.

## 5. Mill-country search

See `docs/phase0/origin-table.md`, Phase 1 section. G.T. Trading resolved from gtrel.com and Tradesparq; Burlytex and Stalwart from the Volza directory; Shifeng and Suzhou Kingdom set to China from the vendor name. 62 local-agent lines still have an unknown mill country.

## 6. Open items for Hamza

1. **SunSirs login** (or a 100ppi login): the site blocks automated access. Without it, caprolactam for Jan 2025 to Jun 2025 rests on the Haiyang quarterly figures only.
2. **PBS CPI for Oct 2016 to Jun 2017**: back-calculate from PBS's published year-on-year rates, keep looking for a copy, or leave it missing (base months stay in Jul–Aug 2017).
3. **FOB/CFR comparison documents** for the ocean-freight share.
4. **Which caprolactam series is primary**: Comtrade (monthly, ends Dec 2024) or the SunSirs file (daily, from Jul 2025), and whether to chain-link them through the Haiyang quarters.
5. **Free UN Comtrade key** (`COMTRADE_API_KEY` in `.env`) for faster, complete Comtrade pulls; the public preview works without one.
