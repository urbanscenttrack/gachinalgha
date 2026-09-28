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
    ['about', 'sport', 'programs', 'vision', 'moments', 'contact'].forEach(function (id) {
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

  /* ── 히어로 경기 영상: 화면에 보이면 미리보기 자동재생, 버튼으로 전체 영상 ── */
  var box = $('#film'), vid = $('#filmVideo'), play = $('#filmPlay');
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
