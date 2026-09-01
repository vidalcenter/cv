#!/usr/bin/env python3
"""
substituir_imagens.py
Downloads CC-licensed replacements from Wikimedia Commons and creates
original vector diagrams for estagios_fragmentacao and matriz_mancha_corredor.
"""
import requests
import io
import json
import sys
from pathlib import Path
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, FancyArrowPatch
import numpy as np

IMG_DIR = Path(r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\meu_site\books\ciencia-paisagem\img")
HEADERS = {"User-Agent": "CienciaPaisagemTextbook/1.0 (educational academic; uefs.edu.br)"}

# ============================================================
# Helpers
# ============================================================

def get_wikimedia_url(filename):
    """Use Wikimedia API to get the direct CDN URL and license info."""
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata",
        "iiextmetadatafilter": "LicenseShortName|Artist",
        "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=HEADERS, timeout=20)
        data = r.json()
        for page in data["query"]["pages"].values():
            info = page.get("imageinfo", [{}])[0]
            url  = info.get("url", "")
            mime = info.get("mime", "")
            size = info.get("size", 0)
            meta = info.get("extmetadata", {})
            license_ = meta.get("LicenseShortName", {}).get("value", "CC")
            if url and "image" in mime and size > 40_000:
                return url, size, license_
    except Exception as e:
        print(f"   API error for {filename}: {e}")
    return None, 0, ""


def search_wikimedia(query, n=5):
    """Search Wikimedia Commons File namespace, return list of filenames."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",
        "srlimit": n,
        "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=HEADERS, timeout=20)
        data = r.json()
        return [item["title"].replace("File:", "")
                for item in data.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"   Search error: {e}")
    return []


def download_image(url, dest_path):
    """Download and validate image, return (bytes_written, error_str)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=90, stream=True)
        r.raise_for_status()
        content = r.content
        # Validate via Pillow
        img = Image.open(io.BytesIO(content))
        img.load()          # fully decode
        fmt = img.format
        if fmt not in ("JPEG", "PNG", "WEBP"):
            return 0, f"unexpected format {fmt}"
        with open(dest_path, "wb") as f:
            f.write(content)
        return len(content), ""
    except Exception as e:
        return 0, str(e)


def pick_and_download(local_name, candidates, search_query=None):
    """
    Try each candidate filename; if all fail and search_query is given,
    fall back to Wikimedia search results.
    Returns (success, license_string).
    """
    dest = IMG_DIR / local_name
    tried = list(candidates)

    if search_query:
        found = search_wikimedia(search_query, n=5)
        tried += [f for f in found if f not in tried]

    for fname in tried:
        url, size, lic = get_wikimedia_url(fname)
        if not url:
            continue
        print(f"   ↳ trying: {fname[:60]}  ({size//1024} KB, {lic})")
        nb, err = download_image(url, dest)
        if nb > 0:
            print(f"   ✅ saved {nb//1024} KB  — {lic}")
            return True, lic
        else:
            print(f"   ✖ {err}")

    print(f"   ❌ all candidates failed for {local_name}")
    return False, ""


# ============================================================
# Downloads
# ============================================================
print("\n" + "="*60)
print("DOWNLOADS — Wikimedia Commons CC")
print("="*60)

