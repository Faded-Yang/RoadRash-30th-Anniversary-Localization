# -*- coding: utf-8 -*-
"""把简体终稿转成繁体（zh-CN -> zh-TW）"""
import json, os, sys, ssl, time, io, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
def gtx(text, tl, sl):
    q = urllib.parse.urlencode({'client':'gtx','sl':sl,'tl':tl,'dt':'t','q':text})
    req = urllib.request.Request('https://translate.googleapis.com/translate_a/single?'+q, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        d = json.loads(r.read().decode('utf-8'))
    return ''.join(seg[0] for seg in d[0] if seg and seg[0])
zh = {int(k):v for k,v in json.load(open(os.path.join(ROOT,'translations','zz_final.json'),encoding='utf8')).items()}
out = dict(zh)
ids = sorted(zh)
B = 25
for k in range(0, len(ids), B):
    chunk = ids[k:k+B]
    lines = [zh[i].replace('\n','\u2028').replace('\t','\u2029') for i in chunk]
    for attempt in range(3):
        try:
            res = gtx('\n'.join(lines), 'zh-TW', 'zh-CN')
            got = res.split('\n')
            if len(got) == len(chunk):
                for j, i in enumerate(chunk):
                    out[i] = got[j].replace('\u2028','\n').replace('\u2029','\t')
            else:
                for i in chunk:
                    out[i] = gtx(zh[i].replace('\n','\u2028'), 'zh-TW', 'zh-CN').replace('\u2028','\n')
            break
        except Exception as e:
            time.sleep(2)
    if (k//B) % 8 == 0: print('  %d/%d' % (k, len(ids)), flush=True)
os.makedirs(os.path.join(ROOT,'translations','lang'), exist_ok=True)
json.dump({str(k):v for k,v in sorted(out.items())}, open(os.path.join(ROOT,'translations','lang','zh-TW.json'),'w',encoding='utf8'), ensure_ascii=False, indent=0)
print('zh-TW saved', len(out))
