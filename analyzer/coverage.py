"""Coverage checks and the base month per construction (decision 7A).

Rule (decisions.md, parameters): the base month of a construction is the first month with a priced
purchase and full verified factor coverage, not earlier than Oct 2016.

"Full coverage" for a priced import line on date d means every factor of config v0.1-ci has a usable value:
- caprolactam, freight and USD/CNY are looked up at d - lag (import lead time 45 days, PK-02), with the
  missing-data tolerance of the series frequency (daily 7 days, weekly 14 days, monthly 1 month);
- USD/PKR at d (rate near receipt, PK-42), PBS CPI and US CPI-U for the month of d (deflators), with the
  same monthly tolerance (last month's index may stand in for a missing month).
A value is usable only if status is ok and its period starts on or before the date (point-in-time rule).
"""
from __future__ import annotations

import bisect
import datetime as dt
from collections import defaultdict

TOL = {"D": 7, "W": 14, "M": 31, "10D": 20, "Q": 92}
LAG_DAYS = 45


def _d(s):
    return dt.date.fromisoformat(s)


class Series:
    def __init__(self, recs, freq):
        ok = sorted((r["period_start"], r["value"]) for r in recs if r["status"] == "ok")
        self.dates = [_d(a) for a, _ in ok]
        self.vals = [v for _, v in ok]
        self.freq = freq

    def at(self, day: dt.date):
        i = bisect.bisect_right(self.dates, day) - 1
        if i < 0:
            return None
        if self.freq == "M":
            months = (day.year - self.dates[i].year) * 12 + day.month - self.dates[i].month
            if months > 1:  # monthly tolerance: last month's value may stand in for a missing month
                return None
        elif (day - self.dates[i]).days > TOL[self.freq]:
            return None
        return self.vals[i]

    def month(self, day: dt.date):
        """Monthly value for the month of `day` (deflators)."""
        i = bisect.bisect_right(self.dates, day.replace(day=1)) - 1
        if i < 0 or self.dates[i] != day.replace(day=1):
            return None
        return self.vals[i]


def line_coverage(day: dt.date, factors: dict):
    """factors: name -> (Series, mode) where mode is 'lag' or 'receipt' or 'month'."""
    missing = []
    for name, (s, mode) in factors.items():
        if s is None:
            missing.append(name); continue
        if mode == "lag":
            v = s.at(day - dt.timedelta(days=LAG_DAYS))
        elif mode == "receipt":
            v = s.at(day)
        else:  # deflator for the month of the purchase, same monthly tolerance
            v = s.at(day)
        if v is None:
            missing.append(name)
    return missing


def base_months(po, factors, start="2016-10"):
    """Return {key: {month, lines_in_month, reason, first_missing}} using priced import lines."""
    by_key = defaultdict(lambda: defaultdict(list))
    for r in po:
        if r["material_key"] is None or "excluded_from_pricing" in r["flags"] or r["import_or_local"] != "IMPORT":
            continue
        by_key[r["material_key"]][r["purchase_date"][:7]].append(r)
    out = {}
    for key, months in by_key.items():
        first_gap = None
        found = None
        for m in sorted(months):
            if m < start:
                continue
            lines = months[m]
            gaps = set()
            for r in lines:
                gaps |= set(line_coverage(_d(r["purchase_date"]), factors))
            if not gaps:
                found = (m, len(lines)); break
            if first_gap is None:
                first_gap = (m, sorted(gaps))
        out[key] = {
            "month": found[0] if found else None,
            "lines_in_month": found[1] if found else 0,
            "first_purchase_month": min(months),
            "first_gap": first_gap,
        }
    return out
