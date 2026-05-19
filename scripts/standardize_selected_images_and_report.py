#!/usr/bin/env python3
"""Standardize selected sample images and write a Feishu-ready scene report."""

from __future__ import annotations

import json
import re
import shutil
from collections import OrderedDict, defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
BLUEPRINT_PATH = ROOT / "dataset" / "annotations" / "SCENE_BLUEPRINT.md"
REPORT_PATH = ROOT / "reports" / "feishu_scene_reference_report.md"
MAPPING_PATH = ROOT / "reports" / "selected_image_standardization_map.csv"

DOMAIN_ZH = {
    "visual_security": "视觉安防与违规监控",
    "embodied_robotics": "具身智能与机器人操作",
    "heavy_load_construction": "建筑工程与重型载荷",
    "precision_defect_gen": "精密制造与缺陷生成",
    "extreme_emergency": "极端工况与应急响应",
}

TASK_ZH = {
    "industrial_logic_and_compliance": "工业逻辑与合规链",
    "rigid_body_kinematics_and_coupling": "刚体运动学与耦合",
    "topology_mutation_and_failure": "拓扑变形与局部失效",
    "fluid_dynamics_and_thermodynamics": "流体/热力学演化",
    "spatial_exploration_and_viewpoint": "空间探索与视角控制",
}

TITLE_ZH = {
    "vsec_unregistered_vehicle_intrusion": "未报备车辆闯入禁区",
    "vsec_missing_ppe_at_height": "高空作业未佩戴防护装备",
    "vsec_forklift_overspeed_pallet_shift": "叉车超速转弯导致托盘货物侧滑",
    "vsec_crane_unsafe_swing_near_people": "吊装载荷靠近人员造成危险摆动",
    "vsec_surveillance_blind_spot_sweep": "监控盲区扫视发现禁区闯入",
    "vsec_perimeter_fence_breach": "工业围栏局部破损入侵",
    "vsec_dangerous_goods_liquid_leak": "危险品装卸区液体泄漏扩散",
    "vsec_pedestrian_forklift_near_miss": "行人进入叉车通道触发避让",
    "vsec_smoke_alarm_evacuation": "工业烟雾报警与人员疏散",
    "vsec_guard_removed_conveyor": "输送机防护罩缺失暴露夹点",
    "erob_robot_arm_precision_grasp": "多轴机械臂高精度抓取",
    "erob_cobot_human_handover": "协作机器人与人员安全交接",
    "erob_tracked_robot_rubble": "履带机器人复杂地形越障",
    "erob_quadruped_stairs_rubble_fpv": "四足机器人楼梯/废墟第一视角通行",
    "erob_amr_warehouse_navigation": "仓储 AMR 避障导航",
    "erob_light_curtain_emergency_stop": "机器人工作站光幕触发急停",
    "erob_robot_tool_contact_force": "机器人末端工具接触力控制",
    "erob_multi_robot_coordination": "多机器人协同避让/交接",
    "erob_gripper_failure_recovery": "夹爪局部失效与恢复",
    "hload_dual_crawler_crane_lift": "双履带吊协同吊装",
    "hload_wire_rope_overload_snap": "钢丝绳过载局部断裂",
    "hload_mining_truck_muddy_slope": "矿用卡车泥泞坡道爬坡",
    "hload_gantry_wind_disturbance": "龙门/岸桥强风扰动",
    "hload_bridge_segment_alignment_drone": "桥梁节段无人机对位巡检",
    "hload_excavator_linkage_loading": "挖掘机液压连杆带载动作",
    "hload_ground_settlement_outrigger": "吊车支腿地基沉降",
    "hload_tunnel_pipe_burst_mud_surge": "隧道/基坑管道破裂泥水涌出",
    "hload_hoist_collision_near_structure": "吊物靠近结构物触发停机",
    "hload_formwork_collapse_local": "模板/支撑架局部失稳坍塌",
    "pdef_pcb_solder_bridge_short": "PCB 焊锡桥接短路生成",
    "pdef_engine_endoscope_crack": "发动机/管道内窥镜微裂纹巡检",
    "pdef_gear_tooth_missing_wear": "齿轮缺齿或严重磨损",
    "pdef_cnc_curved_surface_cutting": "五轴 CNC 曲面切削",
    "pdef_cutting_fluid_spray": "高速加工切削液喷溅",
    "pdef_weld_porosity_crack": "焊缝局部气孔或裂纹生成",
    "pdef_surface_scratch_inspection": "精密表面细微划痕生成",
    "pdef_tube_bundle_endoscopy": "换热管束内窥镜穿行",
    "pdef_connector_pin_bent": "密集连接器单针脚弯曲或桥接",
    "pdef_precision_assembly_misalignment": "精密装配微小错位",
    "emerg_flange_high_pressure_leak": "法兰高压泄漏喷射",
    "emerg_storage_tank_flash_fire": "储罐区局部闪燃蔓延",
    "emerg_transmission_tower_icing_collapse": "覆冰输电铁塔结构失效",
    "emerg_dust_explosion_confined_space": "受限空间粉尘爆炸触发链",
    "emerg_reactor_runaway_pressure_release": "反应釜超压泄放",
    "emerg_battery_thermal_runaway": "电池热失控与局部烟热扩散",
    "emerg_tunnel_fire_smoke_layering": "隧道火灾烟气分层扩散",
    "emerg_crane_load_drop_evacuation": "吊载坠落风险与疏散响应",
    "emerg_cooling_tower_plume_failure": "冷却塔羽流异常变化",
    "emerg_dam_or_retaining_wall_breach": "挡墙/尾矿坝局部溃口",
}


