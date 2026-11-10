// Road Rash 30th Anniversary Edition - Localization Installer (single file)
// gcc -O2 -municode? no: use ANSI main + wide APIs
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PACK_MAGIC    0x314B505A   /* 'ZPK1' */
#define TRAILER_MAGIC 0x314C5252   /* 'RRL1' */
#define TRAILER_LEN   16
#define ENTRY_SIZE    40

#define OFF_CHARSET   0x60171
#define OFF_FACE      0x1059B4
#define FACE_SLOT     13

static unsigned int rd32(const unsigned char* p){ return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24); }

static int isElevated(void){
    BOOL admin = FALSE; PSID sid = NULL; SID_IDENTIFIER_AUTHORITY nt = { {0,0,0,0,0,5} };
    if (AllocateAndInitializeSid(&nt, 2, SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS,
                                 0,0,0,0,0,0, &sid)) {
        CheckTokenMembership(NULL, sid, &admin);
        FreeSid(sid);
    }
    return admin;
}
static int fileExistsW(const wchar_t* p){ return GetFileAttributesW(p) != INVALID_FILE_ATTRIBUTES; }
static int readFileW(const wchar_t* p, unsigned char** out, unsigned int* len){
    HANDLE h = CreateFileW(p, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    LARGE_INTEGER sz; GetFileSizeEx(h, &sz);
    *len = (unsigned int)sz.QuadPart;
    *out = (unsigned char*)malloc(*len ? *len : 1);
    DWORD got = 0;
    if (!ReadFile(h, *out, *len, &got, NULL) || got != *len){ CloseHandle(h); free(*out); return 0; }
    CloseHandle(h); return 1;
}
static int writeFileW(const wchar_t* p, const unsigned char* data, unsigned int len){
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
static void pauseExit(int code){
    printf("\n按回车退出..."); fflush(stdout); getchar(); exit(code);
}
static void die(const char* m){ printf("\n[错误] %s\n", m); pauseExit(1); }

/* 主语言 ID -> 我们的语言代码 */
static const char* langFromLangId(LANGID lid){
    switch (PRIMARYLANGID(lid)){
        case LANG_ENGLISH: return "en";
        case LANG_GERMAN: return "de";
        case LANG_FRENCH: return "fr";
        case LANG_SPANISH: return "es";
        case LANG_ITALIAN: return "it";
        case LANG_PORTUGUESE: return "pt";
        case LANG_DUTCH: return "nl";
        case LANG_DANISH: return "da";
        case LANG_SWEDISH: return "sv";
        case LANG_NORWEGIAN: return "nb";
        case LANG_FINNISH: return "fi";
        case LANG_ICELANDIC: return "is";
        case LANG_CATALAN: return "ca";
        case LANG_BASQUE: return "eu";
        case LANG_GALICIAN: return "gl";
        case LANG_AFRIKAANS: return "af";
        case LANG_ALBANIAN: return "sq";
        case LANG_INDONESIAN: return "id";
        case LANG_MALAY: return "ms";
        case LANG_FILIPINO: return "tl";
        case LANG_SWAHILI: return "sw";
        case LANG_WELSH: return "cy";
        case LANG_IRISH: return "ga";
        case LANG_MALTESE: return "mt";
        case LANG_POLISH: return "pl";
        case LANG_CZECH: return "cs";
        case LANG_SLOVAK: return "sk";
        case LANG_HUNGARIAN: return "hu";
        case LANG_SLOVENIAN: return "sl";
        case LANG_CROATIAN:  /* 0x1a 同时是 Serbian 的主语言号，按子语言区分 */
            switch (SUBLANGID(lid)){
                case SUBLANG_SERBIAN_LATIN:
                case SUBLANG_SERBIAN_CYRILLIC: return "sr";
            }
            return "hr";
        case LANG_ROMANIAN: return "ro";
        case LANG_RUSSIAN: return "ru";
        case LANG_UKRAINIAN: return "uk";
        case LANG_BULGARIAN: return "bg";
        case LANG_MACEDONIAN: return "mk";
        case LANG_BELARUSIAN: return "be";
        case LANG_MONGOLIAN: return "mn";
        case LANG_KAZAK: return "kk";
        case LANG_KYRGYZ: return "ky";
        case LANG_TAJIK: return "tg";
        case LANG_GREEK: return "el";
        case LANG_TURKISH: return "tr";
        case LANG_AZERI: return "az";
        case LANG_HEBREW: return "he";
        case LANG_ARABIC: return "ar";
        case LANG_FARSI: return "fa";
        case LANG_URDU: return "ur";
        case LANG_PASHTO: return "ps";
        case LANG_SINDHI: return "sd";
        case LANG_ESTONIAN: return "et";
        case LANG_LATVIAN: return "lv";
        case LANG_LITHUANIAN: return "lt";
        case LANG_VIETNAMESE: return "vi";
        case LANG_THAI: return "th";
        case LANG_JAPANESE: return "ja";
        case LANG_KOREAN: return "ko";
        case LANG_CHINESE:
            switch (SUBLANGID(lid)){
                case SUBLANG_CHINESE_TRADITIONAL:
                case SUBLANG_CHINESE_HONGKONG:
                case SUBLANG_CHINESE_MACAU: return "zh-TW";
                default: return "zh-CN";
            }
    }
    return NULL;
}
static int isOfficial(const char* code){
    return !strcmp(code,"en")||!strcmp(code,"de")||!strcmp(code,"fr")||!strcmp(code,"es")||!strcmp(code,"it");
}

/* ---------------- 找游戏目录 ---------------- */
static int findGameDir(wchar_t* out){
    wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
    wchar_t* slash = wcsrchr(self, L'\\'); if (slash) *slash = 0;
    wchar_t cand[MAX_PATH];
    /* 1) 安装器所在目录（用户把 exe 放进游戏目录） */
    joinW(cand, self, L"RoadRash95.exe");
    if (fileExistsW(cand)) { wcscpy(out, self); return 1; }
    /* 2) 安装器所在目录的上一级 */
    wchar_t up[MAX_PATH]; wcscpy(up, self);
    slash = wcsrchr(up, L'\\'); if (slash) { *slash = 0;
        joinW(cand, up, L"RoadRash95.exe"); if (fileExistsW(cand)) { wcscpy(out, up); return 1; } }
    /* 3) 常见 Steam 路径 */
    const wchar_t* fixed[] = {
        L"C:\\Program Files (x86)\\Steam\\steamapps\\common\\RoadRash",
        L"C:\\Program Files\\Steam\\steamapps\\common\\RoadRash",
        L"D:\\Steam\\steamapps\\common\\RoadRash",
        L"D:\\SteamLibrary\\steamapps\\common\\RoadRash",
        L"E:\\SteamLibrary\\steamapps\\common\\RoadRash",
        L"F:\\SteamLibrary\\steamapps\\common\\RoadRash"
    };
    for (int i = 0; i < (int)(sizeof(fixed)/sizeof(fixed[0])); i++){
        joinW(cand, fixed[i], L"RoadRash95.exe");
        if (fileExistsW(cand)) { wcscpy(out, fixed[i]); return 1; }
    }
    /* 4) 从注册表读 Steam 库 */
    HKEY hk;
    const wchar_t* keys[] = { L"SOFTWARE\\Valve\\Steam", L"SOFTWARE\\WOW6432Node\\Valve\\Steam" };
    for (int k = 0; k < 2; k++){
        if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, keys[k], 0, KEY_READ, &hk) == ERROR_SUCCESS){
            wchar_t path[MAX_PATH]; DWORD sz = sizeof(path);
            if (RegQueryValueExW(hk, L"InstallPath", NULL, NULL, (LPBYTE)path, &sz) == ERROR_SUCCESS){
                joinW(cand, path, L"steamapps\\common\\RoadRash\\RoadRash95.exe");
                if (fileExistsW(cand)) { joinW(out, path, L"steamapps\\common\\RoadRash"); RegCloseKey(hk); return 1; }
            }
            RegCloseKey(hk);
        }
    }
    return 0;
}

