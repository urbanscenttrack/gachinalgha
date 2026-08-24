# 대한장애인드론축구협회 (가치날자) 공식 홈페이지

> 같이 날고, 같이 웃고, 같이 성장합니다.

정적 사이트(HTML/CSS/JS)입니다. 빌드 도구나 런타임 의존성 없이 그대로 배포됩니다.

- **운영 도메인(예정)**: https://www.kpdsa.or.kr
- **네이버 블로그**: https://blog.naver.com/droneboy123
- **문의**: 010-8877-8936 / kpdsa2024@gmail.com

---

## 1. 폴더 구조

```
.
├── index.html              메인 페이지 (본문이 HTML에 그대로 들어있음 = 검색엔진이 읽음)
├── 404.html                존재하지 않는 페이지
├── 50x.html                서버 오류 페이지 (지원하는 호스팅에서만 사용)
├── robots.txt              크롤러 규칙 (Googlebot / Yeti(네이버) / Bingbot / Daumoa)
├── sitemap.xml             사이트맵
├── site.webmanifest        PWA 매니페스트 (홈 화면 추가)
├── og-image.jpg            SNS 공유 미리보기 이미지 (1200×630)
├── favicon.ico
├── apple-touch-icon.png    iOS 홈 화면 아이콘 (180×180)
├── icon-192.png / icon-512.png / icon-512-maskable.png
├── _headers                보안 헤더 (Netlify / Cloudflare Pages 전용)
├── netlify.toml            Netlify 배포 설정
├── .github/workflows/pages.yml   GitHub Pages 자동 배포
├── brand/                  로고 원본 (06_협회엠블럼 = 현재 사용 중)
├── photos/                 사진 교체용 (역할 이름으로 넣으면 빌드가 자동 처리)
├── tools/                  원본 번들 → 정적 사이트 재생성 스크립트 (배포에 포함되지 않음)
└── assets/
    ├── css/site.css        전체 스타일 (압축됨)
    ├── js/site.js          헤더·모바일 메뉴·스크롤 애니메이션·이벤트 추적
    ├── fonts/*.woff2       Pretendard 서브셋 (실제 사용 글자만, 18개 파일 103KB)
    └── img/*.avif,*.webp   반응형 이미지 (AVIF 우선, WebP 대체)
```

---

## 2. 로컬에서 확인하기

```bash
python3 -m http.server 8000
```

브라우저에서 http://localhost:8000 을 엽니다.
(파일을 더블클릭해 `file://` 로 열면 일부 경로가 동작하지 않습니다. 반드시 서버로 확인하세요.)

---

## 3. 배포

### 방법 A — GitHub Pages (무료, 기본 권장)

```bash
git remote add origin https://github.com/<계정>/<저장소>.git
git branch -M main
git push -u origin main
```

그다음 GitHub 저장소에서 **Settings → Pages → Source: GitHub Actions** 를 선택합니다.
`.github/workflows/pages.yml` 이 자동으로 배포합니다.

커스텀 도메인을 쓰려면 Settings → Pages → Custom domain 에 `www.kpdsa.or.kr` 을 입력하고,
도메인 DNS에 `www` CNAME → `<계정>.github.io` 를 추가한 뒤 **Enforce HTTPS** 를 켭니다.

#### 도메인 연결 시 주소 바꾸기

현재 `canonical` · OG · `sitemap.xml` · `robots.txt` · 구조화 데이터가 모두
`https://urbanscenttrack.github.io/gachinalgha` 를 가리킵니다.

`www.kpdsa.or.kr` 를 연결하면 `tools/build.py` 맨 위의 **`SITE` 한 줄만** 바꾸고
다시 빌드하면 전부 따라갑니다.

```python
SITE = "https://www.kpdsa.or.kr"
```

#### (참고) 예전 안내 — 임시 주소로 올리는 경우

`index.html` 의 `canonical`, `og:url`, `og:image`, `twitter:image`, 구조화 데이터 안의 URL,
그리고 `sitemap.xml` / `robots.txt` 가 모두 `https://www.kpdsa.or.kr` 를 가리키고 있습니다.

`<계정>.github.io/<저장소>/` 같은 임시 주소로 먼저 공개한다면 **검색엔진에 등록하기 전에**
그 주소로 일괄 치환하세요. 도메인이 준비되면 다시 되돌립니다.

```bash
sed -i '' 's|https://www.kpdsa.or.kr|https://<계정>.github.io/<저장소>|g' index.html sitemap.xml robots.txt
```

