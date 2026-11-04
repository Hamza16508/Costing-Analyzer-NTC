# PO knowledge base: how the company's NTC purchase orders work

Source: the PO questionnaire filled in by **Mohsin Ali, Deputy Manager Commercial (in that role until Jan 2024)**, dated 3 Nov 2026 ([filled file](questionnaire/NTC-PO-Questionnaire-filled-2026-11-03.docx)), checked against the PO export (`Nylon Tyre Cord.xls.xlsx`, sha256 `195acf95…899e`).

Hamza's instruction (4 Nov 2026): this knowledge is **built into the system** as the analyzer's understanding of the company's POs. There are no supporting documents and no further PO questions. The machine-readable form is `config/po_knowledge.json`, which the analyzer loads at run time; each rule below carries the same id.

Note on scope in time: the respondent held the Deputy Manager Commercial role until Jan 2024 and still works closely with the commercial department in his current role. Hamza confirmed on 4 Nov 2026 that his answers are first-hand for the whole period, 2016–2026.

## 1. Price and timing

| Id | Rule | From |
| --- | --- | --- |
| PK-01 | PO_UNIT_PRICE is **landed cost**, worked out at receipt. Supplier prices are negotiated per order at the current market price, and orders are shipped quarterly. | A1 = D; A2 = A + quarterly shipments; Hamza 3 Nov |
| PK-02 | Order-to-delivery lead time: **40–45 days for imports, 5–10 days for local purchases.** The supplier price therefore reflects market conditions about 40–45 days before TRANSACTION_DATE. Factor lags for imported cord start from this. | B1 |
| PK-03 | TRANSACTION_DATE is the GRN date (goods received into store). | Part D |
| PK-04 | Deliveries are CFR (cost and freight to Karachi). | B2 |

## 2. Exchange rates and currency

| Id | Rule | From |
| --- | --- | --- |
| PK-05 | The supplier is paid against the bill of lading. The USD/PKR rate for that payment is negotiated between the company's Finance (Treasury) department and the bank's treasury. Duties use the official rate that the Pakistan Single Window / WeBOC system fills in automatically. Karachi office builds the cost sheet from both, plus actual port and shipping-line expenses, and sends it to head office. | A3 = E |
| PK-06 | The rate inside PO_UNIT_PRICE is therefore a **negotiated bank rate**, not a published one. SBP's daily rate is the closest public proxy; USD figures stay flagged approximate unless the bank's rates are supplied. | A3; clearing round Q3 |
| PK-07 | Invoices are about **90–95% in USD**, the rest mostly CNY or EUR. The analyzer treats the supplier price as USD-denominated. | A4 = E |

## 3. Corrections and provisional prices

| Id | Rule | From |
| --- | --- | --- |
| PK-08 | A line's price can be **entered as provisional and corrected later on the same line**, but only until stock from that line is issued. After issue the price is locked, and a change needs special permission. | A5 = B + E |
| PK-09 | The **16 import lines with whole-number prices** (8 in 2026) are **provisional prices** still to be replaced by the final landed cost. They get the flag `provisional_price`: kept in volume, excluded from pricing until a new export shows a costed price. | Part E |
| PK-10 | The 5 receipts with two prices for one item (89481, 152651, 153935, 156822, 158578) are **both** separately costed shipments and partly provisional. The whole-number price on each gets `provisional_price`; the decimal price is used. | Part E ("Both above") |
| PK-11 | Quality claims are settled by **debit notes, mostly adjusted as a discount on the next shipment's invoice**. A low price can therefore carry an earlier claim; the analyzer cannot see these, and they stay in the unexplained remainder. | B4 |

## 4. What landed cost contains

