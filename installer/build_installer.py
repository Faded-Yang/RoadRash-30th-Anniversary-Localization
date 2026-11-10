# -*- coding: utf-8 -*-
"""构建单文件安装器：生成各语言 DLL -> 汇编内嵌包 -> 编译 installer.exe
   不依赖游戏原始文件（块结构由 id 集合推导）"""
import os, sys, json, struct, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_dll
from languages import LANGS, OFFICIAL

def load(p):
    return {int(k): v for k, v in json.load(open(p, encoding='utf8')).items()}

def blocks_from_ids(ids):
    bids = sorted({i // 16 + 1 for i in ids})
    return [(b, [''] * 16) for b in bids]

def main():
    en = load(os.path.join(ROOT, 'translations', 'en.json'))
    ids = sorted(en)
    blocks = blocks_from_ids(ids)
    outdir = os.path.join(ROOT, 'build', 'langs')
    os.makedirs(outdir, exist_ok=True)

    entries = []
    for code, native, cp, charset, face in LANGS:
        if code in OFFICIAL:
            continue
        p = os.path.join(ROOT, 'translations', 'lang', code + '.json')
        if not os.path.exists(p):
            print('  skip', code); continue
        zh = load(p)
        full = dict(en); full.update(zh)
        nb = []
        for bid, _ in blocks:
            nb.append((bid, [full.get((bid - 1) * 16 + k, '') for k in range(16)]))
        dll = os.path.join(outdir, 'ENU_%s.DLL' % code)
        build_dll.build(nb, dll)
        entries.append({'code': code, 'name': native, 'cp': cp, 'charset': charset, 'face': face, 'dll': dll})
        print('  %-6s %-16s cp%-5d cs%-3d %-12s %d' % (code, native, cp, charset, face, os.path.getsize(dll)))

    count = len(entries)
    header = 8 + count * 40
    pool = bytearray(); noffs = []
    for e in entries:
        noffs.append(header + len(pool)); pool += e['name'].encode('utf-8') + b'\0'
    base = header + len(pool)
    off = base; blobs = []
    for e in entries:
        d = open(e['dll'], 'rb').read(); blobs.append((off, d)); off += len(d)
    pack = bytearray(off)
    struct.pack_into('<II', pack, 0, 0x314B505A, count)
    for i, e in enumerate(entries):
        o = 8 + i * 40
        cb = e['code'].encode('ascii')[:7]; pack[o:o + len(cb)] = cb
        struct.pack_into('<H', pack, o + 8, e['cp'])
        pack[o + 10] = e['charset']
        f = e['face'].encode('ascii')[:12]; pack[o + 11] = len(f); pack[o + 12:o + 12 + len(f)] = f
        struct.pack_into('<H', pack, o + 24, len(e['name'].encode('utf-8')))
        struct.pack_into('<I', pack, o + 26, noffs[i])
        struct.pack_into('<I', pack, o + 30, blobs[i][0])
        struct.pack_into('<I', pack, o + 34, len(blobs[i][1]))
    pack[header:header + len(pool)] = pool
    for i, (o, d) in enumerate(blobs):
        pack[o:o + len(d)] = d
    print('pack: %d languages, %d bytes' % (count, len(pack)))

    exe = os.path.join(ROOT, 'dist', 'RoadRash-30th-Localization.exe')
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    tmp = os.path.join(ROOT, 'build', 'installer_base.exe')
    r = subprocess.run(['gcc', '-O2', '-s', '-o', tmp, os.path.join(HERE, 'installer.c'),
                        '-lshell32', '-luser32', '-ladvapi32'], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr); sys.exit(1)
    base_bytes = open(tmp, 'rb').read()
    with open(exe, 'wb') as f:
        f.write(base_bytes); f.write(pack)
        f.write(struct.pack('<II', 0x314C5252, len(pack))); f.write(b'\0' * 8)
    print('built', exe, os.path.getsize(exe), 'bytes')

if __name__ == '__main__':
    main()
