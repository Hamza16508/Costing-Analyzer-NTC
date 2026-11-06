"""Helpers to build factor_value records (schema 0.2)."""
from __future__ import annotations

import calendar
import datetime as dt

SCHEMA_VERSION = "0.2"


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def month_end(y: int, m: int) -> str:
    return dt.date(y, m, calendar.monthrange(y, m)[1]).isoformat()


def value(series_id, period_start, period_end, val, unit, currency, *, source_name, link, retrieved_at,
          tier="primary", vintage=None, published_at=None, attempts=None, tag=None):
    ok = val is not None
    rec = {
        "record_type": "factor_value",
        "schema_version": SCHEMA_VERSION,
        "applies_on": period_start,
        "source": {"name": source_name, "link": link, "retrieved_at": retrieved_at},
        "series_id": series_id,
        "period_start": period_start,
        "period_end": period_end,
        "value": float(val) if ok else None,
        "unit": unit,
        "currency": currency,
        "status": "ok" if ok else "missing",
        "attempts": attempts or ([] if ok else [{"when": retrieved_at, "where": link or source_name, "outcome": "no value published for this period"}]),
        "source_link": link,
        "retrieved_at": retrieved_at,
        "published_at": published_at,
        "vintage": vintage or retrieved_at[:10],
        "source_tier": tier,
        "tag": tag,
    }
    return rec
