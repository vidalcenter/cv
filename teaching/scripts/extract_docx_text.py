from __future__ import annotations

import argparse
from pathlib import Path


def extract_docx_text(docx_path: Path) -> str:
    try:
        from docx import Document  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "python-docx não está disponível no ambiente. Instale com: python -m pip install python-docx"
        ) from exc

    document = Document(str(docx_path))
    lines: list[str] = []
    for paragraph in document.paragraphs:
        text = (paragraph.text or "").strip()
        if not text:
            continue
        style_name = getattr(getattr(paragraph, "style", None), "name", "") or ""
        if style_name.startswith("Heading"):
            lines.append(f"\n# {text}\n")
        else:
            lines.append(text)

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai texto de um .docx para .txt")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    docx_path: Path = args.docx
    out_path: Path = args.out

    if not docx_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {docx_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(extract_docx_text(docx_path), encoding="utf-8")


if __name__ == "__main__":
    main()
