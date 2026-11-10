.code32
.text
.globl rr_load
/* int __stdcall rr_load(void* h, unsigned id, char* buf, int cch)
   8(%ebp)=h 12(%ebp)=id 16(%ebp)=buf 20(%ebp)=cch
   0x61c440/0x61c324/0x61c270 是 IAT 槽地址；0x406000 起是本桩的私有数据区 */
rr_load:
    pushl %ebp
    movl %esp, %ebp
    pushl %esi
    pushl %edi
    pushl %ebx
    /* 惰性解析 LoadStringW */
    movl 0x4060c8, %eax
    testl %eax, %eax
    jne 1f
    pushl $0x406300
    call *0x61c440
    pushl $0x406310
    pushl %eax
    call *0x61c324
    movl %eax, 0x4060c8
    testl %eax, %eax
    je 9f
1:
    /* LoadStringW(h, id, bufw, 256) */
    pushl $256
    pushl $0x406100
    pushl 12(%ebp)
    pushl 8(%ebp)
    call *0x4060c8
    testl %eax, %eax
    jle 9f
    /* WideCharToMultiByte(cp,0,bufw,-1,buf,cch,0,0) */
    pushl $0
    pushl $0
    pushl 20(%ebp)
    pushl 16(%ebp)
    pushl $-1
    pushl $0x406100
    pushl $0
    pushl 0x4060cc
    call *0x61c270
    testl %eax, %eax
    jg 3f
    /* 缓冲区不够：逐字符转换并按 cch 截断 */
    xorl %esi, %esi
    xorl %edi, %edi
    movl 20(%ebp), %ebx
    decl %ebx
    js 9f
2:
    movzwl 0x406100(,%esi,2), %eax
    testl %eax, %eax
    je 4f
    movl %ebx, %ecx
    subl %edi, %ecx
    jle 4f
    pushl $0
    pushl $0
    pushl %ecx
    movl 16(%ebp), %edx
    addl %edi, %edx
    pushl %edx
    pushl $1
    leal 0x406100(,%esi,2), %edx
    pushl %edx
    pushl $0
    pushl 0x4060cc
    call *0x61c270
    testl %eax, %eax
    jle 4f
    addl %eax, %edi
    incl %esi
    jmp 2b
4:
    movl 16(%ebp), %edx
    movb $0, (%edx,%edi)
    movl %edi, %eax
    jmp 5f
3:
    decl %eax
    jmp 5f
9:
    xorl %eax, %eax
5:
    popl %ebx
    popl %edi
    popl %esi
    popl %ebp
    ret $16
