"""Write out/series/ntc_fcl.china_ports.json from the digitized FCL chart.

Usage: python scripts/build_fcl_china.py <path to fcl_china_weekly_2025_2026.csv>
Fails if the recomputed 4-week moving average disagrees with the chart's own labels.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from analyzer.sources import company_files as cf  # noqa: E402

path = sys.argv[1]
bad = cf.fcl_ma_check(path)
assert not bad, f"moving average does not match the chart: {bad}"
recs = cf.fcl_china_weekly(path)
out = ROOT / "out/series" / f"{cf.FCL_SERIES}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(recs, indent=1))
ok = [r for r in recs if r["status"] == "ok"]
print(f"{out}: {len(recs)} weeks, {len(ok)} with a value, {ok[0]['period_start']} to {ok[-1]['period_start']}")
