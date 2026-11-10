# -*- coding: utf-8 -*-
"""校验 patch 文件：只校验 patch 里出现的键"""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
STYLE = set('YGO-'); PH = re.compile(r'%(?:s|d|c|%)')
src = json.load(open(sys.argv[1], encoding='utf8'))
patch = json.load(open(sys.argv[2], encoding='utf8'))
errs=[]; warns=[]
for i, z in sorted(patch.items(), key=lambda x:int(x[0])):
    if i not in src: errs.append('id %s 不在源里' % i); continue
    e = src[i]
    if not isinstance(z,str) or not z.strip(): errs.append('id %s 空译文' % i); continue
    if e and e[0] in STYLE and int(i) >= 1000 and not z.startswith(e[0]):
        errs.append('id %s 缺颜色码 %r' % (i, e[0]))
    pe=sorted(PH.findall(e)); pz=sorted(PH.findall(z))
    if pe!=pz: errs.append('id %s 占位符不符 %s vs %s' % (i,pe,pz))
    if e.count('\n')!=z.count('\n'): warns.append('id %s 换行数 %d vs %d' % (i,e.count('\n'),z.count('\n')))
    if e.count('\t')!=z.count('\t'): errs.append('id %s Tab数 %d vs %d' % (i,e.count('\t'),z.count('\t')))
    if len(z) > max(12,int(len(e)*1.6)): warns.append('id %s 偏长 %d vs %d' % (i,len(e),len(z)))
print('patch 条数 %d' % len(patch))
for x in errs[:60]: print('  [错误]', x)
for x in warns[:40]: print('  [提醒]', x)
print('OK' if not errs else 'HAS ERRORS')
