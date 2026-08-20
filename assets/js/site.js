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
setTimeout(revealAll,3000);
window.addEventListener('pageshow',function(e){if(e.persisted)revealAll();});
document.addEventListener('visibilitychange',function(){
if(document.visibilityState==='visible')setTimeout(revealAll,1200);
});
window.addEventListener('beforeprint',revealAll);
}
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