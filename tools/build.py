#!/usr/bin/env python3
"""Generates index.html. Keeping the repetitive project/skill markup in one
place means the six project blocks can't drift out of sync with each other."""
import io, os, re

PROJECTS = [
    # id, accent,        icon,                repo,                                                              img,               svg,   metrics,                                                              disclaimer
    ("p1", "var(--cyan)",   "fa-boxes-packing",  "https://github.com/Hany15/Amazon-sorting-center-digital-twin",     "twin-ops",        False,
     [("100,000/hr","p1.m1"),("96,400/hr","p1.m2"),("400","p1.m3"),("530+","p1.m4")], None,
     ["Python","PyTorch","PPO","Multi-Agent RL","LSTM","Discrete-Event Simulation","Three.js","Pygame","SQLite","Pytest"]),
    ("p2", "var(--violet)", "fa-helicopter",     "https://github.com/Hany15/drone-rl-flight-control",                "drone",           False,
     [], "p2.disclaimer",
     ["Python","PyTorch","PPO","LSTM","Safe-RL","Gymnasium","ONNX","Docker"]),
    ("p3", "var(--pink)",   "fa-flag-checkered", "https://github.com/Hany15/ai-evolution-racing-lab",                "racing-1",        False,
     [], None,
     ["Python","PyTorch","Stable-Baselines3","PPO","SAC","A2C","Gymnasium","Pygame","SQLite"]),
    ("p4", "var(--green)",  "fa-x-ray",          "https://github.com/Hany15/AI-Medical-Assistant-",                  "fracture-result", False,
     [("90.21%","p4.m1"),("89.31%","p4.m2"),("76.67%","p4.m3"),("63.89%","p4.m4"),("69.70%","p4.m5"),("4,083","p4.m6")], "p4.disclaimer",
     ["Python","PyTorch","EfficientNet-B0","Grad-CAM","OpenCV","Streamlit","SQLite","ReportLab"]),
    ("p5", "var(--amber)",  "fa-building-shield","https://github.com/Hany15/hms-ai-erp-platform",                    "hms-dashboard",   True,
     [], None,
     ["Python","FastAPI","PostgreSQL","SQLAlchemy","Redis","React","Docker"]),
    ("p6", "var(--cyan)",   "fa-satellite-dish", "https://github.com/Hany15/-AI-Powered-Air-Defense-Simulation-Platform-","multiagent-1",False,
     [], None,
     ["Python","PyTorch","Multi-Agent RL","PySide6","SQLite"]),
]

CAPS = [
    ("cap.ai",      "fa-brain",           "var(--green)",  ["PyTorch","EfficientNet","Computer Vision","Grad-CAM","OpenCV","Scikit-learn","Albumentations","Explainable AI"]),
    ("cap.rl",      "fa-diagram-project", "var(--violet)", ["PPO","SAC","A2C","Multi-Agent RL","CTDE","Safe-RL","LSTM Policies","Self-Play","Domain Randomization"]),
    ("cap.sim",     "fa-cubes",           "var(--pink)",   ["Discrete-Event Simulation","Entity-Component-System","Deterministic Replay","Procedural Generation","Sensor Simulation","Operations Research"]),
    ("cap.backend", "fa-server",          "var(--cyan)",   ["Python","FastAPI","PostgreSQL","SQLAlchemy","Redis","Docker","Clean Architecture","Multi-Tenant Systems"]),
    ("cap.viz",     "fa-display",         "var(--amber)",  ["Three.js","Pygame","PySide6","Streamlit","Flutter","Dart","Unreal Engine 5","Firebase"]),
]

STATS = [
    ("3",      "+",  "var(--cyan)",   "impact.years",      "impact.years.note"),
    ("10",     "",   "var(--violet)", "impact.team",       "impact.team.note"),
    ("13000",  " USD","var(--green)", "impact.budget",     "impact.budget.note"),
    ("12",     "+",  "var(--cyan)",   "impact.projects",   "impact.projects.note"),
    ("530",    "+",  "var(--violet)", "impact.tests",      "impact.tests.note"),
    ("96400",  "",   "var(--pink)",   "impact.throughput", "impact.throughput.note"),
    ("90.21",  "%",  "var(--green)",  "impact.accuracy",   "impact.accuracy.note"),
    ("4083",   "",   "var(--amber)",  "impact.images",     "impact.images.note"),
]

RANGE = [
    ("r1", "meetsync-1", "fa-calendar-days", "var(--cyan)",   "https://github.com/Hany15/MeetSync-flutter", None,
     ["Flutter","Dart","Cross-Platform"]),
    ("r2", "music-1",    "fa-music",         "var(--green)",  "https://github.com/Hany15/Music-App-flutter", None,
     ["Flutter","Dart","UI Animation"]),
    ("r3", None,         "fa-cube",          "var(--violet)", "https://github.com/Hany15/Online-game-for-phones-AAA", None,
     ["Unreal Engine 5","C++","Blueprints"]),
    ("r4", None,         "fa-gift",          "var(--pink)",   "https://github.com/Hany15/Awebsite-with-a-new-concept", "https://auragift.web.app",
     ["JavaScript","Firebase"]),
]

# Professional Strengths.  Bar widths are visual weight only — no numeric
# proficiency is displayed, so nothing reads as a "100% mastery" claim.
LANGS_SPOKEN = [
    ("ps.lang.ar", "AR", "ps.level.native", "var(--green)",  92),
    ("ps.lang.en", "EN", "ps.level.c2",     "var(--cyan)",   88),
    ("ps.lang.ru", "RU", "ps.level.b2",     "var(--violet)", 66),
]

