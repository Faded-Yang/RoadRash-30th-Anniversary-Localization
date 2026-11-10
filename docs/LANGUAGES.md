# 支持的语言清单与技术边界

## 渲染链路（v1.2.0 之后）

```
TEXT\<LANG>.DLL  ──RT_STRING(UTF-16)──▶  [120 字节兼容层]
                                        LoadStringW
                                        ↓
                                        WideCharToMultiByte(目标代码页)
                                        ↓
                                        DrawTextA + 对应 lfCharSet
```

两处关键：

1. **文本转码兼容层**：把 `LoadStringA`（按系统代码页转码）换成 `LoadStringW` + `WideCharToMultiByte(目标代码页)`。
   于是**渲染不再依赖系统区域设置** —— 韩文版在中文 Windows 上也能正确显示。
2. **字体字符集**：`CreateFontA` 的 `fdwCharSet` 必须与目标代码页匹配，`DrawTextA` 才会按对应的多字节编码解释字节。

## 为什么仍然不是「所有语言」

`WideCharToMultiByte` 需要一个**代码页**。Windows 只为下列书写系统提供了 ANSI 代码页：

| 代码页 | charset | 字体 | 语言 |
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

**没有代码页 = 做不了**：

| 书写系统 | 语言 |
|---|---|
| 天城文 | hi 印地语、mr 马拉地语、ne 尼泊尔语、sa 梵语 |
| 孟加拉系 | bn 孟加拉语、as 阿萨姆语 |
| 印度诸文 | gu 古吉拉特语、pa 旁遮普语、or 奥里亚语、ta 泰米尔语、te 泰卢固语、kn 卡纳达语、ml 马拉雅拉姆语、si 僧伽罗语 |
| 东南亚 | km 高棉语、lo 老挝语、my 缅甸语 |
| 高加索/非洲 | ka 格鲁吉亚语、hy 亚美尼亚语、am 阿姆哈拉语、ti 提格里尼亚语 |
| 其他 | bo 藏语、dz 宗喀语、chr 切罗基语、iu 因纽特语 |

UNICODE 本身能表示它们，但 GDI 的 `DrawTextA` 没有「UTF-8 字符集」这种东西；
要再进一步只能把绘制也换成 `DrawTextW`，那就是重写渲染层了。

## 翻译来源

- `zh-CN`：人工翻译，并用官方 `DEU/FRA/ESP/ITA` 四个本地化版本逐条对照校核（见 `docs/REVIEW.md`）
- 其余语言：Google 翻译批量产出，三重保护：行首颜色码 `Y/G/O/-`、`%s/%d/%c` 占位符、`\n`/`\t`
- 车手短名（Axle/Bose/Cydney/Jon/Pearl/Rhonda/Jim/Mike）在**所有语言**保留英文——它们参与人物立绘路径
  `Chars\<名字>-F.RRI`，翻译会导致立绘丢失（官方四语版也保留英文）
- 制作名单（credits，id 1000-1999）在所有语言保留英文
