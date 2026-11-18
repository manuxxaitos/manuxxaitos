// Vista previa del README como en GitHub: lo pasa por la API de Markdown de GitHub (mismo saneado), le pone
// github-markdown-css y saca capturas en claro y oscuro (tools/out/vista-{claro,oscuro}.png).
// Correr: node tools/vista.mjs   (necesita gh con sesión)
import path from 'node:path';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';

const req = createRequire(path.join(process.env.HOME, '.claude/skills/teardown/node_modules/x.js'));
const {chromium} = req('playwright');
const raiz = path.resolve(import.meta.dirname, '..');
const out = path.join(raiz, 'tools/out');
const cuerpo = execFileSync('gh', ['api', '-X', 'POST', '/markdown', '--input', '-'], {
  input: JSON.stringify({text: fs.readFileSync(path.join(raiz, 'README.md'), 'utf8'), mode: 'markdown', context: 'manuxxaitos/manuxxaitos'}),
}).toString().replaceAll('https://github.com/manuxxaitos/manuxxaitos/raw/main/', '');

const pagina = (tema) => `<!doctype html><html><head><meta charset="utf-8"><base href="file://${raiz}/">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-${tema === 'claro' ? 'light' : 'dark'}.css">
<style>body{margin:0;background:${tema === 'claro' ? '#fff' : '#0d1117'}}
.caja{width:830px;margin:24px;padding:24px;border:1px solid ${tema === 'claro' ? '#d1d9e0' : '#3d444d'};border-radius:6px}</style>
</head><body><div class="caja markdown-body">${cuerpo}</div>
<script>/* lo que hace <themed-picture> en github.com: toma la versión del tema de GitHub */
if (${tema === 'oscuro'}) document.querySelectorAll('themed-picture').forEach((t) => {
  const s = t.querySelector('source'), i = t.querySelector('img');
  if (s && i) i.src = s.getAttribute('srcset');
});</script></body></html>`;

const b = await chromium.launch({executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--allow-file-access-from-files']});
for (const tema of ['claro', 'oscuro']) {
  const f = path.join(out, `vista-${tema}.html`);
  fs.writeFileSync(f, pagina(tema));
  const ctx = await b.newContext({viewport: {width: 880, height: 900}, deviceScaleFactor: 2,
    colorScheme: tema === 'claro' ? 'light' : 'dark'});
  const p = await ctx.newPage();
  await p.goto('file://' + f, {waitUntil: 'networkidle'});
  await p.waitForTimeout(1500);
  await p.screenshot({path: path.join(out, `vista-${tema}.png`), fullPage: true});
  await ctx.close();
}
await b.close();
console.log('→ tools/out/vista-claro.png, vista-oscuro.png');
