// Graba tomascardozo.com en tiempo real, en dos tomas: la entrada (palabra por palabra) y una tarjeta de proyecto que
// abre su ventana con el efecto genio. Captura con Page.captureScreenshot en bucle (no rompe cuadros como el screencast)
// y ffmpeg pega cada cuadro con su duración real. Salida: tools/out/portfolio.mp4.
// Correr: node tools/grabar-portfolio.mjs [slug-del-proyecto]
import path from 'node:path';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';

const req = createRequire(path.join(process.env.HOME, '.claude/skills/teardown/node_modules/x.js'));
const {chromium} = req('playwright');
const proyecto = process.argv[2] || 'kench';
const W = 960, H = 600;
const out = path.join(import.meta.dirname, 'out');
const URL = 'https://tomascardozo.com/';

const b = await chromium.launch({executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--use-angle=metal']});

/** graba mientras corre accion(p); devuelve la carpeta con cuadros y lista.txt */
async function toma(nombre, preparar, accion) {
  const dir = path.join(out, 'toma-' + nombre);
  fs.rmSync(dir, {recursive: true, force: true});
  fs.mkdirSync(dir, {recursive: true});
  const ctx = await b.newContext({viewport: {width: W, height: H}, deviceScaleFactor: 1.5});
  const p = await ctx.newPage();
  await preparar(p);
  const cdp = await ctx.newCDPSession(p);
  const cuadros = [];
  let grabando = true;
  const bucle = (async () => {
    while (grabando) {
      const t = Date.now();
      const {data} = await cdp.send('Page.captureScreenshot', {format: 'jpeg', quality: 90});
      const f = String(cuadros.length).padStart(5, '0') + '.jpg';
      fs.writeFileSync(path.join(dir, f), Buffer.from(data, 'base64'));
      cuadros.push({f, t});
    }
  })();
  await accion(p);
  grabando = false;
  await bucle;
  await ctx.close();
  let txt = '';
  cuadros.forEach((c, i) => {
    const d = ((cuadros[i + 1]?.t ?? c.t + 33) - c.t) / 1000;
    txt += `file '${c.f}'\nduration ${d.toFixed(4)}\n`;
  });
  txt += `file '${cuadros.at(-1).f}'\n`;
  fs.writeFileSync(path.join(dir, 'lista.txt'), txt);
  const seg = (cuadros.at(-1).t - cuadros[0].t) / 1000;
  console.log(nombre, cuadros.length, 'cuadros,', (cuadros.length / seg).toFixed(1), 'fps');
  return dir;
}

const a = await toma('entrada', async (p) => {
  await p.goto(URL, {waitUntil: 'domcontentloaded'});
}, async (p) => {
  await p.mouse.move(W * 0.62, H * 0.6);
  await p.waitForTimeout(6000);
});

const tarjeta = `[data-open="${proyecto}"]`;
const c = await toma('ventana', async (p) => {
  await p.goto(URL + '#', {waitUntil: 'networkidle'});
  await p.keyboard.press('Space'); // adelanta la entrada
  await p.waitForTimeout(1500);
  await p.locator(tarjeta).first().evaluate((el) => el.scrollIntoView({block: 'center'}));
  await p.waitForTimeout(2500);
  await p.mouse.move(W * 0.2, H * 0.9);
}, async (p) => {
  const caja = await p.locator(tarjeta).first().boundingBox();
  await p.waitForTimeout(400);
  await p.mouse.move(caja.x + caja.width * 0.5, caja.y + caja.height * 0.45, {steps: 30});
  await p.waitForTimeout(1300);
  await p.mouse.down();
  await p.mouse.up();
  await p.waitForTimeout(4200);
});
await b.close();

const salida = path.join(out, 'portfolio.mp4');
const vf = `fps=30,scale=${W * 1.5}:${H * 1.5},setsar=1`;
execFileSync('ffmpeg', ['-y', '-v', 'error',
  '-f', 'concat', '-safe', '0', '-i', path.join(a, 'lista.txt'),
  '-f', 'concat', '-safe', '0', '-i', path.join(c, 'lista.txt'),
  '-filter_complex', `[0]${vf}[a];[1]${vf}[c];[a][c]xfade=transition=fade:duration=0.5:offset=5.4,format=yuv420p`,
  '-c:v', 'libx264', '-crf', '15', salida]);
console.log('→', salida);
