"""
Download images from Wikimedia Commons for Análise da Paisagem lessons.
Uses the Wikimedia Commons API to find CC/public domain images.
"""
import requests
import os
import time
import json
import re

BASE = r"aulas\analise_paisagem\aulas"
API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "AcademicPresentation/1.0 (educational use)"}


def search_commons(query, limit=3):
    """Search Wikimedia Commons for images matching query."""
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
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, page in pages.items():
            info = page.get("imageinfo", [{}])[0]
            meta = info.get("extmetadata", {})
            license_val = meta.get("LicenseShortName", {}).get("value", "")
            results.append({
                "title": page.get("title", ""),
                "url": info.get("thumburl", info.get("url", "")),
                "width": info.get("thumbwidth", info.get("width", 0)),
                "height": info.get("thumbheight", info.get("height", 0)),
                "license": license_val,
                "mime": info.get("mime", ""),
                "desc": meta.get("ImageDescription", {}).get("value", "")[:100],
            })
        return results
    except Exception as e:
        print(f"  [ERRO] Busca falhou para '{query}': {e}")
        return []


def download_image(url, filepath):
    """Download image from URL to filepath."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  [OK] {os.path.basename(filepath)} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  [ERRO] Download falhou: {e}")
        return False


# Define images needed per lesson
LESSONS = {
    "ecologia_paisagem": [
        {
            "query": "landscape ecology matrix patch corridor aerial",
            "filename": "matriz_mancha_corredor.jpg",
            "alt": "Modelo matriz-mancha-corredor em paisagem real",
        },
        {
            "query": "forest fragmentation aerial view tropical",
            "filename": "fragmentacao_florestal.jpg",
            "alt": "Fragmentação florestal vista aérea",
        },
        {
            "query": "riparian forest corridor gallery forest stream",
            "filename": "corredor_ecologico.jpg",
            "alt": "Corredor ecológico — mata ciliar conectando fragmentos",
        },
        {
            "query": "edge effect forest fragment border",
            "filename": "efeito_borda.jpg",
            "alt": "Efeito de borda em fragmento florestal",
        },
    ],
    "cartografia_tematica": [
        {
            "query": "hypsometric map altitude topographic",
            "filename": "mapa_hipsometrico.jpg",
            "alt": "Exemplo de mapa hipsométrico com gradação de cores",
        },
        {
            "query": "drainage pattern dendritic trellis radial",
            "filename": "padroes_drenagem.jpg",
            "alt": "Padrões de drenagem: dendrítico, treliça, radial",
        },
        {
            "query": "land use land cover map classification thematic",
            "filename": "mapa_uso_cobertura.jpg",
            "alt": "Mapa temático de uso e cobertura da terra",
        },
        {
            "query": "watershed drainage basin boundary divide map",
            "filename": "bacia_hidrografica.jpg",
            "alt": "Bacia hidrográfica com divisores de água",
        },
    ],
    "interpretacao_visual": [
        {
            "query": "satellite image land cover Sentinel Landsat color",
            "filename": "imagem_satelite_cores.jpg",
            "alt": "Imagem de satélite com diferentes tonalidades",
        },
        {
            "query": "remote sensing texture forest urban smooth rough",
            "filename": "textura_superficies.jpg",
            "alt": "Diferentes texturas em imagem de satélite",
        },
        {
            "query": "spatial pattern urban grid regular dendritic",
            "filename": "padroes_espaciais.jpg",
            "alt": "Padrões espaciais: reticular (urbano) e dendrítico (drenagem)",
        },
    ],
    "sensoriamento_remoto_fundamentos": [
        {
            "query": "electromagnetic spectrum wavelength diagram optical infrared",
            "filename": "espectro_eletromagnetico.jpg",
            "alt": "Espectro eletromagnético — regiões óptica, infravermelha e micro-ondas",
        },
        {
            "query": "Sentinel-2 satellite bands spectral response",
            "filename": "sentinel2_bandas.jpg",
            "alt": "Bandas espectrais do Sentinel-2",
        },
        {
            "query": "false color composite true color satellite Landsat comparison",
            "filename": "composicao_colorida.jpg",
            "alt": "Composição colorida: cor verdadeira vs. falsa cor",
        },
        {
            "query": "NDVI vegetation index map green red",
            "filename": "ndvi_exemplo.jpg",
            "alt": "Índice NDVI — vegetação em gradiente verde-vermelho",
        },
    ],
    "dominios_paisagens_tropicais": [
        {
            "query": "Brazilian biomes map cerrado caatinga amazon atlantic forest",
            "filename": "dominios_morfoclimaticos.jpg",
            "alt": "Mapa dos domínios morfoclimáticos do Brasil",
        },
        {
            "query": "cerrado savanna vegetation Brazil typical",
            "filename": "cerrado_vegetacao.jpg",
            "alt": "Vegetação típica do Cerrado",
        },
        {
            "query": "caatinga semiarid vegetation Brazil northeast dry",
            "filename": "caatinga_vegetacao.jpg",
            "alt": "Vegetação da Caatinga no semiárido nordestino",
        },
        {
            "query": "Amazon rainforest canopy tropical forest aerial",
            "filename": "floresta_amazonica.jpg",
            "alt": "Floresta Amazônica — dossel contínuo tropical",
        },
        {
            "query": "Atlantic forest Mata Atlantica Brazil remnant",
            "filename": "mata_atlantica.jpg",
            "alt": "Remanescente de Mata Atlântica",
        },
    ],
    "fluxos_fragmentacao_resiliencia": [
        {
            "query": "landscape fragmentation stages perforation dissection",
            "filename": "estagios_fragmentacao.jpg",
            "alt": "Estágios da fragmentação (Forman): perfuração, dissecção, fragmentação",
        },
        {
            "query": "habitat connectivity wildlife corridor landscape",
            "filename": "conectividade_habitat.jpg",
            "alt": "Conectividade entre habitats via corredores",
        },
        {
            "query": "resilient landscape heterogeneous connected mosaic",
            "filename": "paisagem_resiliente.jpg",
            "alt": "Paisagem resiliente: heterogênea e conectada",
        },
    ],
    "sensoriamento_remoto_mudancas": [
        {
            "query": "deforestation time series satellite before after",
            "filename": "serie_temporal_desmatamento.jpg",
            "alt": "Série temporal de desmatamento em imagens de satélite",
        },
        {
            "query": "NDVI change detection vegetation difference map",
            "filename": "ndvi_mudanca.jpg",
            "alt": "Mapa de diferença de NDVI — ganho e perda de vegetação",
        },
        {
            "query": "land cover change detection comparison map",
            "filename": "deteccao_mudancas.jpg",
            "alt": "Detecção de mudanças em cobertura da terra",
        },
    ],
    "sensoriamento_remoto_avancado": [
        {
            "query": "LiDAR point cloud canopy height model forest",
            "filename": "lidar_modelo_dossel.jpg",
            "alt": "LiDAR — modelo de altura do dossel (CHM)",
        },
        {
            "query": "SAR synthetic aperture radar flood inundation image",
            "filename": "sar_radar.jpg",
            "alt": "Imagem SAR mostrando áreas inundáveis",
        },
        {
            "query": "drone UAV aerial photography survey mapping",
            "filename": "drone_rpa.jpg",
            "alt": "RPA (drone) em operação de mapeamento",
        },
    ],
    "unidades_paisagem": [
        {
            "query": "landscape units map geomorphology delineation",
            "filename": "mapa_unidades_paisagem.jpg",
            "alt": "Mapa de unidades de paisagem delimitadas",
        },
        {
            "query": "map overlay spatial analysis GIS layers",
            "filename": "sobreposicao_camadas.jpg",
            "alt": "Sobreposição de camadas temáticas em SIG",
        },
    ],
    "percepcao_valoracao_paisagem": [
        {
            "query": "landscape viewpoint observation perspective scenic",
            "filename": "perspectiva_paisagem.jpg",
            "alt": "Ponto de vista elevado sobre a paisagem",
        },
        {
            "query": "cultural landscape heritage monument UNESCO",
            "filename": "paisagem_cultural.jpg",
            "alt": "Paisagem cultural — patrimônio e identidade",
        },
    ],
}


def main():
    total = sum(len(v) for v in LESSONS.values())
    downloaded = 0
    failed = 0

    print(f"=== Download de {total} imagens para {len(LESSONS)} aulas ===\n")

    for lesson, images in LESSONS.items():
        lesson_dir = os.path.join(BASE, lesson, "img")
        os.makedirs(lesson_dir, exist_ok=True)
        print(f"\n--- {lesson} ({len(images)} imagens) ---")

        for img in images:
            filepath = os.path.join(lesson_dir, img["filename"])

            # Skip if already downloaded
            if os.path.exists(filepath):
                print(f"  [SKIP] {img['filename']} já existe")
                downloaded += 1
                continue

            print(f"  Buscando: {img['query'][:50]}...")
            results = search_commons(img["query"], limit=3)

            if not results:
                print(f"  [AVISO] Nenhum resultado para '{img['query'][:40]}...'")
                failed += 1
                continue

            # Pick first result with acceptable license
            chosen = None
            for r in results:
                if r["url"] and r["width"] >= 400:
                    chosen = r
                    break
            if not chosen:
                chosen = results[0] if results else None

            if chosen and chosen["url"]:
                print(f"  Baixando: {chosen['title'][:60]} [{chosen['license']}]")
                if download_image(chosen["url"], filepath):
                    downloaded += 1
                else:
                    failed += 1
            else:
                print(f"  [AVISO] Sem URL válida")
                failed += 1

            time.sleep(1)  # Rate limiting

    print(f"\n=== Resultado: {downloaded}/{total} baixadas, {failed} falhas ===")

    # Save manifest
    manifest = {}
    for lesson, images in LESSONS.items():
        manifest[lesson] = []
        for img in images:
            filepath = os.path.join(BASE, lesson, "img", img["filename"])
            manifest[lesson].append({
                "filename": img["filename"],
                "alt": img["alt"],
                "exists": os.path.exists(filepath),
            })

    with open(os.path.join(BASE, "imagens_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("Manifesto salvo em imagens_manifest.json")


if __name__ == "__main__":
    main()
