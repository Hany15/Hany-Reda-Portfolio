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
                           bulletFontName="CV", spaceAfter=1.5),
 "skill":   ParagraphStyle("skill", fontName="CV", fontSize=8.55, leading=12,
                           textColor=INK, leftIndent=11, firstLineIndent=-11,
                           spaceAfter=2.5),
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
    # Single column, one "Label: value" line per row. A two-column table lets
    # ATS text extraction interleave labels and values (all labels first, then
    # all values); a colon-delimited single line always reads in order.
    return [Paragraph(f"<b>{k}:</b> {v}", S["skill"]) for k, v in rows]


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

    f += section(content["l_skills"])
    f += skills_table(content["skills"])

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

    f += section(content["l_languages"])
    f.append(Paragraph(content["languages"], S["body"]))

    doc.build(f)
    return path


# ══════════════════════════════════════════════════════════════════════════
LINK = ('<a href="{u}" color="#0E6E8C">{t}</a>')
CONTACT_EN = (
    "developeractionobject@gmail.com<br/>"
    + LINK.format(u="https://wa.me/79969382354", t="WhatsApp +7 996 938 2354") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://t.me/Hany_230", t="Telegram @Hany_230") + "<br/>"
    + LINK.format(u="https://github.com/Hany15", t="github.com/Hany15") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://www.linkedin.com/in/hany-reda-854667417", t="linkedin.com/in/hany-reda-854667417")
    + " &nbsp;|&nbsp; " + LINK.format(u="https://hany15.github.io/Hany-Reda-Portfolio/", t="hany15.github.io/Hany-Reda-Portfolio")
)
CONTACT_RU = (
    "developeractionobject@gmail.com<br/>"
    + LINK.format(u="https://wa.me/79969382354", t="WhatsApp +7 996 938 2354") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://t.me/Hany_230", t="Telegram @Hany_230") + "<br/>"
    + LINK.format(u="https://github.com/Hany15", t="github.com/Hany15") + " &nbsp;|&nbsp; "
    + LINK.format(u="https://www.linkedin.com/in/hany-reda-854667417", t="linkedin.com/in/hany-reda-854667417")
    + " &nbsp;|&nbsp; " + LINK.format(u="https://hany15.github.io/Hany-Reda-Portfolio/", t="hany15.github.io/Hany-Reda-Portfolio")
)

