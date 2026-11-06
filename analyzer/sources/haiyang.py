"""Haiyang Technology (SSE 603382) quarterly operating data: average caprolactam purchase price.

The company publishes, with each periodic report, the average purchase price of its main raw
materials (CNY/t, VAT excluded) for the quarter and the same quarter a year earlier. Values below
were read from the PDFs on static.sse.com.cn on 5 Nov 2026. published_at is the date of the
announcement in which we found the value (a comparative figure is dated by the later report,
because the original-quarter announcement was not read).
Used as a bridge for Jan-Jun 2025, where UN Comtrade (ends Dec 2024) and the SunSirs file (starts
Jul 2025) do not overlap. Not part of the v0.1-ci weights.
"""
from analyzer import factor

SID = "haiyang.cpl_purchase_q"
BASE = "https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/"
PDF = {
    "2025-10-30": BASE + "2025-10-30/603382_20251030_SAS5.pdf",
    "2026-04-28": BASE + "2026-04-28/603382_20260428_DVSD.pdf",
    "2026-08-20": BASE + "2026-08-20/603382_20260820_D7T0.pdf",
    "2026-10-30": BASE + "2026-10-30/603382_20261030_W45E.pdf",
}
# (year, quarter, CNY/t ex VAT, announcement date)
VALUES = [
    (2024, 3, 11078.36, "2025-10-30"),
    (2025, 1, 9318.88, "2026-04-28"),
    (2025, 2, 8066.03, "2026-08-20"),
    (2025, 3, 7592.28, "2025-10-30"),
    (2026, 1, 8892.87, "2026-04-28"),
    (2026, 2, 10623.21, "2026-08-20"),
    (2026, 3, 10919.00, "2026-10-30"),
]


def records(retrieved_at):
    out = []
    for y, q, v, pub in VALUES:
        m0 = 3 * q - 2
        out.append(factor.value(SID, f"{y}-{m0:02d}-01", factor.month_end(y, m0 + 2), v, "CNY/t", "CNY",
                                source_name="Haiyang Technology quarterly operating data (SSE 603382), avg purchase price ex VAT",
                                link=PDF[pub], retrieved_at=retrieved_at, tier="primary",
                                published_at=pub))
    return out
