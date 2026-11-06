"""Build purchase records from the ERP PO export (Phase 1).

Reads `Nylon Tyre Cord.xls.xlsx` and returns one purchase_record (schema 0.2) per line,
with the Phase 0 flags and exclusions (decisions.md, po-mapping.md) and the PO knowledge
rules (config/po_knowledge.json). Modifies nothing.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = json.loads((ROOT / "config/po_knowledge.json").read_text())
SCHEMA_VERSION = "0.2"

KEY_RE = re.compile(r"\b(840|1260|1890)\s*[-/]?\s*D\s*[-/]?\s*(\d)", re.I)
EPI_RE = re.compile(r"(\d{2})\s*-?\s*EPI", re.I)
NAME_COUNTRY = {"CHINA": "CN", "THAILAND": "TH", "INDIA": "IN", "INDONESIA": "ID",
                # Chinese provinces and cities in vendor names without the word CHINA
                "SHANDONG": "CN", "SUZHOU": "CN", "JIANGSU": "CN", "ZHEJIANG": "CN", "QINGDAO": "CN", "NINGBO": "CN"}
TYRE_MAKERS_AND_GROUP = ("DIAMOND TYRES", "CROWN TYRES", "GHAURI TYRES", "SERVICE INDUSTRIES", "SERVICE LONG MARCH")
CREDIT_TERMS = set(KNOWLEDGE["fx"]["usance_gain_loss"]["applies_to_terms"])
TWO_PRICE_RECEIPTS = {89481, 152651, 153935, 156822, 158578}


def material_key(desc: str, category: str):
    if category != "NYLON CORD":
        return None
    d = desc.upper()
    if "CHAFER" in d:
        return "chafer"
    m = KEY_RE.search(d)
    return f"{m.group(1)}D/{m.group(2)}" if m else None


def epi_of(desc: str):
    m = EPI_RE.search(desc)
    return int(m.group(1)) if m else None


def origin_of(vendor: str, status: str):
    table = KNOWLEDGE["vendor_mill_country"]
    if vendor in table:
        name_says = next((c for k, c in NAME_COUNTRY.items() if k in vendor.upper()), None)
        if name_says and name_says == table[vendor]:
            return name_says, "vendor_name"
        return table[vendor], "confirmed_table"
    if any(t in vendor.upper() for t in TYRE_MAKERS_AND_GROUP):
        return None, "not_applicable"
    for k, c in NAME_COUNTRY.items():
        if k in vendor.upper():
            return c, "vendor_name"
    return None, "unknown"


def _s(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s or None


def _json_safe(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def load(path: Path, retrieved_at: str | None = None):
    path = Path(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    retrieved_at = retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    rows = ws.iter_rows(values_only=True)
    next(rows)  # category row
    header = [str(h) for h in next(rows)]
    lines = []
    for i, r in enumerate(rows, start=3):
        rec = dict(zip(header, r))
        if rec.get("RECEIPT_NUM") is None:
            continue
        rec["_row"] = i
        lines.append(rec)

    # identical lines (same date, receipt, item, qty, price)
    ident = Counter((l["TRANSACTION_DATE"], l["RECEIPT_NUM"], l["ITEM_CODE"], l["QUANTITY"], l["PO_UNIT_PRICE"]) for l in lines)
    seq = defaultdict(int)
    out = []
    for l in lines:
        receipt = int(l["RECEIPT_NUM"])
        item = str(l["ITEM_CODE"])
        seq[(receipt, item)] += 1
        date = l["TRANSACTION_DATE"].date().isoformat()
        price = float(l["PO_UNIT_PRICE"])
        status = l["STATUS1"]
        vendor = l["VENDOR_NAME"]
        cat = l["MINOR"]
        flags, notes = [], []

        def add(*fs, note=None):
            for f in fs:
                if f not in flags:
                    flags.append(f)
            if note:
                notes.append(note)

        if receipt == 132135 and price <= 1:
            add("provisional_duplicate", "excluded_from_pricing", "excluded_from_volume", note="decisions.md: provisional 1 PKR/kg entry, re-entered on 2025-03-25")
        if "SERVICE LONG MARCH" in vendor.upper() and price == 0:
            add("intercompany", "excluded_from_pricing", note="decisions.md: zero-price intercompany transfer")
        if receipt == 28753:
            add("excluded_from_pricing", note="decisions.md: Hanif 1 PKR/kg")
        if receipt == 103502 and price > 1e6:
            add("duplicate_entry", "excluded_from_pricing", "excluded_from_volume", note="Q1: scaled duplicate of the 956.415 line")
        if ident[(l["TRANSACTION_DATE"], l["RECEIPT_NUM"], l["ITEM_CODE"], l["QUANTITY"], l["PO_UNIT_PRICE"])] > 1:
            add("identical_line", note="PK-28: real delivery, informational")
        if receipt == 41304:
            add("code_description_conflict", note="PK-29: classified by description")
        whole = price > 5 and float(price).is_integer() and "duplicate_entry" not in flags
        if status == "IMPORT" and whole:
            add("provisional_price", "excluded_from_pricing", note="PK-09: whole-number import price, provisional")
        if receipt in TWO_PRICE_RECEIPTS and whole:
            add("provisional_price", "excluded_from_pricing", note="PK-10/PK-40: provisional price on a two-price receipt")
        if l["FREIGHT_CHARGES"] in (None, ""):
            add("freight_in_price")
        if status == "IMPORT" and l["LC_NUMBER"] in (None, ""):
            add("missing_lc_number", note="PK-22: LC number missing in the export")
        if (_s(l["PARTY_REFERNCE"]) or "").upper() == "EFS":
            add("efs_import", note="PK-23: Export Facilitation Scheme")
        if status == "IMPORT" and l["TERM_NAME"] in CREDIT_TERMS:
            add("usance_fx", note="PK-42: credit term; FX gain/loss is Period Cost, outside the price")

        region, basis = origin_of(vendor, status)
        raw = {k: _json_safe(v) for k, v in l.items() if k != "_row"}
        out.append({
            "record_type": "purchase_record",
            "schema_version": SCHEMA_VERSION,
            "applies_on": date,
            "source": {"name": "ERP PO export (Nylon Tyre Cord.xls.xlsx)", "link": None, "retrieved_at": retrieved_at},
            "purchase_id": f"{receipt}:{item}:{seq[(receipt, item)]}",
            "po_number": _s(l["ERP_PO"]),
            "po_header_id": _s(l["PO_HEADER_ID"]),
            "lc_number": _s(l["LC_NUMBER"]),
            "material_code": item,
            "legacy_code": _s(l["LEGACE_CODE"]),
            "material_name": l["ITEM_DESCRIPTION"],
            "material_key": material_key(l["ITEM_DESCRIPTION"], cat),
            "epi": epi_of(l["ITEM_DESCRIPTION"]) if cat == "NYLON CORD" else None,
            "purchase_date": date,
            "quantity": float(l["QUANTITY"]),
            "quantity_unit": l["UOM_CODE"],
            "currency": "PKR",
            "unit_price": price,
            "total_price": float(l["Q_VALUE"]),
            "supplier": vendor,
            "vendor_site": _s(l["VENDOR_SITE"]),
            "origin_region": region,
            "origin_basis": basis,
            "import_or_local": status,
            "delivery_terms": _s(l["DELIVERY_TERMS"]),
            "payment_terms": _s(l["TERM_NAME"]),
            "freight_per_receipt": None if l["FREIGHT_CHARGES"] in (None, "") else float(l["FREIGHT_CHARGES"]),
            "bilty_no": _s(l["BILTY_NO"]),
            "vehicle_num": _s(l["VEHICLE_NUM"]),
            "category": cat,
            "store": _s(l["SUBINVENTORY"]),
            "flags": flags,
            "flag_notes": notes,
            "raw": raw,
            "origin": {"file": path.name if path.name.endswith(".xls.xlsx") else "Nylon Tyre Cord.xls.xlsx", "sha256": sha, "sheet": "Sheet1", "row": l["_row"]},
        })
    return out, sha
