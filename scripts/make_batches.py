"""Group built docs (out/db/<collection>/<doc>.json) into ArtifactData batch lists.
Usage: python scripts/make_batches.py <glob relative to out/db> [...]   -> prints one JSON list per line."""
import json, pathlib, sys
OUT = pathlib.Path(__file__).resolve().parent.parent / "out/db"
files = sorted({p for g in sys.argv[1:] for p in OUT.glob(g)})
cur, size = [], 0
for p in files:
    n = p.stat().st_size
    if cur and (len(cur) == 50 or size + n > 900_000):
        print(json.dumps(cur)); cur, size = [], 0
    cur.append({"op": "set", "collection": p.parent.name, "doc_id": p.stem, "file_path": str(p)}); size += n
if cur:
    print(json.dumps(cur))
