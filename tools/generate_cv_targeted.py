#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Role-targeted one-page CVs.

One CV can't win two different searches. A recruiter hiring a Full-Stack
engineer and one hiring an ML engineer scan for different things in the first
six seconds. These variants keep every real fact but re-order the page so the
top third answers *this* role: the profile line, the highlights, the skills and
the project order all pivot, while experience, education and languages stay
identical.

Nothing is invented and nothing is dropped — the AI work is still on the
full-stack CV (lower down) and the full-stack work is still on the AI CV. Only
the emphasis moves.

Outputs (in cv/):
  cv_fullstack_en.pdf   cv_fullstack_ru.pdf
  cv_ai_en.pdf          cv_ai_ru.pdf
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_cv_1page import build_one, EN as BASE_EN, RU as BASE_RU  # noqa: E402


def variant(base, over):
    """Start from the shared one-page content and override the role-sensitive
    fields. Experience, education, languages and contact come through as-is."""
    c = dict(base)
    c.update(over)
    return c


# ── shared experience, trimmed to the same roles both variants show ─────────
# (kept from the base one-pager: these are the real roles and dates)

# ════════════════════════════════════════════════════════════════════════════
# FULL-STACK — leads with shipped products: ERP, e-commerce, then the rest
# ════════════════════════════════════════════════════════════════════════════
FS_EN = variant(BASE_EN, {
 "pdf_title": "Mohamed Hany Reda - CV (Full-Stack)",
 "pdf_subject": "Full-Stack Software Engineer",
 "title": "Full-Stack Software Engineer &nbsp;&middot;&nbsp; JavaScript · React · Python · FastAPI",
 "profile":
   "Full-stack software engineer with 3+ years building and shipping web, mobile and AI-enabled products "
   "end to end — architecture, backend APIs, frontend UI, automated tests and deployment. Sole owner of a "
   "multi-tenant ERP on FastAPI + PostgreSQL + React, and of a live e-commerce platform with zero-downtime "
   "releases. I take a feature from requirements to production, and have led teams of up to 10 when a project "
   "needed it. Available remotely worldwide, on-site or hybrid; open to relocation.",
 "l_highlights": "Selected Highlights",
 "highlights": [
   "Sole owner of a <b>multi-tenant ERP</b> (inventory, procurement, sales/CRM, finance, HR) on FastAPI, "
   "PostgreSQL and React, with tenant isolation enforced by PostgreSQL Row-Level Security at the database layer.",
   "Own the client side and UX of a <b>live e-commerce platform</b>, with serverless Node.js order/payment "
   "logic on Firebase and a repeatable zero-downtime deploy pipeline.",
   "Built a <b>400-lane logistics digital twin</b> modelling ~96,400 items/hour, with a browser 3D view "
   "(Three.js) and 530+ automated tests.",
   "Shipped a published <b>medical-imaging AI</b> product end to end: 90.21% accuracy, Grad-CAM, Streamlit app "
   "and Telegram bot.",
   "Led a team of <b>10</b> on an AI logistics system (~$13,000, 11 months) and a team of <b>8</b> on a "
   "corporate web product (~$10,000 budget).",
 ],
 "l_skills": "Skills",
 "skills": [
   ("Frontend", "JavaScript, React, Three.js, Flutter/Dart, responsive UI, cross-browser development"),
   ("Backend", "Python, FastAPI, Node.js, Firebase Cloud Functions, REST APIs, Clean Architecture, RBAC, multi-tenant"),
   ("Databases", "PostgreSQL, SQLAlchemy, Redis, SQLite, Row-Level Security"),
   ("DevOps &amp; tooling", "Docker, Git, CI, Pytest, Ruff, MyPy"),
   ("Also", "PyTorch, computer vision, reinforcement learning, Grad-CAM, Unreal Engine 5; team leadership, budget ownership"),
 ],
 "l_projects": "Key Projects",
 "projects": [
   "<b>HMS — Multi-Tenant ERP</b> — FastAPI · PostgreSQL (RLS) · React · Docker; ZATCA Phase 1 e-invoicing, RBAC, Arabic/English RTL.",
   "<b>AuraGift — Live E-Commerce</b> — JavaScript · Node.js · Firebase Cloud Functions; serverless orders/payments, zero-downtime deploys.",
   "<b>High-Throughput Sorting-Center Digital Twin</b> — Python · Three.js · discrete-event simulation; ~96,400 items/hour, 530+ tests.",
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM; 90.21% accuracy. Research software, not a certified medical device.",
 ],
})

