# Source registry and adapter slots (Phase 0 addendum, 3 Nov 2026)

Every sourcing adapter is one Python class behind one interface, registered in `config/sources.yaml` (Phase 1). Each adapter writes schema-checked batch files only (see storage-adapter.md); none writes a database, and none is called during a breakdown run.

## Adapter interface (Phase 1)

```python
class SourceAdapter(Protocol):
    source_id: str                      # e.g. "nbs.benzene", "chemanalyst.cpl"
    access: Literal["free", "free_key", "licensed"]
    requires_env: tuple[str, ...]       # names of .env variables; empty for free sources
    series: tuple[str, ...]             # series_ids it can fill

    def status(self) -> AdapterStatus   # ready | pending_credentials | blocked (with reason)
    def fetch(self, series_id: str, start: date, end: date) -> list[FactorValue]  # values + attempts
```

Rules:
- A licensed adapter whose `requires_env` variables are missing reports `pending_credentials`. It is skipped without error, and the skip is written to `coverage` as an attempt.
- Several adapters may fill the same factor. The factor definition's `data_source` list gives the order of preference, so a licensed series can later rank ahead of a free one **without changing the factor contract**: only the ordered list in the factor definition changes, under a new config version.
- Every value carries `source_link`, `retrieved_at`, `published_at`, `vintage`, `source_tier` and, for licensed data, `licence: company` (stored in `raw`). Licensed values stay inside the analyzer's private database and the company's own outputs; they are never written to the repository.

## Company-licensed sources (logins provided later)

The company holds logins for these three platforms. Credentials will come from the git-ignored `.env`; no adapter is built until they arrive. The slots are reserved now.

| Platform | Adapter slot | Fills | `.env` variables (names only) | Notes |
| --- | --- | --- | --- | --- |
| ChemAnalyst | `chemanalyst` | caprolactam and benzene price series (China, plus other regions as licensed); possibly N6 chips and nylon tyre cord | `CHEMANALYST_USER`, `CHEMANALYST_PASSWORD` (or `CHEMANALYST_API_KEY` if an API is licensed) | Ranks first for cpl and benzene once live; the free series below stay as cross-checks |
| GlobalWits | `globalwits` | competitor raw-material purchase records: importer-level customs rows for HS 5902.10 (and later other tyre inputs) | `GLOBALWITS_USER`, `GLOBALWITS_PASSWORD` (or `GLOBALWITS_API_KEY`) | Feeds competitor_record; `present_fields` records what each row carries |
| Volza | `volza` | the same as GlobalWits; also a second view of the owner's own import landed prices | `VOLZA_USER`, `VOLZA_PASSWORD` (or `VOLZA_API_KEY`) | Rows found on both platforms are de-duplicated by (date, importer, HS code, quantity) |

At connection time, Claude will confirm with the owner whether each platform offers an export or API (preferred) or only an interactive login. For an interactive login, the adapter reads files the owner exports, and those files go in the git-ignored `secrets/` or `out/` folders.

## Free, public, verified sources found (3 Nov 2026)

"Verified" means the page itself was opened and the value read; "search only" means it was seen only in search results.

| Factor | Source | Access | History | Verified | What it gives |
| --- | --- | --- | --- | --- | --- |
| Benzene (China) | **NBS (国家统计局) "流通领域重要生产资料市场价格变动情况"**, 纯苯 (石油苯, 工业级) | free, official, HTML release three times a month | from at least 1–10 Nov 2016 (5,609.4 CNY/t)[^nbs2016] to mid-Oct 2026 (10,492.4 CNY/t)[^nbs2026] | Yes, both ends opened | 10-day national market price, CNY/t. **Closes the benzene gap from Nov 2016.** Oct 2016 releases are to be checked in Phase 1 |
| Benzene (cross-check) | FRED WPU06140197, US PPI Aromatics | free | Aug 2001 – Sep 2026, monthly, index Jun 2001=100[^fredarom] | Yes | US index, not China; backup and direction check only |
| Caprolactam (China) | **SunSirs** (sunsirs.com, same group as 100ppi) | free articles; price-chart history may need membership | articles from at least 2017; Sinopec weekly settlement reported | No: the site serves a bot check to automated fetches | Daily/weekly CPL market price and Sinopec settlement. Needs a browser session or the new network settings; Phase 1 tests access first |
| Caprolactam (China imports) | China Customs statistics (stats.customs.gov.cn), HS 2933.71 | free, official, interactive query | monthly | No: robots-disallowed for automated fetches | Import value and quantity, so a monthly CNY or USD/t unit value. Interactive query; manual export if automation is not allowed |
| Caprolactam, N6 cord (trade unit values) | UN Comtrade monthly (comtradeapi.un.org), HS 2933.71, 2902.20, 5902.10 | free with a registered key (`COMTRADE_API_KEY` in `.env`); free tier 250–500 calls/day, up to 100,000 rows per call (comtradr docs; figure not consistent)[^comtrade] | China monthly from 2016 expected; to be confirmed | Limits read from comtradr docs; data not yet queried | Monthly unit values: China CPL imports, China 5902.10 exports (a product benchmark), Pakistan 5902.10 imports |
| Caprolactam, N6 cord (producer) | Haiyang Technology (603382.SH) filings on cninfo | free, official PDFs | quarterly operating data since listing (Jun 2025); prospectus gives earlier years | Search only | CPL average purchase price and N6 cord average selling price; already 6 V points in the Causal Identifier |
| Freight | SCFI composite (en.sse.net.cn) | free page | weekly | Opened, no history download | already V in the Causal Identifier (third-party compilation) |

