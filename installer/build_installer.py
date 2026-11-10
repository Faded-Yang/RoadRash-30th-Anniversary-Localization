# -*- coding: utf-8 -*-
"""构建单文件安装器：编译桩 -> 生成各语言 DLL -> 打包 -> 编译 installer.exe"""
import os, sys, json, struct, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_dll
from languages import LANGS, OFFICIAL

HDR = 20
ENTRY = 40

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print('CMD FAIL:', ' '.join(cmd)); print(r.stdout); print(r.stderr); sys.exit(1)
    return r

def build_thunk():
    obj = os.path.join(ROOT, 'build', 'thunk.o')
    bin = os.path.join(ROOT, 'build', 'thunk.bin')
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    src = os.path.join(HERE, 'thunk.S')
    for flags in (['-m32'], []):
        try:
            sh(['gcc'] + flags + ['-c', '-nostdlib', '-o', obj, src])
            break
        except SystemExit:
            continue
    else:
        print('cannot compile thunk'); sys.exit(1)
    sh(['objcopy', '-O', 'binary', '--only-section=.text', obj, bin])
    data = open(bin, 'rb').read()
    print('thunk: %d bytes' % len(data))
    return data

def main():
    thunk = build_thunk()
    en = {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'translations', 'en.json'), encoding='utf8')).items()}
    ids = sorted(en)
    bids = sorted({i // 16 + 1 for i in ids})

    outdir = os.path.join(ROOT, 'build', 'langs')
    os.makedirs(outdir, exist_ok=True)
    entries = []
    for code, native, cp, charset, face in LANGS:
        if code in OFFICIAL: continue
        p = os.path.join(ROOT, 'translations', 'lang', code + '.json')
        if not os.path.exists(p): continue
        zh = {int(k): v for k, v in json.load(open(p, encoding='utf8')).items()}
        full = dict(en); full.update(zh)
        blocks = [(b, [full.get((b - 1) * 16 + k, '') for k in range(16)]) for b in bids]
        dll = os.path.join(outdir, 'ENU_%s.DLL' % code)
        build_dll.build(blocks, dll)
        entries.append({'code': code, 'name': native, 'cp': cp, 'charset': charset, 'face': face, 'dll': dll})
        print('  %-6s %-16s cp%-5d cs%-3d %-12s %d' % (code, native, cp, charset, face, os.path.getsize(dll)))

    count = len(entries)
    names_start = HDR + count * ENTRY
    pool = bytearray(); noffs = []
    for e in entries:
        noffs.append(names_start + len(pool)); pool += e['name'].encode('utf-8') + b'\0'
    data_base = names_start + len(pool)
    off = data_base; blobs = []
    for e in entries:
        d = open(e['dll'], 'rb').read(); blobs.append((off, d)); off += len(d)
    thunk_off = off; off += len(thunk)
    pack = bytearray(off)
    struct.pack_into('<IIIII', pack, 0, 0x314B505A, count, thunk_off, len(thunk), 0)
    for i, e in enumerate(entries):
        o = HDR + i * ENTRY
        cb = e['code'].encode('ascii')[:7]; pack[o:o + len(cb)] = cb
        struct.pack_into('<H', pack, o + 8, e['cp'])
        pack[o + 10] = e['charset']
        f = e['face'].encode('ascii')[:12]; pack[o + 11] = len(f); pack[o + 12:o + 12 + len(f)] = f
        struct.pack_into('<H', pack, o + 24, len(e['name'].encode('utf-8')))
        struct.pack_into('<I', pack, o + 26, noffs[i])
        struct.pack_into('<I', pack, o + 30, blobs[i][0])
        struct.pack_into('<I', pack, o + 34, len(blobs[i][1]))
    pack[names_start:names_start + len(pool)] = pool
    for i, (o, d) in enumerate(blobs): pack[o:o + len(d)] = d
    pack[thunk_off:thunk_off + len(thunk)] = thunk
    print('pack: %d languages, %d bytes' % (count, len(pack)))

    exe = os.path.join(ROOT, 'dist', 'RoadRash-30th-Localization.exe')
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    tmp = os.path.join(ROOT, 'build', 'installer_base.exe')
    sh(['gcc', '-O2', '-s', '-o', tmp, os.path.join(HERE, 'installer.c'), '-lshell32', '-luser32', '-ladvapi32'])
    base = open(tmp, 'rb').read()
    with open(exe, 'wb') as f:
        f.write(base); f.write(pack)
        f.write(struct.pack('<II', 0x314C5252, len(pack))); f.write(b'\0' * 8)
    print('built', exe, os.path.getsize(exe), 'bytes')

if __name__ == '__main__':
    main()
