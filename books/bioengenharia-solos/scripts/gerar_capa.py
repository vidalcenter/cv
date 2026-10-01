"""
Gera a capa para "Soluções Baseadas na Natureza para Bioengenharia de Água e Solo"
Tema forte em raízes, camadas de solo e sustentação biológica.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

W, H = 1357, 1888
DPI = 150

# Paleta terrosa e orgânica
c_soil_dark = (35, 20, 15)
c_soil_core = (55, 30, 20)
c_vegetation = (50, 140, 70)
c_light_green = (120, 190, 100)
c_acc = (230, 200, 140) # areia/raiz
WHITE = (255, 255, 255)
SUBTLE = (200, 190, 180)

def get_font(name, size, bold=False):
    cands = [
        f"C:/Windows/Fonts/{name}bd.ttf" if bold else f"C:/Windows/Fonts/{name}.ttf",
        f"C:/Windows/Fonts/{name}-Bold.ttf" if bold else f"C:/Windows/Fonts/{name}-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for path in cands:
        if os.path.exists(path): return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# 1. Fundo Gradiente ou Imagem Real
bg_img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", "talude_biotextil.jpg")

if os.path.exists(bg_img_path):
    bg_img = Image.open(bg_img_path).convert("RGBA")
    bg_w, bg_h = bg_img.size
    aspect_capa = W / H
    aspect_bg = bg_w / bg_h
    
    if aspect_bg > aspect_capa:
        new_h = H
        new_w = int(aspect_bg * H)
        bg_img = bg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        offset = (new_w - W) // 2
        bg_img = bg_img.crop((offset, 0, offset + W, H))
    else:
        new_w = W
        new_h = int(W / aspect_bg)
        bg_img = bg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        offset = (new_h - H) // 2
        bg_img = bg_img.crop((0, offset, W, offset + H))
    img = bg_img
else:
    img = Image.new("RGBA", (W, H), c_soil_dark)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        if t < 0.2: # Topo verde (ar/vegetação)
            tr = t / 0.2
            r = int(c_vegetation[0]*(1-tr) + c_soil_core[0]*tr)
            g = int(c_vegetation[1]*(1-tr) + c_soil_core[1]*tr)
            b = int(c_vegetation[2]*(1-tr) + c_soil_core[2]*tr)
        else: # Solo e subsolo
            tr = (t - 0.2) / 0.8
            r = int(c_soil_core[0]*(1-tr) + c_soil_dark[0]*tr)
            g = int(c_soil_core[1]*(1-tr) + c_soil_dark[1]*tr)
            b = int(c_soil_core[2]*(1-tr) + c_soil_dark[2]*tr)
        draw.line([(0, y), (W, y)], fill=(r,g,b,255))


# 2. Camadas do solo estilizadas
np.random.seed(101)
layer_img = Image.new("RGBA", (W, H), (0,0,0,0))
layer_draw = ImageDraw.Draw(layer_img)

for i in range(5):
    y_base = 400 + i * 250
    pts = [(0, H), (0, y_base)]
    for x in range(0, W + 100, 50):
        amp = max(20, 80 - i*10)
        y = y_base + math.sin(x * 0.005 + i) * amp + math.cos(x * 0.01) * 30
        pts.append((x, y))
    pts.append((W, y_base))
    pts.append((W, H))
    
    alpha = 40 - i*5
    # tom ligeiramente mais escuro a cada perfil
    layer_draw.polygon(pts, fill=(20, 10, 5, alpha))
img = Image.alpha_composite(img, layer_img)

# 3. Raízes de Bioengenharia
roots_img = Image.new("RGBA", (W, H), (0,0,0,0))
r_draw = ImageDraw.Draw(roots_img)

def draw_root(x, y, angle, length, thickness, depth):
    if depth == 0 or thickness < 1: return
    x_end = x + math.cos(angle) * length
    y_end = y + math.sin(angle) * length
    # cor da raiz baseada na profundidade e espessura
    clr = (c_acc[0], c_acc[1], c_acc[2], max(30, int(80 + thickness*15)))
    r_draw.line([(x, y), (x_end, y_end)], fill=clr, width=int(thickness))
    
    # bifurcação
    if random.random() < 0.7:
        a_offset = random.uniform(0.2, 0.6)
        draw_root(x_end, y_end, angle + a_offset, length * 0.7, thickness * 0.6, depth - 1)
        a_offset2 = random.uniform(0.2, 0.6)
        draw_root(x_end, y_end, angle - a_offset2, length * 0.7, thickness * 0.6, depth - 1)
    else:
        a_offset = random.uniform(-0.3, 0.3)
        draw_root(x_end, y_end, angle + a_offset, length * 0.9, thickness * 0.8, depth - 1)

for _ in range(8):  # grandes sistemas isolados
    sx = random.randint(100, W - 100)
    draw_root(sx, 300, math.pi/2 + random.uniform(-0.2, 0.2), 150, 8, 7)

roots_img = roots_img.filter(ImageFilter.GaussianBlur(radius=0.5))
img = Image.alpha_composite(img, roots_img)

# Área escura para leitura
ov = Image.new("RGBA", (W, H), (0,0,0,0))
ov_draw = ImageDraw.Draw(ov)
ov_draw.rectangle([0, 0, W, H], fill=(20, 15, 5, 80)) # Overlay geral amarelado/amarronzado sutil

for y in range(0, 450):
    alpha = int(220 * (1 - y / 450))
    ov_draw.line([(0, y), (W, y)], fill=(15, 10, 5, alpha))

for y in range(1200, H):
    t = (y - 1200) / (H - 1200)
    alpha = int(230 * t)
    ov_draw.line([(0, y), (W, y)], fill=(10, 5, 0, alpha))
img = Image.alpha_composite(img, ov)

# 4. Textos
draw = ImageDraw.Draw(img)
font_t = get_font("calibri", 110, bold=True)
font_st = get_font("calibri", 46)
font_a = get_font("calibri", 54, bold=True)
font_i = get_font("calibri", 36)
font_s = get_font("calibri", 30)

def draw_spaced(draw, txt, xc, y, f, fill, sp):
    cw = [f.getbbox(c)[2]-f.getbbox(c)[0] for c in txt]
    tw = sum(cw) + sp*(len(txt)-1)
    x = xc - tw//2
    for c, w in zip(txt, cw):
        draw.text((x,y), c, font=f, fill=fill)
        x += w + sp

font_k = get_font("calibri", 42, bold=True)
draw_spaced(draw, "SOLUÇÕES BASEADAS NA NATUREZA", W//2, 55, font_k, c_light_green, 6)
draw_spaced(draw, "BIOENGENHARIA", W//2, 120, font_t, WHITE, 12)
draw_spaced(draw, "DE ÁGUA E SOLO", W//2, 230, font_t, c_light_green, 12)

draw.line([(W//2 - 300, 365), (W//2 + 300, 365)], fill=(c_light_green[0], c_light_green[1], c_light_green[2], 150), width=2)
# Subtítulo na box
sub_bg = Image.new("RGBA", (W, 140), (0,0,0,0))
ImageDraw.Draw(sub_bg).rounded_rectangle([W//2-500, 5, W//2+500, 135], radius=15, fill=(5,15,10, 180))
img.paste(Image.alpha_composite(Image.new("RGBA", (W, 140), (0,0,0,0)), sub_bg), (0, 395), sub_bg)
draw = ImageDraw.Draw(img)

def center_t(draw, text, y, font, fill):
    bb = font.getbbox(text)
    draw.text(((W-(bb[2]-bb[0]))//2, y), text, font=font, fill=fill)

center_t(draw, "Fundamentos, Técnicas e Protocolos", 410, font_st, WHITE)
center_t(draw, "para Regiões Tropicais", 465, font_st, WHITE)

# Organizadores e detalhes em baixo
font_org = get_font("calibri", 44, bold=True)
font_lbl = get_font("calibri", 28)

draw.line([(W//2 - 350, 1375), (W//2 + 350, 1375)], fill=c_light_green+(120,), width=2)
draw_spaced(draw, "ORGANIZADORES", W//2, 1400, font_lbl, c_light_green, 5)
center_t(draw, "Luiz Diego Vidal Santos", 1455, font_org, WHITE)
center_t(draw, "Francisco Sandro Rodrigues Holanda", 1512, font_org, WHITE)
center_t(draw, "Emersson Guedes da Silva", 1569, font_org, WHITE)
center_t(draw, "UEFS  •  UFS", 1640, font_i, SUBTLE)
center_t(draw, "2026  •  CC BY-NC-SA 4.0", 1700, font_s, SUBTLE)

# Salvar
out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img", "capa_bioengenharia_de_solos.png"))
final = Image.new("RGB", img.size, (0,0,0))
final.paste(img, mask=img.split()[3])
final.save(out, "PNG", dpi=(DPI, DPI))
print(f"Salvo: {out}")
