#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates cv/cv_en.pdf and cv/cv_ru.pdf from a single content model.

Design goals:
  * text-selectable and ATS-parseable (no images, no text-as-graphics)
  * one shared layout engine, two content dictionaries -> the two PDFs can
    never drift structurally out of sync
  * every figure traceable to the portfolio / project repositories
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, HRFlowable)

# ── fonts: Arial carries full Cyrillic coverage on Windows ─────────────────
FONT_DIR = r"C:\Windows\Fonts"
for name, fn in (("CV", "arial.ttf"), ("CV-B", "arialbd.ttf"), ("CV-I", "ariali.ttf")):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
pdfmetrics.registerFontFamily("CV", normal="CV", bold="CV-B", italic="CV-I")

INK      = colors.HexColor("#12181F")
MUTED    = colors.HexColor("#4A5568")
ACCENT   = colors.HexColor("#0E6E8C")
RULE     = colors.HexColor("#C9D4DC")

S = {
 "name":    ParagraphStyle("name", fontName="CV-B", fontSize=21, leading=24,
                           textColor=INK, spaceAfter=2),
 "title":   ParagraphStyle("title", fontName="CV-B", fontSize=9.6, leading=13,
                           textColor=ACCENT, spaceAfter=3),
 "tag":     ParagraphStyle("tag", fontName="CV", fontSize=8.6, leading=12,
                           textColor=MUTED, spaceAfter=5),
 "contact": ParagraphStyle("contact", fontName="CV", fontSize=8.3, leading=12.5,
                           textColor=INK),
 "h2":      ParagraphStyle("h2", fontName="CV-B", fontSize=9.4, leading=11,
                           textColor=ACCENT, spaceBefore=9, spaceAfter=3),
 "body":    ParagraphStyle("body", fontName="CV", fontSize=8.7, leading=12.3,
                           textColor=INK, spaceAfter=3),
 "small":   ParagraphStyle("small", fontName="CV", fontSize=8.2, leading=11.6,
                           textColor=MUTED, spaceAfter=2),
 "role":    ParagraphStyle("role", fontName="CV-B", fontSize=9, leading=12,
                           textColor=INK, spaceBefore=4, spaceAfter=0),
 "meta":    ParagraphStyle("meta", fontName="CV-I", fontSize=8.1, leading=11,
                           textColor=MUTED, spaceAfter=2),
 "bullet":  ParagraphStyle("bullet", fontName="CV", fontSize=8.55, leading=12,
                           textColor=INK, leftIndent=9, bulletIndent=1,
                           spaceAfter=1.5),
 "note":    ParagraphStyle("note", fontName="CV-I", fontSize=7.7, leading=10.5,
                           textColor=MUTED, leftIndent=9, spaceAfter=2),
}


def rule():
    return HRFlowable(width="100%", thickness=0.7, color=RULE,
                      spaceBefore=1, spaceAfter=4)


def section(label):
    return [Paragraph(label.upper(), S["h2"]), rule()]


def bullets(items, style="bullet"):
    # reportlab takes the list marker from a <bullet> tag inside the markup
    return [Paragraph("<bullet>&#8226;</bullet>" + x, S[style]) for x in items]


