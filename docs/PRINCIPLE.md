# 逆向原理：这游戏的文本是怎么来的

> 全部结论均由静态逆向（pefile + capstone）+ 实机验证得出，未使用任何猜测。

## 1. 文本载体：语言 DLL 里的 RT_STRING

`TEXT\<LANG>.DLL` 是**纯资源 PE32 DLL**（无导出、无代码），只有一张标准 Win32 字符串表：

| 项 | 值 |
|---|---|
| 资源类型 | `RT_STRING` = 6 |
| 块 ID | `#1..#86`、`#126`、`#251`（88 块 × 16 条） |
| 语言 | `#1033` (0x409) |
| 每条格式 | `u16 字符数 + UTF-16LE 字符` |

- 英文原版 1372 条 / 58025 字符；DEU 1373、FRA 1387、ESP 1372、ITA 1368（各语言 id 集合略有出入）。
- 字符串 ID = `(块号-1)*16 + 块内序号`。

## 2. EXE 的语言选择逻辑

```
0x43f9f0:
  RegOpenKeyExA(HKLM, "SOFTWARE\\Electronic Arts\\RoadRash 95", KEY_QUERY_VALUE)
  RegQueryValueExA(hk, "Language", ...)          ; 0x505b14 = "Language"
  与 "English"/"French"/"German"/"Italian"/"Spanish"
     （0x505b20/0x505b2c/0x505b34/0x505b3c/0x505b48）比较
  → 全局 [0x595968] = 0 / 0x10 / 0x20 / 0x30 / 0x40，失败 = -1
```

`0x4401dc` / `0x44020a` 处**硬编码**了回落逻辑：语言槽取不到时，直接
`LoadLibraryA("Text\\ENU.dll")`。

> **这就是本项目方案的基础**：把中文/译文放进「英语槽位」，任何检测失败都回落到它，
> 于是完全不需要改注册表、不需要改语言选择表。

## 3. 文本出口

- `LoadStringA([0x5cd470], id, buf, n)`，`[0x5cd470]` = 语言 DLL 的 `HMODULE`。
- EXE **没有** `FindResourceA / LoadResource / LockResource / SizeofResource` 导入 —— 只有 `LoadStringA`，
  所以除了字符串表没有第二条取文本的路。

## 4. 字体与绘制（中文必须改的两处）

全游戏**唯一**一处 `CreateFontA` 在 RVA `0x460d9d`（函数 `0x460d40`）：

| 参数 | 原值 |
|---|---|
| nHeight | `[ebp+8]`（调用方给） |
| fnWeight | `700` |
| **fdwCharSet** | **`0` = ANSI_CHARSET** ← 中文会乱码的根因 |
| fdwPitchAndFamily | `4` |
| **lpszFace** | **`"Arial Narrow"`**（RVA 0x1065b4） |

绘制用 `DrawTextA`（flags `0x4851`），先画阴影再画正文。

因此只需要 2 处**等长字节**补丁：

| 文件偏移 | 原 | 新 |
|---|---|---|
| `0x60171` | `6A 00`（`push 0`） | `6A 86`（`push 134` = GB2312_CHARSET） |
| `0x1059B4` | `"Arial Narrow\0"` | `"SimHei"+7×0`（13 字节） |

> 该 EXE 固定基址、无 ASLR，文件偏移稳定；安装器另有 SHA-256 校验防止打错版本。

## 5. 文本格式里的坑

### 5.1 行首颜色码
`Y`（黄）/ `G`（绿）/ `O`（橙）/ `-`（白），**只存在于 id ≥ 1000**（制作名单与结局旁白）。
id < 1000 里以 `Y/G/O` 开头的是正文词首（`Go Home`、`GAME LOADING`、`Yes`、`You...`）——
跨 5 语言首字母不一致即可证明，**不得补前缀**，否则首字母会被当颜色码吃掉。

### 5.2 角色短名参与图片路径
`Chars/%s-F`、`Chars/%s-%c` 的 `%s` 来自 helper `0x4332e0`：
index 0 → 硬编码 `"Thrash"`；1..8 → 读 `[0x5cd49c]+0x598/0x59c/...` 共 8 个名字指针。
即 **id 32 与 358-365 的车手短名是人名图片文件名的一部分**。
证据：官方 DEU/FRA/ESP/ITA 对这 9 条**全部保持英文**，却翻译了 37-39 的绰号部分。

其余图片路径全是硬编码 ASCII（`Bikes/Rat/Banzai`、`Postcard/City`、`Street/Klub`、
`Results/Win%d`、`Restroom/Rest%d`、`Chars/Axle-N` …），所以车名/赛道名/地点名可以放心翻译。

### 5.3 CP936 没有 © ® ™
`LoadStringA` 转 ANSI 时会变 `?`。简体中文终稿已统一：`©`→`(C)`，`®`/`™`→ 删除。

## 6. 被排除的方案

| 方案 | 为什么放弃 |
|---|---|
| 占用意大利语槽（改语言名 + 路径 + 注册表） | 依赖注册表，Steam 切语言会破坏 |
| 新增第 6 语言 | 语言表在 `0x505b54` 步长 16，第 6 项会压到 `%d %d` 常量，需代码洞 |
| 改写 `LoadStringA`→`LoadStringW` 以支持任意 Unicode | 需要重写渲染层，超出「只用游戏自带机制」的范围。见 docs/LANGUAGES.md |

## 7. 工具链

```
tools/build_dll.py       从块结构 + JSON 生成纯资源 PE32（手工布局资源树/RVA）
tools/patch_exe.py       字体补丁（等长原地写、幂等、可逆）
tools/verify_dll.py      真实 LoadLibraryW + LoadStringA 逐条比对
tools/mtranslate.py      Google 翻译批量管道（占位符/颜色码/换行保护）
tools/make_ref.py        生成 5 语言逐 id 对照
installer/installer.c    单文件安装器（C + Win32，内嵌全部语言 DLL）
```