임시 주소로 운영하는 동안에는 검색엔진 등록을 미루는 편이 낫습니다.
잘못된 canonical로 색인되면 도메인 연결 후 정리에 시간이 걸립니다.

> GitHub Pages는 HTTPS를 지원하지만 **응답 헤더를 지정할 수 없습니다.** `_headers` 파일이 무시되므로
> CSP·HSTS 같은 보안 헤더가 적용되지 않습니다. 헤더까지 적용하려면 아래 방법 B를 쓰세요.

### 방법 B — Cloudflare Pages 또는 Netlify (보안 헤더까지 적용, 권장)

저장소를 연결하고 빌드 명령은 비워둔 채 **출력 디렉터리를 `/`** 로 지정하면 끝입니다.
`_headers` 파일이 자동 인식되어 HSTS, CSP, X-Content-Type-Options 등이 적용됩니다.

---

## 4. 배포 후 반드시 할 일 (분석 도구 연결)

### 4-1. Google Analytics 4

1. https://analytics.google.com 에서 속성을 만들고 측정 ID(`G-XXXXXXXXXX`)를 발급받습니다.
2. `index.html` 아래쪽 `<!-- Google Analytics 4 -->` 주석 블록을 찾습니다.
3. `G-XXXXXXXXXX` 두 곳을 실제 ID로 바꾸고, 감싸고 있는 `<!--` `-->` 를 지웁니다.

연결되면 `assets/js/site.js` 에 이미 들어있는 아래 이벤트가 자동 수집됩니다.

| 이벤트 | 발생 시점 | 파라미터 |
|---|---|---|
| `contact_click` | 전화·이메일 링크 클릭 | `method` (phone/email) |
| `outbound_click` | 외부 링크(네이버 블로그 등) 클릭 | `link_domain` |
| `nav_click` | 페이지 내 메뉴 이동 | `section` |
| `scroll_depth` | 25 / 50 / 75 / 90% 도달 | `percent` |

GA4에서 `contact_click` 을 **전환(주요 이벤트)** 으로 표시해 두면 문의 성과를 바로 볼 수 있습니다.

### 4-2. Google Search Console

1. https://search.google.com/search-console 에서 도메인을 등록합니다.
2. HTML 태그 방식을 고르면 나오는 코드를 `index.html` 의
   `<!-- <meta name="google-site-verification" ...> -->` 줄에 넣고 주석을 해제합니다.
3. 소유 확인 후 **Sitemaps** 메뉴에 `sitemap.xml` 을 제출합니다.

### 4-3. 네이버 서치어드바이저 (국내 검색 유입의 핵심)

1. https://searchadvisor.naver.com → 웹마스터도구 → 사이트 등록
2. HTML 태그 방식의 코드를 `index.html` 의
   `<!-- <meta name="naver-site-verification" ...> -->` 줄에 넣고 주석을 해제합니다.
3. **요청 → 사이트맵 제출** 에 `https://www.kpdsa.or.kr/sitemap.xml` 을 등록합니다.
4. **요청 → 웹페이지 수집** 으로 메인 URL을 직접 수집 요청합니다.
5. **검증 → 로봇스텍스트 / 리치결과** 로 정상 인식 여부를 확인합니다.

> 네이버 크롤러(Yeti)는 자바스크립트 실행이 제한적입니다. 이 사이트는 본문이 HTML에
> 그대로 들어있어 문제없지만, 앞으로 콘텐츠를 JS로 그려내는 방식은 피하세요.

### 4-4. Bing 웹마스터도구

https://www.bing.com/webmasters 에서 **Google Search Console 계정으로 가져오기**를 쓰면
1분 만에 끝납니다. 수동 등록 시 `msvalidate.01` 메타태그 줄의 주석을 해제하세요.

### 4-5. 네이버 블로그 연동

- 블로그 링크는 구조화 데이터(`sameAs`)와 문의 섹션에 이미 연결되어 있습니다.
- 블로그 각 글 하단에 홈페이지 주소를 넣어 **상호 링크**를 만들면 검색 노출에 도움이 됩니다.
- 네이버 **스마트플레이스** 등록(협회 위치·연락처 노출)도 함께 권장합니다.

---

## 5. 내용 수정하기

`index.html` 을 직접 편집하면 됩니다. 텍스트는 모두 HTML 안에 있습니다.

### ⚠️ 한글 텍스트를 추가·수정한 뒤에는 폰트를 다시 만들어야 합니다

