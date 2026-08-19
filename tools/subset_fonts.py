#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""빌드된 사이트의 Pretendard 서브셋 폰트를 '실제 사용 글자'만 남기고 재서브셋."""
import os, re, sys, html, glob, shutil
from fontTools import subset
from fontTools.ttLib import TTFont

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(OUT, "assets/css/site.css")
FDIR = os.path.join(OUT, "assets/fonts")

# ── 1. 페이지에서 실제로 쓰이는 문자 수집 ──────────────────────────────
def text_of(path):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)

chars = set()
for f in ["index.html", "404.html", "50x.html", "site.webmanifest"]:
    p = os.path.join(OUT, f)
    if os.path.exists(p):
        chars |= set(text_of(p))

# 안전 여유분: 영숫자·기본 문장부호·자주 쓰는 기호
chars |= set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
chars |= set(" .,·!?%&()[]{}<>/\\|-–—_:;'\"“”‘’…*+=@#~^` ")
chars |= set("₩$€°㎡①②③④⑤※→←↑↓☎✓★☆")
chars = {c for c in chars if c.strip() or c == " "}
print(f"필요 글자 수: {len(chars)}")

# ── 2. @font-face 블록별로 재서브셋 ────────────────────────────────────
css = open(CSS, encoding="utf-8").read()
blocks = re.findall(r"@font-face\{[^}]*\}", css)
print(f"@font-face 블록: {len(blocks)}")

def parse_range(ur):
    cps = set()
    for tok in ur.split(","):
        tok = tok.strip().lower().replace("u+", "")
        if "-" in tok:
            a, b = tok.split("-")
            cps |= set(range(int(a, 16), int(b, 16) + 1))
        elif "?" in tok:
            a = int(tok.replace("?", "0"), 16); b = int(tok.replace("?", "f"), 16)
            cps |= set(range(a, b + 1))
        else:
            cps.add(int(tok, 16))
    return cps

need_cps = {ord(c) for c in chars}
kept, dropped, before, after = [], 0, 0, 0

for blk in blocks:
    m_src = re.search(r'url\("([^"]+)"\)', blk)
    m_ur = re.search(r"unicode-range:([^;}]+)", blk)
    if not m_src:
        kept.append(blk); continue
    rel = m_src.group(1)                      # ../fonts/pretendard-xxx.woff2
    path = os.path.normpath(os.path.join(os.path.dirname(CSS), rel))
    if not os.path.exists(path):
        kept.append(blk); continue
    blk_cps = parse_range(m_ur.group(1)) if m_ur else None
    want = need_cps & blk_cps if blk_cps else need_cps
    before += os.path.getsize(path)
    if not want:
        os.remove(path); dropped += 1; continue

    font = TTFont(path)
    have = set()
    for t in font["cmap"].tables:
        have |= set(t.cmap.keys())
    want &= have
    if not want:
        font.close(); os.remove(path); dropped += 1; continue

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = False
    opts.retain_gids = False
    opts.layout_features = ["kern", "liga", "clig", "calt", "ccmp", "locl", "mark", "mkmk", "rlig"]
    opts.name_IDs = ["*"]; opts.name_legacy = False; opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.drop_tables = ["FFTM", "PfEd", "TeX", "BASE", "JSTF", "DSIG"]
    opts.recalc_bounds = True
    s = subset.Subsetter(options=opts)
    s.populate(unicodes=want)
    s.subset(font)
    font.flavor = "woff2"
    font.save(path)
    font.close()

    # 새 unicode-range를 실제 남은 글자로 좁힘
    ranges = []
    for cp in sorted(want):
        if ranges and cp == ranges[-1][1] + 1:
            ranges[-1][1] = cp
        else:
            ranges.append([cp, cp])
    ur = ",".join(f"U+{a:x}" if a == b else f"U+{a:x}-{b:x}" for a, b in ranges)
    blk = re.sub(r"unicode-range:[^;}]+", "unicode-range:" + ur, blk)
    after += os.path.getsize(path)
    kept.append(blk)

# ── 3. CSS 재작성 ──────────────────────────────────────────────────────
new_css = css
for blk in blocks:
    new_css = new_css.replace(blk, "", 1)
new_css = "".join(kept) + new_css
open(CSS, "w", encoding="utf-8").write(new_css)

print(f"유지 {len(kept)}개 / 제거 {dropped}개")
print(f"폰트 용량 {before/1024:.0f}KB -> {after/1024:.0f}KB")
print(f"site.css {len(css)/1024:.1f}KB -> {len(new_css)/1024:.1f}KB")
