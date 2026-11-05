"""Phase 1: build the analyzer database documents and the coverage summary.

Usage: python scripts/build_db.py <path to Nylon Tyre Cord.xls.xlsx>

Reads the PO export and every out/series/*.json, writes:
- out/db/<collection>/<doc_id>.json  (each document < 200 KiB)
- out/db/batches/NN.json             (ArtifactData batch write lists, <= 50 writes and < 900 KB each)
- out/db/coverage/summary.json       (what the analyzer page shows)
Validates every record against schemas/ first.
"""
import datetime as dt
import json
import pathlib
import statistics
import sys
from collections import defaultdict

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from analyzer import po as po_mod  # noqa: E402
from analyzer import coverage as cov  # noqa: E402

OUT = ROOT / "out/db"
MAX_DOC = 200 * 1024
CONFIG_VERSION = "v0.1-ci"

SERIES_META = {
    # series_id: (display name, frequency)
    "sunsirs.cpl_china": ("Caprolactam, China market (SunSirs, company file)", "D"),
    "comtrade.cn_import_uv.293371": ("Caprolactam, China import unit value (UN Comtrade)", "M"),
    "comtrade.cn_export_uv.590210": ("Nylon tyre cord, China export unit value (UN Comtrade)", "M"),
    "comtrade.pk_import_uv.590210": ("Nylon tyre cord, Pakistan import unit value (UN Comtrade)", "M"),
    "haiyang.cpl_purchase_q": ("Caprolactam, Haiyang avg purchase price, quarterly (SSE filings)", "Q"),
    "nbs.benzene_10day": ("Benzene, China 10-day market price (NBS)", "10D"),
    "fred.wpu06140197": ("US PPI aromatics (benzene cross-check)", "M"),
    "scfi.composite": ("Container freight, SCFI composite", "W"),
    "sbp_m2m.usd_pkr": ("USD/PKR, SBP M2M (company file)", "D"),
    "sbp_m2m.cny_pkr": ("CNY/PKR, SBP M2M (company file)", "D"),
    "fred.dexchus": ("USD/CNY, FRED H.10", "D"),
    "fred.dcoilbrenteu": ("Brent crude (FRED / EIA)", "D"),
    "pbs.cpi_national": ("Pakistan national CPI, 2015-16 base (PBS)", "M"),
    "fred.cpiaucns": ("US CPI-U, NSA (FRED)", "M"),
}


def chunks(records, prefix):
    """Split records into docs under MAX_DOC bytes; returns [(doc_id, body)]."""
    out, cur, n = [], [], 1
    for r in records:
        cur.append(r)
        if len(json.dumps({"records": cur})) > MAX_DOC:
            cur.pop()
            out.append((f"{prefix}-{n}", cur)); n += 1; cur = [r]
    if cur:
        out.append((f"{prefix}-{n}", cur))
    return out


