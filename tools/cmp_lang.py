
import pefile, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
base = sys.argv[1]
def extract(path):
    pe = pefile.PE(path, fast_load=False)
    out = {}
    blocks = {}
    if not hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'): return out, blocks
    for er in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if er.id != 6: continue
        for e1 in er.directory.entries:
            for e2 in e1.directory.entries:
                d = pe.get_data(e2.data.struct.OffsetToData, e2.data.struct.Size)
                p=0; arr=[]
                for k in range(16):
                    if p+2>len(d): break
                    ln=int.from_bytes(d[p:p+2],'little'); p+=2
                    if ln>0:
                        s=d[p:p+ln*2].decode('utf-16le','replace'); p+=ln*2
                        arr.append(s); out[(e1.id-1)*16+k]=s
                blocks[e1.id]=(len(d), len(arr))
    return out, blocks
files = ['ENU.DLL','DEU.DLL','FRA.DLL','ESP.DLL','ITA.DLL']
sets = {}
for f in files:
    p=os.path.join(base,f)
    s,bl = extract(p)
    sets[f]=s
    print('%-9s strings=%-5d chars=%-6d blocks=%d ids=%d..%d' % (f, len(s), sum(len(v) for v in s.values()), len(bl), min(bl), max(bl)))
ref = sets['ENU.DLL']
print()
print('ID set equality vs ENU:', {f: (set(sets[f].keys())==set(ref.keys())) for f in files})
# compare e.g. a few
print()
print('sample DEU strings:')
for k in sorted(sets['DEU.DLL'])[:6]: print('  ',k,repr(sets['DEU.DLL'][k])[:150])
print()
print('#### non-PE files headers ####')
for f in ['BADLOC.DLL','FUTB.DLL','FUTD.DLL','FUTR.DLL']:
    p=os.path.join(base,f)
    b=open(p,'rb').read(64)
    print('%-12s %s  ascii=%r' % (f, b[:16].hex(), b[:16]))
