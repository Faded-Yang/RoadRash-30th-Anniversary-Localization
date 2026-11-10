# -*- coding: utf-8 -*-
"""Google 翻译批量生成本地化 JSON（占位符/颜色码/换行 全程保护）
   主端点 clients5（配额独立），回退 gtx；每批断点续存"""
import json, os, re, sys, ssl, time, io, random
import urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from languages import LANGS

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
KEEP_EN_IDS = {32} | set(range(358, 366))
CREDIT_LO, CREDIT_HI = 1000, 1999
STYLE = set('YGO-')
PH_MAP = [('%s', '[[S]]'), ('%d', '[[D]]'), ('%c', '[[C]]'), ('%%', '[[X]]')]
HOSTS = ['https://translate.googleapis.com', 'https://translate.google.com']

def protect(text, has_style):
    style, body = '', text
    if has_style and text and text[0] in STYLE:
        style, body = text[0], text[1:]
    body = body.replace('\t', '[[T]]').replace('\n', '[[N]]')
    for a, b in PH_MAP:
        body = body.replace(a, b)
    return style, body

def unprotect(style, body):
    body = body.replace('[[N]]', '\n').replace('[[T]]', '\t')
    for k, v in (('[[S]]', '%s'), ('[[D]]', '%d'), ('[[C]]', '%c'), ('[[X]]', '%%')):
        body = body.replace(k, v)
    for k in ('[[S]]', '[[D]]', '[[C]]', '[[X]]', '[[N]]', '[[T]]'):
        body = body.replace(k, '')
    return style + body

_rot = [0]

def _c5(text, tl, sl, timeout):
    q = urllib.parse.urlencode({'client': 'dict-chrome-ex', 'sl': sl, 'tl': tl, 'q': text})
    req = urllib.request.Request('https://clients5.google.com/translate_a/t?' + q,
                                 headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        d = json.loads(r.read().decode('utf-8'))
    if isinstance(d, list):
        if len(d) == 1 and isinstance(d[0], str):
            return d[0]
        if all(isinstance(x, str) for x in d):
            return '\n'.join(d)
    raise ValueError('bad response')

def _gtx(text, tl, sl, timeout):
    host = HOSTS[_rot[0] % len(HOSTS)]
    q = urllib.parse.urlencode({'client': 'gtx', 'sl': sl, 'tl': tl, 'dt': 't', 'q': text})
    req = urllib.request.Request(host + '/translate_a/single?' + q, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        d = json.loads(r.read().decode('utf-8'))
    return ''.join(seg[0] for seg in d[0] if seg and seg[0])

def gtx(text, tl, sl='en', timeout=40):
    last = None
    for attempt in range(8):
        fn = _c5 if attempt % 2 == 0 else _gtx
        try:
            out = fn(text, tl, sl, timeout)
            _rot[0] += 1
            return out
        except Exception as e:
            last = e
            code = getattr(e, 'code', 0)
            wait = (6 + attempt * 6 + random.random() * 4) if code == 429 else (2 + attempt * 2)
            if attempt >= 2:
                sys.stdout.write('    ..retry(%s) %.0fs\n' % (code or type(e).__name__, wait)); sys.stdout.flush()
            time.sleep(wait)
            _rot[0] += 1
    raise last

def translate_batch(items, tl):
    joined = '\n'.join(b for _, _, b in items)
    out = gtx(joined, tl)
    lines = out.split('\n')
    if len(lines) == len(items):
        return {items[i][0]: lines[i] for i in range(len(items))}
    res = {}
    for sid, st, body in items:
        res[sid] = gtx(body, tl); time.sleep(0.4)
    return res

def do_lang(code, en, target):
    out = dict(en); todo = []
    for i in sorted(en):
        s = en[i]
        if i in KEEP_EN_IDS or (CREDIT_LO <= i <= CREDIT_HI): continue
        if not re.search(r'[A-Za-z]', s): continue
        st, body = protect(s, i >= 1000)
        todo.append((i, st, body))
    B, fail = 20, 0
    for k in range(0, len(todo), B):
        chunk = todo[k:k + B]
        try:
            res = translate_batch(chunk, code)
        except Exception as e:
            fail += len(chunk)
            print('  [%s] batch %d FAILED: %s' % (code, k, str(e)[:60]), flush=True)
            continue
        for sid, st, body in chunk:
            tr = res.get(sid)
            if tr is not None:
                out[sid] = unprotect(st, tr)
        json.dump({str(x): v for x, v in sorted(out.items())}, open(target, 'w', encoding='utf8'),
                  ensure_ascii=False, indent=0)
        if (k // B) % 5 == 0:
            print('  [%s] %d/%d fail=%d' % (code, k + len(chunk), len(todo), fail), flush=True)
        time.sleep(0.4)
    return out, fail

def main():
    codes = sys.argv[1:] if len(sys.argv) > 1 else [l[0] for l in LANGS]
    en = {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'scratch', 'ENU.json'), encoding='utf8')).items()}
    os.makedirs(os.path.join(ROOT, 'translations', 'lang'), exist_ok=True)
    for code in codes:
        target = os.path.join(ROOT, 'translations', 'lang', '%s.json' % code)
        if os.path.exists(target):
            print('skip %s (exists)' % code, flush=True); continue
        t0 = time.time()
        print('=== %s ===' % code, flush=True)
        out, fail = do_lang(code, en, target)
        print('  saved %s (%.1fs, failed %d)' % (code, time.time() - t0, fail), flush=True)

if __name__ == '__main__':
    main()
