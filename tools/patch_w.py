# -*- coding: utf-8 -*-
"""给 RoadRash95.exe 打「LoadStringW 兼容层」补丁（让任意语言在任意系统代码页下正确渲染）"""
import sys, os, struct, io
import pefile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CAVE_VA   = 0x405FD8
CALL_SITES = [0x3fef5, 0x3ffb6, 0x4000a, 0x4034e, 0x403b9, 0x403f2]   # RVA
LOADSTRINGA_IAT = bytes.fromhex('ff1588c76100')
OFF_PLSW = 0x0F0
OFF_CP   = 0x0F4
OFF_BUF  = 0x128
OFF_SUSER= 0x328
OFF_SLSW = 0x338

def make_blob(code_bytes, cp):
    blob = bytearray(b'\xCC' * 0x350)
    blob[0:len(code_bytes)] = code_bytes
    struct.pack_into('<I', blob, OFF_PLSW, 0)
    struct.pack_into('<I', blob, OFF_CP, cp)
    blob[OFF_BUF:OFF_BUF+0x200] = b'\0' * 0x200
    s1 = b'user32.dll\0'; s2 = b'LoadStringW\0'
    blob[OFF_SUSER:OFF_SUSER+len(s1)] = s1
    blob[OFF_SLSW:OFF_SLSW+len(s2)] = s2
    return bytes(blob)

def analyze(exe_path):
    pe = pefile.PE(exe_path, fast_load=True)
    info = {}
    info['e_lfanew'] = pe.DOS_HEADER.e_lfanew
    info['opt'] = pe.OPTIONAL_HEADER.get_file_offset()
    info['dllchar_off'] = info['opt'] + 70
    info['sections'] = pe.FILE_HEADER.NumberOfSections
    info['sec_tab'] = info['opt'] + pe.FILE_HEADER.SizeOfOptionalHeader
    text = [s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text'][0]
    info['text_hdr'] = text.get_file_offset()
    info['cave_off'] = pe.get_offset_from_rva(CAVE_VA - pe.OPTIONAL_HEADER.ImageBase)
    info['call_offs'] = [pe.get_offset_from_rva(r) for r in CALL_SITES]
    pe.close()
    return info

def check_cave(data, info):
    off = info['cave_off']
    region = data[off:off+0x350]
    bad = [i for i, b in enumerate(region) if b != 0xCC]
    return len(bad) == 0, bad[:5]

def apply(exe_path, code_bytes, cp, backup=True):
    pe = pefile.PE(exe_path, fast_load=True)
    data = bytearray(open(exe_path, 'rb').read())
    info = analyze(exe_path)
    ok_cave, bad = check_cave(bytes(data), info)
    report = []
    report.append(('code cave 0x%x 可用' % CAVE_VA, 'ok' if ok_cave else 'BAD %r' % bad))

    # 1) 关掉 ASLR（固定映像基址，桩函数里用的是绝对地址）
    dc_off = info['dllchar_off']
    dc = struct.unpack_from('<H', data, dc_off)[0]
    if dc & 0x40:
        struct.pack_into('<H', data, dc_off, dc & ~0x40)
        report.append(('清除 DYNAMIC_BASE(ASLR)', 'ok'))
    else:
        report.append(('清除 DYNAMIC_BASE(ASLR)', 'already'))

    # 2) .text 设为可写（桩函数在代码洞里放缓存与缓冲区）
    th = info['text_hdr']
    ch = struct.unpack_from('<I', data, th + 36)[0]
    if not (ch & 0x80000000):
        struct.pack_into('<I', data, th + 36, ch | 0x80000000)
        report.append(('.text 增加 MEM_WRITE', 'ok'))
    else:
        report.append(('.text 增加 MEM_WRITE', 'already'))

    # 3) 写入桩与数据
    blob = make_blob(code_bytes, cp)
    data[info['cave_off']:info['cave_off']+len(blob)] = blob
    report.append(('写入桩代码 + 数据 (%d B)' % len(blob), 'ok'))

    # 4) 改 6 处 LoadStringA 调用
    for rva, off in zip(CALL_SITES, info['call_offs']):
        cur = bytes(data[off:off+6])
        if cur == LOADSTRINGA_IAT:
            rel = CAVE_VA - (0x400000 + rva + 5)
            data[off:off+6] = b'\xE8' + struct.pack('<i', rel) + b'\x90'
            report.append(('调用点 0x%x' % rva, 'ok'))
        elif cur[0] == 0xE8:
            report.append(('调用点 0x%x' % rva, 'already'))
        else:
            report.append(('调用点 0x%x' % rva, 'MISMATCH %r' % cur))
    pe.close()

    ok = all(r[1] in ('ok', 'already') for r in report)
    if ok:
        if backup:
            bak = exe_path + '.rrzhbak'
            if not os.path.exists(bak):
                import shutil; shutil.copyfile(exe_path, bak)
        with open(exe_path, 'r+b') as f:
            f.seek(0); f.write(bytes(data)); f.truncate()
    return report, ok

if __name__ == '__main__':
    exe = sys.argv[1]
    cp = int(sys.argv[2])
    codef = sys.argv[3] if len(sys.argv) > 3 else 'thunk.bin'
    code = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), codef), 'rb').read()
    rep, ok = apply(exe, code, cp)
    for n, s in rep: print('  %-40s %s' % (n, s))
    print('RESULT', 'OK' if ok else 'FAILED')
