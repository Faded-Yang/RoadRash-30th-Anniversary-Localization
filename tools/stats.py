
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
en = {int(k):v for k,v in json.load(open(sys.argv[1],encoding='utf8')).items()}
zh = {int(k):v for k,v in json.load(open(sys.argv[2],encoding='utf8')).items()}
same = [i for i in en if zh.get(i)==en[i]]
diff = [i for i in en if zh.get(i)!=en[i]]
print('总条数 %d' % len(en))
print('已翻译(与英文不同) %d (%.1f%%)' % (len(diff), 100*len(diff)/len(en)))
print('保留英文 %d' % len(same))
print('英文总字符 %d -> 中文总字符 %d' % (sum(len(v) for v in en.values()), sum(len(zh.get(i,'')) for i in en)))
print('英文字符省下 %.0f%%' % (100*(1-sum(len(zh.get(i,'')) for i in en)/sum(len(v) for v in en.values()))))
