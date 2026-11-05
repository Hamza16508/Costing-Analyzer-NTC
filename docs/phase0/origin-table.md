# Vendor → mill country (decision Q5 of 3 Nov 2026: procurement table plus Claude's own search)

Status: **draft for procurement to fill in**. `origin_basis`: `vendor_name` (the name states a mill country), `confirmed_table` (procurement confirmed it), `verified_source` (found on a page Claude opened; linked), `unknown`.

Line counts and kg come from the PO export (KGS and MTR lines together).

## Import vendors whose name does not prove the mill's country

| Vendor | Lines | kg | Active | Proposed origin | Basis | Evidence | Procurement: confirm or correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPS London Ltd., United Kingdom | 91 | 1,401,370 | 2016-10 – 2022-06 | unknown | – | Searched 3 Nov 2026; nothing found | |
| G.T. Trading Co., Ltd., Thailand | 85 | 1,060,994 | 2016-10 – 2020-12 | unknown (Thailand if it ships Thai mill cord) | – | Searched; no company page found | |
| Yusheng Enterprise Limited, Hong Kong | 61 | 818,828 | 2019-12 – 2023-08 | China (provisional) | verified_source | A company brochure on DirectIndustry names Yusheng Enterprise Limited at Dong Sheng Plaza, Weifang, Shandong, and lists "Dipped Nylon 6 tire Cord Fabric" among its products.[^1] Whether the Hong Kong entity is the same company is not proven | |
| Burlytex Group Limited, Dubai, UAE | 36 | 535,999 | 2016-10 – 2024-08 | unknown | – | Searched; nothing found | |
| Stalwart Group DMCC, Dubai, UAE | 15 | 236,364 | 2021-03 – 2021-10 | unknown | – | Searched; nothing found | |
| Altek International FZE, Dubai, UAE | 4 | 35,783 | 2021 | unknown | – | Not yet searched | |
| HL Group Ltd | 8 | 24,252 | 2022-08 – 2024-09 | unknown | – | Not yet searched | |
| Crypto Trade Limited, Seychelles | 1 | 18,580 | 2021-05 | unknown | – | Not yet searched | |

Chinese trading houses (Jiangsu Haohui Trading 565 lines, Ningbo Jinlun Import & Export 155) are set to China by vendor name. Procurement should flag any that shipped non-Chinese cord.

## Local vendors (STATUS1 = LOCAL)

MB & Company, Qaisar Traders, Bond & Built, Trade Impex, Hanif Enterprises and Easy Tech Trading are local agents or stockists: origin `unknown` unless procurement knows the mill. Diamond, Crown and Ghauri Tyres, Service Industries and Service Long March are tyre makers or group companies: origin `not_applicable` (no import mill).

## Next steps (Phase 1)

- Continue the search for every vendor above, using company registries (UK Companies House for GPS London, DMCC and Dubai registers, Hong Kong Companies Registry) and trade directories. Record every attempt.
- Once Volza or GlobalWits is connected, take the shipper and mill country from the owner's own import records, the strongest evidence. That source is licensed, so it stays out of the repository.

[^1]: Yusheng Enterprise Limited, "Square woven fabric" brochure, DirectIndustry, https://pdf.directindustry.com/pdf/yusheng-enterpise-limited/square-woven-fabric/4560886-1075090.html (opened 3 Nov 2026).

## Phase 1 (5 Nov 2026)

The commercial table is now confirmed (PK-30, Mohsin, 3 Nov): every trader is China except G.T. Trading (Thailand). The database sets `origin_basis = confirmed_table` for traders, `vendor_name` where the name states the country and agrees with the table, and `not_applicable` for tyre makers and group companies.

| Vendor | Database origin | Lines | Search result (5 Nov 2026) |
| --- | --- | --- | --- |
| G.T. Trading Co., Ltd., Thailand | TH | 85 | Bangkok trader in tyre cord fabrics and industrial yarns since 1995, also a stock-lot dealer.[^gt1] Its public export records show tyre cord shipped from Laem Chabang with origin Thailand, with Pakistan its second market.[^gt2] Consistent with TH; the mill is not named |
| Burlytex Group, Stalwart Group | CN | 36, 15 | Volza's public directory lists both as exporters of nylon-6 dipped tyre cord fabric to Pakistan only (2022–2025).[^volza] The page does not show origin, so CN rests on the confirmed table |
| GPS London, Yusheng, Altek, HL Group, Crypto Trade | CN | 165 | Nothing new found; CN rests on the confirmed table (Yusheng also has the Weifang brochure above) |
| Shandong Shifeng (Group), Suzhou Kingdom Textile | CN | 84, 6 | Names state Chinese provinces and cities (Shandong, Suzhou); set to CN with basis `vendor_name` |
| Local agents (MB & Company, Bond & Built, Qaisar Traders, Trade Impex, Hanif, Easy Tech) | unknown | 62 | Local stockists; no public source names their mill. Stay `unknown` until Volza or GlobalWits shipper data is connected |

[^gt1]: G.T. Trading Co., Ltd., company profile, https://gtrel.com/about-us/ (search result read 5 Nov 2026).
[^gt2]: Tradesparq, G.T. Trading Co. Ltd supplier page, https://www.tradesparq.com/sitemap/company/supplier/g-t-trading-co-ltd (search result read 5 Nov 2026).
[^volza]: Volza, nylon tyre cord suppliers directory, https://www.volza.com/p/nylon-tyre-cord/suppliers-directory/ (search result read 5 Nov 2026).
