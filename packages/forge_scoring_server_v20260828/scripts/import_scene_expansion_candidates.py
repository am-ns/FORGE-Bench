#!/usr/bin/env python3
"""Batch import staged scene-expansion candidates into dataset/images."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from PIL import Image

from find_reference_images import _average_hash, _hamming_hex


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_SOURCES = (
    "dataset/images_candidates/scene_expansion",
    "dataset/images_candidates/scene_expansion_filtered",
    "dataset/images_candidates/scene_expansion_recovered",
)


def _image_paths(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _existing_hashes() -> list[str]:
    hashes: list[str] = []
    for path in Path("dataset/images").glob("*/*/*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            hashes.append(_average_hash(path))
        except Exception:
            pass
    return hashes


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_bit_count(_hamming_hex(ahash, old)) <= max_distance for old in seen_hashes)


def _scene_from_candidate(source_root: Path, candidate: Path) -> tuple[str, str] | None:
    rel = candidate.relative_to(source_root)
    if len(rel.parts) < 3:
        return None
    return rel.parts[0], rel.parts[1]


def _next_ref_path(scene_dir: Path, suffix: str) -> Path:
    max_idx = 0
    for path in scene_dir.iterdir() if scene_dir.exists() else []:
        if not path.is_file() or not path.stem.startswith("ref_"):
            continue
        try:
            max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
        except ValueError:
            pass
    return scene_dir / f"ref_{max_idx + 1:02d}{suffix.lower()}"


def run(args: argparse.Namespace) -> None:
    rows: list[dict[str, str]] = []
    seen_hashes = _existing_hashes()
    imported = 0
    skipped = 0

    source_roots = [Path(item) for item in args.sources]
    for source_root in source_roots:
        for candidate in _image_paths(source_root):
            status = {
                "status": "skipped",
                "reason": "",
                "source_root": source_root.as_posix(),
                "candidate_path": candidate.as_posix(),
                "dataset_path": "",
                "width": "",
                "height": "",
            }
            scene = _scene_from_candidate(source_root, candidate)
            if scene is None:
                status["reason"] = "candidate_not_under_domain_scene"
                rows.append(status)
                skipped += 1
                continue
            domain, scene_name = scene
            try:
                with Image.open(candidate) as image:
                    status["width"] = str(image.width)
                    status["height"] = str(image.height)
                    image.verify()
                ahash = _average_hash(candidate)
            except Exception as exc:
                status["reason"] = f"invalid_image:{exc}"
                rows.append(status)
                skipped += 1
                continue
            if _near_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
                status["reason"] = "near_duplicate_existing"
                rows.append(status)
                skipped += 1
                continue
            scene_dir = Path("dataset/images") / domain / scene_name
            scene_dir.mkdir(parents=True, exist_ok=True)
            dst = _next_ref_path(scene_dir, candidate.suffix)
            shutil.copy2(candidate, dst)
            seen_hashes.append(ahash)
            imported += 1
            status.update({
                "status": "imported",
                "reason": "imported",
                "dataset_path": dst.as_posix(),
            })
            rows.append(status)
            print(f"imported\t{candidate.as_posix()}\t{dst.as_posix()}")

    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
            "status", "reason", "source_root", "candidate_path", "dataset_path", "width", "height"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"imported_count={imported}")
    print(f"skipped_count={skipped}")
    print(manifest.as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", nargs="+", default=list(DEFAULT_SOURCES))
    parser.add_argument("--manifest", default="reports/scene_expansion_batch_import_manifest.csv")
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
