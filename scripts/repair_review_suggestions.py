#!/usr/bin/env python3
"""Repair review edits that were previously recorded without changing the real text."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "dataset/annotations/samples.json",
    ROOT / "dataset/annotations/video_generation_500_samples.json",
)
PACKAGE = ROOT / "reports/video_generation_500_package/prompts.jsonl"

CAMERA = {
    "static": "locked static camera",
    "orbit": "constant-radius 45 degree orbit around the subject",
    "dolly": "smooth dolly forward while keeping the subject framed",
    "pan": "smooth left-to-right inspection pan, not an orbit",
}

# These are deliberately image-specific.  None of these references depicts a
# confined space; only the first image clearly supports a dust-specific event.
EXPLOSIONS = {
    "emerg_032": ("industrial dust collector", "Industrial dust collector in an open factory", "A localized dust explosion occurs at the existing dust collector while the surrounding factory scene remains unchanged.", "Dust-collector explosion", "除尘器发生粉尘爆炸"),
    "emerg_036": ("outdoor storage silos", "Outdoor storage silos", "An explosion occurs at one of the existing storage silos while the surrounding scene remains unchanged.", "Storage-silo explosion", "储藏罐发生爆炸"),
    "emerg_149": ("outdoor storage tanks", "Outdoor storage tanks", "An explosion occurs at one of the existing storage tanks while the surrounding scene remains unchanged.", "Storage-tank explosion", "储藏罐发生爆炸"),
    "emerg_151": ("storage silos and plant structure", "Storage silos and visible plant structures", "An explosion occurs in the existing storage-silo area while the surrounding plant remains unchanged.", "Explosion in storage-silo area", "储藏罐区域发生爆炸"),
    "emerg_153": ("industrial equipment enclosure", "Industrial equipment enclosure", "An explosion occurs at the existing equipment enclosure while the surrounding factory scene remains unchanged.", "Equipment-enclosure explosion", "机箱发生爆炸"),
    "emerg_154": ("storage silos and conveyor structure", "Storage silos and visible conveyor structure", "An explosion occurs in the existing storage-silo area while the surrounding structures remain unchanged.", "Explosion in storage-silo area", "储藏罐区域发生爆炸"),
    "emerg_257": ("outdoor storage silos", "Outdoor storage silos", "An explosion occurs at one of the existing storage silos while the surrounding scene remains unchanged.", "Storage-silo explosion", "储藏罐发生爆炸"),
    "emerg_261": ("outdoor storage silo", "Outdoor storage silo and its existing support structure", "An explosion occurs at the existing storage silo while the surrounding scene remains unchanged.", "Storage-silo explosion", "储藏罐发生爆炸"),
}
EXPLOSION_SCENES = {
    "emerg_032": "emerg_dust_collector_explosion",
    "emerg_036": "emerg_storage_silo_explosion",
    "emerg_149": "emerg_storage_tank_explosion",
    "emerg_151": "emerg_storage_silo_area_explosion",
    "emerg_153": "emerg_equipment_enclosure_explosion",
    "emerg_154": "emerg_storage_silo_area_explosion",
    "emerg_257": "emerg_storage_silo_explosion",
    "emerg_261": "emerg_storage_silo_explosion",
}

# Actual phrases found in the current records (the old script tried variants
# that were not present).  Smaller replacements are intentional and traceable
# to the review notes.
GROUPS = [
    ("erob_001 erob_002", [("performs precision grasping", "performs controlled end-effector manipulation"), ("precision grasping", "controlled end-effector manipulation")]),
    ("erob_072 erob_073 erob_074 erob_075", [("Two robots coordinate", "Robots coordinate"), ("two mobile robots", "mobile robots"), ("Two mobile robots", "Mobile robots")]),
    ("erob_076 erob_077", [("multiple mobile robots", "two industrial robot arms"), ("Two robots coordinate", "Two robot arms coordinate")]),
    ("erob_170 erob_174", [("Robot applies", "The robot arm applies"), ("robot sanding", "robot-arm sanding")]),
    ("erob_190 erob_216", [("rubble", "uneven ground"), ("debris", "uneven ground")]),
    ("emerg_004", [("pipe flange valve", "storage tank"), ("valve connection", "storage tank")]),
    ("emerg_092 emerg_094 emerg_231 emerg_232 emerg_234 emerg_236", [("retaining wall or containment berm", "containment berm"), ("retaining wall or bund", "bund")]),
    ("emerg_093", [(" or containment berm", ""), (" or bund", "")]),
    ("emerg_158", [("central ", ""), (" connection", "")]),
    ("emerg_167", [("pipeline connection", "trailer"), ("along the adjacent pipeline", "")]),
    ("emerg_168 emerg_169", [("pipeline connection", "industrial equipment"), ("along the adjacent pipeline", "")]),
    ("emerg_170", [("pipeline connection", "industrial equipment")]),
    ("emerg_212", [("storage tank pipeline connection", "factory area")]),
    ("emerg_270", [("dust collection or process equipment", "industrial equipment")]),
    ("emerg_299 emerg_300 emerg_304 emerg_307 emerg_323", [("dust collection or process equipment", "industrial equipment"), (", triggering a clear shutdown response", "")]),
    ("emerg_302", [("Ice-loaded transmission tower", "Transmission tower"), ("ice-loaded transmission tower", "transmission tower"), ("ice-laden transmission tower", "transmission tower"), ("transmission tower yields", "Transmission tower yields"), ("ice loading", "loading"), ("transmission tower ice snow", "transmission tower"), ("ice/snow load context, or ", "")]),
    ("emerg_308", [("one battery module inside a battery energy storage container", "a storage tank"), ("battery module", "storage tank")]),
    ("emerg_327", [("at the far end of an enclosed passage", "in the factory area")]),
    ("emerg_328", [("at the far end", "")]),
    ("emerg_329", [("at the far end of an enclosed passage", "at a closed factory gate")]),
    ("hload_022 hload_239", [("climbs a muddy slope", "travels along a muddy road")]),
    ("hload_051", [("through hydraulic linkage", "")]),
    ("hload_071 hload_076 hload_219", [("underground pipe in a construction trench", "pipe"), ("construction trench", "work area")]),
    ("hload_077", [("underground pipe in a construction trench", "storage tank")]),
    ("hload_115", [("suspended precast bridge segment", "building under construction")]),
    ("hload_228 hload_230 hload_233", [("unequal-angle ", "")]),
    ("hload_284", [("existing wire rope under overload", "wire rope")]),
    ("pdef_011 pdef_012 pdef_015 pdef_018", [("The borescope approaches an existing internal ", "The camera approaches a "), ("borescope", "camera")]),
    ("pdef_031", [(", with the spindle, tool, and workpiece fixture maintaining a credible relationship", "")]),
    ("pdef_071 pdef_072", [("borescope", "camera")]),
    ("pdef_074", [("The borescope moves through a heat-exchanger tube bundle", "The camera moves forward"), ("borescope", "camera")]),
    ("pdef_156 pdef_157 pdef_211", [("During precision assembly, ", ""), ("during precision assembly", "")]),
    ("pdef_165 pdef_166", [("sprays toward the high-speed cutting tool", "sprays outward")]),
    ("pdef_175 pdef_176", [("borescope and internal ", "camera and "), ("borescope", "camera")]),
    ("pdef_216 pdef_217", [("borescope moves through a heat-exchanger tube bundle", "camera moves forward"), ("internal ", ""), ("borescope", "camera")]),
    ("pdef_226", [("existing pipe weld seam", "gear"), ("pipe weld seam", "gear")]),
    ("pdef_130", [("five axis ", ""), ("five-axis ", ""), ("5-axis ", "")]),
    ("vsec_011 vsec_012 vsec_014 vsec_151 vsec_152", [(" or safety harness", "")]),
    ("vsec_031 vsec_032 vsec_141", [("existing ", "")]),
    ("vsec_061 vsec_069 vsec_115 vsec_159", [("hazardous-goods loading area ", ""), ("hazardous-goods loading area", "industrial area")]),
    ("vsec_173 vsec_175 vsec_176 vsec_187", [(" or vehicle", "")]),
    ("vsec_178", [("personnel or ", "")]),
]

CUSTOM_SCENARIOS = {
    "pdef_130": "The CNC machine cuts a curved surface while the tool and workpiece remain stable.",
    "hload_203": "The visible machine performs one small, mechanically plausible movement while all surrounding structures remain unchanged.",
    "hload_220": "The camera inspects the visible machine as one existing component moves slightly; no specific unseen load or mechanism is introduced.",
    "hload_221": "The camera moves slowly to inspect the visible structure; the structure itself remains fixed and no new action is introduced.",
    "hload_244": "The camera moves slowly to inspect the visible structure; all existing parts remain fixed and unchanged.",
    "hload_245": "The camera moves slowly to inspect the visible equipment; no specific mechanical action is imposed.",
    "hload_250": "The camera moves slowly to inspect the visible structure; no unseen load, tool, or operation is introduced.",
    "hload_267": "The camera moves slowly to inspect the visible equipment while every existing component remains unchanged.",
    "hload_277": "The camera inspects the visible structure without introducing a specific load movement or unseen operation.",
}

CHINESE_TITLES = {
    "emerg_302": "输电塔局部变形并倒塌",
    "erob_156": "AMR接近可见障碍物时减速",
    "erob_230": "AGV在关闭的门前等待",
    "hload_203": "机械设备发生小幅运动",
    "hload_220": "镜头检查机械设备的轻微运动",
    "hload_221": "镜头缓慢检查可见结构",
    "hload_228": "吊装载荷因吊索角度不同而倾斜",
    "hload_230": "吊装载荷因吊索角度不同而倾斜",
    "hload_233": "吊装载荷因吊索角度不同而倾斜",
    "hload_244": "镜头缓慢检查可见结构",
    "hload_245": "镜头缓慢检查可见设备",
    "hload_250": "镜头缓慢检查可见结构",
    "hload_267": "镜头缓慢检查可见设备",
    "pdef_137": "镜头检查设备并发现轻微位置偏差",
    "pdef_144": "镜头检查仪器并发现轻微位置偏差",
    "pdef_145": "镜头检查仪器并发现轻微位置偏差",
    "pdef_150": "镜头检查设备并发现轻微位置偏差",
    "pdef_151": "镜头检查设备并发现轻微位置偏差",
    "pdef_191": "镜头检查管道并发现轻微位置偏差",
    "vsec_173": "人员或推车接近未隔离区域",
    "vsec_175": "人员或推车接近未隔离区域",
    "vsec_176": "人员或推车接近未隔离区域",
    "vsec_178": "推车接近未隔离区域",
    "vsec_187": "人员或推车接近未隔离区域",
}

def zh(ids: str, text: str) -> None:
    for task_id in ids.split():
        CHINESE_TITLES[task_id] = text

# Chinese summaries of the *revised* scenarios, not the historical titles.
zh("erob_001 erob_002", "机械臂在工件附近进行受控的末端操作")
zh("erob_072 erob_073 erob_074 erob_075", "移动机器人协同避让或交接")
zh("erob_076 erob_077", "两台机械臂协同避让或交接")
zh("erob_170 erob_174", "机械臂保持工具与工件接触")
zh("erob_190 erob_216", "机器人通过不平整地面")
zh("emerg_004", "储藏罐发生高压泄漏")
zh("emerg_092 emerg_094 emerg_231 emerg_232 emerg_234 emerg_236", "围堰区域内的液体扩散")
zh("emerg_093", "危险液体在装卸区域扩散")
zh("emerg_158", "阀门处发生局部泄漏")
zh("emerg_167", "拖车附近发生泄漏")
zh("emerg_168 emerg_169 emerg_170", "工业设备附近发生泄漏")
zh("emerg_212", "工厂区域发生泄漏")
zh("emerg_270", "工业设备发生异常")
zh("emerg_299 emerg_300 emerg_304 emerg_307 emerg_323", "工业设备附近出现烟尘或异常")
zh("emerg_308", "储藏罐发生异常")
zh("emerg_327", "厂区出现烟雾并影响视线")
zh("emerg_328", "烟雾影响通道视线")
zh("emerg_329", "关闭的大门附近出现烟雾")
zh("hload_022 hload_239", "车辆沿泥泞道路行驶")
zh("hload_051", "挖掘机铲斗进行受控运动")
zh("hload_071 hload_076 hload_219", "管道破裂并流出泥水")
zh("hload_077", "储藏罐发生局部异常")
zh("hload_115", "镜头检查在建建筑")
zh("hload_228 hload_230 hload_233", "吊索角度不同导致载荷倾斜")
zh("hload_284", "钢丝绳发生局部变形并断裂")
zh("pdef_011 pdef_012 pdef_015 pdef_018", "镜头接近表面的细小裂纹")
zh("pdef_031", "机床加工过程中出现局部缺陷")
zh("pdef_071 pdef_072", "镜头接近可见的细小裂纹")
zh("pdef_074", "镜头向前检查换热器管束")
zh("pdef_156 pdef_157 pdef_211", "零件出现轻微装配偏差")
zh("pdef_165 pdef_166", "切削液向外喷出")
zh("pdef_175 pdef_176", "镜头检查表面细小缺陷")
zh("pdef_216 pdef_217", "镜头向前检查换热器管束")
zh("pdef_226", "齿轮出现细小缺陷")
zh("pdef_130", "数控机床加工曲面")
zh("vsec_011 vsec_012 vsec_014 vsec_151 vsec_152", "未戴安全帽的人员进行高处作业")
zh("vsec_031 vsec_032 vsec_141", "起重机吊载接近人员并触发停止")
zh("vsec_061 vsec_069 vsec_115 vsec_159", "化学液体泄漏并沿地面扩散")
zh("vsec_173 vsec_175 vsec_176 vsec_187", "人员或推车接近未隔离区域")
zh("vsec_178", "推车接近未隔离区域")

def walk(value, pairs):
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
        return " ".join(value.split())
    if isinstance(value, list):
        return [walk(x, pairs) for x in value]
    if isinstance(value, dict):
        structural = {"task_id", "scene_id", "image_path", "source_image_path", "id"}
        return {k: (v if k in structural else walk(v, pairs)) for k, v in value.items()}
    return value

def prompt(sample):
    scenario = sample["constraint_annotations"]["domain_scenario"].rstrip(".") + "."
    return ("Use the reference image as the exact first frame. Create a 5-second photorealistic industrial video. "
            + scenario + " Camera: " + CAMERA[sample["motion_type"]] + ". "
            "Preserve every visible subject's identity, count, geometry, material, lighting, background, and all non-event regions. "
            "Do not add people, vehicles, tools, loads, text, logos, or other objects not already visible; avoid cuts, global regeneration, flicker, warping, disappearance, penetration, floating motion, and identity swaps.")

def main():
    rules = {}
    for ids, pairs in GROUPS:
        for task_id in ids.split():
            rules[task_id] = pairs
    touched = set()
    for path in TARGETS:
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, sample in enumerate(data["samples"]):
            task_id = sample["task_id"]
            # Repair identifiers damaged by the first revision of this script.
            sample["scene_id"] = sample["scene_id"].replace("uneven ground", "uneven_ground")
            if task_id in rules:
                sample = walk(sample, rules[task_id])
                touched.add(task_id)
            if task_id in CUSTOM_SCENARIOS:
                old = sample["constraint_annotations"]["domain_scenario"]
                sample = walk(sample, [(old, CUSTOM_SCENARIOS[task_id])])
                sample["constraint_annotations"]["domain_scenario"] = CUSTOM_SCENARIOS[task_id]
                touched.add(task_id)
            if task_id in EXPLOSIONS:
                subject, requirement, scenario, title, title_zh = EXPLOSIONS[task_id]
                old = sample["constraint_annotations"]["domain_scenario"]
                sample = walk(sample, [(old, scenario), (sample.get("reference_subject", ""), subject), (sample.get("image_requirement", ""), requirement)])
                sample["reference_subject"] = subject
                sample["image_requirement"] = requirement
                sample["constraint_annotations"].update(domain_scenario=scenario, image_requirement=requirement, task_title=title, task_title_zh=title_zh)
                sample["task_title"] = title
                sample["task_title_zh"] = title_zh
                sample["scene_id"] = EXPLOSION_SCENES[task_id]
                touched.add(task_id)
            if task_id in CHINESE_TITLES:
                sample["task_title_zh"] = CHINESE_TITLES[task_id]
                sample.setdefault("constraint_annotations", {})["task_title_zh"] = CHINESE_TITLES[task_id]
                touched.add(task_id)
            if task_id in touched:
                sample["video_generation_prompt"] = prompt(sample)
                data["samples"][i] = sample
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    canonical = {x["task_id"]: x for x in json.loads(TARGETS[1].read_text(encoding="utf-8"))["samples"]}
    rows = [json.loads(x) for x in PACKAGE.read_text(encoding="utf-8").splitlines() if x.strip()]
    for row in rows:
        if row["task_id"] in canonical:
            row["video_generation_prompt"] = canonical[row["task_id"]]["video_generation_prompt"]
    PACKAGE.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    resolution_path = ROOT / "reports/prompt_review_460_resolution.json"
    resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
    resolution["changed_prompt_tasks"] = sorted(set(resolution.get("changed_prompt_tasks", [])) | touched)
    regeneration_ids = {row["task_id"] for row in resolution.get("regeneration", [])}
    for task_id, requirement in {
        "erob_156": "Autonomous mobile robot positioned beneath an existing metal rack in a factory",
        "erob_193": "Industrial robot gripper visibly holding an existing metal gear",
        "erob_259": "Tracked inspection robot on a clear paved industrial lane",
    }.items():
        if task_id not in regeneration_ids:
            sample = canonical[task_id]
            resolution.setdefault("regeneration", []).append({
                "task_id": task_id,
                "action": "replacement_selected_pending_apply",
                "note": "User requested replacement and video regeneration",
                "current_image_path": sample["image_path"],
                "required_replacement_image": requirement,
                "scene_id": sample["scene_id"],
            })
    resolution["regeneration"] = sorted(resolution["regeneration"], key=lambda row: row["task_id"])
    resolution_path.write_text(json.dumps(resolution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = json.loads((ROOT / "reports/prompt_review_460.json").read_text(encoding="utf-8"))
    baseline = {x["task_id"]: x for x in json.loads((ROOT / "reports/prompt_alignment_review_460/manifest.json").read_text(encoding="utf-8"))}
    noted = [x["task_id"] for x in review if x.get("note", "").strip()]
    unchanged = [task_id for task_id in noted if baseline.get(task_id, {}).get("prompt_en") == canonical[task_id]["video_generation_prompt"]]
    print(json.dumps({"repaired_tasks": len(touched), "explosion_tasks": len(EXPLOSIONS), "noted_tasks": len(noted), "changed_vs_baseline": len(noted) - len(unchanged), "still_unchanged": unchanged}, ensure_ascii=False))

if __name__ == "__main__":
    main()
