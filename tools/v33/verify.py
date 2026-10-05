"""Prove the localised pack differs from upstream v33 in exactly one file."""
import hashlib
import os
import zipfile

HD2 = r"D:/SteamLibrary/steamapps/common/Helldivers 2"
UPSTREAM = os.path.join(HD2, "HD2ModManager", "Vanilla-Plus-Megapack-v33.zip")
OURS = os.path.join(HD2, "HD2ModManager", "HD2PatchTools", "publish",
                    "Vanilla-Plus-Megapack-v33-\u6c49\u5316\u7248.zip")
ENTRY = "options/KnowYourConstellation/9ba626afa44a3aa3.patch_0"


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    a = zipfile.ZipFile(UPSTREAM)
    b = zipfile.ZipFile(OURS)
    na, nb = a.namelist(), b.namelist()
    print("条目: 上游 %d, 我们 %d" % (len(na), len(nb)))
    if na != nb:
        print("  文件清单顺序不同:")
        print("   仅上游:", sorted(set(na) - set(nb)))
        print("   仅我们:", sorted(set(nb) - set(na)))
    same = changed = 0
    for name in na:
        da, db = a.read(name), b.read(name)
        if digest(da) == digest(db):
            same += 1
        else:
            changed += 1
            print("  差异: %-58s %d -> %d 字节" % (name, len(da), len(db)))
    print("逐字节相同 %d 个文件, 不同 %d 个文件" % (same, changed))
    ok = changed == 1 and digest(a.read(ENTRY)) != digest(b.read(ENTRY))
    print("结论:", "仅 Know Your Constellation 被替换" if ok else "与预期不符，需要人工检查")


if __name__ == "__main__":
    main()