def _parse_blueprint() -> OrderedDict[str, dict]:
    rows: OrderedDict[str, dict] = OrderedDict()
    current_domain = ""
    heading_domain = {
        "Visual Security": "visual_security",
        "Embodied Robotics": "embodied_robotics",
        "Heavy Load Construction": "heavy_load_construction",
        "Precision Defect Generation": "precision_defect_gen",
        "Extreme Emergency": "extreme_emergency",
    }
    pattern = re.compile(
        r"^\| `(?P<scene>[^`]+)` \| `(?P<task>[^`]+)` \| (?P<samples>\d+) \| "
        r"(?P<requirement>.*?) \| (?P<example>.*?) \|$"
    )
    for line in BLUEPRINT_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_domain = heading_domain.get(line[3:].strip(), current_domain)
        match = pattern.match(line)
        if not match:
            continue
        scene_id = match.group("scene")
        rows[scene_id] = {
            "scene_id": scene_id,
            "domain": current_domain,
            "task_category": match.group("task"),
            "image_requirement": match.group("requirement"),
            "example_task": match.group("example"),
        }
    return rows


def _load_samples() -> list[dict]:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))["samples"]


def _write_samples(samples: list[dict]) -> None:
    SAMPLES_PATH.write_text(
        json.dumps({"samples": samples}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def _copy_as_jpg(source: Path, dest: Path) -> tuple[int, int]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == dest.resolve():
        return _image_size(dest)
    with Image.open(source) as image:
        image = image.convert("RGB")
        width, height = image.size
        image.save(dest, "JPEG", quality=92, optimize=True)
        return width, height


def _short_prompt(prompt: str) -> str:
    prompt = " ".join(prompt.split())
    if len(prompt) <= 260:
        return prompt
    return prompt[:257].rstrip() + "..."


def _scene_title_en(row: dict) -> str:
    text = row["example_task"].split(";")[0].strip().rstrip(".")
    return text


def main() -> None:
    blueprint = _parse_blueprint()
    samples = _load_samples()
    samples_by_scene: defaultdict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        samples_by_scene[sample["scene_id"]].append(sample)

    canonical_by_old: dict[str, str] = {}
    canonical_by_scene: dict[str, list[dict]] = {}
    mapping_rows = []

    for scene_id in blueprint:
        scene_samples = samples_by_scene.get(scene_id, [])
        if not scene_samples:
            continue
        unique_paths = []
        for sample in scene_samples:
            if sample["image_path"] not in unique_paths:
                unique_paths.append(sample["image_path"])
        domain = scene_samples[0]["domain"]
        scene_images = []
        for index, old_rel in enumerate(unique_paths, 1):
            source = ROOT / old_rel
            dest = ROOT / "dataset" / "images" / domain / f"{scene_id}__ref_{index:02d}.jpg"
            width, height = _copy_as_jpg(source, dest)
            new_rel = dest.relative_to(ROOT).as_posix()
            canonical_by_old[old_rel] = new_rel
            info = {
                "path": new_rel,
                "width": width,
                "height": height,
                "area": width * height,
                "source": old_rel,
            }
            scene_images.append(info)
            mapping_rows.append((scene_id, domain, old_rel, new_rel, width, height))
        canonical_by_scene[scene_id] = scene_images

    for sample in samples:
        sample["image_path"] = canonical_by_old.get(sample["image_path"], sample["image_path"])
        row = blueprint[sample["scene_id"]]
        sample["task_title"] = _scene_title_en(row)
        sample["task_title_zh"] = TITLE_ZH.get(sample["scene_id"], sample["scene_id"].replace("_", " "))
        sample["constraint_annotations"]["task_title"] = sample["task_title"]
        sample["constraint_annotations"]["task_title_zh"] = sample["task_title_zh"]

    _write_samples(samples)

    MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MAPPING_PATH.open("w", encoding="utf-8", newline="") as handle:
        handle.write("scene_id,domain,old_image_path,new_image_path,width,height\n")
        for row in mapping_rows:
            handle.write(",".join(str(item) for item in row) + "\n")

    lines = [
        "# FORGE-Bench 场景代表图与题目报告",
        "",
        "说明：每个场景选取当前入选图中分辨率最高的一张作为代表图；所有样本已同步引用规范命名图片。",
        "",
        "| 大类 | 小类 | 场景ID | 题目 | 图片名 | Prompt |",
        "|---|---|---|---|---|---|",
    ]
    for scene_id, row in blueprint.items():
        scene_samples = samples_by_scene.get(scene_id, [])
        if not scene_samples:
            continue
        images = canonical_by_scene[scene_id]
        best = sorted(images, key=lambda item: (-item["area"], item["path"]))[0]
        sample = scene_samples[0]
        title = TITLE_ZH.get(scene_id, _scene_title_en(row))
        prompt = _short_prompt(sample["video_generation_prompt"]).replace("|", "／")
        lines.append(
            "| {domain} | {task} | `{scene}` | {title} | `{image}` | {prompt} |".format(
                domain=f"{sample['domain']}（{DOMAIN_ZH[sample['domain']]}）",
                task=f"{sample['task_category']}（{TASK_ZH[sample['task_category']]}）",
                scene=scene_id,
                title=title,
                image=best["path"],
                prompt=prompt,
            )
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"standardized {len(mapping_rows)} selected images")
    print(f"updated {len(samples)} samples")
    print(f"wrote {REPORT_PATH.relative_to(ROOT).as_posix()}")
    print(f"wrote {MAPPING_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
