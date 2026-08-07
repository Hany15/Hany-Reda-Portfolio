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
  {"role": "Freelance Software &amp; AI Engineer  |  Self-Employed",
   "meta": "2022 — Present",
   "points": [
     "Design and deliver complete software and AI products end to end — requirements, architecture, implementation and deployment.",
     "Build reinforcement-learning and simulation systems, and integrate computer-vision models into production-facing tools.",
     "Design backend systems and relational databases, and integrate internal and third-party REST APIs.",
     "Act as the technical point of contact for clients, translating business requirements into actionable engineering tasks.",
   ]},
  {"role": "Software Developer  |  HMS Medical Equipment Company",
   "meta": "",
   "points": [
     "Developed the company's web presence and ERP/AI platform work, translating business requirements with stakeholders directly.",
     "Built responsive interfaces with consistent performance across devices, and optimised page performance.",
   ]},
  {"role": "Software Engineer  |  Enterprise Inventory Management System",
   "meta": "",
   "points": [
     "Designed and built a complete inventory management solution deployed over the company's internal network.",
     "Implemented authentication and role-based permissions across admin and staff users.",
     "Built an admin dashboard covering inventory management and operational reporting.",
     "Designed the SQLite schema and the internal networking layer connecting client workstations.",
   ]},
  {"role": "Android Game Developer  |  Independent / Google Play",
   "meta": "",
   "points": [
     "Designed, developed and published 3 Android games on Google Play, each taken from concept through store release.",
     "Achieved more than 5,000 combined downloads; ran Google Ads campaigns to support visibility and acquisition.",
   ]},
 ],

 "l_education": "Education",
 "education": {
   "degree": "Bachelor of Computer Engineering",
   "meta": "Tomsk State University of Control Systems and Radioelectronics (TUSUR) · Tomsk, Russia · Expected graduation: 2028",
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
 "languages": "<b>Arabic</b> — Native &nbsp;•&nbsp; <b>English</b> — Professional Working Proficiency &nbsp;•&nbsp; "
              "<b>Russian</b> — Professional Working Proficiency &nbsp;•&nbsp; <b>German</b> — Basic",
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
  {"role": "Инженер по разработке ПО и ИИ  |  Фриланс",
   "meta": "2022 — настоящее время",
   "points": [
     "Проектирую и поставляю законченные программные и ИИ-продукты: требования, архитектура, реализация и развёртывание.",
     "Разрабатываю системы обучения с подкреплением и моделирования, интегрирую модели компьютерного зрения в рабочие инструменты.",
     "Проектирую backend-системы и реляционные базы данных, интегрирую внутренние и сторонние REST API.",
     "Выступаю техническим контактным лицом для клиентов, перевожу бизнес-требования в конкретные инженерные задачи.",
   ]},
  {"role": "Разработчик ПО  |  HMS Medical Equipment Company",
   "meta": "",
   "points": [
     "Разработка веб-присутствия компании и работ по платформе ERP/ИИ, согласование требований напрямую с заказчиками.",
     "Создание адаптивных интерфейсов со стабильной производительностью на всех устройствах и оптимизация скорости загрузки.",
   ]},
  {"role": "Инженер-программист  |  Корпоративная система управления складом",
   "meta": "",
   "points": [
     "Спроектировал и построил комплексное решение для управления складом, развёрнутое во внутренней сети компании.",
     "Реализовал аутентификацию и ролевой доступ для администраторов и сотрудников.",
     "Разработал админ-панель для управления запасами и операционной отчётности.",
     "Спроектировал схему SQLite и сетевой уровень, связывающий рабочие станции с системой.",
   ]},
  {"role": "Разработчик мобильных игр  |  Независимо / Google Play",
   "meta": "",
   "points": [
     "Спроектировал, разработал и опубликовал 3 игры для Android в Google Play — от идеи до релиза в магазине.",
     "Более 5 000 суммарных загрузок; вёл кампании Google Ads для повышения видимости и привлечения пользователей.",
   ]},
 ],

 "l_education": "Образование",
 "education": {
   "degree": "Бакалавр компьютерной инженерии",
   "meta": "Томский государственный университет систем управления и радиоэлектроники (ТУСУР) · Томск, Россия · "
           "Ожидаемое окончание: 2028",
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
 "languages": "<b>Арабский</b> — родной &nbsp;•&nbsp; <b>Английский</b> — профессиональный рабочий уровень &nbsp;•&nbsp; "
              "<b>Русский</b> — профессиональный рабочий уровень &nbsp;•&nbsp; <b>Немецкий</b> — базовый",
}


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "cv")
    os.makedirs(out, exist_ok=True)
    for content, fn in ((EN, "cv_en.pdf"), (RU, "cv_ru.pdf")):
        p = build(content, os.path.join(out, fn))
        print("%-12s %6.1f KB" % (fn, os.path.getsize(p) / 1024))