EN = {
 "pdf_title": "Mohamed Hany Reda - CV",
 "pdf_subject": "Full-Stack Software Engineer",
 "footer": "Mohamed Hany Reda  \u2014  Curriculum Vitae",
 "page_word": "Page",
 "name": "MOHAMED HANY REDA",
 "title": "Full-Stack Software Engineer",
 "tagline": "Remote \u2014 available worldwide, open to relocation &nbsp;|&nbsp; 3+ years of experience &nbsp;|&nbsp; led engineering teams of up to 10",
 "contact": CONTACT_EN,

 "l_summary": "Professional Summary",
 "summary":
   "Full-stack software engineer with 3+ years shipping production web, mobile and AI-enabled products end to end "
   "\u2014 architecture, backend APIs, frontend UI, automated testing and deployment. Sole owner of a multi-tenant "
   "ERP built on FastAPI, PostgreSQL and React with database-level tenant isolation, and of a live e-commerce "
   "platform with zero-downtime releases. Comfortable taking a feature from requirements through production, and "
   "have also led engineering teams of up to 10 and owned project budgets when a project needed it. Native Arabic, "
   "C2 English, B2 Russian \u2014 able to work directly with teams across three markets.",

 "l_skills": "Technical Skills",
 "skills": [
   ("Frontend", "JavaScript, React, Three.js, Flutter/Dart, responsive UI, cross-browser development"),
   ("Backend", "Python, FastAPI, Node.js, Firebase Cloud Functions, REST APIs, Clean Architecture, RBAC, multi-tenant systems"),
   ("Databases", "PostgreSQL, SQLAlchemy, Redis, SQLite, Row-Level Security"),
   ("DevOps &amp; Tooling", "Docker, Git, CI, Pytest, Ruff, MyPy"),
   ("Delivery &amp; Leadership", "Agile, Scrum, Kanban, requirements analysis, SRS, user stories, backlog, risk and release management; team leadership up to 10, budget ownership, stakeholder communication"),
   ("Also experienced with", "PyTorch, computer vision, reinforcement learning (PPO/SAC/A2C), Grad-CAM explainability, Unreal Engine 5"),
 ],

 "l_projects": "Key Projects",
 "projects": [
  {"name": "HMS \u2014 Multi-Tenant Enterprise ERP &amp; AI Platform",
   "meta": 'Python \u00b7 FastAPI \u00b7 PostgreSQL \u00b7 SQLAlchemy \u00b7 Redis \u00b7 React \u00b7 Docker \u2014 '
           '<a href="https://github.com/Hany15/hms-ai-erp-platform" color="#0E6E8C">repository</a>',
   "points": [
     "Sole owner of a multi-tenant ERP covering inventory, procurement, sales/CRM, finance, maintenance and HR in one Clean Architecture codebase.",
     "Enforced tenant isolation with PostgreSQL Row-Level Security at the database layer rather than trusting application code.",
     "Saudi ZATCA Phase 1 e-invoicing compliance, RBAC and audit logging, full Arabic/English RTL support.",
   ]},
  {"name": "AuraGift \u2014 Live E-Commerce Platform",
   "meta": 'JavaScript \u00b7 Node.js \u00b7 Firebase Cloud Functions \u00b7 Firebase Hosting \u00b7 UX/UI \u2014 '
           '<a href="https://auragift.web.app" color="#0E6E8C">auragift.web.app</a>',
   "points": [
     "Own the client side and UX of a premium digital-gifting platform in production.",
     "Built serverless order- and payment-processing logic with Node.js on Firebase Cloud Functions.",
     "Set up and maintain a repeatable, zero-downtime deployment pipeline on Firebase Hosting.",
   ]},
  {"name": "High-Throughput Sorting-Center Digital Twin",
   "meta": 'Python \u00b7 PyTorch \u00b7 Three.js \u00b7 Discrete-Event Simulation \u00b7 Pytest \u2014 '
           '<a href="https://github.com/Hany15/Amazon-sorting-center-digital-twin" color="#0E6E8C">repository</a>',
   "points": [
     "Built a 400-lane logistics digital twin on a custom deterministic simulation engine, modelling ~96,400 items/hour.",
     "Browser-based 3D operations view (Three.js) and a full automated test suite of 530+ tests.",
   ]},
  {"name": "Fracture Detection AI \u2014 Explainable Medical Imaging",
   "meta": 'Python \u00b7 PyTorch \u00b7 EfficientNet-B0 \u00b7 Streamlit \u2014 '
           '<a href="https://github.com/Hany15/AI-Medical-Assistant-" color="#0E6E8C">repository</a>',
   "points": [
     "End-to-end computer-vision product for bone-fracture detection: 90.21% accuracy, Grad-CAM explanations.",
     "Shipped as a Streamlit web app and Telegram bot with automated PDF reporting.",
   ],
   "note": "Research and portfolio software. Not a certified medical device."},
  {"name": "Additional engineering projects",
   "meta": "Reinforcement-learning research, multi-agent simulation, cross-platform apps, Unreal Engine",
   "points": [
     'Full list and source code at <a href="https://hany15.github.io/Hany-Reda-Portfolio/" color="#0E6E8C">hany15.github.io/Hany-Reda-Portfolio</a>.',
   ]},
 ],

 "l_experience": "Professional Experience",
 "experience": [
  {"role": "Full-Stack Developer / Technical Owner  |  HMS \u2014 medical equipment manufacturer",
   "meta": "Jan 2024 \u2014 Present",
   "points": [
     "Own the corporate web product end to end: requirements, architecture, front end and back end, release and support.",
     "Make the technical and architectural calls; integrate with internal company systems; surface technical risk before release.",
   ]},
  {"role": "Full-Stack Developer / Product Delivery Owner  |  AuraGift \u2014 digital gifting e-commerce",
   "meta": "Jan 2024 \u2014 Present",
   "points": [
     "Own the client side and UX of a live premium platform, from requirement through QA to production deploy.",
     "Built serverless Node.js functions on Firebase Cloud Functions to process orders and payments.",
     "Built the interface and UX layer \u2014 responsive layout, animation, cross-browser behaviour, performance tuning.",
   ]},
  {"role": "Technical Project Lead / Full-Stack Developer  |  HMS",
   "meta": "Jan 2023 \u2014 Jun 2023",
   "points": [
     "Led a team of 8 on a corporate web product while contributing to the build as a full-stack developer.",
     "Independently managed a project budget of roughly $10,000, and unblocked developers on hard technical problems.",
   ]},
  {"role": "Full-Stack Developer / Technical Project Manager  |  Freelance \u2014 Self-employed",
   "meta": "Jun 2022 \u2014 Present",
   "points": [
     "Single point of accountability between client and delivery: requirements, architecture, build and handover.",
     "Led a team of 10 on an AI-enabled logistics system, ~$13,000 budget over 11 months; built cross-platform Flutter apps, backend services and REST integrations.",
   ]},
  {"role": "Unreal Engine Developer / Independent Product Owner  |  Independent (indie)",
   "meta": "Jan 2020 \u2014 Present",
   "points": [
     "Shipped 3 Android titles on Google Play (5,000+ combined downloads); built networked multiplayer with server authority and cloud player data.",
   ]},
  {"role": "Media Team Lead  |  Resala Charity Organization, Egypt",
   "meta": "Jan 2020 \u2014 Dec 2020",
   "points": [
     "Led the media function at one of the largest charities in Egypt and the Middle East; completed a six-month leadership programme.",
   ]},
 ],

 "l_education": "Education &amp; Certifications",
 "education": {
   "degree": "Bachelor \u2014 Computer Science &amp; Engineering",
   "meta": "Tomsk State University of Control Systems and Radioelectronics (TUSUR) \u00b7 2026",
   "courses": "IBM Professional Course \u2014 Certificate of Appreciation &nbsp;\u00b7&nbsp; TUSUR \u2014 Recognition for "
              "contributing to an educational VR system &nbsp;\u00b7&nbsp; Unreal Engine course author (Udemy, 2024) "
              "&nbsp;\u00b7&nbsp; Digital Marketing (Google, 2021)",
 },

 "l_languages": "Languages",
 "languages": "<b>Arabic</b> \u2014 Native &nbsp;\u00b7&nbsp; <b>English</b> \u2014 C2, full professional &nbsp;\u00b7&nbsp; "
              "<b>Russian</b> \u2014 B2, upper-intermediate",
}

