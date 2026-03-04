#!/usr/bin/env python3
"""
triple_nipples.py – draws three pink circles side‑by‑side.

Usage:
    python triple_nipples.py          # creates triple_nipples.png
    python triple_nipples.py --size 300 300 --radius 0.2 --colour 255,0,255,255

The arguments are optional and let you tweak canvas size, circle radius
(as a fraction of the smaller canvas side), and RGBA colour.
"""

# ------------------------------------------------------------
# 1️⃣  Imports
# ------------------------------------------------------------
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise ImportError(
        "\n❗️ Pillow is not installed.\n"
        "Run: pip install --user pillow   (or sudo pip install pillow)\n"
    ) from exc


# ------------------------------------------------------------
# 2️⃣  Core drawing routine
# ------------------------------------------------------------
def draw_triple(
    width: int = 200,
    height: int = 200,
    radius_ratio: float = 0.25,
    colour: tuple = (255, 105, 180, 255),   # hot‑pink, fully opaque
) -> Image.Image:
    """
    Return a Pillow Image containing three circles.

    The circles are placed at 1/4, 1/2, and 3/4 of the canvas width,
    all vertically centered.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = int(min(width, height) * radius_ratio)

    # X‑positions: 25 %, 50 %, 75 % of the width
    centers_x = (width // 4, width // 2, 3 * width // 4)
    center_y = height // 2

    for cx in centers_x:
        bbox = [(cx - radius, center_y - radius),
                (cx + radius, center_y + radius)]
        draw.ellipse(bbox, fill=colour)

    return img


# ------------------------------------------------------------
# 3️⃣  CLI interface
# ------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw three pink circles side‑by‑side."
    )
    parser.add_argument(
        "--size",
        nargs=2,
        type=int,
        default=(200, 200),
        metavar=("WIDTH", "HEIGHT"),
        help="Canvas size in pixels (default: 200 200).",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=0.25,
        help="Radius as fraction of the smaller canvas side (default: 0.25).",
    )
    parser.add_argument(
        "--colour",
        type=str,
        default="255,105,180,255",
        help=(
            "RGBA colour for the circles, comma‑separated. "
            "Defaults to hot‑pink (255,105,180,255)."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("triple_nipples.png"),
        help="Filename to write (default: triple_nipples.png).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    width, height = args.size
    radius_ratio = args.radius
    colour = tuple(int(v) for v in args.colour.split(","))

    img = draw_triple(width, height, radius_ratio, colour)

    # Ensure parent directories exist
    args.output.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.output)

    print(f"✅ Saved {args.output}")


if __name__ == "__main__":
    main()
