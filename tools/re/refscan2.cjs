
const fs=require('fs');
const b=fs.readFileSync(process.argv[2]);
function u16(o){return b.readUInt16LE(o);} function u32(o){return b.readUInt32LE(o);}
const e_lfanew=u32(0x3c), coff=e_lfanew+4, optSize=u16(coff+16), opt=coff+20;
const numSec=u16(coff+2), secOff=opt+optSize;
const secs=[];for(let i=0;i<numSec;i++){const s=secOff+i*40;secs.push({name:b.toString('ascii',s,s+8).replace(/\0+$/,''),vsize:u32(s+8),vaddr:u32(s+12),rawsize:u32(s+16),rawptr:u32(s+20)});}
const o2rva=off=>{for(const s of secs)if(off>=s.rawptr&&off<s.rawptr+s.rawsize)return s.vaddr+(off-s.rawptr);return null;};
const rva2o=rva=>{for(const s of secs)if(rva>=s.vaddr&&rva<s.vaddr+Math.max(s.vsize,s.rawsize))return s.rawptr+(rva-s.vaddr);return null;};
const IMG=0x400000;
const targets = [['Text\\ENU.dll',0x104f54],['Text\\FRA.dll',0x104f64],['Text\\DEU.dll',0x104f74],['Text\\ITA.dll',0x104f84],['Text\\ESP.dll',0x104f94],['Language',0x104f14]];
for(const [name,fo] of targets){
  const rva=o2rva(fo);
  const va=IMG+rva;
  const needle=Buffer.alloc(4); needle.writeUInt32LE(va>>>0,0);
  const hits=[]; let i=0;
  while((i=b.indexOf(needle,i))!==-1){ hits.push(i); i++; }
  console.log('\n'+name.padEnd(16),'RVA 0x'+rva.toString(16),'VA 0x'+va.toString(16),'refs:',hits.length);
  for(const h of hits.slice(0,6)){
    console.log('   at file 0x'+h.toString(16)+' (rva 0x'+(o2rva(h)||0).toString(16)+') ctx:', [...b.subarray(h-12,h+16)].map(x=>x.toString(16).padStart(2,'0')).join(' '));
  }
}
