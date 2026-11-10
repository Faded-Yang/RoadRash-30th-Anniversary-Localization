
import pefile, capstone, sys
path = sys.argv[1]
start = int(sys.argv[2], 0); length = int(sys.argv[3], 0)
pe = pefile.PE(path, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
data = pe.__data__
off = pe.get_offset_from_rva(start)
code = data[off:off+length]
print('==== RVA 0x%x (file 0x%x) ====' % (start, off))
for i in md.disasm(code, ib+start):
    print('  0x%08x  %-20s %s %s' % (i.address, i.bytes.hex()[:20], i.mnemonic, i.op_str))
