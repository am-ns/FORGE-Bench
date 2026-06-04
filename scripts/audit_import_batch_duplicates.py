#!/usr/bin/env python3
"""Audit exact and perceptual duplicates for one imported image batch."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _iter_images(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _average_hash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    value = 0
    for bit in (arr > float(arr.mean())).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _dhash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.int16)
    value = 0
    for bit in (arr[:, 1:] > arr[:, :-1]).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _phash(path: Path, hash_size: int = 8, highfreq: int = 4) -> str:
    size = hash_size * highfreq
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((size, size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    dct = cv2.dct(arr)
    low = dct[:hash_size, :hash_size]
    median = float(np.median(low[1:, 1:]))
    value = 0
    for bit in (low > median).flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def _accepted_paths(import_report: Path) -> set[str]:
    out: set[str] = set()
    with import_report.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") == "accepted" and row.get("dest_path"):
                out.add(row["dest_path"].replace("\\", "/"))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-report", required=True)
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--report", required=True)
    parser.add_argument("--ahash-distance", type=int, default=4)
    parser.add_argument("--dhash-distance", type=int, default=6)
    parser.add_argument("--phash-distance", type=int, default=8)
    args = parser.parse_args()

    import_report = _repo_path(args.import_report)
    image_root = _repo_path(args.image_root)
    accepted = _accepted_paths(import_report)

    records = []
    for path in _iter_images(image_root):
        rel = path.relative_to(ROOT).as_posix()
        try:
            records.append({
                "path": rel,
                "is_imported": rel in accepted,
                "sha256": _sha256(path),
                "ahash": _average_hash(path),
                "dhash": _dhash(path),
                "phash": _phash(path),
            })
        except Exception as exc:
            records.append({"path": rel, "is_imported": rel in accepted, "error": str(exc)})

    rows = []
    imported = [record for record in records if record.get("is_imported") and not record.get("error")]
    others = [record for record in records if not record.get("error")]
    for item in imported:
        for other in others:
            if item["path"] == other["path"]:
                continue
            exact = item["sha256"] == other["sha256"]
            ah = _hamming(item["ahash"], other["ahash"])
            dh = _hamming(item["dhash"], other["dhash"])
            ph = _hamming(item["phash"], other["phash"])
            if exact or ah <= args.ahash_distance or dh <= args.dhash_distance or ph <= args.phash_distance:
                rows.append({
                    "imported_path": item["path"],
                    "matched_path": other["path"],
                    "matched_is_imported": str(other["is_imported"]).lower(),
                    "exact_sha256": str(exact).lower(),
                    "ahash_distance": str(ah),
                    "dhash_distance": str(dh),
                    "phash_distance": str(ph),
                })

    out = _repo_path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "imported_path", "matched_path", "matched_is_imported", "exact_sha256",
            "ahash_distance", "dhash_distance", "phash_distance",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    exact_rows = sum(1 for row in rows if row["exact_sha256"] == "true")
    print(f"imported={len(imported)}")
    print(f"duplicate_matches={len(rows)}")
    print(f"exact_matches={exact_rows}")
    print(f"report={out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
