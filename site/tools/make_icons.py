# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10"]
# ///
"""Draw the home-screen icons (a ship on waves) into site/static/icons/.

Run once from the repository root when the artwork changes:
    uv run site/tools/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "static" / "icons"
BG = (29, 91, 196)       # --color-accent (light theme)
FG = (255, 255, 255)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#1d5bc4"/>
<path d="M14 34h36l-5 9H19z" fill="#fff"/>
<path d="M22 34V26h14v8M28 26v-6h6v6" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round"/>
<path d="M10 49c4 0 4-2.5 8-2.5s4 2.5 8 2.5 4-2.5 8-2.5 4 2.5 8 2.5 4-2.5 8-2.5 4 2.5 6 2.5"
 fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def draw(size):
    s = size / 64
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    # Hull
    d.polygon([(14 * s, 34 * s), (50 * s, 34 * s), (45 * s, 43 * s), (19 * s, 43 * s)], fill=FG)
    w = max(2, round(3 * s))
    # Cabin and funnel
    d.line([(22 * s, 34 * s), (22 * s, 26 * s), (36 * s, 26 * s), (36 * s, 34 * s)], fill=FG, width=w, joint="curve")
    d.line([(28 * s, 26 * s), (28 * s, 20 * s), (34 * s, 20 * s), (34 * s, 26 * s)], fill=FG, width=w, joint="curve")
    # Wave: a row of shallow arcs
    for i in range(6):
        x0 = (10 + 8 * i) * s
        d.arc([x0, 46.5 * s - 2.5 * s, x0 + 8 * s, 49 * s + 2.5 * s], start=200, end=340, fill=FG, width=w)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "icon.svg").write_text(SVG)
    for size in (192, 512):
        draw(size).save(OUT / f"icon-{size}.png", optimize=True)
    print(f"Wrote icons to {OUT}")


if __name__ == "__main__":
    main()
