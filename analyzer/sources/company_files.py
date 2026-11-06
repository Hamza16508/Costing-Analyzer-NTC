"""Owner-supplied files (tier company_supplied). Kept in the project folder, read here.

- SBP M2M rates (`SBP M2M Exch Rates Jul 2015 till date.xlsx`): USD/PKR and CNY/PKR, daily.
- FCL freight from Chinese ports (`fcl_china_weekly_2025_2026.csv`): weekly USD per FCL, 2025-2026, digitized from
  the owner's chart "FCL Movement - Chinese Ports" (6 Nov 2026).
- Caprolactam (`Cap Data with Currency rate.xlsx`, sheet Cap): SunSirs China domestic price, CNY/t VAT excluded
  (Mohsin, 5 Nov 2026); repeated dates averaged (Q4 = A).
"""
from __future__ import annotations

import datetime as dt
import hashlib
from collections import defaultdict

import openpyxl

from analyzer.factor import now_utc, value


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sbp_m2m(path, file_name="SBP M2M Exch Rates Jul 2015 till date.xlsx"):
    ts = now_utc()
    sha = _sha(path)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["SBP M2M Exch Rate"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    iu, ic = hdr.index("USD/PKR"), hdr.index("CNY/PKR")
    out = {"sbp_m2m.usd_pkr": [], "sbp_m2m.cny_pkr": []}
    for r in rows[1:]:
        if r[0] is None:
            continue
        d = r[0].date().isoformat()
        for sid, i, unit in (("sbp_m2m.usd_pkr", iu, "PKR per USD"), ("sbp_m2m.cny_pkr", ic, "PKR per CNY")):
            rec = value(sid, d, d, r[i], unit, "PKR", source_name=f"SBP M2M revaluation rate, company file {file_name}",
                        link="https://www.sbp.org.pk/ecodata/rates/m2m/index.htm", retrieved_at=ts, tier="company_supplied",
                        vintage=f"file-sha256:{sha[:12]}")
            rec["raw"] = {"file": file_name, "sha256": sha}
            out[sid].append(rec)
    return out


def sunsirs_cpl(path, file_name="Cap Data with Currency rate.xlsx"):
    ts = now_utc()
    sha = _sha(path)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Cap"]
    by_day = defaultdict(list)
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[1] is None or r[2] is None:
            continue
        by_day[r[1].date().isoformat()].append(float(r[2]))
    out = []
    for d in sorted(by_day):
        vals = by_day[d]
        rec = value("sunsirs.cpl_china", d, d, sum(vals) / len(vals), "CNY/t (VAT excluded)", "CNY",
                    source_name=f"SunSirs caprolactam China market price, recorded by the company, file {file_name}",
                    link="https://www.sunsirs.com/", retrieved_at=ts, tier="company_supplied", vintage=f"file-sha256:{sha[:12]}")
        rec["raw"] = {"file": file_name, "sha256": sha, "entries": vals}
        out.append(rec)
    return out


FCL_SERIES = "ntc_fcl.china_ports"
FCL_UNIT = "USD per FCL (container size not stated on the chart)"


def _rows(path):
    import csv
    with open(path, newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def fcl_ma_check(path):
    """Recompute the chart's moving average (trailing 4 weeks of 2026, blanks as 0, chained into 2025 wk49-52)
    and return [(week, chart_label, recomputed)] where they differ by more than 1 USD."""
    rows = _rows(path)
    y25 = [float(r["usd_2025"] or 0) for r in rows]
    y26 = [float(r["usd_2026"] or 0) for r in rows if r["ma_label"]]
    chain = y25[-3:] + y26
    bad = []
    for i, r in enumerate(r for r in rows if r["ma_label"]):
        ma = sum(chain[i:i + 4]) / 4
        if abs(ma - float(r["ma_label"])) > 1:
            bad.append((int(r["week"]), float(r["ma_label"]), ma))
    return bad


def fcl_china_weekly(path, file_name="fcl_china_weekly_2025_2026.csv", image="FCL Movement - Chinese Ports (WhatsApp 2026-11-06).jpeg"):
    """Weekly freight cost per FCL from Chinese ports, 2025 and 2026, digitized from the owner's chart.

    Weeks are taken as ISO weeks (Monday to Sunday). A week with no bar or a "-" is recorded as missing,
    not as zero, because it means nothing was recorded that week, not free freight.
    """
    ts = now_utc()
    sha = _sha(path)
    out = []
    for r in _rows(path):
        wk = int(r["week"])
        for year in (2025, 2026):
            raw = r[f"usd_{year}"]
            if raw == "" and year == 2026 and not r["ma_label"]:
                continue  # weeks not reached yet
            start = dt.date.fromisocalendar(year, wk, 1)
            v = float(raw) if raw not in ("", "0") else None
            rec = value(FCL_SERIES, start.isoformat(), (start + dt.timedelta(days=6)).isoformat(), v, FCL_UNIT, "USD",
                        source_name=f"NTC chart 'FCL Movement - Chinese Ports', digitized from {image}, file {file_name}",
                        link=None, retrieved_at=ts, tier="company_supplied", vintage=f"file-sha256:{sha[:12]}",
                        attempts=None if v is not None else [{"when": ts, "where": file_name,
                                                              "outcome": "chart shows no shipment for this week"}])
            rec["raw"] = {"file": file_name, "sha256": sha, "week": wk, "read": r[f"read_{year}"],
                          "chart_ma_label": float(r["ma_label"]) if year == 2026 and r["ma_label"] else None}
            out.append(rec)
    out.sort(key=lambda x: x["period_start"])
    return out
