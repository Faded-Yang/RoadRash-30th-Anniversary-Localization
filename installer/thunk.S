.code32
.text
.globl rr_load
/* int __stdcall rr_load(void* h, unsigned id, char* buf, int cch)
   8(%ebp)=h  12(%ebp)=id  16(%ebp)=buf  20(%ebp)=cch   返回后 ret 16
   注意：0x61c440 / 0x61c324 / 0x61c270 是 IAT *槽地址*，须 call *[槽] */
rr_load:
    pushl %ebp
    movl %esp, %ebp
    pushl %esi
    pushl %edi
    pushl %ebx
    /* ---- 惰性解析 LoadStringW ---- */
    movl 0x4060c8, %eax
    testl %eax, %eax
    jne 1f
    pushl $0x406300              /* "user32.dll" */
    call *0x61c440               /* GetModuleHandleA */
    pushl $0x406310              /* "LoadStringW" */
    pushl %eax
    call *0x61c324               /* GetProcAddress */
    movl %eax, 0x4060c8
    testl %eax, %eax
    je 9f
1:
    /* ---- LoadStringW(h, id, bufw, 256) ---- */
    pushl $256
    pushl $0x406100
    pushl 12(%ebp)
    pushl 8(%ebp)
    call *0x4060c8
    testl %eax, %eax
    jle 9f
    /* ---- WideCharToMultiByte(cp,0,bufw,-1,buf,cch,0,0) ---- */
    pushl $0
    pushl $0
    pushl 20(%ebp)
    pushl 16(%ebp)
    pushl $-1
    pushl $0x406100
    pushl $0
    pushl 0x4060cc
    call *0x61c270               /* WideCharToMultiByte */
    testl %eax, %eax
    jle 9f
    decl %eax
    jmp 2f
9:
    xorl %eax, %eax
2:
    popl %ebx
    popl %edi
    popl %esi
    popl %ebp
    ret $16
