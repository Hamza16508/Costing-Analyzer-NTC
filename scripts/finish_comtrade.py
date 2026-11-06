"""Retry missing Comtrade months, then drop flat (annual-spread) years. Rewrites out/series/<id>.json."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from analyzer.sources import comtrade
root = pathlib.Path(__file__).resolve().parent.parent
for sid in sys.argv[1:]:
    p = root / f"out/series/{sid}.json"
    recs = comtrade.retry_missing(json.loads(p.read_text()), log=lambda *a: print(*a, flush=True))
    recs = comtrade.drop_flat_years(recs)
    p.write_text(json.dumps(recs, indent=1))
    print(sid, "ok", sum(r["status"] == "ok" for r in recs), "of", len(recs))
