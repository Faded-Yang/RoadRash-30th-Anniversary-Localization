# Road Rash 30th Anniversary — 多语言本地化

**暴力摩托：30 周年纪念版** 的非官方多语言本地化 —— 使用游戏自带的语言 DLL 机制，外加 120 字节的文本转码兼容层，让**任何语言在任何语言的 Windows 上都能正确显示**。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Faded-Yang/RoadRash-30th-Anniversary-Localization?label=release&color=red)](../../releases)
[![Build](https://img.shields.io/github/actions/workflow/status/Faded-Yang/RoadRash-30th-Anniversary-Localization/release.yml?label=build)](../../actions)
![Languages](https://img.shields.io/badge/languages-63-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%2095%E2%80%93%2011-lightgrey)
![Chinese](https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-human%20translated-red)

---

## 安装（一分钟）

1. 下载 `RoadRash-30th-Localization.exe`（[最新 Release](../../releases/latest)）
2. **把它放进游戏目录** —— 和 `RoadRash95.exe` 同级，通常是
   `...\Steam\steamapps\common\RoadRash\`
3. 双击运行 → 按提示选语言 → 完成（会自动请求管理员权限）

> 安装器**只认自己所在的目录**，不会去猜 Steam 路径。放错了会明确提示你放回去。

```bat
installer.exe            :: 交互式菜单，自动推荐系统语言
installer.exe ja         :: 直接装日语
installer.exe uninstall  :: 还原成原版
```

## 支持的语言

游戏**官方自带** English / Deutsch / Français / Italiano / Español 五种，本项目不需要也不提供。
其余 **56 种 + 繁体** 由本项目生成，**全部可在任意语言的 Windows 上正常显示**（v1.2.0 起）：

<details>
<summary><b>展开完整清单（按 Windows 代码页分组）</b></summary>

| 代码页 | 字符集 | 字体 | 语言 |
|---|---|---|---|
| 1252 | ANSI | Arial Narrow（原版） | pt nl da sv nb fi is ca eu gl af sq id ms tl sw ht cy ga mt lb |
| 1250 | EastEurope | Arial | pl cs sk hu sl hr ro bs |
| 1251 | Russian | Arial | ru uk bg sr mk be mn kk ky tg |
| 1253 | Greek | Arial | el |
| 1254 | Turkish | Arial | tr az |
| 1255 | Hebrew | Arial | he |
| 1256 | Arabic | Arial | ar fa ur ps sd |
| 1257 | Baltic | Arial | et lv lt |
| 1258 | Vietnamese | Arial | vi |
| 874 | Thai | Tahoma | th |
| 932 | ShiftJIS | MS Gothic | ja |
| 936 | GB2312 | SimHei | **zh-CN** |
| 949 | Hangul | Gulim | ko |
| 950 | Big5 | MingLiU | zh-TW |

</details>

## 它到底改了什么

```
RoadRash\
  TEXT\ENU.DLL                 ← 换成目标语言的文本资源 DLL（备份 ENU.DLL.rrzhbak）
  RoadRash95.exe               ← 字体 2 处 + 文本转码兼容层（备份 RoadRash95.exe.rrzhbak）
```

| 改动 | 内容 |
|---|---|
| 字体字符集 | 文件偏移 `0x60171`：`push 0` → `push <字符集>`
| 字体名 | `0x1059B4`：`"Arial Narrow"` → 对应语言字体
| **文本转码兼容层** | .text 代码洞里 120 字节桩 + 6 处 `LoadStringA`→`LoadStringW` 调用重定向 |

### 兼容层是干什么的

1996 年的程序用 `LoadStringA` 取文本，它会按**系统 ANSI 代码页**把 UTF-16 转成字节。
中文系统（CP936）下，日文/韩文/阿拉伯文等字符会直接变成 `?` —— 这就是旧版「满屏问号」的根因。

兼容层把这一步换成 `LoadStringW` + `WideCharToMultiByte(目标代码页)`，
于是**文本渲染与系统区域设置彻底解耦**。

- 桩代码 120 字节，**零重定位**，放在 .text 既有的对齐填充里（不新增节、不改文件大小）
- 改动：关闭 ASLR（1 bit）、.text 加写权限（1 bit）、6 处调用点各 6 字节
- 全部可逆：卸载即还原

> 实测：**韩文（CP949）在中文 Windows（CP936）上完整显示** —— 韩文完全不在 GBK 里，
> 这是「真的绕开了系统代码页」的铁证。

## 技术边界

仍然只有 **Windows 存在 ANSI 代码页的书写系统**可渲染（对应 `WideCharToMultiByte` 的代码页）。
印地语、孟加拉语、泰米尔语、泰卢固语、高棉语、老挝语、缅甸语、格鲁吉亚语、亚美尼亚语、阿姆哈拉语等 30+ 种做不到。
详见 [docs/LANGUAGES.md](docs/LANGUAGES.md)。

## 仓库结构

```
installer/installer.c          单文件安装器（内嵌全部语言 DLL + 补丁器）
installer/thunk.S              文本转码兼容层（32 位汇编，120 字节）
installer/build_installer.py   构建脚本
tools/build_dll.py             从 id→文本 JSON 生成纯资源 PE32 DLL
tools/mtranslate.py            Google 翻译批量管道（占位符/颜色码/换行保护）
tools/re/                      PE 逆向小工具
translations/en.json           英文原文（1372 条）
translations/lang/*.json       58 个语言包
docs/PRINCIPLE.md              逆向原理与二进制事实
docs/LANGUAGES.md              语言支持边界
docs/REVIEW.md                 五语逐条审校记录
docs/LEDGER.md                 完整工程台账
```

## 构建

```bash
pip install pefile
python installer/build_installer.py
# 产物：dist/RoadRash-30th-Localization.exe
```

需要 32 位 gcc（用于汇编兼容层）。CI 用 msys2 UCRT64 + `gcc -m32`。

## 许可与致谢

- 代码：**MIT**（见 [LICENSE](LICENSE)）
- 本补丁不含任何游戏原始资源，仅供个人学习与本地化交流，**禁止商用**
- 逆向参考（仅交叉验证，未复用代码/译文）：
  [OBLPlife/RoadRash30th-Chinese](https://github.com/OBLPlife/RoadRash30th-Chinese) ·
  [xiezhengtao13-sys/RoadRash-30th-CHS-Patch](https://github.com/xiezhengtao13-sys/RoadRash-30th-CHS-Patch)

<sub>“Road Rash” 为 Electronic Arts Inc. 的商标。本项目为非官方、非商业的粉丝本地化作品，与 EA 无关。</sub>
