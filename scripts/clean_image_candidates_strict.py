#!/usr/bin/env python3
"""Build a strict clean pool from dataset/images_candidates and remove old pools."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DOMAIN_NAMES = {
    "visual_security",
    "embodied_robotics",
    "heavy_load_construction",
    "precision_defect_gen",
    "extreme_emergency",
}


def _repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def _as_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _require_within(path: Path, root: Path, label: str, *, allow_equal: bool = False) -> None:
    resolved = path.resolve()
    resolved_root = root.resolve()
    if not resolved.is_relative_to(resolved_root) or (resolved == resolved_root and not allow_equal):
        raise ValueError(f"{label} must stay inside {resolved_root}")


def _load_scene_domains(samples_path: Path) -> dict[str, str]:
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for sample in data["samples"]:
        scene = str(sample.get("scene_id", ""))
        domain = str(sample.get("domain", ""))
        if scene and domain:
            out[scene] = domain
    return out


def _iter_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _candidate_scene(path: Path, candidate_root: Path, scene_domains: dict[str, str]) -> tuple[str | None, str | None]:
    stem = path.stem
    for scene, domain in scene_domains.items():
        if stem == scene or stem.startswith(scene + "__") or stem.startswith(scene + "_ref_"):
            return scene, domain

    try:
        rel = path.relative_to(candidate_root)
    except ValueError:
        return None, None
    parts = rel.parts
    for index, part in enumerate(parts[:-1]):
        if part in DOMAIN_NAMES and index + 1 < len(parts):
            scene = parts[index + 1]
            if scene_domains.get(scene) == part:
                return scene, part
    return None, None


def _average_hash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.float32)
    avg = float(arr.mean())
    bits = (arr > avg).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _dhash(path: Path, hash_size: int = 8) -> str:
    with Image.open(path) as image:
        image = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(image, dtype=np.int16)
    bits = (arr[:, 1:] > arr[:, :-1]).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def _hamming(a: str, b: str) -> int:
    return int.bit_count(int(a, 16) ^ int(b, 16))


def _metrics(path: Path) -> dict[str, float | int]:
    with Image.open(path) as image:
        image = image.convert("RGB")
        width, height = image.size
        arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))
    white_ratio = float(np.mean((arr[:, :, 0] > 238) & (arr[:, :, 1] > 238) & (arr[:, :, 2] > 238)))
    return {
        "width": width,
        "height": height,
        "short_side": min(width, height),
        "pixels": width * height,
        "laplacian_var": laplacian_var,
        "edge_density": edge_density,
        "white_ratio": white_ratio,
    }


def _quality_reason(metrics: dict[str, float | int], args: argparse.Namespace) -> str:
    if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
        return "resolution_below_min"
    if metrics["short_side"] < args.min_short_side:
        return "short_side_below_min"
    if metrics["pixels"] < args.min_pixels:
        return "pixel_count_below_min"
    if metrics["laplacian_var"] < args.min_laplacian:
        return "too_blurry"
    if metrics["edge_density"] > args.max_edge_density:
        return "too_many_edges_or_diagram_like"
    if metrics["white_ratio"] > args.max_white_ratio:
        return "page_or_white_background_like"
    return "accepted"


def _accepted_report_paths(reports_root: Path) -> set[str]:
    accepted: set[str] = set()
    for report in sorted(reports_root.rglob("*.csv")):
        try:
            with report.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    if row.get("status") != "accepted":
                        continue
                    for field in ("local_path", "source_path", "path", "candidate_path"):
                        value = (row.get(field) or "").strip()
                        if not value:
                            continue
                        accepted.add(_as_rel(_repo_path(value)))
        except Exception:
            continue
    return accepted


def _existing_hashes(root: Path) -> dict[str, list[tuple[str, str, str]]]:
    hashes: dict[str, list[tuple[str, str, str]]] = {}
    for path in _iter_images(root):
        try:
            hashes.setdefault(path.parent.name, []).append((_average_hash(path), _dhash(path), _as_rel(path)))
        except Exception:
            continue
    return hashes


def _next_ref_path(output_root: Path, domain: str, scene: str) -> Path:
    scene_dir = output_root / domain / scene
    scene_dir.mkdir(parents=True, exist_ok=True)
    max_index = 0
    for path in scene_dir.glob("ref_*.*"):
        match = re.match(r"ref_(\d+)$", path.stem)
        if match:
            max_index = max(max_index, int(match.group(1)))
    return scene_dir / f"ref_{max_index + 1:03d}.jpg"


def _copy_jpeg(source: Path, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with Image.open(source) as image:
        image.convert("RGB").save(tmp, "JPEG", quality=92, optimize=True)
    os.replace(tmp, dest)


def _safe_remove_old_dirs(candidate_root: Path, output_root: Path) -> int:
    candidate_root = candidate_root.resolve()
    output_root = output_root.resolve()
    removed = 0
    for child in candidate_root.iterdir():
        if not child.is_dir():
            continue
        resolved = child.resolve()
        if resolved == output_root or output_root.is_relative_to(resolved):
            continue
        if not resolved.is_relative_to(candidate_root):
            continue
        shutil.rmtree(child)
        removed += 1
    return removed


def run(args: argparse.Namespace) -> None:
    candidate_root = _repo_path(args.candidate_root)
    output_root = _repo_path(args.output_root)
    reports_root = _repo_path(args.reports_root)
    image_root = _repo_path(args.image_root)
    samples_path = _repo_path(args.samples)
    manifest_path = _repo_path(args.manifest)
    allowed_candidate_root = ROOT / "dataset" / "images_candidates"
    _require_within(candidate_root, allowed_candidate_root, "candidate-root", allow_equal=True)
    _require_within(output_root, candidate_root, "output-root")

    scene_domains = _load_scene_domains(samples_path)
    accepted_reports = _accepted_report_paths(reports_root)
    seen_hashes = _existing_hashes(image_root)
    if output_root.exists() and not args.dry_run:
        shutil.rmtree(output_root)
    rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    copied = 0

    for source in _iter_images(candidate_root):
        if output_root.exists() and source.resolve().is_relative_to(output_root.resolve()):
            continue
        rel_source = _as_rel(source)
        scene, domain = _candidate_scene(source, candidate_root, scene_domains)
        row = {
            "status": "rejected",
            "reason": "",
            "source_path": rel_source,
            "dest_path": "",
            "scene_id": scene or "",
            "domain": domain or "",
        }
        if scene is None or domain is None:
            row["reason"] = "scene_mapping_unresolved"
            rows.append(row)
            counts[row["reason"]] += 1
            continue
        if args.require_accepted_report and rel_source not in accepted_reports:
            row["reason"] = "not_accepted_in_previous_reports"
            rows.append(row)
            counts[row["reason"]] += 1
            continue
        try:
            metrics = _metrics(source)
            row.update({
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "short_side": str(metrics["short_side"]),
                "pixels": str(metrics["pixels"]),
                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
                "edge_density": f"{metrics['edge_density']:.4f}",
                "white_ratio": f"{metrics['white_ratio']:.4f}",
            })
            reason = _quality_reason(metrics, args)
            if reason != "accepted":
                row["reason"] = reason
                rows.append(row)
                counts[reason] += 1
                continue
            ahash = _average_hash(source)
            dhash = _dhash(source)
            duplicate = next(
                (
                    path for old_a, old_d, path in seen_hashes.get(scene, [])
                    if _hamming(ahash, old_a) <= args.ahash_distance
                    or _hamming(dhash, old_d) <= args.dhash_distance
                ),
                None,
            )
            if duplicate:
                row["reason"] = "near_duplicate"
                row["duplicate_of"] = duplicate
                rows.append(row)
                counts[row["reason"]] += 1
                continue
        except Exception as exc:
            row["reason"] = f"read_error:{exc}"
            rows.append(row)
            counts["read_error"] += 1
            continue

        dest = _next_ref_path(output_root, domain, scene)
        if not args.dry_run:
            _copy_jpeg(source, dest)
        seen_hashes.setdefault(scene, []).append((ahash, dhash, _as_rel(dest)))
        row["status"] = "accepted"
        row["reason"] = "accepted"
        row["dest_path"] = _as_rel(dest)
        rows.append(row)
        copied += 1
        counts["accepted"] += 1

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "status", "reason", "source_path", "dest_path", "scene_id", "domain",
        "width", "height", "short_side", "pixels", "laplacian_var",
        "edge_density", "white_ratio", "duplicate_of",
    ]
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    removed_dirs = 0
    if args.delete_old_roots and not args.dry_run:
        removed_dirs = _safe_remove_old_dirs(candidate_root, output_root)

    print(f"candidates={len(rows)}")
    print(f"accepted={copied}")
    print(f"rejected={len(rows) - copied}")
    print(f"removed_old_candidate_dirs={removed_dirs}")
    print(f"output_root={_as_rel(output_root)}")
    print(f"manifest={_as_rel(manifest_path)}")
    for reason, count in counts.most_common():
        print(f"{reason}={count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", default="dataset/images_candidates")
    parser.add_argument("--output-root", default="dataset/images_candidates/clean_strict_20260526")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--manifest", default="reports/clean_image_candidates_strict_20260526.csv")
    parser.add_argument("--min-width", type=int, default=640)
    parser.add_argument("--min-height", type=int, default=480)
    parser.add_argument("--min-short-side", type=int, default=520)
    parser.add_argument("--min-pixels", type=int, default=500000)
    parser.add_argument("--min-laplacian", type=float, default=45.0)
    parser.add_argument("--max-edge-density", type=float, default=0.20)
    parser.add_argument("--max-white-ratio", type=float, default=0.68)
    parser.add_argument("--ahash-distance", type=int, default=4)
    parser.add_argument("--dhash-distance", type=int, default=6)
    parser.add_argument("--require-accepted-report", action="store_true", default=True)
    parser.add_argument("--allow-unreported", dest="require_accepted_report", action="store_false")
    parser.add_argument("--delete-old-roots", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
