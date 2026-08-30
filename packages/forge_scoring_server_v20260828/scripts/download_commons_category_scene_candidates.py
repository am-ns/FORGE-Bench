#!/usr/bin/env python3
"""Download scene candidates from curated Wikimedia Commons categories."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

from find_reference_images import (
    _average_hash,
    _download,
    _hamming_hex,
    _image_metrics,
    _license_ok,
    _mime_ok,
    _url_ok,
)


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "FORGE-Bench Commons category candidate downloader/1.0"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
BLOCKED_TERMS = (
    "book", "cover", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "logo", "manual", "catalog", "catalogue",
    "journal", "magazine", "newspaper", "volume", "page", "plate",
    "pdf", "djvu", "svg", "blueprint", "schematic", "flowchart",
    "icon", "symbol", "toy", "miniature", "model", "illustration",
    "infographic", "advertisement", "brochure", "patent", "cartoon",
)


SCENE_CATEGORIES = {
    "visual_security/vsec_unregistered_vehicle_intrusion": [
        "Security gates", "Industrial buildings", "Trucks",
    ],
    "visual_security/vsec_missing_ppe_at_height": [
        "Aerial work platforms", "Fall arrest", "Construction workers",
    ],
    "visual_security/vsec_forklift_overspeed_pallet_shift": [
        "Forklifts", "Warehouses", "Pallets",
    ],
    "visual_security/vsec_crane_unsafe_swing_near_people": [
        "Cranes", "Construction sites", "Construction workers",
    ],
    "visual_security/vsec_surveillance_blind_spot_sweep": [
        "Surveillance cameras", "Warehouses", "Security cameras",
    ],
    "visual_security/vsec_perimeter_fence_breach": [
        "Fences", "Security fences", "Industrial fences",
    ],
    "visual_security/vsec_dangerous_goods_liquid_leak": [
        "Chemical plants", "Chemical storage tanks", "Industrial piping",
    ],
    "visual_security/vsec_pedestrian_forklift_near_miss": [
        "Forklifts", "Warehouses", "Factory floors",
    ],
    "visual_security/vsec_smoke_alarm_evacuation": [
        "Industrial buildings", "Smoke detectors", "Fire alarms",
    ],
    "visual_security/vsec_guard_removed_conveyor": [
        "Conveyor belts", "Industrial conveyors", "Machine guards",
    ],
    "embodied_robotics/erob_robot_arm_precision_grasp": [
        "Industrial robots", "Robotic arms", "Robot grippers",
    ],
    "embodied_robotics/erob_cobot_human_handover": [
        "Collaborative robots", "Industrial robots",
    ],
    "embodied_robotics/erob_tracked_robot_rubble": [
        "Tracked robots", "Robots",
    ],
    "embodied_robotics/erob_quadruped_stairs_rubble_fpv": [
        "Quadrupedal robots", "Robots",
    ],
    "embodied_robotics/erob_amr_warehouse_navigation": [
        "Autonomous mobile robots", "Mobile robots", "Warehouse robots",
    ],
    "embodied_robotics/erob_light_curtain_emergency_stop": [
        "Industrial robots", "Machine safety",
    ],
    "embodied_robotics/erob_robot_tool_contact_force": [
        "Industrial robots", "Robot welding", "Robotic arms",
    ],
    "embodied_robotics/erob_gripper_failure_recovery": [
        "Robot grippers", "Industrial robots",
    ],
    "precision_defect_gen/pdef_cnc_curved_surface_cutting": [
        "CNC machines", "Milling machines", "Machine tools",
    ],
    "precision_defect_gen/pdef_pcb_solder_bridge_short": [
        "Printed circuit boards", "Surface-mount technology",
    ],
    "precision_defect_gen/pdef_gear_tooth_missing_wear": [
        "Gears", "Gear wheels",
    ],
    "precision_defect_gen/pdef_weld_porosity_crack": [
        "Welding", "Welded joints", "Pipe welding",
    ],
    "precision_defect_gen/pdef_surface_scratch_inspection": [
        "Metalworking", "Surface finishing", "Scratches",
    ],
    "precision_defect_gen/pdef_tube_bundle_endoscopy": [
        "Heat exchangers", "Tube bundles",
    ],
    "precision_defect_gen/pdef_connector_pin_bent": [
        "Electrical connectors", "Connectors",
    ],
    "precision_defect_gen/pdef_precision_assembly_misalignment": [
        "Bearings", "Shafts", "Machine tools",
    ],
    "precision_defect_gen/pdef_engine_endoscope_crack": [
        "Endoscopy", "Aircraft engines", "Engine maintenance",
    ],
    "precision_defect_gen/pdef_cutting_fluid_spray": [
        "Cutting fluids", "CNC machines", "Machine tools",
    ],
    "heavy_load_construction/hload_dual_crawler_crane_lift": [
        "Crawler cranes", "Construction cranes", "Heavy lift cranes",
    ],
    "heavy_load_construction/hload_wire_rope_overload_snap": [
        "Wire ropes", "Crane hooks", "Cranes",
    ],
    "heavy_load_construction/hload_mining_truck_muddy_slope": [
        "Mining trucks", "Dump trucks", "Muddy roads",
    ],
    "heavy_load_construction/hload_gantry_wind_disturbance": [
        "Gantry cranes", "Container cranes", "Container terminals",
    ],
    "heavy_load_construction/hload_bridge_segment_alignment_drone": [
        "Bridge construction", "Precast concrete", "Construction cranes",
    ],
    "heavy_load_construction/hload_excavator_linkage_loading": [
        "Excavators", "Hydraulic excavators", "Excavator buckets",
    ],
    "heavy_load_construction/hload_ground_settlement_outrigger": [
        "Crane outriggers", "Mobile cranes", "Construction sites",
    ],
    "heavy_load_construction/hload_tunnel_pipe_burst_mud_surge": [
        "Pipeline construction", "Trenches", "Construction sites",
    ],
    "heavy_load_construction/hload_hoist_collision_near_structure": [
        "Hoists", "Construction cranes", "Construction sites",
    ],
    "heavy_load_construction/hload_formwork_collapse_local": [
        "Formwork", "Scaffolding", "Construction sites",
    ],
    "extreme_emergency/emerg_flange_high_pressure_leak": [
        "Pipe flanges", "Industrial piping", "Chemical plants",
    ],
    "extreme_emergency/emerg_storage_tank_flash_fire": [
        "Storage tanks", "Tank farms", "Refineries",
    ],
    "extreme_emergency/emerg_transmission_tower_icing_collapse": [
        "Transmission towers", "Power lines in snow", "Ice storms",
    ],
    "extreme_emergency/emerg_dust_explosion_confined_space": [
        "Grain silos", "Dust collectors", "Industrial buildings",
    ],
    "extreme_emergency/emerg_reactor_runaway_pressure_release": [
        "Chemical reactors", "Pressure vessels", "Chemical plants",
    ],
    "extreme_emergency/emerg_battery_thermal_runaway": [
        "Battery energy storage systems", "Lithium-ion batteries", "Battery rooms",
    ],
    "extreme_emergency/emerg_tunnel_fire_smoke_layering": [
        "Tunnels", "Industrial tunnels", "Underground corridors",
    ],
    "extreme_emergency/emerg_crane_load_drop_evacuation": [
        "Cranes", "Construction sites", "Suspended loads",
    ],
    "extreme_emergency/emerg_cooling_tower_plume_failure": [
        "Cooling towers", "Power plants", "Steam plumes",
    ],
    "extreme_emergency/emerg_dam_or_retaining_wall_breach": [
        "Retaining walls", "Dams", "Containment berms",
    ],
}


def _url_json(params: dict, timeout: float) -> dict:
    url = f"{COMMONS_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _category_members(category: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    rows: list[dict] = []
    cont: dict[str, str] = {}
    while len(rows) < limit:
        params = {
            "action": "query",
            "format": "json",
            "generator": "categorymembers",
            "gcmtitle": f"Category:{category}",
            "gcmnamespace": "6",
            "gcmtype": "file",
            "gcmlimit": str(min(50, limit - len(rows))),
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": "1600",
            **cont,
        }
        data = _url_json(params, timeout)
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            infos = page.get("imageinfo") or []
            if infos:
                rows.append({
                    "title": page.get("title", ""),
                    "pageid": str(page.get("pageid", "")),
                    "imageinfo": infos[0],
                })
        cont = data.get("continue", {})
        if sleep_s:
            time.sleep(sleep_s)
        if not cont:
            break
    return rows


def _title_ok(title: str) -> tuple[bool, str]:
    tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
    lowered = title.lower()
    for term in BLOCKED_TERMS:
        if " " in term:
            if term in lowered:
                return False, f"blocked_term:{term}"
        elif term in tokens:
            return False, f"blocked_term:{term}"
    return True, ""


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_bit_count(_hamming_hex(ahash, old)) <= max_distance for old in seen_hashes)


def _write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _existing_hashes(candidate_roots: list[Path]) -> list[str]:
    hashes: list[str] = []
    roots = [Path("dataset/images"), *candidate_roots]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                try:
                    hashes.append(_average_hash(path))
                except Exception:
                    pass
    return hashes


def _next_candidate_path(output_dir: Path, scene_key: str, suffix: str) -> Path:
    scene_dir = output_dir / scene_key
    scene_dir.mkdir(parents=True, exist_ok=True)
    max_idx = 0
    for path in scene_dir.iterdir():
        if not path.is_file() or not path.stem.startswith("ref_"):
            continue
        try:
            max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
        except ValueError:
            pass
    return scene_dir / f"ref_{max_idx + 1:02d}{suffix.lower()}"


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    manifest = Path(args.manifest)
    rows: list[dict[str, str]] = []
    candidate_roots = [Path(item) for item in args.candidate_roots]
    seen_hashes = _existing_hashes([output_dir, *candidate_roots])
    accepted = 0
    allowed_scenes = None
    if args.scenes_file:
        scene_data = json.loads(Path(args.scenes_file).read_text(encoding="utf-8"))
        allowed_scenes = set(scene_data["scenes"] if isinstance(scene_data, dict) else scene_data)

    scene_items = [
        (scene, categories)
        for scene, categories in SCENE_CATEGORIES.items()
        if not args.domains or scene.split("/", 1)[0] in set(args.domains.split(","))
    ]
    if allowed_scenes is not None:
        scene_items = [
            (scene, categories)
            for scene, categories in scene_items
            if scene.split("/", 1)[1] in allowed_scenes or scene in allowed_scenes
        ]
    if args.max_scenes:
        scene_items = scene_items[: args.max_scenes]

    for scene_key, categories in scene_items:
        accepted_scene = 0
        for category in categories:
            if accepted >= args.target_new or accepted_scene >= args.per_scene:
                break
            try:
                members = _category_members(category, args.category_limit, args.sleep, args.timeout)
            except Exception as exc:
                rows.append({
                    "status": "search_error",
                    "reason": str(exc),
                    "scene": scene_key,
                    "category": category,
                })
                _write_manifest(rows, manifest)
                continue
            for member in members:
                if accepted >= args.target_new or accepted_scene >= args.per_scene:
                    break
                info = member["imageinfo"]
                image_url = info.get("thumburl") or info.get("url", "")
                source_url = info.get("descriptionurl", "")
                title = member["title"]
                row = {
                    "status": "rejected",
                    "reason": "",
                    "scene": scene_key,
                    "category": category,
                    "source_title": title,
                    "source_url": source_url,
                    "image_url": image_url,
                    "local_path": "",
                    "width": str(info.get("width", "")),
                    "height": str(info.get("height", "")),
                    "mime": str(info.get("mime", "")),
                }
                title_ok, title_reason = _title_ok(title)
                if not title_ok:
                    row["reason"] = title_reason
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                license_ok, license_text = _license_ok(info)
                row["license"] = license_text
                if not license_ok:
                    row["reason"] = "license_not_allowed"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                if not _mime_ok(info.get("mime", "")):
                    row["reason"] = "blocked_mime_type"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                if not _url_ok(source_url) or not _url_ok(image_url):
                    row["reason"] = "blocked_url"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                if int(info.get("width", 0)) < args.min_width or int(info.get("height", 0)) < args.min_height:
                    row["reason"] = "source_resolution_below_minimum"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
                if suffix not in IMAGE_SUFFIXES:
                    suffix = ".jpg"
                dst = _next_candidate_path(output_dir, scene_key, suffix)
                try:
                    _download(image_url, dst)
                    with Image.open(dst) as image:
                        image.verify()
                    metrics = _image_metrics(dst)
                    if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
                        dst.unlink(missing_ok=True)
                        row["reason"] = "downloaded_resolution_below_minimum"
                        rows.append(row)
                        _write_manifest(rows, manifest)
                        continue
                    ahash = _average_hash(dst)
                    if _near_duplicate(ahash, seen_hashes, args.duplicate_hamming_distance):
                        dst.unlink(missing_ok=True)
                        row["reason"] = "near_duplicate"
                        rows.append(row)
                        _write_manifest(rows, manifest)
                        continue
                except Exception as exc:
                    dst.unlink(missing_ok=True)
                    row["reason"] = f"download_error:{exc}"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                seen_hashes.append(ahash)
                accepted += 1
                accepted_scene += 1
                row.update({
                    "status": "accepted",
                    "reason": "accepted",
                    "local_path": dst.as_posix(),
                    "width": str(metrics["width"]),
                    "height": str(metrics["height"]),
                })
                rows.append(row)
                _write_manifest(rows, manifest)
                print(f"accepted\t{accepted}\t{scene_key}\t{dst.as_posix()}", flush=True)

    _write_manifest(rows, manifest)
    print(f"accepted_total={accepted}")
    print(manifest.as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="dataset/images_candidates/scene_expansion_commons_categories")
    parser.add_argument("--manifest", default="reports/scene_expansion_commons_categories.csv")
    parser.add_argument("--target-new", type=int, default=100)
    parser.add_argument("--per-scene", type=int, default=12)
    parser.add_argument("--category-limit", type=int, default=80)
    parser.add_argument("--min-width", type=int, default=900)
    parser.add_argument("--min-height", type=int, default=600)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--domains", default="")
    parser.add_argument("--candidate-roots", nargs="*", default=[])
    parser.add_argument("--scenes-file", default="")
    parser.add_argument("--max-scenes", type=int, default=0)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