FS_RU = variant(BASE_RU, {
 "pdf_title": "Мохамед Хани Реда - Резюме (Full-Stack)",
 "pdf_subject": "Full-Stack разработчик",
 "title": "Full-Stack разработчик &nbsp;&middot;&nbsp; JavaScript · React · Python · FastAPI",
 "profile":
   "Full-Stack разработчик (инженер-программист) с опытом более 3 лет: создаю и довожу до релиза веб-, мобильные и AI-продукты по "
   "полному циклу — архитектура, backend API, frontend UI, автотесты и деплой. Единственный владелец "
   "мультиарендной ERP на FastAPI + PostgreSQL + React и работающей e-commerce платформы с релизами без "
   "простоев. Веду фичу от требований до продакшена; руководил командами до 10 человек, когда это было нужно. "
   "Готов работать удалённо, в офисе или гибридно; готов к переезду.",
 "l_highlights": "Ключевые достижения",
 "highlights": [
   "Единственный владелец <b>мультиарендной ERP</b> (склад, закупки, продажи/CRM, финансы, кадры) на FastAPI, "
   "PostgreSQL и React; изоляция арендаторов через Row-Level Security на уровне БД.",
   "Отвечаю за клиентскую часть и UX <b>работающей e-commerce платформы</b>: бессерверная логика заказов и "
   "платежей на Node.js/Firebase и повторяемый деплой без простоев.",
   "Построил <b>цифровой двойник</b> на 400 линий (~96&nbsp;400 единиц в час), 3D-вид в браузере (Three.js) и 530+ автотестов.",
   "Выпустил <b>AI для медицинских изображений</b> по полному циклу: точность 90,21%, Grad-CAM, приложение Streamlit и Telegram-бот.",
   "Руководил командой из <b>10</b> на AI-логистике (~$13&nbsp;000, 11 мес.) и командой из <b>8</b> на корпоративном веб-продукте (бюджет ~$10&nbsp;000).",
 ],
 "l_skills": "Навыки",
 "skills": [
   ("Frontend", "JavaScript, React, Three.js, Flutter/Dart, адаптивная вёрстка, кроссбраузерность"),
   ("Backend", "Python, FastAPI, Node.js, Firebase Cloud Functions, REST API, Clean Architecture, RBAC, мультиарендность"),
   ("Базы данных", "PostgreSQL, SQLAlchemy, Redis, SQLite, Row-Level Security"),
   ("DevOps и инструменты", "Docker, Git, CI, Pytest, Ruff, MyPy"),
   ("Также", "PyTorch, компьютерное зрение, обучение с подкреплением, Grad-CAM, Unreal Engine 5; руководство командами, бюджет"),
 ],
 "l_projects": "Ключевые проекты",
 "projects": [
   "<b>HMS — мультиарендная ERP</b> — FastAPI · PostgreSQL (RLS) · React · Docker; ZATCA Phase 1, RBAC, арабский/английский и RTL.",
   "<b>AuraGift — e-commerce</b> — JavaScript · Node.js · Firebase Cloud Functions; бессерверные заказы/платежи, деплой без простоев.",
   "<b>Цифровой двойник сортировочного центра</b> — Python · Three.js · дискретно-событийное моделирование; ~96&nbsp;400 ед./час, 530+ тестов.",
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM; точность 90,21%. Исследовательское ПО, не медицинское изделие.",
 ],
})

