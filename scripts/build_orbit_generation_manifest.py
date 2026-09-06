#!/usr/bin/env python3
"""Build a dry-run manifest for orbit-only video generation.

This script intentionally preserves each sample's original
video_generation_prompt. It only selects the angle-change/orbit subset and
reports image/video availability for downstream generation.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
DEFAULT_IMAGE_INDEX = ROOT / "reports" / "video_generation_500_images" / "index.json"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "hailuo_orbit_manifest"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def task_category(sample: dict[str, Any]) -> str:
    return str(sample.get("task_category") or sample.get("abstract_task") or "")


def resolve_rooted(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def build_image_index(path: Path) -> dict[str, dict[str, Any]]:
    rows = load_json(path)
    if not isinstance(rows, list):
        raise SystemExit(f"Expected image index list: {path}")
    return {str(row["task_id"]): row for row in rows}


def select_samples(samples: list[dict[str, Any]], motion_type: str, limit: int | None) -> list[dict[str, Any]]:
    selected = [sample for sample in samples if sample.get("motion_type") == motion_type]
    selected.sort(key=lambda item: str(item["task_id"]))
    if limit is not None:
        selected = selected[:limit]
    return selected


def make_row(
    sample: dict[str, Any],
    image_row: dict[str, Any] | None,
    existing_video_dir: Path | None,
) -> dict[str, Any]:
    task_id = str(sample["task_id"])
    source_image_path = str(sample.get("image_path") or "")
    exported_image_path = str((image_row or {}).get("exported_image_path") or "")
    source_image_abs = resolve_rooted(source_image_path) if source_image_path else None
    exported_image_abs = resolve_rooted(exported_image_path) if exported_image_path else None
    video_path = existing_video_dir / f"{task_id}.mp4" if existing_video_dir else None

    prompt = str(sample.get("video_generation_prompt") or "")
    return {
        "task_id": task_id,
        "domain": sample.get("domain"),
        "scene_id": sample.get("scene_id"),
        "task_category": task_category(sample),
        "motion_type": sample.get("motion_type"),
        "viewpoint_motion_target": sample.get("viewpoint_motion_target"),
        "source_image_path": source_image_path,
        "source_image_exists": bool(source_image_abs and source_image_abs.is_file()),
        "exported_image_path": exported_image_path,
        "exported_image_exists": bool(exported_image_abs and exported_image_abs.is_file()),
        "existing_video_path": str(video_path.relative_to(ROOT).as_posix()) if video_path else "",
        "existing_video_exists": bool(video_path and video_path.is_file()),
        "prompt_chars": len(prompt),
        "video_generation_prompt": prompt,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "task_id",
        "domain",
        "scene_id",
        "task_category",
        "motion_type",
        "viewpoint_motion_target",
        "source_image_path",
        "source_image_exists",
        "exported_image_path",
        "exported_image_exists",
        "existing_video_path",
        "existing_video_exists",
        "prompt_chars",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_subset_json(path: Path, source_data: dict[str, Any], selected: list[dict[str, Any]]) -> None:
    subset = dict(source_data)
    subset["split_id"] = f"{source_data.get('split_id', 'samples')}_orbit_only"
    subset["selection"] = {
        "motion_type": "orbit",
        "prompt_policy": "original video_generation_prompt preserved without modification",
        "num_samples": len(selected),
    }
    subset["samples"] = selected
    path.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    samples_path = Path(args.samples)
    image_index_path = Path(args.image_index)
    output_dir = Path(args.output_dir)
    existing_video_dir = Path(args.existing_video_dir) if args.existing_video_dir else None

    source_data = load_json(samples_path)
    samples = source_data.get("samples", source_data)
    if not isinstance(samples, list):
        raise SystemExit(f"Expected samples list in {samples_path}")

    image_index = build_image_index(image_index_path)
    selected = select_samples(samples, args.motion_type, args.limit)
    rows = [make_row(sample, image_index.get(str(sample["task_id"])), existing_video_dir) for sample in selected]

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "orbit_manifest.jsonl", rows)
    write_csv(output_dir / "orbit_manifest.csv", rows)
    write_subset_json(output_dir / "orbit_samples.json", source_data, selected)

    summary = {
        "source_samples": str(samples_path),
        "image_index": str(image_index_path),
        "output_dir": str(output_dir),
        "motion_type": args.motion_type,
        "limit": args.limit,
        "selected_samples": len(selected),
        "prompt_policy": "original video_generation_prompt preserved without modification",
        "source_images_missing": sum(1 for row in rows if not row["source_image_exists"]),
        "exported_images_missing": sum(1 for row in rows if not row["exported_image_exists"]),
        "existing_videos_found": sum(1 for row in rows if row["existing_video_exists"]),
        "existing_videos_missing": sum(1 for row in rows if existing_video_dir and not row["existing_video_exists"]),
        "by_domain": dict(Counter(str(row["domain"]) for row in rows)),
        "by_task_category": dict(Counter(str(row["task_category"]) for row in rows)),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"selected_samples={summary['selected_samples']}")
    print(f"source_images_missing={summary['source_images_missing']}")
    print(f"exported_images_missing={summary['exported_images_missing']}")
    if existing_video_dir:
        print(f"existing_videos_found={summary['existing_videos_found']}")
        print(f"existing_videos_missing={summary['existing_videos_missing']}")
    print(f"output_dir={output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--image-index", default=str(DEFAULT_IMAGE_INDEX))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--motion-type", default="orbit")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--existing-video-dir")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
