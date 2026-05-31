#!/usr/bin/env python3
"""Audit near-duplicate images in the formal dataset image library."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _iter_images(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)


def _average_hash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    avg = float(arr.mean())
    value = 0
    for bit in (arr > avg).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _dhash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.int16)
    value = 0
    for bit in (arr[:, 1:] > arr[:, :-1]).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def run(args: argparse.Namespace) -> None:
    root = Path(args.image_root)
    rows = []
    seen: dict[str, list[tuple[str, str, Path]]] = {}
    image_count = 0
    for path in _iter_images(root):
        image_count += 1
        scene = path.parent.name
        ahash = _average_hash(path)
        dhash = _dhash(path)
        duplicate = next(
            (
                old_path for old_a, old_d, old_path in seen.get(scene, [])
                if _hamming(ahash, old_a) <= args.ahash_distance
                or _hamming(dhash, old_d) <= args.dhash_distance
            ),
            None,
        )
        if duplicate is not None:
            rows.append({
                "image_path": path.as_posix(),
                "near_duplicate_of": duplicate.as_posix(),
            })
        seen.setdefault(scene, []).append((ahash, dhash, path))

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_path", "near_duplicate_of"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"images={image_count}")
    print(f"near_duplicates={len(rows)}")
    print(f"report={report.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--report", default="reports/image_library_duplicate_audit.csv")
    parser.add_argument("--ahash-distance", type=int, default=4)
    parser.add_argument("--dhash-distance", type=int, default=6)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
