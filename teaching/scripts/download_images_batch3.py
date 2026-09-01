"""Download batch 3 of images for Extensão Rural presentations."""
import urllib.request, os, ssl

img_dir = os.path.join("aulas", "extensao_rural", "aulas", "img")
os.makedirs(img_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

images = [
    (
        "gini_mapa_mundial.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/"
        "2014_Gini_Index_World_Map%2C_income_inequality_distribution_by_country_per_World_Bank.svg/"
        "1280px-2014_Gini_Index_World_Map%2C_income_inequality_distribution_by_country_per_World_Bank.svg.png",
    ),
    (
        "aviao_pulverizacao_nara.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/"
        "CROP_DUSTER_PLANE_AT_WORK_IN_IMPERIAL_VALLEY_-_NARA_-_548884.jpg/"
        "1280px-CROP_DUSTER_PLANE_AT_WORK_IN_IMPERIAL_VALLEY_-_NARA_-_548884.jpg",
    ),
    (
        "paulo_freire_1977.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/be/Paulo_Freire_1977.jpg",
    ),
    (
        "metodo_paulo_freire.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/60/Method_Paulo_Freire.jpg",
    ),
    (
        "desmatamento_mato_grosso.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/b1/DeforestationinBrazil2.jpg",
    ),
    (
        "colheitadeira_mecanizada.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/"
        "Harvest%2C_agriculture%2C_grain%2C_wheat-field%2C_combine_harvester_Fortepan_89614.jpg/"
        "1280px-Harvest%2C_agriculture%2C_grain%2C_wheat-field%2C_combine_harvester_Fortepan_89614.jpg",
    ),
]

headers = {"User-Agent": "Mozilla/5.0 (academic-site-builder/1.0; luiz.vidal@ufs.br)"}

for name, url in images:
    path = os.path.join(img_dir, name)
    if os.path.exists(path):
        print(f"SKIP (exists): {name}")
        continue
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK: {name} ({len(data) // 1024} KB)")
    except Exception as e:
        print(f"FAIL: {name} -> {e}")
