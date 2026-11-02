"""Phase 0 read-only: list causal-identifier/2 keys from the saved page HTML."""
import sys, json, re
h = open(sys.argv[1], encoding='utf8').read()
i = h.index('const DATA = ') + len('const DATA = ')
d, _ = json.JSONDecoder().raw_decode(h[i:])
print("schema", d['schema']); print("top", list(d))
for k in ['snapshot','cost','supply','workings','action','network','tracking']:
    if isinstance(d.get(k), dict): print(k, list(d[k]))
print("cost.parts[]", list(d['cost']['parts'][0]))
print("causes[]", list(d['causes'][0])); print("causes[].episodes[]", list(d['causes'][0]['episodes'][0])); print("causes[].indicators[]", list(d['causes'][0]['indicators'][0]))
print("delivered[]", list(d['delivered'][0])); print("episodes[]", list(d['episodes'][0]))
print("ruledOut[]", list(d['ruledOut'][0]))
for k in ['sources','couldNotVerify','confidence','weakestLink','nextData']: v=d.get(k); print(k, type(v).__name__, (list(v[0]) if isinstance(v,list) and v and isinstance(v[0],dict) else (list(v) if isinstance(v,dict) else str(v)[:80])))
