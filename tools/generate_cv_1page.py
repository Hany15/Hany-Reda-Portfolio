#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the one-page recruiter CV: cv/cv_en_1page.pdf and cv/cv_ru_1page.pdf.

The full CV runs 3-4 pages, which is right for a technical reviewer but wrong
for a first-pass recruiter who reads page one and stops. This condenses the
same facts to a single page: headline, availability, leadership evidence,
four roles, top projects, education and languages.

Reuses the layout primitives from generate_cv.py so both documents stay
visually identical.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, HRFlowable)

from generate_cv import INK, MUTED, ACCENT, RULE, LINK, CONTACT_EN, CONTACT_RU  # noqa: E402

# tighter type scale than the full CV so everything fits one page
S1 = {
 "name":    ParagraphStyle("n1", fontName="CV-B", fontSize=18, leading=21, textColor=INK, spaceAfter=1),
 "title":   ParagraphStyle("t1", fontName="CV-B", fontSize=8.8, leading=11.5, textColor=ACCENT, spaceAfter=2),
 "contact": ParagraphStyle("c1", fontName="CV", fontSize=7.4, leading=10.6, textColor=INK),
 "h2":      ParagraphStyle("h1", fontName="CV-B", fontSize=8.4, leading=10, textColor=ACCENT,
                           spaceBefore=6, spaceAfter=2),
 "body":    ParagraphStyle("b1", fontName="CV", fontSize=7.7, leading=10.4, textColor=INK, spaceAfter=2),
 "role":    ParagraphStyle("r1", fontName="CV-B", fontSize=8.1, leading=10.4, textColor=INK,
                           spaceBefore=3, spaceAfter=0),
 "meta":    ParagraphStyle("m1", fontName="CV-I", fontSize=7.2, leading=9.4, textColor=MUTED, spaceAfter=1),
 "bullet":  ParagraphStyle("bu1", fontName="CV", fontSize=7.6, leading=10.2, textColor=INK,
                           leftIndent=8, bulletIndent=1, spaceAfter=0.8),
 "small":   ParagraphStyle("s1", fontName="CV", fontSize=7.2, leading=9.8, textColor=MUTED, spaceAfter=1),
}


def rule1():
    return HRFlowable(width="100%", thickness=0.6, color=RULE, spaceBefore=0.5, spaceAfter=3)


def sec(label):
    return [Paragraph(label.upper(), S1["h2"]), rule1()]


def bl(items):
    return [Paragraph("<bullet>&#8226;</bullet>" + x, S1["bullet"]) for x in items]