def skills_table(rows):
    data = [[Paragraph(f"<b>{k}</b>", S["small"]), Paragraph(v, S["body"])] for k, v in rows]
    t = Table(data, colWidths=[33 * mm, 139 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return t


def job(role_line, meta_line, points, note=None):
    """Keeps a role header with its first bullets so it never orphans."""
    flow = [Paragraph(role_line, S["role"])]
    if meta_line:
        flow.append(Paragraph(meta_line, S["meta"]))
    flow += bullets(points)
    if note:
        flow.append(Paragraph(note, S["note"]))
    return KeepTogether(flow)


def build(content, path):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=19 * mm, rightMargin=19 * mm,
                          topMargin=14 * mm, bottomMargin=13 * mm,
                          title=content["pdf_title"], author="Mohamed Hany Reda",
                          subject=content["pdf_subject"])
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")

    def decorate(canvas, d):
        canvas.saveState()
        canvas.setFillColor(ACCENT)
        canvas.rect(0, A4[1] - 5 * mm, A4[0], 5 * mm, stroke=0, fill=1)
        canvas.setFont("CV", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 8 * mm, content["footer"])
        canvas.drawRightString(A4[0] - doc.rightMargin, 8 * mm,
                               "%s %d" % (content["page_word"], d.page))
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=decorate)])

    f = []
    # ── header ───────────────────────────────────────────────────────────
    f.append(Paragraph(content["name"], S["name"]))
    f.append(Paragraph(content["title"], S["title"]))
    f.append(Paragraph(content["tagline"], S["tag"]))
    f.append(Paragraph(content["contact"], S["contact"]))
    f.append(Spacer(1, 3))
    f.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                        spaceBefore=3, spaceAfter=1))

    f += section(content["l_summary"])
    f.append(Paragraph(content["summary"], S["body"]))

    f += section(content["l_avail"])
    f.append(Paragraph(content["avail"], S["body"]))

    f += section(content["l_competencies"])
    f.append(Paragraph("  •  ".join(content["competencies"]), S["body"]))

    f += section(content["l_skills"])
    f.append(skills_table(content["skills"]))

    f += section(content["l_projects"])
    for p in content["projects"]:
        f.append(job(p["name"], p["meta"], p["points"], p.get("note")))

    f += section(content["l_experience"])
    for e in content["experience"]:
        f.append(job(e["role"], e["meta"], e["points"]))

    f += section(content["l_education"])
    f.append(Paragraph(content["education"]["degree"], S["role"]))
    f.append(Paragraph(content["education"]["meta"], S["meta"]))
    f.append(Paragraph(content["education"]["courses"], S["small"]))

    f += section(content["l_certs"])
    f += bullets(content["certs"])

    f += section(content["l_languages"])
    f.append(Paragraph(content["languages"], S["body"]))

    doc.build(f)
    return path


# ══════════════════════════════════════════════════════════════════════════
LINK = ('<a href="{u}" color="#0E6E8C">{t}</a>')
CONTACT_EN = (
    "developeractionobject@gmail.com &nbsp;|&nbsp; Tomsk, Russia<br/>"
    + LINK.format(u="https://wa.me/79969382354", t="WhatsApp +7 996 938 2354") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://t.me/Hany_230", t="Telegram @Hany_230") + "<br/>"
    + LINK.format(u="https://github.com/Hany15", t="github.com/Hany15") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://www.linkedin.com/in/hany-reda-854667417", t="linkedin.com/in/hany-reda-854667417")
    + " &nbsp;|&nbsp; " + LINK.format(u="https://hany15.github.io/Hany-Reda-Portfolio/", t="hany15.github.io/Hany-Reda-Portfolio")
)
CONTACT_RU = (
    "developeractionobject@gmail.com &nbsp;|&nbsp; Томск, Россия<br/>"
    + LINK.format(u="https://wa.me/79969382354", t="WhatsApp +7 996 938 2354") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://t.me/Hany_230", t="Telegram @Hany_230") + "<br/>"
    + LINK.format(u="https://github.com/Hany15", t="github.com/Hany15") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://www.linkedin.com/in/hany-reda-854667417", t="linkedin.com/in/hany-reda-854667417")
    + " &nbsp;|&nbsp; " + LINK.format(u="https://hany15.github.io/Hany-Reda-Portfolio/", t="hany15.github.io/Hany-Reda-Portfolio")
)

