#!/usr/bin/env python3
"""Import user-supplied loss-gap images into dataset/images.

The source directory keeps the original files. Imported copies are converted to
JPEG and named by scene family so samples can reference stable, readable paths.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "dataset" / "imagesforloss"
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
REPORT_PATH = ROOT / "reports" / "imagesforloss_import.csv"

REMOVED_SCENE_ID = "erob_pipe_crawler_inspection"

SCENE_TITLES = {
    "vsec_surveillance_blind_spot_sweep": "CCTV blind-spot sweep reveals restricted-area entry",
    "vsec_perimeter_fence_breach": "Localized breach in an industrial perimeter barrier",
    "vsec_smoke_alarm_evacuation": "Industrial smoke alarm and evacuation response",
    "erob_tracked_robot_rubble": "Tracked robot traversal over rubble and uneven ground",
    "erob_quadruped_stairs_rubble_fpv": "Quadruped robot viewpoint over stairs or debris",
    "erob_light_curtain_emergency_stop": "Robot-cell light curtain triggers emergency stop",
    "hload_mining_truck_muddy_slope": "Mining truck climbs a muddy haul-road slope",
    "hload_formwork_collapse_local": "Localized formwork or shoring support failure",
    "pdef_weld_porosity_crack": "Localized porosity or crack generation on a weld seam",
    "pdef_surface_scratch_inspection": "Fine scratch generation on a precision surface",
    "pdef_connector_pin_bent": "Single bent or bridged pin in a dense connector",
    "pdef_precision_assembly_misalignment": "Small pose misalignment during precision assembly",
    "emerg_transmission_tower_icing_collapse": "Ice-loaded transmission tower structural failure",
    "emerg_dust_explosion_confined_space": "Dust explosion trigger in a confined industrial area",
    "emerg_battery_thermal_runaway": "Battery thermal runaway and local smoke spread",
    "emerg_tunnel_fire_smoke_layering": "Tunnel fire with stratified smoke movement",
    "emerg_cooling_tower_plume_failure": "Cooling tower plume anomaly under flow or fan failure",
}

SCENE_TITLES_ZH = {
    "vsec_surveillance_blind_spot_sweep": "监控盲区扫视发现禁区闯入",
    "vsec_perimeter_fence_breach": "工业围栏局部破损入侵",
    "vsec_smoke_alarm_evacuation": "工业烟雾报警与人员疏散",
    "erob_tracked_robot_rubble": "履带机器人复杂地形越障",
    "erob_quadruped_stairs_rubble_fpv": "四足机器人楼梯/废墟第一视角通行",
    "erob_light_curtain_emergency_stop": "机器人工作站光幕触发急停",
    "hload_mining_truck_muddy_slope": "矿用卡车泥泞坡道爬坡",
    "hload_formwork_collapse_local": "模板/支撑架局部失稳坍塌",
    "pdef_weld_porosity_crack": "焊缝局部气孔或裂纹生成",
    "pdef_surface_scratch_inspection": "精密表面细微划痕生成",
    "pdef_connector_pin_bent": "密集连接器单针脚弯曲或桥接",
    "pdef_precision_assembly_misalignment": "精密装配微小错位",
    "emerg_transmission_tower_icing_collapse": "覆冰输电铁塔结构失效",
    "emerg_dust_explosion_confined_space": "受限空间粉尘爆炸触发链",
    "emerg_battery_thermal_runaway": "电池热失控与局部烟热扩散",
    "emerg_tunnel_fire_smoke_layering": "隧道火灾烟气分层扩散",
    "emerg_cooling_tower_plume_failure": "冷却塔羽流异常变化",
}

ASSIGNMENTS = {
    "vsec_surveillance_blind_spot_sweep": [
        "4-230110102159120.jpeg",
        "OIP-C (4).webp",
        "OIP-C (5).webp",
        "屏幕截图 2026-05-17 193202.png",
    ],
    "vsec_perimeter_fence_breach": ["OIP-C (2).webp"],
    "vsec_smoke_alarm_evacuation": ["OIP-C (49).webp"],
    "erob_tracked_robot_rubble": ["OIP-C (6).webp"],
    "erob_quadruped_stairs_rubble_fpv": [
        "OIP-C (10).webp",
        "OIP-C (7).webp",
        "OIP-C (8).webp",
        "OIP-C (9).webp",
        "下载 (1).webp",
    ],
    "erob_light_curtain_emergency_stop": [
        "OIP-C (1).webp",
        "OIP-C (11).webp",
        "OIP-C (12).webp",
        "OIP-C (13).webp",
        "OIP-C (14).webp",
        "OIP-C.webp",
    ],
    "hload_mining_truck_muddy_slope": [
        "OIP-C (15).webp",
        "OIP-C (16).webp",
        "OIP-C (17).webp",
        "image017-已增强-SR.jpg",
        "下载 (2).webp",
    ],
    "hload_formwork_collapse_local": [
        "OIP-C (18).webp",
        "OIP-C (19).webp",
        "OIP-C (20).webp",
        "OIP-C (21).webp",
        "下载 (3).webp",
    ],
    "pdef_weld_porosity_crack": [
        "OIP-C (22).webp",
        "OIP-C (23).webp",
        "OIP-C (24).webp",
        "下载 (4).webp",
    ],
    "pdef_surface_scratch_inspection": [
        "OIP-C (25).webp",
        "OIP-C (26).webp",
        "OIP-C (27).webp",
        "OIP-C (28).webp",
        "OIP-C (29).webp",
        "OIP-C (30).webp",
        "OIP-C (35).webp",
        "下载 (5).webp",
        "下载.webp",
    ],
    "pdef_connector_pin_bent": [
        "O1CN01Fgsqek1XTEvKK2gMe_!!2213325452924-0-cib.jpg",
        "OIP-C (31).webp",
        "OIP-C (32).webp",
    ],
    "pdef_precision_assembly_misalignment": [
        "OIP-C (3).webp",
        "OIP-C (33).webp",
        "OIP-C (34).webp",
        "OIP-C (36).webp",
        "OIP-C (37).webp",
        "OIP-C (38).webp",
    ],
    "emerg_transmission_tower_icing_collapse": [
        "OIP-C (39).webp",
        "OIP-C (40).webp",
        "OIP-C (41).webp",
        "OIP-C (42).webp",
        "OIP-C (43).webp",
    ],
    "emerg_dust_explosion_confined_space": [
        "OIP-C (44).webp",
        "OIP-C (45).webp",
        "OIP-C (46).webp",
    ],
    "emerg_battery_thermal_runaway": [
        "OIP-C (47).webp",
        "OIP-C (48).webp",
        "OIP-C (50).webp",
        "OIP-C (51).webp",
        "OIP-C (52).webp",
        "OIP-C (53).webp",
        "OIP-C (54).webp",
        "下载 (6).webp",
    ],
    "emerg_tunnel_fire_smoke_layering": [
        "OIP-C (55).webp",
        "OIP-C (56).webp",
        "OIP-C (57).webp",
        "OIP-C (58).webp",
        "下载 (7).webp",
    ],
    "emerg_cooling_tower_plume_failure": [
        "OIP-C (59).webp",
        "OIP-C (60).webp",
        "OIP-C (61).webp",
        "OIP-C (62).webp",
        "OIP-C (63).webp",
        "OIP-C (64).webp",
    ],
}


def _domain_from_scene(scene_id: str) -> str:
    if scene_id.startswith("vsec_"):
        return "visual_security"
    if scene_id.startswith("erob_"):
        return "embodied_robotics"
    if scene_id.startswith("hload_"):
        return "heavy_load_construction"
    if scene_id.startswith("pdef_"):
        return "precision_defect_gen"
    if scene_id.startswith("emerg_"):
        return "extreme_emergency"
    raise ValueError(f"unknown scene prefix: {scene_id}")


def _convert_to_jpg(source: Path, dest: Path) -> tuple[int, int]:
    with Image.open(source) as image:
        image = image.convert("RGB")
        width, height = image.size
        dest.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest, "JPEG", quality=92, optimize=True)
        return width, height


def _load_samples() -> list[dict]:
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    return data["samples"]


def _write_samples(samples: list[dict]) -> None:
    SAMPLES_PATH.write_text(
        json.dumps({"samples": samples}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _renumber(samples: list[dict]) -> None:
    counters: defaultdict[str, int] = defaultdict(int)
    prefixes = {
        "visual_security": "vsec",
        "embodied_robotics": "erob",
        "heavy_load_construction": "hload",
        "precision_defect_gen": "pdef",
        "extreme_emergency": "emerg",
    }
    for sample in samples:
        domain = sample["domain"]
        counters[domain] += 1
        old_task_id = sample["task_id"]
        new_task_id = f"{prefixes[domain]}_{counters[domain]:03d}"
        sample["task_id"] = new_task_id
        for variant in sample.get("sensitivity_variants", []):
            variant["id"] = re.sub(r"^[a-z]+_[0-9]{3}", new_task_id, variant["id"])
        for question in sample.get("industrial_logic_questions", []):
            question["text"] = question["text"].replace(old_task_id, new_task_id)


def main() -> None:
    samples = _load_samples()
    samples = [s for s in samples if s.get("scene_id") != REMOVED_SCENE_ID]

    imported_by_scene: dict[str, list[str]] = {}
    rows = []
    for scene_id, filenames in ASSIGNMENTS.items():
        domain = _domain_from_scene(scene_id)
        scene_paths = []
        for index, filename in enumerate(filenames, 1):
            source = SOURCE_DIR / filename
            if not source.exists():
                raise FileNotFoundError(source)
            dest = ROOT / "dataset" / "images" / domain / f"{scene_id}__loss_{index:02d}.jpg"
            width, height = _convert_to_jpg(source, dest)
            rel = dest.relative_to(ROOT).as_posix()
            scene_paths.append(rel)
            rows.append({
                "scene_id": scene_id,
                "domain": domain,
                "source_filename": filename,
                "image_path": rel,
                "source_width": width,
                "source_height": height,
                "task_title": SCENE_TITLES[scene_id],
                "task_title_zh": SCENE_TITLES_ZH[scene_id],
            })
        imported_by_scene[scene_id] = scene_paths

    for sample in samples:
        scene_id = sample.get("scene_id")
        scene_paths = imported_by_scene.get(scene_id)
        if not scene_paths:
            continue
        variant = int(sample["task_id"].split("_")[-1])
        sample["image_path"] = scene_paths[(variant - 1) % len(scene_paths)]
        sample["task_title"] = SCENE_TITLES[scene_id]
        sample["task_title_zh"] = SCENE_TITLES_ZH[scene_id]
        sample["constraint_annotations"]["task_title"] = SCENE_TITLES[scene_id]
        sample["constraint_annotations"]["task_title_zh"] = SCENE_TITLES_ZH[scene_id]

    _renumber(samples)
    _write_samples(samples)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"imported {len(rows)} images into dataset/images")
    print(f"removed scene: {REMOVED_SCENE_ID}")
    print(f"wrote {len(samples)} samples")
    print(f"wrote {REPORT_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
