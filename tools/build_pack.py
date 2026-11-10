# -*- coding: utf-8 -*-
"""打包：为每种语言生成 DLL，汇编内嵌包，编译并附加到 installer.exe"""
import os, sys, json, struct, subprocess, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from languages import LANGS, OFFICIAL
import build_dll

ENU_TPL = os.path.join(ROOT, 'scratch', 'ENU.json')

def load_json(p):
    return {int(k): v for k, v in json.load(open(p, encoding='utf8')).items()}

def lang_json(code):
    p = os.path.join(ROOT, 'translations', 'lang', '%s.json' % code)
    if code == 'zh-CN':
        p = os.path.join(ROOT, 'translations', 'zz_final.json')
    return load_json(p) if os.path.exists(p) else None

def main():
    en = load_json(ENU_TPL)
    tpl = os.path.join(ROOT, 'build', 'ENU_orig.DLL')
    # 原始英文结构模板
    game = r'C:\Program Files (x86)\Steam\steamapps\common\RoadRash'
    src = os.path.join(game, 'TEXT', 'ENU.DLL.rrzhbak')
    if not os.path.exists(src):
        src = os.path.join(game, 'TEXT', 'ENU.DLL.zhbak')
    blocks = build_dll.read_blocks(src)

    os.makedirs(os.path.join(ROOT, 'build', 'langs'), exist_ok=True)
    entries = []
    for code, native, cp, charset, face in LANGS:
        if code in OFFICIAL:
            continue
        zh = lang_json(code)
        if zh is None:
            print('  [skip] %s 无翻译' % code); continue
        # 未翻译的 id 回落英文
        full = dict(en); full.update(zh)
        newblocks = []
        for bid, arr in blocks:
            out = []
            for k, s in enumerate(arr):
                sid = (bid - 1) * 16 + k
                out.append(full.get(sid, s))
            newblocks.append((bid, out))
        dll_path = os.path.join(ROOT, 'build', 'langs', 'ENU_%s.DLL' % code)
        build_dll.build(newblocks, dll_path)
        entries.append({'code': code, 'name': native, 'cp': cp, 'charset': charset,
                        'face': face, 'dll': dll_path})
        print('  built %-6s %-18s cp%-5d cs%-3d %-12s %d bytes' % (
            code, native, cp, charset, face, os.path.getsize(dll_path)))

    # ---- 组装 pack ----
    count = len(entries)
    header_size = 8 + count * 40
    name_pool = bytearray()
    name_offs = []
    for e in entries:
        b = e['name'].encode('utf-8')
        name_offs.append(header_size + len(name_pool))
        name_pool += b + b'\0'
    data_base = header_size + len(name_pool)
    dll_blobs = []
    off = data_base
    for e in entries:
        data = open(e['dll'], 'rb').read()
        dll_blobs.append((off, data)); off += len(data)
    pack = bytearray(off)
    struct.pack_into('<II', pack, 0, 0x314B505A, count)
    for i, e in enumerate(entries):
        o = 8 + i * 40
        code_b = e['code'].encode('ascii')[:7]
        pack[o:o+len(code_b)] = code_b
        struct.pack_into('<H', pack, o+8, e['cp'])
        pack[o+10] = e['charset']
        f = e['face'].encode('ascii')[:12]
        pack[o+11] = len(f)
        pack[o+12:o+12+len(f)] = f
        nlen = len(e['name'].encode('utf-8'))
        struct.pack_into('<H', pack, o+24, nlen)
        struct.pack_into('<I', pack, o+26, name_offs[i])
        struct.pack_into('<I', pack, o+30, dll_blobs[i][0])
        struct.pack_into('<I', pack, o+34, len(dll_blobs[i][1]))
    pack[header_size:header_size+len(name_pool)] = name_pool
    for i, (o, data) in enumerate(dll_blobs):
        pack[o:o+len(data)] = data
    pack_path = os.path.join(ROOT, 'build', 'pack.bin')
    open(pack_path, 'wb').write(pack)
    print('\npack: %d 语言, %d 字节' % (count, len(pack)))

    # ---- 编译 + 附加 ----
    exe = os.path.join(ROOT, 'build', 'installer.exe')
    cmd = ['gcc', '-O2', '-s', '-o', exe, os.path.join(ROOT, 'tools', 'installer.c'),
           '-lshell32', '-luser32', '-ladvapi32', '-static-libgcc']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('COMPILE FAILED'); print(r.stdout); print(r.stderr); return
    base = open(exe, 'rb').read()
    with open(exe, 'wb') as f:
        f.write(base); f.write(pack)
        f.write(struct.pack('<II', 0x314C5252, len(pack)))
        f.write(b'\0' * 8)
    print('installer.exe: %d 字节' % os.path.getsize(exe))

if __name__ == '__main__':
    main()