EN = {
 "pdf_title": "Mohamed Hany Reda - CV",
 "pdf_subject": "Technical IT Project Manager | Software Engineer | AI & Digital Products",
 "footer": "Mohamed Hany Reda  —  Curriculum Vitae",
 "page_word": "Page",
 "name": "MOHAMED HANY REDA",
 "title": "Technical IT Project Manager &nbsp;|&nbsp; Software Engineer &nbsp;|&nbsp; AI &amp; Digital Products",
 "tagline": "Reinforcement Learning · Simulation &amp; Digital Twins · Autonomous Systems · Explainable AI · Production Software Architecture",
 "contact": CONTACT_EN,

 "l_avail": "Availability",
 "avail": "Based in Tomsk, Russia, with a Russian work permit. Available on-site, remotely or hybrid, and open to business trips. Not relocating. Full-time employment.",
 "l_summary": "Professional Summary",
 "summary":
   "Software engineer and technical project lead who builds complete intelligent systems rather than isolated models. "
   "My work spans deterministic simulation and digital twins, reinforcement-learning decision systems, explainable computer "
   "vision, and multi-tenant enterprise architecture — each delivered as a working product with a data layer, an interface, "
   "and automated tests. I connect business goals, product requirements and engineering execution, and my engineering "
   "background lets me understand technical dependencies, identify delivery risks early, and make project decisions with "
   "real technical context. Working proficiency in English and Russian alongside native Arabic supports collaboration "
   "across international teams.",

 "l_competencies": "Core Competencies",
 "competencies": [
   "Technical Project Planning &amp; Roadmapping", "Requirements Analysis", "Scope &amp; Change Management",
   "Risk Identification &amp; Mitigation", "Stakeholder Communication", "Cross-Functional Coordination",
   "Technical Decision Support", "Product &amp; Business Alignment", "System Architecture",
   "Reproducible Engineering", "Explainability &amp; Safety by Design", "Multilingual Collaboration",
 ],

 "l_skills": "Technical Skills",
 "skills": [
   ("Languages", "Python, Dart, C++, C#, SQL, JavaScript"),
   ("AI / ML", "PyTorch, EfficientNet, Computer Vision, Grad-CAM, OpenCV, Scikit-learn, Albumentations, Explainable AI"),
   ("Reinforcement Learning", "PPO, SAC, A2C, Multi-Agent RL, CTDE, Safe-RL, LSTM policies, Self-Play, Domain Randomization"),
   ("Simulation", "Discrete-Event Simulation, Entity-Component-System, Deterministic Replay, Procedural Generation, "
                  "Sensor Simulation, Operations Research (Erlang C, M/M/c, Little's Law)"),
   ("Backend", "FastAPI, PostgreSQL, SQLAlchemy, Redis, SQLite, REST APIs, Clean Architecture, Multi-Tenant Systems, RBAC"),
   ("Visualization", "Three.js, Pygame, PySide6, Streamlit, Flutter, Unreal Engine 5, Firebase"),
   ("Engineering", "Docker, Git, Pytest, CI, Ruff, MyPy, ONNX"),
 ],

 "l_projects": "Key Projects",
 "projects": [
  {"name": 'High-Throughput Sorting-Center Digital Twin',
   "meta": 'Python · PyTorch · PPO · Multi-Agent RL · LSTM · Discrete-Event Simulation · Three.js — '
           '<a href="https://github.com/Hany15/Amazon-sorting-center-digital-twin" color="#0E6E8C">repository</a>',
   "points": [
     "Built a logistics digital twin of a 400-lane sorting centre on a custom deterministic discrete-event engine with an "
     "Entity-Component-System architecture, making every run reproducible from a single seed.",
     "Modelled ~96,400 items/hour against a 100,000 items/hour design target, validated against classical queueing-theory baselines.",
     "Implemented PPO-based parcel routing, multi-agent coordination using centralised training with decentralised execution (CTDE), "
     "and an LSTM predictive-maintenance model.",
     "Added a fault-injection Chaos Agent, time-machine replay with scenario branching, a 2D operations centre and a browser-based 3D twin.",
     "530+ automated tests documented in the repository, with Ruff and MyPy in the toolchain.",
   ]},
  {"name": "Strict Drone Safe-RL — Autonomous Control Research Platform",
   "meta": 'Python · PyTorch · PPO · LSTM · Gymnasium · ONNX · Docker — '
           '<a href="https://github.com/Hany15/drone-rl-flight-control" color="#0E6E8C">repository</a>',
   "points": [
     "Trained drone-control policies under wind, sensor drift, control latency, motor degradation and GPS-denied navigation.",
     "PPO with an LSTM actor-critic under Automatic Domain Randomization, plus a Rapid Motor Adaptation-inspired module for online "
     "adaptation to changing dynamics.",
     "Simulated IMU, VIO and LiDAR sensing; five-stage fault-injection curriculum; TrainingGuardian stability monitoring.",
     "Hard safety limits and emergency fail-safe design, with an ONNX export path for edge deployment.",
   ],
   "note": "Simulation and research platform. No real-world autonomous flight validation is claimed."},
  {"name": "Fracture Detection AI — Explainable Medical Imaging Product",
   "meta": 'Python · PyTorch · EfficientNet-B0 · Grad-CAM · Streamlit · SQLite · ReportLab — '
           '<a href="https://github.com/Hany15/AI-Medical-Assistant-" color="#0E6E8C">repository</a>',
   "points": [
     "End-to-end computer-vision product for bone-fracture detection on the 4,083-image FracAtlas X-ray dataset.",
     "Measured results: 90.21% accuracy, 89.31% ROC AUC, 76.67% precision, 63.89% recall, 69.70% F1.",
     "Grad-CAM overlays make every prediction inspectable; shipped as a Streamlit application and Telegram bot with automated "
     "PDF reporting and local SQLite prediction history.",
     "Trilingual interface (English, Arabic, Russian); 21/21 documented tests passing.",
   ],
   "note": "Research and portfolio software. Not a certified medical device."},
  {"name": "HMS — Multi-Tenant Enterprise ERP &amp; AI Platform",
   "meta": 'Python · FastAPI · PostgreSQL · SQLAlchemy · Redis · React · Docker — '
           '<a href="https://github.com/Hany15/hms-ai-erp-platform" color="#0E6E8C">repository</a>',
   "points": [
     "Multi-tenant ERP covering inventory, warehousing, procurement, sales/CRM, finance, maintenance and HR in one Clean Architecture codebase.",
     "Enforced tenant isolation with PostgreSQL Row-Level Security at the database layer rather than trusting application code.",
     "Saudi ZATCA Phase 1 e-invoicing compliance, RBAC and audit logging, full Arabic/English RTL support.",
     "Offline rule-based advisor that runs without any external LLM, with provider-agnostic LLM agents as an optional layer.",
   ]},
  {"name": "AI Evolution Racing Lab — Explainable RL Research",
   "meta": 'Python · PyTorch · Stable-Baselines3 · PPO/SAC/A2C · Gymnasium — '
           '<a href="https://github.com/Hany15/ai-evolution-racing-lab" color="#0E6E8C">repository</a>',
   "points": [
     "Self-evolving simulation where procedurally generated worlds and adaptive difficulty memory drive RL driver training across generations.",
     "Explainability layer combining policy-entropy confidence, input-gradient saliency and neural activation visualisation.",
     "AI tournaments, evolution timeline and automated research reports.",
   ]},
  {"name": "Multi-Agent Autonomous Simulation Platform",
   "meta": 'Python · PyTorch · Multi-Agent RL · PySide6 · SQLite — '
           '<a href="https://github.com/Hany15/-AI-Powered-Air-Defense-Simulation-Platform-" color="#0E6E8C">repository</a>',
   "points": [
     "Multi-agent self-play across navigator, observer and interceptor roles in procedurally generated environments with dynamic "
     "weather and day/night cycles.",
     "Decision-probability and value-estimate logging with SQLite episodic memory, surfaced through a real-time PySide6 monitoring dashboard.",
   ]},
 ],

 "l_experience": "Professional Experience",
 "experience": [
  {"role": "Full-Stack Developer / Technical Owner  |  HMS &mdash; medical equipment manufacturer",
   "meta": "January 2024 &mdash; Present",
   "points": [
     "Own the corporate web product end to end: gather requirements from internal stakeholders and translate them into scoped, estimated work with realistic deadlines.",
     "Make the technical and architectural calls; build front end and back end, responsive layout, and integration with internal company systems.",
     "Carry every feature through development, testing, release and support, surfacing technical risk before it reaches a release.",
     "Agree priorities with stakeholders and explain technical constraints in business language.",
   ]},
  {"role": "Full-Stack Developer / Product Delivery Owner  |  AuraGift &mdash; digital gifting e-commerce",
   "meta": "January 2024 &mdash; Present",
   "points": [
     "Own the client side and UX of a premium digital-gifting platform, running features from requirement through QA to production deploy.",
     "Built the interface and UX layer &mdash; responsive layout, animation, cross-browser behaviour and performance tuning.",
     "Set up and maintain hosting and deployment on Firebase Hosting, giving a predictable, repeatable release process with no downtime.",
   ]},
  {"role": "Technical Project Lead / Full-Stack Developer  |  HMS",
   "meta": "January 2023 &mdash; June 2023",
   "points": [
     "Led a team of 8 on a corporate web product while contributing to the build as a full-stack developer.",
     "Planned phases, decomposed and assigned work, and tracked schedule, quality and milestone delivery.",
     "Independently managed a project budget of roughly $10,000 &mdash; planning spend, allocating budget and paying contributors.",
     "Unblocked developers on hard problems and took on critical modules where extra support was needed.",
   ]},
  {"role": "Technical Project Manager / Product Engineer  |  Freelance &middot; Self-employed",
   "meta": "June 2022 &mdash; Present",
   "points": [
     "Single point of accountability between client and delivery: discovery interviews, requirements formalised into SRS, user stories and acceptance criteria, phase planning and risk management.",
     "Led a team of 10 on an AI logistics system with a budget of roughly $13,000 over 11 months (January&ndash;November 2024).",
     "Design solution architecture and make the stack and integration decisions; build AI features &mdash; ML models in product services, LLM tooling, computer vision and explainable AI.",
     "Build cross-platform Flutter applications for mobile, web and desktop, plus backend services, relational databases and REST integrations.",
   ]},
  {"role": "Unreal Engine Developer / Independent Product Owner  |  Independent (indie)",
   "meta": "January 2020 &mdash; Present",
   "points": [
     "Ship own games and desktop products from concept to store listing, promotion and updates.",
     "Built networked multiplayer with server authority (Advanced Sessions) and cloud player data (Microsoft PlayFab) &mdash; a distributed client-server system assembled solo.",
     "Published 3 Android titles on Google Play with 5,000+ combined downloads, handling store requirements and release management end to end.",
     "Authored and published an Unreal Engine (Blueprints) course on Udemy; ran Google Ads acquisition campaigns.",
     "Key project &mdash; PROJECT NOVA: multiplayer sci-fi shooter on Unreal Engine 5 (C++ and Blueprints) with character replication, matchmaking, Nanite/Lumen and Niagara effects.",
   ]},
  {"role": "Media Team Lead  |  Resala Charity Organization, Egypt",
   "meta": "January 2020 &mdash; December 2020",
   "points": [
     "Led the media function at one of the largest charities in Egypt and the Middle East: organised team workflow, assigned ownership and tracked delivery.",
     "Coordinated people and activities across campaigns and events, managing deadlines under limited resources.",
     "Communicated with organisational stakeholders and resolved conflicts within the team.",
     "Completed a six-month leadership and management development programme.",
   ]},
 ],

 "l_education": "Education",
 "education": {
   "degree": "Bachelor — Computer Science &amp; Engineering",
   "meta": "Tomsk State University of Control Systems and Radioelectronics (TUSUR) · Tomsk, Russia · 2026",
   "courses": "Relevant coursework: Algorithms, Data Structures, Operating Systems, Software Engineering, Artificial Intelligence, "
              "Computer Vision, Machine Learning, Networking, Databases.",
 },

 "l_certs": "Certifications &amp; Recognition",
 "certs": [
   "IBM Professional Course — Certificate of Appreciation",
   "Resala Charity Organization — Certificate of Appreciation, Media Development Manager",
   "Tomsk State University (TUSUR) — Recognition for contributing to an educational Virtual Reality (VR) system",
 ],

 "l_languages": "Languages",
 "languages": "<b>Arabic</b> — Native &nbsp;•&nbsp; <b>English</b> — C2, full professional &nbsp;•&nbsp; "
              "<b>Russian</b> — B2, upper-intermediate",
}

