# 暴力摩托 30 周年纪念版 汉化 —— 完整台账

## 1. 目标与结论
用游戏**自带的多语言文本 DLL 机制**做简体中文汉化，不注入、不 hook、不接管渲染。
成品：`dist\暴力摩托30周年_简体中文汉化_v1.0.zip`（安装.ps1 + ENU_zh.DLL + README）。

## 2. 二进制事实（全部静态逆向确认 + 实测）

### 2.1 文本载体
- `TEXT\<LANG>.DLL` = **纯资源 PE32 DLL**（无导出、无代码），只含 `RT_STRING`(类型 6)。
- 资源树：根 → type 6 → 块 id `#1..#86, #126, #251`（共 88 块）→ 语言 `#1033`(0x409) → 数据。
- 数据格式：每块 16 条，每条 `u16 字符数 + UTF-16LE 字符`。
- ENU 1372 条 / 58025 字符；DEU 1373、FRA 1387、ESP 1372、ITA 1368（各语言 id 集合略有差异）。

### 2.2 EXE 取文本链路
- `0x43f9f0`：`RegOpenKeyExA(HKLM, "SOFTWARE\\Electronic Arts\\RoadRash 95", KEY_QUERY_VALUE)`
  → `RegQueryValueExA(hk, "Language", ...)` → 逐个与 `English/French/German/Italian/Spanish`
  （0x505b20/0x505b2c/0x505b34/0x505b3c/0x505b48）比较 → 全局 `[0x595968]` = 0/0x10/0x20/0x30/0x40，失败 = -1。
- `0x43ff90`：取 `[0x595968] + id` 偏移拼 `Text\<XXX>.dll` 路径，`LoadLibraryA`。
- `0x4401dc / 0x44020a`：**硬编码回落到 `Text\ENU.dll`**（这就是能「中文占英语槽」的根本原因）。
- 文本出口：`LoadStringA([0x5cd470], id, buf, n)`；`[0x5cd470]` = 语言 DLL 句柄。
- EXE **没有** `FindResourceA/LoadResource/LockResource/SizeofResource` 导入 —— 只有 LoadString。

### 2.3 字体与绘制
- 全游戏**唯一** `CreateFontA` 在 `0x460d9d`（函数 `0x460d40`），参数：
  `nHeight=[ebp+8]`, `nWidth=0`, `fnWeight=700`, `fdwCharSet=0(ANSI)`, `fdwQuality=0`,
  `fdwPitchAndFamily=4`, `lpszFace="Arial Narrow"`(@RVA 0x1065b4)。
- 绘制：`DrawTextA`（flags 0x4851），先画阴影再画正文；`SetBkMode(TRANSPARENT)`、`SetTextColor`。
- `AddFontResourceA` 有导入但**无调用点**；`BADLOC/FUTB/FUTD/FUTR.DLL` 是 TTF 字体（OS/2 表），未被引用。

### 2.4 文本格式约定
- **行首颜色码**：`Y`(黄) / `G`(绿) / `O`(橙) / `-`(白)，**只存在于 id ≥ 1000**（credits 与结局旁白）。
  id < 1000 里以 Y/G/O 开头的都是正文词首（`Go Home`/`GAME LOADING`/`Yes`/`You...`），
  跨 5 语言首字母不一致即可证明，**不得补前缀**。
- 占位符：`%s` `%d` `%c`（68 条含占位符）；`\n` 61 条、`\t` 215 条。
- `%s` 形态的路径：`Chars/%s-F`、`Chars/%s-%c`（%s 来自 helper `0x4332e0`）。
  该 helper：index 0 → 硬编码 `"Thrash"`；1..8 → 读 `[0x5cd49c]+0x598/0x59c/...`（8 个名字指针）。
  即**角色短名参与人物立绘文件名**。
  证据：官方 DEU/FRA/ESP/ITA 对 id 32、358-365 **全部保持英文**；对 37-39 却翻译了绰号部分。
  → 结论：id 32、358-365 必须保留英文，其余可译。
- 其余图片路径全是**硬编码 ASCII**（`Bikes/Rat/Banzai`、`Showroom/...`、`Postcard/City`、`Street/Klub`、
  `Results/Win%d`、`Restroom/Rest%d`、`Chars/Axle-N`…），因此车名/赛道名/地点名可放心翻译。
- CP936 **不含 ©(U+00A9) ®(U+00AE) ™(U+2122)** → `LoadStringA` 转 ANSI 会变 `?`。
  终稿规范化：`©`→`(C)`，`®`/`™`→ 删除。共 12 条受影响。

## 3. 最终方案
1. `TEXT\ENU.DLL` ← 中文资源 DLL（原文件备份 `ENU.DLL.zhbak`）。
2. `RoadRash95.exe` 2 处等长原地补丁：
   - RVA `0x60d71`：`6A 00` → `6A 86`（`push 0` → `push 134`，ANSI_CHARSET → GB2312_CHARSET）
   - RVA `0x1065b4`：`"Arial Narrow\0"` → `"SimHei"+7*0`（13 字节等长）
   - 文件偏移：`0x60171`、`0x1059B4`（EXE 固定基址、无 ASLR）
