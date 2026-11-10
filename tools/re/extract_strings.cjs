
const fs=require('fs');
const f=process.argv[2], out=process.argv[3];
const b=fs.readFileSync(f);
function u16(o){return b.readUInt16LE(o);} function u32(o){return b.readUInt32LE(o);}
const e_lfanew=u32(0x3c), coff=e_lfanew+4, optSize=u16(coff+16), opt=coff+20, magic=u16(opt);
const ddOff=opt+(magic===0x20b?112:96);
const numDirs=u32(ddOff-4);
const dirs=[];for(let i=0;i<Math.min(numDirs,16);i++)dirs.push({va:u32(ddOff+i*8),sz:u32(ddOff+i*8+4)});
const numSec=u16(coff+2), secOff=opt+optSize;
const secs=[];for(let i=0;i<numSec;i++){const s=secOff+i*40;secs.push({vsize:u32(s+8),vaddr:u32(s+12),rawsize:u32(s+16),rawptr:u32(s+20)});}
const r2o=rva=>{for(const s of secs)if(rva>=s.vaddr&&rva<s.vaddr+Math.max(s.vsize,s.rawsize))return s.rawptr+(rva-s.vaddr);return null;};
const rbase=r2o(dirs[2].va);

function dirEntries(off){const p=rbase+off;const named=u16(p+12),ids=u16(p+14);const out=[];for(let i=0;i<named+ids;i++){const e=p+16+i*8;out.push({nameOrId:u32(e),child:u32(e+4)});}return out;}

const blocks=[];
for(const t of dirEntries(0)){
  if((t.nameOrId & 0x7fffffff)!==6) continue;
  const sub = t.child & 0x7fffffff;
  for(const blk of dirEntries(sub)){
    if(blk.nameOrId & 0x80000000) continue;
    const bid = blk.nameOrId;
    for(const lang of dirEntries(blk.child & 0x7fffffff)){
      const leaf = rbase + (lang.child & 0x7fffffff);
      const dataOff = r2o(u32(leaf)); const size = u32(leaf+4);
      blocks.push({bid, lang: lang.nameOrId, dataOff, size});
    }
  }
}
blocks.sort((a,b)=>a.bid-b.bid);
console.log('blocks:', blocks.length, 'ids:', blocks.map(x=>x.bid).join(','));
const strings = {};
let totalChars=0;
for(const blk of blocks){
  let p=blk.dataOff; const end=blk.dataOff+blk.size;
  for(let k=0;k<16;k++){
    if(p+2>end){ break; }
    const len=u16(p); p+=2;
    if(len===0){ continue; }
    const s=b.toString('utf16le',p,p+len*2); p+=len*2;
    strings[(blk.bid-1)*16+k] = s;
    totalChars += len;
  }
}
const keys=Object.keys(strings).map(Number).sort((a,b)=>a-b);
console.log('non-empty strings:', keys.length, 'total chars:', totalChars);
console.log('id range', keys[0], '..', keys[keys.length-1]);
const gaps=[]; for(let i=keys[0];i<=keys[keys.length-1];i++) if(!(i in strings)) gaps.push(i);
console.log('missing ids count:', gaps.length);
console.log('--- first 50 ---');
for(const k of keys.slice(0,50)) console.log(k, JSON.stringify(strings[k]));
fs.writeFileSync(out, JSON.stringify(strings,null,1),'utf8');
console.log('saved', out);
