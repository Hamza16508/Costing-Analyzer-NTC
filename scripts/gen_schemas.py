"""Generates the six Phase 0 contract schemas (JSON Schema 2020-12, draft 0.1). Design artefact only."""
import json, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs/phase0/schemas"
BASE = "https://costing-analyzer.local/schemas/0.1/"
DATE = {"type": "string", "format": "date"}
DT = {"type": "string", "format": "date-time"}
URI = {"type": "string", "format": "uri"}
DUR = {"type": "string", "pattern": r"^P(?!$)(\d+Y)?(\d+M)?(\d+W)?(\d+D)?$", "description": "ISO 8601 duration, date part only (e.g. P0D, P1M, P3M, P14D)."}
MONTH = {"type": "string", "pattern": r"^\d{4}-(0[1-9]|1[0-2])$"}
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
SOURCE = {"type": "object", "additionalProperties": False, "required": ["name", "retrieved_at"],
          "properties": {"link": {"type": ["string", "null"], "format": "uri"}, "name": {"type": "string", "minLength": 1}, "retrieved_at": DT}}
MATERIAL_KEY = {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9_./-]*$", "description": "Material key as read from ITEM_DESCRIPTION. Nylon cord v0.1: 840D/2, 1260D/2, 840D/1, 1890D/2, 1260D/1, chafer. Database doc ids use a slug with / replaced by - (840D-2)."}
NUM_OR_NULL = {"type": ["number", "null"]}

def common(record_type, extra_required, props, desc):
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + record_type + ".schema.json",
            "title": record_type.replace("_", " ").capitalize(), "description": desc, "type": "object",
            "additionalProperties": False,
            "required": ["record_type", "schema_version", "applies_on", "source"] + extra_required,
            "properties": {"record_type": {"const": record_type}, "schema_version": {"const": "0.1"},
                           "applies_on": {**DATE, "description": "The date this record applies to; drives every point-in-time check."},
                           "source": SOURCE, **props}}

PURCHASE_FLAGS = ["excluded_from_pricing", "excluded_from_volume", "intercompany", "provisional_duplicate", "identical_line", "code_description_conflict", "duplicate_entry", "provisional_price", "efs_import", "freight_in_price", "usance_fx"]
purchase = common("purchase_record", ["purchase_id", "po_number", "material_code", "material_name", "material_key", "purchase_date", "quantity", "quantity_unit", "currency", "unit_price", "total_price", "supplier", "import_or_local", "category", "flags", "raw", "origin"], {
    "purchase_id": {"type": "string", "pattern": r"^\d+:[^:]+:\d+$", "description": "RECEIPT_NUM:ITEM_CODE:n, n = 1-based order of the line within that receipt and item in file order."},
    "po_number": {"type": "string"}, "po_header_id": {"type": ["string", "null"]}, "lc_number": {"type": ["string", "null"]},
    "material_code": {"type": "string"}, "legacy_code": {"type": ["string", "null"]}, "material_name": {"type": "string"},
    "material_key": {"anyOf": [MATERIAL_KEY, {"type": "null"}], "description": "null for excluded categories (CLOTH, TEXTILE)."},
    "purchase_date": {**DATE, "description": "TRANSACTION_DATE (delivery date). Equals applies_on."},
    "quantity": {"type": "number", "exclusiveMinimum": 0}, "quantity_unit": {"enum": ["KGS", "MTR"]},
    "currency": {"const": "PKR"}, "unit_price": {"type": "number", "minimum": 0}, "total_price": {"type": "number", "minimum": 0},
    "supplier": {"type": "string"}, "vendor_site": {"type": ["string", "null"]},
    "origin_region": {"type": ["string", "null"], "description": "Mill country; null until the vendor-to-origin table is confirmed for traders."},
    "origin_basis": {"enum": ["vendor_name", "confirmed_table", "unknown"]},
    "import_or_local": {"enum": ["IMPORT", "LOCAL"]}, "delivery_terms": {"type": ["string", "null"]}, "payment_terms": {"type": ["string", "null"]},
    "freight_per_receipt": {**NUM_OR_NULL, "description": "PKR per receipt, repeated on each line of the receipt. Never sum across lines."},
    "bilty_no": {"type": ["string", "null"]}, "vehicle_num": {"type": ["string", "null"]},
    "category": {"enum": ["NYLON CORD", "CLOTH", "TEXTILE"]}, "store": {"type": ["string", "null"]},
    "flags": {"type": "array", "uniqueItems": True, "items": {"enum": PURCHASE_FLAGS}},
    "flag_notes": {"type": "array", "items": {"type": "string"}},
    "raw": {"type": "object", "description": "Every original column (36) of the line, unmodified."},
    "origin": {"type": "object", "additionalProperties": False, "required": ["file", "sha256", "sheet", "row"],
               "properties": {"file": {"type": "string"}, "sha256": SHA, "sheet": {"type": "string"}, "row": {"type": "integer", "minimum": 3, "description": "1-based Excel row (header is row 2)."}}}},
    "One delivered PO line from the ERP export. The brief names the provenance block source{file, sha256, sheet, row}; it is held in `origin` so that the common `source` block keeps the same shape on all six records.")

