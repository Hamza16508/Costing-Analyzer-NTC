"""Phase 0 read-only check: material keys, code/description conflicts, medians."""
import sys, re, pandas as pd
df = pd.read_excel(sys.argv[1], sheet_name='Sheet1', header=1); df = df[df.RECEIPT_NUM.notna()].copy()
df['d'] = pd.to_datetime(df.TRANSACTION_DATE)
def key_of(s):
    s = str(s).upper()
    if 'CHAFER' in s: return 'chafer'
    m = re.search(r'\b(840|1260|1890)\s*[-/]?\s*D\s*[-/]?\s*(\d)', s)
    return f"{m.group(1)}D/{m.group(2)}" if m else None
df['mk'] = df.ITEM_DESCRIPTION.map(key_of)
nc = df[df.MINOR=='NYLON CORD']
print("NYLON CORD keys", nc.mk.value_counts(dropna=False).to_dict())
print("other minors", df[df.MINOR!='NYLON CORD'][['MINOR','ITEM_DESCRIPTION']].value_counts().to_dict())
print("LEGACE_CODE", df.LEGACE_CODE.nunique(), "blank", df.LEGACE_CODE.isna().sum())
code_key = nc.groupby('ITEM_CODE').mk.agg(lambda s: s.value_counts().to_dict())
for ic, v in code_key.items():
    if len(v) > 1: print("conflict", ic, v, nc[(nc.ITEM_CODE==ic)].groupby('mk').d.agg(lambda s: sorted(set(s.dt.date.astype(str)))).to_dict() if False else "")
for ic in ['102-TX01150-00-000-000','102-TX01305-00-000-000']:
    g = df[df.ITEM_CODE==ic]; mode = g.mk.mode()[0]
    print(ic, "mode", mode, g[g.mk!=mode][['d','RECEIPT_NUM','ITEM_DESCRIPTION']].to_string(header=False))
for y in [2016, 2026]:
    s = df[df.d.dt.year==y]
    print(y, "median all", round(s.PO_UNIT_PRICE.median(),2), "KGS nylon", round(s[(s.UOM_CODE=='KGS')&(s.MINOR=='NYLON CORD')].PO_UNIT_PRICE.median(),2),
          "qty-weighted", round((s.Q_VALUE.sum()/s.QUANTITY.sum()),2))
print("MTR lines minor", df[df.UOM_CODE=='MTR'].MINOR.value_counts().to_dict())
print("103502", df[df.RECEIPT_NUM==103502][['ITEM_CODE','QUANTITY','PO_UNIT_PRICE','Q_VALUE']].to_string())
