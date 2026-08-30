#!/usr/bin/env python3
"""Build a generation manifest for camera-motion samples without playable video."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from run_minimax_video_batch import existing_output_is_playable


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="reports/video_generation_500_manifest.jsonl")
    parser.add_argument("--samples", default="dataset/annotations/video_generation_500_samples.json")
    parser.add_argument("--out", default="reports/hailuo_missing_camera_motion_manifest.jsonl")
    parser.add_argument("--limit", type=int, help="Keep only the first N missing motion samples.")
    parser.add_argument(
        "--existing-roots",
        nargs="+",
        default=[
            "dataset/batch_outputs_ult",
            "dataset/batch_outputs_ult_recovered_from_parts",
            "results/minimax_500/videos",
            "results/minimax_angle_probe/videos",
            "results/minimax_angle_probe_latest/videos",
        ],
    )
    args = parser.parse_args()

    rows = load_jsonl(ROOT / args.manifest)
    samples_data = json.loads((ROOT / args.samples).read_text(encoding="utf-8"))
    samples = {str(row["task_id"]): row for row in samples_data["samples"]}
    motion_ids = {
        task_id for task_id, sample in samples.items() if str(sample.get("motion_type", "static")).lower() != "static"
    }

    playable_ids: set[str] = set()
    invalid_files: list[str] = []
    for root_text in args.existing_roots:
        root = ROOT / root_text
        if not root.is_dir():
            continue
        for video in root.rglob("*.mp4"):
            if video.stem not in motion_ids:
                continue
            playable, _ = existing_output_is_playable(video)
            if playable:
                playable_ids.add(video.stem)
            else:
                invalid_files.append(str(video.relative_to(ROOT)))

    selected = [row for row in rows if str(row.get("task_id")) in motion_ids - playable_ids]
    if args.limit is not None:
        selected = selected[: args.limit]
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in selected),
        encoding="utf-8",
    )
    summary = {
        "camera_motion_samples": len(motion_ids),
        "playable_existing": len(playable_ids),
        "invalid_existing_files": len(invalid_files),
        "selected_missing": len(selected),
        "by_motion_type": dict(Counter(samples[str(row["task_id"])]["motion_type"] for row in selected)),
        "output": str(out_path.relative_to(ROOT)),
    }
    (out_path.with_suffix(".summary.json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