| Id | Rule | From |
| --- | --- | --- |
| PK-12 | **Included:** supplier price, sea freight, marine insurance, customs duties, port, terminal and shipping-line charges, clearing agent fees, bank and LC charges, inland freight to the factory, stamps and bonds. | Part C |
| PK-13 | **Excluded:** sales tax (adjustable) and income tax withheld at import. | Part C |
| PK-14 | Exchange gain or loss: left blank in the questionnaire. **Superseded by PK-32**: Hamza answered it on 4 Nov. | Part C |
| PK-15 | Customs duty: normal treatment on every shipment, with **customs duty at 0%** for PCT 5902.1000. Other duties may apply; the duty rate is constant across shipments of one PO. | A8 = A + E; Part D |
| PK-16 | Payment terms **change the price**: Sight, 60 and 90 days are priced differently. LC and CAD bank charges are inside PO_UNIT_PRICE. TERM_NAME is kept as a feature, and Phase 3 tests its effect. | B3 |

## 5. Freight

| Id | Rule | From |
| --- | --- | --- |
| PK-17 | FREIGHT_CHARGES is **local freight**: Karachi port to factory for imports, and supplier's warehouse to factory for local purchases. | A6 = E |
| PK-18 | **If FREIGHT_CHARGES is blank, freight is already included in PO_UNIT_PRICE** (flag `freight_in_price`). When it is filled, it is per receipt and is **not** added on top of PO_UNIT_PRICE, which is already landed cost (PK-12). It is used only to read the inland freight share. | A6 = E; Part C |
| PK-19 | A BILTY_NO with several numbers joined by "+" means one receipt delivered by several trucks, each with its own bilty. | Part D |

## 6. Payment channel and schemes

| Id | Rule | From |
| --- | --- | --- |
| PK-20 | VENDOR_SITE IMPORTS(CAD) = cash against documents, IMPORTS(LC) = letter of credit, IMPORTS = either. | Part D |
| PK-21 | One LC can cover several POs from the same supplier: partial shipments under one order booking and LC (110 of 395 LCs). | Part D |
| PK-22 | LC_NUMBER blank on 68 import lines (Sight 48, CAD 16, others 4) is **missing data**, not "no LC". STATUS1 says import or local. | Part D |
| PK-23 | **PARTY_REFERNCE "EFS" = Export Facilitation Scheme**, not electronic funds. 93 import lines carry it, all in 2025–2026 (Weifang Kelida 53, Jiangsu Haohui 38, Qingdao Hifortune 2). EFS imports normally come in under duty and tax relief for export production. These lines get the flag `efs_import`, and Phase 3 tests whether their landed cost differs. Their median price since 2021 is 776 PKR/kg against 801 for other imports; not yet controlled for timing. "CASH" (466 lines) and the other entries are payment references (cheque, online transfer, cash). | Part D; data check 4 Nov |
| PK-24 | SUBINVENTORY ATT and CTT are receiving stores; LOAN (1 line) is stock **borrowed**. | Part D |

## 7. Materials, vendors and completeness

| Id | Rule | From |
| --- | --- | --- |
| PK-25 | **EPI changes the price per kg** within a construction; width does not. The material key stays the construction, and EPI is recorded as a sub-key so like is compared with like. | A7 = B |
| PK-26 | Purchases from other tyre makers and local stockists are **emergency purchases at local market price, and borrowing or exchange returned in kind**. They are not comparable with import landed cost: flagged by `import_or_local = LOCAL` and kept out of the import price series. | A9 = A + B |
| PK-27 | The export is **complete** for Oct 2016 – Oct 2026. Dec 2018 and Jul 2020 really had no deliveries. | A10 = A; Part E |
| PK-28 | Receipts 75257 and 146081 are **two real deliveries each**: the identical lines are kept, and the `identical_line` flag is informational only. | Part E |
| PK-29 | Receipt 41304: the **description is right**, so the lines are classified by description. | Part E |
| PK-30 | Mill country: **China** for GPS London, Yusheng, Burlytex, Stalwart, Altek, HL Group, Crypto Trade, Jiangsu Haohui and Ningbo Jinlun; **Thailand** for G.T. Trading. Mill names not given. `origin_basis = confirmed_table`. | Part F |
| PK-31 | The costing structure stayed the same through 2016–2026, with only minor changes. | B5 |

## Items left blank

