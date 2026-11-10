# -*- coding: utf-8 -*-
"""把角色短名强制回英文（参与 Chars/%s-F 图片路径），其余保持译文"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
enu = {int(k):v for k,v in json.load(open(sys.argv[1],encoding='utf8')).items()}
zh  = {int(k):v for k,v in json.load(open(sys.argv[2],encoding='utf8')).items()}
KEEP_EN = [32] + list(range(358, 366))     # Axle + 8 个短名
for i in KEEP_EN:
    if i in zh:
        if zh[i] != enu[i]:
            print('revert id %4d: %r -> %r' % (i, zh[i], enu[i]))
        zh[i] = enu[i]
json.dump({str(k):v for k,v in sorted(zh.items())}, open(sys.argv[2],'w',encoding='utf8'), ensure_ascii=False, indent=1)
print('done, total', len(zh))
