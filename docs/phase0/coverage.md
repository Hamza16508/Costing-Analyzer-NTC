# Source coverage by factor and year, 2016–2026 (Phase 0)

Legend: **V** usable verified history in hand · **F** free source exists with history for that year, not yet loaded (Phase 1) · **?** free source claimed, start not verified · **P** pending credentials · **–** nothing found / missing.

"In hand" means V-tagged points in the Causal Identifier's `ext` (read 2 Nov 2026). S and A points count as missing.

## Nylon-cord factors and normalisers

| Series | 2016 (Oct–Dec) | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | In CI ext today |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| USD/PKR (SBP) | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | F | 3 V / 118 A |
| USD/CNY (FRED DEXCHUS) | F | F | F | F | F | F | F | F | F | F | F | 120 V / 1 A |
| Brent (FRED DCOILBRENTEU / EIA) | F | F | F | F | F | F | F | F | F | F | F | 121 V |
| Freight (SCFI composite) | V | V | V | V | V | V | V | V | V | V | V | 121 V (third-party compilation) |
| Caprolactam | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | 4 V / 48 S / 69 A |
| Benzene | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | P / – | 6 V / 28 S / 87 A |
| Haiyang N6 cord ASP (benchmark) | – | – | – | – | – | – | V (from Jun) | V | V | V | V | 6 V / 2 A |
| PAMA sales (demand) | – | – | – | – | – | – | – | – | – | – | V (Sep) | 1 V |
| PBS CPI national, 2015-16 base | ? | ? (Jul 2017+ claimed) | ? | F | F | F | F | F | F | F | F | – |
| US CPI-U NSA (FRED CPIAUCNS) | F | F | F | F | F | F | F | F | F | F (Oct 2025 gap claimed, not confirmed) | F (to Sep) | – |
| Events (GDELT 2.0 + CI collector) | F | F | F | F | F | F | F | F | F | F | F | 53 events (31 sourced) |
| Competitor raw-material prices (customs, HS 5902.10) | P | P | P | P | P | P | P | P | P | P | P | 0 rows |
| Market benchmark (UN Comtrade unit value, annual) | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | – |

## Spot-verification of nylon-cord rows (2 Nov 2026)

The shell in this session cannot reach any of these hosts: the environment's network policy returned 403 on CONNECT for sbp.org.pk, fred.stlouisfed.org, api.eia.gov and the rest (checked via the proxy status log). Pages were opened instead with the page-fetch tool, which reads HTML and PDF but not Excel or CSV files.

| Source | Opened? | Earliest date found | Access method | Result |
| --- | --- | --- | --- | --- |
| SBP BFER_Daily.xlsx | No: binary file, page fetch can't read it; shell blocked | not verified | direct xlsx download, no login | Third party (frankfurter.dev/providers/sbp) says history from 2013-07-02 from this file: still unverified |
| SBP BFER_Daily.pdf | Yes | 1 Sep 2026 (current month only) | direct PDF | Daily average bank floating rate, 24 currencies, PKR per unit; USD 277.751786 on 1 Sep 2026. Not a history source |
| SBP M2M / weighted-average pages (`/ecodata/rates/m2m/<yyyy>/<Mon>/`) | Yes | not established: the archived Feb 2018 URL now serves Oct 2026 content | HTML | Backup path uncertain; archive.sbp.org.pk to try in Phase 1 |
| SBP EasyData | Yes | not shown | web, guest access, download; developer guide linked | Exchange-rate series not visible on the landing page |
| FRED DEXCHUS | Yes | 1981-01-02 | CSV/API, free | Daily, CNY per USD, Fed H.10 noon buying rates |
| FRED DCOILBRENTEU | Yes | 1987-05-20 | CSV/API, free | Daily, USD/bbl, source EIA; latest 27 Oct 2026 |
| FRED CPIAUCNS | Yes | Jan 1913 | CSV/API, free | Monthly, 1982-84=100, latest Sep 2026 (336.940). The page notes don't mention an Oct 2025 gap; check the data file in Phase 1 |
| SCFI (en.sse.net.cn) | Yes | not shown | HTML, period query box; no download | No Pakistan lane |
| NCFI (Baltic Exchange overview PDF) | Yes | base week 10, 2012 | weekly, Friday | Lanes: Europe, Mediterranean, Middle East (Dammam, Dubai). **No India or Pakistan lane**, contradicting the earlier "India & Pakistan" note; either way, no Karachi lane |
| SunSirs | Reached a security-check page only | – | browser challenge | Blocked for automated access |
| 100ppi | Reached a security-check page only | – | browser challenge | Blocked for automated access |
| ChemAnalyst | Site refused the fetch | – | login | Pending credentials |
| Haiyang quarterly reports | Not opened (search only) | listed on SSE in Jun 2025 (603382) | cninfo PDFs | Quarterly operating data from listing; earlier history only from the prospectus |
| PBS CPI page | Yes | Sep 2023 on the listing page | monthly review PDFs | No time-series file on the page; PBS FAQ says monthly national indices are extracted on request |
| PBS rebasing (Mettis, 4 Sep 2019) | Yes | Aug 2019 first reported on 2015-16 base | news | Back data before Jul 2019 on the new base not confirmed |
| opendata.com.pk CPI 2016-2020 | Yes | Jul 2016 (fiscal year label) | PDF | PBS, 2015-16 base, but **urban, commodity-wise**, not the national general index |
| GDELT 2.0 | masterfilelist fetch failed | Feb 2015 (Aalto datahub listing) | CSV every 15 min, free | Not opened at source |
| UN Comtrade | Page is a JS app; not readable | – | API; key requirement not confirmed | Phase 1 |

## Gaps that matter for v1

1. **Caprolactam and benzene** (the two largest factors) have no usable free history: 4 and 6 V points. Free Chinese price sites block automated access; ChemAnalyst needs credentials. Without them, every month falls back to `missing_factor` for those factors and their weight goes to the remainder.
2. **USD/PKR**: only 3 V points in hand. The SBP xlsx is the right source but could not be opened from this session. Every USD figure stays `usd_approximate` until it is loaded.
3. **PBS CPI Oct 2016 – Jun 2019** on the 2015-16 national base is not confirmed from PBS itself; the one free file found is urban, commodity-wise.
4. **No China–Karachi freight lane** index exists; the SCFI composite stands in.
5. **Competitor raw-material prices**: none until GlobalWits/Volza credentials arrive; UN Comtrade gives at best annual unit values.
