// Road Rash 30th Anniversary - per-language localization installer
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PACK_MAGIC    0x314B505A
#define TRAILER_MAGIC 0x314C5252
#define TRAILER_LEN   16
#define HDR_SIZE      48

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

static const unsigned CALL_RVA[6] = {0x3fef5,0x3ffb6,0x4000a,0x4034e,0x403b9,0x403f2};
static const unsigned CALL_OFF[6] = {0x3f2f5,0x3f3b6,0x3f40a,0x3f74e,0x3f7b9,0x3f7f2};
static const unsigned char LSA_CALL[6] = {0xFF,0x15,0x88,0xC7,0x61,0x00};

enum { M_TITLE=0, M_GAMEDIR, M_NOTFOUND, M_BKDLL, M_BKEXE, M_BKEXIST, M_WRDLL, M_PATCH,
       M_DONE, M_UNINST, M_R_DLL, M_R_EXE, M_NOBK, M_UNINSTD, M_ENTER, M_ADMIN, M_ERR, M_FAIL, M_COUNT };

static const char* M[M_COUNT];

static unsigned rd32(const unsigned char* p){ return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24); }
static void wr32(unsigned char* p, unsigned v){ p[0]=(unsigned char)v; p[1]=(unsigned char)(v>>8); p[2]=(unsigned char)(v>>16); p[3]=(unsigned char)(v>>24); }

