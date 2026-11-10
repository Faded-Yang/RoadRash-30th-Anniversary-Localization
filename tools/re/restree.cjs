
const fs=require('fs');
const f=process.argv[2];
const b=fs.readFileSync(f);
function u16(o){return b.readUInt16LE(o);} function u32(o){return b.readUInt32LE(o);}
const e_lfanew=u32(0x3c), coff=e_lfanew+4, optSize=u16(coff+16), opt=coff+20, magic=u16(opt);
const ddOff=opt+(magic===0x20b?112:96);
const numDirs=u32(ddOff-4);
const dirs=[];for(let i=0;i<Math.min(numDirs,16);i++)dirs.push({va:u32(ddOff+i*8),sz:u32(ddOff+i*8+4)});
const numSec=u16(coff+2), secOff=opt+optSize;
const secs=[];for(let i=0;i<numSec;i++){const s=secOff+i*40;secs.push({vsize:u32(s+8),vaddr:u32(s+12),rawsize:u32(s+16),rawptr:u32(s+20)});}
const r2o=rva=>{for(const s of secs)if(rva>=s.vaddr&&rva<s.vaddr+Math.max(s.vsize,s.rawsize))return s.rawptr+(rva-s.vaddr);return null;};
const rs=dirs[2]; const rbase=r2o(rs.va);

function readName(nameField){
  const p = rbase + (nameField & 0x7fffffff);
  const len = u16(p);
  return b.toString('utf16le', p+2, p+2+len*2);
}
function walk(dirOff, depth, path){
  const p = rbase + dirOff;
  const named=u16(p+12), ids=u16(p+14);
  const out=[];
  for(let i=0;i<named+ids;i++){
    const e=p+16+i*8;
    const nameOrId=u32(e), childOff=u32(e+4);
    let label;
    if(nameOrId & 0x80000000) label = readName(nameOrId);
    else label = '#'+nameOrId;
    const isDir = !!(childOff & 0x80000000);
    const cOff = childOff & 0x7fffffff;
    if(isDir){ out.push({label, dir:true, children: walk(cOff, depth+1, path.concat(label))}); }
    else {
      const leaf = rbase + cOff;
      const dataRva=u32(leaf), size=u32(leaf+4), cp=u32(leaf+8);
      out.push({label, dir:false, dataRva, size, cp, dataOff: r2o(dataRva)});
    }
  }
  return out;
}
const tree = walk(0,0,[]);
function show(nodes, ind){
  for(const n of nodes){
    if(n.dir){ console.log(ind+'DIR ['+n.label+'] '+n.children.length); show(n.children, ind+'  '); }
    else console.log(ind+'DATA ['+n.label+'] rva=0x'+(n.dataRva||0).toString(16)+' size='+n.size+' cp='+n.cp+' off='+n.dataOff);
  }
}
console.log('=== TOP ===');
show(tree,'');
