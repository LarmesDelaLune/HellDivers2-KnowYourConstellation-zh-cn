"""生成本地化版的 test_panel_zh.lua（把写死的英文期望值换成中文）。"""

import io
import os

BUILD = (r"D:\SteamLibrary\steamapps\common\Helldivers 2\HD2ModManager"
         r"\Vanilla-Plus-Megapack-v12\options\KnowYourConstellation\_zhbuild")
src = os.path.join(BUILD, "tests", "test_panel.lua")
dst = os.path.join(BUILD, "tests", "test_panel_zh.lua")

text = io.open(src, encoding="utf-8").read()
pairs = [
    ("heavies={'Bile Titans'}", "heavies={'吐酸泰坦'}"),
    ("assert(m.marquee:find('BILE BUGS') and m.marquee:find('DRAGONROACH ACTIVITY') "
     "and m.marquee:find('Bile Titans'))",
     "assert(m.marquee:find('胆汁虫群') and m.marquee:find('蟑龙活动') "
     "and m.marquee:find('吐酸泰坦'))"),
    ("find('[HUNTER SWARMS]',1,true)", "find('[追猎虫群]',1,true)"),
]
for english, chinese in pairs:
    assert english in text, "pattern not found: %s" % english[:40]
    text = text.replace(english, chinese)

text = text.replace("-- Panel tests", "-- Panel tests (zh-CN localised expectations)", 1)

# 合成字体：原来按“每字节 0.55em”，无法表示 CJK。改成按字符度量：
# ASCII 仍用原来的宽度表，多字节字符按 1em（真实字体里汉字≈一个字高）。
old_span = """local function span(t,size)
    local result=0
    local previous
    for c in t:gmatch('.') do
        result=result+size*(c=='W' and .9 or c=='I' and .25 or c==' ' and .3 or .55)
        if previous=='E' and c=='N' then result=result-.06*size end
        previous=c
    end
    return result
end"""
new_span = """local function span(t,size)
    local result=0
    local previous
    local i,n=1,#t
    while i<=n do
        local b=t:byte(i)
        if b<0x80 then
            local c=string.char(b)
            result=result+size*(c=='W' and .9 or c=='I' and .25 or c==' ' and .3 or .55)
            if previous=='E' and c=='N' then result=result-.06*size end
            previous=c
            i=i+1
        else
            -- multi-byte character (CJK): one em per glyph
            result=result+size
            previous=nil
            i=i+((b<0xE0 and 2) or (b<0xF0 and 3) or 4)
        end
    end
    return result
end"""
assert old_span in text, "span() model not found"
text = text.replace(old_span, new_span, 1)

# 这条断言按“字节下标”比较缓存 caret；中文必须按字符边界比较。
old_loop = """for i=1,#surface.metrics.text do
    assert(math.abs(surface.metrics.edges[i+1]-span(surface.metrics.text:sub(1,i),20*a.scale))<.001,
        'Cached repeated-cycle carets differ from full-prefix proportional font measurements')
end"""
new_loop = """local _starts={}
do
    local i,n=1,#surface.metrics.text
    while i<=n do
        _starts[#_starts+1]=i
        local b=surface.metrics.text:byte(i)
        i=i+((b<0x80 and 1) or (b<0xE0 and 2) or (b<0xF0 and 3) or 4)
    end
    _starts[#_starts+1]=#surface.metrics.text+1
end
for k=1,#_starts-1 do
    assert(math.abs(surface.metrics.edges[k+1]
        -span(surface.metrics.text:sub(1,_starts[k+1]-1),20*a.scale))<.001,
        'Cached repeated-cycle carets differ from full-prefix proportional font measurements')
end"""
assert old_loop in text, "byte-indexed caret assertion not found"
text = text.replace(old_loop, new_loop, 1)

with io.open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
print("wrote", dst, os.path.getsize(dst), "bytes")
