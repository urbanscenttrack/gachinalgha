# 대한장애인드론축구협회 (가치날자) 공식 홈페이지

> 같이 날고, 같이 웃고, 같이 성장합니다.

- **사이트**: https://gachinalja.co.kr
- **네이버 블로그**: https://blog.naver.com/droneboy123
- **문의**: 010-8877-8936 / kpdsa2024@gmail.com

손으로 작성한 정적 사이트(HTML·CSS·JS)입니다. 빌드 과정 없이 파일을 고치고 `git push` 하면
1~2분 뒤 자동 배포됩니다.

---

## 1. 폴더 구조

```
.
├── index.html               메인 페이지 — 문구는 모두 여기서 고칩니다
├── 404.html / 50x.html      오류 페이지
├── assets/
│   ├── css/site.css         디자인 전체 (색·글자·간격은 맨 위 :root 변수에 모여 있음)
│   ├── js/site.js           메뉴·3D 드론볼·스크롤 연출·영상 재생·방문 통계 이벤트
│   ├── fonts/               Pretendard·Anton — 페이지에 쓰인 글자만 담은 경량 폰트
│   ├── img/                 사진 (AVIF·WebP × 두 크기)
│   └── video/               경기 영상 (미리보기 12초 / 전체 3분 46초 / 포스터)
├── photos/                  사진 원본 보관
├── brand/                   로고 원본 (06_협회엠블럼 = 현재 사용 중)
├── tools/
│   ├── subset_fonts.py      문구를 고친 뒤 폰트 다시 만들기
│   ├── image.py             새 사진을 웹용으로 변환
│   └── fonts-src/           폰트 원본 (SIL OFL)
├── robots.txt · sitemap.xml · site.webmanifest · CNAME
├── og-image.jpg · favicon.ico · icon-*.png · apple-touch-icon.png
└── .github/workflows/pages.yml   GitHub Pages 자동 배포
```

## 2. 디자인 원칙

| 항목 | 값 | 비고 |
|---|---|---|
| 바탕 | `#FFFFFF` / `#F4F6F9` | 흰색과 옅은 회색을 섹션마다 번갈아 |
| 글자 | `#111418` / `#4A505B` / `#6B717C` | 제목 / 본문 / 보조 |
| 주 색 | `#12264A` 네이비 | 버튼·상단 바·문의 영역 (푸터 `#0C1A33`) |
| 강조 | `#2F6BB3` | 브랜드 블루. 섹션 머리말·번호 등 작은 곳에만 |
| 서체 | Pretendard / Anton | 본문 전체 / 히어로 `FLY TOGETHER` 한 곳만 |
| 모서리 | 20 / 14 / 10px | 카드 / 아이콘 / 버튼 |

공공기관·협회 홈페이지처럼 차분하고 신뢰감 있게 가는 것이 원칙입니다. 색을 더하지 말고
네이비·회색과 간격·굵기로 위계를 잡으세요.

### 움직이는 요소

| 요소 | 위치 | 동작 |
|---|---|---|
| 3D 드론볼 | 히어로 (`#ball3d`) | 캔버스로 직접 그린 입체 공. 천천히 돌고, 마우스 방향으로 기울어짐 |
| 원근 바닥 | 히어로 뒤 격자 | 공이 떠 있는 무대처럼 보이게 함 |
| 순차 등장 | 히어로 요소 전체 | 위에서 한 칸씩 내려오며 자리 잡음 (`.drop`, `--i` 순서) |
| 글자 벌어짐 | `FLY` / `TOGETHER` | 스크롤하면 양옆으로 벌어지고 공이 커짐 |
| 영상 화면 세우기 | 경기 영상 섹션 | 눕혀진 화면이 스크롤하면 똑바로 섬 |
| 입체 카드 | 카드·표·문의 패널 | 마우스를 올리면 그 방향으로 살짝 기울어짐 (PC만) |

기기에서 '동작 줄이기'를 켠 방문자에게는 모두 멈춘 상태로 보입니다.

## 3. 내용 수정하기

### 문구 수정

`index.html` 을 열어 해당 문장을 고칩니다.

> ⚠️ **새로운 한글 글자가 들어가면 폰트를 다시 만들어야 합니다.**
> 용량을 줄이려고 페이지에 쓰인 글자만 폰트에 담아 두었습니다. 새 글자는 기본 글꼴로 보입니다.
>
> ```bash
> pip3 install fonttools brotli
> python3 tools/subset_fonts.py
> ```

### 사진 교체

```bash
python3 tools/image.py 새사진.jpg prog-edu 1200
```

같은 이름을 쓰면 `index.html` 은 고칠 필요가 없습니다. 원본은 `photos/` 에 보관해 두세요.

| 이름 | 위치 |
|---|---|
| `g-tournament` | 드론축구 — 경기장·점수판 |
| `prog-edu` / `prog-event` / `prog-tournament` / `prog-coach` | 주요 사업 4개 |
| `g-group` / `g-training` / `g-booth` | 현장의 순간들 |

### 영상 교체

`assets/video/` 의 세 파일을 같은 이름으로 바꿉니다.

- `match-loop.mp4` / `match-loop-m.mp4` — 자동재생 미리보기 (PC 1176px·약 4MB / 모바일 960px·약 3MB). **12초 안팎, 소리 없음**
- `match-full.mp4` — 첫 화면 영상의 "전체 영상" 버튼으로 재생 (GitHub 한도 100MB 미만)
- `match-poster.webp/.avif` — 영상 로딩 전 보이는 정지 화면

전체 영상을 유튜브에 올리시면 사이트 용량 부담 없이 더 좋습니다. 링크 주시면 연결해 드립니다.

### 로고

모든 로고·아이콘은 `brand/06_협회엠블럼/엠블럼_마스터_1398px.png` 에서 만들어졌습니다.

## 4. 배포

`main` 브랜치에 push 하면 `.github/workflows/pages.yml` 이 GitHub Pages 로 배포합니다.
커스텀 도메인 `gachinalja.co.kr` 은 `CNAME` 파일과 가비아 DNS(A 레코드 4개 + www CNAME)로 연결돼 있습니다.

> GitHub Pages 는 응답 헤더를 지정할 수 없어 `_headers`(보안 헤더)는 적용되지 않습니다.
> 보안 헤더까지 쓰려면 Cloudflare Pages 로 옮기면 됩니다.

## 5. 검색·분석 연결 현황

| 항목 | 상태 |
|---|---|
| Google Search Console | ✅ DNS TXT 인증 · 사이트맵 제출 완료 |
| 네이버 서치어드바이저 | ✅ 메타태그 인증 |
| 구조화 데이터 | 단체 · 웹사이트 · FAQ · **영상 · 대회 정보** |
| Google Analytics 4 | ⏳ `index.html` 의 주석 블록에 측정 ID 넣고 주석 해제 |
| 네이버 스마트플레이스 | ⏳ 등록 권장 (지도·전화 카드 노출) |

GA4 가 연결되면 아래 이벤트가 자동 수집됩니다.

| 이벤트 | 발생 시점 |
|---|---|
| `contact_click` | 전화·이메일 클릭 |
| `outbound_click` | 블로그 등 외부 링크 |
| `video_play` | 전체 영상 재생 |
| `nav_click` / `scroll_depth` | 메뉴 이동 / 스크롤 25·50·75·90% |

## 6. 라이선스

- 콘텐츠·사진·영상: © 대한장애인드론축구협회. 무단 사용 금지.
- 서체: [Pretendard](https://github.com/orioncactus/pretendard), [Anton](https://fonts.google.com/specimen/Anton) — SIL Open Font License 1.1