- Part C, **exchange gain or loss**: neither box ticked. Answered by Hamza on 4 Nov (PK-32).
- Part C, **usual share %** for every cost item: blank (optional).
- Part F, **mill names**: blank (optional).
- Part G, **documents**: none. Hamza confirmed there are none to attach.
- "Anything else": blank.
- A3, answer E: the last sentence is cut off ("…then sent to HO for further pri."). The meaning is clear enough to use.

## 8. Exchange gain or loss (Hamza, 4 Nov 2026)

| Id | Rule | From |
| --- | --- | --- |
| PK-32 | **Exchange gain or loss is part of landed cost when the LC or import payment is on 30, 60 or 90 days' credit.** For Sight, CAD and Immediate payments, no later FX adjustment applies. For usance lines, PO_UNIT_PRICE carries the actual payment-date rate, so it can differ from the rate on the cost sheet, and the price may be revised after receipt (PK-08). The analyzer converts usance lines with the rate nearest the payment date (TRANSACTION_DATE + credit days) and flags them `usance_fx`. | Hamza, follow-up Q3; replaces PK-14 |

## 9. What a landed-cost sheet looks like (training documents from Mohsin, 4 Nov 2026)

Two ERP printouts for one import consignment: an LC cost sheet (3 Nov 2026) and the LC account statement (2 Nov 2026). They are kept in the project's shared folder (`costing-analyzer/training/`), **not in the repository**, because they are internal company and bank records. The consignment is **rubber chemicals (HS 3812.1000), not nylon cord**, but it goes through the same costing that produces PO_UNIT_PRICE: Chinese supplier, 25,500 kg, PR dated 29 Jul 2026, GD dated 31 Oct 2026.

| Line on the cost sheet | PKR | Share of PO cost |
| --- | --- | --- |
| LC cost: USD 83,700 × 277.90 | 23,260,230 | 95.5% |
| Sindh Infrastructure Cess | 433,759 (1.86% of LC cost) | 1.8% |
| Bank charges | 42,178 | 0.2% |
| D/O charges | 127,247 | 0.5% |
| Freight from port to factory | 447,991 | 1.8% |
| Wharfage | 45,219 | 0.2% |
| Other clearing | 4,380 | 0.0% |
| **PO cost (= landed cost)** | **24,361,004 = 955.33 PKR/kg** | 100% |
| Sales tax (refundable, outside PO cost) | 4,219,566 | – |

| Id | Rule | From |
| --- | --- | --- |
| PK-33 | **PO cost = LC cost (USD invoice × one exchange rate) + levies + other charges.** Refundable sales tax sits below the PO cost and is excluded. This confirms PK-12 and PK-13. | Cost sheet |
| PK-34 | The LC cost uses **one rate** for the whole invoice (277.90 here), recorded on the sheet. The cost sheet is dated after the GD, so the rate belongs to the payment or retirement, not to the PO date. | Cost sheet; PK-05 |
| PK-35 | **Freight from port to factory is a line inside PO cost.** Inland freight is therefore always part of landed cost. FREIGHT_CHARGES in the export is a record of that same cost and is never added again. This answers follow-up Q1 with option A, on the evidence of this sheet. | Cost sheet; PK-18 |
| PK-36 | The duty-type levy on this consignment is the **Sindh Infrastructure Cess (~1.86% of LC value)**. No customs, additional or regulatory duty lines appear, consistent with customs duty at 0% (PK-15). Whether nylon cord (PCT 5902.1000) also carries ACD or RD is not shown, since this is a different HS code. | Cost sheet; follow-up Q2 partly answered |
| PK-37 | Charges are booked over time as journal vouchers against the LC account (D/O, wharfage, cess, stamps, excise processing). Some are still unposted when the cost sheet is printed. The landed cost settles once these are posted, which is why early prices can be provisional (PK-08, PK-09). | LC account statement |
| PK-38 | On this consignment, the **supplier's price is about 95% of landed cost**, and cess, port, bank and inland charges about 5%. The analyzer uses this as a sanity check only: weights still come from the factor definitions (decision 6). | Cost sheet (one consignment; indicative only) |