# ════════════════════════════════════════════════════════════════════════════
# AI / ML — leads with models shipped as real products, then the engineering
# ════════════════════════════════════════════════════════════════════════════
AI_EN = variant(BASE_EN, {
 "pdf_title": "Mohamed Hany Reda - CV (AI / ML)",
 "pdf_subject": "AI / Machine Learning Engineer",
 "title": "AI / Machine Learning Engineer &nbsp;&middot;&nbsp; Computer Vision · Reinforcement Learning",
 "profile":
   "Machine-learning engineer with 3+ years building AI products and shipping them as real applications, not "
   "notebooks — computer vision, reinforcement learning and explainable AI. I take a model from data through "
   "training and evaluation to a running product, and I bring full-stack engineering (Python, FastAPI, Docker) "
   "so the model actually reaches users. Available remotely worldwide, on-site or hybrid; open to relocation.",
 "l_highlights": "Selected Highlights",
 "highlights": [
   "Shipped a published <b>medical-imaging AI</b>: EfficientNet-B0, 90.21% accuracy, Grad-CAM explanations, "
   "delivered as a Streamlit app and Telegram bot with automated PDF reports.",
   "Built a 400-lane logistics <b>digital twin with PPO routing and multi-agent CTDE</b> reinforcement "
   "learning, modelling ~96,400 items/hour, with 530+ tests.",
   "Trained <b>safe reinforcement-learning drone control</b> (PPO/LSTM) under domain randomisation and fault "
   "injection; exported to ONNX.",
   "Built an <b>evolutionary racing lab</b> comparing PPO/SAC/A2C across procedurally generated worlds, with "
   "saliency and activation explainability.",
   "Delivered the full <b>deployment layer</b> around each model — apps, APIs, dashboards — so the AI ships.",
 ],
 "l_skills": "Skills",
 "skills": [
   ("AI / ML", "PyTorch, computer vision (EfficientNet, OpenCV), reinforcement learning (PPO/SAC/A2C, multi-agent CTDE), explainable AI (Grad-CAM, saliency), LLM tooling"),
   ("ML engineering", "Python, training/eval loops, data pipelines, ONNX, experiment logging, reproducible runs, Pytest"),
   ("Deployment", "FastAPI, Streamlit, Docker, SQLite/PostgreSQL, Telegram bots, PySide6 dashboards"),
   ("Also full-stack", "JavaScript, React, Flutter/Dart, Node.js/Firebase — I ship the product around the model"),
   ("Delivery", "Requirements, agile, team leadership up to 10, budget ownership"),
 ],
 "l_projects": "Key Projects",
 "projects": [
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM on 4,083 X-rays; 90.21% accuracy; Streamlit + Telegram. Research software, not a certified medical device.",
   "<b>Sorting-Center Digital Twin</b> — PPO routing, multi-agent CTDE, discrete-event simulation; ~96,400 items/hour, 530+ tests.",
   "<b>Strict Drone Safe-RL</b> — PPO/LSTM under domain randomisation and fault injection; ONNX export. Simulation/research platform only.",
   "<b>AI Evolution Racing Lab</b> — PPO/SAC/A2C tournaments across procedural worlds, with saliency/activation explainability.",
   "<b>Multi-Agent Air-Defense Simulation</b> — cooperating agents, self-play, trajectory prediction, PySide6 live dashboard.",
 ],
})

AI_RU = variant(BASE_RU, {
 "pdf_title": "Мохамед Хани Реда - Резюме (AI / ML)",
 "pdf_subject": "Инженер AI / ML",
 "title": "Инженер AI / ML &nbsp;&middot;&nbsp; Компьютерное зрение · Обучение с подкреплением",
 "profile":
   "Инженер по машинному обучению с опытом более 3 лет: строю AI-продукты и довожу их до реальных приложений, "
   "а не ноутбуков — компьютерное зрение, обучение с подкреплением и объяснимый ИИ. Веду модель от данных до "
   "работающего продукта и добавляю full-stack инженерию (Python, FastAPI, Docker), чтобы модель дошла до "
   "пользователей. Готов к удалённой работе, офису, гибриду и переезду.",
 "l_highlights": "Ключевые достижения",
 "highlights": [
   "Выпустил <b>AI для медицинских изображений</b>: EfficientNet-B0, точность 90,21%, объяснения Grad-CAM; "
   "приложение Streamlit и Telegram-бот с автоматическими PDF-отчётами.",
   "Построил логистический <b>цифровой двойник с маршрутизацией PPO и многоагентным CTDE</b>, ~96&nbsp;400 "
   "единиц в час, 530+ тестов.",
   "Обучил <b>безопасное RL-управление дроном</b> (PPO/LSTM) при рандомизации предметной области и внедрении "
   "отказов; экспорт в ONNX.",
   "Создал <b>эволюционную гоночную лабораторию</b>, сравнивающую PPO/SAC/A2C в процедурных мирах, с "
   "объяснимостью (saliency, активации).",
   "Реализовал полный <b>слой деплоя</b> вокруг каждой модели — приложения, API, дашборды.",
 ],
 "l_skills": "Навыки",
 "skills": [
   ("AI / ML", "PyTorch, компьютерное зрение (EfficientNet, OpenCV), обучение с подкреплением (PPO/SAC/A2C, многоагентный CTDE), объяснимый ИИ (Grad-CAM, saliency), LLM-инструменты"),
   ("ML-инженерия", "Python, циклы обучения/оценки, пайплайны данных, ONNX, логирование экспериментов, воспроизводимость, Pytest"),
   ("Деплой", "FastAPI, Streamlit, Docker, SQLite/PostgreSQL, Telegram-боты, дашборды PySide6"),
   ("Также full-stack", "JavaScript, React, Flutter/Dart, Node.js/Firebase — собираю продукт вокруг модели"),
   ("Поставка", "Требования, agile, руководство командами до 10, ответственность за бюджет"),
 ],
 "l_projects": "Ключевые проекты",
 "projects": [
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM на 4&nbsp;083 снимках; точность 90,21%; Streamlit + Telegram. Исследовательское ПО, не медицинское изделие.",
   "<b>Цифровой двойник сортировочного центра</b> — маршрутизация PPO, многоагентный CTDE, дискретно-событийное моделирование; ~96&nbsp;400 ед./час, 530+ тестов.",
   "<b>Strict Drone Safe-RL</b> — PPO/LSTM при рандомизации и внедрении отказов; экспорт в ONNX. Только платформа моделирования.",
   "<b>AI Evolution Racing Lab</b> — турниры PPO/SAC/A2C в процедурных мирах; объяснимость (saliency, активации). Плюс многоагентная симуляция ПВО (self-play, PySide6).",
 ],
})

