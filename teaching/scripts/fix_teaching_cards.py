"""
Fix teaching index cards: Pandoc strips content from <a> (inline) when it
contains <div> (block-level). Solution: wrap each slide-grid section in a
raw HTML block (```{=html}) and replace Quarto shortcodes with actual HTML.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    ROOT / "teaching" / "index.qmd",
    ROOT / "teaching" / "index-en.qmd",
    ROOT / "teaching" / "index-es.qmd",
]

# Shortcode -> HTML replacements
SHORTCODE_MAP = {
    "{{< fa display >}}":        '<i class="fa-solid fa-display"></i>',
    "{{< fa user-graduate >}}":  '<i class="fa-solid fa-user-graduate"></i>',
}


def fix_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    # Replace shortcodes inside slide-grid blocks only
    # Find all ::: {.slide-grid} ... ::: blocks and convert them
    pattern = re.compile(
        r'^::: \{\.slide-grid\}\s*\n(.*?)\n^:::',
        re.MULTILINE | re.DOTALL,
    )

    def replace_grid(m):
        content = m.group(1)
        # Replace shortcodes with HTML
        for shortcode, html in SHORTCODE_MAP.items():
            content = content.replace(shortcode, html)
        return f'```{{=html}}\n<div class="slide-grid">\n{content}\n</div>\n```'

    text = pattern.sub(replace_grid, text)

    path.write_text(text, encoding="utf-8")
    print(f"  ✓ {path.name}")


if __name__ == "__main__":
    for f in FILES:
        fix_file(f)
    print("Done!")
