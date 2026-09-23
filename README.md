# Know Your Constellation — 简体中文 (v3.15)

非官方简体中文化：把 **Vanilla Plus Megapack** 里的敌情预测面板
（`mods/cowboybingus/enemy_intelligence`，上游版本 **v3.15**）的显示文本换成中文，
滚动方式与英文原版一致。已在游戏内实测：中文正常显示、不闪退。

![status](https://img.shields.io/badge/game%20build-25327279-informational)

## 下载 / 安装

从 [Releases](../../releases) 下载 `KnowYourConstellation-v3.15-zh-CN.zip`（或在 `dist/` 里）：

1. 关闭游戏，用 **HD2Arsenal** 或 **HD2MM** 导入该 ZIP。
2. 确保已安装 **Bingus Shared Loader v16 或更新**（本包不含加载器）。
3. 与整合包同时使用时，二选一：
   * 把本包**优先级设为高于整合包**；或
   * 在整合包选项里取消勾选 *Know Your Constellation*。
4. **Purge / Deploy**，正常启动游戏。

验证：`%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\EnemyIntelligence.log`
首行应为 `v3.15-zh-CN`；进入任务简报界面可看到中文滚动预报。

适用范围：游戏 **Steam build 25327279 / 1.8.45850.0**（模块内置游戏指纹校验，
游戏更新后需要重新构建）。

## 改了什么（相对上游源码）

上游的面板是 **ASCII-only** 且跑马灯**按字节**切分文本，中文会触发
`Invalid caret advance`（面板隐藏，严重时崩游戏）。本汉化做了 4 处改动：

| 文件 | 改动 |
| --- | --- |
| `src/panel.lua` | 跑马灯由「按字节」改为**按 UTF-8 字符边界**迭代（新增 `char_starts()`；`M.window()` 用字符边界换算字节下标）；内联 `ascii()` 放宽；`Invalid caret advance` 上界放宽到 `max(padding-inset, 2×detail_size)` |
| `src/model.lua` | `M.ascii()` 由「只许 ASCII」改为「只禁控制字符与分号」；面板固定文案改中文 |
| `src/catalogue.lua` | 31 条编组标题/说明 → 中文 |
| `src/heavy_data.lua` | 4 个重型单位显示名 → 中文 |

术语来源：游戏官方简体中文字符串资源（不是社区昵称）。

完整补丁见 [`patches/0001-zh-CN-localization.patch`](patches/0001-zh-CN-localization.patch)，
可以直接应用到上游 checkout：

```bash
git clone https://github.com/CowboyBingus/VanillaPlusMegapack.git
cd VanillaPlusMegapack
git am /path/to/0001-zh-CN-localization.patch
```

## 自己构建

上游要求 Windows x64 + Python 3.10+ + **其 `dependencies.json` 里 pin 的 LuaJIT**
（`msvcbuild.bat nogc64`，并用 `HD2_LUAJIT` 指向它），然后 `python -B scripts/build.py`。
注意上游构建会对**英文产物做逐字节比对**，改动过源码的构建需要按他们的流程更新
`components.lock.json`。

本仓库 `tools/` 里是我们实际用过的脚本（**路径按本机写的，使用前请改成你的路径**）：

| 脚本 | 作用 |
| --- | --- |
| `build.py` | 按上游 `scripts/module.py` 模板拼装 wrapper → 用**游戏自带 `bin\lua51.dll`** 编译成字节码 → 打进 `.patch_N` |
| `tests.py` | 用游戏 LuaJIT 跑组件自带测试（含本地化面板测试） |
| `localise_test.py` | 由上游 `tests/test_panel.lua` 生成中文本地化测试副本（英文期望值→中文、合成字体改为按字符度量、caret 断言按字符边界比较） |
| `deploy.py` | 写入本地 Arsenal 仓库并复核（会把原文件备份） |

测试：`python tests.py` —— `test_panel_zh` 覆盖中文逐字量宽、右边缘进入、六种分辨率、
切换任务不重播、滚动连续性、裁剪与缓存上限，全部通过。

## 致谢与授权说明

* 上游 mod 与整合包：**CowboyBingus** — <https://github.com/CowboyBingus/VanillaPlusMegapack>
  （加载器：<https://github.com/CowboyBingus/BingusSharedLoader>）
* 本仓库是**非官方汉化**，与上游作者无隶属关系；`data/` 里的模块是从上游源码重新编译的衍生作品。
* 上游仓库目前**未声明开源许可证**（CONTRIBUTING 原文：*"No repository-wide license has
  been selected."*）。因此本仓库只发布**补丁 + 构建脚本 + 自建缩略图**，
  不打包上游美术资源；若上游作者提出异议，会立即下架。
* 缩略图为自制占位图；整合包自带的 `thumbnail.png` 是原作者作品，未在本仓库分发。

## English summary

Unofficial Simplified Chinese localisation of the *Know Your Constellation* forecast panel
(upstream v3.15) inside Vanilla Plus Megapack. The upstream panel is ASCII-only and its marquee
slices text **byte-wise**, so any CJK text triggers `Invalid caret advance` (the panel hides and the
game can crash). This patch walks the marquee by **UTF-8 character boundaries** instead, relaxes the
validator to "no control characters or semicolons", and translates the catalogue/panel strings using
terminology from the game's official zh-Hans resources. Verified in game: Chinese text renders and
scrolls exactly like the English build. Install the ZIP from `dist/`, keep Bingus Shared Loader v16+
installed, and give this mod priority over the megapack (or uncheck the megapack's forecast option).
Unofficial, not affiliated with the upstream author.