RU = {
 "pdf_title": "\u041c\u043e\u0445\u0430\u043c\u0435\u0434 \u0425\u0430\u043d\u0438 \u0420\u0435\u0434\u0430 - \u0420\u0435\u0437\u044e\u043c\u0435",
 "pdf_subject": "Full-Stack \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a",
 "footer": "\u041c\u043e\u0445\u0430\u043c\u0435\u0434 \u0425\u0430\u043d\u0438 \u0420\u0435\u0434\u0430  \u2014  \u0420\u0435\u0437\u044e\u043c\u0435",
 "page_word": "\u0421\u0442\u0440.",
 "name": "\u041c\u041e\u0425\u0410\u041c\u0415\u0414 \u0425\u0410\u041d\u0418 \u0420\u0415\u0414\u0410",
 "title": "Full-Stack \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a",
 "tagline": "\u0423\u0434\u0430\u043b\u0451\u043d\u043d\u043e \u2014 \u0433\u043e\u0442\u043e\u0432 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c \u0438\u0437 \u043b\u044e\u0431\u043e\u0439 \u0442\u043e\u0447\u043a\u0438 \u043c\u0438\u0440\u0430, \u0433\u043e\u0442\u043e\u0432 \u043a \u043f\u0435\u0440\u0435\u0435\u0437\u0434\u0443 &nbsp;|&nbsp; 3+ \u043b\u0435\u0442 \u043e\u043f\u044b\u0442\u0430 &nbsp;|&nbsp; \u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u043b \u043a\u043e\u043c\u0430\u043d\u0434\u0430\u043c\u0438 \u0434\u043e 10 \u0447\u0435\u043b\u043e\u0432\u0435\u043a",
 "contact": CONTACT_RU,

 "l_summary": "\u041f\u0440\u043e\u0444\u0438\u043b\u044c",
 "summary":
   "Full-Stack \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a \u0441 \u043e\u043f\u044b\u0442\u043e\u043c \u0431\u043e\u043b\u0435\u0435 3 \u043b\u0435\u0442: \u0432\u044b\u043f\u0443\u0441\u043a\u0430\u044e \u0432 \u043f\u0440\u043e\u0434\u0430\u043a\u0448\u0435\u043d \u0432\u0435\u0431-, \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0435 \u0438 AI-\u043f\u0440\u043e\u0434\u0443\u043a\u0442\u044b \u043f\u043e \u043f\u043e\u043b\u043d\u043e\u043c\u0443 \u0446\u0438\u043a\u043b\u0443 \u2014 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430, backend API, frontend UI, \u0430\u0432\u0442\u043e\u0442\u0435\u0441\u0442\u044b \u0438 \u0440\u0430\u0437\u0432\u0451\u0440\u0442\u044b\u0432\u0430\u043d\u0438\u0435. \u0415\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0432\u043b\u0430\u0434\u0435\u043b\u0435\u0446 \u043c\u0443\u043b\u044c\u0442\u0438\u0430\u0440\u0435\u043d\u0434\u043d\u043e\u0439 ERP \u043d\u0430 FastAPI, PostgreSQL \u0438 React \u0441 \u0438\u0437\u043e\u043b\u044f\u0446\u0438\u0435\u0439 \u0430\u0440\u0435\u043d\u0434\u0430\u0442\u043e\u0440\u043e\u0432 \u043d\u0430 \u0443\u0440\u043e\u0432\u043d\u0435 \u0411\u0414, \u0430 \u0442\u0430\u043a\u0436\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0449\u0435\u0439 e-commerce \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b \u0441 \u0440\u0435\u043b\u0438\u0437\u0430\u043c\u0438 \u0431\u0435\u0437 \u043f\u0440\u043e\u0441\u0442\u043e\u0435\u0432. \u0412\u0435\u0434\u0443 \u0444\u0438\u0447\u0443 \u043e\u0442 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u0439 \u0434\u043e \u043f\u0440\u043e\u0434\u0430\u043a\u0448\u0435\u043d\u0430; \u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u043b \u043a\u043e\u043c\u0430\u043d\u0434\u0430\u043c\u0438 \u0434\u043e 10 \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u0438 \u043e\u0442\u0432\u0435\u0447\u0430\u043b \u0437\u0430 \u0431\u044e\u0434\u0436\u0435\u0442\u044b \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432. \u0410\u0440\u0430\u0431\u0441\u043a\u0438\u0439 \u2014 \u0440\u043e\u0434\u043d\u043e\u0439, \u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439 \u2014 C2, \u0440\u0443\u0441\u0441\u043a\u0438\u0439 \u2014 B2.",

 "l_skills": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043d\u0430\u0432\u044b\u043a\u0438",
 "skills": [
   ("Frontend", "JavaScript, React, Three.js, Flutter/Dart, \u0430\u0434\u0430\u043f\u0442\u0438\u0432\u043d\u0430\u044f \u0432\u0451\u0440\u0441\u0442\u043a\u0430, \u043a\u0440\u043e\u0441\u0441\u0431\u0440\u0430\u0443\u0437\u0435\u0440\u043d\u043e\u0441\u0442\u044c"),
   ("Backend", "Python, FastAPI, Node.js, Firebase Cloud Functions, REST API, Clean Architecture, RBAC, \u043c\u0443\u043b\u044c\u0442\u0438\u0430\u0440\u0435\u043d\u0434\u043d\u044b\u0435 \u0441\u0438\u0441\u0442\u0435\u043c\u044b"),
   ("\u0411\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445", "PostgreSQL, SQLAlchemy, Redis, SQLite, Row-Level Security"),
   ("DevOps \u0438 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b", "Docker, Git, CI, Pytest, Ruff, MyPy"),
   ("\u0422\u0430\u043a\u0436\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u043b \u0441", "PyTorch, \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u043d\u043e\u0435 \u0437\u0440\u0435\u043d\u0438\u0435, \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435 \u0441 \u043f\u043e\u0434\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u0438\u0435\u043c (PPO/SAC/A2C), Grad-CAM, Unreal Engine 5"),
 ],

 "l_projects": "\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u044b",
 "projects": [
  {"name": "HMS \u2014 \u043c\u0443\u043b\u044c\u0442\u0438\u0430\u0440\u0435\u043d\u0434\u043d\u0430\u044f ERP \u0438 AI-\u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0430",
   "meta": 'Python \u00b7 FastAPI \u00b7 PostgreSQL \u00b7 SQLAlchemy \u00b7 Redis \u00b7 React \u00b7 Docker \u2014 '
           '<a href="https://github.com/Hany15/hms-ai-erp-platform" color="#0E6E8C">\u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0439</a>',
   "points": [
     "\u0415\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0432\u043b\u0430\u0434\u0435\u043b\u0435\u0446 \u043c\u0443\u043b\u044c\u0442\u0438\u0430\u0440\u0435\u043d\u0434\u043d\u043e\u0439 ERP: \u0441\u043a\u043b\u0430\u0434, \u0437\u0430\u043a\u0443\u043f\u043a\u0438, \u043f\u0440\u043e\u0434\u0430\u0436\u0438 \u0438 CRM, \u0444\u0438\u043d\u0430\u043d\u0441\u044b, \u043e\u0431\u0441\u043b\u0443\u0436\u0438\u0432\u0430\u043d\u0438\u0435 \u0438 \u043a\u0430\u0434\u0440\u044b \u0432 \u0435\u0434\u0438\u043d\u043e\u0439 \u043a\u043e\u0434\u043e\u0432\u043e\u0439 \u0431\u0430\u0437\u0435 \u043d\u0430 Clean Architecture.",
     "\u0418\u0437\u043e\u043b\u044f\u0446\u0438\u044f \u0430\u0440\u0435\u043d\u0434\u0430\u0442\u043e\u0440\u043e\u0432 \u0447\u0435\u0440\u0435\u0437 Row-Level Security \u0432 PostgreSQL \u043d\u0430 \u0443\u0440\u043e\u0432\u043d\u0435 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445, \u0430 \u043d\u0435 \u043d\u0430 \u0434\u043e\u0432\u0435\u0440\u0438\u0438 \u043a \u043a\u043e\u0434\u0443 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f.",
     "\u0421\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435 ZATCA Phase 1 (\u0421\u0430\u0443\u0434\u043e\u0432\u0441\u043a\u0430\u044f \u0410\u0440\u0430\u0432\u0438\u044f), RBAC \u0438 \u0436\u0443\u0440\u043d\u0430\u043b \u0430\u0443\u0434\u0438\u0442\u0430, \u043f\u043e\u043b\u043d\u0430\u044f \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u0430\u0440\u0430\u0431\u0441\u043a\u043e\u0433\u043e/\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u043e\u0433\u043e \u0438 RTL.",
   ]},
  {"name": "AuraGift \u2014 \u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0449\u0430\u044f e-commerce \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0430",
   "meta": 'JavaScript \u00b7 Node.js \u00b7 Firebase Cloud Functions \u00b7 Firebase Hosting \u00b7 UX/UI \u2014 '
           '<a href="https://auragift.web.app" color="#0E6E8C">auragift.web.app</a>',
   "points": [
     "\u041e\u0442\u0432\u0435\u0447\u0430\u044e \u0437\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u0441\u043a\u0443\u044e \u0447\u0430\u0441\u0442\u044c \u0438 UX \u043f\u0440\u0435\u043c\u0438\u0430\u043b\u044c\u043d\u043e\u0439 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b \u0446\u0438\u0444\u0440\u043e\u0432\u044b\u0445 \u043f\u043e\u0434\u0430\u0440\u043a\u043e\u0432 \u0432 \u043f\u0440\u043e\u0434\u0430\u043a\u0448\u0435\u043d\u0435.",
     "\u0420\u0435\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043b \u0431\u0435\u0441\u0441\u0435\u0440\u0432\u0435\u0440\u043d\u0443\u044e \u043b\u043e\u0433\u0438\u043a\u0443 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0437\u0430\u043a\u0430\u0437\u043e\u0432 \u0438 \u043f\u043b\u0430\u0442\u0435\u0436\u0435\u0439 \u043d\u0430 Node.js \u0432 Firebase Cloud Functions.",
     "\u041d\u0430\u0441\u0442\u0440\u043e\u0438\u043b \u0438 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u044e \u043f\u043e\u0432\u0442\u043e\u0440\u044f\u0435\u043c\u044b\u0439 \u043f\u0440\u043e\u0446\u0435\u0441\u0441 \u0434\u0435\u043f\u043b\u043e\u044f \u0431\u0435\u0437 \u043f\u0440\u043e\u0441\u0442\u043e\u0435\u0432 \u043d\u0430 Firebase Hosting.",
   ]},
  {"name": "\u0426\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u0434\u0432\u043e\u0439\u043d\u0438\u043a \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043e\u0447\u043d\u043e\u0433\u043e \u0446\u0435\u043d\u0442\u0440\u0430",
   "meta": 'Python \u00b7 PyTorch \u00b7 Three.js \u00b7 \u0434\u0438\u0441\u043a\u0440\u0435\u0442\u043d\u043e-\u0441\u043e\u0431\u044b\u0442\u0438\u0439\u043d\u043e\u0435 \u043c\u043e\u0434\u0435\u043b\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u00b7 Pytest \u2014 '
           '<a href="https://github.com/Hany15/Amazon-sorting-center-digital-twin" color="#0E6E8C">\u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0439</a>',
   "points": [
     "\u041f\u043e\u0441\u0442\u0440\u043e\u0438\u043b \u0446\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u0434\u0432\u043e\u0439\u043d\u0438\u043a \u043d\u0430 400 \u043b\u0438\u043d\u0438\u0439 \u043d\u0430 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u043c \u0434\u0435\u0442\u0435\u0440\u043c\u0438\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u043c \u0434\u0432\u0438\u0436\u043a\u0435, \u043c\u043e\u0434\u0435\u043b\u0438\u0440\u0443\u044e\u0449\u0438\u0439 ~96 400 \u0435\u0434\u0438\u043d\u0438\u0446 \u0432 \u0447\u0430\u0441.",
     "3D-\u043f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0432 \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0435 (Three.js) \u0438 \u043d\u0430\u0431\u043e\u0440 \u0438\u0437 \u0431\u043e\u043b\u0435\u0435 530 \u0430\u0432\u0442\u043e\u0442\u0435\u0441\u0442\u043e\u0432.",
   ]},
  {"name": "Fracture Detection AI \u2014 \u043e\u0431\u044a\u044f\u0441\u043d\u0438\u043c\u0430\u044f \u043c\u0435\u0434\u0438\u0446\u0438\u043d\u0441\u043a\u0430\u044f \u0432\u0438\u0437\u0443\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f",
   "meta": 'Python \u00b7 PyTorch \u00b7 EfficientNet-B0 \u00b7 Streamlit \u2014 '
           '<a href="https://github.com/Hany15/AI-Medical-Assistant-" color="#0E6E8C">\u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0439</a>',
   "points": [
     "\u0417\u0430\u043a\u043e\u043d\u0447\u0435\u043d\u043d\u044b\u0439 \u043f\u0440\u043e\u0434\u0443\u043a\u0442 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u043d\u043e\u0433\u043e \u0437\u0440\u0435\u043d\u0438\u044f \u0434\u043b\u044f \u0432\u044b\u044f\u0432\u043b\u0435\u043d\u0438\u044f \u043f\u0435\u0440\u0435\u043b\u043e\u043c\u043e\u0432: \u0442\u043e\u0447\u043d\u043e\u0441\u0442\u044c 90,21%, \u043e\u0431\u044a\u044f\u0441\u043d\u0435\u043d\u0438\u044f Grad-CAM.",
     "\u041f\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d \u043a\u0430\u043a \u0432\u0435\u0431-\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Streamlit \u0438 \u0431\u043e\u0442 Telegram \u0441 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u043c\u0438 PDF-\u043e\u0442\u0447\u0451\u0442\u0430\u043c\u0438.",
   ],
   "note": "\u0418\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u043e\u0435 \u0438 \u043f\u043e\u0440\u0442\u0444\u043e\u043b\u0438\u043e-\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435. \u041d\u0435 \u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u043c \u043c\u0435\u0434\u0438\u0446\u0438\u043d\u0441\u043a\u0438\u043c \u0438\u0437\u0434\u0435\u043b\u0438\u0435\u043c."},
  {"name": "\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u0438\u043d\u0436\u0435\u043d\u0435\u0440\u043d\u044b\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u044b",
   "meta": "\u0418\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f \u043f\u043e RL, \u043c\u043d\u043e\u0433\u043e\u0430\u0433\u0435\u043d\u0442\u043d\u043e\u0435 \u043c\u043e\u0434\u0435\u043b\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435, \u043a\u0440\u043e\u0441\u0441\u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0435\u043d\u043d\u044b\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f, Unreal Engine",
   "points": [
     '\u041f\u043e\u043b\u043d\u044b\u0439 \u0441\u043f\u0438\u0441\u043e\u043a \u0438 \u0438\u0441\u0445\u043e\u0434\u043d\u044b\u0439 \u043a\u043e\u0434: <a href="https://hany15.github.io/Hany-Reda-Portfolio/" color="#0E6E8C">hany15.github.io/Hany-Reda-Portfolio</a>.',
   ]},
 ],

 "l_experience": "\u041e\u043f\u044b\u0442 \u0440\u0430\u0431\u043e\u0442\u044b",
 "experience": [
  {"role": "Full-Stack Developer / Technical Owner  |  HMS \u2014 \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u043c\u0435\u0434\u0438\u0446\u0438\u043d\u0441\u043a\u043e\u0433\u043e \u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u044f",
   "meta": "\u042f\u043d\u0432. 2024 \u2014 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f",
   "points": [
     "\u041e\u0442\u0432\u0435\u0447\u0430\u044e \u0437\u0430 \u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u044b\u0439 \u0432\u0435\u0431-\u043f\u0440\u043e\u0434\u0443\u043a\u0442 \u0446\u0435\u043b\u0438\u043a\u043e\u043c: \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f, \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430, frontend \u0438 backend, \u0440\u0435\u043b\u0438\u0437 \u0438 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430.",
     "\u041f\u0440\u0438\u043d\u0438\u043c\u0430\u044e \u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0438 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u043d\u044b\u0435 \u0440\u0435\u0448\u0435\u043d\u0438\u044f; \u0438\u043d\u0442\u0435\u0433\u0440\u0438\u0440\u0443\u044e \u0441 \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u043c\u0438 \u0441\u0438\u0441\u0442\u0435\u043c\u0430\u043c\u0438 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438; \u0432\u044b\u044f\u0432\u043b\u044f\u044e \u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0440\u0438\u0441\u043a\u0438 \u0434\u043e \u0440\u0435\u043b\u0438\u0437\u0430.",
   ]},
  {"role": "Full-Stack Developer / Product Delivery Owner  |  AuraGift \u2014 e-commerce \u0446\u0438\u0444\u0440\u043e\u0432\u044b\u0445 \u043f\u043e\u0434\u0430\u0440\u043a\u043e\u0432",
   "meta": "\u042f\u043d\u0432. 2024 \u2014 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f",
   "points": [
     "\u041e\u0442\u0432\u0435\u0447\u0430\u044e \u0437\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u0441\u043a\u0443\u044e \u0447\u0430\u0441\u0442\u044c \u0438 UX \u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0449\u0435\u0439 \u043f\u0440\u0435\u043c\u0438\u0430\u043b\u044c\u043d\u043e\u0439 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b \u2014 \u043e\u0442 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u0439 \u0447\u0435\u0440\u0435\u0437 QA \u0434\u043e \u0434\u0435\u043f\u043b\u043e\u044f.",
     "\u0420\u0435\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043b \u0431\u0435\u0441\u0441\u0435\u0440\u0432\u0435\u0440\u043d\u044b\u0435 \u0444\u0443\u043d\u043a\u0446\u0438\u0438 \u043d\u0430 Node.js \u0432 Firebase Cloud Functions \u0434\u043b\u044f \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0437\u0430\u043a\u0430\u0437\u043e\u0432 \u0438 \u043f\u043b\u0430\u0442\u0435\u0436\u0435\u0439.",
     "\u041f\u043e\u0441\u0442\u0440\u043e\u0438\u043b \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0438 UX-\u0441\u043b\u043e\u0439 \u2014 \u0430\u0434\u0430\u043f\u0442\u0438\u0432\u043d\u0430\u044f \u0432\u0451\u0440\u0441\u0442\u043a\u0430, \u0430\u043d\u0438\u043c\u0430\u0446\u0438\u0438, \u043a\u0440\u043e\u0441\u0441\u0431\u0440\u0430\u0443\u0437\u0435\u0440\u043d\u043e\u0441\u0442\u044c, \u043e\u043f\u0442\u0438\u043c\u0438\u0437\u0430\u0446\u0438\u044f \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438.",
   ]},
  {"role": "Technical Project Lead / Full-Stack Developer  |  HMS",
   "meta": "\u042f\u043d\u0432. 2023 \u2014 \u0438\u044e\u043d\u044c 2023",
   "points": [
     "\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u043b \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 \u0438\u0437 8 \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043d\u0430 \u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u043e\u043c \u0432\u0435\u0431-\u043f\u0440\u043e\u0434\u0443\u043a\u0442\u0435, \u0441\u043e\u0432\u043c\u0435\u0449\u0430\u044f \u0441 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u043e\u0439.",
     "\u0421\u0430\u043c\u043e\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e \u0443\u043f\u0440\u0430\u0432\u043b\u044f\u043b \u0431\u044e\u0434\u0436\u0435\u0442\u043e\u043c \u043f\u0440\u043e\u0435\u043a\u0442\u0430 \u043e\u043a\u043e\u043b\u043e $10 000 \u0438 \u043f\u043e\u043c\u043e\u0433\u0430\u043b \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u0430\u043c \u0441 \u0441\u043b\u043e\u0436\u043d\u044b\u043c\u0438 \u0437\u0430\u0434\u0430\u0447\u0430\u043c\u0438.",
   ]},
  {"role": "Full-Stack Developer / Technical Project Manager  |  \u0424\u0440\u0438\u043b\u0430\u043d\u0441 \u2014 \u0441\u0430\u043c\u043e\u0437\u0430\u043d\u044f\u0442\u043e\u0441\u0442\u044c",
   "meta": "\u0418\u044e\u043d\u044c 2022 \u2014 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f",
   "points": [
     "\u0415\u0434\u0438\u043d\u0430\u044f \u0442\u043e\u0447\u043a\u0430 \u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0441\u0442\u0438 \u043c\u0435\u0436\u0434\u0443 \u0437\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u043e\u043c \u0438 \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0435\u0439: \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f, \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430, \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0438 \u043f\u0435\u0440\u0435\u0434\u0430\u0447\u0430.",
     "\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u043b \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 \u0438\u0437 10 \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043d\u0430 \u043b\u043e\u0433\u0438\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0439 AI-\u0441\u0438\u0441\u0442\u0435\u043c\u0435, \u0431\u044e\u0434\u0436\u0435\u0442 ~$13 000 \u0437\u0430 11 \u043c\u0435\u0441\u044f\u0446\u0435\u0432; \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u043b \u043a\u0440\u043e\u0441\u0441\u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0435\u043d\u043d\u044b\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f Flutter, backend-\u0441\u0435\u0440\u0432\u0438\u0441\u044b \u0438 REST-\u0438\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u0438.",
   ]},
  {"role": "Unreal Engine Developer / Independent Product Owner  |  \u041d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u0430\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430 (indie)",
   "meta": "\u042f\u043d\u0432. 2020 \u2014 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f",
   "points": [
     "\u0412\u044b\u043f\u0443\u0441\u0442\u0438\u043b 3 \u0438\u0433\u0440\u044b \u0434\u043b\u044f Android \u0432 Google Play (5 000+ \u0437\u0430\u0433\u0440\u0443\u0437\u043e\u043a); \u0440\u0435\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043b \u0441\u0435\u0442\u0435\u0432\u043e\u0439 \u043c\u0443\u043b\u044c\u0442\u0438\u043f\u043b\u0435\u0435\u0440 \u0441 \u0441\u0435\u0440\u0432\u0435\u0440\u043d\u043e\u0439 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0435\u0439 \u0438 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u043c \u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435\u043c \u0434\u0430\u043d\u043d\u044b\u0445 \u0438\u0433\u0440\u043e\u043a\u043e\u0432.",
   ]},
  {"role": "\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u043c\u0435\u0434\u0438\u0430\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f  |  Resala Charity Organization, \u0415\u0433\u0438\u043f\u0435\u0442",
   "meta": "\u042f\u043d\u0432. 2020 \u2014 \u0434\u0435\u043a. 2020",
   "points": [
     "\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u043b \u043c\u0435\u0434\u0438\u0430\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435\u043c \u0432 \u043e\u0434\u043d\u043e\u0439 \u0438\u0437 \u043a\u0440\u0443\u043f\u043d\u0435\u0439\u0448\u0438\u0445 \u0431\u043b\u0430\u0433\u043e\u0442\u0432\u043e\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0445 \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0439 \u0415\u0433\u0438\u043f\u0442\u0430; \u043f\u0440\u043e\u0448\u0451\u043b \u0448\u0435\u0441\u0442\u0438\u043c\u0435\u0441\u044f\u0447\u043d\u0443\u044e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0443 \u043b\u0438\u0434\u0435\u0440\u0441\u0442\u0432\u0430.",
   ]},
 ],

 "l_education": "\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 \u0438 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u044b",
 "education": {
   "degree": "\u0411\u0430\u043a\u0430\u043b\u0430\u0432\u0440 \u2014 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u043a\u0430 \u0438 \u0432\u044b\u0447\u0438\u0441\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0442\u0435\u0445\u043d\u0438\u043a\u0430",
   "meta": "\u0422\u043e\u043c\u0441\u043a\u0438\u0439 \u0433\u043e\u0441\u0443\u0434\u0430\u0440\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0443\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442 \u0441\u0438\u0441\u0442\u0435\u043c \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0438 \u0440\u0430\u0434\u0438\u043e\u044d\u043b\u0435\u043a\u0442\u0440\u043e\u043d\u0438\u043a\u0438 (\u0422\u0423\u0421\u0423\u0420) \u00b7 2026",
   "courses": "IBM Professional Course \u2014 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 &nbsp;\u00b7&nbsp; \u0422\u0423\u0421\u0423\u0420 \u2014 \u043f\u0440\u0438\u0437\u043d\u0430\u043d\u0438\u0435 \u0437\u0430 \u0432\u043a\u043b\u0430\u0434 \u0432 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u043d\u0443\u044e VR-\u0441\u0438\u0441\u0442\u0435\u043c\u0443 &nbsp;\u00b7&nbsp; \u0410\u0432\u0442\u043e\u0440\u0441\u043a\u0438\u0439 \u043a\u0443\u0440\u0441 \u043f\u043e Unreal Engine (Udemy, 2024) &nbsp;\u00b7&nbsp; \u0426\u0438\u0444\u0440\u043e\u0432\u043e\u0439 \u043c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433 (Google, 2021)",
 },

 "l_languages": "\u042f\u0437\u044b\u043a\u0438",
 "languages": "<b>\u0410\u0440\u0430\u0431\u0441\u043a\u0438\u0439</b> \u2014 \u0440\u043e\u0434\u043d\u043e\u0439 &nbsp;\u00b7&nbsp; <b>\u0410\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439</b> \u2014 C2 &nbsp;\u00b7&nbsp; <b>\u0420\u0443\u0441\u0441\u043a\u0438\u0439</b> \u2014 B2",
}

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "cv")
    os.makedirs(out, exist_ok=True)
    for content, fn in ((EN, "cv_en.pdf"), (RU, "cv_ru.pdf")):
        p = build(content, os.path.join(out, fn))
        print("%-12s %6.1f KB" % (fn, os.path.getsize(p) / 1024))
