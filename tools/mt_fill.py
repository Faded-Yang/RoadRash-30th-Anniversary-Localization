# -*- coding: utf-8 -*-
"""补齐：只重翻「仍为英文」的条目（保留已译好的），可反复运行"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mtranslate as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
en = {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'scratch', 'ENU.json'), encoding='utf8')).items()}

def need(i, s):
    if i in M.KEEP_EN_IDS or (M.CREDIT_LO <= i <= M.CREDIT_HI): return False
    if not re.search(r'[A-Za-z]', s): return False
    return True

def fill(code):
    p = os.path.join(ROOT, 'translations', 'lang', code + '.json')
    if not os.path.exists(p):
        print('  no file', code); return
    d = {int(k): v for k, v in json.load(open(p, encoding='utf8')).items()}
    missing = [i for i in sorted(en) if need(i, en[i]) and d.get(i) == en[i]]
    if not missing:
        print('  %-6s complete' % code); return
    print('  %-6s 补 %d 条' % (code, len(missing)), flush=True)
    for k in range(0, len(missing), 15):
        chunk = missing[k:k + 15]
        items = []
        for i in chunk:
            st, body = M.protect(en[i], i >= 1000)
            items.append((i, st, body))
        try:
            res = M.translate_batch(items, code)
        except Exception as e:
            print('    batch fail %s' % str(e)[:50], flush=True); continue
        for sid, st, body in items:
            tr = res.get(sid)
            if tr is not None:
                d[sid] = M.unprotect(st, tr)
        json.dump({str(x): v for x, v in sorted(d.items())}, open(p, 'w', encoding='utf8'),
                  ensure_ascii=False, indent=0)
        time.sleep(0.4)
    left = [i for i in sorted(en) if need(i, en[i]) and d.get(i) == en[i]]
    print('  %-6s 剩余未译 %d' % (code, len(left)), flush=True)

if __name__ == '__main__':
    for code in sys.argv[1:]:
        fill(code)
