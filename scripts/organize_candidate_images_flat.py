#!/usr/bin/env python3
"""Flatten the current image candidate pool and remove obvious rejects."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


REJECTS = {
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0002.jpg": "hot_work_scene_mismatch_no_sparks_or_fire",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0003.jpg": "hot_work_scene_mismatch_pipe_interior",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0004.jpg": "hot_work_scene_mismatch_general_construction",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0005.jpg": "hot_work_scene_mismatch_general_construction",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0007.jpg": "hot_work_scene_mismatch_pipe_interior",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0008.jpg": "hot_work_scene_mismatch_sculpture",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0025.jpg": "hot_work_scene_mismatch_historical_photo",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0027.jpg": "hot_work_scene_mismatch_crowd_photo",
    "dataset/images_candidates/emerg_hot_work_spark_combustible_fire__commons_category__0030.jpg": "hot_work_scene_mismatch_building_exterior",
    "dataset/images_candidates/fast_multisource_smoke_20260607/emerg_hot_work_spark_combustible_fire__commons__0002.jpg": "hot_work_scene_mismatch_fighter_jet",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0001.jpg": "amr_scene_mismatch_signage",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0002.jpg": "amr_scene_mismatch_equipment_cabinet",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0003.jpg": "amr_scene_mismatch_connector_closeup",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0004.jpg": "amr_scene_mismatch_building_exterior",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0005.jpg": "amr_scene_mismatch_building_exterior",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0006.jpg": "amr_scene_mismatch_train",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0009.jpg": "amr_scene_mismatch_aircraft",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0013.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0016.jpg": "amr_scene_mismatch_train",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons__0017.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0001.jpg": "amr_scene_mismatch_product_closeup",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0082.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0083.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0093.jpg": "amr_scene_mismatch_empty_machine_room",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0094.jpg": "amr_scene_mismatch_lift_platform",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0095.jpg": "amr_scene_mismatch_container_yard",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0098.jpg": "amr_scene_mismatch_medical_kiosk",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0099.jpg": "amr_scene_mismatch_robot_demo",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0106.jpg": "amr_scene_mismatch_robot_demo",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0107.jpg": "amr_scene_mismatch_diagram",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0108.jpg": "amr_scene_mismatch_toy_vehicle",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0109.jpg": "amr_scene_mismatch_robot_demo",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0113.jpg": "amr_scene_mismatch_robot_demo",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0118.jpg": "amr_scene_mismatch_robot_toy",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0123.jpg": "amr_scene_mismatch_nonwarehouse_service_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0132.jpg": "amr_scene_mismatch_child_toy",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0135.jpg": "amr_scene_mismatch_police_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0136.jpg": "amr_scene_mismatch_tracked_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0140.jpg": "amr_scene_mismatch_outdoor_robot_demo",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0149.jpg": "amr_scene_mismatch_outdoor_delivery_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0156.png": "amr_scene_mismatch_render",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0158.png": "amr_scene_mismatch_render",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0159.jpg": "amr_scene_mismatch_outdoor_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0162.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0168.jpg": "amr_scene_mismatch_toy_vehicle",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0171.jpg": "amr_scene_mismatch_exhibit_space",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0177.jpg": "amr_scene_mismatch_toy_robot",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0181.jpg": "amr_scene_mismatch_circuit_board",
    "dataset/images_candidates/erob_amr_warehouse_navigation__commons_category__0182.jpg": "amr_scene_mismatch_robot_kit",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0003.jpg": "gripper_scene_mismatch_pencil_closeup",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0012.jpg": "gripper_scene_mismatch_pencil_closeup",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0013.jpg": "gripper_scene_mismatch_stage_photo",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0014.jpg": "gripper_scene_mismatch_tool_closeup",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0016.jpg": "gripper_scene_mismatch_shoes",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0021.jpg": "gripper_scene_mismatch_camera_accessory",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0022.jpg": "gripper_scene_mismatch_leather_handles",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0025.jpg": "gripper_scene_mismatch_light_panel",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0026.jpg": "gripper_scene_mismatch_light_panel",
    "dataset/images_candidates/erob_gripper_failure_recovery__commons__0035.jpg": "near_duplicate_dataset",
    "dataset/images_candidates/pdef_surface_scratch_inspection__commons__0001.jpg": "surface_defect_scene_mismatch_archaeology_sample",
    "dataset/images_candidates/pdef_surface_scratch_inspection__commons__0002.jpg": "surface_defect_scene_mismatch_mineral_sample",
    "dataset/images_candidates/pdef_surface_scratch_inspection__commons__0004.jpg": "surface_defect_scene_mismatch_artifact_sample",
    "dataset/images_candidates/pdef_surface_scratch_inspection__commons_category__0014.jpg": "near_duplicate_dataset",
}


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def as_rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def iter_images(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def unique_dest(output_root: Path, source: Path) -> Path:
    dest = output_root / source.name
    if not dest.exists():
        return dest
    index = 2
    while True:
        candidate = output_root / f"{source.stem}__dup{index}{source.suffix.lower()}"
        if not candidate.exists():
            return candidate
        index += 1


def remove_empty_dirs(root: Path, output_root: Path) -> int:
    removed = 0
    for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
        if path == output_root or output_root.is_relative_to(path):
            continue
        try:
            path.rmdir()
            removed += 1
        except OSError:
            pass
    return removed


def run(args: argparse.Namespace) -> None:
    candidate_root = repo_path(args.candidate_root).resolve()
    output_root = repo_path(args.output_root).resolve()
    manifest = repo_path(args.manifest)
    allowed_root = (ROOT / "dataset" / "images_candidates").resolve()
    if not candidate_root.is_relative_to(allowed_root):
        raise ValueError(f"candidate_root must stay inside {allowed_root}")
    if not output_root.is_relative_to(candidate_root) or output_root == candidate_root:
        raise ValueError("output_root must be a child of candidate_root")

    output_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    moved = 0
    deleted = 0
    missing_rejects = set(REJECTS)

    for source in iter_images(candidate_root):
        if source.resolve().is_relative_to(output_root):
            continue
        rel = as_rel(source)
        reason = REJECTS.get(rel)
        if reason:
            if not args.dry_run:
                source.unlink()
            deleted += 1
            missing_rejects.discard(rel)
            rows.append({"status": "deleted", "reason": reason, "source_path": rel, "dest_path": ""})
            continue

        dest = unique_dest(output_root, source)
        if not args.dry_run:
            shutil.move(str(source), str(dest))
        moved += 1
        rows.append({"status": "kept", "reason": "kept", "source_path": rel, "dest_path": as_rel(dest)})

    removed_dirs = 0 if args.dry_run else remove_empty_dirs(candidate_root, output_root)

    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "reason", "source_path", "dest_path"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"kept_moved={moved}")
    print(f"deleted={deleted}")
    print(f"empty_dirs_removed={removed_dirs}")
    print(f"missing_reject_entries={len(missing_rejects)}")
    print(f"output_root={as_rel(output_root)}")
    print(f"manifest={as_rel(manifest)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", default="dataset/images_candidates")
    parser.add_argument("--output-root", default="dataset/images_candidates/curated_flat_20260607")
    parser.add_argument("--manifest", default="reports/images_candidates_flat_cleanup_20260607/flat_manifest.csv")
    parser.add_argument("--dry-run", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
