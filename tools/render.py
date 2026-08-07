#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-renders the build.py template into three fully static, crawlable pages:

    /            English   (canonical root, x-default)
    /ru/         Russian
    /ar/         Arabic  (dir=rtl)

Why: the runtime i18n left every heading and paragraph empty in the HTML source,
so a crawler saw ~1.3 KB of tag soup and no prose, and the RU/AR content had no
URL of its own to rank on. Each page now ships its real text, its own
title/description/OG, reciprocal hreflang alternates, and real JSON-LD.

Also emits robots.txt, sitemap.xml, 404.html and .nojekyll for GitHub Pages.
"""
import io, os, re, json, html, datetime

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE   = "https://hany15.github.io/Hany-Reda-Portfolio"
LANGS  = ["en", "ru", "ar"]
RTL    = {"ar"}
OG_LOC = {"en": "en_US", "ru": "ru_RU", "ar": "ar_SA"}
# hreflang wants a language (optionally region) code; keep them bare + x-default
SUBDIR = {"en": "", "ru": "ru/", "ar": "ar/"}


# ── read the translation dictionary straight out of the JS source ──────────
def load_i18n():
    src = io.open(os.path.join(ROOT, "assets/js/i18n.js"), encoding="utf-8").read()
    body = src.split("window.I18N =", 1)[1].rsplit("};", 1)[0] + "}"
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)          # block comments
    body = re.sub(r"^\s*//.*$", "", body, flags=re.M)          # line comments
    body = re.sub(r",(\s*[}\]])", r"\1", body)                 # trailing commas
    body = re.sub(r"^\s*(en|ru|ar):", lambda m: '"%s":' % m.group(1), body, flags=re.M)
    return json.loads(body)


def esc(s):
    """Escape for HTML text/attribute, without double-escaping existing entities."""
    return html.escape(html.unescape(s), quote=True)


def render(tpl, lang, tr):
    t = lambda k: tr[lang].get(k, tr["en"].get(k, k))
    prefix = "" if lang == "en" else "../"
    page_url = SITE + "/" + SUBDIR[lang]
    doc = tpl

    # ── text nodes.  Most data-i18n elements are empty pairs in the template,
    #    but a few (e.g. the skip link) carry English fallback text — match both,
    #    as long as the content holds no nested markup.
    def fill(m):
        open_tag, tag, key = m.group(1), m.group(2), m.group(3)
        return "%s%s</%s>" % (open_tag, esc(t(key)), tag)
    doc, n_text = re.subn(r'(<(\w+)[^>]*\bdata-i18n="([^"]+)"[^>]*>)[^<]*</\2>', fill, doc)

    # ── attributes: data-i18n-attr="alt:key|aria-label:key"
    def fill_attr(m):
        tag = m.group(0)
        for pair in m.group(1).split("|"):
            if ":" not in pair:
                continue
            attr, key = pair.split(":", 1)
            attr, val = attr.strip(), esc(t(key.strip()))
            if re.search(r'\b%s="' % re.escape(attr), tag):
                tag = re.sub(r'\b%s="[^"]*"' % re.escape(attr), '%s="%s"' % (attr, val), tag, count=1)
            else:
                tag = tag[:-1] + ' %s="%s">' % (attr, val)
        return tag
    doc, n_attr = re.subn(r'<[^>]*\bdata-i18n-attr="([^"]+)"[^>]*>', fill_attr, doc)

    # ── document language / direction
    # data-asset-base lets runtime-built markup (the project modal) resolve
    # asset URLs correctly from /ru/ and /ar/ as well as from the root.
    doc = doc.replace('<html lang="en" dir="ltr">',
                      '<html lang="%s" dir="%s" data-asset-base="%s">'
                      % (lang, "rtl" if lang in RTL else "ltr", prefix), 1)

    # ── head: title, description, canonical, OG/Twitter, hreflang
    title, desc = esc(t("meta.title")), esc(t("meta.desc"))
    doc = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, doc, count=1, flags=re.S)
    doc = re.sub(r'(<meta name="description" content=")[^"]*(">)', r"\g<1>%s\g<2>" % desc, doc, count=1)
    doc = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', r"\g<1>%s\g<2>" % page_url, doc, count=1)
    doc = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', r"\g<1>%s\g<2>" % page_url, doc, count=1)
    doc = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', r"\g<1>%s\g<2>" % title, doc, count=1)
    doc = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', r"\g<1>%s\g<2>" % desc, doc, count=1)
    doc = re.sub(r'(<meta property="og:locale" content=")[^"]*(">)', r"\g<1>%s\g<2>" % OG_LOC[lang], doc, count=1)
    doc = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)', r"\g<1>%s\g<2>" % title, doc, count=1)
    doc = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)', r"\g<1>%s\g<2>" % desc, doc, count=1)

    # og:image — a branded card per language, not a project screenshot
    card = SITE + "/assets/img/og-%s.png" % lang
    doc = re.sub(r'(<meta property="og:image" content=")[^"]*(">)', r"\g<1>%s\g<2>" % card, doc, count=1)
    doc = re.sub(r'(<meta name="twitter:image" content=")[^"]*(">)', r"\g<1>%s\g<2>" % card, doc, count=1)
    doc = doc.replace(
        '<meta property="og:image" content="%s">' % card,
        '\n'.join([
            '<meta property="og:image" content="%s">' % card,
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="%s">' % esc(t("photo.alt")),
        ]), 1)

    alts = "".join(
        '<link rel="alternate" hreflang="%s" href="%s/%s">\n' % (l, SITE, SUBDIR[l]) for l in LANGS
    ) + '<link rel="alternate" hreflang="x-default" href="%s/">\n' % SITE
    og_alt = "".join(
        '<meta property="og:locale:alternate" content="%s">\n' % OG_LOC[l] for l in LANGS if l != lang
    )
    doc = doc.replace('<meta property="og:type" content="website">',
                      alts + og_alt + '<meta property="og:type" content="website">', 1)

    # ── real structured data in the source (was an empty {} filled by JS)
    ld = [
      {"@context": "https://schema.org", "@type": "Person",
       "@id": SITE + "/#person",
       "name": "Mohamed Hany Reda",
       "alternateName": ["Мохамед Хани Реда", "محمد هاني رضا"],
       "jobTitle": t("role.full"),
       "description": t("meta.desc"),
       "url": page_url,
       "image": SITE + "/assets/img/profile-640.webp",
       "email": "mailto:developeractionobject@gmail.com",
       "alumniOf": {"@type": "CollegeOrUniversity",
                    "name": "Tomsk State University of Control Systems and Radioelectronics (TUSUR)"},
       "knowsLanguage": [
           {"@type": "Language", "name": "Arabic"},
           {"@type": "Language", "name": "English"},
           {"@type": "Language", "name": "Russian"}],
       "knowsAbout": ["Reinforcement Learning", "Digital Twins", "Discrete-Event Simulation",
                      "Autonomous Systems", "Explainable AI", "Computer Vision",
                      "Software Architecture", "Technical Project Management",
                      "Multi-Agent Systems", "PyTorch", "FastAPI", "PostgreSQL"],
       "telephone": "+79969382354",
       "contactPoint": [
           {"@type": "ContactPoint", "contactType": "sales",
            "telephone": "+79969382354", "url": "https://wa.me/79969382354",
            "availableLanguage": ["Arabic", "English", "Russian"]},
           {"@type": "ContactPoint", "contactType": "customer support",
            "url": "https://t.me/Hany_230",
            "availableLanguage": ["Arabic", "English", "Russian"]}],
       "sameAs": ["https://github.com/Hany15",
                  "https://www.linkedin.com/in/hany-reda-854667417",
                  "https://t.me/Hany_230"]},
      {"@context": "https://schema.org", "@type": "WebSite",
       "@id": SITE + "/#website", "url": SITE + "/",
       "name": t("meta.title"), "description": t("meta.desc"),
       "inLanguage": lang,
       "author": {"@id": SITE + "/#person"}},
      {"@context": "https://schema.org", "@type": "ProfilePage",
       "@id": page_url + "#profile", "url": page_url,
       "inLanguage": lang, "mainEntity": {"@id": SITE + "/#person"},
       "isPartOf": {"@id": SITE + "/#website"}},
    ]
    doc = re.sub(r'(<script type="application/ld\+json" id="jsonld">).*?(</script>)',
                 lambda m: m.group(1) + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + m.group(2),
                 doc, count=1, flags=re.S)

    # ── counters: ship the final value in the HTML (JS animates from 0 on
    #    scroll; with JS off the correct number simply stays on screen)
    def fill_count(m):
        head, raw, suffix = m.group(1), m.group(2), m.group(3)
        try:
            v = float(raw)
            txt = ("{:,.2f}".format(v) if "." in raw else "{:,.0f}".format(v))
        except ValueError:
            txt = raw
        return "%s%s%s</span>" % (head, txt, esc(suffix))
    doc = re.sub(r'(<span class="stat-num"[^>]*data-count="([\d.]+)"[^>]*data-suffix="([^"]*)"[^>]*>)0</span>',
                 fill_count, doc)

    # ── rewrite relative asset paths for the /ru/ and /ar/ subdirectories
    if prefix:
        doc = re.sub(r'((?:href|src|srcset)=")(assets/|cv/)', r"\1%s\2" % prefix, doc)
        doc = re.sub(r'(srcset="[^"]*?, )(assets/)', r"\1%s\2" % prefix, doc)

    # ── language switcher: real links between the three URLs (crawlable)
    def switcher(m):
        rel = {}
        for l in LANGS:
            if l == lang:
                rel[l] = "./"
            elif lang == "en":
                rel[l] = SUBDIR[l]            # root  -> ru/ , ar/
            elif l == "en":
                rel[l] = "../"                # /ru/  -> /
            else:
                rel[l] = "../" + SUBDIR[l]    # /ru/  -> ../ar/
        out = [
            '<a class="lang-btn" href="%s" hreflang="%s" data-lang="%s" aria-pressed="%s"%s>%s</a>'
            % (rel[l], l, l, "true" if l == lang else "false",
               ' aria-current="page"' if l == lang else "", l.upper())
            for l in LANGS
        ]
        sep = "\n        "
        return m.group(1) + sep + sep.join(out) + "\n      " + m.group(3)

    doc = re.sub(r'(<div class="lang-switch"[^>]*>)(.*?)(</div>)', switcher, doc, count=1, flags=re.S)

    return doc, n_text, n_attr


def main():
    tr  = load_i18n()
    tpl = io.open(os.path.join(ROOT, ".template.html"), encoding="utf-8").read()

    for lang in LANGS:
        doc, n_text, n_attr = render(tpl, lang, tr)
        out_dir = ROOT if lang == "en" else os.path.join(ROOT, lang)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "index.html")
        io.open(path, "w", encoding="utf-8", newline="\n").write(doc)
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        print("  %-16s %6.1f KB   %3d text nodes, %2d attrs filled" %
              (rel, len(doc.encode()) / 1024, n_text, n_attr))

    today = datetime.date.today().isoformat()
    # ── sitemap with reciprocal hreflang alternates ────────────────────────
    urls = []
    for lang in LANGS:
        alts = "".join(
            '\n    <xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>' % (l, SITE, SUBDIR[l])
            for l in LANGS)
        alts += '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>' % SITE
        urls.append(
            "  <url>\n    <loc>%s/%s</loc>\n    <lastmod>%s</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n    <priority>%s</priority>%s\n  </url>"
            % (SITE, SUBDIR[lang], today, "1.0" if lang == "en" else "0.9", alts))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
               '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sitemap)

    # Never disallow CSS/JS — Google fetches them to confirm the page renders,
    # and blocking them raises "blocked resource" warnings in Search Console.
    robots = ("User-agent: *\n"
              "Allow: /\n\n"
              "Sitemap: %s/sitemap.xml\n" % SITE)
    io.open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(robots)

    # GitHub Pages serves 404.html for unknown paths; keep the visitor on-site.
    nf = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8">\n'
          '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
          '<meta name="robots" content="noindex">\n<title>Page not found | Mohamed Hany Reda</title>\n'
          '<link rel="stylesheet" href="/Hany-Reda-Portfolio/assets/css/main.css">\n</head>\n'
          '<body><main id="main" style="min-height:80svh;display:flex;flex-direction:column;'
          'align-items:center;justify-content:center;text-align:center;gap:18px;padding:40px 20px">\n'
          '<h1 style="font-family:var(--display);font-size:clamp(1.4rem,5vw,2.4rem)">404</h1>\n'
          '<p style="color:var(--dim)">That page does not exist.</p>\n'
          '<a class="btn btn-primary" href="/Hany-Reda-Portfolio/">Back to the portfolio</a>\n'
          '</main></body></html>\n')
    io.open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8", newline="\n").write(nf)

    # tell GitHub Pages to serve the tree as-is (no Jekyll processing)
    io.open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8").write("")

    print("  sitemap.xml, robots.txt, 404.html, .nojekyll written")


if __name__ == "__main__":
    main()
