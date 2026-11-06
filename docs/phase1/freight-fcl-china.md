# FCL freight from Chinese ports (owner's chart), 6 Nov 2026

Source: chart "FCL Movement - Chinese Ports" sent by Hamza (WhatsApp image, 6 Nov 2026). Weekly freight cost per FCL in USD, 2025 (weeks 1-52) and 2026 (weeks 1-44), with a moving-average line. The image and the digitized table are in the project folder, `costing-analyzer/data/freight/`.

Series in the databank: `ntc_fcl.china_ports`, tier `company_supplied`, unit "USD per FCL (container size not stated on the chart)", weekly, ISO weeks Monday to Sunday. 96 weeks, 88 with a value. Built by `scripts/build_fcl_china.py`; document `ext/ntc_fcl.china_ports__all-1` in the analyzer artifact.

## 1. Reading check

- The chart's "Moving Average" is a trailing 4-week mean of the 2026 bars. Recomputing it from the digitized bars reproduces all 44 of the chart's own MA labels within 1 USD, so every 2026 value is pinned. 2026 week 30 (1,700) was read from the MA identity because its label overlaps another.
- Two quirks of the chart's MA: weeks with no shipment ("-") count as zero, which drags the line down in weeks 1-14 (e.g. week 11 shows 825 when the shipments that month cost 1,440-1,740); and weeks 1-3 of 2026 borrow 2025 weeks 49-52. The databank stores the weekly bars only, with no-shipment weeks as missing, not zero.
- 2025 values have no MA check. Eight 2025 labels overlap others and are marked `check` in the CSV (weeks 9, 10, 15, 17, 24, 34, 38, 43); the error is at most a few tens of USD.

## 2. Against public indices

| Point | Chart | Public data | Verdict |
|---|---|---|---|
| 2025 shape | high in Jan (2,000-3,250), ~1,000-1,200 Feb-Apr, peak 3,765 in wk25, falls to 855-1,500 Sep-Dec | SCFI fell from Jan to Mar 2025, jumped in June 2025 (Shanghai-Jebel Ali +55% May-June, Israel-Iran war), slid to a 2023 low in Sep-Oct 2025 | Consistent |
| 2026 level, Sep-Oct | 3,770-4,225 | Arab News, 2 Oct 2026: China-to-Pakistan rates rose from $2,000-2,400 to $4,000-4,500 per container | Consistent |
| 2026 rally timing | climbs from wk32 (early Aug), peaks wk36 (31 Aug-6 Sep) | SCFI rose 8 weeks in a row to mid-Sep 2026; Persian Gulf lane still rising late Sep | Consistent, the lane peaked a little earlier |
| 2026 level vs Gulf lane | ~3,900 in late Sep | SCFI Shanghai-Persian Gulf $6,489-6,586/TEU on 24-30 Sep | Lower, as expected: Karachi is outside Hormuz and gained transshipment traffic |
| Iran war start (28 Feb 2026, wk9) | no spike in March-April (1,400-1,900) | Gulf rates quadrupled; Freightos says other lanes rose only moderately | Plausible for a non-Gulf lane, but worth asking the logistics team |
| Jan 2025 | 2,425 / 2,025 / 3,252 | SCFI Persian Gulf averaged $1,170/TEU in Q1 2025 | Higher than the index: either 40ft boxes, all-in charges, or pre-Chinese-New-Year rush. Unit question below |

No figure contradicts the public record. The chart looks like the company's own booked or quoted rates (weeks with no bar are weeks with no shipment), which makes it more useful than any index: there is no public China-Karachi lane index (see `docs/phase0/coverage.md`).

## 3. Relevance to costing

- Deliveries are CFR Karachi (PK-04). Ocean freight is inside the supplier's price, so it reaches PO_UNIT_PRICE through the supplier's quote, not as a separate line. Inland freight is the separate FREIGHT_CHARGES line (PK-17, PK-35).
- Size of the effect, rough: 840D/2 landed price is about PKR 750/kg, roughly $2,650/t. If an FCL carries about 18 t of cord, $1,300/FCL (2025 typical) is about $70/t or 2.7% of landed cost, and $4,000/FCL (Sep 2026) is about $220/t or 8%. The 2026 rise of about $2,600/FCL is about PKR 40/kg. For a 40ft box with more tonnage the share is smaller. The Causal Identifier's freight weight is 0.056, inside that range.
- Lag: CFR prices are fixed at quote or LC time, a few weeks before loading; the voyage to Karachi is about 2-3 weeks. The databank keeps the factor at receipt minus 45 days, which fits. 840D/2 import prices rose from about PKR 690/kg (Apr 2026) to 853 (Sep 2026); freight explains only a part of that, and the Sep freight peak has not yet shown in Oct receipts (825).
- Use in Phase 3: this lane series replaces the SCFI composite for 2025-2026 when splitting price changes, and calibrates SCFI to the lane (Sep 2026 vs Sep 2025: the lane is about 2.7x, the SCFI composite roughly 2.5-3x). It is too short to set base months, so the coverage rule keeps SCFI.

## 4. Open questions for the owner

1. Container size (20ft or 40ft), and whether the figure is base ocean freight or all-in (BAF, war-risk and emergency surcharges).
2. Who keeps it (logistics team, forwarder?) and whether the weekly table exists as a spreadsheet, plus earlier years. A spreadsheet back to 2016 would replace SCFI as the freight factor.
3. Which Chinese ports and which destination (Karachi or Port Qasim).
4. Tonnes of cord per FCL, to turn USD per FCL into USD per kg.
5. This does not settle FOB vs CFR (Gate 1 question 3); it gives the freight amount, but a CFR invoice next to its freight bill is still needed to prove the supplier passes it through.
