
import json, os, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = sys.argv[1]
en = {int(k):v for k,v in json.load(open(os.path.join(ROOT,'scratch','ENU.json'),encoding='utf8')).items()}
rows=[]
for f in sorted(os.listdir(os.path.join(ROOT,'translations','lang'))):
    if not f.endswith('.json'): continue
    code=f[:-5]
    d={int(k):v for k,v in json.load(open(os.path.join(ROOT,'translations','lang',f),encoding='utf8')).items()}
    diff=sum(1 for i in en if d.get(i)!=en[i])
    rows.append((code, diff, len(d)))
rows.sort(key=lambda x:x[1])
print('code  translated/1372')
for c,d,n in rows:
    flag=' <<< LOW' if d < 700 else ''
    print('  %-6s %4d/%d%s' % (c, d, n, flag))
