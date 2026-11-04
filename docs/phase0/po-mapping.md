# PO export: mapping onto the purchase record (Phase 0, draft 0.1)

Source file: `Nylon Tyre Cord.xls.xlsx`, sha256 `195acf952a493a3e0297299fb78c4a36f6a9afb51d0bc5eeb9a3b7ac9d41899e`.
Re-checked on 2 Nov 2026 with `scripts/check_po_export.py`, `scripts/check_po_keys.py` and `scripts/check_ci_po_vs_file.py` (read only).

## File layout

- Sheets: `Sheet1` (data) and `Cell Description` (which columns the ERP generates and which users type).
- `Sheet1` row 1 is a category row (erp / Master data / input ...); the header is row 2; data starts at row 3.
- 36 columns, 1,989 data lines, 2016-10-19 to 2026-10-24, every time stamp at midnight.
- Every line: `TRANSACTION_TYPE = DELIVER`, `ORGANIZATION_CODE = TYR`.
- Columns AB–AI (`SUMQUANTITYPER...`, `SUMQ_VALUEPER...`) are Excel subtotals: kept in `raw`, never used.
- `SRR_NO` and `CHALLAN_NO` are empty on all lines. `PARTY_REFERNCE` is free text (kept in `raw`).

## Field mapping

| Purchase record field | Column | Notes (verified figures) |
| --- | --- | --- |
| purchase_id | RECEIPT_NUM + ITEM_CODE + n | 1,301 receipts; no line number in the export, so n is the 1-based order of the line within (receipt, item) in file order |
| po_number | ERP_PO | 761 POs |
| po_header_id | PO_HEADER_ID | 761; one-to-one with ERP_PO (checked both ways) |
| lc_number | LC_NUMBER | 395 LCs; blank on 163 lines |
| material_code | ITEM_CODE | 28 codes (full form `102-TX01150-00-000-000`) |
| legacy_code | LEGACE_CODE | 8 distinct codes plus blank on 143 lines (the "9" counted blank as a value) |
| material_name | ITEM_DESCRIPTION | 34 descriptions |
| material_key | parsed from ITEM_DESCRIPTION | see below |
| purchase_date / applies_on | TRANSACTION_DATE | delivery date at midnight; no PO or LC date exists |
| quantity, quantity_unit | QUANTITY, UOM_CODE | KGS 1,947 lines = 22,235,206.57 kg; MTR 42 lines (all CLOTH) |
| currency | (constant) | PKR on every line |
| unit_price | PO_UNIT_PRICE | PKR per unit. Median 2016: 328.5. Median 2026: 745.5 for KGS nylon-cord lines (728.9 over all 2026 lines) |
| total_price | Q_VALUE | equals QUANTITY × PO_UNIT_PRICE on all 1,989 lines (tolerance 0.01) |
| supplier | VENDOR_NAME | 33 vendors |
| vendor_site | VENDOR_SITE | |
| origin_region | parsed from VENDOR_NAME | traders (Hong Kong, Dubai, UK, Seychelles) hide the mill's country: needs the owner's vendor-to-origin table; `origin_basis` records how it was set |
| import_or_local | STATUS1 | IMPORT 1,894, LOCAL 95 |
| delivery_terms | DELIVERY_TERMS | local only: EX-FACTORY 52, FREE DELIVERY 43; blank on all imports |
| payment_terms | TERM_NAME | Sight 1,280, CAD 414, Immediate 202, 60 Days 43, 90 Days 20, 15 Days 19, 100% Advance 8, 30 Days 3 |
| freight_per_receipt | FREIGHT_CHARGES | PKR per receipt, repeated on every line of the receipt (one distinct value per receipt, checked); filled on 765 lines; never sum across lines; treated as inland trucking |
| bilty_no, vehicle_num | BILTY_NO, VEHICLE_NUM | |
| category | MINOR | NYLON CORD 1,945, CLOTH 42, TEXTILE 2 |
| store | SUBINVENTORY | |
| raw | all 36 columns | unmodified |
| origin | file, sha256, sheet, row | Excel row number (header row 2) |

## Material keys (NYLON CORD lines only)

