
const fs=require('fs');
const f=process.argv[2];
const b=fs.readFileSync(f);
function asciiStrings(min){ const out=[]; let cur='', start=0;
  for(let i=0;i<b.length;i++){ const c=b[i];
    if(c>=0x20 && c<0x7f){ if(!cur) start=i; cur+=String.fromCharCode(c); }
    else { if(cur.length>=min) out.push({off:start, s:cur}); cur=''; } }
  if(cur.length>=min) out.push({off:start,s:cur});
  return out;
}
function utf16Strings(min){ const out=[]; let cur='', start=0;
  for(let i=0;i+1<b.length;i+=2){ const c=b[i]|(b[i+1]<<8);
    if((c>=0x20&&c<0x7f)||(c>=0x4e00&&c<=0x9fff)){ if(!cur) start=i; cur+=String.fromCharCode(c); }
    else { if(cur.length>=min) out.push({off:start,s:cur}); cur=''; } }
  return out;
}
const a=asciiStrings(4);
const re=/(TEXT|\.DLL|\.dll|ENU|DEU|FRA|ESP|ITA|lang|Lang|LANG|\.INI|\.CFG|registry|Registry|Software|Electronic|RoadRash|Road Rash|install|Install|CHS|JPN|KOR|\.RSC|\.RRA)/;
console.log('--- ASCII strings matching keywords ---');
for(const x of a){ if(re.test(x.s)) console.log('0x'+x.off.toString(16), JSON.stringify(x.s)); }
