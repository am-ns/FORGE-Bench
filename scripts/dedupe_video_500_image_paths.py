#!/usr/bin/env python3
"""Replace duplicate image paths in the 500 split with unused high-quality images."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_stratified_video_manifest import image_metrics, manifest_row
from scripts.materialize_video_generation_500_images import materialize, write_index


SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
SPLIT = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
EXPORT_DIR = ROOT / "reports" / "video_generation_500_images"
MANIFEST = ROOT / "reports" / "video_generation_500_manifest.jsonl"
REPORT = ROOT / "reports" / "video_generation_500_dedupe_replacements.csv"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

REJECTED_PATHS = {
    "dataset/images/embodied_robotics/erob_quadruped_stairs_rubble_fpv/ref_07.jpg",
    "dataset/images/embodied_robotics/erob_tracked_robot_rubble/ref_17.jpg",
    "dataset/images/extreme_emergency/emerg_battery_thermal_runaway/ref_11.jpg",
    "dataset/images/extreme_emergency/emerg_hot_work_spark_combustible_fire/ref_03.jpg",
    "dataset/images/heavy_load_construction/hload_blind_lift_spotter_view/ref_33.jpg",
    "dataset/images/heavy_load_construction/hload_dual_crawler_crane_lift/ref_16.jpg",
    "dataset/images/heavy_load_construction/hload_ground_settlement_outrigger/ref_14.jpg",
    "dataset/images/heavy_load_construction/hload_ground_settlement_outrigger/ref_15.jpg",
    "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_08.jpg",
    "dataset/images/heavy_load_construction/hload_hoist_collision_near_structure/ref_10.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_03.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_04.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_05.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_06.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_08.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_09.jpg",
    "dataset/images/heavy_load_construction/hload_sling_angle_center_of_gravity/ref_11.jpg",
    "dataset/images/heavy_load_construction/hload_tunnel_pipe_burst_mud_surge/ref_16.jpg",
    "dataset/images/heavy_load_construction/hload_wire_rope_overload_snap/ref_09.jpg",
    "dataset/images/precision_defect_gen/pdef_cnc_curved_surface_cutting/ref_01.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_05.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_06.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_07.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_08.jpg",
    "dataset/images/precision_defect_gen/pdef_weld_porosity_crack/ref_11.jpg",
    "dataset/images/visual_security/vsec_conveyor_jam_loto_clearance/ref_03.jpg",
    "dataset/images/visual_security/vsec_crane_unsafe_swing_near_people/ref_13.jpg",
    "dataset/images/visual_security/vsec_crane_unsafe_swing_near_people/ref_15.jpg",
    "dataset/images/visual_security/vsec_dangerous_goods_liquid_leak/ref_11.jpg",
    "dataset/images/visual_security/vsec_dangerous_goods_liquid_leak/ref_14.jpg",
    "dataset/images/visual_security/vsec_electrical_cabinet_smoke_isolation/ref_01.jpg",
    "dataset/images/visual_security/vsec_surveillance_blind_spot_sweep/ref_15.jpg",
}

MANUAL_REPLACEMENTS = {
    "emerg_308": "dataset/images/extreme_emergency/emerg_dust_explosion_confined_space/ref_18.jpg",
    "emerg_323": "dataset/images/extreme_emergency/emerg_hot_work_spark_combustible_fire/ref_07.jpg",
    "hload_281": "dataset/images/heavy_load_construction/hload_wire_rope_overload_snap/ref_16.jpg",
}


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(payload: dict) -> list[dict]:
    return payload["samples"]


def norm(value: object) -> str:
    return str(value).replace("\\", "/")


def image_candidates() -> list[dict]:
    candidates = []
    for path in (ROOT / "dataset" / "images").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in REJECTED_PATHS:
            continue
        metrics = image_metrics(path)
        if int(metrics["short_side"]) < 680:
            continue
        parts = Path(rel).parts
        candidates.append({
            "path": rel,
            "domain": parts[2],
            "scene_id": parts[3],
            "score": float(metrics["quality_score"]),
            "short_side": int(metrics["short_side"]),
            "sharpness": float(metrics["laplacian_var"]),
        })
    candidates.sort(key=lambda item: (item["score"], item["short_side"], item["sharpness"]), reverse=True)
    return candidates


def pick_replacement(sample: dict, used: set[str], candidates: list[dict]) -> dict:
    manual_path = MANUAL_REPLACEMENTS.get(str(sample["task_id"]))
    if manual_path:
        if manual_path in used:
            raise SystemExit(f"manual replacement already used: {manual_path}")
        metrics = image_metrics(ROOT / manual_path)
        return {
            "path": manual_path,
            "domain": Path(manual_path).parts[2],
            "scene_id": Path(manual_path).parts[3],
            "score": float(metrics["quality_score"]),
            "short_side": int(metrics["short_side"]),
            "sharpness": float(metrics["laplacian_var"]),
        }
    scene = str(sample["scene_id"])
    domain = str(sample["domain"])
    for candidate in candidates:
        if candidate["path"] not in used and candidate["scene_id"] == scene:
            return candidate
    for candidate in candidates:
        if candidate["path"] not in used and candidate["domain"] == domain:
            return candidate
    raise SystemExit(f"no replacement candidate for {sample['task_id']}")


def update_other_payload(payload: dict, replacements: dict[str, str]) -> None:
    for sample in rows(payload):
        task_id = str(sample.get("task_id"))
        if task_id in replacements:
            sample["image_path"] = replacements[task_id]


def write_outputs(split_payload: dict) -> None:
    split_samples = rows(split_payload)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for path in EXPORT_DIR.iterdir():
        if path.is_file() and path.name != "index.csv" and path.name != "index.json":
            path.unlink()
    export_rows = materialize(split_samples, EXPORT_DIR)
    write_index(export_rows, EXPORT_DIR)
    split_id = split_payload.get("split_id", "video_generation_500_seed_5001729")
    MANIFEST.write_text(
        "\n".join(json.dumps(manifest_row(sample, split_id, "stratified_500"), ensure_ascii=False) for sample in split_samples) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    split_payload = load_payload(SPLIT)
    split_rows = rows(split_payload)
    counts = Counter(norm(sample["image_path"]) for sample in split_rows)
    duplicate_paths = {path for path, count in counts.items() if count > 1}
    used = {norm(sample["image_path"]) for sample in split_rows}
    candidates = image_candidates()
    changes = []
    replacements: dict[str, str] = {}

    seen_duplicate_paths: set[str] = set()
    for sample in split_rows:
        current = norm(sample["image_path"])
        if current not in duplicate_paths:
            continue
        if current not in seen_duplicate_paths:
            seen_duplicate_paths.add(current)
            continue
        replacement = pick_replacement(sample, used, candidates)
        used.add(replacement["path"])
        replacements[str(sample["task_id"])] = replacement["path"]
        changes.append({
            "task_id": sample["task_id"],
            "old_image_path": current,
            "new_image_path": replacement["path"],
            "new_short_side": replacement["short_side"],
            "new_sharpness": f"{replacement['sharpness']:.1f}",
        })
        sample["image_path"] = replacement["path"]

    with REPORT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "old_image_path", "new_image_path", "new_short_side", "new_sharpness"])
        writer.writeheader()
        writer.writerows(changes)

    if args.apply:
        samples_payload = load_payload(SAMPLES)
        update_other_payload(samples_payload, replacements)
        SAMPLES.write_text(json.dumps(samples_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        SPLIT.write_text(json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_outputs(split_payload)

    final_unique = len({norm(sample["image_path"]) for sample in split_rows})
    print(json.dumps({
        "apply": args.apply,
        "changes": len(changes),
        "final_unique_images": final_unique,
        "report": REPORT.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
