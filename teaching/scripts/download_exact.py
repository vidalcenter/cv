import urllib.request, urllib.parse, ssl, json, os, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HEADERS = {"User-Agent": "AcademicBot/1.0 (educational; landscape-analysis-course)"}
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
            info = p["imageinfo"][0]
            return info.get("thumburl", info.get("url"))
    return None

def download(url, path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        d = resp.read()
    with open(path, "wb") as f:
        f.write(d)
    return len(d)

# Nomes EXATOS encontrados no Commons
files = {
    "carl_troll.jpg": ("File:Carl Th. Troll.jpg", 500),
    "milton_santos.jpg": ("File:Milton Santos (TV Brasil).jpg", 800),
    "absaber_1.jpg": ("File:Aziz Ab'Saber 1.jpg", 800),
    "vidal_blache.jpg": ("File:VIdal de la Blache, Paul, BNF Gallica cropped.jpg", 500),
    "foto_aerea_1930.jpg": ("File:Belpmoos 1930.jpg", 800),
}

print("=== BAIXANDO IMAGENS ===\n")
for local_name, (remote_title, width) in files.items():
    filepath = os.path.join(IMG_DIR, local_name)
    print(f"[{remote_title}]")
    url = get_thumb(remote_title, width)
    if url:
        print(f"  URL: {url[:100]}")
        try:
            sz = download(url, filepath)
            print(f"  OK: {local_name} ({sz // 1024} KB)")
        except Exception as e:
            print(f"  ERRO download: {e}")
    else:
        print(f"  ERRO: URL nao encontrada, tentando nome alternativo...")
    time.sleep(1.5)

print(f"\nArquivos baixados: {os.listdir(IMG_DIR)}")