def main(xlsx):
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    schemas = {n: jsonschema.Draft202012Validator(json.loads((ROOT / f"schemas/{n}.schema.json").read_text()),
                                                  format_checker=jsonschema.FormatChecker())
               for n in ("purchase_record", "factor_value")}
    po, sha = po_mod.load(xlsx)
    bad = [(r["purchase_id"], e.message) for r in po for e in schemas["purchase_record"].iter_errors(r)]
    assert not bad, bad[:5]

    series = {}
    for f in sorted((ROOT / "out/series").glob("*.json")):
        recs = json.loads(f.read_text())
        bad = [(r["series_id"], r["period_start"], e.message) for r in recs for e in schemas["factor_value"].iter_errors({k: v for k, v in r.items() if k != "raw"})]
        assert not bad, bad[:5]
        series[f.stem] = recs

    docs = []  # (collection, doc_id, body)
    by_year = defaultdict(list)
    for r in po:
        by_year[r["purchase_date"][:4]].append(r)
    for y, recs in sorted(by_year.items()):
        for doc_id, part in chunks(recs, y):
            docs.append(("po", doc_id, {"year": int(y), "schema_version": "0.2", "source_sha256": sha, "built_at": now, "records": part}))
    for sid, recs in sorted(series.items()):
        by_y = defaultdict(list)
        for r in recs:
            by_y[r["period_start"][:4]].append(r)
        whole = len(json.dumps(recs)) < MAX_DOC
        groups = [("all", recs)] if whole else sorted(by_y.items())
        for g, part in groups:
            for doc_id, p2 in chunks(part, f"{sid}__{g}"):
                docs.append(("ext", doc_id, {"series_id": sid, "schema_version": "0.2", "built_at": now, "records": p2}))

    # coverage summary
    srows = []
    for sid, recs in sorted(series.items()):
        okr = [r for r in recs if r["status"] == "ok"]
        name, freq = SERIES_META.get(sid, (sid, "?"))
        srows.append({"series_id": sid, "name": name, "unit": recs[0]["unit"], "tier": recs[0]["source_tier"],
                      "frequency": freq, "first": okr[0]["period_start"] if okr else None, "last": okr[-1]["period_start"] if okr else None,
                      "ok": len(okr), "periods": len(recs), "missing": [r["period_start"] for r in recs if r["status"] == "missing"][:400],
                      "link": recs[0]["source_link"]})

    S = {sid: cov.Series(recs, SERIES_META[sid][1]) for sid, recs in series.items() if sid in SERIES_META}
    variants = {
        "comtrade_cpl": {"caprolactam": (S.get("comtrade.cn_import_uv.293371"), "lag"), "freight": (S.get("scfi.composite"), "lag"),
                         "usd_pkr": (S.get("sbp_m2m.usd_pkr"), "receipt"), "pbs_cpi": (S.get("pbs.cpi_national"), "month"),
                         "us_cpi": (S.get("fred.cpiaucns"), "month")},
        "sunsirs_cpl": {"caprolactam": (S.get("sunsirs.cpl_china"), "lag"), "freight": (S.get("scfi.composite"), "lag"),
                        "usd_pkr": (S.get("sbp_m2m.usd_pkr"), "receipt"), "cny_pkr": (S.get("sbp_m2m.cny_pkr"), "lag"),
                        "pbs_cpi": (S.get("pbs.cpi_national"), "month"), "us_cpi": (S.get("fred.cpiaucns"), "month")},
    }
    bm = {v: cov.base_months(po, f) for v, f in variants.items()}

    keys = defaultdict(lambda: {"lines": 0, "kg": 0.0, "priced_lines": 0, "dates": [], "p2026": []})
    for r in po:
        if r["material_key"] is None:
            continue
        k = keys[r["material_key"]]
        k["lines"] += 1
        if "excluded_from_volume" not in r["flags"] and r["quantity_unit"] == "KGS":
            k["kg"] += r["quantity"]
        if "excluded_from_pricing" not in r["flags"]:
            k["priced_lines"] += 1
            if r["purchase_date"].startswith("2026") and r["import_or_local"] == "IMPORT":
                k["p2026"].append(r["unit_price"])
        k["dates"].append(r["purchase_date"])
    order = ["840D/2", "1260D/2", "840D/1", "1890D/2", "1260D/1", "chafer"]
    by_key = [{"key": key, "lines": keys[key]["lines"], "kg": round(keys[key]["kg"], 2), "priced_lines": keys[key]["priced_lines"],
               "first": min(keys[key]["dates"]), "last": max(keys[key]["dates"]),
               "median_2026": statistics.median(keys[key]["p2026"]) if keys[key]["p2026"] else None} for key in order]
    flags = defaultdict(int)
    for r in po:
        for f in r["flags"]:
            flags[f] += 1

    def reason(key):
        a, b = bm["comtrade_cpl"].get(key), bm["sunsirs_cpl"].get(key)
        gap = a["first_gap"]
        txt = f"Caprolactam from UN Comtrade monthly unit values. First purchase {a['first_purchase_month']}"
        if gap:
            txt += f"; earlier months lack {', '.join(gap[1])} (first gap {gap[0]})"
        if b and b["month"]:
            txt += f". With the SunSirs file instead, the base month would be {b['month']}"
        return txt + "."
    base_rows = [{"key": key, "month": bm["comtrade_cpl"][key]["month"], "lines_in_month": bm["comtrade_cpl"][key]["lines_in_month"],
                  "month_sunsirs": bm["sunsirs_cpl"].get(key, {}).get("month"), "reason": reason(key)} for key in order]

    summary = {"updated_at": now, "config_version": CONFIG_VERSION, "po_sha256": sha,
               "po": {"lines": len(po), "kg": round(sum(r["quantity"] for r in po if r["quantity_unit"] == "KGS" and "excluded_from_volume" not in r["flags"]), 2),
                      "priced_lines": sum("excluded_from_pricing" not in r["flags"] for r in po), "by_key": by_key, "flags": dict(flags)},
               "series": srows, "base_months": base_rows, "base_month_detail": bm}
    docs.append(("coverage", "summary", summary))
    docs.append(("config", "settings", {"config_version": CONFIG_VERSION, "real_base_month": "2026-09", "import_lag_days": cov.LAG_DAYS,
                                        "tolerance_days": cov.TOL, "remainder_threshold": 0.10, "min_event_cases": 3,
                                        "fx_rate_date": "receipt (PK-42)", "usd_flag": "usd_approximate", "updated_at": now}))

    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    writes = []
    for c, d, body in docs:
        p = OUT / c / f"{d}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        txt = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        assert len(txt.encode()) < 256 * 1024, (c, d, len(txt))
        p.write_text(txt)
        writes.append({"op": "set", "collection": c, "doc_id": d, "file_path": str(p), "_bytes": len(txt.encode())})
    batches, cur, size = [], [], 0
    for w in writes:
        if cur and (len(cur) == 50 or size + w["_bytes"] > 900_000):
            batches.append(cur); cur, size = [], 0
        cur.append(w); size += w["_bytes"]
    batches.append(cur)
    (OUT / "batches").mkdir(exist_ok=True)
    for i, b in enumerate(batches, 1):
        (OUT / "batches" / f"{i:02d}.json").write_text(json.dumps([{k: v for k, v in w.items() if k != "_bytes"} for w in b], indent=1))
    print(f"{len(docs)} docs, {len(batches)} batches")
    for i, b in enumerate(batches, 1):
        print(i, len(b), sum(w["_bytes"] for w in b), [w["collection"] + "/" + w["doc_id"] for w in b][:3], "...")
    print(json.dumps(base_rows, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