Where a free CPL series exists only as article text (SunSirs, news), each value is stored with its article link and tagged `S` until the page itself is opened and read, matching the Causal Identifier's rule.

## Citation rule (decision 1, 3 Nov 2026)

Every source shown in a report, doc or page is cited as a footnote with its link and the date it was opened, and marked as verified only when the page itself was read.

[^nbs2016]: NBS 10-day prices, 1–10 Nov 2016 (benzene 5,609.4 CNY/t), copy on China Securities Journal: https://cs.com.cn/xwzx/hg/201611/t20161114_5093867.html (opened 3 Nov 2026).
[^nbs2026]: NBS 10-day prices, mid-Oct 2026 (benzene 10,492.4 CNY/t): https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202610/t20261023_1965679.html (opened 3 Nov 2026).
[^fredarom]: FRED WPU06140197, PPI Aromatics: https://fred.stlouisfed.org/series/WPU06140197 (opened 3 Nov 2026).
[^comtrade]: comtradr documentation on UN Comtrade API limits: https://docs.ropensci.org/comtradr/articles/large_data.html (opened 3 Nov 2026).

## Still not covered free

- A continuous daily or weekly caprolactam price from Oct 2016 that can be read automatically. SunSirs is the best candidate, followed by customs unit values (monthly) and ChemAnalyst (licensed).
- Competitor raw-material prices at importer level: GlobalWits or Volza only.

## Phase 1 sources as loaded (5 Nov 2026)

Every value in the analyzer database carries its own `source_link`, `retrieved_at`, `unit` and `source_tier`. The table lists where each series came from; the coverage is in `docs/phase1/gate1-report.md`.

| Series id | Source | Tier | Notes |
| --- | --- | --- | --- |
| `sunsirs.cpl_china` | Hamza's file `Cap Data with Currency rate.xlsx` (SunSirs, CNY/t VAT excluded) | company_supplied | Jul 2025 – Nov 2026, daily, repeated dates averaged |
| `comtrade.cn_import_uv.293371` | UN Comtrade public preview API, China imports of HS 2933.71[^ct] | primary | Monthly USD/t (CIF value ÷ net weight). **2016 is dropped**: every 2016 month carries the same unit value (1,455.94 USD/t), an annual figure spread over months. **Ends Dec 2024**: Comtrade has no China monthly data for 2025–26 yet |
| `haiyang.cpl_purchase_q` | Haiyang Technology quarterly operating data on static.sse.com.cn (603382)[^hy] | primary | Average caprolactam purchase price, CNY/t ex VAT, 2024 Q3 and 2025 Q1 – 2026 Q3. Bridges Jan–Jun 2025, where Comtrade and the SunSirs file do not overlap. Each value is dated by the announcement it was read from |
| `comtrade.cn_export_uv.590210`, `comtrade.pk_import_uv.590210` | UN Comtrade, HS 5902.10 | primary | Market benchmarks for nylon tyre cord, not factors |
| `nbs.benzene_10day` | NBS 10-day releases on www.stats.gov.cn/sj/zxfb/[^nbs] | primary | Nov 2021 onward. Older releases (2016 – Oct 2021) are no longer listed on the NBS site; single copies exist (NBS English site, gov.cn, Chongqing statistics bureau, chinadaily) but there is no list to read them from |
| `scfi.composite` | GYUL91 shipping-indicators compilation (Korea NLIC data)[^scfi]; latest two weeks from SSE itself | third_party (history), primary (latest) | SSE's own history query needs a subscriber login. The compilation matches SSE on both weeks checked (3,687.35 and 3,681.34) |
| `sbp_m2m.usd_pkr`, `sbp_m2m.cny_pkr` | Hamza's file `SBP M2M Exch Rates Jul 2015 till date.xlsx` | company_supplied | SBP's own site blocks automated access (Cloudflare); not needed |
| `pbs.cpi_national` | PBS "Historical indices and growth rates 2015-16"[^pbsh] and Monthly Reviews Jul–Oct 2026[^pbsm] | primary | Monthly from Jul 2017. **Oct 2016 – Jun 2017 missing**: the PBS table gives only the FY2016-17 average, and no third-party copy was found |
| `fred.cpiaucns` | FRED CSV | primary | Oct 2025 blank in FRED (not published); stored as missing |
| `fred.dexchus`, `fred.dcoilbrenteu`, `fred.wpu06140197` | FRED CSV | primary | Cross-checks and event work; not in the v0.1-ci weights |

[^ct]: https://comtradeapi.un.org/public/v1/preview/C/M/HS (queried 5 Nov 2026; each value links its own query).
[^nbs]: https://www.stats.gov.cn/sj/zxfb/ (list read 5 Nov 2026; each value links its release).
[^scfi]: https://raw.githubusercontent.com/GYUL91/shipping-indicators-dashboard/master/docs/data/all.json (read 5 Nov 2026); SSE: https://en.sse.net.cn/indices/scfinew.jsp.
[^pbsh]: https://www.pbs.gov.pk/wp-content/uploads/2020/07/indices_and_growth_rates_historical-1.pdf (read 5 Nov 2026).
[^hy]: e.g. https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-10-30/603382_20261030_W45E.pdf (read 5 Nov 2026; each value links its own report).
[^pbsm]: e.g. https://www.pbs.gov.pk/wp-content/uploads/2020/07/Monthly-Review-October2026.pdf (read 5 Nov 2026).
