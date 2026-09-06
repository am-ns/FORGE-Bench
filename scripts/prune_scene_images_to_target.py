#!/usr/bin/env python3
"""Prune formal scene image folders to a fixed per-scene target.

The script keeps the highest-scoring references in each scene directory, repoints
samples that used pruned images to retained references from the same scene, and
optionally deletes the pruned files.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _require_within(path: Path, root: Path, label: str) -> None:
    resolved = path.resolve()
    resolved_root = root.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"{label} must stay inside {resolved_root}")


def _iter_images(image_root: Path) -> list[Path]:
    return sorted(
        path
        for path in image_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )


def _scene_key(path: Path, image_root: Path) -> tuple[str, str]:
    rel = path.relative_to(image_root)
    if len(rel.parts) < 3:
        raise ValueError(f"unexpected image path shape: {path}")
    return rel.parts[0], rel.parts[1]


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
        "aspect_ratio": max(width, height) / max(1, min(width, height)),
    }


def _quality_score(metrics: dict[str, float | int], path: Path) -> float:
    short_side = float(metrics["short_side"])
    pixels = float(metrics["pixels"])
    sharp = float(metrics["laplacian_var"])
    edge_density = float(metrics["edge_density"])
    white_ratio = float(metrics["white_ratio"])
    aspect_ratio = float(metrics["aspect_ratio"])

    score = 0.0
    score += min(35.0, math.log2(max(pixels, 1.0) / 250000.0) * 8.0)
    score += min(20.0, short_side / 40.0)
    score += min(25.0, math.log1p(sharp) * 3.0)
    score -= max(0.0, white_ratio - 0.45) * 80.0
    score -= max(0.0, edge_density - 0.20) * 70.0
    score -= max(0.0, 0.015 - edge_density) * 200.0
    score -= max(0.0, aspect_ratio - 2.4) * 8.0
    if "feishu" in path.name.lower():
        score -= 15.0
    return score


def _load_samples(samples_path: Path) -> tuple[dict, list[dict]]:
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    if not isinstance(samples, list):
        raise ValueError("samples file must contain a list or a {'samples': [...]} object")
    return data, samples


def _choose_replacement(
    old_path: str,
    retained: list[dict[str, object]],
    sample_index: int,
) -> str:
    old_stem = Path(old_path).stem.lower()
    numbered = [row for row in retained if Path(str(row["image_path"])).stem.lower().startswith("ref_")]
    pool = numbered or retained
    if old_stem.startswith("ref_"):
        try:
            old_num = int(old_stem.split("_", 1)[1])
            return str(min(pool, key=lambda row: abs(int(row.get("ref_index") or 0) - old_num))["image_path"])
        except Exception:
            pass
    return str(pool[sample_index % len(pool)]["image_path"])


def run(args: argparse.Namespace) -> None:
    image_root = _repo_path(args.image_root)
    samples_path = _repo_path(args.samples)
    report_path = _repo_path(args.report)
    _require_within(image_root, ROOT / "dataset" / "images", "image-root")
    _require_within(samples_path, ROOT / "dataset" / "annotations", "samples")
    _require_within(report_path, ROOT / "reports", "report")

    data, samples = _load_samples(samples_path)
    reference_counts = Counter(str(sample.get("image_path", "")).replace("\\", "/") for sample in samples)
    by_scene: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for image in _iter_images(image_root):
        by_scene[_scene_key(image, image_root)].append(image)

    rows: list[dict[str, object]] = []
    kept_by_scene: dict[tuple[str, str], list[dict[str, object]]] = {}
    replacements: dict[str, str] = {}

    for scene_key, images in sorted(by_scene.items()):
        scored = []
        for image in images:
            rel = _rel(image)
            metrics = _metrics(image)
            stem = image.stem.lower()
            ref_index = None
            if stem.startswith("ref_"):
                try:
                    ref_index = int(stem.split("_", 1)[1])
                except ValueError:
                    ref_index = None
            score = _quality_score(metrics, image) + min(reference_counts[rel], 5) * 10.0
            scored.append({
                "domain": scene_key[0],
                "scene_id": scene_key[1],
                "image_path": rel,
                "score": score,
                "reference_count": reference_counts[rel],
                "ref_index": ref_index,
                **metrics,
            })

        retained = sorted(
            scored,
            key=lambda row: (
                -int(row["reference_count"]),
                -float(row["score"]),
                int(row["ref_index"] or 100000),
                str(row["image_path"]),
            ),
        )[: args.target_per_scene]
        retained_paths = {str(row["image_path"]) for row in retained}
        kept_by_scene[scene_key] = retained
        for row in scored:
            action = "keep" if str(row["image_path"]) in retained_paths else "prune"
            row["action"] = action
            row["replacement_path"] = ""
            if action == "prune":
                row["replacement_path"] = _choose_replacement(str(row["image_path"]), retained, len(replacements))
                replacements[str(row["image_path"])] = str(row["replacement_path"])
            rows.append(row)

    updated = 0
    for index, sample in enumerate(samples):
        image_path = str(sample.get("image_path", "")).replace("\\", "/")
        replacement = replacements.get(image_path)
        if replacement:
            sample["image_path"] = replacement
            updated += 1

    report_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "action", "domain", "scene_id", "image_path", "replacement_path",
        "reference_count", "score", "width", "height", "short_side", "pixels",
        "laplacian_var", "edge_density", "white_ratio", "aspect_ratio",
    ]
    with report_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (str(row["domain"]), str(row["scene_id"]), str(row["action"]), str(row["image_path"]))))

    if not args.dry_run:
        tmp = samples_path.with_suffix(samples_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, samples_path)
        for old_path in sorted(replacements):
            target = ROOT / old_path
            _require_within(target, image_root, "pruned image")
            if target.exists():
                target.unlink()

    print(f"target_per_scene={args.target_per_scene}")
    print(f"scenes={len(by_scene)}")
    print(f"images_before={sum(len(images) for images in by_scene.values())}")
    print(f"images_kept={sum(min(len(images), args.target_per_scene) for images in by_scene.values())}")
    print(f"images_pruned={len(replacements)}")
    print(f"samples_updated={updated}")
    print(f"dry_run={str(args.dry_run).lower()}")
    print(f"report={_rel(report_path)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--report", default="reports/scene_image_prune_to_target.csv")
    parser.add_argument("--target-per-scene", type=int, default=16)
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