RU = {
 "pdf_title": "Мохамед Хани Реда - Резюме",
 "pdf_subject": "Технический менеджер IT-проектов | Инженер-программист | ИИ и цифровые продукты",
 "footer": "Мохамед Хани Реда  —  Резюме",
 "page_word": "Стр.",
 "name": "МОХАМЕД ХАНИ РЕДА",
 "title": "Технический менеджер IT-проектов &nbsp;|&nbsp; Инженер-программист &nbsp;|&nbsp; ИИ и цифровые продукты",
 "tagline": "Обучение с подкреплением · Моделирование и цифровые двойники · Автономные системы · Объяснимый ИИ · Архитектура промышленного ПО",
 "contact": CONTACT_RU,

 "l_avail": "Доступность",
 "avail": "Живу в Томске, есть разрешение на работу в России. Готов работать в офисе, удалённо или гибридно, готов к командировкам. К переезду не готов. Полная занятость.",
 "l_summary": "Профиль",
 "summary":
   "Инженер-программист и технический руководитель проектов, создающий целостные интеллектуальные системы, а не отдельные модели. "
   "Мои работы охватывают детерминированное моделирование и цифровые двойники, системы принятия решений на основе обучения с "
   "подкреплением, объяснимое компьютерное зрение и мультиарендную корпоративную архитектуру — каждая доведена до рабочего "
   "продукта со слоем данных, интерфейсом и автоматическими тестами. Связываю бизнес-цели, продуктовые требования и техническую "
   "реализацию; инженерный опыт позволяет понимать технические зависимости, заранее выявлять риски срыва сроков и принимать "
   "управленческие решения с учётом реального технического контекста. Профессиональное владение английским и русским наряду с "
   "родным арабским обеспечивает работу в международных командах.",

 "l_competencies": "Ключевые компетенции",
 "competencies": [
   "Планирование проектов и дорожные карты", "Анализ требований", "Управление объёмом и изменениями",
   "Выявление и снижение рисков", "Коммуникация с заинтересованными сторонами", "Кросс-функциональная координация",
   "Поддержка технических решений", "Согласование продукта и бизнеса", "Архитектура систем",
   "Воспроизводимая инженерия", "Объяснимость и безопасность по замыслу", "Многоязычное взаимодействие",
 ],

 "l_skills": "Технические навыки",
 "skills": [
   ("Языки", "Python, Dart, C++, C#, SQL, JavaScript"),
   ("ИИ / ML", "PyTorch, EfficientNet, компьютерное зрение, Grad-CAM, OpenCV, Scikit-learn, Albumentations, объяснимый ИИ"),
   ("Обучение с подкреплением", "PPO, SAC, A2C, многоагентное RL, CTDE, Safe-RL, политики на LSTM, самоигра, рандомизация предметной области"),
   ("Моделирование", "Дискретно-событийное моделирование, Entity-Component-System, детерминированное воспроизведение, "
                     "процедурная генерация, моделирование датчиков, исследование операций (Erlang C, M/M/c, закон Литтла)"),
   ("Бэкенд", "FastAPI, PostgreSQL, SQLAlchemy, Redis, SQLite, REST API, Clean Architecture, мультиарендные системы, RBAC"),
   ("Визуализация", "Three.js, Pygame, PySide6, Streamlit, Flutter, Unreal Engine 5, Firebase"),
   ("Инженерия", "Docker, Git, Pytest, CI, Ruff, MyPy, ONNX"),
 ],

 "l_projects": "Ключевые проекты",
 "projects": [
  {"name": "Цифровой двойник высокопроизводительного сортировочного центра",
   "meta": 'Python · PyTorch · PPO · многоагентное RL · LSTM · дискретно-событийное моделирование · Three.js — '
           '<a href="https://github.com/Hany15/Amazon-sorting-center-digital-twin" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Построил логистический цифровой двойник сортировочного центра на 400 линий на собственном детерминированном "
     "дискретно-событийном движке с архитектурой Entity-Component-System: любой прогон воспроизводится по одной начальной величине.",
     "Смоделирована производительность ~96 400 единиц в час при целевом показателе 100 000 единиц в час; результаты проверены "
     "относительно классических моделей теории массового обслуживания.",
     "Реализована маршрутизация посылок на основе PPO, координация агентов по схеме централизованного обучения с "
     "децентрализованным исполнением (CTDE) и прогнозное обслуживание на LSTM.",
     "Добавлены внедрение отказов (Chaos Agent), воспроизведение записей с ветвлением сценариев, операционный центр 2D и "
     "3D-двойник в браузере.",
     "В репозитории задокументировано более 530 автоматических тестов; в инструментарии Ruff и MyPy.",
   ]},
  {"name": "Strict Drone Safe-RL — исследовательская платформа автономного управления",
   "meta": 'Python · PyTorch · PPO · LSTM · Gymnasium · ONNX · Docker — '
           '<a href="https://github.com/Hany15/drone-rl-flight-control" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Обучение политик управления дроном в условиях ветра, дрейфа датчиков, задержек управления, деградации двигателей и "
     "навигации без GPS.",
     "PPO с актор-критиком на LSTM при автоматической рандомизации предметной области и модуль в духе Rapid Motor Adaptation "
     "для адаптации к изменяющейся динамике на лету.",
     "Моделирование датчиков IMU, VIO и LiDAR; пятиэтапная программа внедрения отказов; монитор устойчивости TrainingGuardian.",
     "Жёсткие ограничения безопасности и аварийная защита, экспорт в ONNX для периферийных устройств.",
   ],
   "note": "Платформа моделирования и исследований. Проверка реальных автономных полётов не заявляется."},
  {"name": "Fracture Detection AI — объяснимый продукт медицинской визуализации",
   "meta": 'Python · PyTorch · EfficientNet-B0 · Grad-CAM · Streamlit · SQLite · ReportLab — '
           '<a href="https://github.com/Hany15/AI-Medical-Assistant-" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Законченный продукт компьютерного зрения для выявления переломов на наборе рентгеновских снимков FracAtlas (4 083 изображения).",
     "Измеренные результаты: точность 90,21%, ROC AUC 89,31%, precision 76,67%, recall 63,89%, F1 69,70%.",
     "Наложения Grad-CAM делают каждый прогноз проверяемым; поставляется как приложение Streamlit и бот Telegram с "
     "автоматической генерацией PDF-отчётов и локальной историей прогнозов в SQLite.",
     "Трёхъязычный интерфейс (английский, арабский, русский); пройден 21 из 21 задокументированного теста.",
   ],
   "note": "Исследовательское и портфолио-приложение. Не является сертифицированным медицинским изделием."},
  {"name": "HMS — мультиарендная корпоративная ERP и ИИ-платформа",
   "meta": 'Python · FastAPI · PostgreSQL · SQLAlchemy · Redis · React · Docker — '
           '<a href="https://github.com/Hany15/hms-ai-erp-platform" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Мультиарендная ERP: склад, логистика, закупки, продажи и CRM, финансы, обслуживание и кадры в единой кодовой базе на Clean Architecture.",
     "Изоляция арендаторов обеспечена через Row-Level Security в PostgreSQL на уровне базы данных, а не доверием к коду приложения.",
     "Соответствие требованиям электронного выставления счетов ZATCA (Саудовская Аравия), RBAC и журнал аудита, полная "
     "поддержка арабского и английского с RTL.",
     "Офлайн-советник на правилах, работающий без внешних языковых моделей, с опциональными провайдер-независимыми LLM-агентами.",
   ]},
  {"name": "AI Evolution Racing Lab — исследование объяснимого RL",
   "meta": 'Python · PyTorch · Stable-Baselines3 · PPO/SAC/A2C · Gymnasium — '
           '<a href="https://github.com/Hany15/ai-evolution-racing-lab" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Саморазвивающаяся симуляция: процедурно создаваемые миры и память адаптивной сложности управляют обучением "
     "RL-гонщиков от поколения к поколению.",
     "Слой объяснимости: оценка уверенности через энтропию политики, карты значимости по градиентам входа и визуализация активаций.",
     "Турниры ИИ, хронология эволюции и автоматические исследовательские отчёты.",
   ]},
  {"name": "Платформа многоагентного автономного моделирования",
   "meta": 'Python · PyTorch · многоагентное RL · PySide6 · SQLite — '
           '<a href="https://github.com/Hany15/-AI-Powered-Air-Defense-Simulation-Platform-" color="#0E6E8C">репозиторий</a>',
   "points": [
     "Многоагентная самоигра с ролями навигатора, наблюдателя и перехватчика в процедурно создаваемых средах с динамической "
     "погодой и сменой дня и ночи.",
     "Журналирование вероятностей решений и оценок ценности с эпизодической памятью в SQLite, вывод в панель мониторинга "
     "PySide6 в реальном времени.",
   ]},
 ],

 "l_experience": "Опыт работы",
 "experience": [
  {"role": "Full-Stack Developer / Technical Owner  |  HMS &mdash; производитель медицинского оборудования",
   "meta": "Январь 2024 &mdash; настоящее время",
   "points": [
     "Отвечаю за корпоративный веб-продукт целиком: собираю требования от внутренних заказчиков и перевожу их в задачи, объём работ и реалистичные сроки.",
     "Принимаю технические и архитектурные решения; разрабатываю frontend и backend, адаптивную вёрстку и интеграцию с внутренними системами компании.",
     "Веду каждую фичу по циклу разработка &rarr; тестирование &rarr; релиз &rarr; поддержка, выявляя технические риски до релиза.",
     "Согласую приоритеты со стейкхолдерами и объясняю технические ограничения на понятном для бизнеса языке.",
   ]},
  {"role": "Full-Stack Developer / Product Delivery Owner  |  AuraGift &mdash; e-commerce цифровых подарков",
   "meta": "Январь 2024 &mdash; настоящее время",
   "points": [
     "Отвечаю за клиентскую часть и UX премиальной платформы цифровых подарков, веду фичи от требований через контроль качества до продакшна.",
     "Реализовал интерфейс и UX-слой &mdash; адаптивная вёрстка, анимации, кроссбраузерность и оптимизация производительности.",
     "Настроил и поддерживаю хостинг и деплой на Firebase Hosting: предсказуемый и повторяемый процесс выпуска без простоев.",
   ]},
  {"role": "Technical Project Lead / Full-Stack Developer  |  HMS",
   "meta": "Январь 2023 &mdash; июнь 2023",
   "points": [
     "Руководил командой из 8 специалистов при разработке корпоративного веб-продукта, совмещая руководство с разработкой.",
     "Планировал этапы, декомпозировал и распределял задачи, контролировал сроки, качество и ключевые этапы.",
     "Самостоятельно управлял бюджетом проекта около $10&nbsp;000: планировал расходы, распределял бюджет и организовывал выплаты участникам.",
     "Помогал разработчикам решать сложные задачи и подключался к критическим модулям.",
   ]},
  {"role": "Technical Project Manager / Product Engineer  |  Фриланс &middot; Самозанятость",
   "meta": "Июнь 2022 &mdash; настоящее время",
   "points": [
     "Единая точка ответственности между заказчиком и реализацией: интервью, формализация требований в ТЗ/SRS, user stories и критерии приёмки, планирование этапов и управление рисками.",
     "Руководил командой из 10 специалистов на логистической AI-системе с бюджетом около $13&nbsp;000 в течение 11 месяцев (январь&ndash;ноябрь 2024).",
     "Проектирую архитектуру решений и принимаю решения по стеку и интеграциям; внедряю AI &mdash; ML-модели в продуктовых сервисах, LLM-инструменты, computer vision и объяснимый AI.",
     "Создаю кроссплатформенные приложения на Flutter для mobile, web и desktop, backend-сервисы, реляционные БД и интеграции REST API.",
   ]},
  {"role": "Unreal Engine Developer / Independent Product Owner  |  Независимая разработка (indie)",
   "meta": "Январь 2020 &mdash; настоящее время",
   "points": [
     "Выпускаю собственные игры и десктоп-продукты от концепции до публикации, продвижения и обновлений.",
     "Спроектировал сетевой мультиплеер с серверной авторизацией (Advanced Sessions) и облачным хранением данных игроков (Microsoft PlayFab) &mdash; распределённая клиент-серверная система, собранная самостоятельно.",
     "Опубликовал 3 игры для Android в Google Play с 5&nbsp;000+ загрузок, полностью пройдя требования стора и релиз-менеджмент.",
     "Создал и опубликовал авторский курс по Unreal Engine (Blueprints) на Udemy; вёл рекламные кампании в Google Ads.",
     "Ключевой проект &mdash; PROJECT NOVA: многопользовательский sci-fi шутер на Unreal Engine 5 (C++ и Blueprints): репликация персонажей, матчмейкинг, Nanite/Lumen и эффекты Niagara.",
   ]},
  {"role": "Руководитель медианаправления  |  Resala Charity Organization, Египет",
   "meta": "Январь 2020 &mdash; декабрь 2020",
   "points": [
     "Руководил медианаправлением в одной из крупнейших благотворительных организаций Египта и Ближнего Востока: организовывал рабочие процессы, распределял ответственность и контролировал выполнение.",
     "Координировал людей и активности при подготовке кампаний и мероприятий, управляя дедлайнами при ограниченных ресурсах.",
     "Вёл коммуникацию со стейкхолдерами организации и разрешал конфликтные ситуации внутри команды.",
     "Прошёл шестимесячную программу развития лидерства и управления.",
   ]},
 ],

 "l_education": "Образование",
 "education": {
   "degree": "Бакалавр — информатика и вычислительная техника",
   "meta": "Томский государственный университет систем управления и радиоэлектроники (ТУСУР) · Томск, Россия · 2026",
   "courses": "Профильные дисциплины: алгоритмы, структуры данных, операционные системы, программная инженерия, "
              "искусственный интеллект, компьютерное зрение, машинное обучение, сети, базы данных.",
 },

 "l_certs": "Сертификаты и признание",
 "certs": [
   "IBM Professional Course — сертификат за достижения",
   "Благотворительная организация «Resala» — сертификат, менеджер по развитию медиа",
   "ТУСУР — признание за вклад в разработку образовательной системы виртуальной реальности (VR)",
 ],

 "l_languages": "Языки",
 "languages": "<b>Арабский</b> — родной &nbsp;•&nbsp; <b>Английский</b> — C2, в совершенстве &nbsp;•&nbsp; "
              "<b>Русский</b> — B2, средне-продвинутый",
}


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "cv")
    os.makedirs(out, exist_ok=True)
    for content, fn in ((EN, "cv_en.pdf"), (RU, "cv_ru.pdf")):
        p = build(content, os.path.join(out, fn))
        print("%-12s %6.1f KB" % (fn, os.path.getsize(p) / 1024))
