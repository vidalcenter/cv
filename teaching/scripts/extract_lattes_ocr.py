from __future__ import annotations

import os
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    pdf_path = project_root / "lattes.pdf"
    tessdata_dir = project_root / "tessdata"
    out_path = project_root / "lattes_ocr.txt"
    progress_path = project_root / "lattes_ocr_progress.log"

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

    lang = "por+eng"
    config = "--oem 1 --psm 1"

    doc = fitz.open(pdf_path)

    # Escreve incrementalmente para não perder progresso.
    out_path.write_text("", encoding="utf-8")
    progress_path.write_text("", encoding="utf-8")

    for page_index in range(doc.page_count):
        page_number = page_index + 1
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        text = pytesseract.image_to_string(img, lang=lang, config=config)

        with out_path.open("a", encoding="utf-8", errors="replace") as fp:
            fp.write(f"\n\n===== PAGE {page_number} =====\n")
            fp.write(text)

        with progress_path.open("a", encoding="utf-8") as fp:
            fp.write(f"OK page {page_number}/{doc.page_count} - chars={len(text)}\n")

        print(f"OK page {page_number}/{doc.page_count} - chars={len(text)}")

    print(f"DONE -> {out_path}")


if __name__ == "__main__":
    main()
