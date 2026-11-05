"""Phase 1 checks. The PO export is company data kept outside the repo: set NTC_PO_XLSX to its path."""
import datetime as dt
import json
import os
import pathlib
from collections import Counter

import jsonschema
import pytest

from analyzer import coverage as cov
from analyzer import po as po_mod

ROOT = pathlib.Path(__file__).resolve().parent.parent
XLSX = os.environ.get("NTC_PO_XLSX")
needs_po = pytest.mark.skipif(not XLSX, reason="set NTC_PO_XLSX to the PO export")


@pytest.fixture(scope="module")
def po():
    return po_mod.load(XLSX)[0]


@needs_po
def test_counts_match_phase0(po):
    assert len(po) == 1989
    keys = Counter(r["material_key"] for r in po)
    assert keys == {"840D/2": 1194, "1260D/2": 272, "840D/1": 144, "1890D/2": 129, "1260D/1": 127, "chafer": 79, None: 44}
    kg = sum(r["quantity"] for r in po if r["quantity_unit"] == "KGS")
    assert abs(kg - 22235206.57) < 0.01


@needs_po
def test_flags(po):
    f = Counter(x for r in po for x in r["flags"])
    assert f["efs_import"] == 93
    assert f["missing_lc_number"] == 68
    assert f["intercompany"] == 8
    assert f["provisional_duplicate"] == 4
    assert f["duplicate_entry"] == 1
    assert f["provisional_price"] == 15  # 16 whole-number import prices minus the Burlytex duplicate
    dup = [r for r in po if "duplicate_entry" in r["flags"]][0]
    assert dup["unit_price"] > 1e8 and "excluded_from_volume" in dup["flags"]
    assert all("excluded_from_pricing" in r["flags"] for r in po if r["unit_price"] <= 1)


@needs_po
def test_schema_and_ids(po):
    v = jsonschema.Draft202012Validator(json.loads((ROOT / "schemas/purchase_record.schema.json").read_text()))
    assert not [e for r in po for e in v.iter_errors(r)]
    assert len({r["purchase_id"] for r in po}) == len(po)


def _rec(day, val):
    return {"period_start": day, "value": val, "status": "ok" if val is not None else "missing"}


def test_point_in_time_and_tolerance():
    s = cov.Series([_rec("2020-01-01", 1.0), _rec("2020-02-01", 2.0), _rec("2020-03-01", None)], "M")
    assert s.at(dt.date(2020, 1, 31)) == 1.0          # value whose period started before the date
    assert s.at(dt.date(2019, 12, 31)) is None        # nothing dated after the purchase date is used
    assert s.at(dt.date(2020, 3, 20)) == 2.0          # missing March: February stands in (one month)
    assert s.at(dt.date(2020, 4, 2)) is None          # two months old: beyond tolerance, missing
    assert s.month(dt.date(2020, 2, 14)) == 2.0 and s.month(dt.date(2020, 3, 14)) is None


def test_flat_comtrade_year_dropped():
    from analyzer.sources.comtrade import drop_flat_years
    recs = [{"period_start": f"2016-{m:02d}-01", "value": 1455.94, "status": "ok", "retrieved_at": "x", "source_link": "u"} for m in range(1, 5)]
    recs += [{"period_start": "2017-01-01", "value": 2057.9, "status": "ok", "retrieved_at": "x", "source_link": "u"}]
    out = drop_flat_years(recs)
    assert [r["status"] for r in out] == ["missing"] * 4 + ["ok"]
