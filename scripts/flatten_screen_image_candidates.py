#!/usr/bin/env python3
"""Flatten image candidates into dataset/images_candidates and delete hard rejects."""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def as_rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def require_within(path: Path, root: Path, label: str, *, allow_equal: bool = False) -> None:
    resolved = path.resolve()
    resolved_root = root.resolve()
    if not resolved.is_relative_to(resolved_root) or (resolved == resolved_root and not allow_equal):
        raise ValueError(f"{label} must stay inside {resolved_root}")


def iter_images(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def scene_key(path: Path) -> str:
    stem = re.sub(r"^worker_\d+__", "", path.stem)
    return stem.split("__", 1)[0]


def ahash(path: Path, size: int = 8) -> str:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((size, size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    bits = (arr > float(arr.mean())).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
    return f"{value:0{size * size // 4}x}"


def dhash(path: Path, size: int = 8) -> str:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.int16)
    bits = (arr[:, 1:] > arr[:, :-1]).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
    return f"{value:0{size * size // 4}x}"


def hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def image_metrics(path: Path) -> dict[str, float | int]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        width, height = image.size
        arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    laplacian = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))
    white_ratio = float(np.mean((arr[:, :, 0] > 238) & (arr[:, :, 1] > 238) & (arr[:, :, 2] > 238)))
    dark_ratio = float(np.mean((arr[:, :, 0] < 16) & (arr[:, :, 1] < 16) & (arr[:, :, 2] < 16)))
    return {
        "width": width,
        "height": height,
        "short_side": min(width, height),
        "pixels": width * height,
        "laplacian_var": laplacian,
        "edge_density": edge_density,
        "white_ratio": white_ratio,
        "dark_ratio": dark_ratio,
    }


def reject_reason(metrics: dict[str, float | int], args: argparse.Namespace) -> str:
    if int(metrics["width"]) < args.min_width or int(metrics["height"]) < args.min_height:
        return "resolution_below_min"
    if int(metrics["short_side"]) < args.min_short_side:
        return "short_side_below_min"
    if int(metrics["pixels"]) < args.min_pixels:
        return "pixel_count_below_min"
    if float(metrics["laplacian_var"]) < args.min_laplacian:
        return "too_blurry"
    if float(metrics["edge_density"]) > args.max_edge_density:
        return "diagram_or_edge_heavy"
    if float(metrics["white_ratio"]) > args.max_white_ratio:
        return "white_background_or_page"
    if float(metrics["dark_ratio"]) > args.max_dark_ratio:
        return "mostly_black_or_empty"
    return "accepted"


def existing_hashes(image_root: Path) -> dict[str, list[tuple[str, str, str]]]:
    out: dict[str, list[tuple[str, str, str]]] = {}
    for path in iter_images(image_root):
        scene = path.parent.name
        try:
            out.setdefault(scene, []).append((ahash(path), dhash(path), as_rel(path)))
        except Exception:
            continue
    return out


def unique_root_name(root: Path, source: Path, batch_name: str) -> Path:
    name = source.name
    dest = root / name
    if source.parent == root and not dest.exists():
        return dest
    if not dest.exists() or dest.resolve() == source.resolve():
        return dest
    stem = f"{source.stem}__{batch_name}"
    dest = root / f"{stem}{source.suffix.lower()}"
    index = 2
    while dest.exists() and dest.resolve() != source.resolve():
        dest = root / f"{stem}__{index}{source.suffix.lower()}"
        index += 1
    return dest


def remove_empty_dirs(candidate_root: Path) -> int:
    removed = 0
    for path in sorted((p for p in candidate_root.rglob("*") if p.is_dir()), reverse=True):
        if path == candidate_root:
            continue
        try:
            path.rmdir()
            removed += 1
        except OSError:
            pass
    return removed


