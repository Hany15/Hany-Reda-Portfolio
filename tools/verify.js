/* Repeatable i18n + link integrity check.  Run:  node verify.js  */
const fs = require('fs');
const path = require('path');
process.chdir(path.join(__dirname, '..'));   // run against the repo root
global.window = {};
require('../assets/js/i18n.js');
const I = window.I18N, LANGS = ['en', 'ru', 'ar'];
const html = fs.readFileSync('index.html', 'utf8');
const mainjs = fs.readFileSync('assets/js/main.js', 'utf8');

let fail = 0;
const bad = (m) => { console.log('  ✗ ' + m); fail++; };

/* 1 ─ every language defines the same key set */
const all = new Set(LANGS.flatMap(l => Object.keys(I[l])));
console.log('\n[1] key parity');
for (const k of all) {
  const missing = LANGS.filter(l => !(k in I[l]));
  if (missing.length) bad(`"${k}" missing in: ${missing.join(', ')}`);
}
LANGS.forEach(l => console.log(`  ${l}: ${Object.keys(I[l]).length} keys`));

/* 2 ─ no empty / placeholder values */
console.log('[2] value sanity');
LANGS.forEach(l => Object.entries(I[l]).forEach(([k, v]) => {
  if (typeof v !== 'string' || !v.trim()) bad(`${l}:${k} is empty`);
  if (/\b(TODO|FIXME|Coming soon|Translate this|undefined|null)\b/i.test(v)) bad(`${l}:${k} placeholder: ${v}`);
}));

/* 3 ─ every key the markup references resolves */
console.log('[3] markup references');
const used = new Set();
for (const m of html.matchAll(/data-i18n="([^"]+)"/g)) used.add(m[1]);
for (const m of html.matchAll(/data-i18n-attr="([^"]+)"/g))
  m[1].split('|').forEach(p => { const i = p.indexOf(':'); if (i > 0) used.add(p.slice(i + 1).trim()); });

/* 4 ─ every key the modal builds at runtime resolves (derived from PROJECTS) */
console.log('[4] runtime modal references');
const PROJECTS = eval(mainjs.match(/var PROJECTS = (\[[\s\S]*?\n  \]);/)[1]
  .replace(/var\(--[a-z]+\)/g, '"x"'));
PROJECTS.forEach(p => {
  ['kicker', 'title', 'desc', 'problem', 'approach', 'arch', 'challenges'].forEach(f => used.add(p.id + '.' + f));
  for (let i = 1; i <= p.highlights; i++) used.add(p.id + '.h' + i);
  p.shots.forEach((_, i) => used.add(p.id + (i === 0 ? '.alt' : '.alt2')));
  (p.metrics || []).forEach(m => used.add(m[1]));
  if (p.disclaimer) used.add(p.disclaimer);
});
['projects.close','projects.overview','projects.problem','projects.approach','projects.architecture',
 'projects.results','projects.challenges','projects.tech','projects.github','projects.screenshot',
 'meta.title','meta.desc','role.full','nav.menu','nav.close'].forEach(k => used.add(k));

for (const k of [...used].sort()) {
  const missing = LANGS.filter(l => !(k in I[l]));
  if (missing.length) bad(`referenced key "${k}" missing in: ${missing.join(', ')}`);
}
const unused = Object.keys(I.en).filter(k => !used.has(k));
if (unused.length) bad(`defined but never rendered: ${unused.join(', ')}`);
console.log(`  ${used.size} keys referenced`);

/* 5 ─ referenced images exist on disk */
console.log('[5] image assets');
const imgs = new Set();
for (const m of html.matchAll(/(?:src|srcset)="([^"]+)"/g))
  m[1].split(',').forEach(s => {
    const u = s.trim().split(' ')[0].split('?')[0];   // drop cache-bust query
    if (u.startsWith('assets/')) imgs.add(u);
  });
PROJECTS.forEach(p => {
  p.shots.forEach(s => imgs.add('assets/img/projects/' + s + (p.svg ? '.svg' : '-1200.webp')));
  imgs.add('assets/img/projects/' + p.img + (p.svg ? '.svg' : '-1200.webp'));
});
imgs.forEach(f => { if (!fs.existsSync(f)) bad(`missing asset: ${f}`); });
console.log(`  ${imgs.size} assets referenced, all present`);

/* 6 ─ external links are well-formed and non-duplicated per project */
console.log('[6] links');
const urls = [...html.matchAll(/href="(https?:\/\/[^"]+)"/g)].map(m => m[1]);
urls.forEach(u => { if (!/^https:\/\//.test(u)) bad(`non-https link: ${u}`); });
const repoUrls = urls.filter(u => u.includes('github.com/Hany15/'));
console.log(`  ${urls.length} external links, ${new Set(repoUrls).size} distinct repos`);

console.log(fail ? `\nFAILED — ${fail} problem(s)\n` : '\nAll checks passed.\n');
process.exit(fail ? 1 : 0);