# (local_filename, [preferred_wikimedia_filenames], fallback_search_query)
targets = [
    (
        "coivara_roca_toco.jpg",
        ["Amazon_slash_and_burn_agriculture_Colombia_South_America.jpg"],
        "swidden slash burn amazon indigenous brazil coivara",
    ),
    (
        "quebradeira_babacu.jpg",
        [
            "Quebradeira_de_coco_Babaçu_de_Jacobina.jpg",
            "Quebradeira de coco Babaçu de Jacobina.jpg",
            "Breking_babassu.jpg",
        ],
        "quebradeiras coco babacu extrativismo",
    ),
    (
        "cerrado_vegetacao_fixed.jpg",
        [
            "Cerrado_-_Panorâmica.jpg",
            "Cerrado - Panorâmica.jpg",
            "Cerrado_sensu_stricto.JPG",
            "Cerrado_landscape.jpg",
        ],
        "cerrado savanna vegetation landscape brazil",
    ),
    (
        "floresta_amazonica.jpg",
        [
            "Amazon_Manaus_forest.jpg",
            "Floresta_Amazônica_(Amazon_rainforest).jpg",
            "Amazonia.jpg",
        ],
        "amazon rainforest canopy brazil aerial",
    ),
    (
        "agroflorestal_quilombola.jpg",
        [
            "Agroforest_Sapientia.jpg",
            "Agroforestry_system_Brazil.jpg",
            "Multi-strata_agroforestry.jpg",
            "Shade_grown_cacao_brazil.jpg",
        ],
        "agroforestry multi-strata tropical brazil polyculture",
    ),
    (
        "efeito_borda.jpg",
        [
            "ForestEdge.jpg",
            "Forest_Edge_Deforestation.jpg",
            "Boreal_forest_edge_near_Kapuskasing.jpg",
            "Forest-edge.jpg",
        ],
        "forest edge deforestation clearing boundary",
    ),
    (
        "corredor_ecologico.jpg",
        [
            "Mata_ciliar_Brazil.jpg",
            "Riparian_buffer.jpg",
            "Riparian_forest_Brazil.jpg",
            "Gallery_forest_Brazil.jpg",
        ],
        "riparian forest corridor mata ciliar brazil strip",
    ),
    (
        "mosaico_rural.jpg",
        [
            "Aerial_agriculture_Brazil.jpg",
            "Farmland_mosaic.jpg",
            "Patchwork_fields_aerial.jpg",
            "Agricultural_landscape_Brazil.jpg",
        ],
        "aerial farmland mosaic rural landscape brazil",
    ),
]

results = {}
licenses = {}

for local_name, candidates, query in targets:
    print(f"\n→ {local_name}")
    ok, lic = pick_and_download(local_name, candidates, query)
    results[local_name] = ok
    licenses[local_name] = lic

# ============================================================
# DIAGRAM 1: Estágios de Fragmentação Florestal
# ============================================================
print("\n" + "="*60)
print("DIAGRAM 1: estagios_fragmentacao.jpg")
print("="*60)

FOREST_COLOR  = "#2d5a27"
FOREST_INNER  = "#4a8a3e"
MATRIX_COLOR  = "#d4b483"
GRID_N = 64


