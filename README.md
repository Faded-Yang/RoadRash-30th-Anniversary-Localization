# Road Rash 30th Anniversary — 简体中文汉化补丁

**暴力摩托：30 周年纪念版**（Steam，`RoadRash95.exe`）的非官方简体中文汉化。
使用游戏自带的语言 DLL 机制，不改引擎、不加外挂层，全部可逆。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Faded-Yang/RoadRash-30th-Anniversary-Localization?label=release&color=red)](../../releases)
![Platform](https://img.shields.io/badge/platform-Windows%2095%E2%80%9311-lightgrey)

---

## 安装

1. 从 [Releases](../../releases/latest) 下载 `Install-zh-CN.exe`；
2. **把它放进游戏目录** —— 与 `RoadRash95.exe` 同级，通常是
   `...\Steam\steamapps\common\RoadRash\`；
3. **确认游戏已完全关闭**，双击运行，按提示操作（会请求管理员权限）。

卸载：再运行一次，命令行加 `uninstall`，即可完整还原。

> 安装器只认自己所在的目录；放错了会明确提示。

## 它改了什么

```
RoadRash\
  TEXT\ENU.DLL          ← 换成简体中文文本（原文件备份为 ENU.DLL.rrzhbak）
  RoadRash95.exe        ← 字体字符集/字体名 + 文本转码兼容层（备份 RoadRash95.exe.rrzhbak）
```

游戏从 `TEXT\<语言>.DLL` 的 Win32 `RT_STRING` 资源读取文本，用 `LoadStringA` 取出。
把中文放进「英语槽位」后，默认语言即为中文，且不依赖注册表——任何语言检测失败都会回落到它。

## 翻译

- **1372 条全部人工翻译**，其中 983 条中文化；
- 用游戏**官方德/法/西/意四个本地化版本逐条对照校核**，修正了一批误译（`sheer`→陡峭、`ex-con`→蹲过大牢、`dopest`→骑得最烂 等）；
- 保留行首颜色码、`%s/%d/%c` 占位符与换行制表符；
- 8 位车手短名保留英文（它们参与人物立绘路径 `Chars\<名字>-F.RRI`，翻译会掉图，官方四语版同样保留）。

## 支持的版本

仅**简体中文**。英语/德语/法语/意大利语/西班牙语为游戏官方自带，无需补丁；
其他语言的机翻版本经实测渲染不可靠，已从本项目移除。

## 许可

代码 MIT。本补丁不含任何游戏原始资源，非官方、非商业。
“Road Rash” 为 Electronic Arts Inc. 商标。
