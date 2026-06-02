#!/usr/bin/env python3
"""Copy cross-scene references into target scenes and rebuild all prompts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rebuild_generation_prompts import build_evaluation_prompt, build_prompt


DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_REPORT = ROOT / "reports" / "scene_image_reference_normalization.csv"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _scene_from_image_path(image_path: str) -> str:
    parts = image_path.replace("\\", "/").split("/")
    return parts[3] if len(parts) >= 5 else ""


def _next_image_path(scene_dir: Path, suffix: str, reserved: set[Path]) -> Path:
    indices = []
    if scene_dir.exists():
        for path in scene_dir.iterdir():
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
                continue
            match = re.fullmatch(r"ref_(\d+)", path.stem, flags=re.IGNORECASE)
            if match:
                indices.append(int(match.group(1)))
    index = max(indices, default=0) + 1
    destination = scene_dir / f"ref_{index:02d}{suffix.lower()}"
    while destination in reserved or destination.exists():
        index += 1
        destination = scene_dir / f"ref_{index:02d}{suffix.lower()}"
    reserved.add(destination)
    return destination


def _copy_cross_scene_references(samples: list[dict], dry_run: bool) -> list[dict]:
    copied: dict[tuple[str, str], str] = {}
    reserved: set[Path] = set()
    rows = []
    for sample in samples:
        old_path = str(sample["image_path"]).replace("\\", "/")
        target_scene = sample["scene_id"]
        if _scene_from_image_path(old_path) == target_scene:
            continue
        key = (target_scene, old_path)
        if key not in copied:
            source = ROOT / old_path
            if not source.is_file():
                raise FileNotFoundError(f"Missing referenced image: {old_path}")
            scene_dir = ROOT / "dataset" / "images" / sample["domain"] / target_scene
            if not dry_run:
                scene_dir.mkdir(parents=True, exist_ok=True)
            destination = _next_image_path(scene_dir, source.suffix, reserved)
            if not dry_run:
                shutil.copy2(source, destination)
            copied[key] = _rel(destination)
        sample["image_path"] = copied[key]
        rows.append(
            {
                "task_id": sample["task_id"],
                "scene_id": target_scene,
                "old_image_path": old_path,
                "new_image_path": copied[key],
            }
        )
    return rows


def _rebuild_prompts(samples: list[dict]) -> None:
    for sample in samples:
        sample["evaluation_prompt"] = build_evaluation_prompt(sample)
        sample["prompt"] = sample["evaluation_prompt"]
        sample["video_generation_prompt"] = build_prompt(sample)


def run(args: argparse.Namespace) -> None:
    samples_path = Path(args.samples)
    report_path = Path(args.report)
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    rows = _copy_cross_scene_references(samples, args.dry_run)
    _rebuild_prompts(samples)

    if not args.dry_run:
        tmp = samples_path.with_suffix(samples_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, samples_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["task_id", "scene_id", "old_image_path", "new_image_path"],
            )
            writer.writeheader()
            writer.writerows(rows)

    print(f"samples={len(samples)}")
    print(f"cross_scene_samples_rebound={len(rows)}")
    print(f"copied_images={len({row['new_image_path'] for row in rows})}")
    print(f"dry_run={str(args.dry_run).lower()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
