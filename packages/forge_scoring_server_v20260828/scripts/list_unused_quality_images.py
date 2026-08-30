#!/usr/bin/env python3
"""List unused dataset images sorted by quality for a domain or scene filter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_stratified_video_manifest import image_metrics

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contains", default="")
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--split", default="dataset/annotations/video_generation_500_samples.json")
    args = parser.parse_args()

    split = json.loads(repo_path(args.split).read_text(encoding="utf-8"))
    used = {str(sample["image_path"]).replace("\\", "/") for sample in split["samples"]}
    rows = []
    for path in (ROOT / "dataset" / "images").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in used:
            continue
        if args.contains and args.contains not in rel:
            continue
        metrics = image_metrics(path)
        if int(metrics["short_side"]) < 680:
            continue
        rows.append((float(metrics["quality_score"]), rel, metrics))
    rows.sort(reverse=True)
    for score, rel, metrics in rows[: args.limit]:
        print(
            f"{score:6.1f} short={metrics['short_side']} sharp={metrics['laplacian_var']:.1f} {rel}"
        )


if __name__ == "__main__":
    main()