def skills1(rows):
    data = [[Paragraph("<b>%s</b>" % k, S1["small"]), Paragraph(v, S1["body"])] for k, v in rows]
    t = Table(data, colWidths=[30 * mm, 142 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    return t


def build_one(c, path):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=11 * mm, bottomMargin=10 * mm,
                          title=c["pdf_title"], author="Mohamed Hany Reda",
                          subject=c["pdf_subject"])
    doc.addPageTemplates([PageTemplate(id="p", frames=[
        Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")])])

    f = [Paragraph(c["name"], S1["name"]),
         Paragraph(c["title"], S1["title"]),
         Paragraph(c["contact"], S1["contact"]),
         Spacer(1, 2),
         HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=2, spaceAfter=0)]

    f += sec(c["l_profile"]);  f.append(Paragraph(c["profile"], S1["body"]))
    f += sec(c["l_highlights"]); f += bl(c["highlights"])
    f += sec(c["l_skills"]);   f.append(skills1(c["skills"]))
    f += sec(c["l_exp"])
    for e in c["exp"]:
        f.append(Paragraph(e["role"], S1["role"]))
        f.append(Paragraph(e["meta"], S1["meta"]))
        f += bl(e["points"])
    f += sec(c["l_projects"]); f += bl(c["projects"])
    f += sec(c["l_edu"]);      f.append(Paragraph(c["edu"], S1["body"]))
    f += sec(c["l_langs"]);    f.append(Paragraph(c["langs"], S1["body"]))

    doc.build(f)
    return path


EN = {
 "pdf_title": "Mohamed Hany Reda - CV (one page)",
 "pdf_subject": "Full-Stack Software Engineer",
 "name": "MOHAMED HANY REDA",
 "title": "Full-Stack Software Engineer &nbsp;&middot;&nbsp; AI &amp; Machine Learning",
 "contact": CONTACT_EN,
 "l_profile": "Profile",
 "profile": "Full-stack software engineer with 3+ years building web, mobile and AI products end to end. "
            "I run products through the full cycle — requirements, architecture, build, test, release — and have led "
            "teams of up to 10 while owning the project budget. Available on-site, remotely or hybrid, and open to "
            "business trips.",
 "l_highlights": "Selected Highlights",
 "highlights": [
   "Led a team of <b>10</b> on an AI logistics system with a budget of about <b>$13,000</b> over 11 months.",
   "Led a team of <b>8</b> on a corporate web product and independently managed a budget of about <b>$10,000</b>.",
   "Shipped a published medical-imaging AI product: 90.21% accuracy, Grad-CAM explanations, Streamlit app and Telegram bot.",
   "Built a 400-lane logistics digital twin modelling ~96,400 items/hour, with 530+ automated tests.",
   "Published 3 Android titles (5,000+ downloads) and authored an Unreal Engine course on Udemy.",
 ],
 "l_skills": "Skills",
 "skills": [
   ("Engineering", "Python, Flutter/Dart, C++, C#, SQL, REST API, Docker, Git, PyTorch, OpenCV, Unreal Engine"),
   ("AI / ML", "Computer vision, explainable AI, reinforcement learning, LLM tooling, ML integration"),
   ("Delivery", "Agile, Scrum, Kanban, requirements analysis, SRS, user stories, backlog, risk, release management"),
   ("Leadership", "Team leadership up to 10, budget ownership, stakeholder communication, technical decisions"),
 ],
 "l_exp": "Experience",
 "exp": [
  {"role": "Full-Stack Developer / Technical Owner &nbsp;|&nbsp; HMS", "meta": "January 2024 &mdash; Present",
   "points": ["Own the corporate web product end to end — requirements from stakeholders, architecture, front and back end, release and support."]},
  {"role": "Full-Stack Developer / Product Delivery Owner &nbsp;|&nbsp; AuraGift", "meta": "January 2024 &mdash; Present",
   "points": ["Own the client side and UX of a live premium e-commerce platform; repeatable Firebase deployments with no downtime."]},
  {"role": "Technical Project Manager / Product Engineer &nbsp;|&nbsp; Freelance", "meta": "June 2022 &mdash; Present",
   "points": ["Single point of accountability from discovery and SRS through architecture, build and handover.",
              "Led a team of 10 on an AI logistics system, ~$13,000 budget, 11 months."]},
  {"role": "Technical Project Lead / Full-Stack Developer &nbsp;|&nbsp; HMS", "meta": "January 2023 &mdash; June 2023",
   "points": ["Led a team of 8 and managed a ~$10,000 budget while contributing to the build."]},
  {"role": "Unreal Engine Developer / Independent Product Owner &nbsp;|&nbsp; Indie", "meta": "January 2020 &mdash; Present",
   "points": ["Networked multiplayer with server authority and cloud player data; 3 published Android titles."]},
  {"role": "Media Team Lead &nbsp;|&nbsp; Resala Charity Organization, Egypt", "meta": "January 2020 &mdash; December 2020",
   "points": ["Led the media function; completed a six-month leadership and management programme."]},
 ],
 "l_projects": "Key Projects",
 "projects": [
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM on 4,083 X-rays; 90.21% accuracy. Research software, not a certified medical device.",
   "<b>High-Throughput Sorting-Center Digital Twin</b> — discrete-event simulation, PPO routing, multi-agent CTDE, 530+ tests.",
   "<b>Strict Drone Safe-RL</b> — PPO/LSTM under domain randomisation and fault injection. Simulation and research platform only.",
 ],
 "l_edu": "Education",
 "edu": "<b>Bachelor — Computer Science &amp; Engineering</b>, Tomsk State University of Control Systems and "
        "Radioelectronics (TUSUR) · 2026 &nbsp;•&nbsp; Unreal Engine course author (Udemy, 2024) &nbsp;•&nbsp; "
        "Digital Marketing (Google, 2021)",
 "l_langs": "Languages",
 "langs": "<b>Arabic</b> — Native &nbsp;•&nbsp; <b>English</b> — C2, full professional &nbsp;•&nbsp; "
          "<b>Russian</b> — B2, upper-intermediate",
}

RU = {
 "pdf_title": "Мохамед Хани Реда - Резюме (одна страница)",
 "pdf_subject": "Full-Stack разработчик",
 "name": "МОХАМЕД ХАНИ РЕДА",
 "title": "Full-Stack разработчик &nbsp;&middot;&nbsp; ИИ и машинное обучение",
 "contact": CONTACT_RU,
 "l_profile": "Профиль",
 "profile": "Full-Stack разработчик с опытом более 3 лет: веб-, мобильные и AI-продукты от требований до релиза. Веду продукты по полному циклу — требования, архитектура, разработка, тестирование, релиз — "
            "и руководил командами до 10 человек с ответственностью за бюджет. Готов работать в офисе, удалённо или "
            "гибридно, готов к командировкам.",
 "l_highlights": "Ключевые достижения",
 "highlights": [
   "Руководил командой из <b>10</b> специалистов на логистической AI-системе с бюджетом около <b>$13&nbsp;000</b> в течение 11 месяцев.",
   "Руководил командой из <b>8</b> специалистов на корпоративном веб-продукте и самостоятельно управлял бюджетом около <b>$10&nbsp;000</b>.",
   "Выпустил опубликованный AI-продукт для анализа медицинских изображений: точность 90,21%, объяснения Grad-CAM, приложение Streamlit и Telegram-бот.",
   "Построил цифровой двойник сортировочного центра на 400 линий с производительностью ~96&nbsp;400 единиц в час и более 530 автотестами.",
   "Опубликовал 3 игры для Android (5&nbsp;000+ загрузок) и авторский курс по Unreal Engine на Udemy.",
 ],
 "l_skills": "Навыки",
 "skills": [
   ("Инженерия", "Python, Flutter/Dart, C++, C#, SQL, REST API, Docker, Git, PyTorch, OpenCV, Unreal Engine"),
   ("ИИ / ML", "Компьютерное зрение, объяснимый ИИ, обучение с подкреплением, LLM-инструменты, интеграция ML"),
   ("Поставка", "Agile, Scrum, Kanban, анализ требований, ТЗ/SRS, user stories, бэклог, риски, релиз-менеджмент"),
   ("Лидерство", "Руководство командами до 10 человек, управление бюджетом, коммуникация со стейкхолдерами"),
 ],
 "l_exp": "Опыт работы",
 "exp": [
  {"role": "Full-Stack Developer / Technical Owner &nbsp;|&nbsp; HMS", "meta": "Январь 2024 &mdash; настоящее время",
   "points": ["Отвечаю за корпоративный веб-продукт целиком — требования, архитектура, frontend и backend, релиз и поддержка."]},
  {"role": "Full-Stack Developer / Product Delivery Owner &nbsp;|&nbsp; AuraGift", "meta": "Январь 2024 &mdash; настоящее время",
   "points": ["Отвечаю за клиентскую часть и UX работающей премиальной e-commerce платформы; повторяемые деплои на Firebase без простоев."]},
  {"role": "Technical Project Manager / Product Engineer &nbsp;|&nbsp; Фриланс", "meta": "Июнь 2022 &mdash; настоящее время",
   "points": ["Единая точка ответственности от интервью и ТЗ до архитектуры, разработки и передачи в эксплуатацию.",
              "Руководил командой из 10 специалистов на логистической AI-системе, бюджет ~$13&nbsp;000, 11 месяцев."]},
  {"role": "Technical Project Lead / Full-Stack Developer &nbsp;|&nbsp; HMS", "meta": "Январь 2023 &mdash; июнь 2023",
   "points": ["Руководил командой из 8 человек и управлял бюджетом ~$10&nbsp;000, совмещая с разработкой."]},
  {"role": "Unreal Engine Developer / Independent Product Owner &nbsp;|&nbsp; Indie", "meta": "Январь 2020 &mdash; настоящее время",
   "points": ["Сетевой мультиплеер с серверной авторизацией и облачным хранением данных; 3 опубликованные игры для Android."]},
  {"role": "Руководитель медианаправления &nbsp;|&nbsp; Resala Charity Organization, Египет", "meta": "Январь 2020 &mdash; декабрь 2020",
   "points": ["Руководил медианаправлением; прошёл шестимесячную программу развития лидерства и управления."]},
 ],
 "l_projects": "Ключевые проекты",
 "projects": [
   "<b>Fracture Detection AI</b> — EfficientNet-B0 и Grad-CAM на 4&nbsp;083 снимках; точность 90,21%. Исследовательское ПО, не сертифицированное медицинское изделие.",
   "<b>Цифровой двойник сортировочного центра</b> — дискретно-событийное моделирование, маршрутизация PPO, многоагентный CTDE, 530+ тестов.",
   "<b>Strict Drone Safe-RL</b> — PPO/LSTM при рандомизации предметной области и внедрении отказов. Только платформа моделирования и исследований.",
 ],
 "l_edu": "Образование",
 "edu": "<b>Бакалавр — информатика и вычислительная техника</b>, Томский государственный университет систем управления "
        "и радиоэлектроники (ТУСУР) · 2026 &nbsp;•&nbsp; Авторский курс по Unreal Engine (Udemy, 2024) &nbsp;•&nbsp; "
        "Цифровой маркетинг (Google, 2021)",
 "l_langs": "Языки",
 "langs": "<b>Арабский</b> — родной &nbsp;•&nbsp; <b>Английский</b> — C2, в совершенстве &nbsp;•&nbsp; "
          "<b>Русский</b> — B2, средне-продвинутый",
}


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cv")
    os.makedirs(out, exist_ok=True)
    from pypdf import PdfReader
    for c, fn in ((EN, "cv_en_1page.pdf"), (RU, "cv_ru_1page.pdf")):
        p = build_one(c, os.path.join(out, fn))
        pages = len(PdfReader(p).pages)
        flag = "" if pages == 1 else "   <-- MORE THAN ONE PAGE"
        print("  %-20s %5.0f KB   %d page(s)%s" % (fn, os.path.getsize(p) / 1024, pages, flag))
