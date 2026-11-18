#!/usr/bin/env python3
"""Genera las piezas SVG del README: una pastilla por herramienta (ícono + nombre) y los íconos de redes del encabezado,
cada una en versión clara y oscura (assets/tools/<slug>-{claro,oscuro}.svg, assets/redes/...). Después arma README.md.

El texto va convertido a trazos con Inter (la del portfolio), así se ve igual en cualquier máquina: GitHub muestra los SVG
como imágenes y no les carga fuentes. Los íconos salen de simple-icons (npm pack simple-icons, carpeta en SI).
Correr: python3 tools/pastillas.py
"""
import os, re, json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

RAIZ = Path(__file__).resolve().parent.parent
INTER = RAIZ.parent / 'portfolio-2026/public/fonts/inter-var.woff2'
SI = Path(os.environ.get('SI', '/private/tmp/claude-501/-Users-tomascardozo-main-02-Personal/42dd4297-d312-44df-968e-fe93dca8ef2d/scratchpad/si/package/icons'))

# ── las herramientas, como en «Con qué trabajo» del portfolio ─────────────────────────────────────────────────────────
# (nombre, ícono de simple-icons | ('letras', 'Ae', fondo, tinta) | None, color del ícono o None = el de la marca)
FILAS = [
    ('diseño y motion', [
        ('Figma', 'figma', None),
        ('After Effects', ('letras', 'Ae', '#00005B', '#9999FF'), None),
        ('Premiere', ('letras', 'Pr', '#00005B', '#EA77FF'), None),
    ]),
    ('web', [
        ('HTML', 'html5', None), ('CSS', 'css', None), ('JavaScript', 'javascript', None), ('TypeScript', 'typescript', None),
        ('Three.js', 'threedotjs', None), ('GSAP', 'gsap', None), ('Astro', 'astro', None), ('React', 'react', None),
        ('FastAPI', 'fastapi', None), ('SQLite', 'sqlite', None),
    ]),
    ('ia y automatización', [
        ('Claude Code', 'claude', None), ('API de Anthropic', 'anthropic', None), ('Codex', None, None),
        ('Whisper', None, None), ('Python', 'python', None), ('ffmpeg', 'ffmpeg', None), ('OpenCV', 'opencv', None),
        ('Playwright', None, None),
    ]),
]

TEMAS = {
    'claro': dict(fondo='#f6f8fa', borde='#d1d9e0', texto='#1f2328', apagado='#59636e'),
    'oscuro': dict(fondo='#151b23', borde='#3d444d', texto='#d1d7e0', apagado='#9198a1'),
}

# ── texto a trazos ────────────────────────────────────────────────────────────────────────────────────────────────────
_fuentes = {}
def fuente(peso):
    if peso not in _fuentes:
        f = TTFont(str(INTER))
        _fuentes[peso] = instantiateVariableFont(f, {'wght': peso, 'opsz': 14})
    return _fuentes[peso]

def texto(s, tam, x, y, peso=500, track=0.0):
    """devuelve (d del path, ancho) con la línea base en y"""
    f = fuente(peso)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    esc = tam / f['head'].unitsPerEm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x + cx, y)))
        cx += hmtx[g][0] * esc + track
    return pen.getCommands(), cx - track

def icono(slug):
    svg = (SI / f'{slug}.svg').read_text()
    d = re.search(r' d="([^"]+)"', svg).group(1)
    meta = json.loads((SI.parent / 'data/simple-icons.json').read_text()) if False else None
    return d

_colores = None
def color_marca(slug):
    global _colores
    if _colores is None:
        datos = json.loads((SI.parent / 'data/simple-icons.json').read_text())
        datos = datos.get('icons', datos) if isinstance(datos, dict) else datos
        _colores = {}
        for i in datos:
            s = i.get('slug') or re.sub(r'[^a-z0-9]', '', i['title'].lower().replace('+', 'plus').replace('.', 'dot').replace('&', 'and'))
            _colores[s] = '#' + i['hex']
    return _colores.get(slug, '#888888')

