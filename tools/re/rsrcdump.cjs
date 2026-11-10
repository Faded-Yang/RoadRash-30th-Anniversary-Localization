
const fs=require('fs');
const f = process.argv[2];
const b = fs.readFileSync(f);
function u16(o){return b.readUInt16LE(o);} function u32(o){return b.readUInt32LE(o);}
const e_lfanew=u32(0x3c);
const coff=e_lfanew+4, optSize=u16(coff+16), opt=coff+20, magic=u16(opt);
const ddOff=opt+(magic===0x20b?112:96);
const numDirs=u32(ddOff-4);
const dirs=[];for(let i=0;i<Math.min(numDirs,16);i++)dirs.push({va:u32(ddOff+i*8),sz:u32(ddOff+i*8+4)});
const numSec=u16(coff+2), secOff=opt+optSize;
const secs=[];for(let i=0;i<numSec;i++){const s=secOff+i*40;secs.push({vsize:u32(s+8),vaddr:u32(s+12),rawsize:u32(s+16),rawptr:u32(s+20)});}
const r2o=rva=>{for(const s of secs)if(rva>=s.vaddr&&rva<s.vaddr+Math.max(s.vsize,s.rawsize))return s.rawptr+(rva-s.vaddr);return null;};
const rs=dirs[2];
console.log('rsrc dir va=0x'+rs.va.toString(16),'sz',rs.sz,'raw off 0x'+(r2o(rs.va)||0).toString(16));
const rbase=r2o(rs.va);
const hex=(off,n)=>{const a=[];for(let i=0;i<n;i++)a.push(b[off+i].toString(16).padStart(2,'0'));return a.join(' ');};
console.log('rsrc head:', hex(rbase, 64*4));
const dirAt=off=>{const p=rbase+off;return{nn:u16(p+12),ni:u16(p+14),p};};
const top=dirAt(0);
console.log('top entries named/id', top.nn, top.ni);
for(let i=0;i<top.nn+top.ni;i++){
  const e=top.p+16+i*8;
  console.log(' entry', i, 'nameOrId=0x'+u32(e).toString(16), 'off=0x'+u32(e+4).toString(16));
}
// dump first RT_STRING 6 type dir
for(let i=0;i<top.nn+top.ni;i++){
  const e=top.p+16+i*8;
  if(u32(e)!==6) continue;
  const d1=dirAt(u32(e+4)&0x7fffffff);
  console.log('RT_STRING dir entries', d1.nn, d1.ni);
  for(let j=0;j<Math.min(d1.nn+d1.ni,3);j++){
    const e2=d1.p+16+j*8;
    const id=u32(e2), off2=u32(e2+4);
    const d2=dirAt(off2&0x7fffffff);
    console.log('  sub id', id, 'lang entries', d2.nn, d2.ni);
    for(let k=0;k<d2.nn+d2.ni;k++){
      const e3=d2.p+16+k*8;
      console.log('   lang=0x'+u32(e3).toString(16),'dataRva=0x'+u32(e3+4).toString(16),'size',u32(e3+8));
      const o=r2o(u32(e3+4));
      console.log('   bytes@',o, hex(o, 48));
    }
    break;
  }
  break;
}
// dump .rsrc mid to eyeball whether text-like content exists
console.log('--- search UTF16 ascii text runs in .rsrc ---');
const start=rbase, end=rbase+rs.sz;
let runs=[]; let cur='';
for(let i=start;i<end-1;i+=2){
  const c=b[i]; const hi=b[i+1];
  if(hi===0 && c>=0x20 && c<0x7f){ cur+=String.fromCharCode(c); }
  else { if(cur.length>=4) runs.push(cur); cur=''; }
}
if(cur.length>=4) runs.push(cur);
console.log('utf16le ascii runs found:', runs.length);
console.log(runs.slice(0,60).join(' | '));
