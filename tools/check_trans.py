# -*- coding: utf-8 -*-
import json, re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
STYLE = set('YGO-')
PH = re.compile(r'%(?:s|d|c|%)')

def load(p):
    return json.load(open(p, encoding='utf8'))

def main(src_path, out_path):
    src = load(src_path); out = load(out_path)
    errs = []; warns = []
    sids = set(src.keys()); oids = set(out.keys())
    for i in sorted(sids - oids, key=lambda x: int(x)):
        errs.append('缺少 id %s' % i)
    for i in sorted(oids - sids, key=lambda x: int(x)):
        errs.append('多余 id %s' % i)
    for i in sorted(oids & sids, key=lambda x: int(x)):
        e = src[i]; z = out[i]
        if not isinstance(z, str) or z.strip() == '':
            errs.append('id %s 未翻译 (原文 %r)' % (i, e[:60])); continue
        # style prefix
        if e and e[0] in STYLE and int(i) >= 1000:   # 颜色码只存在于 credits/结局区
            if not z.startswith(e[0]):
                errs.append('id %s 缺样式前缀 %r (原文 %r / 译文 %r)' % (i, e[0], e[:40], z[:40]))
        # placeholders
        pe = sorted(PH.findall(e)); pz = sorted(PH.findall(z))
        if pe != pz:
            errs.append('id %s 占位符不符 原文%s 译文%s (原文 %r / 译文 %r)' % (i, pe, pz, e[:60], z[:60]))
        # newline counts
        if e.count('\n') != z.count('\n'):
            warns.append('id %s 换行数不同 原文%d 译文%d (原文 %r)' % (i, e.count('\n'), z.count('\n'), e[:60]))
        if e.count('\t') != z.count('\t'):
            warns.append('id %s Tab数不同 原文%d 译文%d (原文 %r)' % (i, e.count('\t'), z.count('\t'), e[:60]))
        # length
        if len(z) > max(12, int(len(e)*1.6)):
            warns.append('id %s 译文偏长 原文%d 译文%d (原文 %r / 译文 %r)' % (i, len(e), len(z), e[:50], z[:50]))
    print('==== %s ====' % os.path.basename(out_path))
    print('源 %d 条，译 %d 条' % (len(sids), len(oids)))
    if errs:
        print('\n[错误] %d 条：' % len(errs))
        for x in errs[:80]: print('  ', x)
    if warns:
        print('\n[提醒] %d 条：' % len(warns))
        for x in warns[:40]: print('  ', x)
    if not errs:
        print('\n✔ 无错误，可用于构建。')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
