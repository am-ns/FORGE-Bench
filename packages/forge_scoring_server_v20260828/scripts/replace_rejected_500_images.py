#!/usr/bin/env python3
"""Replace rejected 500-split images and remove rejected source files."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_stratified_video_manifest import manifest_row
from scripts.materialize_video_generation_500_images import materialize, write_index


SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
SPLIT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
EXPORT_DIR = ROOT / "reports" / "video_generation_500_images"
REPORT = ROOT / "reports" / "rejected_500_image_replacements.csv"

REPLACEMENTS = {
    "erob_031": "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_11.jpg",
    "erob_024": "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_06.jpg",
    "emerg_308": "dataset/images/extreme_emergency/emerg_battery_thermal_runaway/ref_13.jpg",
    "emerg_323": "dataset/images/extreme_emergency/emerg_hot_work_spark_combustible_fire/ref_12.jpg",
    "hload_267": "dataset/images/heavy_load_construction/hload_blind_lift_spotter_view/ref_20.jpg",
    "hload_235": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_05.jpg",
    "hload_226": "dataset/images/heavy_load_construction/hload_ground_settlement_outrigger/ref_03.jpg",
    "hload_236": "dataset/images/heavy_load_construction/hload_ground_settlement_outrigger/ref_09.jpg",
    "hload_120": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_01.jpg",
    "hload_277": "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_02.jpg",
    "hload_217": "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_10.jpg",
    "hload_218": "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_12.jpg",
    "hload_227": "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_02.jpg",
    "hload_228": "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_14.jpg",
    "hload_230": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_02.jpg",
    "hload_231": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_11.jpg",
    "hload_233": "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_13.jpg",
    "hload_242": "dataset/images/heavy_load_construction/hload_blind_lift_spotter_view/ref_16.jpg",
    "hload_281": "dataset/images/heavy_load_construction/hload_wire_rope_overload_snap/ref_02.jpg",
    "pdef_031": "dataset/images/precision_defect_gen/pdef_cnc_curved_surface_cutting/ref_03.jpg",
    "pdef_053": "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_09.jpg",
    "pdef_054": "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_16.jpg",
    "pdef_056": "dataset/images/precision_defect_gen/pdef_flange_seal_micro_leak/ref_16.jpg",
    "pdef_057": "dataset/images/precision_defect_gen/pdef_gear_tooth_missing_wear/ref_07.jpg",
    "pdef_058": "dataset/images/precision_defect_gen/pdef_cnc_curved_surface_cutting/ref_02.jpg",
    "vsec_175": "dataset/images/visual_security/vsec_conveyor_jam_loto_clearance/ref_16.jpg",
    "vsec_141": "dataset/images/visual_security/vsec_crane_unsafe_swing_near_people/ref_03.jpg",
    "vsec_146": "dataset/images/visual_security/vsec_crane_unsafe_swing_near_people/ref_05.jpg",
    "vsec_115": "dataset/images/visual_security/vsec_dangerous_goods_liquid_leak/ref_08.jpg",
    "vsec_157": "dataset/images/visual_security/vsec_dangerous_goods_liquid_leak/ref_07.jpg",
    "vsec_131": "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_03.jpg",
    "vsec_170": "dataset/images/visual_security/vsec_surveillance_blind_spot_sweep/ref_05.jpg",
}


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def samples_list(payload: dict) -> list[dict]:
    return payload["samples"] if isinstance(payload, dict) else payload


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def update_payload(payload: dict, rows: list[dict]) -> tuple[dict, list[dict]]:
    by_id = {sample["task_id"]: sample for sample in samples_list(payload)}
    missing = sorted(set(REPLACEMENTS) - set(by_id))
    if missing:
        raise SystemExit(f"missing task ids in payload: {missing}")
    old_paths: dict[str, str] = {}
    for task_id, new_path in REPLACEMENTS.items():
        if not (ROOT / new_path).is_file():
            raise SystemExit(f"replacement image missing: {new_path}")
        sample = by_id[task_id]
        old_path = normalize(str(sample["image_path"]))
        old_paths[task_id] = old_path
        sample["image_path"] = new_path
    for task_id, old_path in old_paths.items():
        rows.append({"task_id": task_id, "old_image_path": old_path, "new_image_path": REPLACEMENTS[task_id]})
    return payload, rows


def write_payload(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def referenced_paths(*payloads: dict) -> set[str]:
    paths = set()
    for payload in payloads:
        for sample in samples_list(payload):
            image_path = sample.get("image_path")
            if image_path:
                paths.add(normalize(str(image_path)))
    return paths


def remove_rejected_sources(rows: list[dict], remaining_refs: set[str]) -> list[str]:
    removed = []
    for row in rows:
        old_path = row["old_image_path"]
        if old_path in remaining_refs:
            continue
        path = ROOT / old_path
        if path.is_file():
            path.unlink()
            removed.append(old_path)
    return removed


def write_manifest(samples: list[dict], split_id: str) -> None:
    rows = [manifest_row(sample, split_id, "stratified_500") for sample in samples]
    MANIFEST.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_report(rows: list[dict], removed: list[str]) -> None:
    removed_set = set(removed)
    with REPORT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["task_id", "old_image_path", "new_image_path", "removed_old_source"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "removed_old_source": row["old_image_path"] in removed_set})


def main() -> None:
    samples_payload = load_payload(SAMPLES)
    split_payload = load_payload(SPLIT)
    rows: list[dict] = []
    samples_payload, rows = update_payload(samples_payload, rows)
    split_payload, rows = update_payload(split_payload, [])

    remaining_refs = referenced_paths(samples_payload, split_payload)
    removed = remove_rejected_sources(rows, remaining_refs)

    write_payload(SAMPLES, samples_payload)
    write_payload(SPLIT, split_payload)

    split_id = split_payload.get("split_id", "video_generation_500_seed_5001729")
    split_samples = samples_list(split_payload)
    rows_for_export = materialize(split_samples, EXPORT_DIR)
    write_index(rows_for_export, EXPORT_DIR)
    write_manifest(split_samples, split_id)
    write_report(rows, removed)

    print(json.dumps({
        "updated_tasks": len(REPLACEMENTS),
        "removed_old_sources": len(removed),
        "replacement_report": REPORT.relative_to(ROOT).as_posix(),
        "exported_images": len(rows_for_export),
        "unique_export_source_images": len({row["source_image_path"] for row in rows_for_export}),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
