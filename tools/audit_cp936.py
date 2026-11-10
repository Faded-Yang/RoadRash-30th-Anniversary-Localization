# -*- coding: utf-8 -*-
"""检查译文能否被 CP936(ACP) 无损表示——LoadStringA 会把不可映射字符变成 '?'"""
import json, sys, io, ctypes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
k = ctypes.windll.kernel32
def cp936_ok(ch):
    w = ch.encode('utf-16le')
    n = k.WideCharToMultiByte(936, 0, w, 1, None, 0, None, None)
    if n != 2 and n != 1:
        return False
    buf = ctypes.create_string_buffer(max(n,1))
    k.WideCharToMultiByte(936, 0, w, 1, buf, n, None, None)
    if ch == '?':
        return True
    return buf.raw[:n] != b'?'

files = sys.argv[1:]
for f in files:
    d = json.load(open(f, encoding='utf8'))
    bad = []
    for i, v in d.items():
        if not isinstance(v, str): continue
        chars = sorted({c for c in v if not cp936_ok(c)})
        if chars: bad.append((int(i), ''.join(chars), v[:60]))
    print('==== %s : %d 条含 CP936 不可表示字符 ====' % (f.split('\\')[-1], len(bad)))
    for i, ch, v in sorted(bad)[:40]:
        print('   id %4d  %r   %r' % (i, ch, v))
