#!/usr/bin/env python3
"""
Download todas as imagens pendentes do IMAGENS_PENDENTES.md (rodada 2).

Fontes:
  - Wikimedia Commons (CC) — imagens técnicas confirmadas
  - Pexels (Pexels License — livre para uso) — imagens decorativas de cabeçalhos

Cada entrada: (url, destino_relativo)
"""

import os
import time
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AcademicProject/1.0"
}

# ============================================================
# MAPEAMENTO COMPLETO DE IMAGENS
# ============================================================

DOWNLOADS = [
    # -------------------------------------------------------
    # GRUPO 1 — Modelagem 3D raízes (Wikimedia)
    # -------------------------------------------------------
    # #1 vetiver_perfil_raiz.jpg — Vetiveria zizanoides (CC-BY-SA 2.0/3.0, David Monniaux)
    (
        "https://upload.wikimedia.org/wikipedia/commons/2/23/Vetiveria_zizanoides_dsc07810.jpg",
        "aulas/bioengenharia_de_solos/aulas/modelagem_3d_raizes/img/raizes_vetiver/vetiver_perfil_raiz.jpg",
    ),
    # #2 vetiver_escala.jpg — Reusa a mesma imagem de vetiver (não encontrada imagem específica com escala)
    (
        "https://upload.wikimedia.org/wikipedia/commons/2/23/Vetiveria_zizanoides_dsc07810.jpg",
        "aulas/bioengenharia_de_solos/aulas/modelagem_3d_raizes/img/raizes_vetiver/vetiver_escala.jpg",
    ),
    # #3 vetiver_nuvem_pontos.png — Nuvem de pontos LiDAR (CC-BY 4.0, Daniel L. Lu)
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Ouster_OS1-64_lidar_point_cloud_of_intersection_of_Folsom_and_Dore_St%2C_San_Francisco.png/1200px-Ouster_OS1-64_lidar_point_cloud_of_intersection_of_Folsom_and_Dore_St%2C_San_Francisco.png",
        "aulas/bioengenharia_de_solos/aulas/modelagem_3d_raizes/img/raizes_vetiver/vetiver_nuvem_pontos.png",
    ),
    # #4 vetiver_malha_3d.png — Malha 3D wireframe de Stanford Bunny (CC-BY-SA 4.0, Wikimedia)
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Stanford_bunny_mesh.png/800px-Stanford_bunny_mesh.png",
        "aulas/bioengenharia_de_solos/aulas/modelagem_3d_raizes/img/raizes_vetiver/vetiver_malha_3d.png",
    ),
    # #5 vetiver_corte_rar.png — Corte transversal de raiz (CC-BY-SA 4.0, TCdeOLiveira)
    (
        "https://upload.wikimedia.org/wikipedia/commons/8/8d/Ruscus_hypophyllum_root_-_cross_section_detail.jpg",
        "aulas/bioengenharia_de_solos/aulas/modelagem_3d_raizes/img/raizes_vetiver/vetiver_corte_rar.png",
    ),

    # -------------------------------------------------------
    # GRUPO 3 — Vida Útil Biotêxteis (Wikimedia + Pexels)
    # -------------------------------------------------------
    # #12 tear_fibras.jpg — Handloom (CC-BY-SA 4.0, Rishikachauhan1)
    (
        "https://upload.wikimedia.org/wikipedia/commons/9/9d/Handloom.jpg",
        "aulas/geotexteis/aulas/vida_util_biotexteis/img/tear_fibras.jpg",
    ),
    # #13 talude_biotextil.jpg — Slope erosion control (Pexels 1068523, landscape/land)
    (
        "https://images.pexels.com/photos/1534057/pexels-photo-1534057.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/geotexteis/aulas/vida_util_biotexteis/img/talude_biotextil.jpg",
    ),
    # #14 camara_degradacao.png — UV degradation test chamber (CC-BY-SA 3.0, Cjp24)
    (
        "https://upload.wikimedia.org/wikipedia/commons/2/20/UV_degradation_test_chamber.jpg",
        "aulas/geotexteis/aulas/vida_util_biotexteis/img/camara_degradacao.png",
    ),
    # #15 coleta_campo.png — Soil sampling in field (CC-BY-SA 2.0, Gary Rogers)
    (
        "https://upload.wikimedia.org/wikipedia/commons/2/2b/Soil_sampling_in_field_East_of_Upholland_Road_-_geograph.org.uk_-_5739011.jpg",
        "aulas/geotexteis/aulas/vida_util_biotexteis/img/coleta_campo.png",
    ),
    # #16 maquina_universal.png — Tensile testing on coir composite (CC0, Kerina yin)
    (
        "https://upload.wikimedia.org/wikipedia/commons/2/22/Tensile_testing_on_a_coir_composite.jpg",
        "aulas/geotexteis/aulas/vida_util_biotexteis/img/maquina_universal.png",
    ),

    # -------------------------------------------------------
    # GRUPO 4 — Ciência PI Tema 01 (Pexels — decorativas)
    # -------------------------------------------------------
    # #17 intro.jpg — Lâmpada/inovação (Pexels 355948 - lightbulb on chalkboard)
    (
        "https://images.pexels.com/photos/355948/pexels-photo-355948.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 01 - Gestao da Inovacao Tecnologica/tema01_apresentacao/Figuras/intro.jpg",
    ),
    # #18 iso56002.jpg — Checklist/norma (Pexels 416322 - notebook checklist)
    (
        "https://images.pexels.com/photos/416322/pexels-photo-416322.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 01 - Gestao da Inovacao Tecnologica/tema01_apresentacao/Figuras/iso56002.jpg",
    ),
    # #19 processo.jpg — Processo/fluxograma (Pexels 1181311 - flowchart whiteboard)
    (
        "https://images.pexels.com/photos/1181311/pexels-photo-1181311.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 01 - Gestao da Inovacao Tecnologica/tema01_apresentacao/Figuras/processo.jpg",
    ),
    # #20 avaliacao.jpg — Análise de gráficos (Pexels 590041 - hand analyzing graphs)
    (
        "https://images.pexels.com/photos/590041/pexels-photo-590041.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 01 - Gestao da Inovacao Tecnologica/tema01_apresentacao/Figuras/avaliacao.jpg",
    ),
    # #21 conclusao.jpg — Equipe colaborando (Pexels 3184299 - professionals brainstorming)
    (
        "https://images.pexels.com/photos/3184299/pexels-photo-3184299.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 01 - Gestao da Inovacao Tecnologica/tema01_apresentacao/Figuras/conclusao.jpg",
    ),

    # -------------------------------------------------------
    # GRUPO 5 — Ciência PI Tema 05 (Wikimedia + Pexels)
    # Nota: #25 trl_nasa.png e #27 stage_gate_process.png já baixadas
    # -------------------------------------------------------
    # #22 iso56005.jpg — Documento/norma (Pexels 6913206 - blackboard business notes)
    (
        "https://images.pexels.com/photos/6913206/pexels-photo-6913206.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/iso56005.jpg",
    ),
    # #23 gestao_pi_56005.png — Post-its/brainstorming (Pexels 7793704 - sticky notes glass wall)
    (
        "https://images.pexels.com/photos/7793704/pexels-photo-7793704.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/gestao_pi_56005.png",
    ),
    # #24 oslo.png — Manual/documento (Pexels 5439449 - man reading contract)
    (
        "https://images.pexels.com/photos/5439449/pexels-photo-5439449.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/oslo.png",
    ),
    # #26 technology_readiness_levels.png — NASA TRL Meter (CC-BY-SA 4.0, Wikimedia)
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/NASA_TRL_Meter_corrected_from_Hari_Seldon.svg/800px-NASA_TRL_Meter_corrected_from_Hari_Seldon.svg.png",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/technology_readiness_levels.png",
    ),
    # #28 innovation_project_management.png — Parede de ideias (Pexels 212286 - man looking at wall)
    (
        "https://images.pexels.com/photos/212286/pexels-photo-212286.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/innovation_project_management.png",
    ),
    # #29 capacidade_absortiva.png — Reunião com gráficos (Pexels 7876381 - person holding charts)
    (
        "https://images.pexels.com/photos/7876381/pexels-photo-7876381.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/capacidade_absortiva.png",
    ),
    # #30 dynamic_capabilities.png — Xadrez Robô/Estratégia (Pexels 8438921 - chess robot man)
    (
        "https://images.pexels.com/photos/8438921/pexels-photo-8438921.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/dynamic_capabilities.png",
    ),
    # #31 patent_development_flow.png — Proceso 5 fases Stage-Gate (CC-BY-SA 4.0, Wikimedia)
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Proceso_5_fases.svg/960px-Proceso_5_fases.svg.png",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/patent_development_flow.png",
    ),
    # #32 gestao_inovacao_modelos.png — Quadro branco (Pexels 7369 - man writing flowchart)
    (
        "https://images.pexels.com/photos/7369/startup-photos.jpg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras/gestao_inovacao_modelos.png",
    ),

    # -------------------------------------------------------
    # GRUPO 6 — Ciência PI Tema 06 (Pexels — decorativas)
    # -------------------------------------------------------
    # #33 intro.jpg — Escritório tech (Pexels 1714208 - dual monitor desk)
    (
        "https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 06 - Valoracao de ativos/tema06_apresentacao/Figuras/intro.jpg",
    ),
    # #34 metodos.jpg — Gráficos em mesa (Pexels 9304917 - charts clipboard top view)
    (
        "https://images.pexels.com/photos/9304917/pexels-photo-9304917.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 06 - Valoracao de ativos/tema06_apresentacao/Figuras/metodos.jpg",
    ),
    # #35 comercializacao.jpg — Reunião negócios (Pexels 7075 - coworkers looking at laptop)
    (
        "https://images.pexels.com/photos/7075/people-office-group-team.jpg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 06 - Valoracao de ativos/tema06_apresentacao/Figuras/comercializacao.jpg",
    ),
    # #36 nits.jpg — Laboratório/cientistas (Pexels 8439008 - scientists robotic arm)
    (
        "https://images.pexels.com/photos/8439008/pexels-photo-8439008.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 06 - Valoracao de ativos/tema06_apresentacao/Figuras/nits.jpg",
    ),
    # #37 conclusao.jpg — Equipe discutindo (Pexels 3153198 - woman sharing presentation)
    (
        "https://images.pexels.com/photos/3153198/pexels-photo-3153198.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "aulas/ciencia_pi/SLIDES_QUARTO/Tema 06 - Valoracao de ativos/tema06_apresentacao/Figuras/conclusao.jpg",
    ),
]


