# -*- coding: utf-8 -*-
"""Desenha o triangulo textural da SBCS com as fronteiras reais das classes.

A versao anterior desta figura havia sido gerada por modelo de imagem e trazia campos
simetricos que nao correspondem aos limites normativos. Aqui os poligonos sao definidos
pelos limites de areia, silte e argila de cada classe e sao validados por amostragem do
simplexo antes do desenho, de modo que nenhuma composicao fique sem classe ou caia em
duas classes ao mesmo tempo.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.path import Path

SAIDA = r"c:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/meu_site/books/bioengenharia-solos/img/triangulo_textural.jpg"

# poligonos em (areia, argila); o silte e o complemento para 100
CLASSES = [
    ('Muito argilosa',        [(0, 60), (40, 60), (0, 100)]),
    ('Argila',                [(0, 60), (20, 40), (45, 40), (45, 55), (40, 60)]),
    ('Argila siltosa',        [(0, 40), (20, 40), (0, 60)]),
    ('Argila arenosa',        [(45, 35), (65, 35), (45, 55)]),
    ('Franco argilo siltoso', [(0, 27), (20, 27), (20, 40), (0, 40)]),
    ('Franco argiloso',       [(20, 27), (45, 27), (45, 40), (20, 40)]),
    ('Franco argilo arenoso', [(52, 20), (45, 27), (45, 35), (65, 35), (80, 20)]),
    ('Franco',                [(23, 27), (45, 27), (52, 20), (52, 7), (43, 7)]),
    ('Franco siltoso',        [(0, 12), (8, 12), (20, 0), (50, 0), (23, 27), (0, 27)]),
    ('Silte',                 [(0, 0), (20, 0), (8, 12), (0, 12)]),
    ('Franco arenoso',        [(50, 0), (70, 0), (85, 15), (80, 20), (52, 20), (52, 7), (43, 7)]),
    ('Areia franca',          [(70, 0), (85, 0), (90, 10), (85, 15)]),
    ('Areia',                 [(85, 0), (100, 0), (90, 10)]),
]

# rotulo: (texto em linhas, posicao em (areia, argila), tamanho)
ROTULOS = [
    ('MUITO\nARGILOSA',        (12, 72), 8.0),
    ('ARGILA',                 (18, 48), 8.5),
    ('ARGILA\nSILTOSA',        (6, 46), 7.5),
    ('ARGILA\nARENOSA',        (52, 42), 7.5),
    ('FRANCO\nARGILO\nSILTOSO', (7, 32), 7.0),
    ('FRANCO\nARGILOSO',       (32, 32), 7.5),
    ('FRANCO\nARGILO\nARENOSO', (60, 26), 7.0),
    ('FRANCO',                 (40, 16), 8.5),
    ('FRANCO SILTOSO',         (18, 12), 7.5),
    ('SILTE',                  (6, 4), 8.0),
    ('FRANCO ARENOSO',         (62, 9), 7.5),
    ('AREIA\nFRANCA',          (81, 5), 6.5),
    ('AREIA',                  (93, 3), 7.0),
]


def xy(areia, argila):
    """Converte (areia, argila) para o plano, com areia crescendo para a esquerda."""
    silte = 100.0 - areia - argila
    return silte + 0.5 * argila, (np.sqrt(3) / 2.0) * argila


def valida():
    """Confere se os poligonos cobrem o simplexo sem lacuna e sem sobreposicao."""
    caminhos = [(nome, Path([xy(a, c) for a, c in pts])) for nome, pts in CLASSES]
    falhas = {'vazio': 0, 'duplo': 0}
    passo = 1.0
    for areia in np.arange(0.5, 100, passo):
        for argila in np.arange(0.5, 100 - areia, passo):
            p = xy(areia, argila)
            n = sum(1 for _, cam in caminhos if cam.contains_point(p, radius=0.12))
            if n == 0:
                falhas['vazio'] += 1
            elif n > 1:
                falhas['duplo'] += 1
    total = sum(1 for areia in np.arange(0.5, 100, passo)
                for _ in np.arange(0.5, 100 - areia, passo))
    print('validacao: %d pontos | sem classe: %d | em duas classes: %d'
          % (total, falhas['vazio'], falhas['duplo']))
    return falhas


fig, ax = plt.subplots(figsize=(8.4, 7.6), dpi=300)

# grade interna de 10 em 10
for v in range(10, 100, 10):
    ax.plot(*zip(xy(100 - v, 0), xy(0, 100 - v)), color='0.78', lw=0.5, zorder=1)      # areia
    ax.plot(*zip(xy(v, 0), xy(0, v)), color='0.78', lw=0.5, zorder=1)                   # argila const.
    ax.plot(*zip(xy(100 - v, v), xy(0, v)), color='0.78', lw=0.5, zorder=1)
for v in range(10, 100, 10):
    ax.plot(*zip(xy(100 - v, 0), xy(100 - v, v)), color='0.78', lw=0.5, zorder=1)

# limites das classes
for nome, pts in CLASSES:
    ax.add_patch(Polygon([xy(a, c) for a, c in pts], closed=True, fill=False,
                         edgecolor='black', lw=1.3, zorder=3))

# contorno do triangulo
ax.add_patch(Polygon([xy(100, 0), xy(0, 0), xy(0, 100)], closed=True, fill=False,
                     edgecolor='black', lw=2.0, zorder=4))

# rotulos das classes
for texto, (a, c), tam in ROTULOS:
    x, y = xy(a, c)
    ax.text(x, y, texto, ha='center', va='center', fontsize=tam, zorder=5,
            family='DejaVu Sans', linespacing=1.15)

# escalas dos tres eixos
for v in range(0, 101, 10):
    # argila, lado esquerdo
    x0, y0 = xy(100 - v, v)
    ax.plot([x0, x0 - 1.6], [y0, y0], color='black', lw=0.9, zorder=4)
    ax.text(x0 - 3.0, y0, str(v), ha='right', va='center', fontsize=7.5)
    # silte, lado direito
    x1, y1 = xy(0, 100 - v)
    ax.plot([x1, x1 + 1.6], [y1, y1], color='black', lw=0.9, zorder=4)
    ax.text(x1 + 3.0, y1, str(v), ha='left', va='center', fontsize=7.5)
    # areia, base
    x2, y2 = xy(v, 0)
    ax.plot([x2, x2], [y2, y2 - 1.6], color='black', lw=0.9, zorder=4)
    ax.text(x2, y2 - 4.0, str(v), ha='center', va='top', fontsize=7.5)

ax.text(xy(60, 55)[0] - 14, xy(60, 55)[1], '% ARGILA', rotation=60,
        ha='center', va='center', fontsize=9.5, family='DejaVu Sans')
ax.text(xy(0, 55)[0] + 14, xy(0, 55)[1], '% SILTE', rotation=-60,
        ha='center', va='center', fontsize=9.5, family='DejaVu Sans')
ax.text(50, -10.5, '% AREIA', ha='center', va='center', fontsize=9.5,
        family='DejaVu Sans')
ax.annotate('', xy=(30, -7.6), xytext=(70, -7.6),
            arrowprops=dict(arrowstyle='->', lw=0.9, color='black'))

ax.set_xlim(-14, 114)
ax.set_ylim(-14, 94)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.2)

falhas = valida()
fig.savefig(SAIDA, dpi=300, facecolor='white', bbox_inches='tight', pil_kwargs={'quality': 92})
print('gravado:', SAIDA, '%.2f MB' % (os.path.getsize(SAIDA) / 1e6))
