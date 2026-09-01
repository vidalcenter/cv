"""Update `papers/index.qmd` from `lattes_ocr.txt` (OCR output).

This script is intentionally heuristic: OCR text is noisy, so we aim for a
useful, readable list rather than perfect BibTeX-grade parsing.

Usage (PowerShell):
    ./.venv/Scripts/python.exe ./scripts/update_papers_from_lattes_ocr.py

It will replace the content between:
  <!-- lattes:auto:start -->
  <!-- lattes:auto:end -->

If markers don't exist, it will append them.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OCR_PATH = ROOT / "lattes_ocr.txt"
PAPERS_QMD = ROOT / "papers" / "index.qmd"

START_MARK = "<!-- lattes:auto:start -->"
END_MARK = "<!-- lattes:auto:end -->"


SECTION_TITLES: list[tuple[str, str]] = [
    ("Artigos completos publicados em periódicos", "## Artigos completos em periódicos"),
    ("Artigos aceitos para publicação", "## Artigos aceitos para publicação"),
    ("Livros publicados", "## Livros"),
    ("Capítulos de livros publicados", "## Capítulos de livros"),
    ("Trabalhos publicados em anais de eventos (completo)", "## Anais de eventos (completo)"),
    ("Trabalhos publicados em anais de eventos (resumo)", "## Anais de eventos (resumo)"),
    (
        "Trabalhos publicados em anais de eventos (resumo expandido)",
        "## Anais de eventos (resumo expandido)",
    ),
]


_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

_ITEM_NUMBER_START_RE = re.compile(r"^\d{1,3}[\.,]\s*")
_ITEM_PREFIX_START_RE = re.compile(r"^(?:E{2,3}B|ERB|EMB|EBE|EEE)\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ]")
_SURNAME_START_RE = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s-]*,")

OTHER_STOP_HEADINGS = {
    "apresentação de trabalho e palestra",
    "apresentacao de trabalho e palestra",
    "produção técnica",
    "producao tecnica",
    "produções técnicas",
    "producoes tecnicas",
    "trabalhos técnicos",
    "trabalhos tecnicos",
    "patentes e registros",
}


def _norm(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def _clean_item(text: str) -> str:
    text = text.strip()

    # Drop OCR-ish prefixes used in the PDF layout
    text = re.sub(r"^(?:E{2,3}B|ERB|EMB)\s*", "", text)
    # Sometimes OCR glues a prefix into the surname (e.g., 'EBEICARVALHO')
    text = re.sub(r"^(?:EBEI|EBE|EEE)", "", text)

    # Remove leading numbering like '12.' or '12,'
    text = re.sub(r"^\d{1,3}[\.,]\s*", "", text)

    # Remove trailing citation counters that are often mangled by OCR
    text = re.sub(r"\bCita(ç|c)\w*\s*:\s*.*$", "", text, flags=re.IGNORECASE)

    # Cleanup whitespace/punctuation spacing
    text = re.sub(r"\s+", " ", text).strip(" -;,")
    return text


def _split_embedded_items(line: str) -> list[str]:
    """Split a line if OCR merged multiple numbered entries into one line."""
    # Example: "... oz, 42, FULANO, ..." -> split before "42,"
    # Restrict to cases where the number follows punctuation, to avoid splitting
    # inside author initials like "F. S. R" that OCR may mangle as "E 5. R".
    pattern = re.compile(r"(?<=[,;])\s(?=\d{1,3}[\.,]\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
    parts = re.split(pattern, line)
    return [p.strip() for p in parts if p.strip()]


def _is_item_start(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
    if _ITEM_NUMBER_START_RE.match(line):
        return True
    if _ITEM_PREFIX_START_RE.match(line):
        return True
    # Surname-only starts are risky; require a year on the same line.
    if _SURNAME_START_RE.match(line) and _YEAR_RE.search(line):
        return True
    return False


def _extract_section(lines: list[str], heading: str) -> list[str]:
    # Find heading line index (exact match after normalization).
    heading_norm = _norm(heading).lower()
    start_idx = None
    for i, line in enumerate(lines):
        if _norm(line).lower() == heading_norm:
            start_idx = i + 1
            break
    if start_idx is None:
        return []

    # End at next known heading or next page marker.
    stop_norms = {heading_norm}
    stop_norms |= {_norm(h).lower() for h, _ in SECTION_TITLES}
    stop_norms |= OTHER_STOP_HEADINGS

    collected: list[str] = []
    for line in lines[start_idx:]:
        ln = _norm(line)
        if not ln:
            collected.append("")
            continue

        lnl = ln.lower()
        if lnl in stop_norms and lnl != heading_norm:
            break
        if ln.startswith("===== PAGE"):
            # Some headings continue across pages; don't stop on page marker.
            collected.append("")
            continue
        collected.extend(_split_embedded_items(ln))

    # Turn lines into items.
    items: list[str] = []
    current: list[str] = []
    for raw in collected:
        if not raw:
            continue
        if _is_item_start(raw) and current:
            items.append(_clean_item(" ".join(current)))
            current = [raw]
        else:
            current.append(raw)
    if current:
        items.append(_clean_item(" ".join(current)))

    # Drop tiny junk items
    items = [it for it in items if len(it) >= 25]
    return items


def build_markdown_from_ocr(ocr_text: str) -> str:
    lines = ocr_text.splitlines()

    parts: list[str] = []
    parts.append(
        "\n".join(
            [
                START_MARK,
                "\n_Esta lista foi gerada automaticamente a partir do OCR do Currículo Lattes (pode conter erros de digitação)._\n",
            ]
        )
    )

    found_any = False
    for heading, md_title in SECTION_TITLES:
        items = _extract_section(lines, heading)
        if not items:
            continue
        found_any = True
        parts.append(md_title)
        for it in items:
            parts.append(f"- {it}")
        parts.append("")

    if not found_any:
        parts.append(
            "Não encontrei automaticamente as seções de publicações no OCR. "
            "Verifique se o arquivo `lattes_ocr.txt` contém a seção 'Produção bibliográfica'."
        )

    parts.append(END_MARK)
    parts.append("")

    return "\n".join(parts)


def replace_between_markers(original: str, replacement_block: str) -> str:
    if START_MARK in original and END_MARK in original:
        before = original.split(START_MARK)[0]
        after = original.split(END_MARK, 1)[1]
        return before + replacement_block + after

    # Append markers at end.
    sep = "\n" if original.endswith("\n") else "\n\n"
    return original + sep + replacement_block


def main() -> None:
    if not OCR_PATH.exists():
        raise SystemExit(f"Arquivo não encontrado: {OCR_PATH}")
    if not PAPERS_QMD.exists():
        raise SystemExit(f"Arquivo não encontrado: {PAPERS_QMD}")

    ocr_text = OCR_PATH.read_text(encoding="utf-8", errors="replace")
    new_block = build_markdown_from_ocr(ocr_text)

    current_qmd = PAPERS_QMD.read_text(encoding="utf-8", errors="replace")
    updated_qmd = replace_between_markers(current_qmd, new_block)

    PAPERS_QMD.write_text(updated_qmd, encoding="utf-8")
    print(f"OK: atualizei {PAPERS_QMD}")


if __name__ == "__main__":
    main()