int main(int argc, char** argv){
    SetConsoleOutputCP(65001);
    printf("====================================================\n");
    printf("  暴力摩托 30 周年纪念版 - 多语言本地化安装器\n");
    printf("  Road Rash 30th Anniversary - Localization\n");
    printf("====================================================\n\n");

    int doUninstall = 0, forced = 0;
    const char* wantCode = NULL;
    for (int i = 1; i < argc; i++){
        if (!_stricmp(argv[i], "uninstall") || !_stricmp(argv[i], "-u")) doUninstall = 1;
        else if (!_stricmp(argv[i], "/force")) forced = 1;
        else wantCode = argv[i];
    }

    if (!isElevated()){
        wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
        wchar_t params[1024] = L"";
        for (int i = 1; i < argc; i++){
            wcscat(params, L"\"");
            wchar_t w[256]; MultiByteToWideChar(CP_ACP, 0, argv[i], -1, w, 256); wcscat(params, w);
            wcscat(params, L"\" ");
        }
        HINSTANCE r = ShellExecuteW(NULL, L"runas", self, params, NULL, SW_SHOWNORMAL);
        if ((INT_PTR)r > 32) return 0;
        die("需要管理员权限（要写入游戏目录），提权失败。");
    }

    wchar_t game[MAX_PATH];
    if (!findGameDir(game))
        die("没找到游戏目录。请把本安装器放进游戏目录（和 RoadRash95.exe 同级）后再运行。");
    printf("游戏目录: %ls\n\n", game);

    wchar_t exePath[MAX_PATH], enuPath[MAX_PATH], enuBak[MAX_PATH], exeBak[MAX_PATH];
    joinW(exePath, game, L"RoadRash95.exe");
    joinW(enuPath, game, L"TEXT\\ENU.DLL");
    joinW(enuBak, game, L"TEXT\\ENU.DLL.rrzhbak");
    joinW(exeBak, game, L"RoadRash95.exe.rrzhbak");

    if (doUninstall){
        int ok = 0;
        if (fileExistsW(enuBak)){ unsigned char* d=NULL; unsigned int n=0; if(readFileW(enuBak,&d,&n)){ ok|=writeFileW(enuPath,d,n); free(d);} printf("  已还原 TEXT\\ENU.DLL\n"); }
        else printf("  [注意] 没有 ENU.DLL 备份\n");
        if (fileExistsW(exeBak)){ unsigned char* d=NULL; unsigned int n=0; if(readFileW(exeBak,&d,&n)){ ok|=writeFileW(exePath,d,n); free(d);} printf("  已还原 RoadRash95.exe\n"); }
        else printf("  [注意] 没有 EXE 备份\n");
        printf("\n%s\n", ok ? "卸载完成，游戏已恢复原版。" : "卸载未完成。");
        pauseExit(ok ? 0 : 1);
    }

    /* 读自身内嵌包 */
    wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
    unsigned char* me = NULL; unsigned int meLen = 0;
    if (!readFileW(self, &me, &meLen)) die("无法读取安装器自身。");
    if (meLen < TRAILER_LEN + 8) die("安装包损坏（缺少内嵌数据）。");
    const unsigned char* tr = me + meLen - TRAILER_LEN;
    if (rd32(tr) != TRAILER_MAGIC) die("安装包损坏（尾部标记不符）。");
    unsigned int packSize = rd32(tr + 4);
    if (packSize + TRAILER_LEN > meLen) die("安装包损坏（大小异常）。");
    unsigned int packOff = meLen - TRAILER_LEN - packSize;
    unsigned char* pack = me + packOff;
    if (rd32(pack) != PACK_MAGIC) die("安装包损坏（头部标记不符）。");
    unsigned int count = rd32(pack + 4);
    if (8 + count * ENTRY_SIZE > packSize) die("安装包损坏（目录越界）。");

    /* 选择语言 */
    LANGID ui = GetUserDefaultUILanguage();
    const char* sysCode = langFromLangId(ui);
    int defIdx = -1;
    for (unsigned int i = 0; i < count; i++){
        const unsigned char* e = pack + 8 + i * ENTRY_SIZE;
        if (sysCode && !strcmp((const char*)e, sysCode)) { defIdx = (int)i; break; }
    }
    if (sysCode && isOfficial(sysCode)){
        printf("系统语言为 %s，而该语言是【游戏官方自带】的（无需本地化补丁）。\n", sysCode);
        printf("如果你的界面不是该语言：游戏会根据注册表 Language 值加载对应文本，\n");
        printf("官方英语版已被本项目占用为汉化版时，请先运行本安装器 uninstall 还原。\n\n");
        if (!forced) pauseExit(0);
    }

    if (wantCode){
        for (unsigned int i = 0; i < count; i++){
            const unsigned char* e = pack + 8 + i * ENTRY_SIZE;
            if (!_stricmp((const char*)e, wantCode)) { defIdx = (int)i; break; }
        }
    }

    printf("可用语言（共 %u 种；* 为推荐）：\n", count);
    for (unsigned int i = 0; i < count; i++){
        const unsigned char* e = pack + 8 + i * ENTRY_SIZE;
        unsigned int nameOff = rd32(e + 26), nameLen = e[24] | (e[25] << 8);
        unsigned int cp = e[8] | (e[9] << 8);
        printf("  %s%2u) %-28s %-6s cp%u\n", ((int)i == defIdx ? "*" : " "), i + 1,
               (const char*)(pack + nameOff), (const char*)e, cp);
        (void)nameLen;
    }
    printf("\n请输入序号（直接回车 = 推荐项）: ");
    fflush(stdout);
    char line[64]; if (!fgets(line, sizeof(line), stdin)) line[0] = 0;
    int pick = defIdx;
    if (line[0] && line[0] != '\n' && line[0] != '\r'){
        int v = atoi(line);
        if (v >= 1 && v <= (int)count) pick = v - 1;
    }
    if (pick < 0) pick = 0;
    const unsigned char* e = pack + 8 + pick * ENTRY_SIZE;
    const char* code = (const char*)e;
    unsigned int cp = e[8] | (e[9] << 8);
    unsigned char charset = e[10];
    unsigned char faceLen = e[11];
    const char* face = (const char*)(e + 12);
    unsigned int dllOff = rd32(e + 30), dllSize = rd32(e + 34);

    unsigned int sysCp = GetACP();
    printf("\n选择: %s  (cp%u, 字体 %.*s, charset %u)\n", code, cp, faceLen, face, charset);
    if (cp != sysCp){
        printf("  [注意] 系统 ANSI 代码页是 cp%u，与所选语言 cp%u 不一致，\n", sysCp, cp);
        printf("         有可能显示为问号。需要把「非 Unicode 程序语言」改成对应语言。\n");
    }
    printf("\n开始安装...\n");

    /* 备份 */
    if (!fileExistsW(enuBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readFileW(enuPath,&d,&n) || !writeFileW(enuBak,d,n)) die("备份 ENU.DLL 失败。");
        free(d); printf("  已备份 TEXT\\ENU.DLL\n");
    } else printf("  ENU.DLL 备份已存在\n");
    if (!fileExistsW(exeBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readFileW(exePath,&d,&n) || !writeFileW(exeBak,d,n)) die("备份 EXE 失败。");
        free(d); printf("  已备份 RoadRash95.exe\n");
    } else printf("  EXE 备份已存在\n");

    /* 写 DLL */
    if (!writeFileW(enuPath, pack + dllOff, dllSize)) die("写入 TEXT\\ENU.DLL 失败（文件被占用？）");
    printf("  已写入 TEXT\\ENU.DLL (%u 字节)\n", dllSize);

    /* 补丁 EXE */
    unsigned char* exeData = NULL; unsigned int exeLen = 0;
    if (!readFileW(exePath, &exeData, &exeLen)) die("读取 EXE 失败。");
    if (exeLen <= OFF_FACE + FACE_SLOT) die("EXE 大小异常。");
    if (exeData[OFF_CHARSET] != 0x6A) die("字体补丁点校验失败（EXE 版本不符）。");
    exeData[OFF_CHARSET + 1] = charset;
    memset(exeData + OFF_FACE, 0, FACE_SLOT);
    memcpy(exeData + OFF_FACE, face, faceLen > FACE_SLOT ? FACE_SLOT : faceLen);
    if (!writeFileW(exePath, exeData, exeLen)) die("写入 EXE 失败（文件被占用？请关闭游戏与 Steam 后重试）。");
    free(exeData);
    printf("  已应用字体补丁（charset=%u, face=%.*s）\n", charset, faceLen, face);

    printf("\n✔ 安装完成！启动游戏即为 %s 界面。\n", code);
    printf("  还原：把本安装器再运行一次并选择卸载（或命令行加 uninstall）。\n");
    pauseExit(0);
    return 0;
}
