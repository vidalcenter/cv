"""Busca e baixa imagens do Wikimedia Commons para Aula 02."""
import urllib.request
import ssl
import json
import time
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {"User-Agent": "AcademicBot/1.0 (educational use; landscape-analysis course)"}
IMG_DIR = os.path.join("aulas", "analise_paisagem", "aulas", "evolucao_conceito_distincoes", "img")
os.makedirs(IMG_DIR, exist_ok=True)


def api_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())


def search_commons(query, limit=5):
    """Busca arquivos no Wikimedia Commons."""
    url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&list=search&srsearch={query}"
        f"&srnamespace=6&srlimit={limit}&format=json"
    )
    data = api_get(url)
    results = data.get("query", {}).get("search", [])
    for r in results:
        print(f"  {r['title']}")
    return [r["title"] for r in results]


def get_image_url(file_title, width=800):
    """Obtém URL de thumbnail de um arquivo no Commons."""
    # file_title deve ser como "File:Example.jpg"
    title = file_title.replace(" ", "_")
    url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&titles={title}"
        f"&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json"
    )
    data = api_get(url)
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "imageinfo" in page:
            info = page["imageinfo"][0]
            return info.get("thumburl", info.get("url"))
    return None


def download_file(url, filepath):
    """Baixa um arquivo."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = resp.read()
    with open(filepath, "wb") as f:
        f.write(data)
    return len(data)


# ── ETAPA 1: Buscar nomes corretos ──────────────────────────────
print("=" * 60)
print("ETAPA 1: Buscando imagens no Wikimedia Commons")
print("=" * 60)

searches = [
    "Carl Troll geographer portrait",
    "Milton Santos geographer Brazil",
    "domínios morfoclimáticos Ab'Sáber Brasil", 
    "aerial photograph landscape 1930",
    "Paul Vidal de la Blache",
    "fazenda café Vale Paraíba",
    "Aziz Ab'Saber",
]

for s in searches:
    print(f"\nBusca: {s}")
    search_commons(s)
    time.sleep(0.5)

# ── ETAPA 2: Baixar com nomes conhecidos ─────────────────────────
print("\n" + "=" * 60)
print("ETAPA 2: Baixando imagens com File: titles conhecidos")
print("=" * 60)

# Nomes exatos de arquivos que sabemos existir no Commons
known_files = {
    "vidal_blache.jpg": "File:Paul Vidal de la Blache.jpg",
    "milton_santos.jpg": "File:Milton Santos.jpg",
}

for local_name, file_title in known_files.items():
    filepath = os.path.join(IMG_DIR, local_name)
    print(f"\nBuscando: {file_title}")
    url = get_image_url(file_title)
    if url:
        print(f"  URL: {url[:100]}")
        try:
            size = download_file(url, filepath)
            print(f"  [OK] {local_name} ({size // 1024} KB)")
        except Exception as e:
            print(f"  [ERRO download] {e}")
    else:
        print(f"  [ERRO] URL não encontrada")
    time.sleep(1)

print(f"\nArquivos na pasta: {os.listdir(IMG_DIR)}")
