# Road Rash 30th Anniversary Edition — 多语言本地化

> **暴力摩托：30 周年纪念版** 的非官方多语言本地化补丁。
> Fan-made multilingual localization for *Road Rash 30th Anniversary Edition* (Steam, `RoadRash95.exe`).

[![build installer](https://github.com/Faded-Yang/RoadRash-30th-Anniversary-Localization/actions/workflows/build.yml/badge.svg)](https://github.com/Faded-Yang/RoadRash-30th-Anniversary-Localization/actions/workflows/build.yml)

---

## 这是什么

这版游戏是 EA 用原始 MSVC 源码重编译的 1996 年 `Road Rash 95`，文本全部放在
`TEXT\<语言>.DLL` 的 Win32 字符串表（`RT_STRING`）里，由 `LoadStringA` 取出、`DrawTextA` 绘制。

本项目的做法是**完全使用游戏自带的本地化机制**：

- 不注入、不 hook、不做外挂式覆盖层；
- 只把 `TEXT\ENU.DLL` 换成对应语言的中文/译文资源 DLL（原文件保留备份）；
- EXE 只改 **2 处等长字节**（字体字符集 + 字体名），不加代码、不改布局；
- 全部可逆（安装器自带卸载）。

## 支持的语言

游戏**官方自带** 5 种（English / Deutsch / Français / Italiano / Español），本项目不需要也不提供。
本项目额外提供 **56 种**语言的本地化，覆盖 Google 翻译支持、且 Windows ANSI 代码页能渲染的书写系统：

| 代码页 | 语言 |
|---|---|
| 1252 | pt nl da sv nb fi is ca eu gl af sq id ms tl sw ht cy ga mt lb |
| 1250 | pl cs sk hu sl hr ro bs |
| 1251 | ru uk bg sr mk be mn kk ky tg |
| 1253 | el |
| 1254 | tr az |
| 1255 | he |
| 1256 | ar fa ur ps sd |
| 1257 | et lv lt |
| 1258 | vi |
| 874 | th |
| 932 | ja |
| 936 | zh-CN（本项目主目标，人工翻译 + 五语审校） |
| 949 | ko |
| 950 | zh-TW |

详见 [docs/LANGUAGES.md](docs/LANGUAGES.md)（含**为什么某些语言做不了**）。

> ⚠️ 这是 1996 年的 ANSI 程序：`LoadStringA` 会按系统 **ANSI 代码页**把 UTF-16 转成单/多字节。
> 因此某个语言能否正常显示，取决于你 Windows 的「非 Unicode 程序语言」设置。
> 安装器会检测并提示不匹配。安装中文版需要系统区域为 **中文(简体, 中国)**。

## 安装

1. 下载 `installer.exe`（见 Releases 或 Actions 构建产物）；
2. 把它**放进游戏目录**（和 `RoadRash95.exe` 同级，通常是
   `...\Steam\steamapps\common\RoadRash`）；
3. 双击运行 → 按提示选语言 → 完成。

安装器会自动：备份 → 写入对应语言 DLL → 打字体补丁。
卸载：再运行一次，命令行加 `uninstall`，或选择卸载。

命令行用法：

```
installer.exe            # 交互式选择
installer.exe ja         # 直接装日语
installer.exe uninstall  # 还原
```

## 目录结构

```
installer/installer.c     单文件安装器源码（C + Win32，内嵌全部语言 DLL）
installer/build_installer.py  编译并打包 installer.exe
tools/                    逆向与本地化工具链
  build_dll.py            从块结构 + JSON 生成资源型 PE32 DLL
  patch_exe.py            字体补丁（等长、幂等、可逆）
  mtranslate.py           Google 翻译批量管道（占位符/颜色码/换行保护）
  make_ref.py             生成 5 语言逐 id 对照
translations/
  zh-CN.json              简体中文（人工翻译 + 官方四语审校）
  lang/*.json             其余 55 种（Google 翻译批量产出）
docs/
  PRINCIPLE.md            逆向原理与二进制事实
  LANGUAGES.md            支持/不支持的语言及技术原因
  LEDGER.md               完整工程台账（偏移、函数、证据、死路）
```

## 许可

- 代码（工具链、安装器）：**MIT**，见 [LICENSE](LICENSE)。
- 译文：本项目产出，可自由使用。
- 游戏本身及其原始文本版权归 **Electronic Arts / Papyrus Design Group** 所有。
  本补丁**不包含**任何游戏原始资源，仅提供替换用的文本资源 DLL，
  仅供个人学习与本地化交流使用，**禁止商用**。

## 致谢 / Prior art

逆向过程中参考了这些公开工作（仅作交叉验证，未复用其代码或译文）：

- [OBLPlife/RoadRash30th-Chinese](https://github.com/OBLPlife/RoadRash30th-Chinese) — 用 `BeginUpdateResourceW` 改写字符串表 + 代码洞改字体
- [xiezhengtao13-sys/RoadRash-30th-CHS-Patch](https://github.com/xiezhengtao13-sys/RoadRash-30th-CHS-Patch) — 纯 `ENU.DLL` + PowerShell 安装
- 官方 `TEXT\{DEU,FRA,ESP,ITA}.DLL` 的逐 id 对照，是译文消歧义最权威的依据
