/* ============================================================================
   Mohamed Hany Reda — portfolio behaviour
   No framework, no build step. Everything degrades without JS except the modal.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduce = reduceMQ.matches;
  reduceMQ.addEventListener('change', function (e) { reduce = e.matches; });

  var LANGS = ['en', 'ru', 'ar'];
  var RTL = { ar: true };
  var STORE = 'hr-lang';

  /* ── PROJECT DATA ──────────────────────────────────────────────────────
     Only `img` entries that exist on disk are referenced. Projects without a
     real screenshot fall back to a generated abstract visual (see `icon`). */
  var PROJECTS = [
    {
      id: 'p1', accent: 'var(--cyan)', repo: 'https://github.com/Hany15/Amazon-sorting-center-digital-twin',
      img: 'twin-ops', shots: ['twin-ops', 'twin-3d'], icon: 'fa-boxes-packing',
      tags: ['Python', 'PyTorch', 'PPO', 'Multi-Agent RL', 'LSTM', 'Discrete-Event Simulation', 'Three.js', 'Pygame', 'SQLite', 'Pytest'],
      metrics: [['100,000/hr', 'p1.m1'], ['96,400/hr', 'p1.m2'], ['400', 'p1.m3'], ['530+', 'p1.m4']],
      highlights: 8
    },
    {
      id: 'p2', accent: 'var(--violet)', repo: 'https://github.com/Hany15/drone-rl-flight-control',
      img: 'drone', shots: ['drone'], icon: 'fa-helicopter',
      tags: ['Python', 'PyTorch', 'PPO', 'LSTM', 'Safe-RL', 'Gymnasium', 'ONNX', 'Docker'],
      metrics: [], highlights: 8, disclaimer: 'p2.disclaimer'
    },
    {
      id: 'p3', accent: 'var(--pink)', repo: 'https://github.com/Hany15/ai-evolution-racing-lab',
      img: 'racing-1', shots: ['racing-1', 'racing-2'], icon: 'fa-flag-checkered',
      tags: ['Python', 'PyTorch', 'Stable-Baselines3', 'PPO', 'SAC', 'A2C', 'Gymnasium', 'Pygame', 'SQLite'],
      metrics: [], highlights: 8
    },
    {
      id: 'p4', accent: 'var(--green)', repo: 'https://github.com/Hany15/AI-Medical-Assistant-',
      img: 'fracture-result', shots: ['fracture-result', 'fracture-hero'], icon: 'fa-x-ray',
      tags: ['Python', 'PyTorch', 'EfficientNet-B0', 'Grad-CAM', 'OpenCV', 'Streamlit', 'SQLite', 'ReportLab'],
      metrics: [['90.21%', 'p4.m1'], ['89.31%', 'p4.m2'], ['76.67%', 'p4.m3'], ['63.89%', 'p4.m4'], ['69.70%', 'p4.m5'], ['4,083', 'p4.m6']],
      highlights: 8, disclaimer: 'p4.disclaimer'
    },
    {
      id: 'p5', accent: 'var(--amber)', repo: 'https://github.com/Hany15/hms-ai-erp-platform',
      img: 'hms-dashboard', shots: ['hms-dashboard', 'hms-invoice'], svg: true, icon: 'fa-building-shield',
      tags: ['Python', 'FastAPI', 'PostgreSQL', 'SQLAlchemy', 'Redis', 'React', 'Docker'],
      metrics: [], highlights: 8
    },
    {
      id: 'p6', accent: 'var(--cyan)', repo: 'https://github.com/Hany15/-AI-Powered-Air-Defense-Simulation-Platform-',
      img: 'multiagent-1', shots: ['multiagent-1', 'multiagent-2'], icon: 'fa-satellite-dish',
      tags: ['Python', 'PyTorch', 'Multi-Agent RL', 'PySide6', 'SQLite'],
      metrics: [], highlights: 8
    }
  ];
  window.PROJECTS = PROJECTS;

  /* ── i18n ──────────────────────────────────────────────────────────────── */
  var current = 'en';
  function t(key) {
    var d = window.I18N[current];
    if (d && Object.prototype.hasOwnProperty.call(d, key)) return d[key];
    var en = window.I18N.en;
    if (en && Object.prototype.hasOwnProperty.call(en, key)) return en[key];
    return key; // last resort: show the key rather than "undefined"
  }
  window.t = t;

  /* The page is pre-rendered in its own language and lives at its own URL
     (/, /ru/, /ar/), so the document is the source of truth — never re-render
     text on load or we would overwrite /ru/ with whatever localStorage says. */
  function pageLang() {
    var l = (document.documentElement.getAttribute('lang') || 'en').slice(0, 2);
    return LANGS.indexOf(l) > -1 ? l : 'en';
  }

  function applyLang(lang) {
    if (LANGS.indexOf(lang) === -1) lang = 'en';
    current = lang;
    if (modalOpenId) renderModal(modalOpenId);
    try { localStorage.setItem(STORE, lang); } catch (e) {}
  }
  window.applyLang = applyLang;

  function setMeta(attr, key, val) {
    var el = document.head.querySelector('meta[' + attr + '="' + key + '"]');
    if (!el) { el = document.createElement('meta'); el.setAttribute(attr, key); document.head.appendChild(el); }
    el.setAttribute('content', val);
  }

  function updateJsonLd() {
    var el = document.getElementById('jsonld');
    if (!el) return;
    el.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Person',
      name: 'Mohamed Hany Reda',
      jobTitle: t('role.full'),
      description: t('meta.desc'),
      email: 'mailto:developeractionobject@gmail.com',
      url: 'https://hany15.github.io/Hany-Reda-Portfolio/',
      sameAs: ['https://github.com/Hany15', 'https://www.linkedin.com/in/hany-reda-854667417'],
      knowsAbout: ['Reinforcement Learning', 'Digital Twins', 'Simulation', 'Autonomous Systems',
                   'Explainable AI', 'Computer Vision', 'Software Architecture']
    });
  }

  /* ── COUNTERS ──────────────────────────────────────────────────────────── */
  var counted = {};
  function fmt(v, dec) {
    try { return v.toLocaleString(current === 'ar' ? 'en-US' : current,
      { minimumFractionDigits: dec, maximumFractionDigits: dec }); }
    catch (e) { return dec ? v.toFixed(dec) : String(Math.round(v)); }
  }
  function renderCounters() {
    document.querySelectorAll('[data-count]').forEach(function (el) {
      var target = parseFloat(el.dataset.count);
      var dec = (el.dataset.count.split('.')[1] || '').length;
      var suffix = el.dataset.suffix || '';
      if (counted[el.dataset.count + suffix]) el.textContent = fmt(target, dec) + suffix;
    });
  }
  function animateCount(el) {
    var raw = el.dataset.count, target = parseFloat(raw);
    var dec = (raw.split('.')[1] || '').length, suffix = el.dataset.suffix || '';
    counted[raw + suffix] = true;
    if (reduce) { el.textContent = fmt(target, dec) + suffix; return; }
    var start = null, dur = 1300;
    (function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * e, dec) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = fmt(target, dec) + suffix;
    })(performance.now());
  }

  /* ── REVEAL + COUNTERS + PROCESS + ACTIVE NAV ──────────────────────────── */
  function initObservers() {
    var revealIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); revealIO.unobserve(e.target); } });
    }, { threshold: 0.06, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { revealIO.observe(el); });

    var countIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { animateCount(e.target); countIO.unobserve(e.target); } });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-count]').forEach(function (el) { countIO.observe(el); });

    // active nav section
    var links = [].slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
    var ids = links.map(function (a) { return a.getAttribute('href').slice(1); });
    var secs = ids.map(function (id) { return document.getElementById(id); }).filter(Boolean);
    if (secs.length) {
      var navIO = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          links.forEach(function (a) {
            a.setAttribute('aria-current', String(a.getAttribute('href') === '#' + e.target.id));
          });
        });
      }, { rootMargin: '-45% 0px -50% 0px' });
      secs.forEach(function (s) { navIO.observe(s); });
    }
  }

  /* ── PROCESS PIPELINE ──────────────────────────────────────────────────── */
  function initProcess() {
    var wrap = document.querySelector('.process');
    if (!wrap) return;
    var steps = [].slice.call(wrap.querySelectorAll('.step'));
    var fill = wrap.querySelector('.process-fill');
    var ticking = false;
    function update() {
      ticking = false;
      var r = wrap.getBoundingClientRect();
      var vh = window.innerHeight;
      var p = (vh * 0.72 - r.top) / r.height;
      p = Math.max(0, Math.min(1, p));
      if (fill) fill.style.height = (p * 100) + '%';
      var upto = Math.round(p * steps.length);
      steps.forEach(function (s, i) { s.classList.toggle('active', i < upto); });
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  /* ── NAV ───────────────────────────────────────────────────────────────── */

  function langHrefsForFileProtocol() {
    if (location.protocol !== 'file:') return;
    document.querySelectorAll('.lang-btn, .brand, a[href$="/"]').forEach(function (a) {
      var h = a.getAttribute('href');
      if (h && h.slice(-1) === '/') a.setAttribute('href', h + 'index.html');
    });
  }

  function initNav() {
    var nav = document.getElementById('nav');
    var bar = document.getElementById('progress');
    var hint = document.querySelector('.scroll-hint');
    var ticking = false;
    function onScroll() {
      ticking = false;
      var y = window.scrollY;
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (bar) bar.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
      if (nav) nav.classList.toggle('scrolled', y > 24);
      if (hint) hint.style.opacity = y > 80 ? '0' : '1';
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
    }, { passive: true });
    onScroll();

    var toggle = document.querySelector('.nav-toggle');
    var menu = document.getElementById('mobile-menu');
    if (toggle && menu) {
      toggle.addEventListener('click', function () {
        var open = menu.classList.toggle('open');
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('data-i18n-attr', 'aria-label:' + (open ? 'nav.close' : 'nav.menu'));
        toggle.setAttribute('aria-label', t(open ? 'nav.close' : 'nav.menu'));
        toggle.querySelector('i').className = (open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars');
      });
      menu.addEventListener('click', function (e) {
        if (e.target.closest('a')) {
          menu.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.querySelector('i').className = 'fa-solid fa-bars';
        }
      });
    }

    /* Language links point at directory URLs (/, /ru/, /ar/) — correct for a
       web server and for the canonical/hreflang tags. Opened straight from
       disk with file://, a directory URL renders the folder listing instead of
       index.html, so rewrite the hrefs in that case only. */
    langHrefsForFileProtocol();

    document.querySelectorAll('.lang-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        try { localStorage.setItem(STORE, b.dataset.lang); } catch (e) {}
      });
    });
  }

  /* ── PROJECT MODAL ─────────────────────────────────────────────────────── */
  var modalOpenId = null, lastFocus = null;
  var backdrop, modalEl;

  var ASSET_BASE = document.documentElement.getAttribute('data-asset-base') || '';

  function imgTag(name, altKey, svg, cls) {
    if (svg) return '<img src="' + ASSET_BASE + 'assets/img/projects/' + name + '.svg" alt="' + esc(t(altKey)) + '" loading="eager" class="' + (cls || '') + '">';
    return '<img src="' + ASSET_BASE + 'assets/img/projects/' + name + '-1200.webp" ' +
      'srcset="' + ASSET_BASE + 'assets/img/projects/' + name + '-600.webp 600w, ' + ASSET_BASE + 'assets/img/projects/' + name + '-1200.webp 1200w" ' +
      'sizes="(max-width: 880px) 100vw, 860px" ' +
      'alt="' + esc(t(altKey)) + '" loading="eager" decoding="async" class="' + (cls || '') + '">';
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }

  function renderModal(id) {
    var p = PROJECTS.filter(function (x) { return x.id === id; })[0];
    if (!p) return;
    var hi = '';
    for (var i = 1; i <= p.highlights; i++) hi += '<li>' + esc(t(p.id + '.h' + i)) + '</li>';
    var shots = p.shots.map(function (s, idx) {
      return imgTag(s, p.id + (idx === 0 ? '.alt' : '.alt2'), p.svg);
    }).join('');

    modalEl.innerHTML =
      '<div class="modal-hero">' + imgTag(p.img, p.id + '.alt', p.svg) +
        '<button class="modal-close" type="button" aria-label="' + esc(t('projects.close')) + '"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button>' +
      '</div>' +
      '<div class="modal-body">' +
        '<p class="modal-kicker" style="color:' + p.accent + '">' + esc(t(p.id + '.kicker')) + '</p>' +
        '<h2 class="modal-title" id="modal-title">' + esc(t(p.id + '.title')) + '</h2>' +
        '<div class="modal-section"><h4>' + esc(t('projects.overview')) + '</h4><p>' + esc(t(p.id + '.desc')) + '</p></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.problem')) + '</h4><p>' + esc(t(p.id + '.problem')) + '</p></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.approach')) + '</h4><p>' + esc(t(p.id + '.approach')) + '</p></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.architecture')) + '</h4><p>' + esc(t(p.id + '.arch')) + '</p></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.results')) + '</h4><ul>' + hi + '</ul></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.challenges')) + '</h4><p>' + esc(t(p.id + '.challenges')) + '</p></div>' +
        '<div class="modal-section"><h4>' + esc(t('projects.tech')) + '</h4><div class="tags">' +
          p.tags.map(function (x) { return '<span class="tag">' + esc(x) + '</span>'; }).join('') + '</div></div>' +
        (p.shots.length > 1 ? '<div class="modal-section"><h4>' + esc(t('projects.screenshot')) + '</h4><div class="modal-shots">' + shots + '</div></div>' : '') +
        (p.disclaimer ? '<div class="disclaimer"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i><span>' + esc(t(p.disclaimer)) + '</span></div>' : '') +
        '<div class="proj-actions" style="margin-top:26px">' +
          '<a class="btn btn-primary btn-sm" href="' + p.repo + '" target="_blank" rel="noopener"><i class="fa-brands fa-github" aria-hidden="true"></i>' + esc(t('projects.github')) + '</a>' +
        '</div>' +
      '</div>';

    modalEl.querySelector('.modal-close').addEventListener('click', closeModal);
  }

  function openModal(id) {
    lastFocus = document.activeElement;
    modalOpenId = id;
    renderModal(id);
    backdrop.classList.add('open');
    backdrop.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    var c = modalEl.querySelector('.modal-close');
    if (c) c.focus();
  }
  function closeModal() {
    if (!modalOpenId) return;
    modalOpenId = null;
    backdrop.classList.remove('open');
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  window.closeModal = closeModal;

  function initModal() {
    backdrop = document.getElementById('modal-backdrop');
    modalEl = document.getElementById('modal');
    if (!backdrop || !modalEl) return;
    backdrop.addEventListener('click', function (e) { if (e.target === backdrop) closeModal(); });
    document.addEventListener('keydown', function (e) {
      if (!modalOpenId) return;
      if (e.key === 'Escape') { closeModal(); return; }
      if (e.key !== 'Tab') return;
      // focus trap
      var f = modalEl.querySelectorAll('a[href],button,[tabindex]:not([tabindex="-1"])');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-modal]');
      if (b) { e.preventDefault(); openModal(b.getAttribute('data-modal')); }
    });
  }

  /* ── BACKGROUND CANVAS ─────────────────────────────────────────────────────
     A light neural-graph field. Pauses when off-screen or the tab is hidden,
     throttled to 30fps, and renders a single static frame under reduced motion. */
  function initCanvas() {
    var cv = document.getElementById('bg-canvas');
    if (!cv) return;
    var ctx = cv.getContext('2d');
    var W, H, nodes = [], dpr = Math.min(window.devicePixelRatio || 1, 2);
    var pointer = { x: -9999, y: -9999 };

    function size() {
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = W * dpr; cv.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function build() {
      var n = W < 640 ? 16 : W < 1100 ? 26 : 38;
      nodes = [];
      for (var i = 0; i < n; i++) nodes.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.16, vy: (Math.random() - 0.5) * 0.16
      });
    }
    size(); build();
    window.addEventListener('resize', function () { size(); build(); draw(); }, { passive: true });

    if (window.matchMedia('(hover:hover) and (pointer:fine)').matches) {
      window.addEventListener('pointermove', function (e) { pointer.x = e.clientX; pointer.y = e.clientY; }, { passive: true });
      window.addEventListener('pointerleave', function () { pointer.x = pointer.y = -9999; }, { passive: true });
    }

    var LINK = 150;
    function draw() {
      ctx.clearRect(0, 0, W, H);
      var i, j;
      if (!reduce) {
        for (i = 0; i < nodes.length; i++) {
          var n = nodes[i];
          n.x += n.vx; n.y += n.vy;
          if (n.x < 0 || n.x > W) n.vx *= -1;
          if (n.y < 0 || n.y > H) n.vy *= -1;
        }
      }
      for (i = 0; i < nodes.length; i++) {
        for (j = i + 1; j < nodes.length; j++) {
          var dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < LINK) {
            ctx.strokeStyle = 'rgba(34,211,238,' + ((1 - d / LINK) * 0.16).toFixed(3) + ')';
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(nodes[j].x, nodes[j].y); ctx.stroke();
          }
        }
        var p = nodes[i];
        var pdx = p.x - pointer.x, pdy = p.y - pointer.y;
        var near = Math.sqrt(pdx * pdx + pdy * pdy) < 130;
        ctx.beginPath(); ctx.arc(p.x, p.y, near ? 2.6 : 1.5, 0, Math.PI * 2);
        ctx.fillStyle = near ? 'rgba(34,211,238,.85)' : 'rgba(139,92,246,.55)';
        ctx.fill();
      }
      running = false;
      if (!reduce && onScreen && !document.hidden) schedule();
    }

    var running = false, onScreen = true, last = 0;
    function schedule() {
      if (running) return;
      running = true;
      requestAnimationFrame(function (ts) {
        if (ts - last < 33) { running = false; schedule(); return; }  // ~30fps
        last = ts; draw();
      });
    }
    var hero = document.getElementById('hero');
    if (hero && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        onScreen = es[0].isIntersecting;
        if (onScreen && !reduce && !document.hidden) schedule();
      }, { threshold: 0 }).observe(hero);
    }
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && onScreen && !reduce) schedule();
    });
    draw();
  }

  /* ── BOOT ──────────────────────────────────────────────────────────────── */
  function boot() {
    applyLang(pageLang());
    initNav();
    initModal();
    initObservers();
    initProcess();
    initCanvas();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
