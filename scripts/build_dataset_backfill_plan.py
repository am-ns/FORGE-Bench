#!/usr/bin/env python3
"""Build a backfill plan from the formal dataset/images counts.

This differs from build_candidate_backfill_plan.py: it counts images already in
dataset/images, not temporary candidate folders. It is intended for deciding
which scenes still need more reference images.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _image_counts(root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not root.exists():
        return counts
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            counts[path.parent.name] += 1
    return counts


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    samples = _load_samples(Path(args.samples))
    counts = _image_counts(Path(args.count_root))
    by_scene: dict[str, dict] = {}
    for sample in samples:
        scene = Path(sample["image_path"]).parent.name
        by_scene.setdefault(scene, sample)

    rows = []
    selected_samples = []
    selected_scenes = []
    for scene, sample in sorted(by_scene.items()):
        count = counts[scene]
        target = args.target_per_scene
        deficit = max(0, target - count)
        skip_reason = ""
        if count >= args.skip_at_least:
            skip_reason = f"count_at_least_{args.skip_at_least}"
        elif deficit == 0:
            skip_reason = "no_deficit"
        else:
            selected_samples.append(sample)
            selected_scenes.append(scene)
        rows.append({
            "domain": sample["domain"],
            "scene": scene,
            "count": count,
            "target": target,
            "deficit": deficit,
            "selected": str(not skip_reason).lower(),
            "skip_reason": skip_reason,
        })

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts_path = out_dir / "dataset_backfill_counts.csv"
    with counts_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "domain", "scene", "count", "target", "deficit", "selected", "skip_reason",
        ])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (-int(row["selected"] == "true"), row["count"], row["domain"], row["scene"])))

    _write_json(out_dir / "selected_scenes.json", {"scenes": selected_scenes})
    _write_json(out_dir / "selected_samples.json", {"samples": selected_samples})

    if args.shards > 1:
        ordered = sorted(
            selected_samples,
            key=lambda sample: (
                counts[Path(sample["image_path"]).parent.name],
                sample["domain"],
                Path(sample["image_path"]).parent.name,
            ),
        )
        shards: list[list[dict]] = [[] for _ in range(args.shards)]
        for idx, sample in enumerate(ordered):
            shards[idx % args.shards].append(sample)
        for idx, shard in enumerate(shards):
            scenes = [Path(sample["image_path"]).parent.name for sample in shard]
            _write_json(out_dir / f"selected_samples_shard_{idx}.json", {"samples": shard})
            _write_json(out_dir / f"selected_scenes_shard_{idx}.json", {"scenes": scenes})

    total = sum(counts.values())
    selected_deficit = sum(max(0, args.target_per_scene - counts[scene]) for scene in selected_scenes)
    skipped = len(by_scene) - len(selected_scenes)
    print(f"dataset_total={total}")
    print(f"sample_scenes={len(by_scene)}")
    print(f"selected_scenes={len(selected_scenes)}")
    print(f"skipped_scenes={skipped}")
    print(f"selected_deficit_to_target={selected_deficit}")
    print(f"counts_csv={counts_path.as_posix()}")
    if args.shards > 1:
        print(f"shards={args.shards}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--count-root", default="dataset/images")
    parser.add_argument("--out-dir", default="reports/scene_expansion_bulk_resume_400/dataset_backfill_plan")
    parser.add_argument("--target-per-scene", type=int, default=16)
    parser.add_argument("--skip-at-least", type=int, default=12)
    parser.add_argument("--shards", type=int, default=2)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
