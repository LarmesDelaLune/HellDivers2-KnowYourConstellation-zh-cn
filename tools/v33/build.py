"""Build the v33-zh-CN Know Your Constellation module and splice it into the v33 option archive.

Source of truth:
  * upstream KnowYourConstellation v3.16 src  (== the source pinned by megapack v33)
  * our four localised files from HD2PatchTools/zh-build/src
Compiled with the game's own LuaJIT (bin/lua51.dll), exactly like the v26/v29 builds.
"""
import ctypes
import hashlib
import os
import shutil
import sys
import zipfile

HD2 = r"D:/SteamLibrary/steamapps/common/Helldivers 2"
PATCHTOOLS = os.path.join(HD2, "HD2ModManager", "HD2PatchTools")
HERE = os.path.dirname(os.path.abspath(__file__))
# 上游 KnowYourConstellation v3.16 源码基线，随仓库分发在 src_upstream/
UPSTREAM_SRC = os.path.join(HERE, "src_upstream")
LOCALISED = os.path.join(PATCHTOOLS, "zh-build", "src")
LOCALISED_FILES = ("catalogue.lua", "model.lua", "panel.lua", "heavy_data.lua")

SYS_SRC = os.path.join(HERE, "src")
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")

V33_ZIP = os.path.join(HD2, "HD2ModManager", "Vanilla-Plus-Megapack-v33.zip")
V29_ZH_DIR = os.path.join(PATCHTOOLS, "publish", "Vanilla-Plus-Megapack-v29-\u6c49\u5316\u7248",
                          "options", "KnowYourConstellation")
ENTRY_PATH = "options/KnowYourConstellation/9ba626afa44a3aa3.patch_0"

sys.path.insert(0, os.path.join(PATCHTOOLS, "tools"))
import repack_patch                                                      # noqa: E402
from luajit_load import load as luajit_load                              # noqa: E402
from repack_patch import load_entries, rebuild                           # noqa: E402

REVISION = "v3.16-zh-CN"
GAME_SHA = "2E2C3B7C2500646DADD5F2B4C6E0504DBB7E7896139F64CDDC0D1813C718F51E"
EXE_SHA = "F5FEE03DCFDB2E553A4752C283590950AC13316B376D8196AA556FF0400D5F06"
MODULE = "mods/cowboybingus/enemy_intelligence"

ORDER = [("create_api", "read_api"), ("resolve", "resolve"), ("mission", "mission"),
         ("catalogue", "catalogue"), ("model", "model"), ("panel", "panel"),
         ("install", "install"), ("heavy", "heavy"), ("heavy_data", "heavy_data"),
         ("presentation", "presentation")]


def step1_prepare_sources():
    print("== 1) 准备源码 ==")
    if not os.path.isdir(UPSTREAM_SRC):
        raise SystemExit("找不到上游源码目录: " + UPSTREAM_SRC)
    os.makedirs(SYS_SRC, exist_ok=True)
    copied = overlayed = 0
    for name in sorted(os.listdir(UPSTREAM_SRC)):
        if not name.endswith(".lua"):
            continue
        shutil.copyfile(os.path.join(UPSTREAM_SRC, name), os.path.join(SYS_SRC, name))
        copied += 1
    for name in LOCALISED_FILES:
        shutil.copyfile(os.path.join(LOCALISED, name), os.path.join(SYS_SRC, name))
        overlayed += 1
    print("   上游 v3.16 文件 %d 个，覆盖本地化文件 %d 个" % (copied, overlayed))
    for name in ("catalogue.lua", "model.lua", "panel.lua", "heavy_data.lua"):
        body = open(os.path.join(SYS_SRC, name), encoding="utf-8").read()
        print("   %-16s %d 字符, 含中文 %s" % (name, len(body),
              "是" if any(ord(c) > 127 for c in body) else "否"))
    for name in ("mission.lua", "resolve.lua"):
        body = open(os.path.join(SYS_SRC, name), encoding="utf-8").read()
        print("   %-16s %d 字符, 含 25480438 %s" % (name, len(body),
              "是" if "25480438" in body else "否"))


def build_wrapper():
    result = ""
    for variable, filename in ORDER:
        with open(os.path.join(SYS_SRC, filename + ".lua"), encoding="utf-8") as fh:
            source = fh.read()
        for forbidden in ("WriteProcessMemory", "VirtualProtect", "VirtualAlloc",
                          "CreateRemoteThread", "Network.", "RPC.", "ffi.cast('void (*"):
            assert forbidden not in source, "Unexpected side effect API: " + forbidden
        result += "local %s = (function()\n%s\nend)()\n" % (variable, source)
    result += ("install(create_api,mission,resolve,catalogue,model,panel,{revision='%s'"
               ",game_sha256='%s',exe_sha256='%s'},heavy,heavy_data,presentation)\n"
               % (REVISION, GAME_SHA, EXE_SHA))
    return result


