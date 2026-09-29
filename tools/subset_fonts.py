#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""페이지에 실제로 쓰인 글자만 남긴 웹폰트를 만듭니다.

HTML의 글자를 고치거나 새 문장을 넣었다면 이 스크립트를 한 번 실행하세요.
    pip3 install fonttools brotli
    python3 tools/subset_fonts.py

원본: tools/fonts-src/PretendardVariable.woff2, Anton-Regular.ttf (둘 다 SIL OFL)
결과: assets/fonts/pretendard.woff2, assets/fonts/anton.woff2
"""
import html, os, re
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "fonts-src")
OUT = os.path.join(ROOT, "assets", "fonts")
PAGES = ["index.html", "404.html", "50x.html"]


def page_text(path):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    # alt·aria-label 등 속성 글자도 화면낭독·대체표시에 쓰이므로 포함
    attrs = " ".join(re.findall(r'(?:alt|aria-label|title|placeholder)="([^"]*)"', s))
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s + " " + attrs)


def build(src, dst, chars, features):
    font = TTFont(src)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = features
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes={ord(c) for c in chars})
    sub.subset(font)
    font.flavor = "woff2"
    font.save(dst)
    return os.path.getsize(dst)


def main():
    os.makedirs(OUT, exist_ok=True)
    text = ""
    for p in PAGES:
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            text += page_text(fp)

    # 여유분: 영숫자·문장부호 전체 (문구 수정 시 깨짐 방지)
    safety = "".join(chr(c) for c in range(0x20, 0x7F)) + "·—–…“”‘’→←↑↓↗●○※©"
    kor = set(text) | set(safety)
    kor = {c for c in kor if c.isprintable()}

    n1 = build(os.path.join(SRC, "PretendardVariable.woff2"), os.path.join(OUT, "pretendard.woff2"),
               kor, ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "case"])
    latin = "".join(chr(c) for c in range(0x20, 0x7F))
    n2 = build(os.path.join(SRC, "Anton-Regular.ttf"), os.path.join(OUT, "anton.woff2"), latin, ["kern", "liga"])

    print(f"Pretendard: {len(kor)}자 → {n1/1024:.0f}KB")
    print(f"Anton: 라틴 → {n2/1024:.0f}KB")


if __name__ == "__main__":
    main()
