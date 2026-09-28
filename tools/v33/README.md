# zh-build-v33 —— Know Your Constellation v3.16 / 整合包 v33 简体中文构建

2026-09-28 完成。对应上游 megapack **v33** + **Bingus Shared Loader v18**，
游戏 build **25480438** / exe **1.8.46015.0**。

## 产物

| 文件 | 说明 |
| --- | --- |
| `publish\Vanilla-Plus-Megapack-v33-汉化版.zip` | 一键整合包：上游 v33 全部 16 个选项 + 中文敌情预测面板 |
| `publish\KnowYourConstellation-v33-ZH-CN.zip` | 独立汉化包：只替换敌情预测模块，配合英文整合包使用 |

两个包的 `data\9ba626afa44a3aa3.patch_0` 都是同一个容器：
`mods/cowboybingus/enemy_intelligence`（中文，35,195 字节）+ 整合包身份模块。

## 脚本

| 脚本 | 作用 |
| --- | --- |
| `build.py` | 拿上游 v3.16 源码 + `zh-build\src` 里的 4 个本地化文件拼 wrapper → 用游戏 `bin\lua51.dll` 编译 → 换进 v33 选项容器 |
| `pack.py` | 生成整合包（解 v33 → 换 KYC 归档 → 重压）和独立包（`manifest.json` + `README.txt` + `thumbnail.png` + `data\`） |
| `verify.py` | 与上游 v33 逐条比对，断言"只有 KYC 那一个文件不同" |
| `inspect.py` | 打印 v29/v33 里 KYC 容器的条目、哈希、选项列表 |

## 重建流程

```powershell
cd "D:\SteamLibrary\steamapps\common\Helldivers 2\HD2ModManager\Vanilla-Plus-Megapack-v12\options\KnowYourConstellation"
python _zhv33\build.py      # 编译 + 换模块，输出 _zhv33\out\
python _zhv33\pack.py       # 打包到 HD2PatchTools\publish\
python _zhv33\verify.py     # 校验
```

（脚本里的 `HD2` 是游戏根目录；`build.py` 默认读
`C:\Users\Admin\AppData\Local\Temp\upstream\kyc\src` 的上游克隆，
没有就用同目录下的 `src_upstream\`。）

## 汉化改了什么（与上游源码的差异）

只有 4 个文件，都在 `zh-build\src\`：

1. **`model.lua`** — `M.ascii()` 从"只许 ASCII"改为"只禁控制字符与分号"；面板固定文案改中文
2. **`panel.lua`**（核心）— 新增 `char_starts()` 按 UTF-8 前导字节算字符边界，跑马灯从按字节循环改为按字符循环，`M.window()` 改用字符边界换算下标，内联 `ascii()` 同样放宽，`Invalid caret advance` 上界放宽到 `max(padding-inset, 2×detail_size)`
3. **`catalogue.lua`** — 31 条编组标题/说明改中文
4. **`heavy_data.lua`** — 4 个重型单位显示名改中文

`mission.lua` / `resolve.lua` 用的是上游原版（v3.16），我们不动。

## 更新时间线（上游怎么跟进的）

| 版本 | 游戏 build | 上游改动 |
| --- | --- | --- |
| v3.15 | 25327279 | 21 个文件 +207/−245：`mission.lua` 里约 30 个游戏内偏移全部重定位 |
| v3.16 | 25480438 | 12 个文件 +149/−47，但代码只有 4 处：两个哈希、一个偏移 `0x21e18e0`→`0x21e1920`、版本号 |
| v3.16.1 | 25480438 | 纯文档，编译产物与 v3.16 完全相同 |

结论：游戏更新后，upstream 是"换哈希 + 挪偏移"还是"大改"，要看那次游戏动了多少结构；
我们的汉化只依赖 `panel.lua` 的排版和文案，跟偏移无关，所以只要上游没重写 `panel.lua`，
汉化补丁都能直接套上。
