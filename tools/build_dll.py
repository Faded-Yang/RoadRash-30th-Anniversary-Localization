# -*- coding: utf-8 -*-
"""从 ENU.DLL 的块结构 + 中文 JSON 生成 resource-only 的 TEXT\CHS.dll"""
import json, struct, sys, os, io
import pefile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def read_blocks(path):
    pe = pefile.PE(path, fast_load=False)
    blocks = []
    for er in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if er.id != 6: continue
        for e1 in er.directory.entries:
            for e2 in e1.directory.entries:
                d = pe.get_data(e2.data.struct.OffsetToData, e2.data.struct.Size)
                p = 0; arr = []
                for k in range(16):
                    if p + 2 > len(d):
                        arr.append(''); continue
                    ln = int.from_bytes(d[p:p+2], 'little'); p += 2
                    if ln > 0:
                        s = d[p:p+ln*2].decode('utf-16le', 'replace'); p += ln*2
                        arr.append(s)
                    else:
                        arr.append('')
                blocks.append((e1.id, arr))
    blocks.sort(key=lambda x: x[0])
    return blocks

def encode_block(strings):
    out = bytearray()
    for s in strings:
        if not s:
            out += struct.pack('<H', 0)
        else:
            b = s.encode('utf-16le'); n = len(b)//2
            if n > 0xFFFF: raise ValueError('string too long')
            out += struct.pack('<H', n) + b
    return bytes(out)

def al(x, a): return (x + a - 1)//a*a

def build(blocks, out_path, lang_id=0x409, image_base=0x10000000):
    n = len(blocks)
    root_off = 0
    type_dir_off = 24
    block_dirs_off = type_dir_off + 16 + n*8
    data_entries_off = block_dirs_off + n*24
    blobs_off = al(data_entries_off + n*16, 8)

    blobs = []; cur = blobs_off
    for bid, arr in blocks:
        data = encode_block(arr)
        blobs.append((bid, cur, data))
        cur = al(cur + len(data), 4)
    rsrc_size = max(cur, 8)

    buf = bytearray(rsrc_size)
    def u16(o, v): struct.pack_into('<H', buf, o, v)
    def u32(o, v): struct.pack_into('<I', buf, o, v)
    def w(o, b): buf[o:o+len(b)] = b

    u16(root_off+12, 0); u16(root_off+14, 1)
    u32(root_off+16, 6); u32(root_off+20, 0x80000000 | type_dir_off)
    u16(type_dir_off+12, 0); u16(type_dir_off+14, n)
    for i, (bid, _, _) in enumerate(blobs):
        e = type_dir_off + 16 + i*8
        u32(e, bid); u32(e+4, 0x80000000 | (block_dirs_off + i*24))
    for i, (bid, boff, data) in enumerate(blobs):
        d = block_dirs_off + i*24
        u16(d+12, 0); u16(d+14, 1)
        u32(d+16, lang_id); u32(d+20, data_entries_off + i*16)   # 叶节点：不带 0x80000000
        de = data_entries_off + i*16
        u32(de, 0x1000 + boff); u32(de+4, len(data)); u32(de+8, 0); u32(de+12, 0)
        w(boff, data)

    sa, fa = 0x1000, 0x200
    rawsize = al(rsrc_size, fa)
    hdr_end = 0x80 + 4 + 20 + 224 + 40
    raw_ptr = al(hdr_end, fa)
    img = al(sa + rsrc_size, sa)

    pe = bytearray(raw_ptr + rawsize)
    def P16(o, v): struct.pack_into('<H', pe, o, v)
    def P32(o, v): struct.pack_into('<I', pe, o, v)

    pe[0:2] = b'MZ'; P32(0x3c, 0x80)
    pe[0x80:0x84] = b'PE\0\0'
    coff = 0x84
    P16(coff+0, 0x14c); P16(coff+2, 1)
    P32(coff+4, 0); P32(coff+8, 0); P32(coff+12, 0)
    P16(coff+16, 224); P16(coff+18, 0x2102)

    opt = coff + 20
    P16(opt+0, 0x10b); pe[opt+2] = 6; pe[opt+3] = 0
    P32(opt+4, 0)          # SizeOfCode
    P32(opt+8, rawsize)    # SizeOfInitializedData
    P32(opt+12, 0)         # SizeOfUninitializedData
    P32(opt+16, 0)         # AddressOfEntryPoint
    P32(opt+20, 0)         # BaseOfCode
    P32(opt+24, 0)         # BaseOfData
    P32(opt+28, image_base)
    P32(opt+32, sa); P32(opt+36, fa)
    P16(opt+40, 4); P16(opt+42, 0)
    P16(opt+44, 0); P16(opt+46, 0)
    P16(opt+48, 4); P16(opt+50, 0)
    P32(opt+52, 0)         # Win32VersionValue
    P32(opt+56, img)       # SizeOfImage
    P32(opt+60, raw_ptr)   # SizeOfHeaders
    P32(opt+64, 0)         # CheckSum
    P16(opt+68, 2)         # Subsystem = GUI
    P16(opt+70, 0)         # DllCharacteristics
    P32(opt+72, 0x100000); P32(opt+76, 0x1000)
    P32(opt+80, 0x100000); P32(opt+84, 0x1000)
    P32(opt+88, 0)         # LoaderFlags
    P32(opt+92, 16)        # NumberOfRvaAndSizes
    dd = opt + 96
    P32(dd + 2*8, sa); P32(dd + 2*8 + 4, rsrc_size)

    sh = opt + 224
    pe[sh:sh+8] = b'.rsrc\0\0\0'
    P32(sh+8, rsrc_size); P32(sh+12, sa); P32(sh+16, rawsize); P32(sh+20, raw_ptr)
    P32(sh+24, 0); P32(sh+28, 0)
    P16(sh+32, 0); P16(sh+34, 0)
    P32(sh+36, 0x40000040)

    pe[raw_ptr:raw_ptr+len(buf)] = buf
    open(out_path, 'wb').write(pe)
    return out_path, rsrc_size, len(pe)

def main():
    enu, zh_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    blocks = read_blocks(enu)
    zh = {}
    if os.path.exists(zh_path):
        zh = {int(k): v for k, v in json.load(open(zh_path, encoding='utf8')).items() if v}
    missing = 0; newblocks = []
    for bid, arr in blocks:
        newarr = []
        for k, s in enumerate(arr):
            sid = (bid-1)*16 + k
            if sid in zh:
                newarr.append(zh[sid])
            else:
                if s: missing += 1
                newarr.append(s)
        newblocks.append((bid, newarr))
    p, rs, total = build(newblocks, out)
    print('built %s  rsrc=%d  file=%d  fallback-en=%d  blocks=%d' % (p, rs, total, missing, len(newblocks)))

if __name__ == '__main__':
    main()
