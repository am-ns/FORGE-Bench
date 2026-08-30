#!/usr/bin/env python3
"""Reuse compatible formal reference images across related FORGE scenes.

The script does not copy files. It updates sample image_path values so a scene
with too few local images can also reference images from explicitly compatible
scene families. Compatibility is intentionally hand-curated and conservative.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
IMAGES_ROOT = ROOT / "dataset" / "images"
REPORT_DIR = ROOT / "reports" / "compatible_image_reuse"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


# Only scene families that can plausibly share the same reference image target.
# The receiving scene keeps its own task/prompt; only the reference image path is
# reused. Do not add broad domain-level fallback here.
COMPATIBLE_SCENES: dict[str, list[str]] = {
    # Forklift / warehouse traffic context.
    "vsec_pedestrian_forklift_near_miss": [
        "vsec_forklift_overspeed_pallet_shift",
        "erob_amr_warehouse_navigation",
    ],
    "vsec_forklift_overspeed_pallet_shift": [
        "vsec_pedestrian_forklift_near_miss",
        "erob_amr_warehouse_navigation",
    ],
    "erob_amr_warehouse_navigation": [
        "vsec_forklift_overspeed_pallet_shift",
        "vsec_pedestrian_forklift_near_miss",
        "erob_multi_robot_coordination",
    ],
    "erob_multi_robot_coordination": [
        "erob_amr_warehouse_navigation",
        "erob_robot_arm_precision_grasp",
        "erob_cobot_human_handover",
    ],

    # Robot arm / cobot / guarded robot-cell / end-effector contexts.
    "erob_robot_arm_precision_grasp": [
        "erob_cobot_human_handover",
        "erob_light_curtain_emergency_stop",
        "erob_robot_tool_contact_force",
        "erob_gripper_failure_recovery",
        "pdef_precision_assembly_misalignment",
    ],
    "erob_cobot_human_handover": [
        "erob_robot_arm_precision_grasp",
        "erob_light_curtain_emergency_stop",
        "erob_robot_tool_contact_force",
        "pdef_precision_assembly_misalignment",
    ],
    "erob_light_curtain_emergency_stop": [
        "erob_robot_arm_precision_grasp",
        "erob_cobot_human_handover",
        "erob_robot_tool_contact_force",
    ],
    "erob_robot_tool_contact_force": [
        "erob_robot_arm_precision_grasp",
        "erob_cobot_human_handover",
        "pdef_cnc_curved_surface_cutting",
        "pdef_precision_assembly_misalignment",
    ],
    "erob_gripper_failure_recovery": [
        "erob_robot_arm_precision_grasp",
        "erob_cobot_human_handover",
    ],
    "pdef_precision_assembly_misalignment": [
        "erob_robot_arm_precision_grasp",
        "erob_cobot_human_handover",
        "erob_robot_tool_contact_force",
    ],

    # Ground robot / inspection crawler contexts.
    "erob_tracked_robot_rubble": [
        "erob_quadruped_stairs_rubble_fpv",
        "erob_amr_warehouse_navigation",
    ],
    "erob_quadruped_stairs_rubble_fpv": [
        "erob_tracked_robot_rubble",
    ],

    # Crane, hoist, lifted-load, exclusion-zone contexts.
    "vsec_crane_unsafe_swing_near_people": [
        "hload_hoist_collision_near_structure",
        "emerg_crane_load_drop_evacuation",
        "hload_dual_crawler_crane_lift",
    ],
    "hload_hoist_collision_near_structure": [
        "vsec_crane_unsafe_swing_near_people",
        "emerg_crane_load_drop_evacuation",
        "hload_dual_crawler_crane_lift",
    ],
    "emerg_crane_load_drop_evacuation": [
        "vsec_crane_unsafe_swing_near_people",
        "hload_hoist_collision_near_structure",
        "hload_dual_crawler_crane_lift",
    ],
    "hload_dual_crawler_crane_lift": [
        "vsec_crane_unsafe_swing_near_people",
        "hload_hoist_collision_near_structure",
        "emerg_crane_load_drop_evacuation",
    ],
    "hload_wire_rope_overload_snap": [
        "vsec_crane_unsafe_swing_near_people",
        "hload_hoist_collision_near_structure",
        "hload_dual_crawler_crane_lift",
    ],
    "hload_gantry_wind_disturbance": [
        "hload_dual_crawler_crane_lift",
        "hload_hoist_collision_near_structure",
    ],

    # Civil structure / wall / support failure contexts.
    "emerg_dam_or_retaining_wall_breach": [
        "hload_formwork_collapse_local",
        "hload_ground_settlement_outrigger",
        "vsec_perimeter_fence_breach",
    ],
    "vsec_perimeter_fence_breach": [
        "emerg_dam_or_retaining_wall_breach",
        "vsec_guard_removed_conveyor",
    ],
    "hload_formwork_collapse_local": [
        "emerg_dam_or_retaining_wall_breach",
        "hload_ground_settlement_outrigger",
    ],

    # Fluid / smoke / thermal / pressure-release contexts.
    "vsec_smoke_alarm_evacuation": [
        "emerg_tunnel_fire_smoke_layering",
        "emerg_battery_thermal_runaway",
    ],
    "emerg_tunnel_fire_smoke_layering": [
        "vsec_smoke_alarm_evacuation",
        "emerg_battery_thermal_runaway",
    ],
    "emerg_flange_high_pressure_leak": [
        "vsec_dangerous_goods_liquid_leak",
        "emerg_reactor_runaway_pressure_release",
    ],
    "emerg_reactor_runaway_pressure_release": [
        "emerg_flange_high_pressure_leak",
        "vsec_dangerous_goods_liquid_leak",
    ],
    "hload_tunnel_pipe_burst_mud_surge": [
        "vsec_dangerous_goods_liquid_leak",
        "emerg_flange_high_pressure_leak",
    ],
    "pdef_cutting_fluid_spray": [
        "pdef_cnc_curved_surface_cutting",
    ],

    # Macro inspection / localized precision-defect contexts.
    "pdef_engine_endoscope_crack": [
        "pdef_tube_bundle_endoscopy",
        "pdef_weld_porosity_crack",
    ],
    "pdef_tube_bundle_endoscopy": [
        "pdef_engine_endoscope_crack",
    ],
    "pdef_weld_porosity_crack": [
        "pdef_surface_scratch_inspection",
        "pdef_engine_endoscope_crack",
    ],
    "pdef_gear_tooth_missing_wear": [
        "pdef_cnc_curved_surface_cutting",
        "pdef_precision_assembly_misalignment",
    ],
    "pdef_connector_pin_bent": [
        "pdef_pcb_solder_bridge_short",
    ],
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def image_paths_by_scene() -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for path in sorted(IMAGES_ROOT.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            result[path.parent.name].append(rel(path))
    return result


def dedupe_keep_order(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def build_pool(scene_id: str, local_images: dict[str, list[str]], target_unique: int) -> tuple[list[str], list[dict]]:
    pool = list(local_images.get(scene_id, []))
    source_rows: list[dict] = [
        {"target_scene": scene_id, "source_scene": scene_id, "image_path": path, "source_type": "local"}
        for path in pool
    ]
    for source_scene in COMPATIBLE_SCENES.get(scene_id, []):
        if len(dedupe_keep_order(pool)) >= target_unique:
            break
        for path in local_images.get(source_scene, []):
            if path in pool:
                continue
            pool.append(path)
            source_rows.append(
                {
                    "target_scene": scene_id,
                    "source_scene": source_scene,
                    "image_path": path,
                    "source_type": "compatible_reuse",
                }
            )
            if len(dedupe_keep_order(pool)) >= target_unique:
                break
    return dedupe_keep_order(pool), source_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-unique", type=int, default=8)
    parser.add_argument("--only-below", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples = data["samples"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        grouped[sample["scene_id"]].append(sample)

    local_images = image_paths_by_scene()
    assignment_rows: list[dict] = []
    pool_rows: list[dict] = []
    scenes_touched = 0

    for scene_id, scene_samples in sorted(grouped.items()):
        current_unique = len({sample["image_path"] for sample in scene_samples})
        if current_unique >= args.only_below:
            continue
        pool, rows = build_pool(scene_id, local_images, args.target_unique)
        pool_rows.extend(rows)
        if len(pool) <= current_unique:
            continue
        scenes_touched += 1
        for index, sample in enumerate(scene_samples):
            old_path = sample["image_path"]
            new_path = pool[index % len(pool)]
            sample["image_path"] = new_path
            assignment_rows.append(
                {
                    "task_id": sample["task_id"],
                    "scene_id": scene_id,
                    "old_image_path": old_path,
                    "new_image_path": new_path,
                    "changed": str(old_path != new_path).lower(),
                    "pool_unique": len(pool),
                }
            )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with (REPORT_DIR / "reuse_pool.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["target_scene", "source_scene", "image_path", "source_type"],
        )
        writer.writeheader()
        writer.writerows(pool_rows)
    with (REPORT_DIR / "sample_reuse_assignments.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["task_id", "scene_id", "old_image_path", "new_image_path", "changed", "pool_unique"],
        )
        writer.writeheader()
        writer.writerows(assignment_rows)

    if not args.dry_run:
        SAMPLES_PATH.write_text(
            json.dumps({"samples": samples}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    final_unique_by_scene = {
        scene_id: len({sample["image_path"] for sample in scene_samples})
        for scene_id, scene_samples in grouped.items()
    }
    print(f"dry_run={args.dry_run}")
    print(f"scenes_touched={scenes_touched}")
    print(f"sample_assignments={len(assignment_rows)}")
    print(f"changed_assignments={sum(1 for row in assignment_rows if row['changed'] == 'true')}")
    print(f"global_unique_image_paths={len({sample['image_path'] for sample in samples})}")
    print("low_unique_after=")
    for scene_id, count in sorted(final_unique_by_scene.items(), key=lambda item: (item[1], item[0])):
        if count < args.only_below:
            print(f"  {scene_id}: {count}")
    print(f"reports={REPORT_DIR.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
