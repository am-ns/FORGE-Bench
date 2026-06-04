#!/usr/bin/env python3
"""Create labeled contact sheets for a flat image review folder."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _load_scenes(samples: Path) -> list[str]:
    data = json.loads(samples.read_text(encoding="utf-8"))
    return sorted({str(item["scene_id"]) for item in data["samples"]}, key=len, reverse=True)


def _scene_from_name(path: Path, scenes: list[str]) -> str:
    name = re.sub(r"^worker_\d+__", "", path.stem)
    for scene in scenes:
        if name == scene or name.startswith(scene + "__"):
            return scene
    return "UNMAPPED"


def _thumb(path: Path, size: int) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), "white")
        x = (size - image.width) // 2
        y = (size - image.height) // 2
        canvas.paste(image, (x, y))
        return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="dataset/images_candidates/review_flat_20260527_151925")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--out-dir", default="reports/review_flat_20260527_151925_sheets")
    parser.add_argument("--thumb", type=int, default=180)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--manifests", nargs="*", default=[])
    args = parser.parse_args()

    root = _repo_path(args.root)
    out_dir = _repo_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scenes = _load_scenes(_repo_path(args.samples))

    groups: dict[str, list[Path]] = defaultdict(list)
    if args.manifests:
        for manifest in args.manifests:
            with _repo_path(manifest).open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    if row.get("status") != "accepted" or not row.get("dest_path"):
                        continue
                    path = _repo_path(row["dest_path"])
                    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                        groups[str(row.get("scene_id") or path.parent.name)].append(path)
    else:
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                groups[_scene_from_name(path, scenes)].append(path)

    font = ImageFont.load_default()
    label_h = 44
    cell = args.thumb
    for scene, paths in sorted(groups.items()):
        rows = (len(paths) + args.cols - 1) // args.cols
        sheet = Image.new("RGB", (args.cols * cell, rows * (cell + label_h)), "white")
        draw = ImageDraw.Draw(sheet)
        for idx, path in enumerate(paths):
            col = idx % args.cols
            row = idx // args.cols
            x = col * cell
            y = row * (cell + label_h)
            sheet.paste(_thumb(path, cell), (x, y))
            label = f"{idx:03d} {path.name}"
            draw.text((x + 4, y + cell + 4), label[:38], fill=(0, 0, 0), font=font)
            draw.text((x + 4, y + cell + 20), label[38:76], fill=(0, 0, 0), font=font)
        out = out_dir / f"{scene}.jpg"
        sheet.save(out, "JPEG", quality=90)
        print(f"{scene},{len(paths)},{out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
