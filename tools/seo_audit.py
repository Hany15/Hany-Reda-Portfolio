#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repeatable SEO audit of the three rendered pages + the GitHub Pages files."""
import io, os, re, json, sys, html
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SITE = "https://hany15.github.io/Hany-Reda-Portfolio"
PAGES = [("index.html", "en", SITE + "/"),
         ("ru/index.html", "ru", SITE + "/ru/"),
         ("ar/index.html", "ar", SITE + "/ar/")]

fails = []
def check(ok, label, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (("  — " + str(detail)) if detail else ""))
    if not ok:
        fails.append(label)

for path, lang, url in PAGES:
    h = io.open(path, encoding="utf-8").read()
    body = h.split("<body>", 1)[1]
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
    print("\n=== %s  (%s) ===" % (path, lang))

    # crawlable content
    check(len(text) > 6000, "substantial crawlable text", "%s chars" % f"{len(text):,}")
    check(len(re.findall(r'data-i18n="[^"]+"></', h)) == 0, "no empty i18n placeholders")
    check(h.count('alt=""') == 0, "no empty alt attributes")

    # title / description
    title = re.search(r"<title>(.*?)</title>", h, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    check(10 <= len(title) <= 65, "title length 10-65", "%d chars" % len(title))
    check(70 <= len(desc) <= 320, "description length", "%d chars" % len(desc))

    # canonical + hreflang reciprocity
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)
    check(canon == url, "canonical is self-referential", canon)
    hl = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h))
    check(set(hl) == {"en", "ru", "ar", "x-default"}, "hreflang covers all + x-default", sorted(hl))
    check(hl.get("x-default") == SITE + "/", "x-default points to root")
    check(all(hl.get(l) == SITE + "/" + ("" if l == "en" else l + "/") for l in ("en", "ru", "ar")),
          "hreflang URLs correct")

    # document language
    m = re.search(r'<html lang="([^"]+)" dir="([^"]+)"', h)
    check(m.group(1) == lang, "html lang", m.group(1))
    check(m.group(2) == ("rtl" if lang == "ar" else "ltr"), "html dir", m.group(2))

    # open graph / twitter
    og = dict(re.findall(r'<meta property="(og:[^"]+)" content="([^"]*)"', h))
    check(og.get("og:url") == url, "og:url matches page")
    check(og.get("og:locale") == {"en": "en_US", "ru": "ru_RU", "ar": "ar_SA"}[lang], "og:locale")
    check(bool(og.get("og:image", "").startswith("https://")), "og:image absolute")
    tw = dict(re.findall(r'<meta name="(twitter:[^"]+)" content="([^"]*)"', h))
    check(tw.get("twitter:card") == "summary_large_image", "twitter card")

    # structured data
    ld = json.loads(re.search(r'id="jsonld">(.*?)</script>', h, re.S).group(1))
    types = [o["@type"] for o in ld]
    check(set(types) == {"Person", "WebSite", "ProfilePage"}, "JSON-LD types", types)
    person = ld[0]
    check(bool(person.get("jobTitle")) and bool(person.get("knowsAbout")), "Person has jobTitle + knowsAbout")

    # headings
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    check(len(h1) == 1, "exactly one H1", len(h1))
    check(len(re.findall(r"<h2[^>]*>", h)) >= 5, "multiple H2 sections")

    # links / assets resolve on disk
    base = os.path.dirname(path)
    refs = set()
    for mm in re.finditer(r'(?:href|src)="((?:\.\./)?(?:assets|cv)/[^"?]+)', h):
        refs.add(os.path.normpath(os.path.join(base, mm.group(1))))
    missing = [r for r in refs if not os.path.exists(r)]
    check(not missing, "local assets resolve", missing[:3] or "%d refs" % len(refs))

# ── site-level files ──────────────────────────────────────────────────────
print("\n=== site files ===")
for f in ("robots.txt", "sitemap.xml", "404.html", ".nojekyll"):
    check(os.path.exists(f), "%s exists" % f)

robots = io.open("robots.txt", encoding="utf-8").read()
check("Sitemap:" in robots, "robots references sitemap")
check("Disallow: /assets" not in robots, "robots does not block CSS/JS")

sm = io.open("sitemap.xml", encoding="utf-8").read()
check(sm.count("<loc>") == 3, "sitemap lists 3 URLs", sm.count("<loc>"))
check(sm.count("xhtml:link") == 12, "sitemap hreflang alternates", sm.count("xhtml:link"))
try:
    import xml.etree.ElementTree as ET
    ET.fromstring(sm); check(True, "sitemap is well-formed XML")
except Exception as e:
    check(False, "sitemap is well-formed XML", e)

check('name="robots" content="noindex"' in io.open("404.html", encoding="utf-8").read(),
      "404 page is noindex")

print("\n" + ("ALL SEO CHECKS PASSED" if not fails else "FAILED: %d — %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