def make_grid(pattern, seed=42):
    rng = np.random.RandomState(seed)
    g = np.zeros((GRID_N, GRID_N), dtype=float)

    if pattern == "continuous":
        g[:] = 1.0
        # tiny gaps at edges
        for i in range(GRID_N):
            for j in range(GRID_N):
                d_edge = min(i, j, GRID_N-1-i, GRID_N-1-j)
                if d_edge < 2 and rng.random() < 0.25:
                    g[i, j] = 0.0

    elif pattern == "perforation":
        g[:] = 1.0
        for _ in range(10):
            cx = rng.randint(8, GRID_N-8)
            cy = rng.randint(8, GRID_N-8)
            r  = rng.randint(2, 5)
            for i in range(max(0, cx-r-1), min(GRID_N, cx+r+2)):
                for j in range(max(0, cy-r-1), min(GRID_N, cy+r+2)):
                    if (i-cx)**2 + (j-cy)**2 < (r + 0.5*rng.random())**2:
                        g[i, j] = 0.0

    elif pattern == "dissection":
        g[:] = 1.0
        # horizontal strip
        mid = GRID_N // 2
        w = 5
        g[mid-w:mid+w, :] = 0.0
        # two vertical strips
        g[:, GRID_N//3-3:GRID_N//3+3] = 0.0
        g[:, 2*GRID_N//3-3:2*GRID_N//3+3] = 0.0
        # add noise holes
        for _ in range(5):
            cx, cy = rng.randint(5, GRID_N-5), rng.randint(5, GRID_N-5)
            r = rng.randint(2, 4)
            for i in range(max(0, cx-r), min(GRID_N, cx+r)):
                for j in range(max(0, cy-r), min(GRID_N, cy+r)):
                    if (i-cx)**2 + (j-cy)**2 < r**2:
                        g[i, j] = 0.0

    elif pattern == "fragmentation":
        # 5 patches
        centers = [(14, 14, 11), (46, 12, 9), (14, 46, 10),
                   (48, 48, 11), (31, 31, 7)]
        for cx, cy, r in centers:
            for i in range(max(0, cx-r-1), min(GRID_N, cx+r+2)):
                for j in range(max(0, cy-r-1), min(GRID_N, cy+r+2)):
                    noise = 0.7 + 0.6 * rng.random()
                    if (i-cx)**2 + (j-cy)**2 < (r * noise)**2:
                        g[i, j] = 1.0

    elif pattern == "isolation":
        # 7 small patches
        centers = [(10, 10, 5), (50, 8, 4), (8, 50, 4),
                   (52, 52, 5), (30, 30, 4), (18, 36, 3), (44, 28, 3)]
        for cx, cy, r in centers:
            for i in range(max(0, cx-r-1), min(GRID_N, cx+r+2)):
                for j in range(max(0, cy-r-1), min(GRID_N, cy+r+2)):
                    noise = 0.65 + 0.7 * rng.random()
                    if (i-cx)**2 + (j-cy)**2 < (r * noise)**2:
                        g[i, j] = 1.0
    return g


patterns   = ["continuous", "perforation", "dissection", "fragmentation", "isolation"]
labels     = ["Floresta\nContínua", "Perfuração", "Dissecção", "Fragmentação", "Isolamento"]
coverages  = ["~95 %", "~75 %", "~55 %", "~35 %", "~18 %"]
seeds      = [1, 2, 3, 4, 5]

from matplotlib.colors import ListedColormap
landscape_cmap = ListedColormap([MATRIX_COLOR, FOREST_COLOR])

fig, axes = plt.subplots(1, 5, figsize=(14, 3.8), constrained_layout=True)
fig.patch.set_facecolor("white")

for ax, pat, lbl, cov, seed in zip(axes, patterns, labels, coverages, seeds):
    grid = make_grid(pat, seed=seed)
    ax.imshow(grid, cmap=landscape_cmap, vmin=0, vmax=1,
              interpolation="nearest", aspect="equal")
    ax.set_title(f"{lbl}\n{cov}", fontsize=8.5, fontweight="bold",
                 color="#1a1a1a", pad=4)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_linewidth(1.2)
        sp.set_color("#555")

# Add inter-panel arrows via figure-level text
for i in range(4):
    x = (i + 1) / 5 + 0.002
    fig.text(x, 0.47, "›", fontsize=16, ha="center", va="center",
             color="#666", transform=fig.transFigure)

# Legend
handles = [
    mpatches.Patch(facecolor=FOREST_COLOR, edgecolor="#1a1a1a", lw=0.5,
                   label="Floresta / Habitat"),
    mpatches.Patch(facecolor=MATRIX_COLOR, edgecolor="#1a1a1a", lw=0.5,
                   label="Matriz (uso antrópico)"),
]
fig.legend(handles=handles, loc="lower center", ncol=2,
           fontsize=8.5, frameon=True,
           bbox_to_anchor=(0.5, -0.04),
           bbox_transform=fig.transFigure)

fig.suptitle("Estágios Progressivos da Fragmentação Florestal",
             fontsize=11, fontweight="bold", color="#1a1a1a", y=1.01)

dest_ef = IMG_DIR / "estagios_fragmentacao.jpg"
fig.savefig(dest_ef, dpi=240, bbox_inches="tight",
            facecolor="white", format="jpeg", pil_kwargs={"quality": 92})
plt.close(fig)
print(f"✅ estagios_fragmentacao.jpg  ({dest_ef.stat().st_size // 1024} KB)")


# ============================================================
# DIAGRAM 2: Matriz–Mancha–Corredor
# ============================================================
print("\n" + "="*60)
print("DIAGRAM 2: matriz_mancha_corredor.jpg")
print("="*60)

fig, ax = plt.subplots(figsize=(9, 7.2))
fig.patch.set_facecolor("white")

# --- background (matrix) --------------------------------------------------
ax.set_facecolor("#e0c882")   # wheat/sandy = agriculture
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])

