#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대한장애인드론축구협회 — 번들 HTML을 배포용 정적 사이트로 변환."""
import json, os, re, base64, shutil, hashlib, io, sys
from PIL import Image, ImageDraw

# 사용법: python3 tools/build.py [원본_번들.html]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(ROOT)
OUT = ROOT
# 배포 주소. 커스텀 도메인(www.kpdsa.or.kr) 연결 후에는 이 한 줄만 바꾸면
# canonical·OG·sitemap·robots·구조화데이터가 한꺼번에 따라갑니다.
SITE = "https://gachinalja.co.kr"

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    src = None
    for f in sorted(os.listdir(SRC_DIR)):
        if f.endswith(".html") and "최종" in f:
            src = os.path.join(SRC_DIR, f)
assert src and os.path.exists(src), "원본 번들 HTML을 찾을 수 없습니다. 경로를 인자로 넘겨주세요."

lines = open(src, encoding="utf-8").read().split("\n")
manifest = json.loads(lines[374])
tpl = json.loads(lines[386])

# 생성 대상 디렉터리만 정리 — README, tools/, .git 등 수작업 파일은 보존
for _d in ["assets/img", "assets/fonts", "assets/css", "assets/js"]:
    _p = os.path.join(OUT, _d)
    if os.path.exists(_p):
        shutil.rmtree(_p)
for d in ["assets/img", "assets/fonts", "assets/css", "assets/js", ".github/workflows"]:
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

# ─────────────────────────────────────────────────────────── 1. 폰트 추출
font_map = {}
fi = 0
for uuid, e in manifest.items():
    if e["mime"].startswith("font/"):
        fi += 1
        name = f"pretendard-{fi:03d}.woff2"
        with open(os.path.join(OUT, "assets/fonts", name), "wb") as fh:
            fh.write(base64.b64decode(e["data"]))
        font_map[uuid] = f"../fonts/{name}"
print(f"fonts: {fi}")

# ─────────────────────────────────────────────────────────── 2. 이미지 처리
ROLES = {
    "16bd702d-ff2a-4841-a95b-d76ee1f85168": ("hero",    1920, "100vw"),
    "ce1c9a5c-6979-4ce6-b53c-6578559001eb": ("belief",  1600, "100vw"),
    "fe061a2b-de3c-4f9a-bfec-06564f331340": ("prog-edu",        1200, "(max-width:960px) 100vw, 50vw"),
    "c6e1daa0-387d-4ff5-9425-5be64aadfb65": ("prog-event",      1200, "(max-width:960px) 100vw, 50vw"),
    "8c4a81f9-94b4-4918-a3b6-293d269ada9a": ("prog-tournament", 1200, "(max-width:960px) 100vw, 50vw"),
    "fee5ce59-666d-4508-a200-7cc54d5745e3": ("prog-coach",      1200, "(max-width:960px) 100vw, 50vw"),
    "6438128d-b4ab-4f37-b816-c871be18c3a9": ("vm-vision",  1200, "(max-width:960px) 100vw, 50vw"),
    "14e343da-9575-4a0e-8726-c33851e89eab": ("vm-mission", 1200, "(max-width:960px) 100vw, 50vw"),
    "d14d5cb6-6adf-4804-b547-cb8764616705": ("g-match",      900, "(max-width:860px) 50vw, 25vw"),
    "2807e4b1-ab52-477b-8d17-c2c73f55a23c": ("g-training",   900, "(max-width:860px) 50vw, 25vw"),
    "c001aea6-06a8-4dbc-8f58-1d4702203187": ("g-event",      900, "(max-width:860px) 50vw, 25vw"),
    "f93fb238-5666-4de5-8e59-6a77e6597be3": ("g-group",      900, "(max-width:860px) 50vw, 25vw"),
    "7738bd51-5acd-40ba-832d-4265347ffdf3": ("g-award",      900, "(max-width:860px) 50vw, 25vw"),
    "8897f564-9100-471b-82a0-3ba64f744813": ("g-tournament", 900, "(max-width:860px) 50vw, 25vw"),
    "1903eba2-414f-4aa8-9a7b-335b1fb94607": ("g-booth",      900, "(max-width:860px) 50vw, 25vw"),
    "1f895eba-b9d8-4051-a1f3-338c4a3837d9": ("g-edu",        900, "(max-width:860px) 50vw, 25vw"),
}

