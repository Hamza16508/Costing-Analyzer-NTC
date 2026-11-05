"""SCFI composite (Shanghai Containerized Freight Index), weekly, index points.

History: SSE's own history query needs a subscriber login, so the weekly series comes from a third-party
compilation (GYUL91/shipping-indicators-dashboard, collected from Korea NLIC), tier third_party, the same
source the Causal Identifier uses. The latest two weeks are read from SSE itself (tier primary) and
cross-checked against the compilation.
"""
from __future__ import annotations

import datetime as dt

import requests

from analyzer.factor import now_utc, value

SERIES = "scfi.composite"
COMP_URL = "https://raw.githubusercontent.com/GYUL91/shipping-indicators-dashboard/master/docs/data/all.json"
SSE_URL = "https://en.sse.net.cn/currentIndex?indexName=scfi"
SSE_PAGE = "https://en.sse.net.cn/indices/scfinew.jsp"


def fetch(start="2016-01-01"):
    ts = now_utc()
    d = requests.get(COMP_URL, timeout=90).json()
    ind = next(i for i in d["indicators"] if i["code"].upper() == "SCFI" or "SCFI" == i.get("name", "").upper()
               or i["code"].upper().startswith("SCFI"))
    recs = {}
    for o in ind["observations"]:
        if o["date"] < start or o.get("value") is None:
            continue
        day = o["date"]
        recs[day] = value(SERIES, day, day, o["value"], "index points", None,
                          source_name=f"SCFI composite via {ind.get('source')} compilation ({ind['code']})",
                          link=COMP_URL, retrieved_at=ts, tier="third_party",
                          vintage=f"compilation-{d['generated_at'][:10]}")
    check = []
    ts2 = now_utc()
    sse = requests.get(SSE_URL, timeout=60).json()["data"]
    comp = next(x for x in sse["lineDataList"] if x["dataItemTypeName"] == "SCFI_T")
    for day, v in ((sse["currentDate"], comp["currentContent"]), (sse["lastDate"], comp["lastContent"])):
        if day in recs:
            check.append((day, recs[day]["value"], v))
        recs[day] = value(SERIES, day, day, v, "index points", None, source_name="Shanghai Shipping Exchange, SCFI composite",
                          link=SSE_PAGE, retrieved_at=ts2, tier="primary")
    return [recs[k] for k in sorted(recs)], ind["code"], check
