#!/usr/bin/env python3
"""Replace images that the user deleted from the replacement review folder."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_stratified_video_manifest import manifest_row
from scripts.materialize_video_generation_500_images import materialize, write_index
from scripts.export_video_gen_package import run as export_package


SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
SPLIT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
EXPORT_DIR = ROOT / "reports" / "video_generation_500_images"
PACKAGE_DIR = ROOT / "reports" / "video_generation_500_package"
REVIEW_DIR = ROOT / "reports" / "video_generation_500_replacement_review"
REPORT = ROOT / "reports" / "user_deleted_review_replacements.csv"

REPLACEMENTS = {
    "emerg_054": "dataset/images/extreme_emergency/emerg_reactor_runaway_pressure_release/ref_08.jpg",
    "emerg_056": "dataset/images/extreme_emergency/emerg_dam_or_retaining_wall_breach/ref_10.jpg",
    "emerg_323": "dataset/images/extreme_emergency/emerg_reactor_runaway_pressure_release/ref_09.jpg",
    "hload_120": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_06.jpg",
    "hload_217": "dataset/images/heavy_load_construction/hload_gantry_wind_disturbance/ref_41.jpg",
    "hload_218": "dataset/images/heavy_load_construction/hload_gantry_wind_disturbance/ref_24.jpg",
    "hload_227": "dataset/images/heavy_load_construction/hload_gantry_wind_disturbance/ref_10.jpg",
    "hload_228": "dataset/images/heavy_load_construction/hload_gantry_wind_disturbance/ref_18.jpg",
    "hload_230": "dataset/images/heavy_load_construction/hload_gantry_wind_disturbance/ref_11.jpg",
    "hload_235": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_04.jpg",
    "hload_242": "dataset/images/heavy_load_construction/hload_tunnel_pipe_burst_mud_surge/ref_10.jpg",
    "hload_267": "dataset/images/heavy_load_construction/hload_blind_lift_spotter_view/ref_19.jpg",
    "hload_277": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_17.jpg",
    "vsec_157": "dataset/images/visual_security/vsec_dangerous_goods_liquid_leak/ref_04.jpg",
    "vsec_193": "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_16.jpg",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value: object) -> str:
    return str(value).replace("\\", "/")


def update_payload(payload: dict, changes: list[dict]) -> None:
    by_id = {sample["task_id"]: sample for sample in payload["samples"]}
    for task_id, new_path in REPLACEMENTS.items():
        if task_id not in by_id:
            raise SystemExit(f"missing task_id: {task_id}")
        if not (ROOT / new_path).is_file():
            raise SystemExit(f"missing replacement image: {new_path}")
        sample = by_id[task_id]
        old_path = norm(sample["image_path"])
        sample["image_path"] = new_path
        changes.append({"task_id": task_id, "old_image_path": old_path, "new_image_path": new_path})


def write_manifest(split_payload: dict) -> None:
    split_id = split_payload.get("split_id", "video_generation_500_seed_5001729")
    MANIFEST.write_text(
        "\n".join(
            json.dumps(manifest_row(sample, split_id, "stratified_500"), ensure_ascii=False)
            for sample in split_payload["samples"]
        )
        + "\n",
        encoding="utf-8",
    )


def rebuild_review(changes: list[dict]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for row in changes:
        task_id = row["task_id"]
        for existing in REVIEW_DIR.glob(f"{task_id}.*"):
            existing.unlink()
        package_image = next((PACKAGE_DIR / "images").glob(f"{task_id}.*"))
        shutil.copy2(package_image, REVIEW_DIR / package_image.name)

    existing_rows = []
    index_path = REVIEW_DIR / "index.csv"
    if index_path.is_file():
        with index_path.open(encoding="utf-8-sig", newline="") as handle:
            existing_rows = list(csv.DictReader(handle))
    by_task = {row["task_id"]: row for row in existing_rows}
    for row in changes:
        task_id = row["task_id"]
        package_image = next((PACKAGE_DIR / "images").glob(f"{task_id}.*"))
        by_task[task_id] = {
            "task_id": task_id,
            "review_image": (REVIEW_DIR / package_image.name).relative_to(ROOT).as_posix(),
            "package_image": package_image.relative_to(ROOT).as_posix(),
            "current_source_image": row["new_image_path"],
            "source_reports": "user_deleted_review_replacements.csv",
        }
    with index_path.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = ["task_id", "review_image", "package_image", "current_source_image", "source_reports"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(by_task[task_id] for task_id in sorted(by_task))


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


def main() -> None:
    samples_payload = load(SAMPLES)
    split_payload = load(SPLIT)
    sample_changes: list[dict] = []
    split_changes: list[dict] = []
    update_payload(samples_payload, sample_changes)
    update_payload(split_payload, split_changes)

    image_paths = [norm(sample["image_path"]) for sample in split_payload["samples"]]
    if len(image_paths) != len(set(image_paths)):
        raise SystemExit("replacement plan would create duplicate 500 image paths")

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
        fieldnames = ["task_id", "old_image_path", "new_image_path"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(split_changes)

    print(json.dumps({
        "updated_tasks": len(split_changes),
        "removed_old_sources": len(removed),
        "report": REPORT.relative_to(ROOT).as_posix(),
        "review_dir": REVIEW_DIR.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