def luz(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contraste(a, b):
    la, lb = sorted((luz(a), luz(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

# ── una pastilla ──────────────────────────────────────────────────────────────────────────────────────────────────────
ALTO, TAM, ICO, PAD, GAP = 26, 12.5, 14, 9, 6

def pastilla(nombre, ico, tema):
    T = TEMAS[tema]
    x0 = PAD
    partes = []
    if isinstance(ico, tuple):  # cuadradito con letras, como los de Adobe
        _, letras, fondo, tinta = ico
        d, w = texto(letras, 7.6, 0, 0, peso=700)
        partes.append(f'<rect x="{x0}" y="{(ALTO - ICO) / 2}" width="{ICO}" height="{ICO}" rx="3" fill="{fondo}"/>')
        partes.append(f'<path transform="translate({x0 + (ICO - w) / 2:.2f} {ALTO / 2 + 2.8:.2f})" d="{d}" fill="{tinta}"/>')
        x = x0 + ICO + GAP
    elif ico:
        c = color_marca(ico)
        if contraste(c, T['fondo']) < 2.2:  # marcas negras en oscuro o claras en claro
            c = T['texto']
        s = ICO / 24
        partes.append(f'<path transform="translate({x0} {(ALTO - ICO) / 2}) scale({s:.4f})" d="{icono(ico)}" fill="{c}"/>')
        x = x0 + ICO + GAP
    else:  # sin ícono: un puntito
        partes.append(f'<circle cx="{x0 + 3}" cy="{ALTO / 2}" r="3" fill="{T["apagado"]}"/>')
        x = x0 + 6 + GAP
    d, w = texto(nombre, TAM, x, ALTO / 2 + TAM * 0.36)
    partes.append(f'<path d="{d}" fill="{T["texto"]}"/>')
    ancho = round(x + w + PAD)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{ALTO}" viewBox="0 0 {ancho} {ALTO}">'
            f'<title>{nombre}</title>'
            f'<rect x=".5" y=".5" width="{ancho - 1}" height="{ALTO - 1}" rx="6" fill="{T["fondo"]}" stroke="{T["borde"]}"/>'
            + ''.join(partes) + '</svg>'), ancho

def red(slug, tema, tam=26, color=None):
    T = TEMAS[tema]
    c = color or color_marca(slug)
    if contraste(c, '#ffffff' if tema == 'claro' else '#0d1117') < 2.2:
        c = T['texto']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tam}" height="{tam}" viewBox="0 0 24 24">'
            f'<title>{slug}</title><path d="{icono(slug)}" fill="{c}"/></svg>')

SOBRE = 'M1.5 4.5h21v15h-21zM1.5 5.5l10.5 8 10.5-8'  # sobre de mail, en trazo
def mail(tema, tam=26):
    T = TEMAS[tema]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tam}" height="{tam}" viewBox="0 0 24 24"><title>mail</title>'
            f'<path d="{SOBRE}" fill="none" stroke="{T["texto"]}" stroke-width="1.8" stroke-linejoin="round"/></svg>')

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o')).strip('-')

def picture(base, alt, extra=''):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}-oscuro.svg">'
            f'<img src="{base}-claro.svg" alt="{alt}"{extra}></picture>')

if __name__ == '__main__':
    (RAIZ / 'assets/tools').mkdir(parents=True, exist_ok=True)
    (RAIZ / 'assets/redes').mkdir(parents=True, exist_ok=True)
    filas_md = []
    for titulo, items in FILAS:
        chips = []
        for nombre, ico, _ in items:
            slug = slugify(nombre)
            for tema in TEMAS:
                svg, _w = pastilla(nombre, ico, tema)
                (RAIZ / f'assets/tools/{slug}-{tema}.svg').write_text(svg)
            chips.append((f'assets/tools/{slug}', nombre))
        filas_md.append((titulo, chips))
    # GitHub saca el <img> del <picture> cuando el <picture> va dentro de un link: las redes van en un gris que se lee
    # en los dos temas, y Behance en su azul
    GRIS = '#848d97'
    (RAIZ / 'assets/redes/behance.svg').write_text(red('behance', 'claro'))
    (RAIZ / 'assets/redes/x.svg').write_text(red('x', 'claro', color=GRIS).replace(f'fill="{TEMAS["claro"]["texto"]}"', f'fill="{GRIS}"'))
    (RAIZ / 'assets/redes/mail.svg').write_text(mail('claro').replace(TEMAS['claro']['texto'], GRIS))
    json.dump(filas_md, open(RAIZ / 'tools/out/filas.json', 'w'), ensure_ascii=False, indent=1)
    print('pastillas:', sum(len(c) for _, c in filas_md))
