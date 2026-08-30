#!/usr/bin/env python3
"""Copy the 500 video-generation reference images into one review folder."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPLIT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
DEFAULT_OUT = ROOT / "reports" / "video_generation_500_images"


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data.get("samples", data) if isinstance(data, dict) else data
    if not isinstance(samples, list):
        raise ValueError("split file must contain a list or a {'samples': [...]} object")
    return samples


def safe_part(value: object) -> str:
    text = str(value or "unknown")
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in text)


def materialize(samples: list[dict], output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    seen_names: set[str] = set()
    for index, sample in enumerate(samples, start=1):
        source_rel = str(sample["image_path"]).replace("\\", "/")
        source = repo_path(source_rel)
        if not source.exists():
            raise FileNotFoundError(source_rel)
        base_name = "__".join(
            [
                f"{index:03d}",
                safe_part(sample["task_id"]),
                safe_part(sample["domain"]),
                safe_part(sample["scene_id"]),
                safe_part(source.name),
            ]
        )
        if base_name in seen_names:
            base_name = f"{index:03d}__{safe_part(sample['task_id'])}__{safe_part(source.name)}"
        seen_names.add(base_name)
        dest = output_dir / base_name
        shutil.copy2(source, dest)
        rows.append(
            {
                "index": index,
                "task_id": sample["task_id"],
                "domain": sample["domain"],
                "scene_id": sample["scene_id"],
                "task_category": sample["task_category"],
                "motion_type": sample["motion_type"],
                "source_image_path": source_rel,
                "exported_image_path": dest.relative_to(ROOT).as_posix(),
            }
        )
    return rows


def write_index(rows: list[dict], output_dir: Path) -> None:
    fields = [
        "index",
        "task_id",
        "domain",
        "scene_id",
        "task_category",
        "motion_type",
        "source_image_path",
        "exported_image_path",
    ]
    csv_path = output_dir / "index.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    json_path = output_dir / "index.json"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default=str(DEFAULT_SPLIT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    split_path = repo_path(args.split)
    output_dir = repo_path(args.output_dir)
    samples = load_samples(split_path)
    rows = materialize(samples, output_dir)
    write_index(rows, output_dir)
    print(json.dumps({
        "output_dir": output_dir.relative_to(ROOT).as_posix(),
        "images": len(rows),
        "unique_source_images": len({row["source_image_path"] for row in rows}),
        "index_csv": (output_dir / "index.csv").relative_to(ROOT).as_posix(),
        "index_json": (output_dir / "index.json").relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
