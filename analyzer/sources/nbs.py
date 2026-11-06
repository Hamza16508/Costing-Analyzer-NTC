"""NBS 10-day national market prices (流通领域重要生产资料市场价格变动情况): benzene (纯苯, 石油苯, 工业级), CNY/t.

Release list from https://www.stats.gov.cn/sj/zxfb/ (covers Nov 2021 onward on the current site).
Each value is stored with the release URL; published_at is the release time shown on the page (Beijing time).
"""
from __future__ import annotations

import re
import time

import requests

from analyzer.factor import now_utc, value

SERIES = "nbs.benzene_10day"
TITLE_RE = re.compile(r"(\d{4})年(\d{1,2})月(上|中|下)旬流通领域重要生产资料市场价格变动情况")
ROW_RE = re.compile(r"纯苯\s*（\s*石油苯\s*，\s*工业级\s*）\s*吨\s*(\d+(?:\.\d+)?)\s")
PUB_RE = re.compile(r"(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2})")
DEKAD = {"上": (1, 10), "中": (11, 20), "下": (21, None)}


def list_releases(pages=67, log=print):
    links = {}
    for p in range(pages):
        url = "https://www.stats.gov.cn/sj/zxfb/" + ("index.html" if p == 0 else f"index_{p}.html")
        try:
            s = requests.get(url, timeout=40).content.decode("utf-8", "replace")
        except Exception as e:
            log("list page failed", p, e); continue
        for h, t in re.findall(r'href="([^"]+)"[^>]*>\s*([^<]*流通领域重要生产资料市场价格变动情况)\s*<', s):
            links[t.strip()] = requests.compat.urljoin(url, h)
        time.sleep(0.3)
    return links


def _text(html):
    t = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", t).replace(" ， ", "，").replace("（ ", "（").replace(" ）", "）")


def fetch_release(title, url):
    import calendar
    y, m, d = TITLE_RE.search(title).groups()
    y, m = int(y), int(m)
    a, b = DEKAD[d]
    b = b or calendar.monthrange(y, m)[1]
    ts = now_utc()
    html, err = None, None
    for i in range(4):
        try:
            html = requests.get(url, timeout=60).content.decode("utf-8", "replace")
            if "纯苯" in html:
                break
        except Exception as e:
            err = e
        time.sleep(3 * (i + 1))
    try:
        if html is None:
            raise err
        t = _text(html)
        mv = ROW_RE.search(t + " ")
        mp = PUB_RE.search(t)
        pub = f"{mp.group(1)}-{mp.group(2)}-{mp.group(3)}T{mp.group(4)}:{mp.group(5)}:00+08:00" if mp else None
        v = float(mv.group(1)) if mv else None
        att = None if v else [{"when": ts, "where": url, "outcome": "benzene row not found on the page"}]
    except Exception as e:
        v, pub, att = None, None, [{"when": ts, "where": url, "outcome": f"request failed: {e!r}"[:200]}]
    return value(SERIES, f"{y}-{m:02d}-{a:02d}", f"{y}-{m:02d}-{b:02d}", v, "CNY/t", "CNY",
                 source_name=f"NBS {title}", link=url, retrieved_at=ts, published_at=pub, attempts=att)
