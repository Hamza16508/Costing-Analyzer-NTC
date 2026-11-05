"""Phase 1: fetch NBS 10-day benzene prices into out/series/nbs.benzene_10day.json."""
import json, sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from analyzer.sources import nbs
root = pathlib.Path(__file__).resolve().parent.parent
links_file = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
links = json.loads(links_file.read_text()) if links_file else nbs.list_releases()
recs = []
for t, u in sorted(links.items()):
    recs.append(nbs.fetch_release(t, u)); print(t, recs[-1]["value"], flush=True); time.sleep(0.4)
recs.sort(key=lambda r: r["period_start"])
(root / "out/series/nbs.benzene_10day.json").write_text(json.dumps(recs, indent=1, ensure_ascii=False))