용량을 줄이기 위해 Pretendard 폰트에서 **현재 페이지에 실제로 쓰인 글자만** 남겼습니다
(2.8MB → 103KB). 새로운 글자를 넣으면 그 글자만 기본 시스템 글꼴로 보입니다.

해결 방법은 두 가지입니다.

**(1) 폰트 서브셋 다시 만들기**

```bash
pip3 install fonttools brotli
python3 tools/subset_fonts.py
```

> `tools/subset_fonts.py` 는 현재 `index.html`·`404.html` 에 쓰인 글자를 다시 스캔합니다.
> 단, 이미 서브셋된 폰트를 또 줄이는 것이므로 **글자를 추가했다면 원본에서 다시 빌드**해야 합니다:
> `python3 tools/build.py ../대한장애인드론축구협회_최종.html && python3 tools/subset_fonts.py`
> (`tools/build.py` 는 `assets/` 만 새로 만들고 이 README나 `tools/` 는 건드리지 않습니다.)

**(2) 간단하게 CDN 폰트로 바꾸기** — 용량이 늘지만(약 +300KB) 글자 제한이 사라집니다.
`index.html` 의 `<link rel="stylesheet" href="assets/css/site.css">` 위에 아래 줄을 넣고,
`assets/css/site.css` 맨 앞의 `@font-face{...}` 블록들을 지웁니다.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
```

### 로고 · 파비콘 교체

사이트에 등장하는 **모든 로고는 협회 공식 엠블럼 하나**에서 생성됩니다.
원본은 `brand/06_협회엠블럼/` 에 있습니다.

| 쓰이는 곳 | 파일 |
|---|---|
| 헤더 · 푸터 로고 (40px) | `assets/img/emblem-256.webp` (+ png 대체) |
| 브라우저 탭 | `favicon.ico` (16/32/48) · `icon-192.png` |
| iOS 홈 화면 | `apple-touch-icon.png` |
| 안드로이드 / PWA | `icon-192.png` · `icon-512.png` · `icon-512-maskable.png` |
| 카카오톡 · SNS 미리보기 | `og-image.jpg` |
| 404 / 50x 페이지 | `icon-192.png` |
| 구조화 데이터 `logo` | `icon-512.png` |

**교체하려면** `brand/06_협회엠블럼/엠블럼_마스터_1398px.png` 를 같은 규격
(정사각형 · 배경 투명 · 원형 바깥 잘라냄)으로 바꾸고 `python3 tools/build.py` 를
실행하면 위 9종이 한꺼번에 다시 만들어집니다.

> **작은 크기에서의 한계** — 엠블럼은 바깥 띠에 글자가 들어간 크레스트라
> 16~32px 브라우저 탭에서는 글자가 뭉개집니다. 원형 엠블럼의 공통된 특성으로,
> 그 크기에서는 빨강·남색 원형 실루엣으로 인지됩니다. 탭에서도 형태를 또렷하게
> 하려면 가운데 심볼(별+사람)만 잘라낸 별도 파비콘이 필요합니다.

> **이전 아이덴티티** — "가치날자" 워드마크 세트는 `brand/01~05_*` 에 그대로
> 보관돼 있습니다. 현재 홈페이지에는 사용되지 않습니다.

### 포인트 컬러(코랄)

파랑 일변도를 피하려고 코랄 계열 포인트 컬러를 도입했습니다. 명도 대비(WCAG AA)를
맞추려고 배경별로 세 단계를 씁니다.

| 토큰 | 값 | 쓰는 곳 | 대비 |
|---|---|---|---|
| ACC | `#D23A18` | 버튼 채움 (흰 글자) | 4.82:1 |
| ACC_SOFT | `#C8360F` | 밝은 배경 위 작은 텍스트 | 4.90:1 |
| ACC_LITE | `#FF8A6E` | 네이비 배경 위 텍스트 | 5.46:1 |

색을 바꾸시려면 `tools/build.py` 의 `ACC, ACC_SOFT, ACC_LITE` 값을 고치고 다시 빌드하세요.
더 밝고 선명한 색(예: `#F04A28`)은 흰 글자 대비가 3.7:1 로 떨어져 접근성 기준에 미달합니다.

> 코랄은 공식 브랜드 팔레트(네이비·블루·스카이·회색)에 없는 색입니다.
> 계속 쓰실 거라면 `brand/00_사용안내.txt` 의 색상값 항목에 추가해 두시길 권합니다.

