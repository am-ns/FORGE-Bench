#!/usr/bin/env python3
"""Rollback imported candidate images and samples into a review staging folder."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from pathlib import Path


def _accepted_rows(manifest_paths: list[Path]) -> list[dict]:
    rows = []
    seen = set()
    for manifest in manifest_paths:
        if not manifest.exists():
            continue
        with manifest.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                dest = (row.get("dest_path") or "").replace("\\", "/")
                task_id = row.get("task_id") or ""
                if row.get("status") == "accepted" and dest and (dest, task_id) not in seen:
                    rows.append(row)
                    seen.add((dest, task_id))
    return rows


def run(args: argparse.Namespace) -> None:
    repo_root = Path(args.repo_root).resolve()
    samples_path = repo_root / args.samples
    review_root = repo_root / args.review_root
    manifests = [repo_root / item for item in args.manifests]
    rows = _accepted_rows(manifests)
    imported_task_ids = {row["task_id"] for row in rows if row.get("task_id")}
    imported_paths = {row["dest_path"].replace("\\", "/") for row in rows}

    data = json.loads(samples_path.read_text(encoding="utf-8"))
    samples = data["samples"]
    kept = [sample for sample in samples if sample.get("task_id") not in imported_task_ids]
    removed = len(samples) - len(kept)

    moved = 0
    for rel in sorted(imported_paths):
        src = repo_root / rel
        if not src.resolve().is_relative_to((repo_root / "dataset" / "images").resolve()):
            raise ValueError(f"refusing to move image outside dataset/images: {src}")
        if not src.exists():
            continue
        dst = review_root / rel
        if not dst.resolve().is_relative_to(review_root.resolve()):
            raise ValueError(f"refusing to move image outside review root: {dst}")
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        moved += 1

    if not args.dry_run and removed:
        data["samples"] = kept
        tmp = samples_path.with_suffix(samples_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, samples_path)

    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["task_id", "dest_path", "source_path", "scene_id", "domain"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    print(f"accepted_manifest_rows={len(rows)}")
    print(f"removed_samples={removed}")
    print(f"moved_images={moved}")
    print(f"review_root={review_root.as_posix()}")
    print(f"report={report_path.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument(
        "--manifests",
        nargs="+",
        default=[
            "reports/screened_image_candidate_import.csv",
            "reports/screened_image_candidate_second_pass.csv",
        ],
    )
    parser.add_argument("--review-root", default="reports/imported_candidate_review_staging")
    parser.add_argument("--report", default="reports/imported_candidate_rollback.csv")
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
