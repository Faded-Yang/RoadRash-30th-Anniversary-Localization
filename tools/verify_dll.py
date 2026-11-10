# -*- coding: utf-8 -*-
import json, sys, os, io, ctypes
import pefile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def extract(path):
    pe = pefile.PE(path, fast_load=False)
    out = {}
    for er in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if er.id != 6: continue
        for e1 in er.directory.entries:
            for e2 in e1.directory.entries:
                d = pe.get_data(e2.data.struct.OffsetToData, e2.data.struct.Size)
                p = 0
                for k in range(16):
                    if p+2 > len(d): break
                    ln = int.from_bytes(d[p:p+2], 'little'); p += 2
                    if ln > 0:
                        s = d[p:p+ln*2].decode('utf-16le', 'replace'); p += ln*2
                        out[(e1.id-1)*16+k] = s
    return out

ref_path, test_path = sys.argv[1], sys.argv[2]
ref = extract(ref_path); got = extract(test_path)
print('pefile: keys equal =', set(ref)==set(got), ' ref', len(ref), ' got', len(got),
      ' diffs', len([k for k in ref if ref[k]!=got.get(k)]))

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
u32 = ctypes.WinDLL('user32', use_last_error=True)
k32.LoadLibraryW.restype = ctypes.c_void_p
k32.LoadLibraryW.argtypes = [ctypes.c_wchar_p]
u32.LoadStringA.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_char_p, ctypes.c_int]
u32.LoadStringA.restype = ctypes.c_int
h = k32.LoadLibraryW(test_path)
print('LoadLibraryW ->', (hex(h) if h else 'FAILED'), ('err=%d' % ctypes.get_last_error()) if not h else '')
if h:
    buf = ctypes.create_string_buffer(4096)
    ok = bad = 0; firstbad = None
    for sid in sorted(got):
        n = u32.LoadStringA(h, sid, buf, 4096)
        raw = buf.raw[:n] if n>0 else b''
        exp = got[sid].encode('gbk', 'replace')
        if raw == exp: ok += 1
        else:
            bad += 1
            if firstbad is None: firstbad = (sid, raw[:60], exp[:60])
    print('LoadStringA(GKB): ok %d  bad %d' % (ok, bad))
    if firstbad: print('  first bad id', firstbad[0], firstbad[1], 'vs', firstbad[2])
    k32.FreeLibrary(ctypes.c_void_p(h))
