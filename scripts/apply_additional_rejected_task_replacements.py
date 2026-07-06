#!/usr/bin/env python3
"""Replace an additional user-specified set of rejected 500-task images."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_stratified_video_manifest import manifest_row
from scripts.export_video_gen_package import run as export_package
from scripts.materialize_video_generation_500_images import materialize, write_index


SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
SPLIT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
EXPORT_DIR = ROOT / "reports" / "video_generation_500_images"
PACKAGE_DIR = ROOT / "reports" / "video_generation_500_package"
REVIEW_DIR = ROOT / "reports" / "video_generation_500_replacement_review"
REPORT = ROOT / "reports" / "additional_rejected_task_replacements.csv"

REPLACEMENTS = {
    "hload_220": "dataset/images/heavy_load_construction/hload_blind_lift_spotter_view/ref_18.jpg",
    "pdef_063": "dataset/images/precision_defect_gen/pdef_gear_tooth_missing_wear/ref_14.jpg",
    "pdef_065": "dataset/images/precision_defect_gen/pdef_flange_seal_micro_leak/ref_01.jpg",
    "pdef_145": "dataset/images/precision_defect_gen/pdef_gauge_level_valve_anomaly/ref_12.jpg",
    "pdef_216": "dataset/images/precision_defect_gen/pdef_tube_bundle_endoscopy/ref_12.jpg",
    "vsec_111": "dataset/images/visual_security/vsec_unregistered_vehicle_intrusion/ref_09.jpg",
    "vsec_193": "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_09.jpg",
    "emerg_133": "dataset/images/extreme_emergency/emerg_cooling_tower_plume_failure/ref_24.jpg",
    "emerg_002": "dataset/images/extreme_emergency/emerg_flange_high_pressure_leak/ref_08.jpg",
    "emerg_212": "dataset/images/extreme_emergency/emerg_storage_tank_flash_fire/ref_08.jpg",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value: object) -> str:
    return str(value).replace("\\", "/")


def update_payload(payload: dict) -> list[dict]:
    by_id = {sample["task_id"]: sample for sample in payload["samples"]}
    changes = []
    for task_id, new_path in REPLACEMENTS.items():
        if task_id not in by_id:
            raise SystemExit(f"missing task_id: {task_id}")
        if not (ROOT / new_path).is_file():
            raise SystemExit(f"missing replacement image: {new_path}")
        sample = by_id[task_id]
        old_path = norm(sample["image_path"])
        sample["image_path"] = new_path
        changes.append({"task_id": task_id, "old_image_path": old_path, "new_image_path": new_path})
    return changes


def write_manifest(split_payload: dict) -> None:
    split_id = split_payload.get("split_id", "video_generation_500_seed_5001729")
    rows = [manifest_row(sample, split_id, "stratified_500") for sample in split_payload["samples"]]
    MANIFEST.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def remove_unreferenced_old_sources(changes: list[dict], *payloads: dict) -> list[str]:
    referenced = {
        norm(sample.get("image_path", ""))
        for payload in payloads
        for sample in payload["samples"]
    }
    removed = []
    for old_path in {row["old_image_path"] for row in changes}:
        if old_path in referenced:
            continue
        path = ROOT / old_path
        if path.is_file():
            path.unlink()
            removed.append(old_path)
    return sorted(removed)


def rebuild_review(changes: list[dict]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    index_path = REVIEW_DIR / "index.csv"
    existing_rows = []
    if index_path.is_file():
        with index_path.open(encoding="utf-8-sig", newline="") as handle:
            existing_rows = list(csv.DictReader(handle))
    by_task = {row["task_id"]: row for row in existing_rows}
    for row in changes:
        task_id = row["task_id"]
        for old_review in REVIEW_DIR.glob(f"{task_id}.*"):
            old_review.unlink()
        package_image = next((PACKAGE_DIR / "images").glob(f"{task_id}.*"))
        review_image = REVIEW_DIR / package_image.name
        shutil.copy2(package_image, review_image)
        by_task[task_id] = {
            "task_id": task_id,
            "review_image": review_image.relative_to(ROOT).as_posix(),
            "package_image": package_image.relative_to(ROOT).as_posix(),
            "current_source_image": row["new_image_path"],
            "source_reports": "additional_rejected_task_replacements.csv",
        }
    with index_path.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = ["task_id", "review_image", "package_image", "current_source_image", "source_reports"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(by_task[task_id] for task_id in sorted(by_task))


def main() -> None:
    samples_payload = load(SAMPLES)
    split_payload = load(SPLIT)
    update_payload(samples_payload)
    split_changes = update_payload(split_payload)

    paths = [norm(sample["image_path"]) for sample in split_payload["samples"]]
    if len(paths) != len(set(paths)):
        raise SystemExit("replacement plan creates duplicate image paths")

    removed = remove_unreferenced_old_sources(split_changes, samples_payload, split_payload)

    SAMPLES.write_text(json.dumps(samples_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SPLIT.write_text(json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = materialize(split_payload["samples"], EXPORT_DIR)
    write_index(rows, EXPORT_DIR)
    write_manifest(split_payload)

    class Args:
        samples = str(SPLIT)
        output_dir = str(PACKAGE_DIR)

    export_package(Args)
    rebuild_review(split_changes)

    with REPORT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "old_image_path", "new_image_path"])
        writer.writeheader()
        writer.writerows(split_changes)

    print(json.dumps({
        "updated_tasks": len(split_changes),
        "removed_old_sources": len(removed),
        "report": REPORT.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
