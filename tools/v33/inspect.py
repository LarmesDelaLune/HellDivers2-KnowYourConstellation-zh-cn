"""比对 v29 / v33 整合包里 Know Your Constellation 选项的结构。"""
import hashlib
import os
import sys
import tempfile
import zipfile

HD2 = r"D:/SteamLibrary/steamapps/common/Helldivers 2/HD2ModManager"
sys.path.insert(0, os.path.join(HD2, "HD2PatchTools", "tools"))

from repack_patch import load_entries  # noqa: E402

ENTRY = "options/KnowYourConstellation/9ba626afa44a3aa3.patch_0"


def main():
    for name in ("Vanilla-Plus-Megapack-v29.zip", "Vanilla-Plus-Megapack-v33.zip"):
        path = os.path.join(HD2, name)
        if not os.path.exists(path):
            print("== %s  (缺失)" % name)
            continue
        z = zipfile.ZipFile(path)
        names = z.namelist()
        options = sorted({p.split("/")[1] for p in names if p.startswith("options/")})
        data = z.read(ENTRY)
        tmp = os.path.join(tempfile.gettempdir(), "kyc_probe.bin")
        with open(tmp, "wb") as fh:
            fh.write(data)
        info, _orig, entries = load_entries(tmp)
        print("== %s: %d 条目, %d 个选项, KYC patch_0 = %d 字节, sha256 %s"
              % (name, len(names), len(options), len(data),
                 hashlib.sha256(data).hexdigest()[:16]), flush=True)
        for ent in entries:
            print("     entry %-52s %d bytes  sha %s"
                  % (ent["path"], len(ent["bc"]),
                     hashlib.sha256(ent["bc"]).hexdigest()[:16]), flush=True)
        print("     options: " + ", ".join(options), flush=True)
        roots = sorted(p for p in names if "/" not in p)
        print("     根文件: " + ", ".join(roots), flush=True)


if __name__ == "__main__":
    main()
