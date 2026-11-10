# -*- coding: utf-8 -*-
"""为每个已验证语言构建一个独立安装器（安装器界面用该语言）"""
import os, sys, json, struct, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_dll
from languages import LANGS

HDR = 48
META = {c: (cp, cs, face) for c, native, cp, cs, face in LANGS}

SHIP = ['zh-CN']  # 只发布简体中文

MSG = {
'zh-CN': ["暴力摩托：30 周年纪念版 — 简体中文安装程序",
 "游戏目录：", "找不到 RoadRash95.exe。请把本安装器放进游戏目录（与 RoadRash95.exe 同级）后再运行。",
 "已备份原版文本 DLL", "已备份原版 EXE", "备份已存在，跳过",
 "已写入本地化文本 DLL", "已应用字体与渲染补丁",
 "安装完成！启动游戏即为简体中文界面。", "开始卸载……",
 "已还原文本 DLL", "已还原 EXE", "没有找到备份文件", "卸载完成，游戏已恢复原版。",
 "按回车键退出……", "需要管理员权限（要写入游戏目录），提权失败。", "错误",
 "补丁失败：EXE 版本不符，或文件正被占用。",
 "检测到游戏正在运行，请先完全关闭 Road Rash 再运行本安装器。"],
'zh-TW': ["暴力摩托：30 週年紀念版 — 繁體中文安裝程式",
 "遊戲目錄：", "找不到 RoadRash95.exe。請把本安裝程式放進遊戲目錄（與 RoadRash95.exe 同級）後再執行。",
 "已備份原版文字 DLL", "已備份原版 EXE", "備份已存在，略過",
 "已寫入本地化文字 DLL", "已套用字型與算繪修補",
 "安裝完成！啟動遊戲即為繁體中文介面。", "開始解除安裝……",
 "已還原文字 DLL", "已還原 EXE", "沒有找到備份檔案", "解除安裝完成，遊戲已恢復原版。",
 "按 Enter 鍵結束……", "需要系統管理員權限（要寫入遊戲目錄），提權失敗。", "錯誤",
 "修補失敗：EXE 版本不符，或檔案正被占用。"],
'ja': ["Road Rash 30th Anniversary — 日本語インストーラー",
 "ゲームフォルダ：", "RoadRash95.exe が見つかりません。このインストーラーをゲームフォルダ（RoadRash95.exe と同じ場所）に置いてから実行してください。",
 "元のテキスト DLL をバックアップしました", "元の EXE をバックアップしました", "バックアップ済みのため省略",
 "ローカライズ済みテキスト DLL を書き込みました", "フォントと描画パッチを適用しました",
 "インストール完了！ゲームを起動すると日本語で表示されます。", "アンインストールを開始します……",
 "テキスト DLL を復元しました", "EXE を復元しました", "バックアップが見つかりません", "アンインストール完了。ゲームを元の状態に戻しました。",
 "Enter キーで終了……", "管理者権限が必要です（ゲームフォルダに書き込むため）。昇格に失敗しました。", "エラー",
 "パッチ適用に失敗しました：EXE のバージョン不一致、またはファイルが使用中です。",
 "ゲームが起動中です。Road Rash を完全に終了してから、もう一度実行してください。"],
'ko': ["Road Rash 30주년 기념판 — 한국어 설치 프로그램",
 "게임 폴더: ", "RoadRash95.exe 를 찾을 수 없습니다. 이 설치 프로그램을 게임 폴더(RoadRash95.exe 와 같은 위치)에 넣은 뒤 실행하세요.",
 "원본 텍스트 DLL 을 백업했습니다", "원본 EXE 를 백업했습니다", "백업이 이미 있어 건너뜁니다",
 "한국어 텍스트 DLL 을 기록했습니다", "글꼴 및 렌더링 패치를 적용했습니다",
 "설치 완료! 게임을 실행하면 한국어로 표시됩니다.", "제거를 시작합니다……",
 "텍스트 DLL 을 복원했습니다", "EXE 를 복원했습니다", "백업 파일을 찾을 수 없습니다", "제거 완료. 게임이 원래 상태로 돌아갔습니다.",
 "Enter 키로 종료……", "관리자 권한이 필요합니다(게임 폴더에 쓰기 위해). 권한 상승에 실패했습니다.", "오류",
 "패치 실패: EXE 버전이 다르거나 파일이 사용 중입니다.",
 "게임이 실행 중입니다. Road Rash 를 완전히 종료한 뒤 다시 실행하세요."],
}

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('FAIL', ' '.join(cmd)); print(r.stdout); print(r.stderr); sys.exit(1)
    return r