def download(url: str, dest: str, retries: int = 3) -> bool:
    """Baixa url para dest com retry e backoff exponencial."""
    full = os.path.join(BASE, dest.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if os.path.exists(full):
        print(f"  [SKIP] Já existe: {dest}")
        return True
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            with open(full, "wb") as f:
                f.write(data)
            size_kb = len(data) / 1024
            print(f"  [OK]   {dest}  ({size_kb:.0f} KB)")
            return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            wait = 5 * attempt
            print(f"  [ERRO] Tentativa {attempt}/{retries} — {e} — Aguardando {wait}s...")
            time.sleep(wait)
    print(f"  [FALHA] Não conseguiu baixar: {dest}")
    return False


def main():
    total = len(DOWNLOADS)
    ok = 0
    fail = 0
    print(f"\n{'='*60}")
    print(f"  Download de {total} imagens pendentes")
    print(f"{'='*60}\n")

    for i, (url, dest) in enumerate(DOWNLOADS, 1):
        print(f"[{i}/{total}] Baixando...")
        if download(url, dest):
            ok += 1
        else:
            fail += 1
        # Respeitar rate limits
        if i < total:
            time.sleep(2)

    print(f"\n{'='*60}")
    print(f"  Concluído: {ok} OK, {fail} falhas")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
