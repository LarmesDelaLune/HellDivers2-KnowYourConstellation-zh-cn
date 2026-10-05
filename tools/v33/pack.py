"""Package the v33 localisation: full megapack and the standalone overlay."""
import hashlib
import json
import os
import shutil
import zipfile

HD2 = r"D:/SteamLibrary/steamapps/common/Helldivers 2"
PATCHTOOLS = os.path.join(HD2, "HD2ModManager", "HD2PatchTools")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MODULE = os.path.join(HERE, "out", "9ba626afa44a3aa3.patch_0")
V33_ZIP = os.path.join(HD2, "HD2ModManager", "Vanilla-Plus-Megapack-v33.zip")

PUBLISH = os.path.join(PATCHTOOLS, "publish")
PACK_DIR = os.path.join(PUBLISH, "Vanilla-Plus-Megapack-v33-汉化版")
PACK_ZIP = PACK_DIR + ".zip"
SOLO_DIR = os.path.join(PUBLISH, "KnowYourConstellation-v33-ZH-CN")
SOLO_ZIP = SOLO_DIR + ".zip"
OLD_SOLO = os.path.join(PUBLISH, "KnowYourConstellation-v29-ZH-CN")

ENTRY = "options/KnowYourConstellation/9ba626afa44a3aa3.patch_0"
GUID = "ff601510-468c-4224-8f14-c8e761a347b0"
NAME = "敌情预测 v3.16 简体中文（非官方汉化）"

DESC = (
    "把 Vanilla Plus Megapack 的敌情预测面板（Know Your Constellation v3.16）"
    "汉化为简体中文，滚动方式与英文原版一致。"
    "适用于整合包 v33 / 游戏 build 25480438。"
    "需另行安装 Bingus Shared Loader v18 或更新。"
    "与整合包同时启用时请把本包优先级设为高于整合包，"
    "或取消勾选整合包里的 Know Your Constellation；"
    "同一时间只启用一种敌情预测。预测不保证敌人实际出现。"
)

README = """敌情预测 v3.16 简体中文（非官方汉化）
======================================

把 Vanilla Plus Megapack 的敌情预测面板汉化为简体中文，滚动方式与英文原版一致。
本包是**独立汉化包**；如果您使用整合包 v33，也可以直接用整合包内的汉化版，二者只需选一个。

对应版本
--------
整合包 v33 / 游戏 Steam build 25480438 / 1.8.46015.0 / 加载器 Bingus Shared Loader v18 或更新

安装
----
1. 关闭游戏，用 HD2Arsenal 或 HD2MM 导入本包（本包不含加载器）。
2. 与整合包同时使用时二选一：
   · 把本包优先级设为高于整合包；或
   · 在整合包选项里取消勾选 Know Your Constellation。
   同一时间只启用一种敌情预测，避免两个模块互相覆盖。
3. Purge / Deploy，正常启动游戏。

验证
----
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs\\EnemyIntelligence.log
首行应显示 v3.16-zh-CN。

卸载
----
停用本包 → Purge / Deploy，即可回到整合包自带的面板（或英文原版）。

说明
----
· 术语对齐游戏官方简体中文资源，非社区昵称。
· 汉化实现：放宽面板的 ASCII 文本限制（改为只禁控制字符与分号），并把跑马灯由
  「按字节切分」改为「按 UTF-8 字符边界切分」，随后重新编译打包。
· 仅本机可见，不改变游戏数值、难度与联机行为。
· 非官方汉化，与上游作者 CowboyBingus 无隶属关系；请支持原作者。
  https://github.com/CowboyBingus/VanillaPlusMegapack
"""


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write_zip(entries, target):
    """entries: list of (arcname, source path)."""
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name, src in entries:
            with open(src, "rb") as fh:
                z.writestr(name, fh.read())


def build_megapack():
    print("== A) 整合包 v33 汉化版 ==")
    if os.path.isdir(PACK_DIR):
        shutil.rmtree(PACK_DIR)
    os.makedirs(PACK_DIR)
    order = []
    with zipfile.ZipFile(V33_ZIP) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            name = item.filename
            dest = os.path.join(PACK_DIR, *name.split("/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if name == ENTRY:
                shutil.copyfile(OUT_MODULE, dest)
            else:
                with z.open(item) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            order.append(name)
    print("   解包 %d 个文件到 %s" % (len(order), PACK_DIR))
    write_zip([(n, os.path.join(PACK_DIR, *n.split("/"))) for n in order], PACK_ZIP)
    print("   写出 %s (%d 字节, sha %s)"
          % (PACK_ZIP, os.path.getsize(PACK_ZIP), sha(PACK_ZIP)[:16]))


def build_standalone():
    print("== B) 独立汉化包 v33 ==")
    if os.path.isdir(SOLO_DIR):
        shutil.rmtree(SOLO_DIR)
    os.makedirs(os.path.join(SOLO_DIR, "data"))
    manifest = {
        "Version": 1,
        "Guid": GUID,
        "Name": NAME,
        "Description": DESC,
        "Options": [{
            "Name": NAME,
            "Description": DESC,
            "Include": ["data"],
            "Image": "thumbnail.png",
        }],
        "IconPath": "thumbnail.png",
    }
    with open(os.path.join(SOLO_DIR, "manifest.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(SOLO_DIR, "README.txt"), "w",
              encoding="utf-8", newline="\r\n") as fh:
        fh.write(README)
    shutil.copyfile(os.path.join(OLD_SOLO, "thumbnail.png"),
                    os.path.join(SOLO_DIR, "thumbnail.png"))
    base = os.path.basename(OUT_MODULE)
    shutil.copyfile(OUT_MODULE, os.path.join(SOLO_DIR, "data", base))
    open(os.path.join(SOLO_DIR, "data", base + ".stream"), "wb").close()
    open(os.path.join(SOLO_DIR, "data", base + ".gpu_resources"), "wb").close()
    files = []
    for root, _dirs, names in os.walk(SOLO_DIR):
        for name in sorted(names):
            full = os.path.join(root, name)
            files.append((os.path.relpath(full, SOLO_DIR).replace("\\", "/"), full))
    files.sort(key=lambda kv: kv[0])
    write_zip(files, SOLO_ZIP)
    print("   写出 %s (%d 字节, sha %s)"
          % (SOLO_ZIP, os.path.getsize(SOLO_ZIP), sha(SOLO_ZIP)[:16]))


def verify():
    print("== C) 校验 ==")
    want = sha(OUT_MODULE)
    for path in (PACK_ZIP, SOLO_ZIP):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            assert "manifest.json" in names, path + " 缺少根目录 manifest.json"
            got = None
            for n in names:
                if n.endswith("9ba626afa44a3aa3.patch_0") and "KnowYourConstellation" in n:
                    got = hashlib.sha256(z.read(n)).hexdigest()
            options = {n.split("/")[1] for n in names if n.startswith("options/")}
            print("   %-44s %d 条目, manifest.json OK, 选项 %s"
                  % (os.path.basename(path), len(names),
                     ("%d 个" % len(options)) if options else "无（独立包）"))
            if got is not None:
                print("      KYC patch_0 sha %s %s"
                      % (got[:16], "与编译结果一致" if got == want else "不一致"))


if __name__ == "__main__":
    build_megapack()
    build_standalone()
    verify()
