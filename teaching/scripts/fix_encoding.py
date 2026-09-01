"""Fix double-encoded UTF-8 characters in a QMD file."""
import re
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else r"aulas\analise_paisagem\aulas\legislacao_ambiental_paisagem\legislacao_ambiental_paisagem.qmd"

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Mapa de substituicoes double-encoding UTF-8
replacements = {
    "\u00c3\u00a1": "\u00e1",  # á
    "\u00c3\u00a0": "\u00e0",  # à
    "\u00c3\u00a2": "\u00e2",  # â
    "\u00c3\u00a3": "\u00e3",  # ã
    "\u00c3\u00a4": "\u00e4",  # ä
    "\u00c3\u00a9": "\u00e9",  # é
    "\u00c3\u00a8": "\u00e8",  # è
    "\u00c3\u00aa": "\u00ea",  # ê
    "\u00c3\u00ab": "\u00eb",  # ë
    "\u00c3\u00ad": "\u00ed",  # í
    "\u00c3\u00ac": "\u00ec",  # ì
    "\u00c3\u00ae": "\u00ee",  # î
    "\u00c3\u00af": "\u00ef",  # ï
    "\u00c3\u00b3": "\u00f3",  # ó
    "\u00c3\u00b2": "\u00f2",  # ò
    "\u00c3\u00b4": "\u00f4",  # ô
    "\u00c3\u00b5": "\u00f5",  # õ
    "\u00c3\u00b6": "\u00f6",  # ö
    "\u00c3\u00ba": "\u00fa",  # ú
    "\u00c3\u00b9": "\u00f9",  # ù
    "\u00c3\u00bb": "\u00fb",  # û
    "\u00c3\u00bc": "\u00fc",  # ü
    "\u00c3\u00a7": "\u00e7",  # ç
    "\u00c3\u00b1": "\u00f1",  # ñ
    "\u00c3\u0081": "\u00c1",  # Á
    "\u00c3\u0080": "\u00c0",  # À
    "\u00c3\u0082": "\u00c2",  # Â
    "\u00c3\u0083": "\u00c3",  # Ã  (keep as-is, tricky)
    "\u00c3\u0089": "\u00c9",  # É
    "\u00c3\u008a": "\u00ca",  # Ê
    "\u00c3\u008d": "\u00cd",  # Í
    "\u00c3\u0093": "\u00d3",  # Ó
    "\u00c3\u009a": "\u00da",  # Ú
    "\u00c3\u0087": "\u00c7",  # Ç
    "\u00c2\u00a7": "\u00a7",  # §
    "\u00c2\u00b0": "\u00b0",  # °
    "\u00c2\u00b2": "\u00b2",  # ²
    "\u00c2\u00b3": "\u00b3",  # ³
    "\u00c2\u00ba": "\u00ba",  # º
    "\u00c2\u00aa": "\u00aa",  # ª
}

fixed = text
for old, new in replacements.items():
    fixed = fixed.replace(old, new)

# Limpar Â isolados (residuais)
fixed = fixed.replace("\u00c2\u00a0", " ")  # non-breaking space
fixed = re.sub(r"\u00c2(?=[\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}])", "", fixed)

# Padroes adicionais: tracos tipograficos e sobrescritos (double-encoding via cp1252)
extra_reps = {
    "\u00e2\u20ac\u201c": "\u2013",  # – en-dash
    "\u00e2\u20ac\u201d": "\u2014",  # — em-dash
    "\u00e2\u0081\u00b4": "\u2074",  # ⁴
    "\u00e2\u0081\u00b5": "\u2075",  # ⁵
    "\u00e2\u0081\u00b6": "\u2076",  # ⁶
    "\u00e2\u0081\u00b7": "\u2077",  # ⁷
    "\u00e2\u0081\u00b8": "\u2078",  # ⁸
}
for old, new in extra_reps.items():
    fixed = fixed.replace(old, new)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(fixed)

print("Correcao concluida!")
print()
print("Primeiras 10 linhas:")
for i, line in enumerate(fixed.split("\n")[:10], 1):
    print(f"{i}: {line}")
print()

# Verificar problemas restantes
issues = [m for m in re.finditer(r"\u00c3[\u0080-\u00bf]|\u00c2[\u00a0-\u00bf]", fixed)]
print(f"Padroes corrompidos restantes: {len(issues)}")
if issues:
    for m in issues[:10]:
        start = max(0, m.start() - 20)
        end = min(len(fixed), m.end() + 20)
        print(f"  ...{fixed[start:end]}...")
