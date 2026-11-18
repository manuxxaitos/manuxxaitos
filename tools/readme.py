#!/usr/bin/env python3
"""Arma README.md: una caja con el saludo y las redes, la grilla de cuatro loops y las herramientas en filas.
Lee tools/out/filas.json (sale de tools/pastillas.py). Correr: python3 tools/pastillas.py && python3 tools/readme.py

Las <source> de <picture> van con URL absoluta al repo (GitHub no siempre resuelve las relativas en srcset);
los <img> van relativos. Para verlo antes de subir: tools/vista.py.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CRUDO = 'https://github.com/manuxxaitos/manuxxaitos/raw/main/'
SITIO = 'https://tomascardozo.com'

GRILLA = [  # (archivo, link, alt)
    ('portfolio', SITIO, 'Mi portfolio: la entrada palabra por palabra y la ventana de Kench que se abre'),
    ('ukiyo', SITIO + '/sandbox/ukiyo/', 'Kaze no tayori: una carta que lleva el viento por cinco grabados ukiyo-e vivos'),
    ('kora', SITIO + '/sandbox/kora/', 'Kora frente al Fuji: diorama 3D en vivo, impreso en ASCII'),
    ('itapiru', SITIO + '/sandbox/lopez-itapiru/', 'Llegada a Itapirú: un óleo de Cándido López pintado de nuevo por código'),
]
REDES = [  # (archivo, link, alt) — van flotando a la derecha, así que en orden inverso
    ('mail', 'mailto:tomascardozo98@gmail.com', 'Mail'),
    ('x', 'https://x.com/tomascardozo98', 'X'),
    ('behance', 'https://www.behance.net/tomasecardozo', 'Behance'),
]

def picture(base, alt, extra=''):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{CRUDO}{base}-oscuro.svg">'
            f'<img src="{base}-claro.svg" alt="{alt}"{extra}></picture>')

filas = json.loads((RAIZ / 'tools/out/filas.json').read_text())
redes = '\n'.join(f'<a href="{href}"><img src="assets/redes/{f}.svg" alt="{alt}" height="26" align="right" hspace="6"></a>'
                  for f, href, alt in REDES)
grilla = []
for i, (f, href, alt) in enumerate(GRILLA):
    grilla.append(f'<a href="{href}"><img src="assets/{f}.webp" width="398" alt="{alt}"></a>')
    if i % 2 == 1 and i < len(GRILLA) - 1:
        grilla.append('<br>')

celdas = [f'''{redes}
<a href="{SITIO}"><img src="assets/marca.svg" width="40" align="left" hspace="4" alt="tomascardozo.com"></a>
<b>Hola, soy Tomás 👋</b><br>
<sub>Diseñador en Buenos Aires. Diseño marcas, sitios y productos. Tomo proyectos freelance.</sub>''',
          '\n'.join(grilla)]
for titulo, chips in filas:
    celdas.append(f'<b>{titulo}</b><br>\n' + '\n'.join(picture(b, alt) for b, alt in chips))

md = '<table>\n' + '\n'.join(f'<tr><td>\n\n{c}\n\n</td></tr>' for c in celdas) + '\n</table>\n'
md += f'\n<sub>Todo lo de arriba se mueve: entrá a <a href="{SITIO}">tomascardozo.com</a>. El código del portfolio está en <a href="https://github.com/manuxxaitos/portfolio-2026">portfolio-2026</a>.</sub>\n'
(RAIZ / 'README.md').write_text(md)
print('README.md', len(md), 'caracteres')