img_info = {}   # uuid -> dict(webp=[(path,w)], avif=[...], w, h)
for uuid, e in manifest.items():
    if not e["mime"].startswith("image/"):
        continue
    role, cap, sizes = ROLES.get(uuid, (uuid[:8], 1200, "100vw"))
    # photos/<역할>.jpg|jpeg|png 가 있으면 번들 사진 대신 그 파일을 씁니다.
    _ov = None
    for _ext in (".jpg", ".jpeg", ".png", ".webp"):
        _c = os.path.join(OUT, "photos", role + _ext)
        if os.path.exists(_c):
            _ov = _c
            break
    if _ov:
        im = Image.open(_ov)
        print(f"  [교체] {role} <- photos/{os.path.basename(_ov)}")
    else:
        im = Image.open(io.BytesIO(base64.b64decode(e["data"])))
    im = im.convert("RGB")
    ow, oh = im.size
    widths = sorted({min(ow, cap), max(320, min(ow, cap) // 2)}, reverse=True)
    out = {"sizes": sizes, "role": role, "webp": [], "avif": []}
    for w in widths:
        h = round(oh * w / ow)
        r = im.resize((w, h), Image.LANCZOS)
        for fmt, q in (("webp", 78), ("avif", 55)):
            fn = f"{role}-{w}.{fmt}"
            r.save(os.path.join(OUT, "assets/img", fn), quality=q, method=6 if fmt == "webp" else None)
            out[fmt].append((f"assets/img/{fn}", w))
    out["w"], out["h"] = widths[0], round(oh * widths[0] / ow)
    img_info[uuid] = out
    print(f"  img {role}: {ow}x{oh} -> {widths}")

# OG 이미지 (1200x630) — 공식 로고 중심 카드
# 사진 위 작은 로고는 카톡·SNS 썸네일에서 뭉개져서, 로고를 크게 쓰는 편이 잘 읽힙니다.
_OGW, _OGH = 1200, 630
og = Image.new("RGB", (_OGW, _OGH), (255, 255, 255))
_dg = ImageDraw.Draw(og)
for _y in range(_OGH):                       # 아주 옅은 세로 그라데이션
    _t = _y / _OGH
    _dg.line([(0, _y), (_OGW, _y)],
             fill=(round(255 - 12 * _t), round(255 - 8 * _t), round(255 - 3 * _t)))
_dg.rectangle([0, _OGH - 10, _OGW, _OGH], fill=(20, 51, 95))   # 하단 브랜드 바

EMBLEM_SRC = os.path.join(OUT, "brand", "06_협회엠블럼", "엠블럼_마스터_1398px.png")
assert os.path.exists(EMBLEM_SRC), f"엠블럼 원본을 찾을 수 없습니다: {EMBLEM_SRC}"
EMBLEM = Image.open(EMBLEM_SRC).convert("RGBA")

_e = EMBLEM.resize((470, 470), Image.LANCZOS)
og = og.convert("RGBA")
og.alpha_composite(_e, ((_OGW - 470) // 2, (_OGH - 10 - 470) // 2))
og = og.convert("RGB")
og.save(os.path.join(OUT, "og-image.jpg"), quality=88, optimize=True, progressive=True)
print("og-image: 협회 엠블럼")

# ─────────────────────────────────────────────────────────── 3. 파비콘 / 앱 아이콘
# 협회 공식 엠블럼(원형 크레스트)으로 생성합니다.
def _icon(size, inner_ratio=0.92, bg=(255, 255, 255)):
    """흰 바탕에 엠블럼을 얹은 정사각 아이콘."""
    im = Image.new("RGBA", (size, size), bg + (255,))
    d = round(size * inner_ratio)
    e = EMBLEM.resize((d, d), Image.LANCZOS)
    im.alpha_composite(e, ((size - d) // 2, (size - d) // 2))
    return im

def _save_png(im, name, colors=192):
    """사진이 아닌 로고이므로 팔레트로 줄여 용량을 크게 낮춥니다."""
    q = im.convert("RGBA").quantize(colors=colors, method=Image.FASTOCTREE)
    q.save(os.path.join(OUT, name), optimize=True)

_icon(180).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
_save_png(_icon(192), "icon-192.png")
_save_png(_icon(512), "icon-512.png", colors=224)
# maskable 은 바깥 20%가 잘릴 수 있어 안전영역(72%)에 맞춰 축소
_save_png(_icon(512, inner_ratio=0.72), "icon-512-maskable.png", colors=224)
_icon(64).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# 헤더·푸터 로고 — 투명 WebP (PNG 대비 1/5 수준)
_em = EMBLEM.resize((256, 256), Image.LANCZOS)
_em.save(os.path.join(OUT, "assets/img/emblem-256.webp"), quality=88, method=6)
_save_png(_em, "assets/img/emblem-256.png")   # 구형 브라우저 대비

# 이전 벡터 파비콘은 엠블럼을 벡터로 변환할 수 없어 사용하지 않습니다.
_old_svg = os.path.join(OUT, "favicon.svg")
if os.path.exists(_old_svg):
    os.remove(_old_svg)
print("icons: 협회 엠블럼으로 생성 (favicon.svg 제거)")

# 헤더·푸터·오류페이지 로고 마크업
EMBLEM_IMG = ('<picture style="flex:none;display:block;width:{px}px;height:{px}px">'
              '<source type="image/webp" srcset="assets/img/emblem-256.webp">'
              '<img src="assets/img/emblem-256.png" alt="" width="256" height="256" '
              'style="width:{px}px;height:{px}px;display:block" '
              'aria-hidden="true" decoding="async"></picture>')

# ─────────────────────────────────────────────────────────── 4. 템플릿 → 정적 HTML
body = tpl.split("<body>", 1)[1].rsplit("</body>", 1)[0]

# 4-1. helmet 안의 <style> 수집, 런타임 스크립트/preconnect 제거
helmet = re.search(r"<helmet>(.*?)</helmet>", body, re.S).group(1)
css_blocks = re.findall(r"<style>(.*?)</style>", helmet, re.S)
body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
body = re.sub(r'<script src="[0-9a-f-]{36}"></script>', "", body)
body = re.sub(r'<script type="text/x-dc".*?</script>', "", body, flags=re.S)
body = body.replace("<x-dc>", "").replace("</x-dc>", "")

# 4-2. 커스텀 속성 → 표준 속성
body = body.replace("sc-camel-view-box=", "viewBox=")
body = body.replace("sc-camel-preserve-aspect-ratio=", "preserveAspectRatio=")

# 4-3. sc-if 정적 해석 (기본 props: 교육·체험 중심 / 갤러리 ON / 드론 애니 ON)
def unwrap(var):
    global body
    p = re.compile(r'<sc-if value="\{\{ ' + var + r' \}\}"[^>]*>(.*?)</sc-if>', re.S)
    body = p.sub(lambda m: m.group(1), body)

def drop(var):
    global body
    p = re.compile(r'<sc-if value="\{\{ ' + var + r' \}\}"[^>]*>.*?</sc-if>', re.S)
    body = p.sub("", body)

# 모바일 메뉴는 JS로 토글되는 실제 요소로 승격
body = re.sub(
    r'<sc-if value="\{\{ menuOpen \}\}"[^>]*>\s*<div style="',
    '<div id="mobileNav" hidden style="', body, flags=re.S)
body = body.replace("협력·문의</a>\n    </div>\n  </sc-if>", "협력·문의</a>\n    </div>")
body = body.replace("</sc-if>\n</header>", "</header>")
drop("sponsorFirst")
unwrap("eduFirst"); unwrap("showGallery"); unwrap("droneAnim")
assert "sc-if" not in body, "sc-if 잔여"

# 4-4. 이벤트 핸들러 속성 제거 (JS에서 위임 처리)
body = body.replace(' sc-camel-on-click="{{ toggleMenu }}"', "")
body = body.replace(' sc-camel-on-click="{{ closeMenu }}"', "")

# 4-5. 메뉴 버튼 접근성 속성
body = body.replace(
    '<button id="hdrMenuBtn" data-mq-show=""',
    '<button id="hdrMenuBtn" type="button" data-mq-show="" aria-expanded="false" aria-controls="mobileNav"')

# 4-6. image-slot → <picture>
def picture_for(uuid, alt, extra_style="", eager=False, cls=""):
    info = img_info[uuid]
    avif = ", ".join(f"{p} {w}w" for p, w in info["avif"])
    webp = ", ".join(f"{p} {w}w" for p, w in info["webp"])
    fallback = info["webp"][0][0]
    load = 'loading="eager" fetchpriority="high" decoding="async"' if eager \
        else 'loading="lazy" decoding="async"'
    style = "width:100%;height:100%;object-fit:cover;display:block;" + extra_style
    return (f'<picture>'
            f'<source type="image/avif" srcset="{avif}" sizes="{info["sizes"]}">'
            f'<source type="image/webp" srcset="{webp}" sizes="{info["sizes"]}">'
            f'<img src="{fallback}" alt="{alt}" width="{info["w"]}" height="{info["h"]}" '
            f'{load} style="{style}"{cls}></picture>')

def slot_repl(m):
    tag = m.group(0)
    uuid = re.search(r'src="([0-9a-f-]{36})"', tag).group(1)
    ph = re.search(r'placeholder="([^"]*)"', tag)
    alt = ph.group(1) if ph else ""
    sid = re.search(r'id="([^"]*)"', tag).group(1)
    if sid == "belief-bg":
        alt = ""   # 장식용 배경 (부모가 aria-hidden)
    else:
        alt = f"{alt} — 대한장애인드론축구협회" if alt else "대한장애인드론축구협회 활동 사진"
    radius = re.search(r'radius="(\d+)"', tag)
    extra = f"border-radius:{radius.group(1)}px;" if radius else ""
    return picture_for(uuid, alt, extra)

body = re.sub(r'<image-slot[^>]*></image-slot>', slot_repl, body)
assert "image-slot" not in body
assert "x-dc" not in body

# 4-7. 히어로 <img src=uuid> → <picture> (LCP: eager + preload)
hero_uuid = "16bd702d-ff2a-4841-a95b-d76ee1f85168"
body = re.sub(
    r'<img src="' + hero_uuid + r'"[^>]*>',
    picture_for(hero_uuid, "", "position:absolute;inset:0;object-position:center;", eager=True),
    body)
# picture 자체가 absolute 컨텍스트를 갖도록 래핑 보정
body = body.replace(
    '<picture><source type="image/avif" srcset="' + img_info[hero_uuid]["avif"][0][0],
    '<picture class="hero-bg" aria-hidden="true"><source type="image/avif" srcset="'
    + img_info[hero_uuid]["avif"][0][0], 1)

# 4-8. style-hover="..." → CSS 클래스
hover_rules = []
def hover_repl(m):
    decl = m.group(1)
    idx = len(hover_rules) + 1
    cls = f"hv{idx}"
    hover_rules.append((cls, decl))
    return f' data-hv="{cls}"'
body = re.sub(r'\sstyle-hover="([^"]*)"', hover_repl, body)

# 4-9. hv 클래스를 class 속성으로 이동
def hv_to_class(m):
    tag = m.group(0)
    cls = re.search(r'data-hv="(hv\d+)"', tag).group(1)
    tag = re.sub(r'\sdata-hv="hv\d+"', "", tag)
    if re.search(r'\sclass="([^"]*)"', tag):
        tag = re.sub(r'\sclass="([^"]*)"', lambda mm: f' class="{mm.group(1)} {cls}"', tag)
    else:
        tag = tag[:-1].rstrip() + f' class="{cls}">'
    return tag
body = re.sub(r'<[a-zA-Z][^>]*data-hv="hv\d+"[^>]*>', hv_to_class, body)
assert "data-hv" not in body and "style-hover" not in body

# 4-10. 색 대비 보정 (WCAG AA)
CONTRAST_FIX = [
    ("rgba(255,255,255,.48)", "rgba(255,255,255,.72)"),
    ("rgba(255,255,255,.5)",  "rgba(255,255,255,.72)"),
    ("rgba(255,255,255,.55)", "rgba(255,255,255,.75)"),
    ("rgba(255,255,255,.62)", "rgba(255,255,255,.78)"),
    ("rgba(255,255,255,.66)", "rgba(255,255,255,.82)"),
    ("opacity:.58", "opacity:.78"),
    ("opacity:.62", "opacity:.8"),
]
for a, b in CONTRAST_FIX:
    body = body.replace(a, b)

# 밝은 배경 위 텍스트 색 대비 보정 (WCAG AA 4.5:1)
body = body.replace("color:#D65A45", "color:#C4472F")   # RED TEAM 라벨 3.88 -> 4.90
body = body.replace("color:#8494A9", "color:#66738A")   # 아레나 캡션 3.09 -> 4.79

# story 섹션(#F5F7FA)의 연한 파랑 번호는 브랜드 블루로 (2.04 -> 5.05)
_i = body.index('<section id="story"')
_j = body.index('<section id="gallery"')
body = body[:_i] + body[_i:_j].replace("color:#8FB2DE", "color:#2F6BB3") + body[_j:]

# 4-10b. dbr 줄바꿈이 숨겨질 때 단어가 붙는 문제 — 공백 보강
body = body.replace('<br class="dbr">', '<br class="dbr"> ')

# 4-10c. 헤딩 레벨 정규화 — 비전·미션 h4(6개)는 h2 바로 아래이므로 h3로 승격
body = body.replace("<h4 ", "<h3 ").replace("</h4>", "</h3>")

# 4-10e. 포인트 컬러(코랄) 도입 — 파랑 일변도에서 벗어나 액션·라벨에 강조
#   ACC      #D23A18  버튼 채움 / 흰 배경 위 텍스트  (흰글자 4.82:1, 흰배경 4.82:1)
#   ACC_SOFT #C8360F  회색(#F5F7FA) 배경 위 작은 텍스트 (4.90:1)
#   ACC_LITE #FF8A6E  네이비 배경 위 텍스트           (5.46:1)
ACC, ACC_SOFT, ACC_LITE = "#D23A18", "#C8360F", "#FF8A6E"

# (a) 섹션 머리말 라벨 — 밝은 섹션 6곳
body = body.replace("letter-spacing:.16em;color:#2F6BB3;text-transform:uppercase",
                    f"letter-spacing:.16em;color:{ACC_SOFT};text-transform:uppercase")
# (b) 섹션 머리말 라벨 — 어두운 Contact 섹션
body = body.replace("letter-spacing:.16em;color:#8FB2DE;text-transform:uppercase",
                    f"letter-spacing:.16em;color:{ACC_LITE};text-transform:uppercase")
# (c) PROGRAM 01~04 라벨 (회색 카드 위)
body = body.replace('letter-spacing:.14em;color:#2F6BB3">PROGRAM',
                    f'letter-spacing:.14em;color:{ACC_SOFT}">PROGRAM')
# (d) 비전·미션 번호 01/02/03 (회색 배경 위)
body = body.replace('color:#2F6BB3;padding-top:3px">',
                    f'color:{ACC_SOFT};padding-top:3px">')
# (e) 문의 카드 화살표 (네이비 배경 위)
for _t in ["전화 걸기", "메일 보내기", "블로그 방문"]:
    body = body.replace(f'color:#8FB2DE">{_t}', f'color:{ACC_LITE}">{_t}')
# (f) RED TEAM 라벨은 팀 색이라 포인트 컬러와 분리해 그대로 둡니다.

# (g) 히어로 헤드라인 — "성장합니다" 강조
_h1_old = "같이 웃고,<br>같이 성장합니다.</h1>"
assert _h1_old in body, "히어로 h1 패턴 불일치"
body = body.replace(_h1_old,
                    f'같이 웃고,<br>같이 <span class="a-h1" style="color:{ACC_LITE}">성장합니다</span>.</h1>', 1)

# (h) 헤더 CTA — 흰 알약에서 코랄 채움으로
_hdr_old = 'style="font-size:14px;font-weight:700;color:#14335F;background:#fff;padding:12px 24px'
assert _hdr_old in body, "헤더 CTA 패턴 불일치"
body = body.replace(_hdr_old,
                    f'style="font-size:14px;font-weight:700;color:#fff;background:{ACC};padding:12px 24px', 1)
body = body.replace('border-radius:999px;transition:transform .2s,background .3s,color .3s;box-shadow:0 4px 16px rgba(0,0,0,.14)',
                    'border-radius:999px;transition:transform .2s,background .3s,color .3s;box-shadow:0 4px 16px rgba(210,58,24,.34)', 1)

# (i) 히어로 1차 CTA — 흰 버튼에서 코랄 버튼으로
_cta_old = 'box-sizing:border-box;background:#fff;color:#14335F;box-shadow:0 8px 28px rgba(0,0,0,.24)'
assert _cta_old in body, "히어로 CTA 패턴 불일치"
body = body.replace(_cta_old,
                    f'box-sizing:border-box;background:{ACC};color:#fff;box-shadow:0 8px 28px rgba(210,58,24,.38)', 1)

# (j) 파트너 점선 CTA
body = body.replace('border:1.5px dashed #BFCCDD;border-radius:16px;padding:26px 36px;color:#2F6BB3;',
                    f'border:1.5px dashed #E6B4A6;border-radius:16px;padding:26px 36px;color:{ACC_SOFT};', 1)

# 4-10e2. 히어로 태그라인을 조각별로 감싸 모바일에서 따로 제어
_tag_old = ('<span style="width:32px;height:1.5px;background:rgba(255,255,255,.32)"></span>'
            '<b style="color:#fff;font-weight:800;font-size:clamp(17px,1.9vw,21px);'
            'letter-spacing:-.01em">가치날자</b> — 같이 날자, 가치있게 날자 · Fly together, Play together')
_tag_new = ('<span class="hero-tag-line" style="width:32px;height:1.5px;'
            'background:rgba(255,255,255,.32)"></span>'
            '<b style="color:#fff;font-weight:800;font-size:clamp(17px,1.9vw,21px);'
            'letter-spacing:-.01em">가치날자</b>'
            '<span class="hero-tag-txt"><span class="hero-tag-dash">— </span>'
            '같이 날자, 가치있게 날자 · Fly together, Play together</span>')
assert _tag_old in body, "히어로 태그라인 패턴 불일치"
body = body.replace(_tag_old, _tag_new, 1)

# 4-10f. 모바일 전용 클래스 부여 (데스크톱 스타일은 건드리지 않음)
def _add_class(sig, cls):
    global body
    def _rep(m):
        tag = m.group(0)
        if 'class="' in tag:
            return re.sub(r'class="([^"]*)"',
                          lambda mm: f'class="{mm.group(1)} {cls}"', tag, count=1)
        return tag[:-1].rstrip() + f' {cls and chr(99)}lass="{cls}">'
    n = len(re.findall(r'<[a-zA-Z][^>]*' + re.escape(sig) + r'[^>]*>', body))
    assert n > 0, f"모바일 클래스 대상 없음: {sig[:50]}"
    body = re.sub(r'<[a-zA-Z][^>]*' + re.escape(sig) + r'[^>]*>', _rep, body)
    return n

_counts = {
    "m-sec":      _add_class("style=\"padding:120px 0", "m-sec"),
    "m-sec2":     _add_class("background:#0E2749;color:#fff;padding:130px 0", "m-sec"),
    "m-card":     _add_class("background:#F5F7FA;border:1px solid transparent;border-radius:18px", "m-card"),
    "m-cardimg":  _add_class('style="height:240px;flex:none"', "m-cardimg"),
    "m-cardbody": _add_class("padding:34px 38px 38px", "m-cardbody"),
    "m-card2":    _add_class("background:#fff;border:1px solid #E4EAF1;border-radius:18px;padding:40px 32px", "m-card2"),
    "m-card3":    _add_class("background:#fff;border:1px solid #E4EAF1;border-radius:16px;padding:30px 32px", "m-card3"),
    "m-card4":    _add_class("background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.13);border-radius:18px;padding:36px 32px", "m-card4"),
    "hero-copy":  _add_class("max-width:620px;text-align:left;margin-left:24px", "hero-copy"),
    "hero-cta":   _add_class("display:flex;gap:12px;margin-top:44px;flex-wrap:wrap", "hero-cta"),
    "hero-tag":   _add_class("margin:60px 0 0;display:flex;align-items:center;gap:14px", "hero-tag"),
    "hero-scrim": _add_class("background:linear-gradient(90deg,#0C2140 0%", "hero-scrim"),
    "hero-eyebrow": _add_class("letter-spacing:.24em;color:rgba(255,255,255,.72);text-transform:uppercase", "hero-eyebrow"),
    # 포인트 컬러 요소 — 모바일에서 브랜드 블루로 되돌리기 위한 표식
    "a-soft":  _add_class(f"color:{ACC_SOFT}", "a-soft"),
    "a-lite":  _add_class(f"color:{ACC_LITE}", "a-lite"),
    "a-fill":  _add_class(f"background:{ACC};color:#fff", "a-fill"),
    "a-dash":  _add_class("dashed #E6B4A6", "a-dash"),
    # 갤러리 타일 (호버 확대용)
    "gal-item": _add_class("min-width:0", "gal-item"),

    # ── 모바일 콘텐츠 압축용 (아래 전부 데스크톱 스타일에는 영향 없음) ──
    # value: 교육/체험/성장 카드
    "m-icon-box": _add_class('background:#F5F7FA;display:grid;place-items:center;color:#2F6BB3', "m-icon-box"),
    "m-body-p":   _add_class('font-size:17px;line-height:1.9;color:#44546A;max-width:56ch', "m-body-p"),

    # about: 드론축구란 상세 리스트(경기 방식/팀 경기/통합 스포츠)
    "m-about-rows": _add_class('style="margin-top:34px"', "m-about-rows"),
    "m-diagram":    _add_class('role="img" aria-label="드론축구 경기장 다이어그램', "m-diagram"),
    "m-arena":      _add_class('border-radius:14px;border:1.5px dashed #C7D3E2', "m-arena"),
    "m-team-row":   _add_class('display:flex;align-items:center;justify-content:space-between;margin-bottom:24px', "m-team-row"),

    # story: 비전·미션 6개 항목 + 이미지 + 배지줄 + 구분선 + 하단 CTA
    "m-story-row": _add_class('gap:18px;padding:24px 0', "m-story-row"),
    "m-vm-img":    _add_class('min-height:clamp(300px,38vw,460px)', "m-vm-img"),
    "m-badge-vision":  _add_class('letter-spacing:.18em;color:#2F6BB3;margin:0 0 28px', "m-badge-row"),
    "m-badge-mission": _add_class('letter-spacing:.18em;color:#14335F;margin:0 0 28px', "m-badge-row"),
    "m-divider-lg": _add_class('gap:16px;margin:clamp(80px,9vw,120px) 0', "m-divider-lg"),
    "m-cta-card":   _add_class('margin-top:56px;display:flex;align-items:center;justify-content:space-between', "m-cta-card"),

    # programs: 카드 제목 · 대상 라인
    "m-h3-lg":    _add_class('font-size:24px;font-weight:700;color:#14335F;letter-spacing:-.02em', "m-h3-lg"),
    "m-tag-line": _add_class('border-top:1px dashed #D5DEE9', "m-tag-line"),

    # 그리드 상단 여백 공통 압축
    "m-grid-top-56": _add_class("margin-top:56px", "m-grid-top-56"),
    "m-grid-top-64": _add_class("margin-top:64px", "m-grid-top-64"),
}
print("모바일 클래스:", _counts)

# 4-10d2. 헤더·푸터 로고를 협회 엠블럼 이미지로 교체
_mark_old = ('<svg viewBox="0 0 100 100" style="width:34px;height:34px;flex:none;color:#8FB2DE" '
             'aria-hidden="true"><use href="#logomark"></use></svg>')
assert body.count(_mark_old) == 2, f"로고 마크 개수 불일치: {body.count(_mark_old)}"
body = body.replace(_mark_old, EMBLEM_IMG.format(px=40))

# 더 이상 쓰이지 않는 logomark 정의 제거
body = re.sub(r'<g id="logomark">.*?</g>\s*', "", body, flags=re.S)
assert "logomark" not in body

# 4-11. <main> 랜드마크
body = body.replace('<a class="skip-link" href="#value">본문 바로가기</a>',
                    '<a class="skip-link" href="#main">본문 바로가기</a>')
body = body.replace('<section id="top"', '<main id="main">\n<section id="top"', 1)
body = body.replace("<footer ", "</main>\n<footer ", 1)

# 4-12. 외부 링크 안전화
body = body.replace('target="_blank" rel="noopener"', 'target="_blank" rel="noopener noreferrer"')

# 4-13. 폰트 uuid → 로컬 경로
font_css = css_blocks[0]
for uuid, path in font_map.items():
    font_css = font_css.replace(f'url("{uuid}")', f'url("{path}")')
font_css = re.sub(r"/\*.*?\*/", "", font_css, flags=re.S).strip()
assert "url(\"" in font_css and not re.search(r'url\("[0-9a-f-]{36}"\)', font_css)

leftover = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", body)
assert not leftover, f"uuid 잔여: {set(leftover)}"

# ─────────────────────────────────────────────────────────── 5. CSS
base_css = css_blocks[1].strip()
extra_css = """
.skip-link{position:absolute;left:-9999px;top:0;z-index:999;background:#14335F;color:#fff;padding:12px 20px;border-radius:0 0 10px 0;font-weight:700}
.skip-link:focus{left:0}
a:focus-visible,button:focus-visible{outline:3px solid #2F6BB3;outline-offset:3px;border-radius:6px}
#mobileNav[hidden]{display:none!important}
.hero-bg{position:absolute;inset:0;display:block}
picture{display:block;width:100%;height:100%}
@media (max-width:900px){br.dbr{display:none}}
img{max-width:100%}
footer a{display:inline-block;padding:5px 2px;min-height:24px}
#hdrLinks a{display:inline-block;padding:9px 2px}
@media print{#siteHeader,#mobileNav{display:none!important}[data-reveal]{opacity:1!important;transform:none!important}body{color:#000}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}}


/* ── 히어로 진입 ── */
@keyframes heroUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
.hero-copy>*{animation:heroUp .85s cubic-bezier(.22,.61,.36,1) both}
.hero-copy>*:nth-child(1){animation-delay:.06s}
.hero-copy>*:nth-child(2){animation-delay:.14s}
.hero-copy>*:nth-child(3){animation-delay:.24s}
.hero-copy>*:nth-child(4){animation-delay:.34s}
.hero-copy>*:nth-child(5){animation-delay:.44s}

/* ── 모바일 메뉴 슬라이드 ── */
@keyframes navDrop{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:none}}
#mobileNav:not([hidden]){animation:navDrop .28s cubic-bezier(.22,.61,.36,1) both}

/* ── 이미지 호버 확대 (마우스 환경만) ── */
.gal-item{overflow:hidden;border-radius:14px}
@media (hover:hover){
  .m-card picture img,.gal-item img{transition:transform .8s cubic-bezier(.22,.61,.36,1)}
  .m-card:hover picture img,.gal-item:hover img{transform:scale(1.06)}
  .m-card4 p:last-child{transition:transform .3s ease}
  .m-card4:hover p:last-child{transform:translateX(6px)}
}

/* ── 버튼 누름 반응 ── */
.hero-cta a:active,#hdrCta:active{transform:translateY(1px) scale(.985)}
"""
hover_rules = [(c, d.replace("border-color:#2F6BB3", "border-color:#D23A18")) for c, d in hover_rules]
MOBILE_CSS = """
/* ── 모바일 전용 (≤960px). 데스크톱 레이아웃에는 영향 없음 ── */
@media (max-width:960px){
  body{line-height:1.72}

  /* 섹션 여백 압축 + 밝은 섹션 대비를 조금 더 줘서 구획이 보이게 */
  .m-sec{padding-top:72px!important;padding-bottom:72px!important}
  #about,#story,#partner{background:#EDF2F8!important}

  /* 히어로 — 왼쪽 정렬, 군더더기 제거 */
  #top{padding:112px 0 76px!important;min-height:auto!important}
  .hero-copy{max-width:100%!important;margin-left:0!important;margin-right:0!important;text-align:left!important}
  .hero-eyebrow{display:none!important}   /* 영문 협회명 — 모바일에서는 생략 */
  .hero-scrim{background:linear-gradient(180deg,rgba(9,24,47,.74) 0%,rgba(9,24,47,.56) 42%,rgba(9,24,47,.88) 100%)!important}
  .hero-copy > p{font-size:15.5px!important;margin-top:20px!important}

  /* 버튼 — 내용 폭에 맞춰 작게, 왼쪽 정렬 */
  .hero-cta{flex-direction:row!important;justify-content:flex-start!important;align-items:center!important;gap:8px!important;margin-top:26px!important}
  .hero-cta a{width:auto!important;max-width:none!important;font-size:14px!important;
    padding:12px 20px!important;min-height:44px!important;justify-content:center!important}

  /* 포인트 컬러는 모바일에서 사용하지 않음 — 브랜드 블루로 복귀 */
  .a-soft{color:#2F6BB3!important}
  .a-lite{color:#8FB2DE!important}
  .a-h1{color:#fff!important}
  .a-fill{background:#fff!important;color:#14335F!important;
    box-shadow:0 8px 28px rgba(0,0,0,.24)!important}
  .a-dash{border-color:#BFCCDD!important;padding:16px 20px!important;font-size:13.5px!important}
  #hdrCta{box-shadow:0 4px 16px rgba(0,0,0,.14)!important}

  /* 태그라인 — 장식 대시는 빼고 두 줄로 */
  .hero-tag{display:block!important;margin-top:30px!important;font-size:14px!important;line-height:1.6!important}
  .hero-tag-line,.hero-tag-dash{display:none!important}
  .hero-tag b{display:block!important;font-size:16px!important;margin-bottom:1px!important}
  .hero-tag-txt{display:block!important}

  /* 카드 경계를 또렷하게 — 배경만으로는 구분이 안 됨 */
  .m-card{background:#fff!important;border-color:#D6E0EC!important;box-shadow:0 2px 12px rgba(20,51,95,.07)!important}
  .m-cardimg{height:150px!important}
  .m-cardbody{padding:16px 18px 18px!important;gap:6px!important}
  .m-card2{padding:22px 20px!important;border-color:#D6E0EC!important}
  .m-card3{padding:20px 18px!important;border-color:#D6E0EC!important}
  .m-card4{padding:20px 18px!important;background:rgba(255,255,255,.07)!important;border-color:rgba(255,255,255,.2)!important}
  .m-card3 b{font-size:15.5px!important}
  .m-card3 small{display:block!important;font-size:13.5px!important;margin-top:6px!important;line-height:1.55!important}
  .m-card4 p:first-child{margin-bottom:8px!important}
  .m-card4 p:nth-child(3){margin-top:6px!important;font-size:12.5px!important}
  .m-card4 p:last-child{margin-top:10px!important}

  /* ── 콘텐츠 밀도 압축 (가치/드론축구란/비전미션/사업 카드) ── */
  .m-grid-top-56{margin-top:28px!important}
  .m-grid-top-64{margin-top:32px!important}

  /* value 카드 — 아이콘 축소, 여백 압축 */
  .m-icon-box{width:38px!important;height:38px!important;border-radius:11px!important;margin-bottom:12px!important}
  .m-icon-box svg{width:18px!important;height:18px!important}
  .m-card2 h3{font-size:17px!important;margin-bottom:6px!important}
  .m-body-p{font-size:14.5px!important;line-height:1.6!important}

  /* about — 드론축구란 상세 리스트 */
  .m-about-rows>div{padding:14px 0!important;gap:14px!important}
  .m-about-rows b{font-size:13px!important;width:78px!important}
  .m-about-rows span{font-size:14px!important;line-height:1.6!important}
  .m-diagram{padding:20px 18px!important}
  .m-arena{height:180px!important}
  .m-diagram p{margin-top:10px!important;font-size:12px!important}
  .m-team-row{margin-bottom:14px!important}
  .m-team-row span:nth-child(2){display:none!important}   /* "DRONE SOCCER ARENA" 캡션 — 좁은 화면에서 줄바꿈 유발, 장식 요소라 생략 */
  .m-team-row span{font-size:11.5px!important;letter-spacing:.08em!important}

  /* story — 비전·미션 이미지·항목·구분선·CTA */
  .m-vm-img{min-height:170px!important}
  .m-badge-row{margin-bottom:14px!important}
  .m-story-row{padding:14px 0!important;gap:10px!important}
  .m-story-row h3{font-size:16px!important;margin-bottom:4px!important}
  .m-story-row p{font-size:14px!important;line-height:1.55!important}
  .m-divider-lg{margin:36px 0!important}
  .m-cta-card{margin-top:24px!important;padding:18px 20px!important;gap:12px!important}
  .m-cta-card p{font-size:14.5px!important}
  .m-cta-card a{font-size:14px!important}

  /* programs — 카드 제목·대상 라인 */
  .m-h3-lg{font-size:18px!important}
  .m-tag-line{font-size:13px!important;line-height:1.6!important;padding-top:10px!important}

  /* 파트너 카드 그리드·CTA 위쪽 여백 */
  #partner [style*="margin-top:52px"]{margin-top:24px!important}
  #partner .hv17{margin-top:20px!important}
}
"""
hover_css = "".join(f".{c}:hover{{{d}}}" for c, d in hover_rules)
site_css = font_css + "\n" + base_css + "\n" + extra_css.strip() + "\n" + hover_css + "\n" + MOBILE_CSS

def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s*([{};:,>])\s*", r"\1", s)
    s = re.sub(r";}", "}", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

site_css_min = minify_css(site_css)
open(os.path.join(OUT, "assets/css/site.css"), "w", encoding="utf-8").write(site_css_min)

CRITICAL = minify_css("""
html{scroll-behavior:smooth}
body{margin:0;font-family:'Pretendard Variable',-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#4A5A70;background:#fff;font-size:16px;line-height:1.8;letter-spacing:-.005em;word-break:keep-all;overflow-x:hidden}
#siteHeader{position:fixed;top:0;left:0;right:0;z-index:100}
#top{min-height:100svh;background:#0C2140}
.skip-link{position:absolute;left:-9999px;top:0}
""")

# ─────────────────────────────────────────────────────────── 6. JS
site_js = r"""
(function(){
'use strict';
var hdr=document.getElementById('siteHeader'),logo=document.getElementById('hdrLogo'),
    links=document.getElementById('hdrLinks'),cta=document.getElementById('hdrCta'),
    btn=document.getElementById('hdrMenuBtn'),nav=document.getElementById('mobileNav');

function applyHdr(){
  if(!hdr)return;
  var on=window.scrollY>40||(nav&&!nav.hidden);
  hdr.style.background=on?'rgba(255,255,255,.97)':'transparent';
  hdr.style.backdropFilter=on?'blur(14px)':'none';
  hdr.style.boxShadow=on?'0 1px 0 #E4EAF1':'none';
  if(logo)logo.style.color=on?'#14335F':'#fff';
  if(links)links.style.color=on?'#4A5A70':'rgba(255,255,255,.8)';
  if(btn)btn.style.color=on?'#14335F':'#fff';
  if(cta){
    if(window.matchMedia('(max-width:960px)').matches){
      cta.style.background=on?'#14335F':'#fff';cta.style.color=on?'#fff':'#14335F';
    }else{ cta.style.background='#D23A18';cta.style.color='#fff'; }
  }
}
window.addEventListener('scroll',applyHdr,{passive:true});
window.addEventListener('resize',applyHdr);
applyHdr();

function setMenu(open){
  if(!nav||!btn)return;
  nav.hidden=!open;
  btn.setAttribute('aria-expanded',open?'true':'false');
  btn.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기');
  applyHdr();
}
if(btn)btn.addEventListener('click',function(){setMenu(nav.hidden);});
if(nav)nav.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false);});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'&&nav&&!nav.hidden){setMenu(false);btn.focus();}
});

var hiddenEls=[];
function reveal(el){el.style.opacity='1';el.style.transform='none';}
function revealAll(){hiddenEls.forEach(reveal);hiddenEls=[];}
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches&&'IntersectionObserver'in window){
  var io=new IntersectionObserver(function(en){
    en.forEach(function(e){
      if(e.isIntersecting){reveal(e.target);io.unobserve(e.target);
        var i=hiddenEls.indexOf(e.target); if(i>-1)hiddenEls.splice(i,1);}
    });
  },{threshold:.12});
  document.querySelectorAll('[data-reveal]').forEach(function(el,idx){
    if(el.getBoundingClientRect().top>window.innerHeight*.92){
      el.style.opacity='0';el.style.transform='translateY(22px)';
      el.style.transition='opacity .7s ease, transform .7s ease';
      el.style.transitionDelay=(idx%3*0.09).toFixed(2)+'s';
      hiddenEls.push(el); io.observe(el);
    }
  });
  /* 안전장치: 관찰자가 동작하지 않는 환경(백그라운드 탭, 크롤러, bfcache 복귀)에서도
     본문이 영구히 숨겨지지 않도록 강제 노출 */
  setTimeout(revealAll,3000);
  window.addEventListener('pageshow',function(e){if(e.persisted)revealAll();});
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible')setTimeout(revealAll,1200);
  });
  window.addEventListener('beforeprint',revealAll);
}

/* ── 이벤트 추적 (GA4가 설정된 경우에만 동작) ── */
function track(name,params){ if(typeof window.gtag==='function')window.gtag('event',name,params||{}); }
document.addEventListener('click',function(e){
  var a=e.target.closest('a'); if(!a)return;
  var h=a.getAttribute('href')||'';
  if(h.indexOf('tel:')===0)      track('contact_click',{method:'phone',link_url:h});
  else if(h.indexOf('mailto:')===0) track('contact_click',{method:'email',link_url:h});
  else if(/^https?:/.test(h)&&a.hostname!==location.hostname)
       track('outbound_click',{link_domain:a.hostname,link_url:h});
  else if(h.charAt(0)==='#')     track('nav_click',{section:h.slice(1)});
});
var marks=[25,50,75,90],hit={};
window.addEventListener('scroll',function(){
  var de=document.documentElement,
      pct=(window.scrollY+window.innerHeight)/de.scrollHeight*100;
  marks.forEach(function(m){ if(pct>=m&&!hit[m]){hit[m]=1;track('scroll_depth',{percent:m});} });
},{passive:true});
})();
"""
site_js_min = re.sub(r"^\s*//.*$", "", site_js, flags=re.M)
site_js_min = re.sub(r"/\*.*?\*/", "", site_js_min, flags=re.S)
site_js_min = "\n".join(l.strip() for l in site_js_min.split("\n") if l.strip())
open(os.path.join(OUT, "assets/js/site.js"), "w", encoding="utf-8").write(site_js_min)

# ─────────────────────────────────────────────────────────── 7. HTML head
# 80자 이내 — 네이버 서치어드바이저 권장 길이(사이트 설명 진단 항목)에 맞춤.
# 구글은 155~160자까지 표시하므로 80자는 양쪽 모두에서 문제없음.
DESC = "대한장애인드론축구협회(가치날자)는 드론축구로 장애인·비장애인이 함께하는 통합 스포츠 문화를 만듭니다. 교육·체험·대회·지도자 양성 운영."
TITLE = "대한장애인드론축구협회 | 같이 날고, 같이 웃고, 같이 성장합니다"

ORG_LD = {
    "@context": "https://schema.org", "@type": "SportsOrganization",
    "@id": SITE + "/#organization",
    "name": "대한장애인드론축구협회",
    "alternateName": ["가치날자", "Korea Para Drone Soccer Association", "KPDSA"],
    "url": SITE + "/", "logo": SITE + "/icon-512.png", "image": SITE + "/og-image.jpg",
    "description": DESC, "sport": "드론축구",
    "areaServed": {"@type": "Country", "name": "대한민국"},
    "address": {"@type": "PostalAddress", "streetAddress": "효원로 1, 604호-17",
                "addressLocality": "수원시 팔달구", "addressRegion": "경기도",
                "addressCountry": "KR"},
    "email": "kpdsa2024@gmail.com", "telephone": "+82-10-8877-8936",
    "founder": {"@type": "Person", "name": "박성춘"},
    "contactPoint": [{"@type": "ContactPoint", "telephone": "+82-10-8877-8936",
                      "email": "kpdsa2024@gmail.com", "contactType": "customer service",
                      "availableLanguage": ["Korean"], "areaServed": "KR"}],
    "sameAs": ["https://blog.naver.com/droneboy123"],
}
WEBSITE_LD = {
    "@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website",
    "url": SITE + "/", "name": "대한장애인드론축구협회", "inLanguage": "ko-KR",
    "publisher": {"@id": SITE + "/#organization"},
}
FAQ_LD = {
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": "드론축구란 무엇인가요?", "acceptedAnswer": {"@type": "Answer",
         "text": "공 모양의 보호 케이지에 담긴 드론을 조종해 상대 진영의 원형 골대를 통과시키면 득점하는 팀 스포츠입니다. "
                 "신체 조건보다 조종 능력과 팀워크가 승부를 가르기 때문에 장애인과 비장애인이 같은 코트에서 동등하게 경쟁할 수 있습니다."}},
        {"@type": "Question", "name": "교육이나 체험은 어떻게 신청하나요?", "acceptedAnswer": {"@type": "Answer",
         "text": "전화(010-8877-8936) 또는 이메일(kpdsa2024@gmail.com), 네이버 블로그를 통해 문의하시면 "
                 "학교·기관·기업 맞춤 프로그램 상담이 가능합니다."}},
        {"@type": "Question", "name": "장애인만 참여할 수 있나요?", "acceptedAnswer": {"@type": "Answer",
         "text": "아닙니다. 대한장애인드론축구협회의 프로그램은 장애인과 비장애인이 함께 참여하는 통합 스포츠를 지향합니다. "
                 "학교, 기관, 기업 단위 체험 및 교육 프로그램도 운영합니다."}},
    ],
}

def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"

hero_preload = ""
hi = img_info[hero_uuid]
hero_preload = ('<link rel="preload" as="image" type="image/avif" '
                f'imagesrcset="{", ".join(f"{p} {w}w" for p, w in hi["avif"])}" '
                f'imagesizes="100vw" fetchpriority="high">')

head = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="대한장애인드론축구협회,가치날자,드론축구,장애인체육,통합스포츠,드론교육,드론체험,드론축구대회,장애인드론축구,수원 드론축구">
<meta name="author" content="대한장애인드론축구협회">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#14335F">
<meta name="format-detection" content="telephone=yes">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="canonical" href="{SITE}/">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="대한장애인드론축구협회">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/og-image.jpg">
<meta property="og:image:secure_url" content="{SITE}/og-image.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="대한장애인드론축구협회 - 같이 날고, 같이 웃고, 같이 성장합니다">

<!-- Twitter / X -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}/og-image.jpg">
<meta name="twitter:image:alt" content="대한장애인드론축구협회 - 같이 날고, 같이 웃고, 같이 성장합니다">

<!-- 검색엔진 소유확인 — 각 콘솔에서 발급받은 값으로 교체 후 주석 해제 -->
<meta name="naver-site-verification" content="6b416343850fb86ff10b9be7f6fead7fe8ea09ba">
<!-- <meta name="google-site-verification" content="GOOGLE_VERIFICATION_CODE"> -->
<!-- <meta name="msvalidate.01" content="BING_VERIFICATION_CODE"> -->

<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">

<style>{CRITICAL}</style>
<link rel="stylesheet" href="assets/css/site.css">
{hero_preload}

{ld(ORG_LD)}
{ld(WEBSITE_LD)}
{ld(FAQ_LD)}

<!-- Google Analytics 4 — G-XXXXXXXXXX 를 실제 측정 ID로 교체 후 주석 해제 -->
<!--
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());
gtag('config','G-XXXXXXXXXX',{{anonymize_ip:true}});
</script>
-->
</head>
<body>
"""

html = head + body.strip() + '\n<script src="assets/js/site.js" defer></script>\n</body>\n</html>\n'
html = re.sub(r"\n{3,}", "\n\n", html)
html = "\n".join(l.rstrip() for l in html.split("\n"))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)

# ─────────────────────────────────────────────────────────── 8. 부속 파일
open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(f"""User-agent: *
Allow: /

User-agent: Yeti
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Daumoa
Allow: /

Sitemap: {SITE}/sitemap.xml
""")

open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>{SITE}/</loc>
    <lastmod>2026-08-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>{SITE}/og-image.jpg</image:loc>
      <image:title>대한장애인드론축구협회</image:title>
    </image:image>
  </url>
</urlset>
""")

manifest_json = {
    "name": "대한장애인드론축구협회", "short_name": "가치날자",
    "description": DESC, "lang": "ko-KR", "dir": "ltr",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#14335F", "theme_color": "#14335F",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(manifest_json, ensure_ascii=False, indent=2))

ERR_TPL = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | 대한장애인드론축구협회</title>
<meta name="robots" content="noindex,follow">
<meta name="theme-color" content="#14335F">
<link rel="icon" href="favicon.ico" sizes="32x32">
<style>
*{{box-sizing:border-box}}
body{{margin:0;min-height:100svh;display:flex;align-items:center;justify-content:center;
background:radial-gradient(880px 480px at 20% 20%,rgba(47,107,179,.25),transparent 60%),#14335F;
color:#fff;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
text-align:center;padding:40px 24px;word-break:keep-all;line-height:1.8}}
main{{max-width:520px}}
.mark{{width:92px;height:92px;display:block;margin:0 auto}}
h1{{margin:28px 0 0;font-size:clamp(28px,6vw,42px);font-weight:800;letter-spacing:-.03em}}
p{{margin:16px 0 0;color:rgba(255,255,255,.8);font-size:16px}}
.acts{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:36px}}
a{{display:inline-flex;align-items:center;min-height:48px;padding:14px 28px;border-radius:999px;
font-weight:700;font-size:15px;text-decoration:none}}
.p{{background:#fff;color:#14335F}}
.s{{border:1.5px solid rgba(255,255,255,.4);color:#fff}}
a:focus-visible{{outline:3px solid #8FB2DE;outline-offset:3px}}
</style></head>
<body><main>
<img src="icon-192.png" alt="" width="192" height="192" class="mark">
<h1>{h1}</h1>
<p>{msg}</p>
<div class="acts">
<a class="p" href="/">홈으로 돌아가기</a>
<a class="s" href="tel:010-8877-8936">전화 문의 010-8877-8936</a>
</div>
</main></body></html>
"""
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(ERR_TPL.format(
    title="페이지를 찾을 수 없습니다", h1="페이지를 찾을 수 없습니다",
    msg="주소가 바뀌었거나 삭제된 페이지입니다.<br>홈에서 원하시는 내용을 찾아보세요."))
open(os.path.join(OUT, "50x.html"), "w", encoding="utf-8").write(ERR_TPL.format(
    title="일시적인 오류", h1="일시적인 오류가 발생했습니다",
    msg="잠시 후 다시 시도해 주세요.<br>문제가 계속되면 전화로 문의해 주시기 바랍니다."))

# 보안 헤더 (Netlify / Cloudflare Pages 형식)
open(os.path.join(OUT, "_headers"), "w", encoding="utf-8").write("""/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: default-src 'self'; script-src 'self' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; font-src 'self'; connect-src 'self' https://www.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'; upgrade-insecure-requests

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/site.webmanifest
  Cache-Control: public, max-age=86400
""")

open(os.path.join(OUT, "netlify.toml"), "w", encoding="utf-8").write("""[build]
  publish = "."

[[redirects]]
  from = "/index.html"
  to = "/"
  status = 301
  force = true
""")

open(os.path.join(OUT, ".nojekyll"), "w").write("")
open(os.path.join(OUT, ".gitattributes"), "w").write("* text=auto eol=lf\n*.woff2 binary\n*.webp binary\n*.avif binary\n*.png binary\n*.jpg binary\n*.ico binary\n")
open(os.path.join(OUT, ".gitignore"), "w").write(".DS_Store\nThumbs.db\nnode_modules/\n*.log\n")

open(os.path.join(OUT, ".github/workflows/pages.yml"), "w", encoding="utf-8").write("""name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - id: deployment
        uses: actions/deploy-pages@v4
""")

print("\n--- 결과 ---")
tot = 0
for root, _, files in os.walk(OUT):
    for f in files:
        tot += os.path.getsize(os.path.join(root, f))
print(f"총 용량 {tot/1e6:.2f} MB")
print(f"index.html {os.path.getsize(os.path.join(OUT,'index.html'))/1024:.1f} KB")
print(f"site.css   {os.path.getsize(os.path.join(OUT,'assets/css/site.css'))/1024:.1f} KB")
print(f"site.js    {os.path.getsize(os.path.join(OUT,'assets/js/site.js'))/1024:.1f} KB")
print(f"hover 규칙 {len(hover_rules)}개")