# ════════════════════════════════════════════════════════════════════════════
# INTERNATIONAL — leads with the trilingual, client-facing bridge: an engineer
# who ships AND talks to international clients in their own language. Aimed at
# Russian/CIS outsourcing firms serving English-speaking clients and at teams
# expanding into MENA/GCC.
# ════════════════════════════════════════════════════════════════════════════
INTL_EN = variant(BASE_EN, {
 "pdf_title": "Mohamed Hany Reda - CV (International)",
 "pdf_subject": "International Full-Stack Software Engineer",
 "title": "International Full-Stack Engineer &nbsp;&middot;&nbsp; Client-Facing · EN · AR · RU",
 "profile":
   "Full-stack software engineer who works directly with international clients in their own language — "
   "fluent in Arabic (native), English (C2) and Russian (B2). I take products end to end (FastAPI, React, "
   "PostgreSQL) and own the client side too: discovery, requirements, demos and handover. A natural bridge "
   "for teams serving English-speaking or MENA/GCC markets — an engineer who ships and speaks to the client. "
   "Available remotely worldwide; open to relocation.",
 "l_highlights": "Selected Highlights",
 "highlights": [
   "<b>Trilingual</b> — Arabic (native), English (C2, full professional), Russian (B2): work directly with "
   "clients across MENA, the GCC, CIS and English-speaking markets.",
   "Single point of accountability on freelance projects — from client discovery and requirements (SRS) "
   "through architecture, build and handover.",
   "Sole owner of a <b>multi-tenant ERP</b> (FastAPI, PostgreSQL RLS, React) with Saudi ZATCA e-invoicing and "
   "full Arabic/English RTL — built for a specific regional market.",
   "Own the client side and UX of a <b>live e-commerce platform</b>, with zero-downtime releases.",
   "Led teams of up to <b>10</b>, translating between client needs and technical delivery.",
 ],
 "l_skills": "Skills",
 "skills": [
   ("Engineering", "JavaScript, React, Node.js, Python, FastAPI, PostgreSQL, Docker, Flutter/Dart, REST APIs"),
   ("Client &amp; delivery", "Discovery interviews, requirements/SRS, demos, stakeholder communication, agile, release and handover"),
   ("Languages", "Arabic — native · English — C2, full professional · Russian — B2"),
   ("Localization", "Arabic/English RTL, Saudi ZATCA e-invoicing, multi-market products"),
   ("Also", "PyTorch, computer vision, reinforcement learning; team leadership up to 10"),
 ],
 "l_projects": "Key Projects",
 "projects": [
   "<b>HMS — Multi-Tenant ERP</b> — FastAPI · PostgreSQL (RLS) · React · Docker; ZATCA Phase 1 e-invoicing, RBAC, Arabic/English RTL.",
   "<b>AuraGift — Live E-Commerce</b> — JavaScript · Node.js · Firebase Cloud Functions; serverless orders/payments, zero-downtime deploys.",
   "<b>High-Throughput Sorting-Center Digital Twin</b> — Python · Three.js · discrete-event simulation; ~96,400 items/hour, 530+ tests.",
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM; 90.21% accuracy. Research software, not a certified medical device.",
 ],
})