def build_thunk():
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    obj = os.path.join(ROOT, 'build', 'thunk.o')
    binp = os.path.join(ROOT, 'build', 'thunk.bin')
    ok = False
    for flags in (['-m32'], []):
        r = subprocess.run(['gcc'] + flags + ['-c','-nostdlib','-o',obj, os.path.join(HERE,'thunk.S')],
                           capture_output=True, text=True)
        if r.returncode == 0: ok = True; break
    if not ok: print('thunk compile failed'); sys.exit(1)
    sh(['objcopy','-O','binary','--only-section=.text', obj, binp])
    return open(binp, 'rb').read()

def build_one(code, en, blocks, thunk, exe_base):
    p = os.path.join(ROOT, 'translations', 'lang', code + '.json')
    zh = {int(k): v for k, v in json.load(open(p, encoding='utf8')).items()}
    full = dict(en); full.update(zh)
    full = {k: (v.replace('\t', '  ') if isinstance(v, str) else v) for k, v in full.items()}
    nb = [(b, [full.get((b-1)*16 + k, '') for k in range(16)]) for b in blocks]
    dll = os.path.join(ROOT, 'build', 'ENU_%s.DLL' % code)
    build_dll.build(nb, dll)
    dllb = open(dll, 'rb').read()

    cp, cs, face = META[code]
    msgs = MSG[code]
    name = {'zh-CN':'简体中文','zh-TW':'繁體中文','ja':'日本語','ko':'한국어'}[code]
    nameb = name.encode('utf-8'); faceb = face.encode('ascii')[:12]

    msg_tab_off = HDR
    str_off = msg_tab_off + 4 * len(msgs)
    blob = bytearray()
    offs = []
    cur = str_off
    for m in msgs:
        offs.append(cur); b = m.encode('utf-8') + b'\0'; blob += b; cur += len(b)
    name_off = cur; nb2 = nameb + b'\0'; blob += nb2; cur += len(nb2)
    dll_off = cur; blob += dllb; cur += len(dllb)
    thunk_off = cur; blob += thunk; cur += len(thunk)

    pack = bytearray(str_off + len(blob))
    struct.pack_into('<IIIIIIII', pack, 0, 0x314B505A, len(msgs), thunk_off, len(thunk), dll_off, len(dllb), name_off, msg_tab_off)
    struct.pack_into('<H', pack, 32, cp)
    pack[34] = cs
    pack[35] = len(faceb)
    pack[36:36+len(faceb)] = faceb
    for i, o in enumerate(offs):
        struct.pack_into('<I', pack, msg_tab_off + i*4, o)
    pack[str_off:str_off+len(blob)] = blob

    out = os.path.join(ROOT, 'dist', 'RoadRash-Localization-%s.exe' % code)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'wb') as f:
        f.write(exe_base); f.write(pack)
        f.write(struct.pack('<II', 0x314C5252, len(pack))); f.write(b'\0'*8)
    print('  %-6s %-8s cp%-5d cs%-3d %-12s dll=%-6d exe=%d' % (code, name, cp, cs, face, len(dllb), os.path.getsize(out)))

def main():
    thunk = build_thunk()
    print('thunk: %d bytes' % len(thunk))
    en = {int(k): v for k, v in json.load(open(os.path.join(ROOT,'translations','en.json'), encoding='utf8')).items()}
    blocks = sorted({i // 16 + 1 for i in en})
    base = os.path.join(ROOT, 'build', 'installer_base.exe')
    sh(['gcc','-O2','-s','-o',base, os.path.join(HERE,'installer.c'), '-lshell32','-luser32','-ladvapi32'])
    exe_base = open(base,'rb').read()
    for code in SHIP:
        build_one(code, en, blocks, thunk, exe_base)

if __name__ == '__main__':
    main()
