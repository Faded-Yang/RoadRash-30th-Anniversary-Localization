
import pefile, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
tdir = sys.argv[1]; outdir = sys.argv[2]
def extract(path):
    pe = pefile.PE(path, fast_load=False)
    out = {}
    for er in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if er.id != 6: continue
        for e1 in er.directory.entries:
            for e2 in e1.directory.entries:
                d = pe.get_data(e2.data.struct.OffsetToData, e2.data.struct.Size)
                p=0
                for k in range(16):
                    if p+2>len(d): break
                    ln=int.from_bytes(d[p:p+2],'little'); p+=2
                    if ln>0:
                        s=d[p:p+ln*2].decode('utf-16le','replace'); p+=ln*2
                        out[(e1.id-1)*16+k]=s
    return out
for f in ['ENU.DLL','DEU.DLL','FRA.DLL','ESP.DLL','ITA.DLL']:
    p = os.path.join(tdir,f)
    s = extract(p)
    name = f.split('.')[0]
    json.dump({str(k):v for k,v in s.items()}, open(os.path.join(outdir,name+'.json'),'w',encoding='utf8'), ensure_ascii=False, indent=0)
    print(name, len(s), 'strings, ids', min(s), '..', max(s))
