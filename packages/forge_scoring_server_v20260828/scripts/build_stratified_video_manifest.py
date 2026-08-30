#!/usr/bin/env python3
"""Build a reproducible 500-sample video-generation manifest."""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_SEED = 5001729
DEFAULT_TOTAL = 500
DEFAULT_MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
DEFAULT_SPLIT = ROOT / "reports" / "video_generation_500_split.json"
DEFAULT_REPORT = ROOT / "reports" / "video_generation_500_coverage.json"
DEFAULT_INCLUDE = ROOT / "reports" / "minimax_angle_probe_manifest.jsonl"
DEFAULT_SAMPLES_OUT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["samples"] if isinstance(data, dict) else data


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def image_metrics(path: Path) -> dict[str, float | int | str]:
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            width, height = image.size
            arr = np.array(image)
    except Exception as exc:
        return {
            "width": 0,
            "height": 0,
            "short_side": 0,
            "pixels": 0,
            "laplacian_var": 0.0,
            "edge_density": 0.0,
            "white_ratio": 1.0,
            "aspect_ratio": 99.0,
            "quality_score": -1000.0,
            "quality_error": str(exc),
        }

    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edge_density = float(np.mean(edges > 0))
    white_ratio = float(np.mean((arr[:, :, 0] > 238) & (arr[:, :, 1] > 238) & (arr[:, :, 2] > 238)))
    aspect_ratio = max(width, height) / max(1, min(width, height))
    score = 0.0
    score += min(35.0, math.log2(max(width * height, 1.0) / 250000.0) * 8.0)
    score += min(20.0, min(width, height) / 40.0)
    score += min(25.0, math.log1p(laplacian_var) * 3.0)
    score -= max(0.0, white_ratio - 0.45) * 80.0
    score -= max(0.0, edge_density - 0.20) * 70.0
    score -= max(0.0, 0.015 - edge_density) * 200.0
    score -= max(0.0, aspect_ratio - 2.4) * 8.0
    if "feishu" in path.name.lower():
        score -= 15.0
    return {
        "width": width,
        "height": height,
        "short_side": min(width, height),
        "pixels": width * height,
        "laplacian_var": laplacian_var,
        "edge_density": edge_density,
        "white_ratio": white_ratio,
        "aspect_ratio": aspect_ratio,
        "quality_score": score,
        "quality_error": "",
    }


def image_quality_by_path(samples: list[dict]) -> dict[str, dict[str, float | int | str]]:
    paths = sorted({str(sample.get("image_path", "")).replace("\\", "/") for sample in samples})
    quality = {}
    for image_path in paths:
        path = repo_path(image_path)
        if path.suffix.lower() not in IMAGE_EXTS:
            quality[image_path] = {"quality_score": -1000.0, "quality_error": "unsupported image extension"}
            continue
        quality[image_path] = image_metrics(path)
    return quality


def camera_control(sample: dict) -> str:
    motion_type = str(sample.get("motion_type") or "static").lower()
    target = sample.get("viewpoint_motion_target")
    if motion_type == "static":
        return "locked static camera"
    if motion_type == "orbit":
        degrees = int(target) if isinstance(target, (int, float)) else 30
        return f"controlled constant-radius {degrees} degree orbit around the reference subject"
    if motion_type == "pan":
        return "smooth left-to-right inspection pan, not an orbit"
    if motion_type == "dolly":
        return "smooth dolly forward from the reference viewpoint while keeping subject framed"
    if motion_type == "crane":
        return "smooth crane-up camera move with stable scale and perspective"
    return f"{motion_type} camera motion from the reference viewpoint"