STYLE_CARDS = [
    ("ps.s1", "fa-hand-holding-heart", "var(--cyan)"),
    ("ps.s2", "fa-wind",               "var(--violet)"),
    ("ps.s3", "fa-shuffle",            "var(--pink)"),
    ("ps.s4", "fa-people-group",       "var(--green)"),
    ("ps.s5", "fa-comments",           "var(--amber)"),
    ("ps.s6", "fa-bullseye",           "var(--cyan)"),
]

REPOS = [
    ("Amazon-sorting-center-digital-twin", "https://github.com/Hany15/Amazon-sorting-center-digital-twin"),
    ("drone-rl-flight-control",            "https://github.com/Hany15/drone-rl-flight-control"),
    ("ai-evolution-racing-lab",            "https://github.com/Hany15/ai-evolution-racing-lab"),
    ("AI-Medical-Assistant-",              "https://github.com/Hany15/AI-Medical-Assistant-"),
    ("hms-ai-erp-platform",                "https://github.com/Hany15/hms-ai-erp-platform"),
    ("MeetSync-flutter",                   "https://github.com/Hany15/MeetSync-flutter"),
]

def img(name, alt_key, svg=False, cls=""):
    if svg:
        return (f'<img src="assets/img/projects/{name}.svg" data-i18n-attr="alt:{alt_key}" alt="" '
                f'loading="lazy" decoding="async" class="{cls}">')
    return (f'<img src="assets/img/projects/{name}-1200.webp" '
            f'srcset="assets/img/projects/{name}-600.webp 600w, assets/img/projects/{name}-1200.webp 1200w" '
            f'sizes="(max-width: 880px) 100vw, 640px" '
            f'data-i18n-attr="alt:{alt_key}" alt="" loading="lazy" decoding="async" class="{cls}">')