factor = common("factor_definition", ["factor_id", "material_key", "name", "unit", "data_source", "lookup_rule", "lag", "max_staleness", "version"], {
    "factor_id": {"type": "string", "pattern": r"^[a-z][a-z0-9_]*$"}, "material_key": MATERIAL_KEY,
    "name": {"type": "string", "minLength": 1}, "unit": {"type": "string", "minLength": 1},
    "data_source": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "pattern": r"^[a-z][a-z0-9_.-]*$"}, "description": "Ordered series_ids; the first with a value inside tolerance wins."},
    "lookup_rule": {"enum": ["last_on_or_before", "window_mean", "period_value"]},
    "lag": DUR, "window": DUR, "max_staleness": DUR,
    "default_weight": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of price in the base month. The sum per material must be <= 1 (checked across documents by the contract loader)."},
    "fx_series": {"type": ["string", "null"], "description": "Series used to convert this factor into the purchase currency at the delivery date; null for unitless indexes."},
    "host_cause": {"type": ["string", "null"], "pattern": r"^([a-z][a-z0-9-]*|delivered:[a-z][a-z0-9-]*)$", "description": "Causal Identifier target: a causes[].id (e.g. cpl-supply) or delivered:<name> (e.g. delivered:freight, delivered:usdpkr). Optional; set at integration (decision Q3, 2 Nov 2026)."},
    "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"}},
    "A cost factor supplied by the host. Unknown fields and values are rejected.")
factor["allOf"] = [{"if": {"properties": {"lookup_rule": {"const": "window_mean"}}}, "then": {"required": ["window"]}}]

attempt = {"type": "object", "additionalProperties": False, "required": ["when", "where", "outcome"],
           "properties": {"when": DT, "where": {"type": "string"}, "outcome": {"type": "string"}}}
series = common("factor_value", ["series_id", "period_start", "period_end", "value", "unit", "currency", "status", "attempts", "source_link", "retrieved_at", "published_at", "vintage", "source_tier", "tag"], {
    "series_id": {"type": "string", "pattern": r"^[a-z][a-z0-9_.-]*$"},
    "period_start": DATE, "period_end": DATE,
    "value": NUM_OR_NULL, "unit": {"type": "string"}, "currency": {"type": ["string", "null"], "pattern": "^[A-Z]{3}$"},
    "status": {"enum": ["ok", "missing"]}, "attempts": {"type": "array", "items": attempt},
    "source_link": {"type": ["string", "null"], "format": "uri"}, "retrieved_at": DT,
    "published_at": {"type": ["string", "null"], "format": "date-time", "description": "When the value was first public; null if unknown. Used by the stricter 'known by then' mode."},
    "vintage": {"type": "string", "description": "Revision label. A revision is a new record with a new vintage, never an overwrite."},
    "source_tier": {"enum": ["primary", "third_party"], "description": "primary = the publisher itself; third_party = a copy held by someone else (e.g. the PBS CPI 2016-2019 copy, decision Q6, provisional)."},
    "tag": {"enum": ["V", "S", "A", None], "description": "Carried from the Causal Identifier: V verified, S snippet, A approximate. Only V (or new records with status ok) are usable."}},
    "One observation of one series for one period. applies_on = period_start.")
