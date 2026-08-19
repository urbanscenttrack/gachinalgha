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
├── favicon.ico / favicon.svg
├── apple-touch-icon.png    iOS 홈 화면 아이콘 (180×180)
├── icon-192.png / icon-512.png / icon-512-maskable.png
├── _headers                보안 헤더 (Netlify / Cloudflare Pages 전용)
├── netlify.toml            Netlify 배포 설정
├── .github/workflows/pages.yml   GitHub Pages 자동 배포
├── brand/                  공식 로고 원본 (SVG·PNG, 인쇄·SNS용 포함)
├── tools/                  원본 번들 → 정적 사이트 재생성 스크립트
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

#### ⚠️ 도메인 연결 전 임시 주소로 먼저 올리는 경우

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

사이트의 파비콘과 헤더·푸터 로고는 모두 `brand/` 폴더의 공식 파일에서 나옵니다.

- `brand/05_파비콘/` — 파비콘 세트 원본. 빌드 시 최상위로 복사됩니다
- `brand/04_심볼만/` — 드론볼 심볼 (SNS 프로필, 워터마크용)
- `brand/01~03_로고_*/` — 인쇄·문서·유니폼용 로고 (밝은배경 / 어두운배경 / 단색)
- `brand/00_사용안내.txt` — 최소 크기·여백·색상값 등 사용 규칙

로고를 바꾸시려면 `brand/` 안의 파일을 교체하고 `python3 tools/build.py` 를 다시 실행하세요.

> 참고: 브랜드 키트의 `favicon.ico` 는 16×16 한 종류만 들어 있어 고해상도 탭에서
> 뭉개집니다. 빌드 스크립트가 동일한 아트워크(`icon-512.png`)로 16/32/48 멀티사이즈
> `favicon.ico` 를 다시 만들어 넣습니다.

### 이미지 교체

`assets/img/` 안의 파일을 같은 이름으로 바꾸거나, `index.html` 의 `<picture>` 블록에서
`srcset` 경로를 수정합니다. 각 이미지는 AVIF·WebP 두 형식 × 두 해상도로 준비되어 있습니다.

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

## 7. 라이선스 / 저작권

- 사이트 콘텐츠 및 사진: © 대한장애인드론축구협회. 무단 사용을 금합니다.
- 본문 글꼴: [Pretendard](https://github.com/orioncactus/pretendard) (SIL Open Font License 1.1)