def manifest_row(sample: dict, batch_id: str, role: str) -> dict:
    return {
        "batch_id": batch_id,
        "task_id": sample["task_id"],
        "probe_role": role,
        "domain": sample["domain"],
        "task_category": sample["task_category"],
        "scene_id": sample["scene_id"],
        "motion_type": sample["motion_type"],
        "viewpoint_motion_target": sample["viewpoint_motion_target"],
        "image_path": sample["image_path"],
        "output_name": f"{sample['task_id']}.mp4",
        "generation_policy": {
            "duration_seconds": 5,
            "style": "photorealistic industrial video",
            "first_frame_lock": True,
            "camera_control": camera_control(sample),
            "identity_lock": True,
            "no_text_overlay": True,
            "no_extra_entities": True,
            "no_global_regeneration": True,
            "preserve_component_counts": True,
        },
    }


def included_manifest_row(sample: dict, include_row: dict, batch_id: str) -> dict:
    row = manifest_row(sample, batch_id, "preseeded_probe")
    row.update({
        "image_path": include_row.get("image_path", row["image_path"]),
        "output_name": include_row.get("output_name", row["output_name"]),
        "generation_policy": include_row.get("generation_policy", row["generation_policy"]),
    })
    return row


def sample_quality(sample: dict, quality_by_path: dict[str, dict[str, float | int | str]]) -> float:
    image_path = str(sample.get("image_path", "")).replace("\\", "/")
    return float(quality_by_path.get(image_path, {}).get("quality_score", -1000.0))


def round_robin_scene_fill(
    candidates: list[dict],
    needed: int,
    rng: random.Random,
    quality_by_path: dict[str, dict[str, float | int | str]],
    used_image_paths: set[str],
) -> list[dict]:
    by_scene: dict[str, list[dict]] = defaultdict(list)
    for sample in candidates:
        by_scene[str(sample["scene_id"])].append(sample)
    for rows in by_scene.values():
        rng.shuffle(rows)
        rows.sort(key=lambda sample: (-sample_quality(sample, quality_by_path), sample["task_id"]))
    scenes = sorted(
        by_scene,
        key=lambda scene: (
            -max(sample_quality(sample, quality_by_path) for sample in by_scene[scene]),
            len(by_scene[scene]),
            scene,
        ),
    )
    picked: list[dict] = []
    while len(picked) < needed and scenes:
        progressed = False
        for scene in list(scenes):
            rows = by_scene[scene]
            if not rows:
                scenes.remove(scene)
                continue
            pick_index = next(
                (
                    index for index, sample in enumerate(rows)
                    if str(sample.get("image_path", "")).replace("\\", "/") not in used_image_paths
                ),
                0,
            )
            sample = rows.pop(pick_index)
            picked.append(sample)
            used_image_paths.add(str(sample.get("image_path", "")).replace("\\", "/"))
            progressed = True
            if len(picked) >= needed:
                break
        if not progressed:
            break
    if len(picked) != needed:
        raise SystemExit(f"could not fill requested split: needed {needed}, got {len(picked)}")
    return picked


def build_split(
    samples: list[dict],
    include_rows: list[dict],
    total: int,
    seed: int,
    quality_by_path: dict[str, dict[str, float | int | str]],
) -> list[dict]:
    rng = random.Random(seed)
    samples_by_id = {sample["task_id"]: sample for sample in samples}
    domains = sorted({sample["domain"] for sample in samples})
    if total % len(domains) != 0:
        raise SystemExit(f"total must be divisible by {len(domains)} domains")
    per_domain = total // len(domains)
    selected: list[dict] = []
    selected_ids: set[str] = set()
    used_image_paths: set[str] = set()

    for row in include_rows:
        task_id = row.get("task_id")
        sample = samples_by_id.get(task_id)
        if sample is None or task_id in selected_ids:
            continue
        selected.append(sample)
        selected_ids.add(task_id)
        used_image_paths.add(str(row.get("image_path", sample.get("image_path", ""))).replace("\\", "/"))

    selected_by_domain = Counter(sample["domain"] for sample in selected)
    for domain in domains:
        needed = per_domain - selected_by_domain[domain]
        if needed < 0:
            raise SystemExit(f"included samples exceed quota for {domain}")
        candidates = [
            sample for sample in samples
            if sample["domain"] == domain and sample["task_id"] not in selected_ids
        ]
        picked = round_robin_scene_fill(candidates, needed, rng, quality_by_path, used_image_paths)
        selected.extend(picked)
        selected_ids.update(sample["task_id"] for sample in picked)

    selected.sort(key=lambda sample: (sample["domain"], sample["scene_id"], sample["task_id"]))
    return selected