INTL_RU = variant(BASE_RU, {
 "pdf_title": "Мохамед Хани Реда - Резюме (International)",
 "pdf_subject": "Full-Stack инженер-программист · международные проекты",
 "title": "Full-Stack инженер · международные проекты &nbsp;&middot;&nbsp; EN · AR · RU",
 "profile":
   "Full-Stack разработчик (инженер-программист), работаю напрямую с международными клиентами на их языке — "
   "арабский (родной), английский (C2), русский (B2). Веду продукты по полному циклу (FastAPI, React, "
   "PostgreSQL) и отвечаю за работу с клиентом: сбор требований, демо, передача. Естественный мост для команд, "
   "работающих с англоязычными или ближневосточными рынками. Готов к удалённой работе и переезду.",
 "l_highlights": "Ключевые достижения",
 "highlights": [
   "<b>Три языка</b> — арабский (родной), английский (C2), русский (B2): работа напрямую с клиентами MENA, "
   "GCC, СНГ и англоязычных рынков.",
   "Единая точка ответственности на фриланс-проектах — от сбора требований (ТЗ) до архитектуры, разработки и передачи.",
   "Единственный владелец <b>мультиарендной ERP</b> (FastAPI, PostgreSQL RLS, React) с ZATCA и арабским/английским RTL — под конкретный региональный рынок.",
   "Отвечаю за клиентскую часть и UX <b>работающей e-commerce платформы</b>; релизы без простоев.",
   "Руководил командами до <b>10</b> человек, переводя между потребностями клиента и технической реализацией.",
 ],
 "l_skills": "Навыки",
 "skills": [
   ("Инженерия", "JavaScript, React, Node.js, Python, FastAPI, PostgreSQL, Docker, Flutter/Dart, REST API"),
   ("Клиент и поставка", "Сбор требований/ТЗ, интервью, демо, коммуникация со стейкхолдерами, agile, релиз и передача"),
   ("Языки", "Арабский — родной · Английский — C2 · Русский — B2"),
   ("Локализация", "Арабский/английский RTL, ZATCA (Саудовская Аравия), мультирыночные продукты"),
   ("Также", "PyTorch, компьютерное зрение, обучение с подкреплением; руководство командами до 10"),
 ],
 "l_projects": "Ключевые проекты",
 "projects": [
   "<b>HMS — мультиарендная ERP</b> — FastAPI · PostgreSQL (RLS) · React · Docker; ZATCA Phase 1, RBAC, арабский/английский и RTL.",
   "<b>AuraGift — e-commerce</b> — JavaScript · Node.js · Firebase Cloud Functions; бессерверные заказы/платежи, деплой без простоев.",
   "<b>Цифровой двойник сортировочного центра</b> — Python · Three.js · дискретно-событийное моделирование; ~96&nbsp;400 ед./час, 530+ тестов.",
   "<b>Fracture Detection AI</b> — EfficientNet-B0 + Grad-CAM; точность 90,21%. Исследовательское ПО, не медицинское изделие.",
 ],
})


