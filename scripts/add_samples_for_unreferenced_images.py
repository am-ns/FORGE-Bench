#!/usr/bin/env python3
"""Add one sample for every formal image that is not referenced by samples.json."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.import_screened_image_candidates import _clone_sample, _next_task_id

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _load_samples(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_samples(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _iter_images(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def run(args: argparse.Namespace) -> None:
    samples_path = Path(args.samples)
    image_root = Path(args.image_root)
    report_path = Path(args.report)
    if not samples_path.is_absolute():
        samples_path = REPO_ROOT / samples_path
    if not image_root.is_absolute():
        image_root = REPO_ROOT / image_root
    if not report_path.is_absolute():
        report_path = REPO_ROOT / report_path

    data = _load_samples(samples_path)
    samples = data["samples"]
    scene_samples: dict[str, list[dict]] = defaultdict(list)
    scene_domain: dict[str, str] = {}
    referenced = set()
    for sample in samples:
        scene = str(sample.get("scene_id") or "")
        domain = str(sample.get("domain") or "")
        image_path = str(sample.get("image_path") or "").replace("\\", "/")
        if scene and domain:
            scene_samples[scene].append(sample)
            scene_domain[scene] = domain
        if image_path:
            referenced.add(image_path)

    task_counters: dict[str, int] = {}
    rows = []
    added = []
    for path in _iter_images(image_root):
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        if rel_path in referenced:
            continue
        rel_parts = path.relative_to(image_root).parts
        if len(rel_parts) < 3:
            rows.append({
                "status": "skipped",
                "reason": "unexpected_image_path_shape",
                "image_path": rel_path,
                "scene_id": "",
                "domain": "",
                "task_id": "",
            })
            continue
        domain, scene = rel_parts[0], rel_parts[1]
        if scene_domain.get(scene) != domain or not scene_samples.get(scene):
            rows.append({
                "status": "skipped",
                "reason": "scene_mapping_unresolved",
                "image_path": rel_path,
                "scene_id": scene,
                "domain": domain,
                "task_id": "",
            })
            continue
        task_id = _next_task_id(samples, domain, task_counters)
        new_sample = _clone_sample(scene_samples[scene][0], task_id, rel_path)
        samples.append(new_sample)
        scene_samples[scene].append(new_sample)
        referenced.add(rel_path)
        added.append(new_sample)
        rows.append({
            "status": "accepted",
            "reason": "sample_added",
            "image_path": rel_path,
            "scene_id": scene,
            "domain": domain,
            "task_id": task_id,
        })

    samples.sort(key=lambda item: item["task_id"])
    if added and not args.dry_run:
        data["samples"] = samples
        _write_samples(samples_path, data)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["status", "reason", "image_path", "scene_id", "domain", "task_id"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"image_root={image_root.relative_to(REPO_ROOT).as_posix()}")
    print(f"existing_samples={len(samples) - len(added)}")
    print(f"unreferenced_images={len(rows)}")
    print(f"samples_added={len(added)}")
    print(f"skipped={sum(1 for row in rows if row['status'] != 'accepted')}")
    print(f"dry_run={args.dry_run}")
    print(f"report={report_path.relative_to(REPO_ROOT).as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--image-root", default="dataset/images")
    parser.add_argument("--report", default="reports/add_samples_for_unreferenced_images.csv")
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
