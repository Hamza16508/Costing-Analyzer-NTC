"""Phase 0 read-only check of the ERP PO export against the stated figures. Modifies nothing."""
import sys, hashlib, re, collections
import pandas as pd
path = sys.argv[1]
print("sha256", hashlib.sha256(open(path,'rb').read()).hexdigest())
xl = pd.ExcelFile(path); print("sheets", xl.sheet_names)
raw = pd.read_excel(path, sheet_name=xl.sheet_names[0], header=None)
print("row1", [x for x in raw.iloc[0].tolist() if pd.notna(x)][:12])
df = pd.read_excel(path, sheet_name=xl.sheet_names[0], header=1)
print("ncols", df.shape[1]); print(list(df.columns))
df = df[df['RECEIPT_NUM'].notna()].copy()
print("lines", len(df))
df['d'] = pd.to_datetime(df['TRANSACTION_DATE'])
print("dates", df.d.min(), df.d.max(), "non-midnight", (df.d.dt.normalize()!=df.d).sum())
for c in ['TRANSACTION_TYPE','ORGANIZATION_CODE','UOM_CODE','STATUS1','DELIVERY_TERMS','MINOR']:
    print(c, df[c].value_counts(dropna=False).to_dict())
print("TERM_NAME", df['TERM_NAME'].value_counts(dropna=False).to_dict())
print("KGS qty", df.loc[df.UOM_CODE=='KGS','QUANTITY'].sum())
for c in ['RECEIPT_NUM','ERP_PO','PO_HEADER_ID','LC_NUMBER','ITEM_CODE','LEGACE_CODE','ITEM_DESCRIPTION','VENDOR_NAME']:
    print("nunique", c, df[c].nunique())
print("LC blank", df.LC_NUMBER.isna().sum())
print("PO->header 1:1", df.groupby('ERP_PO').PO_HEADER_ID.nunique().max(), df.groupby('PO_HEADER_ID').ERP_PO.nunique().max())
print("value==qty*price all", ((df.Q_VALUE - df.QUANTITY*df.PO_UNIT_PRICE).abs() > 0.01).sum(), "mismatches")
print("median price 2016", df[df.d.dt.year==2016].PO_UNIT_PRICE.median(), "2026", df[df.d.dt.year==2026].PO_UNIT_PRICE.median())
print("freight filled", df.FREIGHT_CHARGES.notna().sum(), (df.FREIGHT_CHARGES.fillna(0)!=0).sum())
fr = df[df.FREIGHT_CHARGES.notna()].groupby('RECEIPT_NUM').FREIGHT_CHARGES.nunique().max(); print("freight distinct per receipt max", fr)
for c in ['SRR_NO','CHALLAN_NO']:
    if c in df: print(c, "non-empty", df[c].notna().sum())
print("sunday", (df.d.dt.weekday==6).sum())
r = df[df.RECEIPT_NUM==132135][['d','VENDOR_NAME','ERP_PO','QUANTITY','PO_UNIT_PRICE','BILTY_NO','VEHICLE_NUM']]; print(r.to_string())
print("1PKR lines on 2025-03-12 qty", df[(df.RECEIPT_NUM==132135)&(df.PO_UNIT_PRICE<=1)].QUANTITY.sum())
s = df[df.VENDOR_NAME.str.contains('LONG MARCH',case=False,na=False)]; print("SLM lines", len(s), "zero", (s.PO_UNIT_PRICE==0).sum(), s[s.PO_UNIT_PRICE==0].d.min(), s[s.PO_UNIT_PRICE==0].d.max(), s[s.PO_UNIT_PRICE==0].QUANTITY.round().tolist())
for rn in [28753,103502,55748]:
    print(rn, df[df.RECEIPT_NUM==rn][['d','VENDOR_NAME','ITEM_DESCRIPTION','PO_UNIT_PRICE']].to_string(header=False))
key=['d','RECEIPT_NUM','ITEM_CODE','QUANTITY','PO_UNIT_PRICE']
dup=df[df.duplicated(key,keep=False)]; print("identical lines receipts", sorted(dup.RECEIPT_NUM.unique()), dup.d.dt.date.unique())
def key_of(s):
    s=str(s).upper()
    if 'CHAFER' in s: return 'chafer'
    m=re.search(r'(\d{3,4})\s*D?\s*/\s*(\d)',s)
    return f"{m.group(1)}D/{m.group(2)}" if m else 'OTHER:'+s[:40]
df['mk']=df.ITEM_DESCRIPTION.map(key_of)
print("keys", df.mk.value_counts().to_dict())
print("keys by MINOR", df.groupby(['MINOR','mk']).size().to_dict())
for ic in ['102-TX01150','102-TX01305']:
    print(ic, df[df.ITEM_CODE==ic].groupby('mk').apply(lambda g: (len(g), sorted(g.d.dt.year.unique().tolist()))).to_dict())
for nm in ['DIAMOND','CROWN','GHAURI']:
    print(nm, (df.VENDOR_NAME.str.contains(nm,case=False,na=False)).sum())
m = df.d.dt.to_period('M').unique(); allm = pd.period_range('2016-10','2026-10',freq='M'); print("months w/o delivery", [str(x) for x in allm if x not in set(m)])
print("vendors", sorted(df.VENDOR_NAME.unique()))
