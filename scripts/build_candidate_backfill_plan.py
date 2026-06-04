#!/usr/bin/env python3
"""Build scene lists for candidate image backfill.

The output is intentionally small JSON/CSV files that can be reused by
parallel download scripts. It does not download or delete images.
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
    counts = _image_counts(Path(args.candidate_root))

    by_scene: dict[str, dict] = {}
    for sample in samples:
        scene = Path(sample["image_path"]).parent.name
        by_scene.setdefault(scene, sample)

    rows = []
    low_samples = []
    low_scenes = []
    for scene, sample in sorted(by_scene.items()):
        count = counts[scene]
        deficit = max(0, args.target_per_scene - count)
        row = {
            "domain": sample["domain"],
            "scene": scene,
            "count": count,
            "target": args.target_per_scene,
            "deficit": deficit,
        }
        rows.append(row)
        if deficit > 0:
            low_samples.append(sample)
            low_scenes.append(scene)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts_path = out_dir / "candidate_backfill_counts.csv"
    with counts_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "scene", "count", "target", "deficit"])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (-row["deficit"], row["domain"], row["scene"])))

    _write_json(out_dir / "low_count_scenes.json", {"scenes": low_scenes})
    _write_json(out_dir / "low_count_samples.json", {"samples": low_samples})

    if args.shards > 1:
        ordered = sorted(low_samples, key=lambda sample: (-max(0, args.target_per_scene - counts[Path(sample["image_path"]).parent.name]), sample["domain"], Path(sample["image_path"]).parent.name))
        shards: list[list[dict]] = [[] for _ in range(args.shards)]
        for idx, sample in enumerate(ordered):
            shards[idx % args.shards].append(sample)
        for idx, shard in enumerate(shards):
            scenes = [Path(sample["image_path"]).parent.name for sample in shard]
            _write_json(out_dir / f"low_count_samples_shard_{idx}.json", {"samples": shard})
            _write_json(out_dir / f"low_count_scenes_shard_{idx}.json", {"scenes": scenes})

    total = sum(counts.values())
    print(f"candidate_total={total}")
    print(f"sample_scenes={len(by_scene)}")
    print(f"low_scenes={len(low_scenes)}")
    print(f"counts_csv={counts_path.as_posix()}")
    if args.shards > 1:
        print(f"shards={args.shards}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--candidate-root", default="dataset/images_candidates/scene_expansion_bulk_resume_400")
    parser.add_argument("--out-dir", default="reports/scene_expansion_bulk_resume_400/backfill_plan")
    parser.add_argument("--target-per-scene", type=int, default=8)
    parser.add_argument("--shards", type=int, default=4)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
