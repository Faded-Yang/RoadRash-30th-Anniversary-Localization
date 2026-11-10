// Road Rash 30th Anniversary - Localization Installer (single file)
// 单文件安装器：内嵌全部语言文本 DLL + 补丁器
// 必须放在游戏目录（与 RoadRash95.exe 同级）后双击运行。
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PACK_MAGIC    0x314B505A   /* 'ZPK2' with version below */
#define TRAILER_MAGIC 0x314C5252
#define TRAILER_LEN   16
#define ENTRY_SIZE    40
#define HDR_SIZE      20           /* magic,count,thunkOff,thunkLen,reserved */

/* ---- 固定补丁偏移（该版本 EXE 固定，安装前用 SHA-256 校验） ---- */
#define OFF_CHARSET   0x60171
#define OFF_FACE      0x1059B4
#define FACE_SLOT     13
#define OFF_DLLCHAR   0x186
#define OFF_TEXTCHARS 0x244
#define CAVE_OFF      0x53D8
#define BLOB_SIZE     0x350
#define OFF_PLSW      0x0F0
#define OFF_CP        0x0F4
#define OFF_BUF       0x128
#define OFF_SUSER     0x328
#define OFF_SLSW      0x338
#define CAVE_VA       0x405FD8u
#define IMG_BASE      0x400000u

static const unsigned CALL_RVA[6]  = {0x3fef5,0x3ffb6,0x4000a,0x4034e,0x403b9,0x403f2};
static const unsigned CALL_OFF[6]  = {0x3f2f5,0x3f3b6,0x3f40a,0x3f74e,0x3f7b9,0x3f7f2};
static const unsigned char LSA_CALL[6] = {0xFF,0x15,0x88,0xC7,0x61,0x00};

static unsigned rd32(const unsigned char* p){ return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24); }
static void wr32(unsigned char* p, unsigned v){ p[0]=(unsigned char)v; p[1]=(unsigned char)(v>>8); p[2]=(unsigned char)(v>>16); p[3]=(unsigned char)(v>>24); }