# ════════════════════════════════════════════════════════════════════════════
# BUSINESS DEVELOPMENT / ACCOUNT MANAGEMENT — the trilingual, technically fluent
# bridge that takes a software product into MENA, the Gulf and CIS markets.
# Leads with languages, client-facing delivery and market knowledge; the
# engineering background becomes "I understand and can demo what I sell".
# ════════════════════════════════════════════════════════════════════════════
BD_EN = variant(BASE_EN, {
 "pdf_title": "Mohamed Hany Reda - CV (Business Development)",
 "pdf_subject": "Technical Business Development & Account Management",
 "title": "Technical Business Development / Account Manager &nbsp;&middot;&nbsp; MENA · CIS · EN · AR · RU",
 "profile":
   "Technical business developer and account manager who bridges software products into new markets. Native "
   "Arabic, C2 English, B2 Russian — I speak directly to clients across MENA, the GCC, CIS and English-speaking "
   "markets. With a software-engineering background I understand the product, run demos, turn client needs into "
   "clear requirements, and own the relationship end to end. Ideal for teams expanding into the Arab or Russian-"
   "speaking markets. Remote worldwide; open to relocation.",
 "l_highlights": "Selected Highlights",
 "highlights": [
   "<b>Trilingual</b> — Arabic (native), English (C2), Russian (B2): sell and support directly across MENA, the "
   "GCC, CIS and English-speaking markets.",
   "<b>Engineering background</b> — I speak the product's language, run technical demos, and translate client "
   "needs into requirements engineers can build.",
   "Ran the full client lifecycle on freelance projects: discovery, requirements (SRS), proposal, delivery and handover.",
   "Deep <b>MENA/Gulf market</b> knowledge — Saudi ZATCA e-invoicing, Arabic/RTL products, regional compliance.",
   "Led teams of up to <b>10</b> and owned project budgets — comfortable with stakeholders, timelines and numbers.",
 ],
 "l_skills": "Skills",
 "skills": [
   ("Business development", "Lead qualification, discovery calls, demos, proposals, pipeline, market entry (MENA/GCC/CIS)"),
   ("Account management", "Client relationship ownership, onboarding, requirements, stakeholder communication, retention"),
   ("Technical fluency", "SaaS, APIs, full-stack products, ERP, e-commerce, AI — I understand and demo what I sell"),
   ("Languages", "Arabic — native · English — C2, full professional · Russian — B2"),
   ("Also", "Requirements/SRS, agile, localization (Arabic/English RTL, ZATCA), team leadership up to 10"),
 ],
 "exp": [
  {"role": "Technical Owner / Client-Facing Delivery &nbsp;|&nbsp; HMS", "meta": "January 2024 &mdash; Present",
   "points": ["Own the corporate web product and the relationship with internal stakeholders — gather requirements, align priorities, demo progress, deliver releases."]},
  {"role": "Product Delivery Owner &nbsp;|&nbsp; AuraGift", "meta": "January 2024 &mdash; Present",
   "points": ["Own client-facing delivery and UX of a live e-commerce product, from requirements through QA to production."]},
  {"role": "Technical Project Manager / Client Lead &nbsp;|&nbsp; Freelance", "meta": "June 2022 &mdash; Present",
   "points": ["Single point of contact between client and delivery — discovery calls, requirements (SRS), proposals and handover.",
              "Led a team of 10 on a ~$13,000 project over 11 months."]},
  {"role": "Technical Project Lead &nbsp;|&nbsp; HMS", "meta": "January 2023 &mdash; June 2023",
   "points": ["Led a team of 8 and a ~$10,000 budget; coordinated stakeholders, schedule and delivery."]},
  {"role": "Media Team Lead &nbsp;|&nbsp; Resala Charity Organization, Egypt", "meta": "January 2020 &mdash; December 2020",
   "points": ["Led the media function at one of Egypt's largest charities; completed a six-month leadership and management programme."]},
 ],
 "l_projects": "Products I Delivered (understand &amp; demo)",
 "projects": [
   "<b>HMS — Multi-Tenant ERP</b> — inventory, sales/CRM, finance; Saudi ZATCA e-invoicing and Arabic/English RTL. Built for a regional market.",
   "<b>AuraGift — Live E-Commerce</b> — a premium digital-gifting platform in production, client side and UX.",
   "<b>Fracture Detection AI</b> — a shipped AI product (90.21% accuracy) delivered as an app and a Telegram bot.",
 ],
})

