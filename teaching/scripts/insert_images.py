"""Insert image references into QMD lesson files."""
import re
import os

BASE = r"aulas\analise_paisagem\aulas"

# Each entry: (lesson_folder, qmd_filename, search_pattern, image_insert)
# search_pattern: unique text AFTER which image will be inserted
# image_insert: the markdown image reference to add

INSERTIONS = [
    # === ecologia_paisagem ===
    ("ecologia_paisagem", "ecologia_paisagem.qmd",
     "## A paisagem como mosaico {.smaller-text}",
     "\n![Modelo matriz-mancha-corredor em paisagem real — vista aérea](img/matriz_mancha_corredor.jpg){width=\"90%\" fig-align=\"center\"}\n"),

    ("ecologia_paisagem", "ecologia_paisagem.qmd",
     "## Efeito de borda {.smaller-text}",
     "\n![Efeito de borda em fragmento florestal](img/efeito_borda.jpg){width=\"80%\" fig-align=\"center\"}\n"),

    ("ecologia_paisagem", "ecologia_paisagem.qmd",
     "## Corredores: tipos e funções {.smaller-text}",
     "\n![Corredor ecológico — mata ciliar conectando fragmentos](img/corredor_ecologico.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("ecologia_paisagem", "ecologia_paisagem.qmd",
     "## Fragmentação: o problema central {.smaller-text}",
     "\n![Fragmentação florestal — vista aérea de desmatamento progressivo](img/fragmentacao_florestal.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === cartografia_tematica ===
    ("cartografia_tematica", "cartografia_tematica.qmd",
     "## Mapa hipsométrico e de declividade {.smaller-text}",
     "\n![Exemplo de mapa hipsométrico com gradação de cores por altitude](img/mapa_hipsometrico.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("cartografia_tematica", "cartografia_tematica.qmd",
     "## Mapa de drenagem e bacias hidrográficas {.smaller-text}",
     "\n![Padrão de drenagem dendrítico](img/padroes_drenagem.jpg){width=\"70%\" fig-align=\"center\"}\n"),

    ("cartografia_tematica", "cartografia_tematica.qmd",
     "## Mapa de uso e cobertura da terra {.smaller-text}",
     "\n![Mapa temático de uso e cobertura da terra](img/mapa_uso_cobertura.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === interpretacao_visual ===
    ("interpretacao_visual", "interpretacao_visual.qmd",
     "## Tonalidade e cor {.smaller-text}",
     "\n![Imagem de satélite Landsat com diferentes tonalidades e coberturas](img/imagem_satelite_cores.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("interpretacao_visual", "interpretacao_visual.qmd",
     "## Textura, forma e padrão {.smaller-text}",
     "\n![Diferentes texturas em vista aérea: urbano denso vs. floresta vs. água](img/textura_superficies.jpg){width=\"80%\" fig-align=\"center\"}\n"),

    # === sensoriamento_remoto_fundamentos ===
    ("sensoriamento_remoto_fundamentos", "sensoriamento_remoto_fundamentos.qmd",
     "## Bandas espectrais do Sentinel-2 {.smaller-text}",
     "\n![Bandas espectrais do Sentinel-2](img/sentinel2_bandas.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === dominios_paisagens_tropicais ===
    ("dominios_paisagens_tropicais", "dominios_paisagens_tropicais.qmd",
     "## Os Domínios Morfoclimáticos {.smaller-text}",
     "\n![Mapa dos domínios morfoclimáticos / biomas do Brasil](img/dominios_morfoclimaticos.jpg){width=\"60%\" fig-align=\"center\"}\n"),

    ("dominios_paisagens_tropicais", "dominios_paisagens_tropicais.qmd",
     "## Domínio das Caatingas e o Semiárido Baiano {.smaller-text}",
     "\n![Vegetação da Caatinga no semiárido nordestino](img/caatinga_vegetacao.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === fluxos_fragmentacao_resiliencia ===
    ("fluxos_fragmentacao_resiliencia", "fluxos_fragmentacao_resiliencia.qmd",
     "## Estágios da fragmentação {.smaller-text}",
     "\n![Estágios da fragmentação florestal na Europa](img/estagios_fragmentacao.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("fluxos_fragmentacao_resiliencia", "fluxos_fragmentacao_resiliencia.qmd",
     "## Resiliência da paisagem {.smaller-text}",
     "\n![Paisagem resiliente — mosaico heterogêneo e conectado](img/paisagem_resiliente.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === sensoriamento_remoto_mudancas ===
    ("sensoriamento_remoto_mudancas", "sensoriamento_remoto_mudancas.qmd",
     "## A paisagem muda: como detectar?",
     "\n![Série temporal de desmatamento na Bolívia — imagens de satélite](img/serie_temporal_desmatamento.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === sensoriamento_remoto_avancado ===
    ("sensoriamento_remoto_avancado", "sensoriamento_remoto_avancado.qmd",
     "## Como funciona o LiDAR {.smaller-text}",
     "\n![LiDAR — modelo digital de superfície e estrutura florestal](img/lidar_modelo_dossel.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("sensoriamento_remoto_avancado", "sensoriamento_remoto_avancado.qmd",
     "## Princípios do SAR {.smaller-text}",
     "\n![Imagem SAR — radar de abertura sintética](img/sar_radar.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("sensoriamento_remoto_avancado", "sensoriamento_remoto_avancado.qmd",
     "## A revolução dos drones {.smaller-text}",
     "\n![RPA (drone) — fotografia aérea de alta resolução](img/drone_rpa.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    # === unidades_paisagem ===
    ("unidades_paisagem", "unidades_paisagem.qmd",
     "### Método 1: Sobreposição ponderada",
     "\n![Sobreposição de camadas temáticas em SIG](img/sobreposicao_camadas.jpg){width=\"70%\" fig-align=\"center\"}\n"),

    # === percepcao_valoracao_paisagem ===
    ("percepcao_valoracao_paisagem", "percepcao_valoracao_paisagem.qmd",
     "## Paisagem: objeto ou experiência? {.smaller-text}",
     "\n![Ponto de vista elevado sobre a paisagem — percepção e contemplação](img/perspectiva_paisagem.jpg){width=\"85%\" fig-align=\"center\"}\n"),

    ("percepcao_valoracao_paisagem", "percepcao_valoracao_paisagem.qmd",
     "## Paisagem Cultural: marcos institucionais {.smaller-text}",
     "\n![Paisagem cultural — patrimônio e identidade](img/paisagem_cultural.jpg){width=\"85%\" fig-align=\"center\"}\n"),
]


def insert_after_header(filepath, header_pattern, image_markdown):
    """Insert image markdown right after a section header line."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if image already inserted
    img_file = re.search(r'img/(\S+\.jpg)', image_markdown)
    if img_file and img_file.group(1) in content:
        return "SKIP (already present)"

    # Find the header and insert after it
    idx = content.find(header_pattern)
    if idx == -1:
        return f"NOT FOUND: '{header_pattern[:50]}...'"

    # Insert after the header line
    end_of_header = content.index("\n", idx) + 1
    new_content = content[:end_of_header] + image_markdown + content[end_of_header:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return "OK"


def main():
    ok = 0
    skip = 0
    fail = 0

    for lesson, qmd, header, img_md in INSERTIONS:
        filepath = os.path.join(BASE, lesson, qmd)
        if not os.path.exists(filepath):
            print(f"[ERRO] Arquivo não encontrado: {filepath}")
            fail += 1
            continue

        result = insert_after_header(filepath, header, img_md)
        status = result.split()[0]
        if status == "OK":
            ok += 1
            print(f"[OK] {lesson}: inserida imagem após '{header[:40]}...'")
        elif status == "SKIP":
            skip += 1
            print(f"[SKIP] {lesson}: imagem já presente")
        else:
            fail += 1
            print(f"[FALHA] {lesson}: {result}")

    print(f"\n=== {ok} inseridas | {skip} já existentes | {fail} falhas ===")


if __name__ == "__main__":
    main()
