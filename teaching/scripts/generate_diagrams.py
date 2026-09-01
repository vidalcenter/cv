"""
Gera diagramas conceituais para Aula 02 - Análise da Paisagem.
Usa matplotlib para criar figuras de alta qualidade.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

IMG_DIR = os.path.join("aulas", "analise_paisagem", "aulas", "evolucao_conceito_distincoes", "img")
os.makedirs(IMG_DIR, exist_ok=True)

# Cores UEFS-inspired
UEFS_BLUE = "#2135A6"
UEFS_DARK = "#1a2a6c"
ACCENT_GREEN = "#2e7d32"
ACCENT_ORANGE = "#e65100"
ACCENT_RED = "#c62828"
LIGHT_BG = "#f5f7fa"
WHITE = "#ffffff"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Helvetica", "Arial"],
    "font.size": 12,
    "axes.facecolor": LIGHT_BG,
    "figure.facecolor": WHITE,
})


def save(fig, name):
    path = os.path.join(IMG_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    sz = os.path.getsize(path) // 1024
    print(f"  [OK] {name} ({sz} KB)")


# ═══════════════════════════════════════════════════════════════════
# 1. HIERARQUIA ESCALAR DE BERTRAND (pirâmide)
# ═══════════════════════════════════════════════════════════════════
def diagram_bertrand_hierarchy():
    print("Gerando: hierarquia de Bertrand...")
    fig, ax = plt.subplots(figsize=(10, 7))

    levels = [
        ("Zona", "10⁷ km²", "Zona Intertropical", "#1a237e"),
        ("Domínio", "10⁵–10⁶ km²", "Domínio da Caatinga", "#283593"),
        ("Região Natural", "10³–10⁴ km²", "Depressão Sertaneja", "#3949ab"),
        ("GEOSSISTEMA", "10¹–10² km²", "Vale do Jacuípe", "#e65100"),
        ("Geofácies", "10⁻¹–10⁰ km²", "Encosta c/ veg. secundária", "#5c6bc0"),
        ("Geótopo", "< 10⁻¹ km²", "Afloramento rochoso", "#7986cb"),
    ]

    n = len(levels)
    max_w = 9
    min_w = 2
    h = 0.85
    gap = 0.15

    for i, (name, scale, example, color) in enumerate(levels):
        y = (n - 1 - i) * (h + gap)
        w = max_w - i * (max_w - min_w) / (n - 1)
        x = (max_w - w) / 2

        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor="white", linewidth=2,
            alpha=0.9
        )
        ax.add_patch(rect)

        # Texto principal
        fontweight = "bold" if i == 3 else "normal"
        fontsize = 14 if i == 3 else 11
        ax.text(x + w / 2, y + h * 0.6, name,
                ha="center", va="center", fontsize=fontsize,
                fontweight=fontweight, color="white")
        ax.text(x + w / 2, y + h * 0.25, f"{scale}  •  {example}",
                ha="center", va="center", fontsize=8.5, color="#e0e0e0",
                style="italic")

    # Seta indicando escala
    ax.annotate("", xy=(10, 0), xytext=(10, (n - 1) * (h + gap) + h),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=2))
    ax.text(10.3, n * (h + gap) / 2, "Escala\ncrescente",
            ha="left", va="center", fontsize=10, color="#555", rotation=90)

    # Destaque geossistema
    ax.text(max_w + 0.3, 3 * (h + gap) + h / 2,
            "← Escala operacional\n    de análise",
            fontsize=10, color=ACCENT_ORANGE, fontweight="bold", va="center")

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, n * (h + gap) + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Hierarquia Escalar de Bertrand (1968)",
                 fontsize=16, fontweight="bold", color=UEFS_DARK, pad=15)

    save(fig, "diagrama_bertrand_hierarquia.png")


# ═══════════════════════════════════════════════════════════════════
# 2. MODELO DO GEOSSISTEMA (Sochava/Bertrand)
# ═══════════════════════════════════════════════════════════════════
def diagram_geossistema():
    print("Gerando: modelo do geossistema...")
    fig, ax = plt.subplots(figsize=(10, 7))

    # Três componentes como círculos sobrepostos (Venn)
    from matplotlib.patches import Circle

    centers = [(3.5, 4), (6.5, 4), (5, 6.5)]
    colors = ["#1565c0", "#2e7d32", "#e65100"]
    labels = [
        "POTENCIAL\nECOLÓGICO\n\n(relevo, clima,\nhidrologia, solos)",
        "EXPLORAÇÃO\nBIOLÓGICA\n\n(vegetação, fauna,\nbiodiversidade)",
        "AÇÃO\nANTRÓPICA\n\n(uso da terra, ocupação,\nintervenções)"
    ]

    for center, color, label in zip(centers, colors, labels):
        circ = Circle(center, 2.2, alpha=0.15, facecolor=color, edgecolor=color, linewidth=2.5)
        ax.add_patch(circ)
        ax.text(center[0], center[1], label,
                ha="center", va="center", fontsize=9, fontweight="bold",
                color=color)

    # Centro = geossistema
    ax.text(5, 4.7, "GEOSSISTEMA",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=WHITE,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=UEFS_BLUE,
                      edgecolor="white", linewidth=2, alpha=0.95))

    # Setas de entrada/saída
    ax.annotate("Energia solar\nPrecipitação", xy=(1.2, 7),
                fontsize=8, ha="center", va="center", color="#555",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#e3f2fd", edgecolor="#90caf9"))
    ax.annotate("", xy=(2.5, 6), xytext=(1.5, 6.6),
                arrowprops=dict(arrowstyle="->", color="#1565c0", lw=1.5))

    ax.annotate("Escoamento\nSedimentos\nBiomassa", xy=(8.8, 7),
                fontsize=8, ha="center", va="center", color="#555",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#fff3e0", edgecolor="#ffcc80"))
    ax.annotate("", xy=(8.2, 6.6), xytext=(7.5, 6),
                arrowprops=dict(arrowstyle="->", color=ACCENT_ORANGE, lw=1.5))

    # Labels laterais
    ax.text(5, 1.2, "Sistema aberto: fluxos de energia e matéria",
            ha="center", va="center", fontsize=10, style="italic",
            color="#555")
    ax.text(5, 0.5, "Sochava (1963) • Bertrand (1968)",
            ha="center", va="center", fontsize=9, color="#888")

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Modelo do Geossistema",
                 fontsize=16, fontweight="bold", color=UEFS_DARK, pad=15)

    save(fig, "diagrama_geossistema.png")


# ═══════════════════════════════════════════════════════════════════
# 3. TRILOGIA GTP (Bertrand, 2000s)
# ═══════════════════════════════════════════════════════════════════
def diagram_gtp():
    print("Gerando: trilogia GTP...")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Três caixas interconectadas
    boxes = [
        (1, 2.5, "G\nGeossistema", "Funcionamento\nbiofísico\n\nFonte → Recurso", "#1565c0"),
        (4, 2.5, "T\nTerritório", "Gestão e uso\ndo espaço\n\nRecurso → Política", "#2e7d32"),
        (7, 2.5, "P\nPaisagem", "Percepção e\nrepresentação\n\nIdentidade → Valor", "#e65100"),
    ]

    box_w = 2.5
    box_h = 3.5

    for x, y, title, desc, color in boxes:
        # Caixa principal
        rect = FancyBboxPatch(
            (x, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.15",
            facecolor=color, edgecolor="white", linewidth=3,
            alpha=0.9
        )
        ax.add_patch(rect)

        # Letra grande
        ax.text(x + box_w / 2, y + 1, title.split("\n")[0],
                ha="center", va="center", fontsize=28, fontweight="bold",
                color="white", alpha=0.4)

        # Nome
        ax.text(x + box_w / 2, y + 0.6, title.split("\n")[1],
                ha="center", va="center", fontsize=12, fontweight="bold",
                color="white")

        # Descrição
        ax.text(x + box_w / 2, y - 0.6, desc,
                ha="center", va="center", fontsize=8.5, color="#e0e0e0")

    # Setas bidirecionais entre caixas
    for x1, x2 in [(3.5, 4), (6.5, 7)]:
        ax.annotate("", xy=(x2, 2.5), xytext=(x1, 2.5),
                    arrowprops=dict(arrowstyle="<->", color="#555", lw=2))

    # Texto inferior
    ax.text(5.25, -0.3, "Nenhuma entrada sozinha é suficiente.\nA análise completa articula as três.",
            ha="center", va="center", fontsize=10, style="italic", color="#555")

    ax.text(5.25, -1.0, "Georges Bertrand (revisão, anos 2000)",
            ha="center", va="center", fontsize=9, color="#888")

    ax.set_xlim(0, 10.5)
    ax.set_ylim(-1.5, 5.5)
    ax.axis("off")
    ax.set_title("Trilogia GTP – Geossistema • Território • Paisagem",
                 fontsize=16, fontweight="bold", color=UEFS_DARK, pad=15)

    save(fig, "diagrama_gtp.png")


# ═══════════════════════════════════════════════════════════════════
# 4. MODELO MATRIZ-MANCHA-CORREDOR (Forman & Godron)
# ═══════════════════════════════════════════════════════════════════
def diagram_patch_matrix_corridor():
    print("Gerando: matriz-mancha-corredor...")
    fig, ax = plt.subplots(figsize=(10, 7))

    # Fundo = matriz (pastagem)
    from matplotlib.patches import Rectangle, Polygon

    # Matriz (fundo verde claro)
    ax.add_patch(Rectangle((0, 0), 10, 8, facecolor="#c8e6c9", edgecolor="none"))

    # Manchas (fragmentos florestais)
    patch_coords = [
        (1.5, 5.5, 1.8, 1.5),
        (7, 5, 2, 2),
        (4, 1, 1.5, 1.2),
        (1, 1.5, 1, 0.8),
        (8.5, 2, 0.8, 0.7),
    ]
    for x, y, w, h in patch_coords:
        ellipse = matplotlib.patches.Ellipse(
            (x, y), w, h,
            facecolor="#2e7d32", edgecolor="#1b5e20", linewidth=1.5, alpha=0.8
        )
        ax.add_patch(ellipse)

    # Corredores (matas ciliares)
    corridor_x = np.linspace(0, 10, 100)
    corridor_y1 = 3.5 + 0.3 * np.sin(corridor_x * 0.8)
    corridor_y2 = corridor_y1 + 0.4
    ax.fill_between(corridor_x, corridor_y1, corridor_y2,
                    facecolor="#388e3c", alpha=0.7, edgecolor="#1b5e20", linewidth=1)

    # Corredor vertical
    corridor_y_v = np.linspace(0, 8, 80)
    corridor_x1 = 5.5 + 0.2 * np.sin(corridor_y_v * 1.2)
    corridor_x2 = corridor_x1 + 0.35
    ax.fill_betweenx(corridor_y_v, corridor_x1, corridor_x2,
                     facecolor="#388e3c", alpha=0.6, edgecolor="#1b5e20", linewidth=1)

    # Labels com setas
    ax.annotate("MATRIZ\n(pastagem)", xy=(3, 6.5),
                fontsize=12, fontweight="bold", ha="center",
                color="#33691e",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax.annotate("MANCHA\n(fragmento)", xy=(7, 5), xytext=(9.5, 7),
                fontsize=10, fontweight="bold", ha="center", color="#1b5e20",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85),
                arrowprops=dict(arrowstyle="->", color="#1b5e20", lw=1.5))

    ax.annotate("CORREDOR\n(mata ciliar)", xy=(2.5, 3.8), xytext=(0.5, 2),
                fontsize=10, fontweight="bold", ha="center", color="#1b5e20",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85),
                arrowprops=dict(arrowstyle="->", color="#1b5e20", lw=1.5))

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-1, 9)
    ax.axis("off")
    ax.set_title("Modelo Matriz – Mancha – Corredor (Forman & Godron, 1986)",
                 fontsize=14, fontweight="bold", color=UEFS_DARK, pad=15)

    ax.text(5, -0.5, "Toda paisagem pode ser decomposta nestes três elementos estruturais",
            ha="center", fontsize=10, style="italic", color="#555")

    save(fig, "diagrama_matriz_mancha_corredor.png")


# ═══════════════════════════════════════════════════════════════════
# 5. DEFINIÇÃO OPERACIONAL DE PAISAGEM (diagrama conceitual)
# ═══════════════════════════════════════════════════════════════════
def diagram_definicao_operacional():
    print("Gerando: definição operacional...")
    fig, ax = plt.subplots(figsize=(12, 7))

    # Componentes à esquerda
    components = [
        ("Abióticos", "relevo, clima,\nhidrologia, solos", "#1565c0", 0.5, 5.5),
        ("Bióticos", "vegetação, fauna,\nbiodiversidade", "#2e7d32", 0.5, 3.5),
        ("Socioespaciais", "uso da terra, ocupação,\ninfraestrutura", "#e65100", 0.5, 1.5),
    ]

    for name, desc, color, x, y in components:
        rect = FancyBboxPatch(
            (x, y - 0.6), 2.5, 1.2,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="white", linewidth=2, alpha=0.85
        )
        ax.add_patch(rect)
        ax.text(x + 1.25, y + 0.15, name,
                ha="center", va="center", fontsize=11, fontweight="bold", color="white")
        ax.text(x + 1.25, y - 0.25, desc,
                ha="center", va="center", fontsize=7.5, color="#e0e0e0")

    # Setas → interação
    for y in [5.5, 3.5, 1.5]:
        ax.annotate("", xy=(3.5, y), xytext=(3, y),
                    arrowprops=dict(arrowstyle="->", color="#555", lw=1.5))

    # Caixa central: INTERAÇÃO
    rect_center = FancyBboxPatch(
        (3.5, 2.5), 2.2, 2,
        boxstyle="round,pad=0.15",
        facecolor="#7b1fa2", edgecolor="white", linewidth=2, alpha=0.9
    )
    ax.add_patch(rect_center)
    ax.text(4.6, 3.5, "INTERAÇÃO\n\nmosaico\nheterogêneo",
            ha="center", va="center", fontsize=10, fontweight="bold", color="white")

    # Seta → análise
    ax.annotate("", xy=(6.2, 3.5), xytext=(5.7, 3.5),
                arrowprops=dict(arrowstyle="->", color="#555", lw=2))

    # Três dimensões de análise
    dims = [
        ("Estrutura", "composição e\narranjo espacial", "#c62828", 6.5, 5.5),
        ("Função", "fluxos e\nprocessos", "#ad1457", 6.5, 3.5),
        ("Dinâmica", "mudanças\nno tempo", "#6a1b9a", 6.5, 1.5),
    ]

    for name, desc, color, x, y in dims:
        rect = FancyBboxPatch(
            (x, y - 0.6), 2.2, 1.2,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="white", linewidth=2, alpha=0.85
        )
        ax.add_patch(rect)
        ax.text(x + 1.1, y + 0.15, name,
                ha="center", va="center", fontsize=11, fontweight="bold", color="white")
        ax.text(x + 1.1, y - 0.25, desc,
                ha="center", va="center", fontsize=8, color="#e0e0e0")

    # Setas → produto
    for y in [5.5, 3.5, 1.5]:
        ax.annotate("", xy=(9.2, y), xytext=(8.7, y),
                    arrowprops=dict(arrowstyle="->", color="#555", lw=1.5))

    # Produto final
    rect_final = FancyBboxPatch(
        (9.2, 2), 2.5, 3,
        boxstyle="round,pad=0.15",
        facecolor=UEFS_BLUE, edgecolor="white", linewidth=3, alpha=0.95
    )
    ax.add_patch(rect_final)
    ax.text(10.45, 3.5, "DIAGNÓSTICO\n&\nPLANEJAMENTO\nTERRITORIAL",
            ha="center", va="center", fontsize=11, fontweight="bold", color="white")

    # Labels de fluxo
    ax.text(3.2, 6.5, "Componentes", fontsize=9, fontweight="bold",
            ha="center", color="#555")
    ax.text(4.6, 6.5, "Integração", fontsize=9, fontweight="bold",
            ha="center", color="#7b1fa2")
    ax.text(7.6, 6.5, "Análise", fontsize=9, fontweight="bold",
            ha="center", color="#c62828")
    ax.text(10.45, 6.5, "Aplicação", fontsize=9, fontweight="bold",
            ha="center", color=UEFS_BLUE)

    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    ax.set_title("Paisagem – Definição Operacional de Trabalho",
                 fontsize=16, fontweight="bold", color=UEFS_DARK, pad=15)

    save(fig, "diagrama_definicao_operacional.png")


# ═══════════════════════════════════════════════════════════════════
# EXECUTAR TODOS
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("GERANDO DIAGRAMAS CONCEITUAIS (matplotlib)")
    print("=" * 60)
    diagram_bertrand_hierarchy()
    diagram_geossistema()
    diagram_gtp()
    diagram_patch_matrix_corridor()
    diagram_definicao_operacional()
    print(f"\nTodos os diagramas gerados em: {IMG_DIR}")
    print(f"Arquivos: {os.listdir(IMG_DIR)}")
