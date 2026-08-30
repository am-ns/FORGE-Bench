#!/usr/bin/env python3
"""Launch scene-expansion candidate search in parallel shards."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(args: argparse.Namespace) -> None:
    output_root = Path(args.output_dir)
    report_root = Path(args.report_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    per_worker_target = max(1, (args.target_new + args.workers - 1) // args.workers)
    processes: list[tuple[int, subprocess.Popen]] = []
    for shard in range(args.workers):
        cmd = [
            sys.executable,
            "scripts/expand_scene_image_library.py",
            "--target-new", str(per_worker_target),
            "--per-scene", str(args.per_scene),
            "--search-limit", str(args.search_limit),
            "--sources", args.sources,
            "--sleep", str(args.sleep),
            "--manifest", str(report_root / f"scene_image_expansion_bulk_200_worker_{shard}.csv"),
            "--output-dir", str(output_root / f"worker_{shard}"),
            "--min-topic-score", str(args.min_topic_score),
            "--max-rejections-per-scene", str(args.max_rejections_per_scene),
            "--scene-shards", str(args.workers),
            "--scene-shard-index", str(shard),
            "--min-width", str(args.min_width),
            "--min-height", str(args.min_height),
        ]
        if args.domains:
            cmd.extend(["--domains", args.domains])
        if args.no_strong_match:
            cmd.append("--no-strong-match")
        if args.basic_only:
            cmd.append("--basic-only")
        print("launch", shard, " ".join(cmd), flush=True)
        processes.append((shard, subprocess.Popen(cmd)))

    failures = 0
    for shard, process in processes:
        code = process.wait()
        print(f"worker {shard} exited {code}", flush=True)
        if code != 0:
            failures += 1
    if failures:
        raise SystemExit(f"{failures} workers failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--target-new", type=int, default=200)
    parser.add_argument("--per-scene", type=int, default=10)
    parser.add_argument("--search-limit", type=int, default=10)
    parser.add_argument("--sources", default="openverse")
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--min-topic-score", type=int, default=0)
    parser.add_argument("--max-rejections-per-scene", type=int, default=80)
    parser.add_argument("--no-strong-match", action="store_true")
    parser.add_argument("--min-width", type=int, default=1080)
    parser.add_argument("--min-height", type=int, default=720)
    parser.add_argument("--basic-only", action="store_true")
    parser.add_argument("--domains", default="")
    parser.add_argument("--output-dir", default="dataset/images_candidates/scene_expansion_bulk_200_parallel")
    parser.add_argument("--report-dir", default="reports/scene_expansion_bulk_200_parallel")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