Parsed with `\b(840|1260|1890)\s*[-/]?\s*D\s*[-/]?\s*(\d)` on ITEM_DESCRIPTION; "CHAFER" first.

| Key | Lines |
| --- | --- |
| 840D/2 | 1,194 |
| 1260D/2 | 272 |
| 840D/1 | 144 |
| 1890D/2 | 129 |
| 1260D/1 | 127 |
| chafer | 79 |
| total | 1,945 |

Excluded categories (material_key = null): CLOTH 42 lines (calico, drill, twill) and TEXTILE 2 lines. The two TEXTILE lines are "ACTIVATED POLYESTER TYRE CORD 840 D/2" and "NYLON TYRE CORD 1260 D/3"; both stay excluded by category as decided.

## Data findings (re-verified)

1. **The Causal Identifier's `po` holds every line twice.** Its 11 docs hold 3,978 rows = 2 × 1,989 and 44,563,234.86 qty. Every row matches a file line either on the file's date (1,989) or one day earlier (1,989); none match neither. The same-date copy has prices at 5 decimals or fewer on all rows; the shifted copy has more than 5 decimals on 816 rows. Sundays: 5 in the file, 373 in the stored po (5 + 368). For the page owner; not fixed.
2. **Receipt 132135** (Weifang Kelida, PO 53589, bilty 380, vehicle TLU-483): four lines on 2025-03-12 at 1 PKR/kg totalling 26,278 kg, then the same four quantities on 2025-03-25 at 792.21 / 733.52 / 733.52 / 733.52 PKR/kg. Confirmed.
3. **Service Long March Tyres**: 8 lines, all at 0 PKR/kg, 2023-07-25 to 2026-04-16, 19,726–22,077 kg each. Confirmed.
4. **Impossible prices**
   - Hanif Enterprises, receipt 28753, 2017-05-30: one line at 1 PKR/kg. Confirmed.
   - Burlytex, receipt 103502, 2023-04-27: **the receipt has two lines**, not one. Same item (102-TX01204), same quantity 19,503 kg, same PO 43195, bilty 10045 and vehicle TLN-414. One line is 956,415,064 PKR/kg, the other 956.415 PKR/kg (the same digits scaled by 10^6). Resolved (Q1): the scaled line is a duplicate entry.
   - Chafer receipt 55748 (2019-12-11) at 2,346.35 PKR/kg: "TYRE CORD CHAFER 420D1 N6", a different product. Confirmed.
5. **Identical lines on the same date**: receipts 75257 (2021-03-24) and 146081 (2026-01-29). Confirmed.
6. **Code/description conflicts**: both are on the same receipt, 41304 on 2018-08-27. `102-TX01150` (otherwise 840D/2) carries a 1890D/2 description; `102-TX01305` (otherwise 1890D/2) carries an 840D/2 description. The two lines look swapped; classified by description as decided.
7. **Local suppliers that make tyres**: Diamond Tyres 13 lines, Crown Tyres 8, Ghauri Tyres 1. Ordinary purchases, not competitor records. Confirmed.
8. **Gaps**: no deliveries in Dec 2018 or Jul 2020; nothing before 2016-10-19. Confirmed.
9. **Not in the export**: PO date, LC date, invoice currency, exchange rate. PO_UNIT_PRICE is **landed cost** (confirmed by Hamza, 3 Nov 2026).

## PO knowledge from the commercial specialist

See po-knowledge.md (rules PK-01 to PK-31) and `config/po_knowledge.json`.

## Flags applied at rebuild (from decisions.md)

| Lines | Flags |
| --- | --- |
| Receipt 132135, 4 lines on 2025-03-12 at 1 PKR/kg | provisional_duplicate, excluded_from_pricing, excluded_from_volume |
| Service Long March, 8 zero-price lines | intercompany, excluded_from_pricing |
| Hanif receipt 28753 | excluded_from_pricing |
| Burlytex receipt 103502, the 956,415,064 PKR/kg line | duplicate_entry, excluded_from_pricing, excluded_from_volume (Q1); the 956.415 line is priced normally |
| Receipts 75257 and 146081 | identical_line |
| Receipt 41304, the two swapped lines | code_description_conflict |