def build():
    o = io.StringIO(); w = o.write

    w('''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Mohamed Hany Reda | AI &amp; Software Engineer</title>
<meta name="description" content="AI and Software Engineer specializing in reinforcement learning, simulation, digital twins, autonomous systems, explainable AI, and production software architecture.">
<meta name="author" content="Mohamed Hany Reda">
<link rel="canonical" href="https://hany15.github.io/Hany-Reda-Portfolio/">

<meta property="og:type" content="website">
<meta property="og:url" content="https://hany15.github.io/Hany-Reda-Portfolio/">
<meta property="og:title" content="Mohamed Hany Reda | AI &amp; Software Engineer">
<meta property="og:description" content="AI and Software Engineer specializing in reinforcement learning, simulation, digital twins, autonomous systems, explainable AI, and production software architecture.">
<meta property="og:image" content="https://hany15.github.io/Hany-Reda-Portfolio/assets/img/projects/twin-ops-1200.webp">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Mohamed Hany Reda | AI &amp; Software Engineer">
<meta name="twitter:description" content="AI and Software Engineer specializing in reinforcement learning, simulation, digital twins, autonomous systems, explainable AI, and production software architecture.">
<meta name="twitter:image" content="https://hany15.github.io/Hany-Reda-Portfolio/assets/img/projects/twin-ops-1200.webp">
<meta name="theme-color" content="#04070f">
<script type="application/ld+json" id="jsonld">{}</script>

<script async src="https://www.googletagmanager.com/gtag/js?id=G-1WG4306FK6"></script>
<script>
  window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
  gtag('js',new Date());gtag('config','G-1WG4306FK6',{send_page_view:true});
  function trackContact(m){gtag('event','contact_click',{event_category:'Contact',event_label:m});}
  function trackProject(n){gtag('event','project_open',{event_category:'Projects',event_label:n});}
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="stylesheet" href="assets/css/main.css?v=09c6f1a6">
</head>
<body>

<a class="skip-link" href="#main" data-i18n="a11y.skip">Skip to main content</a>
<div id="progress" role="progressbar" aria-hidden="true" data-i18n-attr="aria-label:a11y.progress"></div>
<canvas id="bg-canvas" aria-hidden="true"></canvas>
<div class="grid-overlay" aria-hidden="true"></div>

<!-- ═══ NAV ═══ -->
<header id="nav">
  <div class="nav-inner">
    <a class="brand" href="#hero">
      <span class="brand-name">MOHAMED HANY REDA</span>
      <span class="brand-role" data-i18n="role.full"></span>
    </a>
    <nav class="nav-links" aria-label="Primary">
      <a href="#hero" data-i18n="nav.home"></a>
      <a href="#delivery" data-i18n="deliv.eyebrow"></a>
      <a href="#projects" data-i18n="nav.projects"></a>
      <a href="#capabilities" data-i18n="nav.capabilities"></a>
      <a href="#process" data-i18n="nav.process"></a>
      <a href="#background" data-i18n="nav.about"></a>
      <a href="#contact" data-i18n="nav.contact"></a>
    </nav>
    <div class="nav-right">
      <div class="lang-switch" role="group" data-i18n-attr="aria-label:nav.langLabel" aria-label="Select language">
        <button class="lang-btn" type="button" data-lang="en" aria-pressed="true">EN</button>
        <button class="lang-btn" type="button" data-lang="ru" aria-pressed="false">RU</button>
        <button class="lang-btn" type="button" data-lang="ar" aria-pressed="false">AR</button>
      </div>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu"
              data-i18n-attr="aria-label:nav.menu" aria-label="Open menu"><i class="fa-solid fa-bars" aria-hidden="true"></i></button>
    </div>
  </div>
</header>
<nav id="mobile-menu" aria-label="Mobile">
  <a href="#hero" data-i18n="nav.home"></a>
  <a href="#projects" data-i18n="nav.projects"></a>
  <a href="#capabilities" data-i18n="nav.capabilities"></a>
  <a href="#process" data-i18n="nav.process"></a>
  <a href="#background" data-i18n="nav.about"></a>
  <a href="#contact" data-i18n="nav.contact"></a>
</nav>

<main id="main">

<!-- ═══ HERO ═══ -->
<section id="hero">
  <img class="hero-photo" src="assets/img/profile-640.webp"
       srcset="assets/img/profile-320.webp 320w, assets/img/profile-640.webp 640w"
       sizes="132px" width="132" height="132" fetchpriority="high"
       data-i18n-attr="alt:photo.alt" alt="">
  <p class="hero-badge"><i aria-hidden="true"></i><span data-i18n="hero.badge"></span></p>
  <h1 class="hero-name">MOHAMED HANY REDA</h1>
  <p class="hero-role" data-i18n="role.full"></p>
  <p class="hero-stack" data-i18n="role.stack"></p>
  <p class="hero-headline" data-i18n="hero.headline"></p>
  <p class="hero-support" data-i18n="hero.support"></p>
  <p class="hero-spec" data-i18n="hero.spec"></p>
  <div class="avail-strip">
    <span class="avail-chip live"><span class="avail-dot" aria-hidden="true"></span><span data-i18n="avail.status"></span></span>
    <span class="avail-chip"><i class="fa-solid fa-laptop" aria-hidden="true"></i><span data-i18n="avail.mode"></span></span>
    <span class="avail-chip"><i class="fa-solid fa-plane" aria-hidden="true"></i><span data-i18n="avail.trips"></span></span>
    <span class="avail-chip"><i class="fa-solid fa-briefcase" aria-hidden="true"></i><span data-i18n="avail.employment"></span></span>
  </div>
  <div class="hero-cta">
    <a class="btn btn-primary" href="#projects"><i class="fa-solid fa-layer-group" aria-hidden="true"></i><span data-i18n="hero.cta.projects"></span></a>
    <a class="btn btn-ghost" href="https://github.com/Hany15" target="_blank" rel="noopener" onclick="trackContact('GitHub-Hero')"><i class="fa-brands fa-github" aria-hidden="true"></i><span data-i18n="hero.cta.github"></span></a>
    <a class="btn btn-secondary" href="#contact"><i class="fa-solid fa-paper-plane" aria-hidden="true"></i><span data-i18n="hero.cta.contact"></span></a>
  </div>
  <div class="cv-row">
    <span class="cv-label"><i class="fa-solid fa-file-arrow-down" aria-hidden="true"></i><span data-i18n="cv.label"></span></span>
    <a class="cv-btn" href="cv/cv_en.pdf" download="Mohamed-Hany-Reda-CV-EN.pdf"
       data-i18n-attr="aria-label:cv.aria.en" onclick="trackContact('CV-EN')">
      <span class="flag">EN</span><span data-i18n="cv.en"></span></a>
    <a class="cv-btn" href="cv/cv_ru.pdf" download="Mohamed-Hany-Reda-CV-RU.pdf"
       data-i18n-attr="aria-label:cv.aria.ru" onclick="trackContact('CV-RU')">
      <span class="flag">RU</span><span data-i18n="cv.ru"></span></a>
    <span class="cv-hint" data-i18n="cv.hint"></span>
    <span class="cv-onepage">
      <span data-i18n="cv.onepage"></span>
      <a href="cv/cv_en_1page.pdf" download="Mohamed-Hany-Reda-CV-EN-1page.pdf"
         data-i18n-attr="aria-label:cv.aria.en1" onclick="trackContact('CV-EN-1page')">EN</a>
      <span class="sep" aria-hidden="true">·</span>
      <a href="cv/cv_ru_1page.pdf" download="Mohamed-Hany-Reda-CV-RU-1page.pdf"
         data-i18n-attr="aria-label:cv.aria.ru1" onclick="trackContact('CV-RU-1page')">RU</a>
    </span>
    <span class="cv-onepage cv-targeted">
      <span data-i18n="cv.targeted"></span>
      <span class="cv-tset"><span class="cv-tlabel" data-i18n="cv.fs"></span>
        <a href="cv/cv_fullstack_en.pdf" download="Mohamed-Hany-Reda-CV-FullStack-EN.pdf" onclick="trackContact('CV-FS-EN')">EN</a>
        <span class="sep" aria-hidden="true">·</span>
        <a href="cv/cv_fullstack_ru.pdf" download="Mohamed-Hany-Reda-CV-FullStack-RU.pdf" onclick="trackContact('CV-FS-RU')">RU</a></span>
      <span class="cv-tset"><span class="cv-tlabel" data-i18n="cv.ai"></span>
        <a href="cv/cv_ai_en.pdf" download="Mohamed-Hany-Reda-CV-AI-EN.pdf" onclick="trackContact('CV-AI-EN')">EN</a>
        <span class="sep" aria-hidden="true">·</span>
        <a href="cv/cv_ai_ru.pdf" download="Mohamed-Hany-Reda-CV-AI-RU.pdf" onclick="trackContact('CV-AI-RU')">RU</a></span>
    </span>
  </div>
  <div class="scroll-hint" aria-hidden="true"><span data-i18n="hero.scroll"></span><span class="chev"></span></div>
</section>

''')

    # ── Professional Strengths (after the hero / personal intro) ────────────
    w('''<!-- ═══ PROFESSIONAL STRENGTHS ═══ -->
<section class="section" id="strengths">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="ps.eyebrow"></span>
    <h2 class="sec-title" data-i18n="ps.title"></h2>
    <p class="sec-sub" data-i18n="ps.sub"></p>
  </div>

  <div class="ps-band card reveal">
    <div class="ps-head">
      <div class="ps-ico" style="background:color-mix(in srgb,var(--green) 12%,transparent);color:var(--green)"><i class="fa-solid fa-language" aria-hidden="true"></i></div>
      <h3 class="ps-card-title" data-i18n="ps.lang.title"></h3>
    </div>
    <p class="ps-desc" style="margin-bottom:0" data-i18n="ps.lang.desc"></p>
    <div class="lang-grid">
''')
    for key, code, level, color, weight in LANGS_SPOKEN:
        w(f'''      <div class="lang-card">
        <div class="lang-top">
          <span class="lang-code" style="color:{color};background:color-mix(in srgb,{color} 10%,transparent)">{code}</span>
          <span>
            <span class="lang-nm2" data-i18n="{key}"></span>
            <span class="lang-lvl2" style="color:{color}" data-i18n="{level}"></span>
          </span>
        </div>
        <p class="lang-ctx" data-i18n="{key}Ctx"></p>
        <span class="lang-meter" aria-hidden="true"><i style="--w:{weight}%;background:{color}"></i></span>
      </div>
''')
    w('''    </div>
    <p class="lang-foot" data-i18n="ps.lang.footnote"></p>
  </div>

  <div class="ps-band card reveal">
    <div class="ps-head">
      <div class="ps-ico" style="background:color-mix(in srgb,var(--violet) 12%,transparent);color:var(--violet)"><i class="fa-solid fa-diagram-project" aria-hidden="true"></i></div>
      <h3 class="ps-card-title" data-i18n="ps.pm.title"></h3>
    </div>
    <p class="ps-desc" style="margin-bottom:0" data-i18n="ps.pm.desc"></p>
    <div class="comp-grid">
''')
    for n in range(1, 11):
        w(f'''        <div class="comp">
          <span class="comp-dot" aria-hidden="true">{n:02d}</span>
          <span>
            <span class="comp-nm" data-i18n="ps.pm.c{n}"></span>
            <span class="comp-d" data-i18n="ps.pm.c{n}d"></span>
          </span>
        </div>
''')
    w('''    </div>
  </div>

  <div class="ps-advantage reveal">
    <div class="ps-head">
      <div class="ps-ico" style="background:color-mix(in srgb,var(--cyan) 14%,transparent);color:var(--cyan)"><i class="fa-solid fa-code-branch" aria-hidden="true"></i></div>
      <h3 class="ps-card-title" data-i18n="ps.adv.title"></h3>
    </div>
    <p class="ps-desc" style="margin-bottom:0" data-i18n="ps.adv.desc"></p>
    <ul class="adv-list">
''')
    for n in range(1, 8):
        w(f'      <li data-i18n="ps.adv.b{n}"></li>\n')
    w('''    </ul>
  </div>

  <p class="ps-sub-title" data-i18n="ps.style.title"></p>
  <div class="style-grid">
''')
    for i, (key, icon, color) in enumerate(STYLE_CARDS):
        w(f'''    <div class="style-card card reveal" data-d="{min(i,4)}">
      <div class="style-ico" style="background:color-mix(in srgb,{color} 12%,transparent);color:{color}"><i class="fa-solid {icon}" aria-hidden="true"></i></div>
      <h3 class="style-nm" data-i18n="{key}"></h3>
      <p class="style-d" data-i18n="{key}d"></p>
    </div>
''')
    w('''  </div>

  <p class="ps-sub-title" style="margin-top:34px" data-i18n="why.eyebrow"></p>
  <h3 class="sec-title" style="text-align:center;font-size:clamp(1.15rem,3vw,1.7rem);margin-bottom:10px" data-i18n="why.title"></h3>
  <p class="sec-sub" style="text-align:center;max-width:640px;margin:0 auto clamp(24px,4vw,36px)" data-i18n="why.sub"></p>
  <div class="why-grid">
''')
    for n in range(1, 7):
        w(f'''    <div class="why-card card reveal" data-d="{min(n-1,4)}">
      <span class="why-num" aria-hidden="true">{n:02d}</span>
      <h4 class="why-nm" data-i18n="why.w{n}"></h4>
      <p class="why-d" data-i18n="why.w{n}d"></p>
    </div>
''')
    w('''  </div>

  <div class="fit-band reveal">
    <p class="fit-title" data-i18n="why.fit"></p>
    <ul class="fit-list">
''')
    for n in range(1, 7):
        w(f'      <li data-i18n="why.fit{n}"></li>\n')
    w('''    </ul>
  </div>

  <div class="ps-value reveal">
    <p data-i18n="ps.value"></p>
    <a class="btn btn-primary" href="#contact" onclick="trackContact('Strengths-CTA')">
      <i class="fa-solid fa-paper-plane" aria-hidden="true"></i><span data-i18n="ps.cta"></span></a>
  </div>
</section>

''')

    # ── Experience / Education / Certifications ─────────────────────────────
    w('''<!-- ═══ BACKGROUND ═══ -->
<section class="section" id="background">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="exp.eyebrow"></span>
    <h2 class="sec-title" data-i18n="exp.title"></h2>
    <p class="sec-sub" data-i18n="exp.sub"></p>
  </div>
  <div class="bg-grid">
    <div class="bg-block card reveal">
      <p class="bg-h" data-i18n="exp.workTitle"></p>
''')
    # only job 1 has a documented date range; rendering an empty <p> for the
    # others would leave a stray gap and an unused translation key
    JOBS_WITH_PERIOD = set(range(1, 7))   # every role now has dates
    for n in range(1, 7):
        period = ('        <p class="job-period" data-i18n="exp.j%d.period"></p>\n' % n
                  if n in JOBS_WITH_PERIOD else '')
        w(f'''      <div class="job">
        <h3 class="job-role" data-i18n="exp.j{n}.role"></h3>
        <p class="job-org" data-i18n="exp.j{n}.org"></p>
{period}        <p class="job-desc" data-i18n="exp.j{n}.desc"></p>
      </div>
''')
    w('''    </div>

    <div>
      <div class="bg-block card reveal" data-d="1">
        <p class="bg-h" data-i18n="exp.eduTitle"></p>
        <div class="edu-card2">
          <p class="edu-deg" data-i18n="exp.edu.degree"></p>
          <p class="edu-school" data-i18n="exp.edu.school"></p>
          <p class="edu-where" data-i18n="exp.edu.where"></p>
          <p class="edu-detail" data-i18n="exp.edu.detail"></p>
        </div>
      </div>

      <div class="bg-block card reveal" data-d="2" style="margin-top:16px">
        <p class="bg-h" data-i18n="exp.certTitle"></p>
        <ul class="cert-list">
          <li data-i18n="exp.c1"></li>
          <li data-i18n="exp.c2"></li>
          <li data-i18n="exp.c3"></li>
        </ul>
      </div>

      <div class="avail-card reveal" data-d="3">
        <p class="bg-h" data-i18n="avail.status"></p>
        <p data-i18n="avail.note"></p>
      </div>
    </div>
  </div>
</section>

<!-- ═══ IMPACT ═══ -->
<section class="section" id="impact">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="impact.eyebrow"></span>
    <h2 class="sec-title" data-i18n="impact.title"></h2>
  </div>
  <div class="impact-grid">
''')
    for i, (val, sfx, color, label, note) in enumerate(STATS):
        w(f'''    <div class="stat reveal" data-d="{min(i,4)}">
      <span class="stat-num" style="color:{color}" data-count="{val}" data-suffix="{sfx}">0</span>
      <span class="stat-label" data-i18n="{label}"></span>
      <span class="stat-note" data-i18n="{note}"></span>
    </div>
''')
    w('''    <div class="stat reveal" data-d="4">
      <span class="stat-num" style="color:var(--cyan);font-size:clamp(.8rem,1.9vw,1rem);line-height:1.5" data-i18n="impact.domains"></span>
      <span class="stat-note" data-i18n="impact.domains.note"></span>
    </div>
  </div>
  <p class="impact-caveat reveal" data-i18n="impact.sub"></p>
</section>

''')

    # ── Commercial / team delivery (sits before the engineering projects so a
    #    recruiter sees paid, team-led work first) ─────────────────────────────
    w('''<!-- ═══ DELIVERY ═══ -->
<section class="section" id="delivery">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="deliv.eyebrow"></span>
    <h2 class="sec-title" data-i18n="deliv.title"></h2>
    <p class="sec-sub" data-i18n="deliv.sub"></p>
  </div>
  <div class="deliv-grid">

    <article class="deliv card reveal">
      <p class="deliv-kicker" data-i18n="d1.kicker"></p>
      <h3 class="deliv-title" data-i18n="d1.title"></h3>
      <p class="deliv-desc" data-i18n="d1.desc"></p>
      <div class="deliv-metrics">
        <div class="deliv-m"><b>10</b><span data-i18n="d1.m1"></span></div>
        <div class="deliv-m"><b>13,000 USD</b><span data-i18n="d1.m2"></span></div>
        <div class="deliv-m"><b data-i18n="d1.m3v"></b><span data-i18n="d1.m3"></span></div>
      </div>
      <div class="deliv-foot">
        <span class="deliv-note"><i class="fa-solid fa-lock" aria-hidden="true"></i><span data-i18n="deliv.noRepo"></span></span>
      </div>
    </article>

    <article class="deliv card reveal" data-d="1">
      <p class="deliv-kicker" data-i18n="d2.kicker"></p>
      <h3 class="deliv-title" data-i18n="d2.title"></h3>
      <p class="deliv-desc" data-i18n="d2.desc"></p>
      <div class="deliv-metrics">
        <div class="deliv-m"><b>8</b><span data-i18n="d2.m1"></span></div>
        <div class="deliv-m"><b>10,000 USD</b><span data-i18n="d2.m2"></span></div>
        <div class="deliv-m"><b data-i18n="d2.m3v"></b><span data-i18n="d2.m3"></span></div>
      </div>
      <div class="deliv-foot">
        <span class="deliv-note"><i class="fa-solid fa-lock" aria-hidden="true"></i><span data-i18n="deliv.noRepo"></span></span>
      </div>
    </article>

    <article class="deliv card reveal" data-d="2">
      <p class="deliv-kicker" data-i18n="d3.kicker"></p>
      <h3 class="deliv-title" data-i18n="d3.title"></h3>
      <p class="deliv-desc" data-i18n="d3.desc"></p>
      <div class="tags"><span class="tag">HTML5</span><span class="tag">CSS3</span><span class="tag">JavaScript</span><span class="tag">Backend</span><span class="tag">Git</span></div>
      <div class="deliv-foot">
        <span class="deliv-note"><i class="fa-solid fa-lock" aria-hidden="true"></i><span data-i18n="deliv.noRepo"></span></span>
      </div>
    </article>

    <article class="deliv card reveal" data-d="3">
      <p class="deliv-kicker" data-i18n="d4.kicker"></p>
      <h3 class="deliv-title" data-i18n="d4.title"></h3>
      <p class="deliv-desc" data-i18n="d4.desc"></p>
      <div class="tags"><span class="tag">HTML5</span><span class="tag">CSS3</span><span class="tag">JavaScript</span><span class="tag">UX/UI</span><span class="tag">Firebase Hosting</span></div>
      <div class="deliv-foot">
        <a class="btn btn-ghost btn-sm" href="https://auragift.web.app" target="_blank" rel="noopener" onclick="trackContact(\'AuraGift-Delivery\')"><i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i><span data-i18n="d4.live"></span></a>
      </div>
    </article>

  </div>
</section>

<!-- ═══ PROJECTS ═══ -->
<section class="section" id="projects">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="projects.eyebrow"></span>
    <h2 class="sec-title" data-i18n="projects.title"></h2>
    <p class="sec-sub" data-i18n="projects.sub"></p>
  </div>
  <div class="proj-list">
''')
    for pid, accent, icon, repo, image, is_svg, metrics, disc, tags in PROJECTS:
        w(f'    <article class="proj card reveal">\n      <div class="proj-media">\n')
        if image:
            w('        ' + img(image, f"{pid}.alt", is_svg) + '\n')
        else:
            w(f'''        <div class="abstract" aria-hidden="true"><div class="abstract-grid"></div><i class="fa-solid {icon}"></i></div>\n''')
        w('      </div>\n      <div class="proj-body">\n')
        w(f'        <p class="proj-kicker" style="color:{accent}" data-i18n="{pid}.kicker"></p>\n')
        w(f'        <h3 class="proj-title" data-i18n="{pid}.title"></h3>\n')
        w(f'        <p class="proj-impact" data-i18n="{pid}.impact"></p>\n')
        if metrics:
            w('        <div class="proj-metrics">\n')
            for v, k in metrics:
                w(f'          <div class="metric"><b style="color:{accent}">{v}</b><span data-i18n="{k}"></span></div>\n')
            w('        </div>\n')
        w('        <div class="tags">' + ''.join(f'<span class="tag">{x}</span>' for x in tags) + '</div>\n')
        w(f'''        <div class="proj-actions">
          <button class="btn btn-ghost btn-sm" type="button" data-modal="{pid}" onclick="trackProject('{pid}')"><i class="fa-solid fa-maximize" aria-hidden="true"></i><span data-i18n="projects.explore"></span></button>
          <a class="btn btn-ghost btn-sm" href="{repo}" target="_blank" rel="noopener"><i class="fa-brands fa-github" aria-hidden="true"></i><span data-i18n="projects.github"></span></a>
        </div>
''')
        if disc:
            w(f'        <p class="disclaimer"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i><span data-i18n="{disc}"></span></p>\n')
        w('      </div>\n    </article>\n')

    w('''  </div>
</section>

<!-- ═══ CAPABILITIES ═══ -->
<section class="section" id="capabilities">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="cap.eyebrow"></span>
    <h2 class="sec-title" data-i18n="cap.title"></h2>
    <p class="sec-sub" data-i18n="cap.sub"></p>
  </div>
  <div class="cap-grid">
''')
    for i, (key, icon, color, items) in enumerate(CAPS):
        w(f'''    <div class="cap card reveal" data-d="{min(i,4)}">
      <div class="cap-icon" style="background:color-mix(in srgb,{color} 12%,transparent);color:{color}"><i class="fa-solid {icon}" aria-hidden="true"></i></div>
      <h3 class="cap-name" data-i18n="{key}"></h3>
      <div class="cap-tags">{''.join(f'<span class="tag">{x}</span>' for x in items)}</div>
    </div>
''')

    w('''  </div>
</section>

<!-- ═══ PROCESS ═══ -->
<section class="section" id="process">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="process.eyebrow"></span>
    <h2 class="sec-title" data-i18n="process.title"></h2>
    <p class="sec-sub" data-i18n="process.sub"></p>
  </div>
  <div class="process">
    <div class="process-rail" aria-hidden="true"><div class="process-fill"></div></div>
''')
    for i in range(1, 9):
        w(f'''    <div class="step">
      <div class="step-dot" aria-hidden="true">{i:02d}</div>
      <h3 class="step-name" data-i18n="process.s{i}"></h3>
      <p class="step-desc" data-i18n="process.s{i}d"></p>
    </div>
''')

    w('''  </div>
</section>

<!-- ═══ PRINCIPLES ═══ -->
<section class="section" id="principles">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="prin.eyebrow"></span>
    <h2 class="sec-title" data-i18n="prin.title"></h2>
  </div>
  <div class="prin-grid">
''')
    for i in range(1, 8):
        w(f'''    <div class="prin card reveal" data-d="{min(i-1,4)}">
      <h3 class="prin-name" data-i18n="prin.p{i}"></h3>
      <p class="prin-desc" data-i18n="prin.p{i}d"></p>
    </div>
''')

    w('''  </div>
</section>

<!-- ═══ ADDITIONAL RANGE ═══ -->
<section class="section" id="range">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="range.eyebrow"></span>
    <h2 class="sec-title" data-i18n="range.title"></h2>
    <p class="sec-sub" data-i18n="range.sub"></p>
  </div>
  <div class="range-grid">
''')
    for i, (rid, image, icon, color, repo, live, tags) in enumerate(RANGE):
        w(f'    <article class="range-card card reveal" data-d="{min(i,4)}">\n      <div class="range-media">\n')
        if image:
            w('        ' + img(image, f"{rid}.alt") + '\n')
        else:
            w(f'        <div class="abstract" aria-hidden="true"><div class="abstract-grid"></div><i class="fa-solid {icon}" style="color:{color}"></i></div>\n')
        w(f'''      </div>
      <div class="range-body">
        <h3 class="range-name" data-i18n="{rid}.title"></h3>
        <p class="range-desc" data-i18n="{rid}.desc"></p>
        <div class="tags">{''.join(f'<span class="tag">{x}</span>' for x in tags)}</div>
        <div class="range-links">
          <a class="range-link" href="{repo}" target="_blank" rel="noopener"><i class="fa-brands fa-github" aria-hidden="true"></i><span data-i18n="range.repo"></span></a>
''')
        if live:
            w(f'          <a class="range-link" href="{live}" target="_blank" rel="noopener" onclick="trackContact(\'AuraGift\')"><i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i><span data-i18n="range.live"></span></a>\n')
        w('        </div>\n      </div>\n    </article>\n')

    w('''  </div>
</section>

<!-- ═══ GITHUB ═══ -->
<section class="section" id="github">
  <div class="sec-head reveal">
    <span class="eyebrow" data-i18n="gh.eyebrow"></span>
    <h2 class="sec-title" data-i18n="gh.title"></h2>
    <p class="sec-sub" data-i18n="gh.sub"></p>
  </div>
  <h3 class="eyebrow" style="text-align:center;margin-bottom:16px" data-i18n="gh.repos"></h3>
  <div class="gh-grid">
''')
    for name, url in REPOS:
        w(f'''    <a class="gh-repo reveal" href="{url}" target="_blank" rel="noopener">
      <i class="fa-solid fa-code-branch" aria-hidden="true"></i>
      <span class="gh-name">{name}</span>
      <i class="fa-solid fa-arrow-right gh-arrow" aria-hidden="true"></i>
    </a>
''')

    w('''  </div>
  <div style="text-align:center;margin-top:26px">
    <a class="btn btn-ghost reveal" href="https://github.com/Hany15" target="_blank" rel="noopener" onclick="trackContact('GitHub-Profile')">
      <i class="fa-brands fa-github" aria-hidden="true"></i><span data-i18n="gh.profile"></span></a>
  </div>
</section>

<!-- ═══ CONTACT ═══ -->
<section class="section" id="contact">
  <div class="contact-card reveal">
    <span class="eyebrow" data-i18n="contact.eyebrow"></span>
    <h2 class="contact-title" data-i18n="contact.title"></h2>
    <p class="contact-text" data-i18n="contact.text"></p>
    <div class="contact-btns">
      <a class="btn btn-primary" href="mailto:developeractionobject@gmail.com" onclick="trackContact('Email')"><i class="fa-solid fa-envelope" aria-hidden="true"></i><span data-i18n="contact.cta"></span></a>
      <a class="btn btn-ghost" href="tel:+79969382354"
         data-i18n-attr="aria-label:contact.aria.phone" onclick="trackContact('Phone')"><i class="fa-solid fa-phone" aria-hidden="true"></i><span data-i18n="contact.phone"></span></a>
      <a class="btn btn-ghost" href="https://t.me/Hany_230" target="_blank" rel="noopener me"
         data-i18n-attr="aria-label:contact.aria.telegram" onclick="trackContact('Telegram')"><i class="fa-brands fa-telegram" aria-hidden="true"></i><span data-i18n="contact.telegram"></span></a>
      <a class="btn btn-ghost" href="https://wa.me/79969382354" target="_blank" rel="noopener"
         data-i18n-attr="aria-label:contact.aria.whatsapp" onclick="trackContact('WhatsApp')"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i><span data-i18n="contact.whatsapp"></span></a>
      <a class="btn btn-secondary" href="https://www.linkedin.com/in/hany-reda-854667417" target="_blank" rel="noopener" onclick="trackContact('LinkedIn')"><i class="fa-brands fa-linkedin" aria-hidden="true"></i><span data-i18n="contact.linkedin"></span></a>
      <a class="btn btn-ghost" href="https://github.com/Hany15" target="_blank" rel="noopener" onclick="trackContact('GitHub')"><i class="fa-brands fa-github" aria-hidden="true"></i><span data-i18n="contact.github"></span></a>
      <a class="btn btn-ghost" href="https://hany15.github.io/Hany-Reda-Portfolio/" target="_blank" rel="noopener" onclick="trackContact('Portfolio')"><i class="fa-solid fa-globe" aria-hidden="true"></i><span data-i18n="contact.portfolio"></span></a>
    </div>
  <div class="cv-row">
    <span class="cv-label"><i class="fa-solid fa-file-arrow-down" aria-hidden="true"></i><span data-i18n="cv.label"></span></span>
    <a class="cv-btn" href="cv/cv_en.pdf" download="Mohamed-Hany-Reda-CV-EN.pdf"
       data-i18n-attr="aria-label:cv.aria.en" onclick="trackContact('CV-EN')">
      <span class="flag">EN</span><span data-i18n="cv.en"></span></a>
    <a class="cv-btn" href="cv/cv_ru.pdf" download="Mohamed-Hany-Reda-CV-RU.pdf"
       data-i18n-attr="aria-label:cv.aria.ru" onclick="trackContact('CV-RU')">
      <span class="flag">RU</span><span data-i18n="cv.ru"></span></a>
    <span class="cv-hint" data-i18n="cv.hint"></span>
    <span class="cv-onepage">
      <span data-i18n="cv.onepage"></span>
      <a href="cv/cv_en_1page.pdf" download="Mohamed-Hany-Reda-CV-EN-1page.pdf"
         data-i18n-attr="aria-label:cv.aria.en1" onclick="trackContact('CV-EN-1page')">EN</a>
      <span class="sep" aria-hidden="true">·</span>
      <a href="cv/cv_ru_1page.pdf" download="Mohamed-Hany-Reda-CV-RU-1page.pdf"
         data-i18n-attr="aria-label:cv.aria.ru1" onclick="trackContact('CV-RU-1page')">RU</a>
    </span>
    <span class="cv-onepage cv-targeted">
      <span data-i18n="cv.targeted"></span>
      <span class="cv-tset"><span class="cv-tlabel" data-i18n="cv.fs"></span>
        <a href="cv/cv_fullstack_en.pdf" download="Mohamed-Hany-Reda-CV-FullStack-EN.pdf" onclick="trackContact('CV-FS-EN')">EN</a>
        <span class="sep" aria-hidden="true">·</span>
        <a href="cv/cv_fullstack_ru.pdf" download="Mohamed-Hany-Reda-CV-FullStack-RU.pdf" onclick="trackContact('CV-FS-RU')">RU</a></span>
      <span class="cv-tset"><span class="cv-tlabel" data-i18n="cv.ai"></span>
        <a href="cv/cv_ai_en.pdf" download="Mohamed-Hany-Reda-CV-AI-EN.pdf" onclick="trackContact('CV-AI-EN')">EN</a>
        <span class="sep" aria-hidden="true">·</span>
        <a href="cv/cv_ai_ru.pdf" download="Mohamed-Hany-Reda-CV-AI-RU.pdf" onclick="trackContact('CV-AI-RU')">RU</a></span>
    </span>
  </div>
  </div>
</section>

</main>

<footer>
  <div class="foot-social">
    <a href="mailto:developeractionobject@gmail.com" data-i18n-attr="aria-label:contact.email" aria-label="Email" onclick="trackContact('Email-Footer')"><i class="fa-solid fa-envelope" aria-hidden="true"></i></a>
    <a href="tel:+79969382354" data-i18n-attr="aria-label:contact.aria.phone" onclick="trackContact('Phone-Footer')"><i class="fa-solid fa-phone" aria-hidden="true"></i></a>
    <a href="https://t.me/Hany_230" target="_blank" rel="noopener me" data-i18n-attr="aria-label:contact.aria.telegram" onclick="trackContact('Telegram-Footer')"><i class="fa-brands fa-telegram" aria-hidden="true"></i></a>
    <a href="https://wa.me/79969382354" target="_blank" rel="noopener" data-i18n-attr="aria-label:contact.aria.whatsapp" onclick="trackContact('WhatsApp-Footer')"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i></a>
    <a href="https://github.com/Hany15" target="_blank" rel="noopener" data-i18n-attr="aria-label:contact.github" aria-label="GitHub" onclick="trackContact('GitHub-Footer')"><i class="fa-brands fa-github" aria-hidden="true"></i></a>
    <a href="https://www.linkedin.com/in/hany-reda-854667417" target="_blank" rel="noopener" data-i18n-attr="aria-label:contact.linkedin" aria-label="LinkedIn" onclick="trackContact('LinkedIn-Footer')"><i class="fa-brands fa-linkedin" aria-hidden="true"></i></a>
    <a href="https://hany15.github.io/Hany-Reda-Portfolio/" target="_blank" rel="noopener" data-i18n-attr="aria-label:contact.portfolio" aria-label="Portfolio"><i class="fa-solid fa-globe" aria-hidden="true"></i></a>
  </div>
  <p class="foot-copy">&copy; 2026 Mohamed Hany Reda. <span data-i18n="footer.rights"></span><br><span data-i18n="footer.built"></span></p>
  <p class="foot-updated"><span data-i18n="footer.updated"></span>: <time datetime="__ISO__">__ISO__</time></p>
</footer>

<!-- ═══ PROJECT MODAL ═══ -->
<div class="modal-backdrop" id="modal-backdrop" aria-hidden="true">
  <div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"></div>
</div>

<script src="assets/js/i18n.js?v=676f64e9"></script>
<script src="assets/js/main.js?v=619307e3"></script>
</body>
</html>
''')
    return o.getvalue()

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html = build()
    with open(os.path.join(here, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"index.html written ({len(html):,} bytes, {html.count(chr(10)):,} lines)")
