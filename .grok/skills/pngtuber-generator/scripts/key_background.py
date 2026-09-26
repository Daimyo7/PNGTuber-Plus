#!/usr/bin/env python3
"""Replace a flat key color with transparency on PNG layers."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: py -3 -m pip install pillow") from exc


def parse_hex(color: str) -> tuple[int, int, int]:
    c = color.strip().lstrip("#")
    if len(c) != 6:
        raise SystemExit("color must be #RRGGBB")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def key_image(path: Path, rgb: tuple[int, int, int], threshold: int) -> None:
    img = Image.open(path).convert("RGBA")
    pixels = img.getdata()
    keyed = []
    for r, g, b, a in pixels:
        if abs(r - rgb[0]) <= threshold and abs(g - rgb[1]) <= threshold and abs(b - rgb[2]) <= threshold:
            keyed.append((r, g, b, 0))
        else:
            keyed.append((r, g, b, a))
    img.putdata(keyed)
    img.save(path)
    print(f"keyed {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="PNG files or a directory of PNGs")
    parser.add_argument("--color", default="#FF00FF", help="Key color (default #FF00FF)")
    parser.add_argument("--threshold", type=int, default=24, help="Per-channel distance")
    args = parser.parse_args()
    rgb = parse_hex(args.color)

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.glob("*.png")))
        else:
            files.append(p)
    if not files:
        raise SystemExit("no PNG files")
    for f in files:
        key_image(f, rgb, args.threshold)


if __name__ == "__main__":
    main()
