"""Generate charts for Extensão Rural presentations (aulas 09, 13, 14).

Charts:
1. Internet access: rural vs urban (PNAD Contínua TIC 2022/2023)
2. Trabalho escravo: resgates por período (MTE/SIT 1995-2023)
3. Conflitos agrários CPT: evolução 2018-2022
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

IMG_DIR = os.path.join("aulas", "extensao_rural", "aulas", "img")
os.makedirs(IMG_DIR, exist_ok=True)

# Cores UEFS-ish
AZUL = "#1a5276"
VERDE = "#27ae60"
VERMELHO = "#c0392b"
LARANJA = "#e67e22"
CINZA = "#7f8c8d"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 14,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.grid": True,
    "grid.alpha": 0.3,
})

# ──────────────────────────────────────────────────────────
# 1. Internet Rural vs Urbano – PNAD Contínua TIC 2022/2023
# Fonte: IBGE - PNAD Contínua - Tecnologia da Informação e Comunicação
# ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

anos = ["2017", "2018", "2019", "2021", "2022"]
rural = [41.0, 49.2, 55.6, 72.0, 78.2]   # % domicílios com internet
urbano = [80.1, 83.8, 86.7, 90.0, 91.5]

x = np.arange(len(anos))
w = 0.35
bars_u = ax.bar(x - w/2, urbano, w, label="Urbano", color=AZUL, edgecolor="white")
bars_r = ax.bar(x + w/2, rural, w, label="Rural", color=VERDE, edgecolor="white")

for bar in bars_u:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{bar.get_height():.0f}%", ha="center", va="bottom", fontsize=11, color=AZUL, fontweight="bold")
for bar in bars_r:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{bar.get_height():.0f}%", ha="center", va="bottom", fontsize=11, color=VERDE, fontweight="bold")

ax.set_xlabel("Ano")
ax.set_ylabel("Domicílios com internet (%)")
ax.set_title("Acesso à Internet: Domicílios Rurais vs Urbanos\n(PNAD Contínua TIC — IBGE)")
ax.set_xticks(x)
ax.set_xticklabels(anos)
ax.set_ylim(0, 105)
ax.legend(loc="upper left", framealpha=0.9)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "grafico_internet_rural_urbano.png"), dpi=200)
plt.close(fig)
print("OK: grafico_internet_rural_urbano.png")

# ──────────────────────────────────────────────────────────
# 2. Trabalho Escravo – Resgates por período (MTE/SIT)
# Fonte: Painel do Trabalho Escravo - SmartLab / MPT / OIT
# ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

periodos = ["1995-\n1999", "2000-\n2004", "2005-\n2009", "2010-\n2014", "2015-\n2019", "2020-\n2023"]
resgates = [2285, 13244, 17405, 10998, 9156, 6476]  # Total ~59564

bars = ax.bar(periodos, resgates, color=[VERMELHO]*6, edgecolor="white", width=0.65)
for bar, val in zip(bars, resgates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f"{val:,}".replace(",", "."), ha="center", va="bottom",
            fontsize=12, fontweight="bold", color=VERMELHO)

ax.set_xlabel("Período")
ax.set_ylabel("Trabalhadores resgatados")
ax.set_title("Trabalhadores Resgatados de Condição Análoga à Escravidão\n(MTE/SIT — Grupo Especial de Fiscalização Móvel, 1995-2023)")
ax.set_ylim(0, 20000)

# Anotação do total
ax.annotate(f"Total: 59.564 trabalhadores resgatados",
            xy=(0.98, 0.95), xycoords="axes fraction",
            fontsize=12, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#fadbd8", edgecolor=VERMELHO, alpha=0.9))

fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "grafico_trabalho_escravo_resgates.png"), dpi=200)
plt.close(fig)
print("OK: grafico_trabalho_escravo_resgates.png")

# ──────────────────────────────────────────────────────────
# 3. Conflitos Agrários CPT – Evolução 2018-2022
# Fonte: CPT - Caderno Conflitos no Campo Brasil
# ──────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

# 3a. Conflitos por terra
anos_cpt = ["2018", "2019", "2020", "2021", "2022"]
conflitos_terra = [1489, 1254, 1576, 1768, 1893]
assassinatos = [28, 32, 18, 35, 47]

ax1.fill_between(range(len(anos_cpt)), conflitos_terra, alpha=0.3, color=LARANJA)
ax1.plot(range(len(anos_cpt)), conflitos_terra, "o-", color=LARANJA, linewidth=2.5, markersize=8)
for i, v in enumerate(conflitos_terra):
    ax1.text(i, v + 40, str(v), ha="center", fontsize=11, fontweight="bold", color=LARANJA)

ax1.set_xticks(range(len(anos_cpt)))
ax1.set_xticklabels(anos_cpt)
ax1.set_title("Conflitos por Terra")
ax1.set_ylabel("N.° de ocorrências")
ax1.set_ylim(1000, 2200)

# 3b. Assassinatos no campo
ax2.fill_between(range(len(anos_cpt)), assassinatos, alpha=0.3, color=VERMELHO)
ax2.plot(range(len(anos_cpt)), assassinatos, "s-", color=VERMELHO, linewidth=2.5, markersize=8)
for i, v in enumerate(assassinatos):
    ax2.text(i, v + 1.5, str(v), ha="center", fontsize=11, fontweight="bold", color=VERMELHO)

ax2.set_xticks(range(len(anos_cpt)))
ax2.set_xticklabels(anos_cpt)
ax2.set_title("Assassinatos no Campo")
ax2.set_ylabel("N.° de vítimas")
ax2.set_ylim(0, 60)

fig.suptitle("Conflitos Agrários no Brasil (CPT — Caderno Conflitos no Campo)", fontsize=15, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "grafico_conflitos_cpt.png"), dpi=200, bbox_inches="tight")
plt.close(fig)
print("OK: grafico_conflitos_cpt.png")

# ──────────────────────────────────────────────────────────
# 4. Comunicação de Massa no Campo – Meios utilizados
# Fonte: Adaptado de dados da PNAD Contínua TIC 2022
# ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

meios = ["Celular/\nSmartphone", "TV\nAberta", "Rádio", "Internet\n(fixo)", "WhatsApp", "YouTube"]
uso_rural = [87.3, 95.1, 42.5, 21.4, 79.0, 45.2]  # % da população rural
cores = [VERDE, AZUL, LARANJA, CINZA, "#27ae60", VERMELHO]

bars = ax.barh(meios, uso_rural, color=cores, edgecolor="white", height=0.6)
for bar, val in zip(bars, uso_rural):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}%", ha="left", va="center", fontsize=12, fontweight="bold")

ax.set_xlabel("Utilização pela população rural (%)")
ax.set_title("Meios de Comunicação no Campo Brasileiro\n(Adaptado de PNAD Contínua TIC / IBGE, 2022)")
ax.set_xlim(0, 110)
ax.invert_yaxis()

fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "grafico_comunicacao_rural.png"), dpi=200)
plt.close(fig)
print("OK: grafico_comunicacao_rural.png")

print("\n=== Todos os gráficos gerados com sucesso! ===")