def coverage(samples: list[dict]) -> dict:
    def counts(key: str) -> dict:
        return dict(sorted(Counter(str(sample.get(key)) for sample in samples).items()))

    return {
        "num_samples": len(samples),
        "num_scenes": len({sample["scene_id"] for sample in samples}),
        "num_unique_images": len({sample["image_path"] for sample in samples}),
        "domain": counts("domain"),
        "task_category": counts("task_category"),
        "motion_type": counts("motion_type"),
        "application_type": counts("application_type"),
        "domain_task": {
            f"{domain}|{task}": count
            for (domain, task), count in sorted(Counter(
                (sample["domain"], sample["task_category"]) for sample in samples
            ).items())
        },
        "scene": counts("scene_id"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-json", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--include-manifest", default=str(DEFAULT_INCLUDE))
    parser.add_argument("--total", type=int, default=DEFAULT_TOTAL)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--split", default=str(DEFAULT_SPLIT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--samples-out", default=str(DEFAULT_SAMPLES_OUT))
    args = parser.parse_args()

    samples = load_samples(Path(args.samples_json))
    include_rows = load_jsonl(Path(args.include_manifest))
    include_by_id = {str(row.get("task_id")): row for row in include_rows}
    quality_by_path = image_quality_by_path(samples)
    selected = build_split(samples, include_rows, args.total, args.seed, quality_by_path)
    batch_id = f"video_generation_{args.total}_seed_{args.seed}"
    include_ids = set(include_by_id)
    rows = [
        included_manifest_row(sample, include_by_id[sample["task_id"]], batch_id)
        if sample["task_id"] in include_by_id
        else manifest_row(sample, batch_id, "stratified_500")
        for sample in selected
    ]

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    split_payload = {
        "split_id": batch_id,
        "seed": args.seed,
        "total": args.total,
        "task_ids": [sample["task_id"] for sample in selected],
    }
    Path(args.split).write_text(json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selected_by_id = {sample["task_id"]: dict(sample) for sample in selected}
    for row in rows:
        sample = selected_by_id[row["task_id"]]
        sample["image_path"] = row["image_path"]
    reporting_samples = [selected_by_id[sample["task_id"]] for sample in selected]
    report = coverage(reporting_samples)
    selected_image_paths = {sample["image_path"] for sample in reporting_samples}
    selected_scores = [
        float(quality_by_path.get(path, {}).get("quality_score", -1000.0))
        for path in selected_image_paths
    ]
    all_scores = [
        float(metrics.get("quality_score", -1000.0))
        for metrics in quality_by_path.values()
    ]
    report["image_quality_selection"] = {
        "selection_policy": "quality-aware scene round-robin with preseeded probe rows locked",
        "all_unique_images": len(quality_by_path),
        "selected_unique_images": len(selected_image_paths),
        "preseeded_probe_count": len(include_by_id),
        "selected_quality_score_mean": sum(selected_scores) / len(selected_scores),
        "selected_quality_score_min": min(selected_scores),
        "all_quality_score_mean": sum(all_scores) / len(all_scores),
        "all_quality_score_min": min(all_scores),
    }
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    samples_payload = {
        "split_id": batch_id,
        "source_samples_json": str(Path(args.samples_json)),
        "samples": reporting_samples,
    }
    Path(args.samples_out).write_text(
        json.dumps(samples_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "manifest": str(manifest_path),
        "split": args.split,
        "report": args.report,
        "samples_out": args.samples_out,
        "coverage": report,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