def compile_with_game_luajit(source, chunk_name):
    dll = os.path.join(HD2, "bin", "lua51.dll")
    lib = ctypes.WinDLL(dll)
    G = -10002
    lib.luaL_newstate.restype = ctypes.c_void_p
    lib.luaL_openlibs.argtypes = [ctypes.c_void_p]
    lib.luaL_loadfile.restype = ctypes.c_int
    lib.luaL_loadfile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.lua_pcall.restype = ctypes.c_int
    lib.lua_pcall.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.lua_pushstring.restype = None
    lib.lua_pushstring.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.lua_setfield.restype = None
    lib.lua_setfield.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
    lib.lua_close.argtypes = [ctypes.c_void_p]

    os.makedirs(WORK, exist_ok=True)
    src_path = os.path.join(WORK, "wrapper.lua")
    bc_path = os.path.join(WORK, "module.luac")
    with open(src_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(source)
    with open(os.path.join(WORK, "compile.lua"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "local fh=assert(io.open(SRC,'rb')); local src=fh:read('*a'); fh:close()\n"
            "local chunk,err=loadstring(src,CHUNK)\n"
            "if not chunk then error('COMPILE: '..tostring(err)) end\n"
            "local dump=string.dump(chunk,true)\n"
            "local out=assert(io.open(OUT,'wb')); out:write(dump); out:close()\n"
            "print('compiled '..#src..' -> '..#dump..' bytes')\n")
    L = lib.luaL_newstate()
    lib.luaL_openlibs(L)
    for key, value in (("SRC", src_path), ("OUT", bc_path), ("CHUNK", "@" + chunk_name)):
        lib.lua_pushstring(L, value.encode("utf-8"))
        lib.lua_setfield(L, G, key.encode())
    if lib.luaL_loadfile(L, os.path.join(WORK, "compile.lua").encode()) != 0:
        raise SystemExit("cannot load compile.lua")
    if lib.lua_pcall(L, 0, 0, 0) != 0:
        raise SystemExit("compile script failed")
    lib.lua_close(L)
    with open(bc_path, "rb") as fh:
        return fh.read()


def module_entry(path):
    tmp = os.path.join(WORK, "probe.bin")
    os.makedirs(WORK, exist_ok=True)
    with open(path, "rb") as src, open(tmp, "wb") as dst:
        dst.write(src.read())
    _info, _orig, entries = load_entries(tmp)
    for ent in entries:
        if ent["path"] == MODULE:
            return ent["bc"]
    raise SystemExit("no %s entry in %s" % (MODULE, path))


def main():
    step1_prepare_sources()

    print("== 2) 拼装包装源码并编译 ==")
    wrapper = build_wrapper()
    print("   wrapper: %d 字节" % len(wrapper.encode("utf-8")))
    bc = compile_with_game_luajit(wrapper, MODULE)
    ok, err = luajit_load(bc)
    print("   模块字节码 %d 字节, LuaJIT 加载: %s%s" % (len(bc), ok, "" if ok else " " + str(err)))
    for probe in ("\u8ffd\u730e\u866b\u7fa4".encode(), "\u5410\u9178\u6cf0\u5766".encode(),
                  "\u654c\u60c5\u9884\u6d4b".encode(), b"Invalid caret advance", b"char_starts",
                  b"[\x5e\32-\126]"):
        print("   %-24s 出现 %d 次" % (probe.decode("utf-8", "replace"), bc.count(probe)))

    print("== 3) 与 v29 已发布的中文模块对比 ==")
    v29_patch = os.path.join(V29_ZH_DIR, "9ba626afa44a3aa3.patch_0")
    if os.path.exists(v29_patch):
        old = module_entry(v29_patch)
        print("   v29 模块 %d 字节 sha %s" % (len(old), hashlib.sha256(old).hexdigest()[:16]))
        print("   v33 模块 %d 字节 sha %s" % (len(bc), hashlib.sha256(bc).hexdigest()[:16]))
        print("   两者%s" % ("完全一致" if old == bc else "不同（需人工确认）"))

    print("== 4) 换进 v33 容器 ==")
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    z = zipfile.ZipFile(V33_ZIP)
    tpl = os.path.join(WORK, "v33_kyc.patch_0")
    with open(tpl, "wb") as fh:
        fh.write(z.read(ENTRY_PATH))
    info, orig, entries = load_entries(tpl)
    print("   模板 %d 字节, %d 条目" % (info["size"], len(entries)))
    swapped = False
    for ent in entries:
        if ent["path"] == MODULE:
            ent["bc"] = bc
            swapped = True
    assert swapped, "enemy_intelligence entry not found"
    repack_patch.orig_entries = entries
    out = rebuild(orig, {})
    dst = os.path.join(OUT, os.path.basename(ENTRY_PATH))
    with open(dst, "wb") as fh:
        fh.write(out)
    open(dst + ".stream", "wb").close()
    open(dst + ".gpu_resources", "wb").close()
    print("   写出 %s (%d 字节)" % (dst, len(out)))

    print("== 5) 复核 ==")
    _c, _o, centries = load_entries(dst)
    cb = [e for e in centries if e["path"] == MODULE][0]["bc"]
    print("   条目 %d 个: %s" % (len(centries),
          ", ".join(e["path"].split("/")[-1] for e in centries)))
    print("   模块 %d 字节, LuaJIT %s, 中文标记 %d, 编组中文 %d"
          % (len(cb), luajit_load(cb)[0], cb.count("\u8ffd\u730e\u866b\u7fa4".encode()),
             cb.count("\u5e38\u89c4\u90e8\u961f".encode())))
    assert cb == bc, "roundtrip mismatch"
    print("   容器内模块与编译结果一致")


if __name__ == "__main__":
    main()
