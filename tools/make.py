#!/usr/bin/env python3
"""Full site build:  template -> three pre-rendered language pages + SEO files.

    python tools/make.py
"""
import subprocess, sys, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

def run(label, cmd):
    print(label)
    subprocess.run(cmd, check=True)

run("1/3  build   - generate the template", [sys.executable, os.path.join(HERE, "build.py")])
shutil.copy("index.html", ".template.html")

run("2/3  render  - en / ru / ar + sitemap, robots, 404",
    [sys.executable, os.path.join(HERE, "render.py")])

print("3/3  verify  - integrity + SEO checks")
try:
    subprocess.run(["node", os.path.join(HERE, "verify.js")], check=True)
except FileNotFoundError:
    print("     (node not found - skipping verify.js)")
subprocess.run([sys.executable, os.path.join(HERE, "seo_audit.py")], check=True)

if os.path.exists(".template.html"):
    os.remove(".template.html")
print("\nBuild complete.")
