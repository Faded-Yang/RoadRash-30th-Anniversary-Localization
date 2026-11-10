# Road Rash 30th Anniversary — Localization Patch

Unofficial localization for **Road Rash: 30th Anniversary Edition** (Steam, `RoadRash95.exe`).
Non-invasive: the game's own language-DLL mechanism is reused — no injection framework, no overlays.

**中文说明见下方。**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Faded-Yang/RoadRash-30th-Anniversary-Localization?label=release&color=red)](../../releases)
![Platform](https://img.shields.io/badge/platform-Windows%2095%E2%80%9311-lightgrey)

---

## Supported languages

| Language | Status | Notes |
|---|---|---|
| 简体中文 (zh-CN) | ✅ **Verified** | Human translation, cross-checked against the game's four official localizations |
| 繁體中文 (zh-TW) | ✅ Verified | Converted from zh-CN |
| 日本語 (ja) | ✅ Verified | Machine translation |
| 한국어 (ko) | ✅ Verified | Machine translation |
| English / Deutsch / Français / Italiano / Español | — | **Already built into the game**, no patch needed |
| Other languages | ⚠️ Experimental | Machine translation; rendering is not verified on all Windows locale settings — not shipped by default |

Only the verified languages are offered by the installer. Other language sources stay in
`translations/lang/` for future work.

## Install

1. Download the installer for your language from [Releases](../../releases/latest).
2. **Put it inside the game folder** — the same folder as `RoadRash95.exe`, usually
   `...\Steam\steamapps\common\RoadRash\`.
3. Double-click and follow the prompt (it will ask for administrator rights).

Uninstall: run it again and choose uninstall.

## What it changes

```
RoadRash\
  TEXT\ENU.DLL          ← replaced with the localized text resource (original kept as ENU.DLL.rrzhbak)
  RoadRash95.exe        ← font charset / font name patch (original kept as RoadRash95.exe.rrzhbak)
```

The game reads its text from `TEXT\<LANG>.DLL` (Win32 `RT_STRING` resources) and fetches it with
`LoadStringA`. Putting the localized DLL into the English slot means the default language becomes
the patched one, with no registry dependency — any language-detection failure falls back to it.

## Repository layout

```
installer/     single-file installer (C + Win32)
tools/         PE tooling, DLL builder, translation pipeline
translations/  en.json + language packs
docs/          reverse-engineering notes and review records
```

## License

Code: MIT. The patch contains no original game assets; fan-made and non-commercial.
"Road Rash" is a trademark of Electronic Arts Inc.

---

# 暴力摩托：30 周年纪念版 · 汉化补丁

**已验证语言**：简体中文、繁體中文、日本語、한국어。
英语 / 德法西意五种是**游戏官方自带**，不需要补丁。
其余语言为机翻且渲染未经完整验证，**默认不随安装包发布**，源码保留在 `translations/lang/` 供后续完善。

**安装**：把对应语言的安装器**放进游戏目录**（与 `RoadRash95.exe` 同级）后双击，按提示操作。
卸载：再运行一次选择卸载，即可完整还原。

**改动**：`TEXT\ENU.DLL` 换成对应语言文本（原文件备份为 `.rrzhbak`）；
`RoadRash95.exe` 仅改字体字符集与字体名（等长字节，原文件备份）。全部可逆。

简体中文为人工翻译，并用游戏官方德/法/西/意四语版本逐条对照校校；
其余已验证语言为机器翻译。详见 `docs/`。
