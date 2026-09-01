"""
Download images from Wikimedia Commons - simplified queries.
"""
import requests
import os
import time

BASE = r"aulas\analise_paisagem\aulas"
API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "AcademicPresentation/1.0 (educational use)"}


def search_commons(query, limit=5):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrlimit": limit,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1280,
    }
    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, page in pages.items():
            info = page.get("imageinfo", [{}])[0]
            meta = info.get("extmetadata", {})
            lic = meta.get("LicenseShortName", {}).get("value", "")
            results.append({
                "title": page.get("title", ""),
                "url": info.get("thumburl", info.get("url", "")),
                "width": info.get("thumbwidth", info.get("width", 0)),
                "license": lic,
            })
        return results
    except Exception as e:
        print(f"  [ERRO] {e}")
        return []


def download(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        kb = os.path.getsize(filepath) / 1024
        print(f"  [OK] {os.path.basename(filepath)} ({kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  [ERRO] {e}")
        return False


# Simplified queries - shorter terms
IMAGES = [
    # ecologia_paisagem
    ("ecologia_paisagem", "fragmentacao_florestal.jpg", "deforestation aerial"),
    ("ecologia_paisagem", "corredor_ecologico.jpg", "riparian corridor"),
    ("ecologia_paisagem", "efeito_borda.jpg", "forest edge"),
    ("ecologia_paisagem", "matriz_mancha_corredor.jpg", "landscape mosaic aerial"),
    # cartografia_tematica
    ("cartografia_tematica", "mapa_hipsometrico.jpg", "topographic map elevation"),
    ("cartografia_tematica", "padroes_drenagem.jpg", "drainage pattern"),
    # interpretacao_visual
    ("interpretacao_visual", "imagem_satelite_cores.jpg", "Landsat satellite"),
    ("interpretacao_visual", "textura_superficies.jpg", "aerial urban forest"),
    ("interpretacao_visual", "padroes_espaciais.jpg", "urban grid aerial"),
    # sensoriamento_remoto_fundamentos
    ("sensoriamento_remoto_fundamentos", "composicao_colorida.jpg", "false color Landsat"),
    # dominios_paisagens_tropicais
    ("dominios_paisagens_tropicais", "dominios_morfoclimaticos.jpg", "biomes Brazil map"),
    ("dominios_paisagens_tropicais", "cerrado_vegetacao.jpg", "cerrado vegetation"),
    ("dominios_paisagens_tropicais", "caatinga_vegetacao.jpg", "caatinga Brazil"),
    ("dominios_paisagens_tropicais", "floresta_amazonica.jpg", "Amazon forest aerial"),
    # fluxos_fragmentacao_resiliencia
    ("fluxos_fragmentacao_resiliencia", "estagios_fragmentacao.jpg", "habitat fragmentation"),
    ("fluxos_fragmentacao_resiliencia", "paisagem_resiliente.jpg", "landscape mosaic resilience"),
    # sensoriamento_remoto_mudancas
    ("sensoriamento_remoto_mudancas", "serie_temporal_desmatamento.jpg", "deforestation satellite"),
    ("sensoriamento_remoto_mudancas", "ndvi_mudanca.jpg", "NDVI map"),
    # sensoriamento_remoto_avancado
    ("sensoriamento_remoto_avancado", "lidar_modelo_dossel.jpg", "LiDAR forest"),
    ("sensoriamento_remoto_avancado", "sar_radar.jpg", "SAR radar image"),
    ("sensoriamento_remoto_avancado", "drone_rpa.jpg", "drone survey"),
    # unidades_paisagem
    ("unidades_paisagem", "mapa_unidades_paisagem.jpg", "landscape map units"),
    ("unidades_paisagem", "sobreposicao_camadas.jpg", "GIS overlay layers"),
    # percepcao_valoracao_paisagem
    ("percepcao_valoracao_paisagem", "perspectiva_paisagem.jpg", "landscape viewpoint"),
]

ok = 0
fail = 0
for lesson, filename, query in IMAGES:
    dirpath = os.path.join(BASE, lesson, "img")
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename)

    if os.path.exists(filepath):
        print(f"[SKIP] {lesson}/{filename}")
        ok += 1
        continue

    print(f"[{lesson}] '{query}' -> {filename}")
    results = search_commons(query)

    chosen = None
    for r in results:
        if r["url"] and r["width"] >= 400:
            chosen = r
            break

    if chosen:
        print(f"  Fonte: {chosen['title'][:60]} [{chosen['license']}]")
        if download(chosen["url"], filepath):
            ok += 1
        else:
            fail += 1
    else:
        print(f"  [SEM RESULTADO]")
        fail += 1

    time.sleep(1.5)

print(f"\n=== {ok} OK / {fail} falhas de {len(IMAGES)} imagens ===")
