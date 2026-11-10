# -*- coding: utf-8 -*-
"""合并 partA/B/C，做 CP936 符号规范化，输出最终 zh.json + 报告"""
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
outroot = sys.argv[1]
merged = {}
report = []
for p in ['A','B','C','D']:
    d = json.load(open(os.path.join(outroot,'translations','out','part%s.zh.json'%p), encoding='utf8'))
    for k,v in d.items():
        merged[int(k)] = v
    print('part%s: %d' % (p, len(d)))

NORM = [('\u00a9','(C)'), ('\u00ae',''), ('\u2122','')]
changed = 0
for k,v in merged.items():
    nv = v
    for a,b in NORM: nv = nv.replace(a,b)
    if nv != v:
        report.append((k, v, nv)); merged[k] = nv; changed += 1
print('符号规范化条数:', changed)
for k,a,b in report: print('   id %4d %r -> %r' % (k, a[:40], b[:40]))

json.dump({str(k):v for k,v in sorted(merged.items())}, open(os.path.join(outroot,'translations','zz_final.json'),'w',encoding='utf8'), ensure_ascii=False, indent=1)
print('total merged:', len(merged))
