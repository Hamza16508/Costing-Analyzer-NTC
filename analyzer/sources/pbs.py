"""PBS national CPI (2015-16 = 100), the PKR deflator (decisions.md, "Currency and real prices").

Two PBS publications, both primary:
- "Historical indices and growth rates 2015-16" PDF: National CPI by month, Jul 2017 onward, one decimal.
- "Monthly Review on Price Indices" PDFs: Table 1 gives National CPI for the month and the month before,
  two decimals. Used for months after the historical table ends.
Months before Jul 2017 are not in either publication (the historical table gives only the FY2016-17
average); they are stored as missing with the attempt.
"""
from __future__ import annotations

import io
import re

import pdfplumber
import requests

from analyzer.factor import month_end, now_utc, value

SERIES = "pbs.cpi_national"
UNIT = "index 2015-16=100"
HIST_URL = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/indices_and_growth_rates_historical-1.pdf"
REVIEW_URLS = {
    # month covered: URL (as linked from https://www.pbs.gov.pk/price-statistics/)
    (2026, 7): "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Monthly-Review-July-2026.pdf",
    (2026, 8): "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Monthly-Review-August-2026.pdf",
    (2026, 9): "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Monthly-Review-September2026.pdf",
    (2026, 10): "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Monthly-Review-October2026.pdf",
}
UA = {"User-Agent": "Mozilla/5.0 (costing-analyzer)"}


def _pdf_text(url):
    r = requests.get(url, headers=UA, timeout=90)
    r.raise_for_status()
    with pdfplumber.open(io.BytesIO(r.content)) as p:
        return [pg.extract_text() or "" for pg in p.pages]


def historical():
    ts = now_utc()
    pages = _pdf_text(HIST_URL)
    vals = {}
    for t in pages[:4]:  # index pages; pages 5-8 are YoY rates
        if "Inflation Rate" in t:
            break
        for y, m, nat in re.findall(r"^(20\d\d) (\d{1,2}) (\d+\.\d) ", t, re.M):
            vals[(int(y), int(m))] = float(nat)
    return vals, ts


def review(url):
    ts = now_utc()
    t = "\n".join(_pdf_text(url))
    i = t.find("Table 1: Consumer Price Index (National)")
    m = re.search(r"General 100\.00 (\d+\.\d\d) (\d+\.\d\d) (\d+\.\d\d)", t[i:])
    return (float(m.group(1)), float(m.group(2))) if m else None, ts


def fetch(start=(2016, 1), end=(2026, 10)):
    hist, ts_h = historical()
    recs = {}
    for (y, m), v in hist.items():
        recs[(y, m)] = value(SERIES, f"{y}-{m:02d}-01", month_end(y, m), v, UNIT, None,
                             source_name="PBS, Historical indices and growth rates (base 2015-16), National CPI",
                             link=HIST_URL, retrieved_at=ts_h)
    for (y, m), url in REVIEW_URLS.items():
        if (y, m) in recs:
            continue
        try:
            got, ts = review(url)
        except Exception as e:  # recorded as an attempt
            got, ts = None, now_utc()
        v = got[0] if got else None
        recs[(y, m)] = value(SERIES, f"{y}-{m:02d}-01", month_end(y, m), v, UNIT, None,
                             source_name=f"PBS, Monthly Review on Price Indices {y}-{m:02d}, Table 1 National CPI",
                             link=url, retrieved_at=ts,
                             attempts=None if v else [{"when": ts, "where": url, "outcome": "Table 1 General row not found"}])
    out = []
    y, m = start
    while (y, m) <= end:
        if (y, m) not in recs:
            ts = now_utc()
            out.append(value(SERIES, f"{y}-{m:02d}-01", month_end(y, m), None, UNIT, None,
                             source_name="PBS national CPI (2015-16 base)", link=HIST_URL, retrieved_at=ts,
                             attempts=[{"when": ts_h, "where": HIST_URL, "outcome": "historical table starts Jul 2017 (FY2016-17 average only)"}]))
        else:
            out.append(recs[(y, m)])
        y, m = (y + (m == 12), m % 12 + 1)
    return out