BD_RU = variant(BASE_RU, {
 "pdf_title": "Мохамед Хани Реда - Резюме (Development бизнеса)",
 "pdf_subject": "Развитие бизнеса и работа с клиентами (техническое)",
 "title": "Менеджер по развитию бизнеса / аккаунт-менеджер (техн.) &nbsp;&middot;&nbsp; MENA · СНГ · EN · AR · RU",
 "profile":
   "Технический менеджер по развитию бизнеса и работе с клиентами — вывожу программные продукты на новые рынки. "
   "Арабский (родной), английский (C2), русский (B2): общаюсь напрямую с клиентами MENA, GCC, СНГ и англоязычных "
   "рынков. С инженерным бэкграундом я понимаю продукт, провожу демо, превращаю потребности клиента в чёткие "
   "требования и веду отношения от первого контакта до передачи. Идеален для команд, выходящих на арабский или "
   "русскоязычный рынок. Удалённо; готов к переезду.",
 "l_highlights": "Ключевые достижения",
 "highlights": [
   "<b>Три языка</b> — арабский (родной), английский (C2), русский (B2): продажи и поддержка напрямую на рынках MENA, GCC, СНГ и англоязычных.",
   "<b>Инженерный бэкграунд</b> — говорю на языке продукта, провожу технические демо, перевожу потребности клиента в требования для разработки.",
   "Вёл полный цикл работы с клиентом на фриланс-проектах: выявление, требования (ТЗ), предложение, поставка и передача.",
   "Глубокое знание рынка <b>MENA/Залив</b> — ZATCA (Саудовская Аравия), арабский/RTL, региональный комплаенс.",
   "Руководил командами до <b>10</b> человек и отвечал за бюджеты — уверенно работаю со стейкхолдерами, сроками и цифрами.",
 ],
 "l_skills": "Навыки",
 "skills": [
   ("Развитие бизнеса", "Квалификация лидов, discovery-звонки, демо, предложения, пайплайн, выход на рынки (MENA/GCC/СНГ)"),
   ("Работа с клиентами", "Ведение клиента, онбординг, сбор требований, коммуникация со стейкхолдерами, удержание"),
   ("Техническая база", "SaaS, API, full-stack продукты, ERP, e-commerce, AI — понимаю и демонстрирую то, что продаю"),
   ("Языки", "Арабский — родной · Английский — C2 · Русский — B2"),
   ("Также", "Требования/ТЗ, agile, локализация (арабский/английский RTL, ZATCA), руководство командами до 10"),
 ],
 "exp": [
  {"role": "Технический владелец / работа с клиентом &nbsp;|&nbsp; HMS", "meta": "Январь 2024 &mdash; настоящее время",
   "points": ["Отвечаю за корпоративный веб-продукт и отношения со стейкхолдерами — сбор требований, приоритеты, демо, релизы."]},
  {"role": "Владелец поставки продукта &nbsp;|&nbsp; AuraGift", "meta": "Январь 2024 &mdash; настоящее время",
   "points": ["Отвечаю за клиентскую поставку и UX работающего e-commerce продукта — от требований через QA до продакшена."]},
  {"role": "Technical PM / ведущий по работе с клиентом &nbsp;|&nbsp; Фриланс", "meta": "Июнь 2022 &mdash; настоящее время",
   "points": ["Единая точка контакта между клиентом и командой — discovery, требования (ТЗ), предложения и передача.",
              "Руководил командой из 10 человек на проекте ~$13&nbsp;000 в течение 11 месяцев."]},
  {"role": "Технический руководитель проекта &nbsp;|&nbsp; HMS", "meta": "Январь 2023 &mdash; июнь 2023",
   "points": ["Руководил командой из 8 человек и бюджетом ~$10&nbsp;000; координировал стейкхолдеров, сроки и поставку."]},
  {"role": "Руководитель медианаправления &nbsp;|&nbsp; Resala Charity Organization, Египет", "meta": "Январь 2020 &mdash; декабрь 2020",
   "points": ["Руководил медианаправлением в одной из крупнейших благотворительных организаций Египта; прошёл шестимесячную программу лидерства."]},
 ],
 "l_projects": "Продукты, которые я поставил (понимаю и демонстрирую)",
 "projects": [
   "<b>HMS — мультиарендная ERP</b> — склад, продажи/CRM, финансы; ZATCA и арабский/английский RTL. Под региональный рынок.",
   "<b>AuraGift — e-commerce</b> — работающая премиальная платформа цифровых подарков, клиентская часть и UX.",
   "<b>Fracture Detection AI</b> — выпущенный AI-продукт (точность 90,21%) в виде приложения и Telegram-бота.",
 ],
})


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cv")
    os.makedirs(out, exist_ok=True)
    from pypdf import PdfReader
    jobs = (
        (FS_EN, "cv_fullstack_en.pdf"), (FS_RU, "cv_fullstack_ru.pdf"),
        (AI_EN, "cv_ai_en.pdf"),        (AI_RU, "cv_ai_ru.pdf"),
        (INTL_EN, "cv_intl_en.pdf"),    (INTL_RU, "cv_intl_ru.pdf"),
        (BD_EN, "cv_bd_en.pdf"),        (BD_RU, "cv_bd_ru.pdf"),
    )
    for c, fn in jobs:
        p = build_one(c, os.path.join(out, fn))
        pages = len(PdfReader(p).pages)
        flag = "" if pages == 1 else "   <-- MORE THAN ONE PAGE"
        print("  %-24s %5.0f KB   %d page(s)%s" % (fn, os.path.getsize(p) / 1024, pages, flag))
