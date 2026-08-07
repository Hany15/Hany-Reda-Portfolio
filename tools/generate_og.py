#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the social share card (og:image) per language.

The previous og:image was a project screenshot branded "OZON DISTRIBUTION
CENTER" — every LinkedIn/WhatsApp share of the portfolio showed someone else's
company name instead of Mohamed's. This renders a proper 1200x630 card:
portrait, name, role and specialisation on the site's own dark palette.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = r"C:\Windows\Fonts"
OUT = os.path.join(ROOT, "assets", "img")

W, H = 1200, 630
BG = (4, 7, 15)
CYAN = (34, 211, 238)
VIOLET = (167, 139, 250)
WHITE = (255, 255, 255)
DIM = (148, 163, 184)

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def shape_ar(text):
    """Arabic needs joining + bidi reordering before PIL can draw it."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text

CARDS = {
 "en": {"role": "Technical IT Project Manager  |  Software Engineer",
        "spec": "Reinforcement Learning  ·  Digital Twins  ·  Autonomous Systems  ·  Explainable AI",
        "foot": "hany15.github.io/Hany-Reda-Portfolio", "rtl": False},
 "ru": {"role": "Технический менеджер IT-проектов  |  Инженер-программист",
        "spec": "Обучение с подкреплением  ·  Цифровые двойники  ·  Автономные системы",
        "foot": "hany15.github.io/Hany-Reda-Portfolio", "rtl": False},
 "ar": {"role": "مدير تقني لمشاريع تكنولوجيا المعلومات  |  مهندس برمجيات",
        "spec": "التعلّم المعزز · التوائم الرقمية · الأنظمة ذاتية التشغيل",
        "foot": "hany15.github.io/Hany-Reda-Portfolio", "rtl": True},
}

def build(lang, cfg):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # soft corner glows, matching the site's backdrop
    for cx, cy, rad, col in ((980, 90, 460, CYAN), (170, 560, 420, VIOLET)):
        for i in range(rad, 0, -8):
            a = int(16 * (1 - i / rad) ** 2)
            if a:
                d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col + (a,))

    # fine technical grid
    for x in range(0, W, 48):
        d.line([(x, 0), (x, H)], fill=(34, 211, 238, 10))
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=(34, 211, 238, 10))

    # accent bar
    for x in range(W):
        t = x / W
        d.line([(x, 0), (x, 6)], fill=(
            int(CYAN[0] + (VIOLET[0] - CYAN[0]) * t),
            int(CYAN[1] + (VIOLET[1] - CYAN[1]) * t),
            int(CYAN[2] + (VIOLET[2] - CYAN[2]) * t)))

    # portrait, circular, on the trailing edge
    ph = Image.open(os.path.join(OUT, "profile-640.webp")).convert("RGB").resize((330, 330), Image.LANCZOS)
    mask = Image.new("L", (330, 330), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 329, 329], fill=255)
    px = 130 if cfg["rtl"] else W - 330 - 90
    py = (H - 330) // 2
    d.ellipse([px - 7, py - 7, px + 337, py + 337], outline=CYAN + (150,), width=3)
    img.paste(ph, (px, py), mask)

    # text column
    tx = W - 90 if cfg["rtl"] else 90
    anchor_a, anchor_m = ("ra", "rm") if cfg["rtl"] else ("la", "lm")
    prep = shape_ar if cfg["rtl"] else (lambda s: s)

    d.text((tx, 176), prep("MOHAMED HANY REDA"), font=font("arialbd.ttf", 58),
           fill=WHITE, anchor=anchor_a)
    d.text((tx, 258), prep(cfg["role"]), font=font("arialbd.ttf", 25),
           fill=CYAN, anchor=anchor_a)

    # wrap the specialisation line
    words = cfg["spec"].split("  ·  ")
    f = font("arial.ttf", 20)
    line, lines = "", []
    for wd in words:
        cand = (line + "  ·  " + wd) if line else wd
        if d.textlength(prep(cand), font=f) > 640 and line:
            lines.append(line); line = wd
        else:
            line = cand
    lines.append(line)
    y = 316
    for ln in lines[:3]:
        d.text((tx, y), prep(ln), font=f, fill=DIM, anchor=anchor_a)
        y += 30

    d.text((tx, 470), prep(cfg["foot"]), font=font("arial.ttf", 19),
           fill=(125, 139, 159), anchor=anchor_a)

    path = os.path.join(OUT, "og-%s.png" % lang)
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    for lang, cfg in CARDS.items():
        p = build(lang, cfg)
        print("  %-14s %5.0f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))
