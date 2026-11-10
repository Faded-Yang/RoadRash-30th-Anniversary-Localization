# -*- coding: utf-8 -*-
"""字体补丁：charset + 字体名（等长原地写）"""
import sys, os
def apply(path, charset, face):
    data = bytearray(open(path, 'rb').read())
    if data[0x60171] != 0x6A:
        return False, 'charset 补丁点不符: %r' % bytes(data[0x60171:0x60173])
    data[0x60172] = charset
    fb = face.encode('ascii')[:12]
    data[0x1059b4:0x1059b4+13] = bytes(13)
    data[0x1059b4:0x1059b4+len(fb)] = fb
    with open(path, 'r+b') as f:
        f.seek(0); f.write(bytes(data)); f.truncate()
    return True, 'ok'
if __name__ == '__main__':
    ok, msg = apply(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    print('FONT', 'OK' if ok else 'FAIL ' + msg)
