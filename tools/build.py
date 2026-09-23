"""把改好的 zh-CN 源码编译成模块字节码，并打进 .patch_N 容器。

模板与作者 components/KnowYourConstellation/scripts/module.py 一致，
但用游戏自带的 bin/lua51.dll 编译（不依赖作者的 pinned LuaJIT）。
"""

import ctypes
import glob
import os
import sys

TOOLS = r"D:\SteamLibrary\steamapps\common\Helldivers 2\HD2ModManager\HD2PatchTools\tools"
sys.path.insert(0, TOOLS)

import repack_patch                                   # noqa: E402
from luajit_load import load as luajit_load           # noqa: E402
from repack_patch import load_entries, rebuild        # noqa: E402

GAME = r"D:\SteamLibrary\steamapps\common\Helldivers 2"
BUILD = os.path.join(GAME, r"HD2ModManager\Vanilla-Plus-Megapack-v12\options"
                            r"\KnowYourConstellation\_zhbuild")
PACK = os.path.join(GAME, r"HD2ModManager\Vanilla-Plus-Megapack-v26\options\KnowYourConstellation")
OUT_DIR = os.path.join(BUILD, "out")
WORK = os.path.join(BUILD, "work")

REVISION = "v3.15-zh-CN"
GAME_SHA = "73374BD4E38386BEB9A23BEF480082B67D457EBC77485FBEC5F488B4E95E201F"
EXE_SHA = "D8E23968D1412B07E06785321727D63EDF74E711214D6F6ADEB3BFCA95CA6827"
MODULE = "mods/cowboybingus/enemy_intelligence"

ORDER = [("create_api", "read_api"), ("resolve", "resolve"), ("mission", "mission"),
         ("catalogue", "catalogue"), ("model", "model"), ("panel", "panel"),
         ("install", "install"), ("heavy", "heavy"), ("heavy_data", "heavy_data"),
         ("presentation", "presentation")]


def build_wrapper():
    result = ""
    for variable, filename in ORDER:
        with open(os.path.join(BUILD, "src", filename + ".lua"), encoding="utf-8") as fh:
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
    """Compile Lua source with the game's own LuaJIT and return stripped bytecode."""
    dll = os.path.join(GAME, "bin", "lua51.dll")
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
    return open(bc_path, "rb").read()


print("== 1) 拼装包装源码 ==")
wrapper = build_wrapper()
print("   wrapper source: %d bytes, %d chars" % (len(wrapper.encode("utf-8")), len(wrapper)))
print("   chinese lines   :", sum(1 for line in wrapper.splitlines()
                                 if any(ord(c) > 127 for c in line)))

print("== 2) 用游戏 LuaJIT 编译 ==")
bc = compile_with_game_luajit(wrapper, MODULE)
ok, err = luajit_load(bc)
print("   bytecode %d bytes, LuaJIT load: %s%s" % (len(bc), ok, "" if ok else " " + str(err)))
for probe in ("追猎虫群".encode(), "吐酸泰坦".encode(), "敌情预测".encode(),
              b"Invalid caret advance", b"char_starts", b"[\x5e\32-\126]"):
    print("   %-34s %d" % (probe.decode("utf-8", "replace")[:34], bc.count(probe)))

print("== 3) 打包成 .patch_N ==")
pack_file = sorted(glob.glob(os.path.join(PACK, "9ba626afa44a3aa3.patch_*")))
pack_file = [f for f in pack_file if not f.endswith((".stream", ".gpu_resources"))][0]
info, orig, entries = load_entries(pack_file)
print("   模板容器: %s (%d bytes, %d 条目)" % (os.path.basename(pack_file), info["size"], len(entries)))
swapped = False
for ent in entries:
    if "enemy_intelligence" in ent["path"]:
        ent["bc"] = bc
        swapped = True
assert swapped, "enemy_intelligence entry not found"
repack_patch.orig_entries = entries
out = rebuild(orig, {})
os.makedirs(os.path.join(OUT_DIR, "data"), exist_ok=True)
dst = os.path.join(OUT_DIR, "data", os.path.basename(pack_file))
open(dst, "wb").write(out)
open(os.path.join(OUT_DIR, "data", os.path.basename(pack_file) + ".stream"), "wb").close()
open(os.path.join(OUT_DIR, "data", os.path.basename(pack_file) + ".gpu_resources"), "wb").close()
print("   写出: %s (%d bytes)" % (dst, len(out)))

check, _, centries = load_entries(dst)
cb = [e for e in centries if "enemy_intelligence" in e["path"]][0]["bc"]
print("   复核: 条目 %d, 模块 %d bytes, LuaJIT %s, 中文标记 %d"
      % (len(centries), len(cb), luajit_load(cb)[0], cb.count("追猎虫群".encode())))
