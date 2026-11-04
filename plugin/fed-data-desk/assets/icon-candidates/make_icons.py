"""Draws the D7 icon candidates (1024 x 1024 PNG, generic shapes, no brand marks).

    uv run --with pillow python plugin/fed-data-desk/assets/icon-candidates/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
S = 1024
NAVY, TEAL, CORAL, PAPER = (27, 42, 74), (27, 175, 160), (235, 104, 52), (247, 248, 249)


def rounded_canvas(bg):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=200, fill=bg)
    return im, d


def candidate_a():
    """Ledger bars: three columns on a baseline, the tallest split into two holders."""
    im, d = rounded_canvas(NAVY)
    base, w, gap = 760, 150, 70
    x0 = (S - (3 * w + 2 * gap)) // 2
    for i, h in enumerate((220, 340, 470)):
        x = x0 + i * (w + gap)
        d.rounded_rectangle([x, base - h, x + w, base], radius=28, fill=TEAL if i < 2 else PAPER)
    x = x0 + 2 * (w + gap)
    d.rounded_rectangle([x, base - 470, x + w, base - 250], radius=28, fill=CORAL)
    d.rounded_rectangle([x0 - 40, base + 30, x0 + 3 * w + 2 * gap + 40, base + 62], radius=16, fill=PAPER)
    im.save(HERE / "candidate-a-ledger-bars.png")


def candidate_b():
    """Dot grid: a 6 x 6 grid of dots, the lower rows filled, one ring dot (who holds the rest)."""
    im, d = rounded_canvas(PAPER)
    n, r = 6, 46
    pad = 190
    step = (S - 2 * pad) / (n - 1)
    for row in range(n):
        for col in range(n):
            cx, cy = pad + col * step, pad + row * step
            box = [cx - r, cy - r, cx + r, cy + r]
            if row >= 3:
                d.ellipse(box, fill=TEAL)
            elif row == 2 and col >= 2:
                d.ellipse(box, fill=TEAL)
            elif row == 0 and col == n - 1:
                d.ellipse(box, outline=CORAL, width=16)
            else:
                d.ellipse(box, fill=NAVY)
    im.save(HERE / "candidate-b-dot-grid.png")


if __name__ == "__main__":
    candidate_a()
    candidate_b()
    print("wrote", ", ".join(p.name for p in sorted(HERE.glob("candidate-*.png"))))
