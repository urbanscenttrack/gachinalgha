/* 대한장애인드론축구협회 — site.js */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ── 헤더: 스크롤하면 그림자 ── */
  var hdr = $('#hdr');
  function onScroll() { hdr.classList.toggle('is-scrolled', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── 모바일 메뉴 ── */
  var btn = $('#menuBtn'), mnav = $('#mnav');
  function setMenu(open) {
    mnav.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    if (open) hdr.classList.add('is-scrolled'); else onScroll();
  }
  btn.addEventListener('click', function () { setMenu(mnav.hidden); });
  mnav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !mnav.hidden) { setMenu(false); btn.focus(); }
  });

  /* ── 현재 섹션을 메뉴에 표시 ── */
  var navLinks = $$('.nav a');
  if ('IntersectionObserver' in window) {
    var secIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (a) {
          a.classList.toggle('is-active', a.getAttribute('href') === '#' + en.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['about', 'sport', 'programs', 'vision', 'film', 'moments', 'contact'].forEach(function (id) {
      var el = document.getElementById(id); if (el) secIo.observe(el);
    });
  }

  /* ── 스크롤 등장 (화면 아래 요소만 숨겼다가 보여줌, 실패해도 3초 뒤 전부 노출) ── */
  var pending = [];
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        io.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    var groups = {};
    $$('.reveal').forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight * 0.92) return;
      var p = el.parentElement, k = p && (p.dataset.rg || (p.dataset.rg = Math.random().toString(36).slice(2)));
      var i = groups[k] = (groups[k] || 0) + 1;
      el.style.transitionDelay = ((i - 1) % 4) * 0.08 + 's';
      el.classList.add('pre');
      pending.push(el);
      io.observe(el);
    });
    var revealAll = function () { pending.forEach(function (el) { el.classList.add('is-in'); }); };
    setTimeout(revealAll, 3000);
    window.addEventListener('pageshow', function (e) { if (e.persisted) revealAll(); });
    window.addEventListener('beforeprint', revealAll);
  }

  /* ── 3D 드론볼: 캔버스에 원근 투영으로 그림 (마우스를 따라 기울고, 천천히 회전) ── */
  var heroEl = $('.hero'), cv = $('#ball3d');
  if (cv && cv.getContext) (function () {
    var ctx = cv.getContext('2d'), W = 0, dpr = 1, visible = true, raf = 0;
    var yaw = 0.6, pitch = 0.42, drift = 0, mx = 0, my = 0, spin = 0, t0 = performance.now(), fx = 0, roll = 0;
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = cv.clientWidth; cv.width = cv.height = Math.round(W * dpr);
    }
    function rot(p) { // yaw(Y축) → pitch(X축)
      var cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
      var x = p[0] * cy + p[2] * sy, z = -p[0] * sy + p[2] * cy, y = p[1];
      return [x, y * cp - z * sp, y * sp + z * cp];
    }
    function proj(p, R, bob) {
      var r = rot(p), f = 4.2 / (4.2 + r[2] / R * 0.9); // 원근
      return [W / 2 + r[0] * f, W / 2 + (r[1] + bob) * f, r[2]];
    }
    function path(pts, R, bob, width, base, depthFade) { // 선분마다 앞/뒤 깊이로 진하기 조절
      for (var i = 0; i < pts.length - 1; i++) {
        var a = proj(pts[i], R, bob), b = proj(pts[i + 1], R, bob), z = (a[2] + b[2]) / 2 / R; // -1 앞 ~ 1 뒤
        var al = base * (depthFade ? (1.05 - (z + 1) * 0.42) : 1);
        ctx.strokeStyle = 'rgba(17,20,24,' + Math.max(al, 0.04).toFixed(3) + ')';
        ctx.lineWidth = width * (z < 0 ? 1 : 0.75);
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      }
    }
    function ring(fn, n) { var o = []; for (var i = 0; i <= n; i++) o.push(fn(i / n * Math.PI * 2)); return o; }
    function draw(now) {
      var t = (now - t0) / 1000, R = W * 0.36, bob = reduce ? 0 : Math.sin(t * 1.3) * W * 0.018;
      if (!reduce) { drift += 0.0035; spin = t * 22; }
      yaw += ((0.6 + drift + mx * 0.5) - yaw) * 0.08;
      pitch += ((0.42 + my * 0.25) - pitch) * 0.08;
      // 비행: 14초 주기로 좌우를 몇 번 오가다가 가운데로 돌아와 제자리 비행
      var nx = 0, ft = t - 1.2;
      if (!reduce && ft > 0) {
        var u = (ft % 14) / 7; // 0~1 비행, 1~2 제자리
        if (u < 1) {
          var room = (heroEl.clientWidth - W) / 2 - 8, amp = Math.max(0, Math.min(W * 0.85, room));
          nx = amp * Math.sin(Math.PI * 2 * u * 1.5) * Math.sin(Math.PI * u);
        }
      }
      var vx = nx - fx; fx = nx;
      roll += (Math.max(-0.35, Math.min(0.35, vx * 0.06)) - roll) * 0.1; // 움직이는 방향으로 기울기
      heroEl.style.setProperty('--bx', fx.toFixed(1) + 'px');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, W);
      ctx.translate(W / 2, W / 2); ctx.rotate(roll); ctx.translate(-W / 2, -W / 2);
      ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      var cx = W / 2, cy = W / 2 + bob;
      // 유리 공 (반투명 구, 좌상단 하이라이트)
      var g = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.45, R * 0.05, cx, cy, R * 1.02);
      g.addColorStop(0, 'rgba(255,255,255,.92)'); g.addColorStop(0.55, 'rgba(236,239,244,.55)'); g.addColorStop(1, 'rgba(190,197,208,.55)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();
      // 경선·위선 (가는 선, 뒤쪽은 옅게)
      for (var m = 0; m < 6; m++) (function (a0) {
        path(ring(function (th) { return [Math.cos(th) * Math.cos(a0) * R, Math.sin(th) * R, Math.cos(th) * Math.sin(a0) * R]; }, 64), R, bob, 1.1, 0.34, true);
      })(m / 6 * Math.PI);
      [-0.62, -0.32, 0.32, 0.62].forEach(function (lat) {
        var yy = Math.sin(lat) * R, rr = Math.cos(lat) * R;
        path(ring(function (th) { return [Math.cos(th) * rr, yy, Math.sin(th) * rr]; }, 64), R, bob, 1.1, 0.34, true);
      });
      // 드론 (팔 4개 + 프로펠러 링 + 회전 날개)
      var a = R * 0.44, body = R * 0.16, h = R * 0.07;
      [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (s) {
        path([[s[0] * body * 0.7, 0, s[1] * body * 0.7], [s[0] * a, 0, s[1] * a]], R, bob, W * 0.012, 0.95, false);
        var rc = [s[0] * a, -h * 0.4, s[1] * a], rr = R * 0.2, sp = spin * s[0] * s[1];
        path(ring(function (th) { return [rc[0] + Math.cos(th) * rr, rc[1], rc[2] + Math.sin(th) * rr]; }, 40), R, bob, W * 0.0065, 0.9, false);
        path([[rc[0] + Math.cos(sp) * rr * 0.86, rc[1] - 1, rc[2] + Math.sin(sp) * rr * 0.86],
              [rc[0] - Math.cos(sp) * rr * 0.86, rc[1] - 1, rc[2] - Math.sin(sp) * rr * 0.86]], R, bob, W * 0.005, 0.35, false);
      });
      // 몸체: 면을 깊이순으로 칠한 상자
      var v = [];
      [-1, 1].forEach(function (x) { [-1, 1].forEach(function (y) { [-1, 1].forEach(function (z) { v.push([x * body, y * h, z * body]); }); }); });
      var faces = [[0, 1, 3, 2, 0.30], [4, 5, 7, 6, 0.22], [0, 1, 5, 4, 0.12], [2, 3, 7, 6, 0.34], [0, 2, 6, 4, 0.18], [1, 3, 7, 5, 0.26]];
      var P = v.map(function (p) { return proj(p, R, bob); });
      faces.map(function (f) { return { f: f, z: (P[f[0]][2] + P[f[1]][2] + P[f[2]][2] + P[f[3]][2]) / 4 }; })
        .sort(function (x, y) { return y.z - x.z; })
        .forEach(function (o) {
          var f = o.f, l = Math.round(17 + f[4] * 60);
          ctx.fillStyle = 'rgb(' + l + ',' + (l + 2) + ',' + (l + 6) + ')';
          ctx.beginPath(); ctx.moveTo(P[f[0]][0], P[f[0]][1]);
          for (var k = 1; k < 4; k++) ctx.lineTo(P[f[k]][0], P[f[k]][1]);
          ctx.closePath(); ctx.fill();
        });
      // 파란 LED
      var led = proj([0, -h * 1.05, 0], R, bob), pulse = reduce ? 1 : 0.75 + Math.sin(t * 3) * 0.25;
      var lg = ctx.createRadialGradient(led[0], led[1], 0, led[0], led[1], R * 0.12);
      lg.addColorStop(0, 'rgba(90,160,255,' + (0.9 * pulse).toFixed(3) + ')'); lg.addColorStop(1, 'rgba(47,107,179,0)');
      ctx.fillStyle = lg; ctx.beginPath(); ctx.arc(led[0], led[1], R * 0.12, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#4F9BFF'; ctx.beginPath(); ctx.arc(led[0], led[1], R * 0.025, 0, Math.PI * 2); ctx.fill();
      // 적도 링(굵게) + 외곽선
      path(ring(function (th) { return [Math.cos(th) * R, 0, Math.sin(th) * R]; }, 90), R, bob, W * 0.011, 0.92, true);
      ctx.strokeStyle = 'rgba(17,20,24,.92)'; ctx.lineWidth = W * 0.011;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
      // 공이 오르내리면 바닥 그림자도 커졌다 작아짐
      heroEl.style.setProperty('--sh', (1 - bob / (W * 0.018) * 0.12).toFixed(3));
      if (!reduce && visible) raf = requestAnimationFrame(draw);
    }
    size(); draw(performance.now());
    window.addEventListener('resize', function () { size(); if (reduce) draw(performance.now()); });
    if (reduce) return;
    heroEl.addEventListener('pointermove', function (e) {
      var r = cv.getBoundingClientRect();
      mx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / (window.innerWidth / 2)));
      my = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / (window.innerHeight / 2)));
    });
    heroEl.addEventListener('pointerleave', function () { mx = my = 0; });
    var restart = function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); };
    if ('IntersectionObserver' in window) new IntersectionObserver(function (en) {
      var was = visible; visible = en[0].isIntersecting; if (visible && !was) restart();
    }).observe(cv);
    document.addEventListener('visibilitychange', function () { if (!document.hidden && visible) restart(); });
  })();

  /* ── 스크롤 연동: 히어로 글자가 양옆으로 벌어짐 · 경기 영상 화면이 세워짐 ── */
  var filmSec = $('#film'), filmBox = $('#filmBox');
  if (!reduce) {
    var ticking = false;
    var onPar = function () {
      ticking = false;
      var vh = window.innerHeight;
      if (heroEl) heroEl.style.setProperty('--p', Math.min(1, Math.max(0, window.scrollY / (heroEl.offsetHeight * 0.9))).toFixed(3));
      if (filmBox) {
        var fp = 1 - (filmBox.getBoundingClientRect().top - vh * 0.18) / (vh * 0.7);
        filmSec.style.setProperty('--fp', Math.min(1, Math.max(0, fp)).toFixed(3));
      }
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onPar); } }, { passive: true });
    window.addEventListener('resize', onPar);
    onPar();
  }

  /* ── 숫자 올라가기 ── */
  if (!reduce && 'IntersectionObserver' in window) {
    var nio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return; nio.unobserve(en.target);
        var el = en.target, to = +el.dataset.count, from = +(el.dataset.from || 0), st = performance.now();
        (function step(now) {
          var k = Math.min(1, (now - st) / 1400), e = 1 - Math.pow(1 - k, 3);
          el.textContent = Math.round(from + (to - from) * e);
          if (k < 1) requestAnimationFrame(step);
        })(st);
        setTimeout(function () { el.textContent = to; }, 1600); // 탭이 가려져 애니메이션이 멈춰도 최종값 보장
      });
    }, { threshold: 0.6 });
    $$('[data-count]').forEach(function (n) { nio.observe(n); });
  }

  /* ── 입체 카드: 마우스 방향으로 살짝 기울어짐 (마우스 쓰는 기기만) ── */
  if (!reduce && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    $$('.card, .spec, .tile, .vm-col, .overview, .contact-panel').forEach(function (el) {
      el.classList.add('tilt');
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        var amt = r.width > 500 ? 3 : 6;
        el.style.setProperty('--rx', (-y * amt).toFixed(2) + 'deg');
        el.style.setProperty('--ry', (x * amt).toFixed(2) + 'deg');
        el.classList.add('is-tilting');
      });
      el.addEventListener('pointerleave', function () {
        el.style.removeProperty('--rx'); el.style.removeProperty('--ry'); el.classList.remove('is-tilting');
      });
    });
  }

  /* ── 경기 영상: 화면에 보이면 미리보기 자동재생, 버튼으로 전체 영상 ── */
  var box = $('#filmBox'), vid = $('#filmVideo'), play = $('#filmPlay');
  var full = false;
  if (vid && 'IntersectionObserver' in window && !reduce) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (full) return;
        if (en.isIntersecting) { vid.preload = 'auto'; var p = vid.play(); if (p && p.catch) p.catch(function () {}); }
        else vid.pause();
      });
    }, { threshold: 0.35 }).observe(vid);
  }
  if (play) play.addEventListener('click', function () {
    full = true;
    box.classList.add('is-full');
    vid.pause();
    vid.src = 'assets/video/match-full.mp4';
    vid.loop = false;
    vid.muted = false;
    vid.controls = true;
    vid.preload = 'auto';
    vid.load();
    var p = vid.play(); if (p && p.catch) p.catch(function () {});
    vid.focus();
    track('video_play', { video: 'match_full' });
  });

  /* ── 이벤트 추적 (GA4 연결 시에만 동작) ── */
  function track(name, params) { if (typeof window.gtag === 'function') window.gtag('event', name, params || {}); }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('tel:') === 0) track('contact_click', { method: 'phone' });
    else if (h.indexOf('mailto:') === 0) track('contact_click', { method: 'email' });
    else if (/^https?:/.test(h) && a.hostname !== location.hostname) track('outbound_click', { link_domain: a.hostname });
    else if (h.charAt(0) === '#') track('nav_click', { section: h.slice(1) });
  });
  var marks = [25, 50, 75, 90], hit = {};
  window.addEventListener('scroll', function () {
    var de = document.documentElement, pct = (window.scrollY + window.innerHeight) / de.scrollHeight * 100;
    marks.forEach(function (m) { if (pct >= m && !hit[m]) { hit[m] = 1; track('scroll_depth', { percent: m }); } });
  }, { passive: true });
})();
