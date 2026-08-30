#!/usr/bin/env python3
"""Create contact sheets for selected dataset image scene folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def thumb(path: Path, size: int) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), "white")
        canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
        return canvas


def write_sheet(scene_dir: Path, out_dir: Path, thumb_size: int, cols: int) -> Path | None:
    paths = sorted(
        path for path in scene_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not paths:
        return None
    font = ImageFont.load_default()
    label_h = 44
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_size, rows * (thumb_size + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        col = index % cols
        row = index // cols
        x = col * thumb_size
        y = row * (thumb_size + label_h)
        sheet.paste(thumb(path, thumb_size), (x, y))
        label = path.name
        draw.text((x + 4, y + thumb_size + 4), label[:40], fill=(0, 0, 0), font=font)
        draw.text((x + 4, y + thumb_size + 20), label[40:80], fill=(0, 0, 0), font=font)
    out = out_dir / f"{scene_dir.parent.name}__{scene_dir.name}.jpg"
    sheet.save(out, "JPEG", quality=90)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_dirs", nargs="+")
    parser.add_argument("--out-dir", default="reports/replacement_contact_sheets")
    parser.add_argument("--thumb", type=int, default=220)
    parser.add_argument("--cols", type=int, default=5)
    args = parser.parse_args()

    out_dir = repo_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for value in args.scene_dirs:
        scene_dir = repo_path(value)
        out = write_sheet(scene_dir, out_dir, args.thumb, args.cols)
        if out:
            print(out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
