# Road Rash 30th Anniversary — 多语言本地化

**暴力摩托：30 周年纪念版** 的非官方多语言本地化 —— 完全使用游戏自带的语言 DLL 机制，不注入、不 hook、不挂外挂层。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Faded-Yang/RoadRash-30th-Anniversary-Localization?label=release&color=red)](../../releases)
[![Build](https://img.shields.io/github/actions/workflow/status/Faded-Yang/RoadRash-30th-Anniversary-Localization/build.yml?label=build)](../../actions)
![Languages](https://img.shields.io/badge/languages-63-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%2095%E2%80%93%2011-lightgrey)
![Chinese](https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-human%20translated-red)

---

## 目录

- [这是什么](#这是什么)
- [安装（一分钟）](#安装一分钟)
- [支持的语言](#支持的语言)
- [它到底改了什么](#它到底改了什么)
- [技术边界：为什么不是所有语言](#技术边界为什么不是所有语言)
- [仓库结构](#仓库结构)
- [构建](#构建)
- [许可与致谢](#许可与致谢)

---

## 这是什么

这版游戏是 EA 用原始 MSVC 源码重编译的 1996 年 `Road Rash 95`。它的文本全部放在
`TEXT\<语言>.DLL` 的 Win32 字符串表（`RT_STRING`）里，由 `LoadStringA` 取出、`DrawTextA` 绘制。

本项目做的就是**把这个 DLL 换成对应语言的版本**：

| | |
|---|---|
| ✅ 使用游戏自己的机制 | 没有 `.dll` 注入、没有 API hook、没有覆盖层 |
| ✅ EXE 只改 2 处等长字节 | 字体字符集 + 字体名，不加代码、不改任何逻辑 |
| ✅ 完全可逆 | 安装器自带备份与卸载 |
| ✅ 简体中文是人工翻译 | 并用官方德/法/西/意四语版**逐条对照校核** |
| ⚙️ 其余 55 种语言 | Google 翻译批量产出，占位符/颜色码/换行三重保护 |

## 安装（一分钟）

1. 下载 `installer.exe`：[最新 Release](../../releases/latest)
   （或下载 `dist/一键安装.cmd` + `dist/installer.exe.gz.b64` 到同一目录，双击 cmd）
2. 把它**放进游戏目录**（和 `RoadRash95.exe` 同级，通常是
   `...\Steam\steamapps\common\RoadRash`）
3. 双击运行 → 按提示选语言 → 完成（会自动请求管理员权限）

```bat
installer.exe            :: 交互式菜单，自动推荐系统语言
installer.exe ja         :: 直接装日语
installer.exe uninstall  :: 还原成原版
```

> ⚠️ 中文版需要系统「非 Unicode 程序语言」= **中文(简体, 中国)**，否则汉字会变 `?`。
> 安装器会检测系统代码页并在不匹配时给出警告。

## 支持的语言

游戏**官方自带** English / Deutsch / Français / Italiano / Español 五种，本项目不需要也不提供。
其余 **56 种** 由本项目生成：

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
  TEXT\ENU.DLL                 ← 换成对应语言的文本资源 DLL（原文件备份为 ENU.DLL.rrzhbak）
  RoadRash95.exe               ← 2 处等长字节补丁（原文件备份为 RoadRash95.exe.rrzhbak）
```

| 文件偏移 | 原值 | 新值 | 作用 |
|---|---|---|---|
| `0x60171` | `6A 00`（`push 0` = ANSI_CHARSET） | `6A <字符集>` | 让 GDI 按对应代码页解释字节 |
| `0x1059B4` | `"Arial Narrow"\0` | 对应字体名 + 填 0 | 指定有该语言字形的字体 |

**为什么占「英语」槽位**：EXE 里写死了「任何语言检测失败都回落到 `Text\ENU.dll`」，
所以把中文放进去 = 默认语言就是中文，而且**零注册表依赖**，Steam 切语言也不会破坏。

## 技术边界：为什么不是所有语言

这是 1996 年的 ANSI 程序：`LoadStringA` 按系统 **ANSI 代码页**转字节，`DrawTextA` 再按字体字符集解释。
**只有 Windows 存在对应 ANSI 代码页的书写系统才可能显示。**

| 做不了 | 原因 |
|---|---|
| 印地 / 孟加拉 / 泰米尔 / 泰卢固 / 卡纳达 / 马拉雅拉姆 / 古吉拉特 / 旁遮普 / 马拉地 / 尼泊尔 / 僧伽罗 | 无 ANSI 代码页 |
| 高棉 / 老挝 / 缅甸 / 藏语 | 同上 |
| 格鲁吉亚 / 亚美尼亚 / 阿姆哈拉 / 提格里尼亚 / 切罗基 | 同上 |

要突破只能把 `LoadStringA`→`LoadStringW`、`DrawTextA`→`DrawTextW`，那是重写渲染层，
已不属于「本地化补丁」范畴。详见 [docs/LANGUAGES.md](docs/LANGUAGES.md)。

## 仓库结构

```
installer/installer.c             单文件安装器（C + Win32，内嵌全部语言 DLL）
installer/build_installer.py      构建脚本（不需要游戏原始文件）
tools/build_dll.py                从 id→文本 JSON 生成资源型 PE32 DLL
tools/patch_exe.py                字体补丁（等长、幂等、可逆）
tools/verify_dll.py               真实 LoadLibraryW + LoadStringA 逐条校验
tools/mtranslate.py               Google 翻译批量管道（占位符/颜色码/换行保护）
tools/mt_fill.py                  补齐漏翻条目
tools/make_ref.py                 生成官方四语逐 id 对照
tools/re/                         PE 逆向小工具（资源树 / 字符串表 / 反汇编）
translations/en.json              英文原文（1372 条）
translations/lang/*.json          58 个语言包
docs/PRINCIPLE.md                 逆向原理与二进制事实
docs/LANGUAGES.md                 语言支持边界
docs/REVIEW.md                    五语逐条审校记录
docs/LEDGER.md                    完整工程台账（偏移、函数、证据、死路）
```

## 构建

```bash
pip install pefile
python installer/build_installer.py
# 产物：dist/RoadRash-30th-Localization.exe
```

CI（[build.yml](.github/workflows/build.yml)）会在每次 push 时自动构建。

## 许可与致谢

- 代码：**MIT**（见 [LICENSE](LICENSE)）
- 本补丁不含任何游戏原始资源，仅供个人学习与本地化交流，**禁止商用**
- 逆向参考（仅交叉验证，未复用代码/译文）：
  [OBLPlife/RoadRash30th-Chinese](https://github.com/OBLPlife/RoadRash30th-Chinese) ·
  [xiezhengtao13-sys/RoadRash-30th-CHS-Patch](https://github.com/xiezhengtao13-sys/RoadRash-30th-CHS-Patch)

<sub>“Road Rash” 为 Electronic Arts Inc. 的商标。本项目为非官方、非商业的粉丝本地化作品，与 EA 无关。</sub>
