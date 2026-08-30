#!/usr/bin/env python3
"""List images in selected scene folders that are not used by the 500 split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_dirs", nargs="+")
    parser.add_argument("--split", default="dataset/annotations/video_generation_500_samples.json")
    args = parser.parse_args()

    data = json.loads(repo_path(args.split).read_text(encoding="utf-8"))
    used = {str(sample["image_path"]).replace("\\", "/") for sample in data["samples"]}
    for value in args.scene_dirs:
        scene_dir = repo_path(value)
        print(f"[{scene_dir.relative_to(ROOT).as_posix()}]")
        for path in sorted(scene_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                rel = path.relative_to(ROOT).as_posix()
                if rel not in used:
                    print(rel)


if __name__ == "__main__":
    main()
