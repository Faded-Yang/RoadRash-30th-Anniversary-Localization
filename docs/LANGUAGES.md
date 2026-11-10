# 支持的语言清单与技术边界

## 为什么不是「所有语言」

这版游戏是 **1996 年的 ANSI 程序**，文本链路是：

```
TEXT\<LANG>.DLL  ──RT_STRING(UTF-16)──▶  LoadStringA  ──按 CP_ACP 转字节──▶  DrawTextA
                                                                              │
                                                          按字体字符集(lfCharSet)解释字节
```

两个环节都受 **Windows ANSI 代码页** 限制：

1. `LoadStringA` 用 **系统 ANSI 代码页 (CP_ACP)** 把 UTF-16 转成字节 —— 代码页外的字符直接变 `?`；
2. `DrawTextA` 用 **字体字符集** 把字节解释回字形 —— 两者必须一致。

所以：**只有 Windows 存在对应 ANSI 代码页的书写系统才可能显示**。
这就是本项目的语言边界，不是实现上的偷懒。

## 支持（63 种，含游戏官方自带 5 种）

| ANSI 代码页 | charset | 字体 | 语言 |
|---|---|---|---|
| 1252 | 0 ANSI | Arial Narrow（原版） | en de fr es it pt nl da sv nb fi is ca eu gl af sq id ms tl sw ht cy ga mt lb |
| 1250 | 238 EastEurope | Arial | pl cs sk hu sl hr ro bs |
| 1251 | 204 Russian | Arial | ru uk bg sr mk be mn kk ky tg |
| 1253 | 161 Greek | Arial | el |
| 1254 | 162 Turkish | Arial | tr az |
| 1255 | 177 Hebrew | Arial | he |
| 1256 | 178 Arabic | Arial | ar fa ur ps sd |
| 1257 | 186 Baltic | Arial | et lv lt |
| 1258 | 163 Vietnamese | Arial | vi |
| 874 | 222 Thai | Tahoma | th |
| 932 | 128 ShiftJIS | MS Gothic | ja |
| 936 | 134 GB2312 | SimHei | zh-CN |
| 949 | 129 Hangul | Gulim | ko |
| 950 | 136 Big5 | MingLiU | zh-TW |

> 同一代码页内的语言可以互相共用系统区域：例如在任意 cp1252 的 Windows 上，
> 德语、葡萄牙语、印尼语……都能正常显示；但中文版必须系统区域 = 中文(CP936)。

## 不支持（Google 翻译支持，但 Windows 无对应 ANSI 代码页）

| 书写系统 | 语言 | 原因 |
|---|---|---|
| 天城文 | hi 印地语、mr 马拉地语、ne 尼泊尔语、sa 梵语 | 无 ANSI 代码页 |
| 孟加拉系 | bn 孟加拉语、as 阿萨姆语 | 同上 |
| 印度诸文 | gu 古吉拉特语、pa 旁遮普语、or 奥里亚语、ta 泰米尔语、te 泰卢固语、kn 卡纳达语、ml 马拉雅拉姆语、si 僧伽罗语 | 同上 |
| 东南亚 | km 高棉语、lo 老挝语、my 缅甸语 | 同上 |
| 高加索/非洲 | ka 格鲁吉亚语、hy 亚美尼亚语、am 阿姆哈拉语、ti 提格里尼亚语 | 同上 |
| 其他 | bo 藏语、dz 宗喀语、chr 切罗基语、iu 因纽特语 | 同上 |

**要突破这个限制**，只能改游戏代码：把 `LoadStringA` 换成 `LoadStringW` + `WideCharToMultiByte`，
并把 `DrawTextA` 换成 `DrawTextW`。那属于「重写渲染层」，已经不是本地化补丁的范畴了
（也违背本项目「只用游戏自带机制」的原则）。

## 另：翻译来源

- `zh-CN`：人工翻译，且用官方 `DEU/FRA/ESP/ITA` 四个本地化版本逐条对照校核（见 `translations/ref/`）；
- 其余语言：Google 翻译批量产出（`tools/mtranslate.py`），并做了三重保护：
  行首颜色码 `Y/G/O/-`、`%s/%d/%c` 占位符、`\n`/`\t` 换行制表符；
- 车手短名（Axle/Bose/Cydney/Jon/Pearl/Rhonda/Jim/Mike）在所有语言都保留英文——
  它们同时用于拼人物立绘路径 `Chars\<名字>-F.RRI`，翻译会导致立绘丢失（官方 4 语版也保留英文）；
- 制作名单（credits，id 1000-1999）在所有语言保留英文。
