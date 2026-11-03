#!/usr/bin/env python3
"""zoom_tiles.py — cắt ảnh diagram thành các ô có overlap và phóng to, để đọc chữ nhỏ chính xác.

Usage:
    python zoom_tiles.py diagram.png --out tiles/ [--grid 2x2] [--scale 2.0] [--overlap 0.12]

Design notes:
- Model vision đọc sai chữ nhỏ (số tiền, ngưỡng, mã lỗi) trên ảnh lớn bị downscale. Nhìn từng ô
  phóng to giảm lỗi đọc mà không cần OCR engine.
- Overlap giữa các ô để nhãn nằm trên đường cắt vẫn đọc trọn vẹn ở ít nhất một ô.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def tile(path: Path, out: Path, cols: int, rows: int, scale: float, overlap: float) -> list[Path]:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    out.mkdir(parents=True, exist_ok=True)
    tw, th = w / cols, h / rows
    ox, oy = tw * overlap, th * overlap
    paths: list[Path] = []
    for r in range(rows):
        for c in range(cols):
            box = (max(0, int(c * tw - ox)), max(0, int(r * th - oy)),
                   min(w, int((c + 1) * tw + ox)), min(h, int((r + 1) * th + oy)))
            crop = img.crop(box)
            crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
            p = out / f"{path.stem}_r{r + 1}c{c + 1}.png"
            crop.save(p)
            paths.append(p)
            print(f"{p}  box={box}")
    return paths


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", default="tiles")
    ap.add_argument("--grid", default="2x2", help="cột x hàng, vd 3x2")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--overlap", type=float, default=0.12)
    a = ap.parse_args(argv)
    cols, rows = (int(x) for x in a.grid.lower().split("x"))
    tile(Path(a.image), Path(a.out), cols, rows, a.scale, a.overlap)
    return 0


if __name__ == "__main__":
    sys.exit(main())
