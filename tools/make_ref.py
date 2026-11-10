# -*- coding: utf-8 -*-
"""生成 5 语言对照参考表：id -> {en,de,fr,es,it}"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
base = sys.argv[1]; outroot = sys.argv[2]
def load(n):
    p = os.path.join(base, n + '.json')
    return {int(k):v for k,v in json.load(open(p, encoding='utf8')).items()}
L = {n: load(n) for n in ['ENU','DEU','FRA','ESP','ITA']}
ids = sorted(L['ENU'])
ref = {}
for i in ids:
    ref[str(i)] = {k: L[k].get(i, '') for k in ['ENU','DEU','FRA','ESP','ITA']}
os.makedirs(os.path.join(outroot,'translations','ref'), exist_ok=True)
json.dump(ref, open(os.path.join(outroot,'translations','ref','5lang.json'),'w',encoding='utf8'), ensure_ascii=False, indent=1)

# 分区参考 + 人类可读
def write_part(name, lo, hi):
    d = {k:v for k,v in ref.items() if lo <= int(k) <= hi}
    json.dump(d, open(os.path.join(outroot,'translations','ref','ref_%s.json'%name),'w',encoding='utf8'), ensure_ascii=False, indent=1)
    with open(os.path.join(outroot,'translations','ref','ref_%s.txt'%name),'w',encoding='utf8') as f:
        for i in sorted(d, key=int):
            e = d[i]
            f.write('#%s\n  EN %s\n  DE %s\n  FR %s\n  ES %s\n  IT %s\n' % (
                i,
                e['ENU'].replace('\n','\\n').replace('\t','\\t'),
                e['DEU'].replace('\n','\\n').replace('\t','\\t'),
                e['FRA'].replace('\n','\\n').replace('\t','\\t'),
                e['ESP'].replace('\n','\\n').replace('\t','\\t'),
                e['ITA'].replace('\n','\\n').replace('\t','\\t')))
    print('ref_%s: %d' % (name, len(d)))
write_part('A', 0, 499)
write_part('B', 500, 989)
write_part('C', 1000, 4003)
# 覆盖率：各语言有多少条与英文不同（= 真的翻译了）
for n in ['DEU','FRA','ESP','ITA']:
    diff = sum(1 for i in ids if L[n].get(i,'') != L['ENU'].get(i,''))
    print('%s 与英文不同的条数: %d / %d' % (n, diff, len(ids)))
