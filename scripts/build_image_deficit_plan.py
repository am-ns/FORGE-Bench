#!/usr/bin/env python3
"""Build a scene-level image deficit plan from the formal image library."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _image_count(scene_dir: Path) -> int:
    if not scene_dir.exists():
        return 0
    return sum(1 for path in scene_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)


def _write_text_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _acquire_lock(path: Path, stale_seconds: float) -> int:
    try:
        return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if time.time() - path.stat().st_mtime <= stale_seconds:
            raise RuntimeError(f"deficit plan is already being rebuilt: {path}")
        path.unlink()
        return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)


def run(args: argparse.Namespace) -> None:
    samples = _load_samples(Path(args.samples))
    by_scene: dict[str, dict] = {}
    for sample in samples:
        scene = sample.get("scene_id")
        domain = sample.get("domain")
        if scene and domain and scene not in by_scene:
            by_scene[str(scene)] = {
                "scene_id": str(scene),
                "domain": str(domain),
                "application_type": str(sample.get("application_type") or ""),
                "task_category": str(sample.get("task_category") or ""),
                "reference_subject": str(sample.get("reference_subject") or ""),
                "image_requirement": str(sample.get("image_requirement") or ""),
            }

    rows = []
    image_root = Path(args.image_root)
    for scene, row in sorted(by_scene.items()):
        count = _image_count(image_root / row["domain"] / scene)
        deficit = max(0, args.target_per_scene - count)
        item = dict(row)
        item["image_count"] = count
        item["target_per_scene"] = args.target_per_scene
        item["deficit"] = deficit
        item["selected"] = deficit > 0
        rows.append(item)

    selected = [row for row in rows if row["selected"]]
    if args.max_scenes > 0:
        selected = selected[:args.max_scenes]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lock_path = out_dir / ".build.lock"
    lock_fd = _acquire_lock(lock_path, args.lock_stale_seconds)
    os.close(lock_fd)
    csv_path = out_dir / "image_deficit_plan.csv"
    try:
        csv_tmp = csv_path.with_suffix(csv_path.suffix + ".tmp")
        with csv_tmp.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["scene_id"])
            writer.writeheader()
            writer.writerows(rows)
        os.replace(csv_tmp, csv_path)

        selected_json = {"scenes": [row["scene_id"] for row in selected]}
        _write_text_atomic(out_dir / "selected_scenes.json", json.dumps(selected_json, indent=2) + "\n")
        _write_text_atomic(
            out_dir / "selected_scenes.txt",
            "\n".join(row["scene_id"] for row in selected) + ("\n" if selected else ""),
        )

        for stale in out_dir.glob("selected_scenes_shard_*.json"):
            stale.unlink()
        shards: list[list[str]] = [[] for _ in range(max(1, args.shards))]
        for idx, row in enumerate(selected):
            shards[idx % len(shards)].append(row["scene_id"])
        for idx, scenes in enumerate(shards):
            payload = {"scenes": scenes}
            _write_text_atomic(
                out_dir / f"selected_scenes_shard_{idx}.json",
                json.dumps(payload, indent=2) + "\n",
            )
    finally:
        lock_path.unlink(missing_ok=True)

    print(f"scenes_total={len(rows)}")
    print(f"selected_scenes={len(selected)}")
    print(f"target_per_scene={args.target_per_scene}")
    print(f"total_deficit={sum(int(row['deficit']) for row in selected)}")
    print(f"out_dir={out_dir.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--out-dir", default="reports/image_deficit_plan")
    parser.add_argument("--target-per-scene", type=int, default=16)
    parser.add_argument("--shards", type=int, default=4)
    parser.add_argument("--max-scenes", type=int, default=0)
    parser.add_argument("--lock-stale-seconds", type=float, default=3600.0)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
