/* ŚLĄSCY SĘDZIOWIE — interakcje */
(function(){
  'use strict';

  /* ---- Page loader (jedna nakładka przy wczytaniu strony) ---- */
  const loader = document.getElementById('loader');
  if (loader){
    const start = Date.now();
    const MIN_MS = 550;            // minimalny czas widoczności (bez mrugania)
    const hide = () => loader.classList.add('hidden');
    const scheduleHide = () => setTimeout(hide, Math.max(0, MIN_MS - (Date.now() - start)));
    if (document.readyState === 'complete') scheduleHide();
    else window.addEventListener('load', scheduleHide);
    setTimeout(hide, 3000);        // bezpiecznik
    window.addEventListener('pageshow', (e) => { if (e.persisted) hide(); });
  }

  /* ---- Nav scroll state ---- */
  const nav = document.getElementById('nav');
  const onScroll = () => {
    if (window.scrollY > 40) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();

  /* ---- Mobile drawer ---- */
  const drawer = document.getElementById('drawer');
  const openD = () => drawer.classList.add('open');
  const closeD = () => drawer.classList.remove('open');
  document.getElementById('burger').addEventListener('click', openD);
  document.getElementById('drawerClose').addEventListener('click', closeD);
  drawer.addEventListener('click', e => { if (e.target === drawer) closeD(); });
  drawer.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', closeD));

  /* ---- Reveal on scroll (rect-based — robust without IntersectionObserver) ---- */
  const reveals = [...document.querySelectorAll('.reveal')];
  const revealCheck = () => {
    const vh = window.innerHeight || document.documentElement.clientHeight;
    for (const el of reveals){
      if (el.classList.contains('in')) continue;
      const r = el.getBoundingClientRect();
      if (r.top < vh * 0.92 && r.bottom > 0) el.classList.add('in');
    }
  };
  window.addEventListener('scroll', revealCheck, {passive:true});
  window.addEventListener('resize', revealCheck);
  revealCheck();
  // run a few times after load in case fonts/layout shift, then a final safety sweep
  [60, 250, 600].forEach(t => setTimeout(revealCheck, t));
  window.addEventListener('load', () => { revealCheck(); setTimeout(revealCheck, 200); });
  setTimeout(() => reveals.forEach(el => el.classList.add('in')), 2500);

  /* ---- Contact form validation ---- */
  const form = document.getElementById('contactForm');
  if (form){
    const showErr = (field, msg) => {
      const f = field.closest('.field') || field.closest('.consent');
      f.classList.add('invalid');
      const e = f.querySelector('.err');
      if (e && msg) e.textContent = msg;
    };
    const clearErr = (el) => {
      const f = el.closest('.field') || el.closest('.consent');
      if (f) f.classList.remove('invalid');
    };
    form.querySelectorAll('input,select,textarea').forEach(el => {
      el.addEventListener('input', () => clearErr(el));
      el.addEventListener('change', () => clearErr(el));
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      let ok = true;
      const name = form.querySelector('#f-name');
      const email = form.querySelector('#f-email');
      const topic = form.querySelector('#f-topic');
      const msg = form.querySelector('#f-msg');
      const consent = form.querySelector('#f-consent');

      if (name.value.trim().length < 3){ showErr(name,'Podaj imię i nazwisko.'); ok=false; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())){ showErr(email,'Podaj poprawny adres e-mail.'); ok=false; }
      if (!topic.value){ showErr(topic,'Wybierz temat.'); ok=false; }
      if (msg.value.trim().length < 10){ showErr(msg,'Wiadomość jest zbyt krótka (min. 10 znaków).'); ok=false; }
      if (!consent.checked){ consent.closest('.consent').classList.add('invalid'); ok=false; }

      if (!ok){
        const firstBad = form.querySelector('.invalid');
        if (firstBad) firstBad.querySelector('input,select,textarea')?.focus();
        return;
      }

      form.style.display = 'none';
      document.getElementById('formOk').classList.add('show');
    });
  }

  /* ---- Active nav link highlight (rect-based) ---- */
  const sections = [...document.querySelectorAll('section[id]')];
  const links = [...document.querySelectorAll('.nav__links a')];
  const spy = () => {
    const mid = window.innerHeight * 0.4;
    let current = '';
    for (const s of sections){
      const r = s.getBoundingClientRect();
      if (r.top <= mid && r.bottom >= mid) current = s.id;
    }
    links.forEach(l => l.style.opacity = (current && l.getAttribute('href') === '#' + current) ? '1' : '');
  };
  window.addEventListener('scroll', spy, {passive:true});
  spy();

  /* ---- Current year ---- */
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---- Expandable news posts ---- */
  document.querySelectorAll('.news-card__more').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.news-card');
      const open = card.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
})();