static int isElevated(void){
    BOOL a = FALSE; PSID sid = NULL; SID_IDENTIFIER_AUTHORITY nt = { {0,0,0,0,0,5} };
    if (AllocateAndInitializeSid(&nt,2,SECURITY_BUILTIN_DOMAIN_RID,DOMAIN_ALIAS_RID_ADMINS,0,0,0,0,0,0,&sid)){
        CheckTokenMembership(NULL, sid, &a); FreeSid(sid);
    }
    return a;
}
static int existsW(const wchar_t* p){ return GetFileAttributesW(p) != INVALID_FILE_ATTRIBUTES; }
static int readW(const wchar_t* p, unsigned char** o, unsigned int* n){
    HANDLE h = CreateFileW(p, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    LARGE_INTEGER s; GetFileSizeEx(h,&s); *n = (unsigned int)s.QuadPart;
    *o = (unsigned char*)malloc(*n ? *n : 1); DWORD got = 0;
    if (!ReadFile(h,*o,*n,&got,NULL) || got != *n){ CloseHandle(h); free(*o); return 0; }
    CloseHandle(h); return 1;
}
static int writeW(const wchar_t* p, const unsigned char* d, unsigned int n){
    SetFileAttributesW(p, FILE_ATTRIBUTE_NORMAL);
    HANDLE h = CreateFileW(p, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    DWORD put = 0; int ok = WriteFile(h,d,n,&put,NULL) && put == n;
    CloseHandle(h); return ok;
}
static int patchW(const wchar_t* p, const unsigned char* d, unsigned int n){
    SetFileAttributesW(p, FILE_ATTRIBUTE_NORMAL);
    HANDLE h = CreateFileW(p, GENERIC_WRITE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return 0;
    DWORD put = 0; int ok = WriteFile(h,d,n,&put,NULL) && put == n;
    if (ok) SetEndOfFile(h);
    CloseHandle(h); return ok;
}
static void joinW(wchar_t* dst, const wchar_t* a, const wchar_t* b){
    wcscpy(dst,a); size_t n = wcslen(dst);
    if (n && dst[n-1] != L'\\'){ dst[n++] = L'\\'; dst[n] = 0; }
    wcscat(dst,b);
}
static void bye(int code){
    printf("\n%s\n", M[M_ENTER]); fflush(stdout); getchar(); exit(code);
}
static void die(const char* m){ printf("\n%s: %s\n", M[M_ERR], m); bye(1); }
static void u8(const wchar_t* w, char* out, int n){
    WideCharToMultiByte(CP_UTF8, 0, w, -1, out, n, NULL, NULL);
}

static int applyPatches(const wchar_t* exePath, unsigned char charset, const char* face,
                        unsigned cp, const unsigned char* thunk, unsigned thunkLen){
    unsigned char* d = NULL; unsigned int n = 0;
    if (!readW(exePath, &d, &n)) return 0;
    if (n < 0x120000){ free(d); return 0; }
    int ok = 1;
    if (d[OFF_CHARSET] == 0x6A) d[OFF_CHARSET+1] = charset; else ok = 0;
    memset(d + OFF_FACE, 0, FACE_SLOT);
    { size_t fl = strlen(face); memcpy(d + OFF_FACE, face, fl > FACE_SLOT ? FACE_SLOT : fl); }
    d[OFF_DLLCHAR] &= (unsigned char)~0x40;
    { unsigned v = rd32(d + OFF_TEXTCHARS); wr32(d + OFF_TEXTCHARS, v | 0x80000000u); }
    memset(d + CAVE_OFF, 0xCC, BLOB_SIZE);
    memcpy(d + CAVE_OFF, thunk, thunkLen > 0xE0 ? 0xE0 : thunkLen);
    memset(d + CAVE_OFF + OFF_BUF, 0, 0x200);
    memcpy(d + CAVE_OFF + OFF_SUSER, "user32.dll", 11);
    memcpy(d + CAVE_OFF + OFF_SLSW, "LoadStringW", 12);
    wr32(d + CAVE_OFF + OFF_PLSW, 0);
    wr32(d + CAVE_OFF + OFF_CP, cp);
    for (int i = 0; i < 6; i++){
        unsigned char* p = d + CALL_OFF[i];
        if (memcmp(p, LSA_CALL, 6) == 0){
            int rel = (int)(CAVE_VA - (IMG_BASE + CALL_RVA[i] + 5));
            p[0] = 0xE8; wr32(p+1, (unsigned)rel); p[5] = 0x90;
        } else if (p[0] != 0xE8) ok = 0;
    }
    if (ok) ok = patchW(exePath, d, n);
    free(d);
    return ok;
}

int main(int argc, char** argv){
    SetConsoleOutputCP(65001);
    printf("\n");

    int uninstall = 0;
    for (int i = 1; i < argc; i++)
        if (!_stricmp(argv[i],"uninstall") || !_stricmp(argv[i],"-u")) uninstall = 1;

    if (!isElevated()){
        wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
        wchar_t params[1024] = L"";
        for (int i = 1; i < argc; i++){ wcscat(params,L"\""); wchar_t w[256];
            MultiByteToWideChar(CP_ACP,0,argv[i],-1,w,256); wcscat(params,w); wcscat(params,L"\" "); }
        HINSTANCE r = ShellExecuteW(NULL, L"runas", self, params, NULL, SW_SHOWNORMAL);
        if ((INT_PTR)r > 32) return 0;
        printf("管理员权限获取失败。\n"); getchar(); return 1;
    }

    wchar_t game[MAX_PATH]; GetModuleFileNameW(NULL, game, MAX_PATH);
    { wchar_t* s = wcsrchr(game, L'\\'); if (s) *s = 0; }

    /* 读取内嵌包 */
    wchar_t self[MAX_PATH]; GetModuleFileNameW(NULL, self, MAX_PATH);
    unsigned char* me = NULL; unsigned int meLen = 0;
    if (!readW(self, &me, &meLen)) { printf("read self failed\n"); getchar(); return 1; }
    if (meLen < TRAILER_LEN + HDR_SIZE) { printf("package corrupt\n"); getchar(); return 1; }
    const unsigned char* tr = me + meLen - TRAILER_LEN;
    unsigned int packSize = rd32(tr + 4);
    unsigned char* pack = me + meLen - TRAILER_LEN - packSize;

    unsigned msgCount = rd32(pack + 4);
    unsigned thunkOff = rd32(pack + 8), thunkLen = rd32(pack + 12);
    unsigned dllOff = rd32(pack + 16), dllSize = rd32(pack + 20);
    unsigned msgOff = rd32(pack + 28);
    unsigned cp = pack[32] | (pack[33] << 8);
    unsigned char charset = pack[34];
    unsigned char faceLen = pack[35];
    char face[16]; memcpy(face, pack + 36, faceLen > 12 ? 12 : faceLen); face[faceLen > 12 ? 12 : faceLen] = 0;
    if (msgCount > M_COUNT) msgCount = M_COUNT;
    for (unsigned i = 0; i < msgCount; i++) M[i] = (const char*)(pack + rd32(pack + msgOff + i*4));
    while (msgCount < M_COUNT) M[msgCount++] = "";

    printf("%s\n", M[M_TITLE]);
    printf("==================================================\n\n");

    wchar_t exePath[MAX_PATH], enuPath[MAX_PATH], enuBak[MAX_PATH], exeBak[MAX_PATH];
    joinW(exePath, game, L"RoadRash95.exe");
    joinW(enuPath, game, L"TEXT\\ENU.DLL");
    joinW(enuBak, game, L"TEXT\\ENU.DLL.rrzhbak");
    joinW(exeBak, game, L"RoadRash95.exe.rrzhbak");

    if (!existsW(exePath)){
        { char b[MAX_PATH*4]; u8(game, b, sizeof b); printf("%s\n", b); }
        printf("\n%s\n", M[M_NOTFOUND]);
        bye(1);
    }
    { char b[MAX_PATH*4]; u8(game, b, sizeof b); printf("%s %s\n\n", M[M_GAMEDIR], b); }

    if (uninstall){
        int ok = 0;
        if (existsW(enuBak)){ unsigned char* d=NULL; unsigned int n=0;
            if (readW(enuBak,&d,&n)){ ok |= patchW(enuPath,d,n); free(d);} printf("[OK] %s\n", M[M_R_DLL]); }
        else printf("[--] %s\n", M[M_NOBK]);
        if (existsW(exeBak)){ unsigned char* d=NULL; unsigned int n=0;
            if (readW(exeBak,&d,&n)){ ok |= patchW(exePath,d,n); free(d);} printf("[OK] %s\n", M[M_R_EXE]); }
        else printf("[--] %s\n", M[M_NOBK]);
        printf("\n%s\n", ok ? M[M_UNINSTD] : M[M_NOBK]);
        bye(ok ? 0 : 1);
    }

    if (!existsW(enuBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readW(enuPath,&d,&n) || !writeW(enuBak,d,n)) die("backup ENU.DLL failed");
        free(d); printf("[OK] %s\n", M[M_BKDLL]);
    } else printf("[--] %s\n", M[M_BKEXIST]);
    if (!existsW(exeBak)){
        unsigned char* d=NULL; unsigned int n=0;
        if (!readW(exePath,&d,&n) || !writeW(exeBak,d,n)) die("backup EXE failed");
        free(d); printf("[OK] %s\n", M[M_BKEXE]);
    } else printf("[--] %s\n", M[M_BKEXIST]);

    if (!writeW(enuPath, pack + dllOff, dllSize)) die("write TEXT\\ENU.DLL failed (file in use?)");
    printf("[OK] %s (%u bytes)\n", M[M_WRDLL], dllSize);

    if (!applyPatches(exePath, charset, face, cp, pack + thunkOff, thunkLen)) die(M[M_FAIL]);
    printf("[OK] %s\n", M[M_PATCH]);

    printf("\n%s\n", M[M_DONE]);
    bye(0);
    return 0;
}
