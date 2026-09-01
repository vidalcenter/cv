"""Insert remaining 5 images that failed due to encoding issues."""
import os
import re

BASE = r"aulas\analise_paisagem\aulas"

FIXES = [
    ("dominios_paisagens_tropicais", "dominios_paisagens_tropicais.qmd",
     "## Os Dom\u00ednios Morfoclim\u00e1ticos {.smaller-text}",
     '\n![Mapa dos dom\u00ednios morfoclim\u00e1ticos / biomas do Brasil](img/dominios_morfoclimaticos.jpg){width="60%" fig-align="center"}\n'),
    ("dominios_paisagens_tropicais", "dominios_paisagens_tropicais.qmd",
     "## Dom\u00ednio das Caatingas e o Semi\u00e1rido Baiano {.smaller-text}",
     '\n![Vegeta\u00e7\u00e3o da Caatinga no semi\u00e1rido nordestino](img/caatinga_vegetacao.jpg){width="85%" fig-align="center"}\n'),
    ("sensoriamento_remoto_avancado", "sensoriamento_remoto_avancado.qmd",
     "## Princ\u00edpios do SAR {.smaller-text}",
     '\n![Imagem SAR \u2014 radar de abertura sint\u00e9tica](img/sar_radar.jpg){width="85%" fig-align="center"}\n'),
    ("sensoriamento_remoto_avancado", "sensoriamento_remoto_avancado.qmd",
     "## A revolu\u00e7\u00e3o dos drones {.smaller-text}",
     '\n![RPA (drone) \u2014 fotografia a\u00e9rea de alta resolu\u00e7\u00e3o](img/drone_rpa.jpg){width="85%" fig-align="center"}\n'),
    ("percepcao_valoracao_paisagem", "percepcao_valoracao_paisagem.qmd",
     "## Paisagem: objeto ou experi\u00eancia? {.smaller-text}",
     '\n![Ponto de vista elevado sobre a paisagem \u2014 percep\u00e7\u00e3o e contempla\u00e7\u00e3o](img/perspectiva_paisagem.jpg){width="85%" fig-align="center"}\n'),
]

for lesson, qmd, header, img_md in FIXES:
    filepath = os.path.join(BASE, lesson, qmd)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    img_match = re.search(r"img/(\S+\.jpg)", img_md)
    if img_match and img_match.group(1) in content:
        print(f"[SKIP] {lesson}: already present")
        continue

    idx = content.find(header)
    if idx == -1:
        print(f"[FAIL] {lesson}: header not found: {header[:50]}")
        continue

    end = content.index("\n", idx) + 1
    new_content = content[:end] + img_md + content[end:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] {lesson}: image inserted")

print("Done!")