def run(args: argparse.Namespace) -> None:
    candidate_root = repo_path(args.candidate_root).resolve()
    image_root = repo_path(args.image_root).resolve()
    manifest = repo_path(args.manifest).resolve()
    allowed_root = (ROOT / "dataset" / "images_candidates").resolve()
    require_within(candidate_root, allowed_root, "candidate-root", allow_equal=True)
    require_within(image_root, ROOT / "dataset" / "images", "image-root", allow_equal=True)
    require_within(manifest.parent, ROOT / "reports", "manifest parent", allow_equal=True)

    rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    seen = existing_hashes(image_root)
    kept = 0
    deleted = 0
    moved = 0

    for source in iter_images(candidate_root):
        rel_source = as_rel(source)
        scene = scene_key(source)
        row = {
            "status": "rejected",
            "reason": "",
            "source_path": rel_source,
            "dest_path": "",
            "scene_id": scene,
            "duplicate_of": "",
        }
        try:
            metrics = image_metrics(source)
            row.update({
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "short_side": str(metrics["short_side"]),
                "pixels": str(metrics["pixels"]),
                "laplacian_var": f"{float(metrics['laplacian_var']):.2f}",
                "edge_density": f"{float(metrics['edge_density']):.4f}",
                "white_ratio": f"{float(metrics['white_ratio']):.4f}",
                "dark_ratio": f"{float(metrics['dark_ratio']):.4f}",
            })
            reason = reject_reason(metrics, args)
            if reason == "accepted":
                source_ahash = ahash(source)
                source_dhash = dhash(source)
                duplicate = next(
                    (
                        old_path for old_a, old_d, old_path in seen.get(scene, [])
                        if _is_near_duplicate(source_ahash, source_dhash, old_a, old_d, args)
                    ),
                    None,
                )
                if duplicate:
                    reason = "near_duplicate"
                    row["duplicate_of"] = duplicate
            if reason != "accepted":
                row["reason"] = reason
                counts[reason] += 1
                deleted += 1
                if not args.dry_run:
                    source.unlink()
                rows.append(row)
                continue
        except Exception as exc:
            row["reason"] = f"read_error:{type(exc).__name__}"
            counts["read_error"] += 1
            deleted += 1
            if not args.dry_run:
                try:
                    source.unlink()
                except OSError:
                    pass
            rows.append(row)
            continue

        batch_name = source.parent.name if source.parent != candidate_root else "root"
        dest = unique_root_name(candidate_root, source, batch_name)
        if not args.dry_run and dest.resolve() != source.resolve():
            shutil.move(str(source), str(dest))
            moved += 1
        kept += 1
        seen.setdefault(scene, []).append((source_ahash, source_dhash, as_rel(dest)))
        row["status"] = "accepted"
        row["reason"] = "accepted"
        row["dest_path"] = as_rel(dest)
        counts["accepted"] += 1
        rows.append(row)

    removed_dirs = 0 if args.dry_run else remove_empty_dirs(candidate_root)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "status", "reason", "source_path", "dest_path", "scene_id", "duplicate_of",
        "width", "height", "short_side", "pixels", "laplacian_var",
        "edge_density", "white_ratio", "dark_ratio",
    ]
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"total={len(rows)}")
    print(f"kept={kept}")
    print(f"deleted={deleted}")
    print(f"moved_to_root={moved}")
    print(f"empty_dirs_removed={removed_dirs}")
    print(f"candidate_root={as_rel(candidate_root)}")
    print(f"manifest={as_rel(manifest)}")
    for reason, count in counts.most_common():
        print(f"{reason}={count}")


def _is_near_duplicate(source_a: str, source_d: str, old_a: str, old_d: str, args: argparse.Namespace) -> bool:
    return hamming(source_a, old_a) <= args.ahash_distance or hamming(source_d, old_d) <= args.dhash_distance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", default="dataset/images_candidates")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--manifest", default="reports/flatten_screen_candidates_20260608/manifest.csv")
    parser.add_argument("--min-width", type=int, default=480)
    parser.add_argument("--min-height", type=int, default=320)
    parser.add_argument("--min-short-side", type=int, default=300)
    parser.add_argument("--min-pixels", type=int, default=160000)
    parser.add_argument("--min-laplacian", type=float, default=25.0)
    parser.add_argument("--max-edge-density", type=float, default=0.24)
    parser.add_argument("--max-white-ratio", type=float, default=0.70)
    parser.add_argument("--max-dark-ratio", type=float, default=0.82)
    parser.add_argument("--ahash-distance", type=int, default=3)
    parser.add_argument("--dhash-distance", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