rng2 = np.random.RandomState(10)
# subtle field-stripe texture
for y_start in range(0, 100, 8):
    ax.fill_between([0, 100], y_start, y_start+4,
                    color="#d4b070", alpha=0.3, linewidth=0)
# dotted crops
for _ in range(280):
    x, y = rng2.uniform(3, 97), rng2.uniform(3, 97)
    ax.plot(x, y, ".", color="#b89040", ms=1.8, alpha=0.5)


# --- helper: draw organic corridor ----------------------------------------
def draw_corridor(ax, pts, width=5, z=2):
    """Draw a brushstroke-like corridor through a list of (x,y) points."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, "-", lw=width*3.5, color="#3a7a3a",
            solid_capstyle="round", solid_joinstyle="round",
            zorder=z, alpha=0.85)
    ax.plot(xs, ys, "-", lw=width*1.8, color="#5aaa5a",
            solid_capstyle="round", solid_joinstyle="round",
            zorder=z+1, alpha=0.55)


# Corridors (drawn before patches so patches sit on top)
# Upper horizontal: patch-A (20,76) → patch-B (78,80)
draw_corridor(ax, [(20,76),(38,78),(58,78),(78,80)], width=3.5)
# Left vertical: patch-A (20,76) → patch-C (18,26)
draw_corridor(ax, [(20,72),(19,52),(18,30)], width=3.5)
# Right vertical: patch-B (78,80) → patch-D (76,22)
draw_corridor(ax, [(78,76),(77,54),(76,26)], width=3.5)
# Lower horizontal: patch-C (18,26) → patch-D (76,22)
draw_corridor(ax, [(22,24),(48,20),(72,22)], width=3.5)
# Short connectors to central patch-E (50,50)
draw_corridor(ax, [(34,52),(50,52)], width=2.5)
draw_corridor(ax, [(50,52),(64,48)], width=2.5)


# --- helper: draw irregular forest patch ----------------------------------
def draw_patch(ax, cx, cy, rx, ry, angle_deg, seed, z=4):
    th = np.linspace(0, 2*np.pi, 60)
    rng_p = np.random.RandomState(seed)
    noise = 1 + 0.18 * rng_p.randn(60)
    x = cx + rx * noise * np.cos(th)
    y = cy + ry * noise * np.sin(th)
    # rotate
    ang = np.radians(angle_deg)
    xr = cx + (x-cx)*np.cos(ang) - (y-cy)*np.sin(ang)
    yr = cy + (x-cx)*np.sin(ang) + (y-cy)*np.cos(ang)
    ax.fill(xr, yr, color="#1e5c1e", zorder=z, alpha=0.92)
    ax.plot(xr, yr, "-", color="#0d3d0d", lw=1.2, zorder=z+1, alpha=0.8)
    # interior lighter zone
    xi = cx + 0.55*rx*noise*np.cos(th)
    yi = cy + 0.55*ry*noise*np.sin(th)
    xri = cx + (xi-cx)*np.cos(ang) - (yi-cy)*np.sin(ang)
    yri = cy + (xi-cx)*np.sin(ang) + (yi-cy)*np.cos(ang)
    ax.fill(xri, yri, color="#2d7d2d", zorder=z+2, alpha=0.4)


# Patches: (cx, cy, rx, ry, angle, seed)
patches_def = [
    (20, 76, 11, 8,  -15, 1),   # A — upper left
    (78, 80, 10, 7,   10, 2),   # B — upper right
    (18, 26, 10, 9,    5, 3),   # C — lower left
    (76, 22, 11, 7,  -10, 4),   # D — lower right
    (50, 52,  7, 5,    0, 5),   # E — central
]
for cx, cy, rx, ry, ang, s in patches_def:
    draw_patch(ax, cx, cy, rx, ry, ang, seed=s)


# --- labels with callout arrows -------------------------------------------
lbl_box = dict(boxstyle="round,pad=0.35", lw=0.8)

# MANCHA label
ax.annotate("MANCHA\n(fragmento florestal)",
            xy=(17, 80), xytext=(2, 93),
            fontsize=9, fontweight="bold", color="#0d3d0d", ha="left",
            bbox=dict(**lbl_box, facecolor="#c8e6c8", edgecolor="#1e5c1e"),
            arrowprops=dict(arrowstyle="->", color="#1e5c1e", lw=1.2,
                            connectionstyle="arc3,rad=-0.1"))

# CORREDOR label (pointing to upper corridor strip)
ax.annotate("CORREDOR\n(conectividade estrutural)",
            xy=(48, 78), xytext=(34, 95),
            fontsize=9, fontweight="bold", color="#0d3d0d", ha="center",
            bbox=dict(**lbl_box, facecolor="#c8e6c8", edgecolor="#1e5c1e"),
            arrowprops=dict(arrowstyle="->", color="#1e5c1e", lw=1.2,
                            connectionstyle="arc3,rad=0.15"))

# MATRIZ label
ax.annotate("MATRIZ\n(uso antrópico / pastagem)",
            xy=(55, 6), fontsize=9, fontweight="bold",
            color="#5c4a00", ha="center",
            bbox=dict(**lbl_box, facecolor="#f5e6b0", edgecolor="#9c8a30"))

# PATCH-E label
ax.annotate("Mancha\ncentral",
            xy=(54, 52), xytext=(68, 62),
            fontsize=8, color="#0d3d0d", ha="center",
            bbox=dict(**lbl_box, facecolor="#c8e6c8", edgecolor="#1e5c1e",
                      alpha=0.85),
            arrowprops=dict(arrowstyle="->", color="#1e5c1e", lw=1.0,
                            connectionstyle="arc3,rad=-0.2"))

for sp in ax.spines.values():
    sp.set_linewidth(1.5)
    sp.set_color("#555")

ax.set_title("Modelo Matriz – Mancha – Corredor\n"
             "(Forman & Godron, 1986; elaboração própria)",
             fontsize=11, fontweight="bold", color="#1a1a1a", pad=10)

dest_mmc = IMG_DIR / "matriz_mancha_corredor.jpg"
fig.savefig(dest_mmc, dpi=240, bbox_inches="tight",
            facecolor="white", format="jpeg", pil_kwargs={"quality": 93})
plt.close(fig)
print(f"✅ matriz_mancha_corredor.jpg  ({dest_mmc.stat().st_size // 1024} KB)")


# ============================================================
# Summary
# ============================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for name, ok in results.items():
    icon = "✅" if ok else "❌"
    lic  = f"  [{licenses.get(name, '')}]" if ok else ""
    print(f"  {icon}  {name}{lic}")
print("  ✅  estagios_fragmentacao.jpg   (diagram — original)")
print("  ✅  matriz_mancha_corredor.jpg  (diagram — original)")

# Save license info for caption updates
license_map = {k: v for k, v in licenses.items() if v}
with open(IMG_DIR / "_licenses.json", "w") as f:
    json.dump(license_map, f, indent=2, ensure_ascii=False)
print(f"\nLicense map saved to img/_licenses.json")