3. **不写注册表、不改语言选择表**。任何语言检测失败都回落 ENU = 中文。
4. 全部可逆（`install.ps1 -Uninstall`）。

### 3.1 曾经考虑并放弃的方案
- **占用意大利语槽位**（EXE 里把 `Italian`/`Text\ITA.dll` 等长改成 `Chinese`/`Text\CHS.dll` + 写注册表）：
  实测可用，但依赖注册表、且 Steam 切语言会破坏；已被「占英语槽」取代。
- **新增第 6 语言**：语言名/路径表无空位（表在 `0x505b54` 步长 16，第 6 项会压到 `%d %d` 常量），
  需代码洞，收益不足。

## 4. 工具链
| 脚本 | 作用 |
|---|---|
| `tools\peinfo.cjs / restree.cjs / extract_all.py` | PE 结构与 RT_STRING 解析 |
| `tools\build_dll.py` | 从块结构 + 中文 JSON 生成**纯资源 PE32 DLL**（资源树/数据项/RVA 手工布局） |
| `tools\verify_dll.py` | 真实 `LoadLibraryW` + `LoadStringA` 逐条比对（含 GBK 编码校验） |
| `tools\patch_exe.py` | 字体补丁（等长原地写、幂等、可逆） |
| `tools\install.py / dist\安装.ps1` | 安装/卸载（PS 版免 Python） |
| `tools\check_trans.py / check_patch.py` | 译文硬规则校验（颜色码/占位符/换行/长度） |
| `tools\audit_cp936.py` | CP936 不可表示字符审计 |
| `tools\make_ref.py` | 生成 5 语言逐 id 对照 |

## 5. 翻译工艺
- 1372 条人工翻译，分 A(0-499 UI/菜单/角色/车/赛道)、B(500-989 垃圾话)、C(1000-4003 credits/结局)、D(990-993)。
- **五语对照审校**：官方 DE/FR/ES/IT 与英文**逐 id 对齐**，用于消歧义。抓到的真错例：
  - id 25 `sheer cliff walls`：FR *falaises abruptes* / DE *steiler* → 陡峭（原误「笔直」）
  - id 43 `An ex-con`：FR *ancien escroc* / ES *ex convicto* → 蹲过大牢（原误「惯犯」）
  - id 145 `pussycat`：ES *gatita* → 小猫（原误「娘炮车」，且原文无侮辱）
  - id 153 `Fidgety`：DE *zappelig* → 躁动（原误「手痒」）；`slickest` → 最靓（原误「滑溜」）
  - id 156 `Stomping`：DE *stampfend* → 碾压（原误「跺脚」）
  - id 716 `dopest`：DE *dämlichste* / FR *la pire des nouilles* / ES *más colgado* / IT *più bifolco*
    **四语一致为贬义** → 「骑得最烂的车手」（不是「最带劲」）
  - id 871 `make an example of you` → 杀鸡儆猴；id 656 `turns me on` → 让我来劲
- 风格：90 年代美式机车混不吝腔，中文「糙、狠、有劲」。
- 保留英文：乐队/曲名、人名、厂牌、版权行、车型号名、8 个车手短名。

## 6. 统计
- 1372 条：**983 条译成中文(71.6%)**，389 条按规则保留英文（credits 主体 + 短名 + 乐队曲名 + 版权行）。
- 英文 58025 字符 → 中文 22305 字符（省 62%，排版更宽松）。

## 7. 已知限制
1. 需系统「非 Unicode 程序语言」= 中文 CP936，否则汉字变 `?`（ANSI 程序天生限制）。
2. Steam 验证完整性会还原两个文件，需重装。
3. 8 个车手短名保留英文（见 2.4）。
4. 视频内嵌英文、图片内嵌英文（如 splash 的美术字）无法通过文本层汉化。

## 8. 死路记录
- ✗ 用 `FindResource/LoadResource` 之类接管文本：EXE 根本没有这些导入。
- ✗ 翻译 id 32 / 358-365：断人物立绘路径（`Chars/%s-F`）。
- ✗ 依赖注册表 `Language` 的方案：Steam 换语言会破坏，且原安装本身没有该值。
- ✗ 在 `run_code` 里写含反引号转义（`\`n`）的 PowerShell 脚本：会提前终止 TS 模板字符串。
- ✗ 用无 BOM 的 UTF-8 写 .ps1：PowerShell 5.1 按 GBK 解析 → 中文全乱、语法报错。
- ✗ pefile 打开的文件退出后仍占映射：`dialogs.py` 死循环进程会锁住 EXE，导致写入失败（保留进程要杀）。
