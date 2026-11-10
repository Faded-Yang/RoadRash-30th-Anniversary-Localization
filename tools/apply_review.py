# -*- coding: utf-8 -*-
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
root = sys.argv[1]
final = {int(k):v for k,v in json.load(open(os.path.join(root,'translations','zz_final.json'),encoding='utf8')).items()}
for name in ['review_A.json','review_B.json']:
    p = os.path.join(root,'translations','out',name)
    if not os.path.exists(p): print('skip', name); continue
    d = {int(k):v for k,v in json.load(open(p,encoding='utf8')).items()}
    n=0
    for i,v in d.items():
        if final.get(i) != v: n+=1
        final[i]=v
    print('%s: 应用 %d 条（实际变化 %d）' % (name, len(d), n))
json.dump({str(k):v for k,v in sorted(final.items())}, open(os.path.join(root,'translations','zz_final.json'),'w',encoding='utf8'), ensure_ascii=False, indent=1)
print('total', len(final))
