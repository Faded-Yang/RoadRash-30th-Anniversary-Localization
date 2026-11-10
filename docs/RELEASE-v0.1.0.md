## 逆向验证与工具链

### 逆向结论
- 文本载体：`TEXT\<LANG>.DLL` 的 `RT_STRING` 资源（块 `#1..#86/#126/#251`，UTF-16LE）
- EXE 读注册表 `Language` 选语言槽，**任何失败都硬编码回落到 `Text\ENU.dll`**
- 全游戏唯一 `CreateFontA`，charset 补丁点 `0x60171`、字体名补丁点 `0x1059B4`
- 角色短名参与 `Chars/%s-F` 立绘路径（官方四语版也保留英文）

### 工具链
- `build_dll.py`：从 id→文本 JSON 生成纯资源 PE32（手工布局资源树 / RVA）
- `patch_exe.py`：等长原地字体补丁（幂等、可逆）
- `verify_dll.py`：真实 `LoadLibraryW` + `LoadStringA` 逐条比对
- `tools/re/`：资源树 / 字符串表 / 反汇编小工具

> 此版本无可执行产物，仅记录方法；安装器自 v1.0.0 起提供。
