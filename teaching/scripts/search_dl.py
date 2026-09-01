import urllib.request, urllib.parse, ssl, json, os, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HEADERS = {"User-Agent": "AcademicBot/1.0 (educational)"}
IMG_DIR = os.path.join("aulas", "analise_paisagem", "aulas", "evolucao_conceito_distincoes", "img")

def api_get(base, params):
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())

def get_thumb(title, w=800):
    data = api_get("https://commons.wikimedia.org/w/api.php", {
        "action": "query", "titles": title,
        "prop": "imageinfo", "iiprop": "url",
        "iiurlwidth": w, "format": "json"
    })
    for p in data["query"]["pages"].values():
        if "imageinfo" in p:
            return p["imageinfo"][0].get("thumburl", p["imageinfo"][0]["url"])
    return None

def download(url, path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        d = resp.read()
    with open(path, "wb") as f:
        f.write(d)
    return len(d)

# ETAPA 1: Buscar nomes
print("=== BUSCANDO NOMES NO WIKIMEDIA COMMONS ===")
searches = [
    "Carl Troll geographer",
    "Milton Santos geographer",
    "dominios morfoclimaticos",
    "Paul Vidal de la Blache",
    "Aziz Ab Saber",
    "fazenda cafe Vale Paraiba patrimonio",
    "aerial photograph Switzerland 1930",
]
for s in searches:
    data = api_get("https://commons.wikimedia.org/w/api.php", {
        "action": "query", "list": "search", "srsearch": s,
        "srnamespace": 6, "srlimit": 3, "format": "json"
    })
    print(f"\nBusca: {s}")
    for r in data.get("query", {}).get("search", []):
        title = r["title"]
        print(f"  {title}")
    time.sleep(0.5)

# ETAPA 2: Baixar com títulos exatos
print("\n\n=== BAIXANDO IMAGENS ===")
files_to_download = {
    "vidal_blache.jpg": "File:Paul Vidal de la Blache.jpg",
}

for local, remote in files_to_download.items():
    print(f"\nBaixando {remote}...")
    url = get_thumb(remote)
    if url:
        try:
            sz = download(url, os.path.join(IMG_DIR, local))
            print(f"  OK: {sz // 1024} KB")
        except Exception as e:
            print(f"  ERRO: {e}")
    else:
        print(f"  URL não encontrada")
    time.sleep(1)

print(f"\nArquivos: {os.listdir(IMG_DIR)}")
