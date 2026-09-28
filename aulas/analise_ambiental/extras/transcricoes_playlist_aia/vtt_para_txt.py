# -*- coding: utf-8 -*-
"""Converte legendas .vtt (auto-subs do YouTube) em .txt limpo para leitura.

Remove cabeçalho WEBVTT, timestamps, tags <...> e linhas repetidas (roll-up).
"""
import html
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"<[^>]+>")
TS_RE = re.compile(r"^\s*(\d{2}:)?\d{2}:\d{2}\.\d{3}\s*-->.*$")
NOTE_RE = re.compile(r"^NOTE\b.*$")


def limpar_vtt(texto: str) -> str:
    linhas_ok = []
    ultima = ""
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("WEBVTT") or linha.startswith("Kind:") or linha.startswith("Language:"):
            continue
        if TS_RE.match(linha) or NOTE_RE.match(linha):
            continue
        linha = TAG_RE.sub("", linha)
        linha = html.unescape(linha).strip()
        if not linha or linha == ultima:  # remove duplicatas do roll-up
            continue
        ultima = linha
        linhas_ok.append(linha)
    return "\n".join(linhas_ok) + "\n"


def main() -> None:
    pasta = Path(__file__).parent
    vtts = sorted(pasta.glob("*.vtt"))
    if not vtts:
        print("Nenhum .vtt encontrado em", pasta)
        sys.exit(1)
    # Usa apenas o track original (sufixo "-orig"): ignora ".pt.vtt" e ".pt-PT.vtt" duplicados
    escolhidos = [v for v in vtts if v.name.endswith("-orig.vtt")]
    for vtt in escolhidos:
        saida = vtt.with_suffix(".txt")
        saida.write_text(limpar_vtt(vtt.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
        n_linhas = len(saida.read_text(encoding="utf-8").splitlines())
        print(f"{vtt.name} -> {saida.name} ({n_linhas} linhas)")


if __name__ == "__main__":
    main()
