"""把中文模块部署到 HD2Arsenal 仓库（原 v26 模块先备份到 source_v26）。"""

import glob
import os
import shutil
import sys

TOOLS = r"D:\SteamLibrary\steamapps\common\Helldivers 2\HD2ModManager\HD2PatchTools\tools"
sys.path.insert(0, TOOLS)
from luajit_load import load as luajit_load           # noqa: E402
from repack_patch import load_entries                # noqa: E402

GAME = r"D:\SteamLibrary\steamapps\common\Helldivers 2"
LOCAL = os.environ["LOCALAPPDATA"]
STORE = os.path.join(LOCAL, r"HD2Arsenal\mods\Vanilla-Plus-Megapack-v26_AR872693\options"
                            r"\KnowYourConstellation")
SRC = os.path.join(GAME, r"HD2ModManager\Vanilla-Plus-Megapack-v12\options"
                          r"\KnowYourConstellation\_zhbuild\out\data\9ba626afa44a3aa3.patch_0")
BACKUP = os.path.join(GAME, r"HD2ModManager\HD2PatchTools\source_v26\KnowYourConstellation")

if not os.path.isdir(STORE):
    raise SystemExit("store option dir not found: %s" % STORE)
if not os.path.exists(SRC):
    raise SystemExit("built module not found: %s" % SRC)

current = [f for f in sorted(os.listdir(STORE))
           if f.startswith("9ba626afa44a3aa3.patch_") and not f.endswith((".stream", ".gpu_resources"))]
if not current:
    raise SystemExit("no patch file in %s" % STORE)
name = current[0]

os.makedirs(BACKUP, exist_ok=True)
backup_path = os.path.join(BACKUP, name)
if not os.path.exists(backup_path):
    shutil.copy2(os.path.join(STORE, name), backup_path)
    print("backed up %s -> source_v26 (%d bytes)" % (name, os.path.getsize(backup_path)))
else:
    print("backup already present:", backup_path)

shutil.copy2(SRC, os.path.join(STORE, name))
print("deployed %s (%d bytes)" % (name, os.path.getsize(os.path.join(STORE, name))))

_, _, entries = load_entries(os.path.join(STORE, name))
bc = [e for e in entries if "enemy_intelligence" in e["path"]][0]["bc"]
print("  module %d bytes, LuaJIT load %s" % (len(bc), luajit_load(bc)[0]))
print("  chinese markers: 追猎虫群=%d 吐酸泰坦=%d 敌情预测=%d"
      % (bc.count("追猎虫群".encode()), bc.count("吐酸泰坦".encode()), bc.count("敌情预测".encode())))
print("  ascii guard left: %d" % bc.count(b"plain ASCII"))
