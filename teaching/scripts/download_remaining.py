"""Download remaining images with longer delays to avoid rate limiting."""
import requests
import os
import time

BASE = r"aulas\analise_paisagem\aulas"
HEADERS = {"User-Agent": "AcademicPresentation/1.0 (educational; luiz.vidal@uefs.br)"}

# Direct URLs from Wikimedia Commons (found in previous search)
DIRECT_URLS = [
    ("interpretacao_visual", "padroes_espaciais.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/A_portion_of_the_Washington_DC_urban_area_LOC_2007625044.jpg/1280px-A_portion_of_the_Washington_DC_urban_area_LOC_2007625044.jpg"),
    ("dominios_paisagens_tropicais", "dominios_morfoclimaticos.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Biomes_of_Brazil.png/800px-Biomes_of_Brazil.png"),
    ("dominios_paisagens_tropicais", "cerrado_vegetacao.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Cerrado_em_Gouveia.jpg/1280px-Cerrado_em_Gouveia.jpg"),
    ("dominios_paisagens_tropicais", "caatinga_vegetacao.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Brazil_-_Caatinga_land_use_change_1985-2024_-_MapBiomas.gif/800px-Brazil_-_Caatinga_land_use_change_1985-2024_-_MapBiomas.gif"),
    ("dominios_paisagens_tropicais", "floresta_amazonica.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/AMAZON_RAINFOREST_RIVER_AND_JUNGLE_-_panoramio.jpg/1280px-AMAZON_RAINFOREST_RIVER_AND_JUNGLE_-_panoramio.jpg"),
    ("fluxos_fragmentacao_resiliencia", "estagios_fragmentacao.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Fragmentation_foresti%C3%A8reRapportUE2013.jpg/1280px-Fragmentation_foresti%C3%A8reRapportUE2013.jpg"),
    ("fluxos_fragmentacao_resiliencia", "paisagem_resiliente.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Disruption.jpg/960px-Disruption.jpg"),
    ("sensoriamento_remoto_mudancas", "serie_temporal_desmatamento.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/1/19/Bolivia-Deforestation-EO.JPG"),
    ("sensoriamento_remoto_mudancas", "ndvi_mudanca.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Map_NDVI_Lublin.jpg/1280px-Map_NDVI_Lublin.jpg"),
    ("sensoriamento_remoto_avancado", "lidar_modelo_dossel.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/02025_Site_1%2C_Manasterzec_%28Sobie%C5%84_Castle%29%2C_Lesko_Forest_District%2C_lidar.png/800px-02025_Site_1%2C_Manasterzec_%28Sobie%C5%84_Castle%29%2C_Lesko_Forest_District%2C_lidar.png"),
    ("sensoriamento_remoto_avancado", "sar_radar.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/First_Tests_for_the_VERITAS%27_Venus_Interferometric_Synthetic_Aperture_Radar_%28PIA25832%29.jpg/1280px-First_Tests_for_the_VERITAS%27_Venus_Interferometric_Synthetic_Aperture_Radar_%28PIA25832%29.jpg"),
    ("sensoriamento_remoto_avancado", "drone_rpa.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/1_aerial_yangshuo_panorama_2017.jpg/1280px-1_aerial_yangshuo_panorama_2017.jpg"),
    ("unidades_paisagem", "mapa_unidades_paisagem.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Cultural_Landscape_Hierarchy_Map_%2857c99a61-046a-e6f4-70ac-d1a117f76e78%29.jpg/800px-Cultural_Landscape_Hierarchy_Map_%2857c99a61-046a-e6f4-70ac-d1a117f76e78%29.jpg"),
    ("unidades_paisagem", "sobreposicao_camadas.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/1988._Early_aerial_survey_data_digitizing._Forest_Pest_Management._Regional_Office%2C_Portland%2C_Oregon._%2834777418864%29.jpg/800px-1988._Early_aerial_survey_data_digitizing._Forest_Pest_Management._Regional_Office%2C_Portland%2C_Oregon._%2834777418864%29.jpg"),
    ("percepcao_valoracao_paisagem", "perspectiva_paisagem.jpg",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Ayrshire_Landscape_%2C_Approaching_the_viewpoint_pillar_on_Brown_Carrick_Hill_-_geograph.org.uk_-_8012755.jpg/1280px-Ayrshire_Landscape_%2C_Approaching_the_viewpoint_pillar_on_Brown_Carrick_Hill_-_geograph.org.uk_-_8012755.jpg"),
]

ok = 0
fail = 0
for lesson, filename, url in DIRECT_URLS:
    dirpath = os.path.join(BASE, lesson, "img")
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename)

    if os.path.exists(filepath):
        print(f"[SKIP] {lesson}/{filename}")
        ok += 1
        continue

    print(f"[{lesson}] {filename}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        kb = os.path.getsize(filepath) / 1024
        print(f"  [OK] {kb:.0f} KB")
        ok += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        fail += 1

    time.sleep(5)  # 5 second delay to avoid rate limiting

print(f"\n=== {ok} OK / {fail} falhas ===")
