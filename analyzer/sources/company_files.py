"""Owner-supplied files (tier company_supplied). Kept in the project folder, read here.

- SBP M2M rates (`SBP M2M Exch Rates Jul 2015 till date.xlsx`): USD/PKR and CNY/PKR, daily.
- Caprolactam (`Cap Data with Currency rate.xlsx`, sheet Cap): SunSirs China domestic price, CNY/t VAT excluded
  (Mohsin, 5 Nov 2026); repeated dates averaged (Q4 = A).
"""
from __future__ import annotations

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
