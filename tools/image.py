#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사진 한 장을 웹용(AVIF·WebP, 두 가지 크기)으로 변환합니다.

    python3 tools/image.py 원본사진.jpg prog-edu 1200
      → assets/img/prog-edu-1200.avif / .webp, prog-edu-600.avif / .webp

기존 이름을 쓰면 index.html 수정 없이 사진만 바뀝니다.
(단, 원본 가로가 지정 폭보다 작으면 원본 폭으로 저장되니 파일명 숫자를 확인하세요.)
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    src, name = sys.argv[1], sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    im = Image.open(src).convert("RGB")
    w0, h0 = im.size
    top = min(w0, cap)
    for w in sorted({top, max(320, top // 2)}, reverse=True):
        h = round(h0 * w / w0)
        r = im.resize((w, h), Image.LANCZOS)
        for ext, q in (("webp", 78), ("avif", 55)):
            out = os.path.join(ROOT, "assets", "img", f"{name}-{w}.{ext}")
            r.save(out, quality=q, **({"method": 6} if ext == "webp" else {}))
            print(f"{out}  {w}x{h}  {os.path.getsize(out)//1024}KB")

if __name__ == "__main__":
    main()
