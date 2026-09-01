"""
Script para baixar imagens do Wikimedia Commons e gerar diagramas para Aula 02.
Todas as imagens são de domínio público ou licença CC.
"""
import urllib.request
import os
import ssl

# Desabilitar verificação SSL para download (ambiente controlado)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

IMG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "aulas", "analise_paisagem", "aulas", "evolucao_conceito_distincoes", "img"
)
os.makedirs(IMG_DIR, exist_ok=True)

# ── URLs de imagens do Wikimedia Commons (domínio público / CC) ─────────────
DOWNLOADS = {
    # Carl Troll - retrato (domínio público, Wikimedia Commons)
    "carl_troll.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Carl_Troll_1959.jpg/440px-Carl_Troll_1959.jpg",
    
    # Milton Santos - Google Doodle tribute (fair use educacional)
    # Usando foto do Wikimedia Commons
    "milton_santos.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Milton_Santos_%28geographer%29.jpg/440px-Milton_Santos_%28geographer%29.jpg",
    
    # Mapa dos domínios morfoclimáticos de Ab'Sáber
    "dominios_morfoclimaticos.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Mapa_dominios_morfoclimaticos_absaber.png/600px-Mapa_dominios_morfoclimaticos_absaber.png",
    
    # Foto aérea histórica (exemplo de fotointerpretação - conceito Troll)
    "foto_aerea_historica.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/ETH-BIB-Fl%C3%BCelen_mit_Bristenstock_aus_1500_m-Inlandfl%C3%BCge-LBS_MH01-006327.tif/lossy-page1-800px-ETH-BIB-Fl%C3%BCelen_mit_Bristenstock_aus_1500_m-Inlandfl%C3%BCge-LBS_MH01-006327.tif.jpg",

    # Vale do Paraíba - paisagem de fazenda histórica (transtemporal - Milton Santos)
    "vale_paraiba.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Fazenda_Pau_d%27Alho_01.jpg/800px-Fazenda_Pau_d%27Alho_01.jpg",
    
    # Vidal de la Blache - tradição francesa
    "vidal_blache.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Paul_Vidal_de_la_Blache.jpg/440px-Paul_Vidal_de_la_Blache.jpg",
}

def download_images():
    """Baixa imagens do Wikimedia Commons."""
    headers = {"User-Agent": "Mozilla/5.0 (educational use)"}
    for filename, url in DOWNLOADS.items():
        filepath = os.path.join(IMG_DIR, filename)
        if os.path.exists(filepath):
            print(f"  [SKIP] {filename} já existe")
            continue
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
            print(f"  [OK]   {filename} ({len(data)//1024} KB)")
        except Exception as e:
            print(f"  [ERRO] {filename}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("ETAPA 1: Baixando imagens do Wikimedia Commons")
    print("=" * 60)
    download_images()
    print("\nDownloads concluídos!")
    print(f"Pasta: {IMG_DIR}")
    print(f"Arquivos: {os.listdir(IMG_DIR)}")