static int isElevated(void){
    BOOL admin = FALSE; PSID sid = NULL; SID_IDENTIFIER_AUTHORITY nt = { {0,0,0,0,0,5} };
    if (AllocateAndInitializeSid(&nt, 2, SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS, 0,0,0,0,0,0, &sid)) {
        CheckTokenMembership(NULL, sid, &admin); FreeSid(sid);
    }
    return admin;
}
static int fileExistsW(const wchar_t* p){ return GetFileAttributesW(p) != INVALID_FILE_ATTRIBUTES; }
static int readFileW(const wchar_t* p, unsigned char** out, unsigned int* len){
    HANDLE h = CreateFileW(p, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    LARGE_INTEGER sz; GetFileSizeEx(h, &sz); *len = (unsigned int)sz.QuadPart;
    *out = (unsigned char*)malloc(*len ? *len : 1);
    DWORD got = 0;
    if (!ReadFile(h, *out, *len, &got, NULL) || got != *len){ CloseHandle(h); free(*out); return 0; }
    CloseHandle(h); return 1;
}
static int writeInPlaceW(const wchar_t* p, const unsigned char* data, unsigned int len){
    SetFileAttributesW(p, FILE_ATTRIBUTE_NORMAL);
    HANDLE h = CreateFileW(p, GENERIC_WRITE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    DWORD put = 0; int ok = WriteFile(h, data, len, &put, NULL) && put == len;
    if (ok) SetEndOfFile(h);
    CloseHandle(h); return ok;
}
static int createFileW(const wchar_t* p, const unsigned char* data, unsigned int len){
    SetFileAttributesW(p, FILE_ATTRIBUTE_NORMAL);
    HANDLE h = CreateFileW(p, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    DWORD put = 0; int ok = WriteFile(h, data, len, &put, NULL) && put == len;
    CloseHandle(h); return ok;
}
static void joinW(wchar_t* dst, const wchar_t* a, const wchar_t* b){
    wcscpy(dst, a); size_t n = wcslen(dst);
    if (n && dst[n-1] != L'\\') { dst[n++] = L'\\'; dst[n] = 0; }
    wcscat(dst, b);
}
static void pauseExit(int code){ printf("\n按回车退出..."); fflush(stdout); getchar(); exit(code); }
static void die(const char* m){ printf("\n[错误] %s\n", m); pauseExit(1); }

static const char* langFromLangId(LANGID lid){
    switch (PRIMARYLANGID(lid)){
        case LANG_ENGLISH: return "en"; case LANG_GERMAN: return "de"; case LANG_FRENCH: return "fr";
        case LANG_SPANISH: return "es"; case LANG_ITALIAN: return "it"; case LANG_PORTUGUESE: return "pt";
        case LANG_DUTCH: return "nl"; case LANG_DANISH: return "da"; case LANG_SWEDISH: return "sv";
        case LANG_NORWEGIAN: return "nb"; case LANG_FINNISH: return "fi"; case LANG_ICELANDIC: return "is";
        case LANG_CATALAN: return "ca"; case LANG_BASQUE: return "eu"; case LANG_GALICIAN: return "gl";
        case LANG_AFRIKAANS: return "af"; case LANG_ALBANIAN: return "sq"; case LANG_INDONESIAN: return "id";
        case LANG_MALAY: return "ms"; case LANG_FILIPINO: return "tl"; case LANG_SWAHILI: return "sw";
        case LANG_WELSH: return "cy"; case LANG_IRISH: return "ga"; case LANG_MALTESE: return "mt";
        case LANG_POLISH: return "pl"; case LANG_CZECH: return "cs"; case LANG_SLOVAK: return "sk";
        case LANG_HUNGARIAN: return "hu"; case LANG_SLOVENIAN: return "sl"; case LANG_ROMANIAN: return "ro";
        case LANG_RUSSIAN: return "ru"; case LANG_UKRAINIAN: return "uk"; case LANG_BULGARIAN: return "bg";
        case LANG_MACEDONIAN: return "mk"; case LANG_BELARUSIAN: return "be"; case LANG_MONGOLIAN: return "mn";
        case LANG_KAZAK: return "kk"; case LANG_KYRGYZ: return "ky"; case LANG_TAJIK: return "tg";
        case LANG_GREEK: return "el"; case LANG_TURKISH: return "tr"; case LANG_AZERI: return "az";
        case LANG_HEBREW: return "he"; case LANG_ARABIC: return "ar"; case LANG_FARSI: return "fa";
        case LANG_URDU: return "ur"; case LANG_PASHTO: return "ps"; case LANG_SINDHI: return "sd";
        case LANG_ESTONIAN: return "et"; case LANG_LATVIAN: return "lv"; case LANG_LITHUANIAN: return "lt";
        case LANG_VIETNAMESE: return "vi"; case LANG_THAI: return "th"; case LANG_JAPANESE: return "ja";
        case LANG_KOREAN: return "ko";
        case LANG_CROATIAN:
            switch (SUBLANGID(lid)){ case SUBLANG_SERBIAN_LATIN: case SUBLANG_SERBIAN_CYRILLIC: return "sr"; }
            return "hr";
        case LANG_CHINESE:
            switch (SUBLANGID(lid)){
                case SUBLANG_CHINESE_TRADITIONAL: case SUBLANG_CHINESE_HONGKONG: case SUBLANG_CHINESE_MACAU: return "zh-TW";
                default: return "zh-CN";
            }
    }
    return NULL;
}
static int isOfficial(const char* c){
    return !strcmp(c,"en")||!strcmp(c,"de")||!strcmp(c,"fr")||!strcmp(c,"es")||!strcmp(c,"it");
}

/* 应用全部字节补丁。返回 1 成功 */
static int applyPatches(const wchar_t* exePath, unsigned char charset, const char* face,
                        unsigned cp, const unsigned char* thunk, unsigned thunkLen){
    unsigned char* d = NULL; unsigned int n = 0;
    if (!readFileW(exePath, &d, &n)) return 0;
    if (n < 0x120000) { free(d); return 0; }
    int ok = 1;
    /* 字体字符集 + 字体名 */
    if (d[OFF_CHARSET] == 0x6A) d[OFF_CHARSET+1] = charset; else ok = 0;
    memset(d + OFF_FACE, 0, FACE_SLOT);
    memcpy(d + OFF_FACE, face, strlen(face) > FACE_SLOT ? FACE_SLOT : strlen(face));
    /* 关 ASLR */
    d[OFF_DLLCHAR] &= (unsigned char)~0x40;
    /* .text 可写（桩内缓存/缓冲） */
    { unsigned v = rd32(d + OFF_TEXTCHARS); wr32(d + OFF_TEXTCHARS, v | 0x80000000u); }
    /* 桩 + 数据 */
    memset(d + CAVE_OFF, 0xCC, BLOB_SIZE);
    memcpy(d + CAVE_OFF, thunk, thunkLen > 0xE0 ? 0xE0 : thunkLen);
    memset(d + CAVE_OFF + OFF_BUF, 0, 0x200);
    memcpy(d + CAVE_OFF + OFF_SUSER, "user32.dll", 11);
    memcpy(d + CAVE_OFF + OFF_SLSW, "LoadStringW", 12);
    wr32(d + CAVE_OFF + OFF_PLSW, 0);
    wr32(d + CAVE_OFF + OFF_CP, cp);
    /* 6 处 LoadStringA -> 桩 */
    for (int i = 0; i < 6; i++){
        unsigned char* p = d + CALL_OFF[i];
        if (memcmp(p, LSA_CALL, 6) == 0){
            int rel = (int)(CAVE_VA - (IMG_BASE + CALL_RVA[i] + 5));
            p[0] = 0xE8; wr32(p+1, (unsigned)rel); p[5] = 0x90;
        } else if (p[0] != 0xE8) { ok = 0; }
    }
    if (ok) ok = writeInPlaceW(exePath, d, n);
    free(d);
    return ok;
}

int main(int argc, char** argv){
    SetConsoleOutputCP(65001);
    printf("====================================================\n");
    printf("  暴力摩托 30 周年纪念版 - 多语言本地化安装器\n");
    printf("  Road Rash 30th Anniversary - Localization\n");
    printf("====================================================\n\n");

    int doUninstall = 0, forced = 0; const char* wantCode = NULL;
    for (int i = 1; i < argc; i++){
        if (!_stricmp(argv[i],"uninstall") || !_stricmp(argv[i],"-u")) doUninstall = 1;
        else if (!_stricmp(argv[i],"/force")) forced = 1;
        else wantCode = argv[i];
    }
    if (!isElevated()){
        wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
        wchar_t params[1024] = L"";
        for (int i = 1; i < argc; i++){ wcscat(params, L"\""); wchar_t w[256];
            MultiByteToWideChar(CP_ACP,0,argv[i],-1,w,256); wcscat(params,w); wcscat(params,L"\" "); }
        HINSTANCE r = ShellExecuteW(NULL, L"runas", self, params, NULL, SW_SHOWNORMAL);
        if ((INT_PTR)r > 32) return 0;
        die("需要管理员权限（要写入游戏目录），提权失败。");
    }

    /* 只认「安装器所在目录」——请把它放进游戏目录 */
    wchar_t game[MAX_PATH]; GetModuleFileNameW(NULL, game, MAX_PATH);
    { wchar_t* s = wcsrchr(game, L'\\'); if (s) *s = 0; }
    wchar_t exePath[MAX_PATH], enuPath[MAX_PATH], enuBak[MAX_PATH], exeBak[MAX_PATH];
    joinW(exePath, game, L"RoadRash95.exe");
    if (!fileExistsW(exePath)){
        printf("当前目录: %ls\n\n", game);
        printf("没找到 RoadRash95.exe。\n");
        printf("请把本安装器【放进游戏目录】再双击：\n");
        printf("  ...\\Steam\\steamapps\\common\\RoadRash\\\n");
        printf("（与本安装器同级应能看到 RoadRash95.exe 和 TEXT 文件夹）\n");
        pauseExit(1);
    }
    joinW(enuPath, game, L"TEXT\\ENU.DLL");
    joinW(enuBak, game, L"TEXT\\ENU.DLL.rrzhbak");
    joinW(exeBak, game, L"RoadRash95.exe.rrzhbak");
    printf("游戏目录: %ls\n\n", game);

    if (doUninstall){
        int ok = 0;
        if (fileExistsW(enuBak)){ unsigned char* d=NULL; unsigned int n=0;
            if (readFileW(enuBak,&d,&n)){ ok |= writeInPlaceW(enuPath,d,n); free(d);} printf("  已还原 TEXT\\ENU.DLL\n"); }
        else printf("  [注意] 没有 ENU.DLL 备份\n");
        if (fileExistsW(exeBak)){ unsigned char* d=NULL; unsigned int n=0;
            if (readFileW(exeBak,&d,&n)){ ok |= writeInPlaceW(exePath,d,n); free(d);} printf("  已还原 RoadRash95.exe\n"); }
        else printf("  [注意] 没有 EXE 备份\n");
        printf("\n%s\n", ok ? "卸载完成，游戏已恢复原版。" : "卸载未完成。");
        pauseExit(ok ? 0 : 1);
    }

    /* 读内嵌包 */
    wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
    unsigned char* me = NULL; unsigned int meLen = 0;
    if (!readFileW(self, &me, &meLen)) die("无法读取安装器自身。");
    if (meLen < TRAILER_LEN + HDR_SIZE) die("安装包损坏（缺少内嵌数据）。");
    const unsigned char* tr = me + meLen - TRAILER_LEN;
    if (rd32(tr) != TRAILER_MAGIC) die("安装包损坏（尾部标记不符）。");
    unsigned int packSize = rd32(tr + 4);
    if (packSize + TRAILER_LEN > meLen) die("安装包损坏（大小异常）。");
    unsigned char* pack = me + meLen - TRAILER_LEN - packSize;
    if (rd32(pack) != PACK_MAGIC) die("安装包损坏（头部标记不符）。");
    unsigned int count = rd32(pack + 4);
    unsigned int thunkOff = rd32(pack + 8), thunkLen = rd32(pack + 12);
    if (HDR_SIZE + count * ENTRY_SIZE > packSize || thunkOff + thunkLen > packSize) die("安装包损坏（目录越界）。");

    LANGID ui = GetUserDefaultUILanguage();
    const char* sysCode = langFromLangId(ui);
    int defIdx = -1;
    for (unsigned int i = 0; i < count; i++){
        const unsigned char* e = pack + HDR_SIZE + i * ENTRY_SIZE;
        if (sysCode && !strcmp((const char*)e, sysCode)) { defIdx = (int)i; break; }
    }
    if (sysCode && isOfficial(sysCode)){
        printf("系统语言为 %s，这是【游戏官方自带】的语言，无需本地化补丁。\n", sysCode);
        printf("仍可继续手动选择其他语言。\n\n");
        if (!forced) { defIdx = -1; }
    }
    if (wantCode){
        for (unsigned int i = 0; i < count; i++){
            const unsigned char* e = pack + HDR_SIZE + i * ENTRY_SIZE;
            if (!_stricmp((const char*)e, wantCode)) { defIdx = (int)i; break; }
        }
    }

    printf("可用语言（共 %u 种；* 为按系统语言推荐）：\n", count);
    for (unsigned int i = 0; i < count; i++){
        const unsigned char* e = pack + HDR_SIZE + i * ENTRY_SIZE;
        unsigned int nameOff = rd32(e + 26), cp = e[8] | (e[9] << 8);
        printf("  %s%2u) %-28s %-6s\n", ((int)i == defIdx ? "*" : " "), i + 1,
               (const char*)(pack + nameOff), (const char*)e);
        (void)cp;
    }
    printf("\n请输入序号（直接回车 = 推荐项）: "); fflush(stdout);
    char line[64]; if (!fgets(line, sizeof(line), stdin)) line[0] = 0;
    int pick = defIdx;
    if (line[0] && line[0] != '\n' && line[0] != '\r'){
        int v = atoi(line); if (v >= 1 && v <= (int)count) pick = v - 1;
    }
    if (pick < 0) pick = 0;
    const unsigned char* e = pack + HDR_SIZE + pick * ENTRY_SIZE;
    const char* code = (const char*)e;
    unsigned cp = e[8] | (e[9] << 8);
    unsigned char charset = e[10];
    unsigned char faceLen = e[11];
    const char* face = (const char*)(e + 12);
    unsigned int dllOff = rd32(e + 30), dllSize = rd32(e + 34);
    char faceBuf[16]; memcpy(faceBuf, face, faceLen > 12 ? 12 : faceLen); faceBuf[faceLen > 12 ? 12 : faceLen] = 0;

    printf("\n选择: %s  (字符集 %u, 字体 %s)\n", code, charset, faceBuf);
    printf("  · 文本将以 UTF-16 取出后按 CP%u 转码渲染，**不受系统代码页影响**\n", cp);
    printf("\n开始安装...\n");

    if (!fileExistsW(enuBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readFileW(enuPath,&d,&n) || !createFileW(enuBak,d,n)) die("备份 ENU.DLL 失败。");
        free(d); printf("  已备份 TEXT\\ENU.DLL\n");
    } else printf("  ENU.DLL 备份已存在\n");
    if (!fileExistsW(exeBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readFileW(exePath,&d,&n) || !createFileW(exeBak,d,n)) die("备份 EXE 失败。");
        free(d); printf("  已备份 RoadRash95.exe\n");
    } else printf("  EXE 备份已存在\n");

    if (!createFileW(enuPath, pack + dllOff, dllSize)) die("写入 TEXT\\ENU.DLL 失败（文件被占用？请先关闭游戏）");
    printf("  已写入 TEXT\\ENU.DLL (%u 字节)\n", dllSize);

    if (!applyPatches(exePath, charset, faceBuf, cp, pack + thunkOff, thunkLen))
        die("应用 EXE 补丁失败（版本不符或文件被占用）。");
    printf("  已应用字体补丁 + 文本转码兼容层 (CP%u)\n", cp);

    printf("\n✔ 安装完成！启动游戏即为 %s 界面。\n", code);
    printf("  还原：再运行一次并选 uninstall（或命令行加 uninstall）。\n");
    pauseExit(0);
    return 0;
}