series["allOf"] = [
    {"if": {"properties": {"status": {"const": "missing"}}}, "then": {"properties": {"value": {"type": "null"}, "attempts": {"minItems": 1}}}},
    {"if": {"properties": {"status": {"const": "ok"}}}, "then": {"properties": {"value": {"type": "number"}}}}]

EVENT_TYPES = ["weather", "disease", "conflict", "sanctions", "trade_policy", "plant_outage", "shipping_disruption", "fx_shock", "demand_shock", "supply_policy", "capacity_cycle"]
event = common("global_event", ["event_id", "title", "start_date", "end_date", "first_reported_at", "event_type", "region", "affected_factor_ids", "learned_impact", "sources"], {
    "event_id": {"type": "string", "pattern": r"^[a-z0-9][a-z0-9-]*$"}, "title": {"type": "string"},
    "start_date": DATE, "end_date": {"type": ["string", "null"], "format": "date"},
    "first_reported_at": {"type": ["string", "null"], "format": "date-time"},
    "event_type": {"enum": EVENT_TYPES}, "region": {"type": "array", "items": {"type": "string"}},
    "affected_factor_ids": {"type": "array", "uniqueItems": True, "items": {"type": "string"}},
    "learned_impact": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["as_of", "value", "method_version", "n_cases"],
        "properties": {"as_of": DATE, "value": NUM_OR_NULL, "method_version": {"type": "string"}, "n_cases": {"type": "integer", "minimum": 0}}}},
    "sources": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["link", "retrieved_at"],
        "properties": {"link": URI, "publisher": {"type": ["string", "null"]}, "published_at": {"type": ["string", "null"], "format": "date-time"}, "retrieved_at": DT}}},
    "judged_metadata": {"type": "object", "description": "Causal Identifier judged fields (dir, dirBasis, severity, relevant, channels, category, why, note, addedBy). Metadata only; never used by the engine."}},
    "A dated global event. Impact is learned from history, never judged.")

competitor = common("competitor_record", ["competitor_id", "scope", "price_type", "record_date", "material_key", "price", "currency", "unit", "source_link", "retrieved_at", "present_fields"], {
    "competitor_id": {"type": "string", "pattern": r"^[a-z0-9][a-z0-9-]*$", "description": "Key into the competitor registry (config/competitors), which holds aliases, e.g. general-tyre = General Tyre / Ghandhara Tyre and Rubber."},
    "scope": {"enum": ["local", "global"]}, "price_type": {"const": "raw_material_purchase"},
    "record_date": DATE, "material_key": MATERIAL_KEY,
    "price": NUM_OR_NULL, "currency": {"type": ["string", "null"], "pattern": "^[A-Z]{3}$"}, "unit": {"type": ["string", "null"]},
    "quantity": NUM_OR_NULL, "quantity_unit": {"type": ["string", "null"]}, "incoterm": {"type": ["string", "null"]},
    "origin_country": {"type": ["string", "null"]}, "hs_code": {"type": ["string", "null"], "pattern": r"^\d{4,10}$"},
    "source_link": {"type": ["string", "null"], "format": "uri"}, "retrieved_at": DT,
    "present_fields": {"type": "array", "uniqueItems": True, "items": {"type": "string"}, "description": "Fields actually present in the source; partial rows allowed."}},
    "A competitor's raw-material purchase price (e.g. a customs import record). Tyre selling prices and the owner's purchases from other tyre makers are not competitor records.")

