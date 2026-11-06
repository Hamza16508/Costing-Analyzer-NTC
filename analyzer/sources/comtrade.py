"""UN Comtrade public preview API: monthly trade unit values (decision 5A/5E, 3 Nov 2026).

The preview API needs no key but takes one period per call. Values are stored with the query
URL as source link. Unit value = primaryValue (USD) / netWgt (kg) x 1000 = USD per tonne.
"""
from __future__ import annotations

import time

import requests

from analyzer.factor import month_end, now_utc, value

BASE = "https://comtradeapi.un.org/public/v1/preview/C/M/HS"

SERIES = {
    # series_id: (reporter, flow, hs, description)
    "comtrade.cn_import_uv.293371": (156, "M", "293371", "China imports of caprolactam (HS 2933.71), all partners, CIF unit value"),
    "comtrade.cn_export_uv.590210": (156, "X", "590210", "China exports of nylon tyre cord fabric (HS 5902.10), all partners, FOB unit value"),
    "comtrade.pk_import_uv.590210": (586, "M", "590210", "Pakistan imports of nylon tyre cord fabric (HS 5902.10), all partners, CIF unit value"),
}


def fetch(series_id: str, months: list[tuple[int, int]], pause=1.2, log=print):
    rep, flow, hs, desc = SERIES[series_id]
    out = []
    for (y, m) in months:
        period = f"{y}{m:02d}"
        url = f"{BASE}?reporterCode={rep}&period={period}&cmdCode={hs}&flowCode={flow}&partnerCode=0"
        rec = None
        err = "rate limited (HTTP 429) on every try"
        for attempt in range(4):
            ts = now_utc()
            try:
                r = requests.get(url, timeout=90)
                if r.status_code == 429:
                    time.sleep(10 * (attempt + 1)); continue
                d = r.json()
                rows = [x for x in d.get("data") or [] if x.get("partnerCode") == 0 and x.get("customsCode") == "C00" and str(x.get("motCode")) == "0"]
                if not rows:
                    rows = [x for x in d.get("data") or [] if x.get("partnerCode") == 0]
                if rows:
                    x = rows[0]
                    kg = x.get("netWgt") or 0
                    usd = x.get("primaryValue")
                    uv = usd / kg * 1000 if kg and usd else None
                    rec = value(series_id, f"{y}-{m:02d}-01", month_end(y, m), uv, "USD/t", "USD",
                                source_name=f"UN Comtrade public preview API: {desc}", link=url, retrieved_at=ts,
                                attempts=[] if uv else [{"when": ts, "where": url, "outcome": "row has no net weight or value"}])
                    rec["raw"] = {"netWgt_kg": kg, "primaryValue_usd": usd, "cifvalue": x.get("cifvalue"), "fobvalue": x.get("fobvalue"), "classificationCode": x.get("classificationCode")}
                else:
                    rec = value(series_id, f"{y}-{m:02d}-01", month_end(y, m), None, "USD/t", "USD",
                                source_name=f"UN Comtrade public preview API: {desc}", link=url, retrieved_at=ts,
                                attempts=[{"when": ts, "where": url, "outcome": f"no data rows ({d.get('error') or 'empty'})"}])
                break
            except Exception as e:  # network or JSON error: retry
                err = repr(e)[:200]
                time.sleep(3 * (attempt + 1))
        if rec is None:
            ts = now_utc()
            rec = value(series_id, f"{y}-{m:02d}-01", month_end(y, m), None, "USD/t", "USD",
                        source_name=f"UN Comtrade public preview API: {desc}", link=url, retrieved_at=ts,
                        attempts=[{"when": ts, "where": url, "outcome": f"request failed: {err}"}])
        out.append(rec)
        log(series_id, period, rec["value"])
        time.sleep(pause)
    return out


def drop_flat_years(recs):
    """China's 2016 monthly rows carry one annual unit value on every month (no monthly movement).
    Such months are stored as missing, with the reason, so they never enter a ratio."""
    from collections import defaultdict
    by_year = defaultdict(list)
    for r in recs:
        if r["status"] == "ok":
            by_year[r["period_start"][:4]].append(r)
    for y, rs in by_year.items():
        vals = {round(r["value"], 4) for r in rs}
        if len(rs) >= 3 and len(vals) == 1:
            for r in rs:
                r.setdefault("raw", {})["flat_unit_value"] = r["value"]
                r["attempts"] = [{"when": r["retrieved_at"], "where": r["source_link"],
                                  "outcome": f"{y} monthly rows all carry the same unit value ({r['value']:.2f} USD/t): an annual figure spread over months, not a monthly price"}]
                r["value"], r["status"] = None, "missing"
    return recs


def retry_missing(recs, pause=1.2, log=print):
    """Re-query months stored as missing because of an empty or failed response."""
    sid = recs[0]["series_id"]
    redo = [(int(r["period_start"][:4]), int(r["period_start"][5:7])) for r in recs
            if r["status"] == "missing" and "flat_unit_value" not in r.get("raw", {})]
    fresh = {r["period_start"]: r for r in fetch(sid, redo, pause=pause, log=log)}
    return [fresh.get(r["period_start"], r) if r["status"] == "missing" else r for r in recs]
