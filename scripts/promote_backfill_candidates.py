#!/usr/bin/env python3
"""Promote staged backfill candidates into the clean candidate pool.

The staging root is expected to already be organized as domain/scene/ref_*.jpg,
which is how targeted_candidate_backfill_v2.py writes outputs. Promotion copies
files into the clean pool with stable ref_XXX names and skips near-duplicates.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from find_reference_images import _average_hash, _hamming_hex


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_bit_count(_hamming_hex(ahash, old)) <= max_distance for old in seen_hashes)


def _hashes(root: Path) -> list[str]:
    hashes: list[str] = []
    if not root.exists():
        return hashes
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                hashes.append(_average_hash(path))
            except Exception:
                pass
    return hashes


def _image_paths(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _next_ref_path(scene_dir: Path, suffix: str) -> Path:
    scene_dir.mkdir(parents=True, exist_ok=True)
    max_idx = 0
    for path in scene_dir.iterdir():
        if not path.is_file() or not path.stem.startswith("ref_"):
            continue
        try:
            max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
        except ValueError:
            pass
    return scene_dir / f"ref_{max_idx + 1:03d}{suffix.lower()}"


def _scene_parts(staging_root: Path, path: Path) -> tuple[str, str] | None:
    rel = path.relative_to(staging_root)
    if len(rel.parts) < 3:
        return None
    return rel.parts[0], rel.parts[1]


def run(args: argparse.Namespace) -> None:
    staging_root = Path(args.staging_root)
    clean_root = Path(args.clean_root)
    manifest = Path(args.manifest)
    seen_hashes = _hashes(Path("dataset/images")) + _hashes(clean_root)
    rows: list[dict[str, str]] = []
    promoted = 0
    skipped = 0

    for src in _image_paths(staging_root):
        row = {
            "status": "skipped",
            "reason": "",
            "source_path": src.as_posix(),
            "promoted_path": "",
            "domain": "",
            "scene": "",
        }
        scene = _scene_parts(staging_root, src)
        if scene is None:
            row["reason"] = "not_under_domain_scene"
            rows.append(row)
            skipped += 1
            continue
        domain, scene_name = scene
        row["domain"] = domain
        row["scene"] = scene_name
        try:
            ahash = _average_hash(src)
        except Exception as exc:
            row["reason"] = f"invalid_image:{exc}"
            rows.append(row)
            skipped += 1
            continue
        if _near_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
            row["reason"] = "near_duplicate_clean_or_dataset"
            rows.append(row)
            skipped += 1
            continue
        dst = _next_ref_path(clean_root / domain / scene_name, src.suffix)
        if args.move:
            shutil.move(str(src), str(dst))
        else:
            shutil.copy2(src, dst)
        seen_hashes.append(ahash)
        promoted += 1
        row.update({
            "status": "promoted",
            "reason": "promoted",
            "promoted_path": dst.as_posix(),
        })
        rows.append(row)

    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "status", "reason", "source_path", "promoted_path", "domain", "scene",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"promoted={promoted}")
    print(f"skipped={skipped}")
    print(manifest.as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-root", required=True)
    parser.add_argument("--clean-root", default="dataset/images_candidates/scene_expansion_bulk_resume_400")
    parser.add_argument("--manifest", default="reports/scene_expansion_bulk_resume_400/promote_backfill_manifest.csv")
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--move", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
