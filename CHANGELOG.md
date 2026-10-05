# Changelog

## 2026-10-05 — 项目暂停

* 上游 Know Your Constellation **v4.1** 内置官方简体中文（joyrhyme，PR #3），
  Better Lobby Management v1.2 同样内置；官方中文随游戏文本语言设置生效。
* 本仓库**不再跟进维护**。上游已不需要第三方汉化包，继续维护只会和上游重复。
* 保留存档：`patches/0001-zh-CN-localization.patch`、`tools/` 与 v3.15/v3.16 时期的
  构建记录。`dist/` 里的 ZIP 对应整合包 v33，已过期。
* 上游当时尚未覆盖文本的 Mod Options Menu、Mod Bindings Menu、Ship Station Hotkeys、
  Shallow Water Diving，改用官方 `scripts/translations.py` 制作的翻译包处理，不在本仓库发布。

## v3.16-zh-CN / megapack v33 (2026-09-28)

* Rebuilt for Vanilla Plus Megapack **v33** (same game build 25480438 / 1.8.46015.0). v33 adds three
  options (Flame Damage Fixed, Mod Options Menu, Mod Bindings Menu) and, from v31, requires
  **Bingus Shared Loader v18**.
* No localisation change: upstream Know Your Constellation is still pinned at **v3.16**, the four files
  we touch are byte-identical, and the recompiled module is byte-identical to the v29 build
  (35,195 bytes, sha256 `9825034b…`).
* Packages: `Vanilla-Plus-Megapack-v33-汉化版.zip` (full pack, 16 options) and
  `KnowYourConstellation-v33-ZH-CN.zip` (standalone overlay).
* Verified against upstream v33: 54 of 55 archive entries are byte-identical; only
  `options/KnowYourConstellation/9ba626afa44a3aa3.patch_0` is replaced. The megapack's
  `components.lock.json` source hashes for v3.16 match the current upstream checkout 31/31, and
  `patches/0001-zh-CN-localization.patch` still applies cleanly.

## v3.16-zh-CN / megapack v29 (2026-09-26)

* Rebuilt for Vanilla Plus Megapack **v29** (game build 25480438 / 1.8.46015.0).
* Localisation patch re-applied cleanly to upstream v3.16 (the four touched files are unchanged).
* Package: `Vanilla-Plus-Megapack-v29-汉化版.zip` — the megapack with the Chinese forecast bundled in,
  so a single import gives all options plus the Chinese panel.

## v3.15-zh-CN (2026-09-23)

* First release: Simplified Chinese for the Know Your Constellation forecast panel (upstream v3.15).
* Fix marquee measurement for multi-byte text (character boundaries instead of byte prefixes).
* Allow non-ASCII display text (reject control characters and semicolons only).
* Translate 31 composition entries, panel captions and 4 heavy-unit names.
* Verified in game on Steam build 25327279 / game 1.8.45850.0.
