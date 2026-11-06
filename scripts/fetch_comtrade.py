"""Phase 1: fetch the three UN Comtrade monthly unit-value series into out/series/."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from analyzer.sources import comtrade
out = pathlib.Path(__file__).resolve().parent.parent / "out/series"; out.mkdir(parents=True, exist_ok=True)
months = [(y, m) for y in range(2016, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
for sid in (sys.argv[1:] or comtrade.SERIES):
    recs = comtrade.fetch(sid, months, log=lambda *a: print(*a, flush=True))
    (out / f"{sid}.json").write_text(json.dumps(recs, indent=1))
