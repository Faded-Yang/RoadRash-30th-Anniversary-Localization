
const fs = require('fs');
const path = require('path');

function u16(b,o){return b.readUInt16LE(o);} 
function u32(b,o){return b.readUInt32LE(o);}

function parsePE(file){
  const b = fs.readFileSync(file);
  const out = {file, size:b.length};
  if (b.toString('ascii',0,2) !== 'MZ') { out.error='not MZ'; return out; }
  const e_lfanew = u32(b,0x3c);
  if (b.toString('ascii',e_lfanew,e_lfanew+4) !== 'PE\0\0'){ out.error='no PE sig @'+e_lfanew; return out; }
  const coff = e_lfanew+4;
  const machine = u16(b,coff);
  const numSections = u16(b,coff+2);
  const optSize = u16(b,coff+16);
  const chars = u16(b,coff+18);
  const opt = coff+20;
  const magic = u16(b,opt);
  out.machine = machine===0x14c?'x86':(machine===0x8664?'x64':('0x'+machine.toString(16)));
  out.magic = magic===0x10b?'PE32':(magic===0x20b?'PE32+':'0x'+magic.toString(16));
  out.characteristics = '0x'+chars.toString(16);
  out.numSections = numSections;
  const ddOff = opt + (magic===0x20b?112:96);
  const numDirs = u32(b, ddOff-4);
  out.numDirs = numDirs;
  const dirs = [];
  for(let i=0;i<Math.min(numDirs,16);i++){
    const va = u32(b,ddOff+i*8), sz = u32(b,ddOff+i*8+4);
    dirs.push({i,va,sz});
  }
  out.dirs = dirs;
  out.imageBase = magic===0x20b ? Number(b.readBigUInt64LE(opt+24)) : u32(b,opt+28);
  // sections
  const secOff = opt + optSize;
  const secs=[];
  for(let i=0;i<numSections;i++){
    const s = secOff+i*40;
    const name = b.toString('ascii',s,s+8).replace(/\0+$/,'');
    const vsize=u32(b,s+8), vaddr=u32(b,s+12), rawsize=u32(b,s+16), rawptr=u32(b,s+20);
    const ch=u32(b,s+36);
    secs.push({name,vaddr,vsize,rawptr,rawsize,ch,exec:!!(ch&0x20000000),read:!!(ch&0x40000000),write:!!(ch&0x80000000)});
  }
  out.sections = secs;
  const rva2off = (rva)=>{ for(const s of secs){ if(rva>=s.vaddr && rva < s.vaddr+Math.max(s.vsize,s.rawsize)) return s.rawptr + (rva-s.vaddr); } return null; };
  out.rva2off = rva2off;
  // exports
  const exp = dirs[0];
  if (exp.sz>0){
    const eo = rva2off(exp.va);
    if(eo!=null){
      const dllNameRva = u32(b,eo+12);
      const nFuncs=u32(b,eo+20), nNames=u32(b,eo+24);
      const aFuncs=rva2off(u32(b,eo+28)), aNames=rva2off(u32(b,eo+32)), aOrds=rva2off(u32(b,eo+36));
      out.exportDllName = dllNameRva? b.toString('ascii',rva2off(dllNameRva), rva2off(dllNameRva)+60).split('\0')[0] : '';
      const names=[];
      for(let i=0;i<nNames;i++){
        const nr = u32(b, aNames+i*4);
        const no = rva2off(nr);
        names.push(b.toString('ascii',no,no+120).split('\0')[0]);
      }
      out.exportNames = names;
      out.numFuncs = nFuncs;
      // ordinals
      out.funcOrdinals = aOrds!=null? Array.from({length:Math.min(nFuncs,400)},(_,i)=>u16(b,aOrds+i*2)) : [];
      out.funcRvas = aFuncs!=null? Array.from({length:Math.min(nFuncs,400)},(_,i)=>u32(b,aFuncs+i*4)) : [];
    }
  }
  // imports
  const imp = dirs[1];
  if (imp.sz>0){
    let io = rva2off(imp.va);
    const imports=[];
    for(let k=0;k<64 && io!=null;k++){
      const nameRva = u32(b,io+12);
      if(nameRva===0) break;
      const no = rva2off(nameRva);
      const dll = b.toString('ascii',no,no+80).split('\0')[0];
      const oftRva = u32(b,io+0);
      const ftRva = u32(b,io+16);
      const entries=[];
      let t = rva2off(oftRva||ftRva);
      for(let j=0;j<3000 && t!=null;j++){
        const v = u32(b,t);
        if(v===0) break;
        if(v & 0x80000000){ entries.push('#'+(v&0xffff)); }
        else { const ho=rva2off(v); entries.push(b.toString('ascii',ho+2,ho+2+80).split('\0')[0]); }
        t+=4;
      }
      imports.push({dll, funcs:entries});
      io+=20;
    }
    out.imports = imports;
  }
  // resources
  const rs = dirs[2];
  out.resourceTypes = [];
  if (rs.sz>0){
    const base = rva2off(rs.va);
    if(base!=null){
      const nNamed=u16(b,base+12), nId=u16(b,base+14);
      for(let i=0;i<nNamed+nId;i++){
        const e=base+16+i*8;
        const nameOrId=u32(b,e);
        const off=u32(b,e+4);
        let typeName;
        if(nameOrId & 0x80000000){ const so=base+(nameOrId&0x7fffffff); const len=u16(b,so); typeName=b.toString('utf16le',so+2,so+2+len*2); }
        else typeName = '#'+nameOrId;
        const dirOff = base + (off & 0x7fffffff);
        const nn=u16(b,dirOff+12), ni=u16(b,dirOff+14);
        out.resourceTypes.push({type:typeName, count:nn+ni});
      }
    }
  }
  return out;
}

const files = process.argv.slice(2);
for(const f of files){
  const info = parsePE(f);
  console.log('='.repeat(70));
  console.log('FILE:', info.file, 'size', info.size);
  if(info.error){ console.log('ERROR', info.error); continue; }
  console.log('machine', info.machine, 'magic', info.magic, 'imageBase', '0x'+info.imageBase.toString(16));
  console.log('char', info.characteristics, 'dll?', !!(parseInt(info.characteristics,16)&0x2000));
  console.log('sections:');
  for(const s of info.sections) console.log('  ', s.name.padEnd(10), 'vaddr=0x'+s.vaddr.toString(16), 'vsize='+s.vsize, 'raw=0x'+s.rawptr.toString(16), s.rawsize, s.exec?'EXEC':'', s.read?'R':'', s.write?'W':'');
  if(info.exportDllName!==undefined){
    console.log('exports dllName:', JSON.stringify(info.exportDllName), 'nFuncs', info.numFuncs, 'nNames', (info.exportNames||[]).length);
    console.log('  names:', (info.exportNames||[]).slice(0,80).join(', '));
    console.log('  ordinals:', (info.funcOrdinals||[]).slice(0,40).join(','));
    console.log('  rvas:', (info.funcRvas||[]).slice(0,40).map(x=>'0x'+x.toString(16)).join(','));
  }
  if(info.imports){
    console.log('imports:', info.imports.map(i=>i.dll+'('+i.funcs.length+')').join(' '));
    for(const i of info.imports) console.log('   ', i.dll, ':', i.funcs.slice(0,60).join(', '));
  }
  if(info.resourceTypes && info.resourceTypes.length) console.log('resources:', info.resourceTypes.map(r=>r.type+'='+r.count).join(' '));
}
