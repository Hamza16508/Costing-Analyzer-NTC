"""Phase 0 read-only check: compare the Causal Identifier po snapshot with the file."""
import sys, json, glob, collections, pandas as pd, datetime as dt
df = pd.read_excel(sys.argv[1], sheet_name='Sheet1', header=1); df = df[df.RECEIPT_NUM.notna()].copy()
df['d'] = pd.to_datetime(df.TRANSACTION_DATE).dt.date
print(df[df.RECEIPT_NUM==103502][['BILTY_NO','VEHICLE_NUM','LC_NUMBER','ERP_PO']].to_string())
f = collections.Counter((str(r.d), int(r.RECEIPT_NUM), round(float(r.QUANTITY),3)) for r in df.itertuples())
same=shift=other=0; prec=collections.Counter()
for p in glob.glob(sys.argv[2]+'/po/*.json'):
    d=json.load(open(p)); cols=d['cols']
    for r in d['rows']:
        k=(str(r[0])[:10], int(r[1]), round(float(r[6]),3))
        kd=(str(dt.date.fromisoformat(k[0])+dt.timedelta(days=1)),k[1],k[2])
        dec=len(str(r[7]).split('.')[1]) if '.' in str(r[7]) else 0
        if k in f: same+=1; prec['same<=5' if dec<=5 else 'same>5']+=1
        elif kd in f: shift+=1; prec['shift<=5' if dec<=5 else 'shift>5']+=1
        else: other+=1
print("CI rows matching file date", same, "one day earlier", shift, "other", other, dict(prec))
