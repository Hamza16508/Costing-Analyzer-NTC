"""FRED series via the public CSV endpoint (fredgraph.csv). A blank cell is stored as missing."""
from __future__ import annotations

import calendar
import csv
import io

import requests

from analyzer.factor import now_utc, value

SERIES = {
    # series_id: (FRED id, unit, currency, frequency, name)
    "fred.cpiaucns": ("CPIAUCNS", "index 1982-84=100", None, "M", "US CPI-U, all items, NSA (USD deflator)"),
    "fred.dexchus": ("DEXCHUS", "CNY per USD", None, "D", "China / US exchange rate, H.10 noon buying rate"),
    "fred.dcoilbrenteu": ("DCOILBRENTEU", "USD/bbl", "USD", "D", "Brent crude, Europe spot (EIA)"),
    "fred.wpu06140197": ("WPU06140197", "index Jun 2001=100", None, "M", "US PPI aromatics (benzene cross-check)"),
}


def fetch(series_id, start="2015-07-01"):
    fid, unit, cur, freq, name = SERIES[series_id]
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fid}"
    page = f"https://fred.stlouisfed.org/series/{fid}"
    ts = now_utc()
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    out = []
    for row in csv.DictReader(io.StringIO(r.text)):
        d = row["observation_date"]
        if d < start:
            continue
        raw = row[fid].strip()
        v = float(raw) if raw not in ("", ".") else None
        if freq == "M":
            y, m = int(d[:4]), int(d[5:7])
            end = f"{y}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"
        else:
            end = d
        out.append(value(series_id, d, end, v, unit, cur, source_name=f"FRED {fid}: {name}", link=page,
                         retrieved_at=ts, attempts=None if v is not None else [{"when": ts, "where": url, "outcome": "blank in the FRED file (not published)"}]))
    return out