def amount():
    return {"type": "object", "additionalProperties": False, "required": ["pkr", "usd"], "properties": {"pkr": NUM_OR_NULL, "usd": NUM_OR_NULL}}
deflated = {"type": "object", "additionalProperties": False, "required": ["value", "index_series", "base_month", "index_vintage", "index_value"],
            "properties": {"value": NUM_OR_NULL, "index_series": {"type": "string"}, "base_month": MONTH, "index_vintage": {"type": "string"}, "index_value": NUM_OR_NULL}}
BD_FLAGS = ["missing_factor", "stale_factor", "remainder_above_threshold", "thin_event_history", "usd_approximate", "excluded_from_pricing", "identical_line", "code_description_conflict", "no_base_period"]
breakdown = common("breakdown_output", ["purchase_id", "run_id", "run_date", "config_version", "method_version", "databank_snapshot", "pkr_nominal", "usd_nominal", "pkr_real", "usd_real", "base_period", "contributions", "event_adjustment", "explained_total", "unexplained", "flags", "competitor_gap"], {
    "purchase_id": {"type": "string"}, "run_id": {"type": "string"}, "run_date": DT,
    "config_version": {"type": "string"}, "method_version": {"type": "string"},
    "databank_snapshot": {**SHA, "description": "sha256 of the snapshot the run read."},
    "pkr_nominal": {"type": "number", "description": "PKR per kg as paid."},
    "usd_nominal": {"type": "object", "additionalProperties": False, "required": ["value", "fx_series", "fx_date", "fx_value", "approximate"],
                    "properties": {"value": NUM_OR_NULL, "fx_series": {"type": "string"}, "fx_date": {"type": ["string", "null"], "format": "date"}, "fx_value": NUM_OR_NULL, "approximate": {"type": "boolean"}}},
    "pkr_real": deflated, "usd_real": deflated,
    "base_period": {"type": "object", "additionalProperties": False, "required": ["month", "base_price"],
                    "properties": {"month": {"anyOf": [MONTH, {"type": "null"}]}, "base_price": amount()}},
    "contributions": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["factor_id", "weight", "value_used", "value_date", "value_vintage", "base_value", "contribution_pkr", "contribution_usd", "status"],
        "properties": {"factor_id": {"type": "string"}, "weight": {"type": "number", "minimum": 0, "maximum": 1},
                       "value_used": NUM_OR_NULL, "value_date": {"type": ["string", "null"], "format": "date"}, "value_vintage": {"type": ["string", "null"]},
                       "series_id": {"type": ["string", "null"]}, "base_value": NUM_OR_NULL,
                       "contribution_pkr": NUM_OR_NULL, "contribution_usd": NUM_OR_NULL, "status": {"enum": ["ok", "stale", "missing"]}}}},
    "untracked": {**amount(), "description": "w_0 term: conversion and margin, constant in real terms."},
    "event_adjustment": {"type": "object", "additionalProperties": False, "required": ["total", "events"],
        "properties": {"total": amount(), "events": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["event_id", "event_type", "impact", "estimate_as_of"],
            "properties": {"event_id": {"type": "string"}, "event_type": {"enum": EVENT_TYPES}, "impact": amount(), "estimate_as_of": DATE, "n_cases": {"type": "integer"}}}}}},
    "explained_total": amount(),
    "unexplained": {"type": "object", "additionalProperties": False, "required": ["value", "share"], "properties": {"value": amount(), "share": NUM_OR_NULL}},
    "flags": {"type": "array", "uniqueItems": True, "items": {"enum": BD_FLAGS}},
    "competitor_gap": {"type": "array", "maxItems": 0, "description": "Empty until Phase 4; the item shape is defined at Gate 4."}},
    "One breakdown per purchase line per config version. Contributions are real-terms amounts per kg in PKR and USD.")

for name, s in [("purchase_record", purchase), ("factor_definition", factor), ("factor_value", series), ("global_event", event), ("competitor_record", competitor), ("breakdown_output", breakdown)]:
    (OUT / f"{name}.schema.json").write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    print("wrote", name)
