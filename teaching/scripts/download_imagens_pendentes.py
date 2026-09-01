#!/usr/bin/env python3
"""
Download de imagens pendentes do Wikimedia Commons.
Usa a API do Wikimedia para obter URLs diretas e baixa para as pastas corretas.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import shutil
from pathlib import Path

# Base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Mapeamento: nome no Wikimedia → (nome_local, pasta_destino)
IMAGENS = [
    {
        "wiki_file": "File:Emater_Logo.svg",
        "local_name": "emater_logo.png",
        "dest_dir": "aulas/extensao_rural/aulas/ater_publica_privada/img",
        "thumb_width": 800,  # SVG precisa de thumbnail PNG
        "description": "Logotipo EMATER-MG (CC-BY-SA 4.0)",
    },
    {
        "wiki_file": "File:Cisterna_da_ASA_(In_Piauí).JPG",
        "local_name": "cisterna_asa_semiarido.jpg",
        "dest_dir": "aulas/extensao_rural/aulas/casos_praticos_extensao/img",
        "thumb_width": 1200,
        "description": "Placa do programa de cisternas ASA (CC-BY-SA 3.0 BR)",
    },
    {
        "wiki_file": "File:Cisternas_na_área_rural_da_Bahia_(16077327289).jpg",
        "local_name": "cisterna_placa_serrinha_ba.jpg",
        "dest_dir": "aulas/extensao_rural/aulas/casos_praticos_extensao/img",
        "thumb_width": 1200,
        "description": "Cisterna de placa em Serrinha/BA (CC-BY-SA 2.0, MDS/Wikimedia)",
    },
    {
        "wiki_file": "File:Integração_Lavoura_Pecuária_Floresta_(ILPF).jpg",
        "local_name": "ilpf_integracao_lavoura.jpg",
        "dest_dir": "aulas/extensao_rural/aulas/casos_praticos_extensao/img",
        "thumb_width": 1200,
        "description": "ILPF Cachoeira Dourada/GO (CC-BY-SA 4.0)",
    },
    {
        "wiki_file": "File:Paulo_Freire_1977.jpg",
        "local_name": "paulo_freire_1977.jpg",
        "dest_dir": "aulas/extensao_rural/aulas/comunicacao_metodologias_participativas/img",
        "thumb_width": 0,  # já é pequena (660x833), baixar original
        "description": "Paulo Freire 1977 (Slobodan Dimitro, CC-BY-SA 3.0)",
    },
    {
        "wiki_file": "File:Method_Paulo_Freire.jpg",
        "local_name": "metodo_paulo_freire.jpg",
        "dest_dir": "aulas/extensao_rural/aulas/comunicacao_metodologias_participativas/img",
        "thumb_width": 0,  # 780x1038, baixar original
        "description": "Método Paulo Freire (André Koehne, CC-BY-SA 3.0)",
    },
    {
        "wiki_file": "File:NASA_TRL_Meter.svg",
        "local_name": "trl_nasa.png",
        "dest_dir": "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras",
        "thumb_width": 800,  # SVG → PNG
        "description": "TRL NASA (CC-BY-SA 4.0)",
    },
    {
        "wiki_file": "File:Stage-Gate_process.png",
        "local_name": "stage_gate_process.png",
        "dest_dir": "aulas/ciencia_pi/SLIDES_QUARTO/Tema 05 - Gestao de Projetos inovacao/tema05_apresentacao/Figuras",
        "thumb_width": 0,  # 445x445, baixar original
        "description": "Processo Stage-Gate (CC-BY-SA 4.0)",
    },
]

# User-Agent para Wikimedia (requerido pela política de uso)
USER_AGENT = "MeuSiteAcademico/1.0 (github.com/ldvsantos/cv; educational use)"


def get_wikimedia_url(wiki_file: str, thumb_width: int = 0) -> str | None:
    """
    Usa a API do Wikimedia para obter a URL direta da imagem.
    Se thumb_width > 0, obtém thumbnail na largura especificada.
    """
    title = wiki_file.replace(" ", "_")

    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }

    if thumb_width > 0:
        params["iiurlwidth"] = str(thumb_width)

    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if page_id == "-1":
            return None
        imageinfo = page_data.get("imageinfo", [{}])
        if imageinfo:
            if thumb_width > 0 and "thumburl" in imageinfo[0]:
                return imageinfo[0]["thumburl"]
            return imageinfo[0].get("url")

    return None


def download_image(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    """Baixa a imagem da URL para o caminho destino com retry e delay."""
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait = 5 * attempt
                print(f"  Tentativa {attempt + 1}/{max_retries} após esperar {wait}s...")
                time.sleep(wait)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req) as response:
                with open(dest_path, "wb") as f:
                    shutil.copyfileobj(response, f)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                continue
            print(f"  ERRO ao baixar: {e}")
            return False
        except Exception as e:
            print(f"  ERRO ao baixar: {e}")
            return False
    return False


def main():
    print("=" * 60)
    print("Download de Imagens Pendentes — Wikimedia Commons")
    print("=" * 60)

    sucesso = 0
    falha = 0
    puladas = 0

    for img in IMAGENS:
        dest_dir = BASE_DIR / img["dest_dir"]
        dest_path = dest_dir / img["local_name"]

        print(f"\n[{img['local_name']}]")
        print(f"  Fonte: {img['wiki_file']}")
        print(f"  Destino: {dest_dir}")

        # Verificar se já existe
        if dest_path.exists():
            print(f"  ⏭ Já existe, pulando.")
            puladas += 1
            continue

        # Criar diretório se necessário
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Obter URL
        print(f"  Consultando API do Wikimedia...")
        url = get_wikimedia_url(img["wiki_file"], img["thumb_width"])

        if not url:
            print(f"  ✗ Não encontrada no Wikimedia.")
            falha += 1
            continue

        print(f"  URL: {url}")

        # Baixar
        print(f"  Baixando...")
        if download_image(url, dest_path):
            size_kb = dest_path.stat().st_size / 1024
            print(f"  ✓ Salvo ({size_kb:.1f} KB)")
            sucesso += 1
        else:
            falha += 1

        # Delay entre downloads para evitar rate-limit
        time.sleep(3)

    print("\n" + "=" * 60)
    print(f"Resultado: {sucesso} baixadas, {puladas} puladas, {falha} falhas")
    print(f"Total de imagens no mapeamento: {len(IMAGENS)}")
    print("=" * 60)

    # Listar imagens que NÃO são possíveis de baixar
    print("\n--- Imagens que NÃO puderam ser encontradas online ---")
    nao_disponiveis = [
        ("1-5", "Modelagem 3D Raízes (vetiver)", "Fotos de laboratório/campo específicas"),
        ("12-16", "Vida Útil Biotêxteis", "Fotos de equipamentos de laboratório específicos"),
        ("17-21", "Ciência PI Tema 01", "Imagens genéricas (intro, conclusão) — criar manualmente"),
        ("22-24,26,28-32", "Ciência PI Tema 05", "Imagens específicas de normas e modelos"),
        ("33-37", "Ciência PI Tema 06", "Imagens genéricas — criar manualmente"),
        ("38-42", "Intro Estatística", "Cópias do Tema 01 — criar junto"),
    ]
    for nums, grupo, motivo in nao_disponiveis:
        print(f"  #{nums}: {grupo} — {motivo}")


if __name__ == "__main__":
    main()
