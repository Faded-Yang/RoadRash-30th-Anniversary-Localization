# -*- coding: utf-8 -*-
"""RoadRash95.exe 字体补丁（唯一必须的 EXE 修改，等长原地写入，可逆）
   charset: ANSI_CHARSET(0) -> GB2312_CHARSET(134)   @ RVA 0x60d71  (push 0 -> push 134)
   face:    "Arial Narrow"  -> "SimHei"              @ RVA 0x1065b4
"""
import sys, os, io, shutil
import pefile
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass

PATCHES = [
    ('charset: ANSI->GB2312',      0x60d71,  bytes.fromhex('6a00'), bytes.fromhex('6a86')),
    ('face: Arial Narrow->SimHei', 0x1065b4, b'Arial Narrow\0', b'SimHei' + b'\0'*7),
]

def _read(path):
    with open(path, 'rb') as f: return f.read()

def _write_in_place(path, data):
    """原地覆盖写入，避免 os.replace 在权限/占用下失败"""
    try: os.chmod(path, 0o666)
    except Exception: pass
    with open(path, 'r+b') as f:
        f.seek(0); f.write(data); f.truncate(); f.flush()
        try: os.fsync(f.fileno())
        except Exception: pass

def apply(exe_path, backup=True):
    pe = pefile.PE(exe_path, fast_load=False)
    try:
        data = bytearray(_read(exe_path))
        results = []
        for name, rva, expect, new in PATCHES:
            off = pe.get_offset_from_rva(rva)
            cur = bytes(data[off:off+len(expect)])
            if bytes(data[off:off+len(new)]) == new:
                results.append((name, 'already', off)); continue
            if cur != expect:
                results.append((name, 'MISMATCH %r' % cur, off)); continue
            data[off:off+len(new)] = new
            results.append((name, 'ok', off))
        ok = all(r[1] in ('ok', 'already') for r in results)
    finally:
        try: pe.close()
        except Exception: pass
    if ok:
        if backup:
            bak = exe_path + '.zhbak'
            if not os.path.exists(bak):
                shutil.copyfile(exe_path, bak)
        _write_in_place(exe_path, bytes(data))
    return results, ok

def restore(exe_path):
    bak = exe_path + '.zhbak'
    if not os.path.exists(bak): return False
    _write_in_place(exe_path, _read(bak))
    return True

def check(exe_path):
    pe = pefile.PE(exe_path, fast_load=False)
    data = _read(exe_path)
    for name, rva, expect, new in PATCHES:
        off = pe.get_offset_from_rva(rva)
        print('  %-30s rva=0x%x file=0x%x  %r' % (name, rva, off, data[off:off+len(new)]))
    pe.close()

if __name__ == '__main__':
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == 'patch':
        res, ok = apply(path)
        for n, s, o in res: print('  %-30s %-12s file_off=0x%x' % (n, s, o))
        print('PATCH', 'OK' if ok else 'FAILED')
    elif cmd == 'restore':
        print('RESTORE', 'OK' if restore(path) else 'NO BACKUP')
    elif cmd == 'check':
        check(path)