**모바일(≤960px)에서는 포인트 컬러를 쓰지 않습니다.** 브랜드 블루로 되돌아갑니다.
빌드 시 `.a-soft` `.a-lite` `.a-h1` `.a-fill` `.a-dash` 클래스가 붙고, 모바일
미디어쿼리에서 원래 색으로 복원합니다. 드론축구 설명의 `RED TEAM` 라벨만은
팀 색이라 예외로 남겨 두었습니다(파랗게 바뀌면 BLUE TEAM 과 구분이 사라집니다).

### 애니메이션

모두 `prefers-reduced-motion: reduce` 를 존중합니다. 시스템에서 "동작 줄이기"를 켠
사용자에게는 전부 정지합니다.

| 효과 | 위치 | 구현 |
|---|---|---|
| 히어로 진입 | 히어로 텍스트·버튼 | 위로 떠오르며 순차 등장 |
| 스크롤 등장 | 전 섹션 | IntersectionObserver, 3개 단위 시차 |
| 이미지 확대 | 프로그램 카드 · 갤러리 | 마우스 올릴 때만 (`hover:hover`) |
| 화살표 이동 | 문의 카드 | 마우스 올릴 때 오른쪽으로 |
| 메뉴 슬라이드 | 모바일 메뉴 | 위에서 내려옴 |
| 누름 반응 | 버튼 | `:active` 에서 살짝 눌림 |

모두 `transform` 과 `opacity` 만 사용해 리플로우가 발생하지 않습니다.

> 스크롤에 반응하는 "바람(비행 궤적)" 효과와 히어로 패럴랙스를 넣었다가 제거했습니다.
> 필요해지면 git 이력의 `2d73d6e` 커밋에서 되살릴 수 있습니다.

### 사진 교체

`photos/` 폴더에 **역할 이름으로 파일을 넣고 다시 빌드**하면 됩니다.
크기 조정, AVIF·WebP 변환, 반응형 `srcset` 생성이 자동으로 처리됩니다.

```bash
cp 새사진.jpg photos/prog-event.jpg
python3 tools/build.py
```

| 역할 이름 | 위치 |
|---|---|
| `hero` | 첫 화면 배경 |
| `belief` | "하늘에는 장벽이 없습니다" 섹션 배경 |
| `prog-edu` / `prog-event` / `prog-tournament` / `prog-coach` | 주요 사업 카드 4장 |
| `vm-vision` / `vm-mission` | 비전 · 미션 |
| `g-match` / `g-training` / `g-event` / `g-group` / `g-award` / `g-tournament` / `g-booth` / `g-edu` | 갤러리 8장 |

확장자는 `.jpg` `.jpeg` `.png` `.webp` 를 인식합니다. `photos/` 에 파일이 없으면
원본 번들에 들어있던 사진을 그대로 씁니다.

> 카드 이미지는 가로로 넓게 잘립니다(`object-fit: cover`, 데스크톱 544×240 / 모바일 327×200).
> 중요한 피사체는 사진 가운데에 오도록 찍거나 미리 잘라 두세요.

---

## 6. 배포 후 점검 체크리스트

| 항목 | 확인 도구 |
|---|---|
| 성능·접근성·SEO 점수 | [PageSpeed Insights](https://pagespeed.web.dev/) |
| 구조화 데이터 | [리치 결과 테스트](https://search.google.com/test/rich-results) |
| 모바일 친화성 | PageSpeed Insights 모바일 탭 |
| SNS 공유 미리보기 | [OG 디버거](https://www.opengraph.xyz/) / 카카오톡에 링크 붙여넣기 |
| 보안 헤더 | [securityheaders.com](https://securityheaders.com/) |
| 접근성 | [WAVE](https://wave.webaim.org/) |
| 네이버 노출 | 서치어드바이저 → 진단 |

---

## 7. 참고 — GitHub 언어 통계

저장소 상단의 Languages 막대는 `.gitattributes` 로 조정해 두었습니다.

- `tools/**` — 빌드 도구(Python). 방문자에게 전달되지 않으므로 `linguist-vendored` 로 제외
- `brand/**` — 로고 원본. 코드가 아니므로 제외
- `assets/css/site.css`, `assets/js/site.js` — 압축돼 있어 linguist 가 "자동 생성 파일"로
  분류하고 통계에서 빼버리므로 `linguist-generated=false` 로 되살림

통계에서 제외했을 뿐 파일은 그대로 저장소에 있습니다.

---

## 8. 라이선스 / 저작권

- 사이트 콘텐츠 및 사진: © 대한장애인드론축구협회. 무단 사용을 금합니다.
- 본문 글꼴: [Pretendard](https://github.com/orioncactus/pretendard) (SIL Open Font License 1.1)
