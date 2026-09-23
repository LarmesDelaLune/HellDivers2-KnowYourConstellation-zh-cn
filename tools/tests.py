"""用游戏自带 LuaJIT 跑组件自带测试（合成数据），验证改动没有破坏逻辑。"""

import ctypes
import os
import sys

GAME = r"D:\SteamLibrary\steamapps\common\Helldivers 2"
BUILD = os.path.join(GAME, r"HD2ModManager\Vanilla-Plus-Megapack-v12\options"
                            r"\KnowYourConstellation\_zhbuild")
WORK = os.path.join(BUILD, "work")

TESTS = ["test_panel_zh", "test_mission", "test_resolve", "test_install", "test_heavy",
         "test_presentation", "test_rows"]


def make_state():
    lib = ctypes.WinDLL(os.path.join(GAME, "bin", "lua51.dll"))
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
    lib.lua_tolstring.restype = ctypes.c_char_p
    lib.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_size_t)]
    lib.lua_close.argtypes = [ctypes.c_void_p]
    return lib


os.makedirs(WORK, exist_ok=True)
runner = os.path.join(WORK, "run_test.lua")
with open(runner, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("arg = {SRC_DIR}\n"
             "local ok, err = pcall(dofile, TEST_FILE)\n"
             "if not ok then print('FAILED: ' .. tostring(err)) os.exit(1) end\n")

LIB = make_state()
failures = 0
for name in TESTS:
    test_file = os.path.join(BUILD, "tests", name + ".lua")
    if not os.path.exists(test_file):
        continue
    lib = LIB
    L = lib.luaL_newstate()
    lib.luaL_openlibs(L)
    for key, value in (("SRC_DIR", os.path.join(BUILD, "src")), ("TEST_FILE", test_file)):
        lib.lua_pushstring(L, value.encode())
        lib.lua_setfield(L, -10002, key.encode())
    print("===== %s =====" % name)
    if lib.luaL_loadfile(L, runner.encode()) != 0:
        print("  cannot load runner")
        failures += 1
    elif lib.lua_pcall(L, 0, 0, 0) != 0:
        size = ctypes.c_size_t()
        msg = lib.lua_tolstring(L, -1, ctypes.byref(size))
        print("  ERROR: %s" % (msg.decode("utf-8", "replace") if msg else "?"))
        failures += 1
    lib.lua_close(L)

print()
print("failures:", failures)
