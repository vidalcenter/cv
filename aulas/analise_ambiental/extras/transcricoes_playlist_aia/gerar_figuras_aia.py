# -*- coding: utf-8 -*-
"""Gera figuras originais para a aula 5.1 (AIA), inspiradas nos conceitos da playlist:
(a) gráfico função do ecossistema x tempo (resistência e resiliência);
(b) escala de qualidade ambiental.
Convenções do projeto: DejaVu Sans, 300 dpi, PNG + SVG, bbox tight.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

SAIDA = Path(__file__).resolve().parents[4] / "img"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 12,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
})


def estilo(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.20)


# ---------------------------------------------------------------- figura (a)
fig, ax = plt.subplots(figsize=(7.2, 4.2))

t1 = np.linspace(0, 4.2, 300)
y1 = 5 + 0.25 * np.sin(2 * np.pi * t1)
t2 = np.linspace(4.2, 5.2, 80)                    # queda (perturbação)
y2 = 5 - 3.5 * (t2 - 4.2) / 1.0
t3 = np.linspace(5.2, 11.0, 300)                  # recuperação
y3 = 1.5 + 3.5 * (1 - np.exp(-(t3 - 5.2) / 1.5))
t4 = np.linspace(11.0, 14.0, 300)
y4 = 5 + 0.25 * np.sin(2 * np.pi * (t4 - 11.0) + 0.4)

ax.plot(t1, y1, color="#2980b9", lw=2.2, label="Função do ecossistema")
ax.plot(t2, y2, color="#2980b9", lw=2.2)
ax.plot(t3, y3, color="#2980b9", lw=2.2)
ax.plot(t4, y4, color="#2980b9", lw=2.2)

ax.axhline(4.75, color="#7f8c8d", ls=":", lw=1.0)
ax.axhline(5.25, color="#7f8c8d", ls=":", lw=1.0)
ax.annotate("Amplitude normal\n(sistema estável)", xy=(1.6, 5.5), fontsize=9, color="#7f8c8d")

ax.annotate("Perturbação", xy=(4.65, 2.6), xytext=(2.9, 1.9),
            arrowprops=dict(arrowstyle="->", color="#c0392b"), color="#c0392b",
            fontsize=9, ha="center")

ax.annotate("", xy=(5.2, 1.05), xytext=(4.2, 1.05),
            arrowprops=dict(arrowstyle="<->", color="#8e44ad", lw=1.4))
ax.text(4.7, 0.75, "Medida de\nresistência", color="#8e44ad", fontsize=9, ha="center")

ax.annotate("", xy=(11.0, 1.05), xytext=(5.2, 1.05),
            arrowprops=dict(arrowstyle="<->", color="#27ae60", lw=1.4))
ax.text(8.1, 0.75, "Medida de resiliência", color="#27ae60", fontsize=9, ha="center")

ax.set_xlabel("Tempo")
ax.set_ylabel("Função do ecossistema")
ax.set_ylim(0, 6.5)
ax.set_xticks([])
ax.set_yticks([])
estilo(ax)
fig.savefig(SAIDA / "resistencia_resiliencia.png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(SAIDA / "resistencia_resiliencia.svg", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- figura (b)
fig, ax = plt.subplots(figsize=(7.2, 1.9))
ax.set_xlim(0, 10)
ax.set_ylim(0, 1.5)
ax.axis("off")

grad = np.linspace(0, 1, 256).reshape(1, -1)
cores = np.zeros((1, 256, 3))
for i in range(256):
    f = i / 255
    if f < 0.5:
        cores[0, i] = [0.75 + 0.25 * f * 2, 0.16 - 0.02 * f * 2, 0.17 - 0.03 * f * 2]
    else:
        g = (f - 0.5) * 2
        cores[0, i] = [1.0 - 0.66 * g, 0.14 + 0.34 * g, 0.14 + 0.02 * g]
ax.imshow(cores, extent=[0, 10, 0.35, 0.95], aspect="auto")

for x, label in [(1.0, "Altamente degradado"), (5.0, "Agrícola / urbano\n(intermediária)"), (9.0, "Próximo do natural")]:
    ax.plot([x, x], [0.95, 1.25], color="#333333", lw=0.8)
    ax.text(x, 1.32, label, ha="center", va="bottom", fontsize=9)

ax.annotate("", xy=(10, 0.15), xytext=(0, 0.15), arrowprops=dict(arrowstyle="->", color="#333333", lw=1.4))
ax.text(0.0, 0.15, "Menor qualidade ambiental", va="center", fontsize=9, color="#333333")
ax.text(10.0, 0.15, "Maior qualidade ambiental", va="center", ha="right", fontsize=9, color="#333333")

fig.savefig(SAIDA / "escala_qualidade_ambiental.png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(SAIDA / "escala_qualidade_ambiental.svg", bbox_inches="tight", facecolor="white")
plt.close(fig)

print("OK:", SAIDA / "resistencia_resiliencia.png")
print("OK:", SAIDA / "escala_qualidade_ambiental.png")
