#!/usr/bin/env python3
"""Deduplicate and conservatively organize dataset/images.

The script only edits files under dataset/images. It does not modify
dataset/annotations/samples.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "dataset" / "images"
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
REPORT_DIR = ROOT / "reports"

SCENE_DOMAINS = {
    "visual_security",
    "embodied_robotics",
    "heavy_load_construction",
    "precision_defect_gen",
    "extreme_emergency",
}

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}

SCENE_KEYWORDS = {
    "vsec_unregistered_vehicle_intrusion": {
        "gate", "loading", "dock", "vehicle", "truck", "road", "restricted", "security", "yard"
    },
    "vsec_missing_ppe_at_height": {
        "aerial", "platform", "scaffold", "height", "boom", "worker", "construction"
    },
    "vsec_forklift_overspeed_pallet_shift": {
        "forklift", "pallet", "warehouse", "truck", "agv", "vehicle", "load"
    },
    "vsec_crane_unsafe_swing_near_people": {
        "crane", "hook", "lift", "load", "tower", "mobile", "crawler", "construction"
    },
    "vsec_surveillance_blind_spot_sweep": {
        "warehouse", "aisle", "gate", "dock", "surveillance", "server", "rack"
    },
    "vsec_perimeter_fence_breach": {"fence", "gate", "barrier", "guardrail", "perimeter"},
    "vsec_dangerous_goods_liquid_leak": {
        "chemical", "storage", "tank", "pipe", "piping", "solvent", "pressure", "vessel", "leak"
    },
    "vsec_pedestrian_forklift_near_miss": {
        "forklift", "pedestrian", "warehouse", "aisle", "truck", "vehicle"
    },
    "vsec_smoke_alarm_evacuation": {"smoke", "alarm", "corridor", "battery", "server", "room"},
    "vsec_guard_removed_conveyor": {"conveyor", "guard", "machine", "rotating", "line"},
    "erob_robot_arm_precision_grasp": {"robot", "arm", "industrial", "gripper", "manipulator"},
    "erob_cobot_human_handover": {"cobot", "collaborative", "robot", "human", "handover", "station"},
    "erob_tracked_robot_rubble": {"tracked", "crawler", "robot", "rubble", "inspection", "pipe"},
    "erob_quadruped_stairs_rubble_fpv": {"quadruped", "anymal", "legged", "robot", "stairs", "rubble"},
    "erob_amr_warehouse_navigation": {"amr", "agv", "autonomous", "mobile", "robot", "warehouse"},
    "erob_light_curtain_emergency_stop": {"light", "curtain", "emergency", "stop", "robot", "cell", "press"},
    "erob_robot_tool_contact_force": {"robot", "welding", "sanding", "drilling", "polishing", "tool"},
    "erob_multi_robot_coordination": {"multi", "swarm", "fleet", "agv", "robot", "coordination"},
    "erob_gripper_failure_recovery": {"gripper", "suction", "end", "effector", "robot", "grasp"},
    "hload_dual_crawler_crane_lift": {"dual", "crawler", "crane", "lift", "suspended", "module"},
    "hload_wire_rope_overload_snap": {"wire", "rope", "sling", "hoist", "cable", "hook"},
    "hload_mining_truck_muddy_slope": {"mining", "haul", "truck", "muddy", "slope", "dump"},
    "hload_gantry_wind_disturbance": {"gantry", "container", "bridge", "crane", "portal"},
    "hload_bridge_segment_alignment_drone": {"bridge", "segment", "beam", "viaduct", "precast"},
    "hload_excavator_linkage_loading": {"excavator", "loader", "hydraulic", "bucket", "soil"},
    "hload_ground_settlement_outrigger": {"outrigger", "support", "pad", "ground", "settlement", "crane"},
    "hload_tunnel_pipe_burst_mud_surge": {"tunnel", "pipe", "burst", "mud", "trench", "excavation"},
    "hload_hoist_collision_near_structure": {"hoist", "hook", "lifted", "load", "scaffold", "structure"},
    "hload_formwork_collapse_local": {"formwork", "scaffold", "support", "shoring", "concrete"},
    "pdef_pcb_solder_bridge_short": {"pcb", "circuit", "solder", "electronics", "trace", "board"},
    "pdef_engine_endoscope_crack": {"endoscope", "borescope", "engine", "turbine", "pipe", "cavity"},
    "pdef_gear_tooth_missing_wear": {"gear", "tooth", "teeth", "sprocket", "rack", "hobbing"},
    "pdef_cnc_curved_surface_cutting": {"cnc", "milling", "axis", "machining", "spindle", "fixture"},
    "pdef_cutting_fluid_spray": {"cutting", "fluid", "coolant", "spray", "tool", "machining"},
    "pdef_weld_porosity_crack": {"weld", "welding", "porosity", "crack", "seam", "pipe"},
    "pdef_surface_scratch_inspection": {"scratch", "surface", "polished", "wafer", "bearing", "inspection"},
    "pdef_tube_bundle_endoscopy": {"tube", "bundle", "heat", "exchanger", "borescope", "endoscopy"},
    "pdef_connector_pin_bent": {"connector", "pin", "terminal", "socket", "wire", "bond"},
    "pdef_precision_assembly_misalignment": {"assembly", "bearing", "shaft", "fixture", "jig", "precision"},
    "emerg_flange_high_pressure_leak": {"flange", "pressure", "leak", "valve", "pipe", "pipeline"},
    "emerg_storage_tank_flash_fire": {"storage", "tank", "fire", "refinery", "oil", "gas"},
    "emerg_transmission_tower_icing_collapse": {"transmission", "tower", "pylon", "ice", "high", "voltage"},
    "emerg_dust_explosion_confined_space": {"dust", "explosion", "silo", "collector", "confined", "workshop"},
    "emerg_reactor_runaway_pressure_release": {"reactor", "pressure", "relief", "vessel", "chemical"},
    "emerg_battery_thermal_runaway": {"battery", "thermal", "charging", "energy", "container"},
    "emerg_tunnel_fire_smoke_layering": {"tunnel", "fire", "smoke", "mine", "corridor", "conveyor"},
    "emerg_crane_load_drop_evacuation": {"crane", "load", "drop", "hook", "lift", "evacuation"},
    "emerg_cooling_tower_plume_failure": {"cooling", "tower", "plume", "steam", "condenser"},
    "emerg_dam_or_retaining_wall_breach": {"dam", "retaining", "wall", "tailings", "berm", "barrier"},
}


def _load_samples() -> list[dict]:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))["samples"]


def _iter_images() -> list[Path]:
    return sorted(
        p for p in IMAGE_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tokens(path: Path) -> set[str]:
    text = f"{path.parent.name} {path.stem}".lower()
    return {
        token
        for token in re.split(r"[^a-z0-9]+", text)
        if len(token) >= 3
    }


def _is_scene_domain(path: Path) -> bool:
    try:
        rel = path.relative_to(IMAGE_ROOT)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in SCENE_DOMAINS


def _is_canonical_scene_name(path: Path) -> bool:
    if not _is_scene_domain(path):
        return False
    rel = path.relative_to(IMAGE_ROOT)
    if len(rel.parts) >= 3:
        scene_id = rel.parts[1]
        return bool(
            re.match(r"^[a-z0-9]+_[a-z0-9_]+$", scene_id)
            and re.match(r"^(ref|strict|loss|feishu)_\d{1,2}\.(jpg|png)$", path.name.lower())
        )
    return bool(re.match(r"^[a-z0-9]+_[a-z0-9_]+__ref_\d{2}\.(jpg|png)$", path.name.lower()))


def _is_deprecated_variant(path: Path, referenced: set[str]) -> bool:
    """Return true for non-sample loss/strict variants kept from old imports."""
    return (
        path.name.startswith(("loss_", "strict_"))
        and _norm_rel(path) not in referenced
    )


def _norm_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _keep_score(path: Path, referenced: set[str]) -> int:
    rel = _norm_rel(path)
    score = 0
    if rel in referenced:
        score += 10000
    if _is_canonical_scene_name(path):
        score += 1000
    if not _is_scene_domain(path):
        score += 500
    if "__" not in path.name:
        score += 100
    if re.match(r"^[a-z0-9_]+\.(jpg|png)$", path.name.lower()):
        score += 50
    score -= len(path.name)
    return score


def _duplicate_actions(images: list[Path], referenced: set[str]) -> tuple[list[dict], set[Path]]:
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for path in images:
        by_hash[_sha256(path)].append(path)

    rows: list[dict] = []
    delete_paths: set[Path] = set()
    for digest, paths in sorted(by_hash.items()):
        if len(paths) < 2:
            continue
        keep = sorted(paths, key=lambda p: (-_keep_score(p, referenced), _norm_rel(p)))[0]
        for path in paths:
            rel = _norm_rel(path)
            action = "keep"
            reason = "selected_keep"
            if path != keep:
                if rel in referenced:
                    action = "keep"
                    reason = "referenced_duplicate_not_deleted"
                else:
                    action = "delete"
                    reason = "exact_duplicate_nonpreferred_name"
                    delete_paths.add(path)
            rows.append({
                "sha256": digest,
                "action": action,
                "reason": reason,
                "path": rel,
                "kept_path": _norm_rel(keep),
                "referenced_by_samples": str(rel in referenced).lower(),
                "canonical_scene_name": str(_is_canonical_scene_name(path)).lower(),
                "keep_score": _keep_score(path, referenced),
            })
    for path in images:
        if _is_deprecated_variant(path, referenced) and path not in delete_paths:
            delete_paths.add(path)
            rows.append({
                "sha256": _sha256(path),
                "action": "delete",
                "reason": "deprecated_loss_or_strict_variant",
                "path": _norm_rel(path),
                "kept_path": "",
                "referenced_by_samples": "false",
                "canonical_scene_name": "false",
                "keep_score": _keep_score(path, referenced),
            })
    return rows, delete_paths


def _image_ok(path: Path) -> tuple[bool, str, int, int]:
    try:
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
    except Exception as exc:
        return False, f"decode_error:{exc}", 0, 0
    if min(width, height) < 500:
        return False, "short_side_below_500", width, height
    if width * height < 600_000:
        return False, "pixel_count_below_600k", width, height
    return True, "ok", width, height


def _scene_domain(scene_id: str, samples: list[dict]) -> str:
    for sample in samples:
        if sample.get("scene_id") == scene_id:
            return sample["domain"]
    prefix_domain = {
        "vsec": "visual_security",
        "erob": "embodied_robotics",
        "hload": "heavy_load_construction",
        "pdef": "precision_defect_gen",
        "emerg": "extreme_emergency",
    }
    return prefix_domain[scene_id.split("_", 1)[0]]


def _next_ref_index(scene_id: str, domain: str) -> int:
    out_dir = IMAGE_ROOT / domain / scene_id
    existing = []
    for path in out_dir.glob("ref_*"):
        match = re.search(r"ref_(\d+)", path.stem)
        if match:
            existing.append(int(match.group(1)))
    return (max(existing) if existing else 0) + 1


def _candidate_actions(
    images: list[Path],
    duplicate_deletes: set[Path],
    samples: list[dict],
    max_per_scene: int,
    min_score: int,
) -> list[dict]:
    existing_hashes_by_scene: dict[str, set[str]] = defaultdict(set)
    assigned_sources: set[Path] = set()
    rows: list[dict] = []

    for path in images:
        if _is_scene_domain(path):
            rel = path.relative_to(IMAGE_ROOT)
            scene_id = ""
            if len(rel.parts) >= 3:
                scene_id = rel.parts[1]
            elif "__ref_" in path.name and "__" in path.name:
                scene_id = path.name.split("__", 1)[0]
            if scene_id:
                existing_hashes_by_scene[scene_id].add(_sha256(path))

    pool = [
        path for path in images
        if not _is_scene_domain(path) and path not in duplicate_deletes
    ]
    sample_scenes = sorted({sample["scene_id"] for sample in samples})
    scene_domains = {scene_id: _scene_domain(scene_id, samples) for scene_id in sample_scenes}

    selected_by_scene: dict[str, int] = defaultdict(int)
    next_index_by_scene = {
        scene_id: _next_ref_index(scene_id, scene_domains[scene_id])
        for scene_id in sample_scenes
    }
    scored: list[tuple[int, str, Path, set[str]]] = []
    for path in pool:
        ok, reason, width, height = _image_ok(path)
        if not ok:
            rows.append({
                "action": "skip",
                "reason": reason,
                "source_path": _norm_rel(path),
                "dest_path": "",
                "scene_id": "",
                "score": 0,
                "matched_tokens": "",
                "width": width,
                "height": height,
            })
            continue
        tokens = _tokens(path)
        for scene_id in sample_scenes:
            matched = tokens & SCENE_KEYWORDS.get(scene_id, set())
            score = len(matched)
            if score >= min_score:
                scored.append((score, scene_id, path, matched))

    for score, scene_id, path, matched in sorted(scored, key=lambda item: (-item[0], item[1], _norm_rel(item[2]))):
        if path in assigned_sources:
            continue
        if selected_by_scene[scene_id] >= max_per_scene:
            continue
        digest = _sha256(path)
        if digest in existing_hashes_by_scene[scene_id]:
            rows.append({
                "action": "delete_source_duplicate",
                "reason": "source_already_exists_in_scene",
                "source_path": _norm_rel(path),
                "dest_path": "",
                "scene_id": scene_id,
                "score": score,
                "matched_tokens": " ".join(sorted(matched)),
                "width": "",
                "height": "",
            })
            assigned_sources.add(path)
            continue
        domain = scene_domains[scene_id]
        suffix = ".jpg" if path.suffix.lower() in {".jpg", ".jpeg"} else ".png"
        dest = IMAGE_ROOT / domain / scene_id / f"ref_{next_index_by_scene[scene_id]:02d}{suffix}"
        next_index_by_scene[scene_id] += 1
        rows.append({
            "action": "move_to_scene",
            "reason": "filename_tokens_match_scene",
            "source_path": _norm_rel(path),
            "dest_path": _norm_rel(dest),
            "scene_id": scene_id,
            "score": score,
            "matched_tokens": " ".join(sorted(matched)),
            "width": "",
            "height": "",
        })
        assigned_sources.add(path)
        selected_by_scene[scene_id] += 1
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _apply_duplicate_deletes(rows: list[dict]) -> int:
    count = 0
    for row in rows:
        if row["action"] != "delete":
            continue
        path = ROOT / row["path"]
        if path.exists() and path.is_file() and path.resolve().is_relative_to(IMAGE_ROOT.resolve()):
            path.unlink()
            count += 1
    return count


def _apply_candidate_moves(rows: list[dict]) -> tuple[int, int]:
    moved = 0
    removed = 0
    for row in rows:
        if row["action"] == "move_to_scene":
            source = ROOT / row["source_path"]
            dest = ROOT / row["dest_path"]
            if source.exists() and source.is_file() and source.resolve().is_relative_to(IMAGE_ROOT.resolve()):
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.move(str(source), str(dest))
                    moved += 1
        elif row["action"] == "delete_source_duplicate":
            source = ROOT / row["source_path"]
            if source.exists() and source.is_file() and source.resolve().is_relative_to(IMAGE_ROOT.resolve()):
                source.unlink()
                removed += 1
    return moved, removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize dataset image library.")
    parser.add_argument("--apply", action="store_true", help="Apply deletes and moves.")
    parser.add_argument("--max-per-scene", type=int, default=2)
    parser.add_argument("--min-score", type=int, default=2)
    args = parser.parse_args()

    samples = _load_samples()
    referenced = {sample["image_path"] for sample in samples}
    images = _iter_images()

    duplicate_rows, duplicate_deletes = _duplicate_actions(images, referenced)
    candidate_rows = _candidate_actions(
        images=images,
        duplicate_deletes=duplicate_deletes,
        samples=samples,
        max_per_scene=args.max_per_scene,
        min_score=args.min_score,
    )

    _write_csv(REPORT_DIR / "image_library_duplicate_actions.csv", duplicate_rows)
    _write_csv(REPORT_DIR / "image_library_candidate_actions.csv", candidate_rows)

    deleted = moved = removed_sources = 0
    if args.apply:
        deleted = _apply_duplicate_deletes(duplicate_rows)
        moved, removed_sources = _apply_candidate_moves(candidate_rows)

    print(f"images_scanned={len(images)}")
    print(f"duplicate_groups={len({row['sha256'] for row in duplicate_rows})}")
    print(f"duplicate_delete_candidates={sum(1 for row in duplicate_rows if row['action'] == 'delete')}")
    print(f"candidate_moves={sum(1 for row in candidate_rows if row['action'] == 'move_to_scene')}")
    print(f"candidate_source_duplicate_deletes={sum(1 for row in candidate_rows if row['action'] == 'delete_source_duplicate')}")
    print(f"applied={str(args.apply).lower()} duplicate_deleted={deleted} moved_to_scene={moved} source_duplicates_deleted={removed_sources}")
    print("reports/image_library_duplicate_actions.csv")
    print("reports/image_library_candidate_actions.csv")


if __name__ == "__main__":
    main()
