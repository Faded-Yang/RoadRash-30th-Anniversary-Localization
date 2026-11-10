
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
base = sys.argv[1]
def load(n): return {int(k):v for k,v in json.load(open(base+'\\'+n+'.json',encoding='utf8')).items()}
langs = {n: load(n) for n in ['ENU','DEU','FRA','ESP','ITA']}
ids = list(range(32,40)) + list(range(358,366)) + [96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,16,17,18,19,20,116,58,60,62]
for i in ids:
    row = [ (n, langs[n].get(i)) for n in langs ]
    same = len({v for _,v in row if v is not None}) == 1
    print('id %4d %s' % (i, 'SAME' if same else 'DIFF'))
    if not same:
        for n,v in row: print('    %-4s %r' % (n, v))
