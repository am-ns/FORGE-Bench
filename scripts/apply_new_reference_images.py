#!/usr/bin/env python3
"""Apply the user-supplied replacement references and build a final audit page."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "reports" / "new pic"
OUT = ROOT / "reports" / "modified_tasks_final_review"
TARGETS = (
    ROOT / "dataset" / "annotations" / "samples.json",
    ROOT / "dataset" / "annotations" / "video_generation_500_samples.json",
)
PACKAGE = ROOT / "reports" / "video_generation_500_package"
RESOLUTION = ROOT / "reports" / "prompt_review_460_resolution.json"
OLD_REVIEW = ROOT / "reports" / "prompt_alignment_review_460" / "manifest.json"

# task_id: (new-pic filename, precise visible subject, image requirement,
# image-grounded event, short title, Chinese title)
R = {
    "erob_156": ("0f93d3e08b1a44c5babcbf2ecb7b24e9.webp", "AMR carrying a metal rack", "Autonomous mobile robot positioned beneath an existing metal rack in a factory", "The AMR moves a short distance forward with the existing rack while its wheels maintain stable contact with the factory floor.", "AMR moves with an existing rack", "AMR承载现有金属架移动"),
    "erob_193": ("微信图片_20260908140102_342_8.jpg", "robot gripper holding a gear", "Industrial robot gripper visibly holding an existing metal gear", "The existing gear shifts slightly within the gripper, then the gripper stops while continuing to hold it.", "Gear shifts slightly in robot gripper", "齿轮在夹爪中轻微滑移"),
    "erob_259": ("微信图片_20260908140103_343_8.jpg", "tracked inspection robot in an industrial yard", "Tracked inspection robot on a clear paved industrial lane", "The tracked inspection robot moves a short distance along the existing paved lane while both tracks maintain stable ground contact.", "Tracked robot moves along factory lane", "履带巡检机器人沿厂区道路移动"),
    "erob_015": ("e823b1667c1a50ac3e92f5d2b2f76991.jpg", "cobot handing a cardboard box to a worker", "Collaborative robot and worker at a handover table with a visible cardboard box", "The cobot slowly extends the cardboard box toward the nearby worker and stops before contact; the worker and box remain stable.", "Cobot presents a box for handover", "协作机器人递送纸箱"),
    "erob_027": ("d689ddbba6577911aab2eca6c4be89cf.jpg", "tracked inspection vehicle on uneven dirt", "Tracked inspection vehicle on an open uneven dirt surface", "The tracked inspection vehicle advances a short distance over the uneven dirt; both tracks maintain continuous ground contact.", "Tracked vehicle crosses uneven dirt", "履带巡检车通过不平地面"),
    "erob_028": ("9f6ffed2e07f5ceb50da3d840546591d.jpg", "red tracked rescue robot on rough ground", "Tracked rescue robot on rough outdoor ground", "The red tracked robot climbs the small existing rough patch while its tracks conform to the ground without changing the chassis geometry.", "Tracked rescue robot climbs rough ground", "履带救援机器人越过粗糙地面"),
    "erob_032": ("ec3f71bb62801f2b3892eceacff36b67.jpg", "quadruped robot on an outdoor staircase", "Quadruped robot positioned on concrete stairs", "The quadruped robot climbs two visible stair steps with alternating foot contacts and a stable body.", "Quadruped climbs outdoor stairs", "四足机器人攀爬室外楼梯"),
    "erob_033": ("29950edc8437484cb05741a204a5a390.webp", "quadruped robot on an indoor staircase", "Quadruped robot positioned on indoor stairs", "The quadruped robot descends two visible stair steps slowly; every foot lands on a tread without crossing the railing.", "Quadruped descends indoor stairs", "四足机器人下楼梯"),
    "erob_034": ("3801213fb80e7bec54e777d80a7bae389b504fc23df7.png", "quadruped robot standing on loose bricks", "Quadruped robot on a localized pile of loose bricks", "The quadruped robot takes two careful steps across the existing brick pile while its body and leg count remain unchanged.", "Quadruped crosses a brick pile", "四足机器人穿过砖块堆"),
    "erob_035": ("import_1776996178614820250011.jpg", "quadruped robot in a marked factory aisle", "Quadruped robot in a clear marked industrial aisle", "The quadruped robot walks straight forward a short distance along the existing yellow aisle line with stable foot contact.", "Quadruped follows a factory aisle", "四足机器人沿车间通道行走"),
    "erob_037": ("682fcb40a31020535fc9c00d.jpg", "quadruped robot beside railway ballast", "Quadruped inspection robot beside a rail wagon on ballast", "The quadruped robot steps from the curb onto the existing ballast and stabilizes beside the rail wagon.", "Quadruped steps onto rail ballast", "四足机器人踏上铁路道砟"),
    "erob_052": ("256e100cd5dd475abd15b959328c2177.jpg", "worker beside a fenced robotic cell", "Worker and industrial robot separated by a visible safety fence", "As the worker approaches the visible fenced robot cell, the robot stops its tool motion and remains stopped.", "Robot stops as worker approaches fence", "人员靠近围栏时机器人停机"),
    "erob_082": ("364692_6faf6f1d-62f2-4122-a5fa-c43351d8a1cc.jpg", "industrial robot end effector engaged with a long fixture", "Industrial robot end effector visibly coupled to an existing long fixture", "The foreground robot end effector develops a small local slip at its existing fixture contact, then pauses without detaching.", "End effector slips at fixture contact", "末端执行器在夹具接触处轻微滑移"),
    "erob_083": ("355d799dcbcb42f6b79c3418f95e009a.webp", "empty industrial robot gripper", "Industrial robot gripper with no object held between its jaws", "The empty robot gripper makes one small controlled jaw movement, then stops; no workpiece or other object appears between the jaws.", "Empty gripper makes a small movement", "空夹爪进行小幅运动"),
    "erob_084": ("u=1570987389,3778561720&fm=253&fmt=auto&app=138&f=JPEG.webp", "two-finger robot gripper above a machined part", "Two-finger robot gripper aligned above an existing machined part", "One existing gripper jaw closes slightly out of alignment, the approach pauses, and the machined part remains fixed on the table.", "Gripper jaw misaligns during approach", "夹爪接近时轻微错位"),
    "erob_146": ("bc588bbf5dcb8068acee220bcec7d3a0.jpg", "warehouse AMR beside its charging unit", "Warehouse AMR and a visible charging unit in an open paved area", "The AMR begins moving away from the visible charging unit, detects the unit still within its clearance zone, and stops after a short distance.", "AMR stops while leaving charger", "AMR离开充电设备时停车"),
    "erob_147": ("c30146448a402bd1337decaeb1899873.jpg", "pallet-carrying AMR in a marked factory lane", "Pallet-carrying AMR in a marked industrial lane", "The loaded AMR advances slowly along the green lane and stops before crossing the yellow boundary line.", "Loaded AMR stops at lane boundary", "载货AMR在通道边界前停车"),
    "erob_222": ("d34b26d961bf463fb9d25288be9cb0fe.webp", "quadruped robot on a muddy riverbank", "Quadruped robot at the edge of wet muddy ground", "The quadruped robot takes two slow steps across the wet muddy patch; each foot presses locally into the soft surface without sliding.", "Quadruped crosses muddy ground", "四足机器人通过泥泞地面"),
    "erob_245": ("u=212178608,2164623156&fm=193.jpg", "worker operating beside a collaborative robot", "Worker and collaborative robot sharing a workstation", "The robot arm slows its existing movement as the nearby worker reaches toward the workstation, maintaining a visible clearance.", "Cobot slows near worker", "协作机器人在人员附近减速"),
    "erob_260": ("d659060bbdf14a7cbeafab91f106f6c5.jpg", "wheeled inspection robot on rocky mountain ground", "Wheeled inspection robot on an uneven rocky trail", "The wheeled inspection robot advances a short distance over the existing rocky trail; all four wheels maintain plausible contact and the chassis stays rigid.", "Wheeled robot crosses rocky ground", "轮式巡检机器人通过岩石地面"),
    "emerg_221": ("b999a9014c086e0628d47f075f3c63e40bd1cbc6.webp", "mobile crane rigged to a wrapped machine load", "Mobile crane, spreader beam, four slings, and wrapped machine load in a clear yard", "The existing wrapped load is lifted a short distance from the ground, then begins a dangerous controlled downward drop while every sling remains attached.", "Lifted machine begins dangerous descent", "吊装设备离地后开始危险下落"),
    "emerg_294": ("20210204104834689.jpg", "enclosed pedestrian transport tunnel", "Long enclosed passage with clear side panels, centerline, and distant exit", "A thin smoke layer develops at the far end of the enclosed tunnel while the camera pans right, keeping the centerline and exit direction visible.", "Smoke reduces tunnel-route visibility", "烟雾降低通道路线可见度"),
    "emerg_305": ("u=607324123,1305968986&fm=253&fmt=auto&app=138&f=JPEG.webp", "outdoor industrial dust collector with connected ducts", "Industrial dust collector, cyclone, fan, and connected ducts", "A small localized dust plume emerges from the lower seam of the existing dust collector and the nearby fan visibly stops; all ducts remain fixed.", "Dust collector seam releases dust", "除尘器接缝局部扬尘"),
    "emerg_306": ("u=2923521955,4152313524&fm=253&fmt=auto&app=120&f=JPEG.webp", "open industrial electrical control cabinet", "Open industrial control cabinet with visible drives, breakers, terminals, and wiring", "A small wisp of smoke appears at one existing terminal inside the open control cabinet and the adjacent drive indicators turn off; cabinet geometry remains unchanged.", "Control-cabinet terminal emits smoke", "控制柜端子局部冒烟"),
    "emerg_314": ("cde11d0424bf4e9b9b1898217ece4fc8.webp", "three large bolted pipe elbows", "Large industrial pipes with clearly visible bolted flange joints", "A narrow high-pressure water spray starts at one visible flange seam on the center pipe and remains localized to that joint.", "Flange seam develops a pressure leak", "法兰接缝发生高压泄漏"),
    "hload_023": ("562c11dfa9ec8a1347d6302b9c22d89fa2ecc0da.webp", "large mining haul truck on a quarry haul road", "Large mining haul truck with all tires visible on an uneven quarry road", "The mining haul truck rolls slowly forward along the existing uneven haul road; all tires rotate with stable ground contact and the rigid body does not slide.", "Mining truck rolls on quarry road", "矿用重卡沿矿区道路行驶"),
    "hload_058": ("a6c55a8f3360155cf291a429567ab8c5a42eb280.jpg", "excavator loading a dump truck", "Tracked excavator with loaded bucket, visible boom linkage, and dump truck", "The excavator lowers its existing loaded bucket slightly into the dump body; the boom, stick, and bucket remain rigidly coupled and no new material appears.", "Excavator lowers loaded bucket", "挖掘机下放已装载铲斗"),
    "hload_069": ("n_v3a4cc966136d84221b0e92471ab042bb8.webp", "mobile crane with outriggers on rough ground", "Mobile crane with visible extended outrigger and support foot on rough ground", "The visible outrigger foot settles a few centimeters into the soft patch beneath it while the crane chassis and boom remain rigid.", "Crane outrigger settles locally", "起重机支腿局部下沉"),
    "hload_109": ("n_v3a728a9af7e6a44fbb06ec2e6e79e2f3d.webp", "corrugated underground pipe in an open trench", "Exposed corrugated pipe in a construction trench with clear soil boundaries", "A local split opens on the upper surface of the existing trench pipe and muddy water flows from that point along the trench bottom.", "Trench pipe develops a muddy leak", "沟槽管道局部破裂并流出泥水"),
    "hload_215": ("1ed83c6da7fb7856f2050adb836fe58ea2d56670.jpg", "large excavator holding a rock in its bucket", "Complete tracked excavator with visible linkage and an existing rock in the bucket", "The excavator raises the existing rock-filled bucket a short distance while all boom, stick, bucket, and track geometry remains stable.", "Excavator raises rock-filled bucket", "挖掘机抬升装有岩石的铲斗"),
    "hload_225": ("d767e7b67a7bd7192f1fa18451e200847938b32d.jpg", "excavator holding soil above a dump truck", "Tracked excavator with a loaded bucket above a dump truck", "The excavator rotates its bucket slightly and releases only the existing soil into the truck while the hydraulic linkage remains coherent.", "Excavator releases existing soil", "挖掘机向卡车卸下现有土料"),
    "hload_226": ("51182d8b55b041289d3422e68253365d.webp", "mobile crane with extended outriggers", "Mobile crane with clearly visible outrigger beams and support feet", "The nearest visible outrigger foot settles slightly into the ground while the unloaded boom and crane chassis remain rigid and stationary.", "Unloaded crane outrigger settles", "空载起重机支腿轻微下沉"),
    "hload_248": ("u=2128187419,595455552&fm=253&fmt=auto&app=138&f=JPEG.webp", "mobile crane hook lifting a compact suspended load", "Mobile crane, hook line, and small suspended load with visible attachment", "The existing suspended load tilts slightly as its attachment shifts off center; the hook line stays taut and connected.", "Suspended load tilts off center", "悬吊载荷因偏心轻微倾斜"),
    "pdef_108": ("a115ad3039124357a0913926c6397767.webp", "multiple precision linear positioning stages", "Precision linear positioning stages with visible guide rails and carriage references", "The inspection view moves across the existing linear stages and reveals one carriage offset a few millimeters from the common alignment line.", "Linear-stage carriage has small offset", "直线模组滑台轻微错位"),
    "pdef_128": ("84e163b1ea78334ef99647bc79454e4a.jpg", "five-axis CNC milling a turbine impeller", "Five-axis CNC spindle, cutting tool, fixture, and turbine impeller", "The existing cutting tool follows one short curved path across the impeller surface while the spindle, fixture, and workpiece remain coherently coupled.", "CNC follows curved impeller path", "五轴机床加工叶轮曲面"),
    "pdef_134": ("619522816324384.jpg", "borescope view inside a cylindrical pipe", "Borescope view of a cylindrical internal pipe wall", "The borescope advances slightly toward one existing dark linear mark on the inner pipe wall while preserving the cylindrical geometry.", "Borescope approaches inner-wall mark", "内窥镜接近管道内壁痕迹"),
    "pdef_136": ("52510172942598a2c3aba9e6f8ac6c83.jpg", "large machined gear and shaft", "Large machined gear and shaft with clearly visible tooth and surface details", "The inspection camera pans slowly across the existing gear teeth and reveals one short hairline crack near a tooth root; the gear remains stationary.", "Camera reveals gear-root crack", "镜头揭示齿根细微裂纹"),
    "pdef_143": ("f1ad6e49b83d737bec1136f6f16ab02bcec09d95ce28c1e5b83fb7f6a7eb14590f0735f857ed4548.jpg.webp", "dense trays of electrical connector pins", "Dense electrical connectors with repeated exposed metal pins", "One existing pin in the foreground connector bends slightly toward its adjacent pin while all surrounding rows remain unchanged.", "One connector pin bends locally", "连接器单个插针局部弯曲"),
    "pdef_153": ("u=1163592298,535154964&fm=253&fmt=auto&app=120&f=JPEG.webp", "large bolted shaft flange assembly", "Close view of a bolted industrial flange seam and shaft assembly", "A tiny bead of lubricant appears at one existing seam on the central flange while the shaft, bolts, and bearing geometry remain fixed.", "Flange seam develops tiny residue", "法兰接缝出现微量油迹"),
    "pdef_181": ("48834b544315403c9a0e0a79386c244d.webp", "industrial linear guide carriages", "Close view of industrial linear rails and carriage seams", "A tiny lubricant bead appears locally at one existing carriage seal while every rail and carriage remains fixed and aligned.", "Linear-guide seal develops tiny leak", "直线导轨滑块密封处微漏"),
    "vsec_029": ("u=1927390518,606062254&fm=253&fmt=auto&app=138&f=JPEG.webp", "loaded forklift beside stacked cartons", "Forklift carrying a tall visible carton load in an open warehouse area", "The loaded forklift begins a slow turn; the existing carton stack shifts slightly outward under inertia but remains on the forks.", "Forklift load shifts during turn", "叉车转弯时纸箱载荷轻微外移"),
    "vsec_043": ("_3d1Wjdolu6Wk8lqZyNzHgca9c5705a7fa565ad77aa08cc89633d4.jpg", "camera-monitored industrial vehicle gate", "Industrial yard gate with surveillance camera, barrier, vehicles, and clear lane depth", "The inspection view moves slowly toward the gate and reveals the existing red truck entering the monitored lane; the barrier and background remain fixed.", "Camera reveals truck entering gate lane", "镜头揭示卡车进入门岗通道"),
    "vsec_111": ("OIP.webp", "worker standing in front of a forklift", "Forklift and worker at a clearly marked pedestrian crossing", "The existing forklift starts to approach the crossing, brakes, and stops before reaching the worker; the final clearance remains visible.", "Forklift stops before worker", "叉车在行人前停车"),
    "vsec_116": ("24cb4c81b2364b8ebcd1e5681cc1def5.webp", "loaded pallet truck in a warehouse", "Pallet truck carrying a tall wrapped pallet in an open warehouse aisle", "The loaded pallet truck makes a slow turn and the existing wrapped pallet shifts slightly outward without falling.", "Pallet shifts on turning truck", "托盘车转弯时载荷轻微外移"),
    "vsec_167": ("1f6cbcb83dc341a89d3cb50efded2e32.webp", "row of industrial switchgear cabinets", "Industrial switchgear cabinets with visible protective doors and controls", "One existing switchgear door near the center swings open slightly, exposing the protected interior, and the adjacent status light changes to red.", "Switchgear protective door opens", "开关柜防护门意外开启"),
    "vsec_169": ("u=1872633924,2563794974&fm=253&fmt=auto&app=138&f=JPEG.webp", "stacked metal frames", "Stacks of metal frames in an industrial storage area", "One existing metal frame in the stack shifts slightly, leaving the stack visibly misaligned; no new objects or people appear.", "Stacked metal frames shift out of alignment", "堆放的金属架发生轻微错位"),
    "vsec_203": ("u=2214500964,110777370&fm=253&fmt=auto&app=138&f=JPEG.webp", "forklift carrying a wrapped pallet", "Forklift carrying a visible wrapped pallet in a warehouse aisle", "The forklift begins a slow left turn and the existing wrapped pallet shifts slightly outward while remaining supported by the forks.", "Wrapped pallet shifts in forklift turn", "叉车转弯时缠膜托盘轻微外移"),
}


def replace_all(value, pairs):
    if isinstance(value, str):
        for old, new in pairs:
            if old:
                value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_all(x, pairs) for x in value]
    if isinstance(value, dict):
        return {k: replace_all(v, pairs) for k, v in value.items()}
    return value


def normalize_periods(value, sentence: str):
    if isinstance(value, str):
        while sentence + "." in value:
            value = value.replace(sentence + ".", sentence)
        return value
    if isinstance(value, list):
        return [normalize_periods(x, sentence) for x in value]
    if isinstance(value, dict):
        return {k: normalize_periods(v, sentence) for k, v in value.items()}
    return value


def camera_clause(sample: dict) -> str:
    return {
        "static": "locked static camera",
        "orbit": "constant-radius 45 degree orbit around the subject",
        "dolly": "smooth dolly forward while keeping the subject framed",
        "pan": "smooth left-to-right inspection pan, not an orbit",
    }[sample["motion_type"]]


CAMERA_ZH = {
    "static": "相机保持完全固定",
    "orbit": "相机以恒定半径绕主体平滑环绕45度",
    "dolly": "相机保持主体入镜并平滑向前推进",
    "pan": "相机从左向右平滑巡检平移，不得环绕主体",
}


def core_prompt_zh(sample: dict) -> str:
    title = sample.get("task_title_zh") or sample.get("constraint_annotations", {}).get("task_title_zh") or sample["task_id"]
    camera = CAMERA_ZH.get(sample.get("motion_type"), "相机按照题目指定方式运动")
    return (
        f"以参考图作为严格首帧，生成一段5秒的写实工业视频。核心任务：{title}。{camera}。"
        "只执行核心任务明确指定的局部动作；保持已有主体的身份、数量、几何结构、材质、光照、背景和非事件区域不变，"
        "不得凭空增加人员、车辆、工具、载荷、文字或其他物体。"
    )


def save_jpeg(source: Path, destination: Path) -> None:
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        destination.parent.mkdir(parents=True, exist_ok=True)
        im.save(destination, "JPEG", quality=95, optimize=True)


def main() -> None:
    if not set(R).issubset({x["task_id"] for x in json.loads(RESOLUTION.read_text(encoding="utf-8"))["regeneration"]}):
        raise RuntimeError("Replacement map does not exactly cover the approved replacement set")
    missing = [v[0] for v in R.values() if not (NEW / v[0]).is_file()]
    if missing:
        raise FileNotFoundError(missing)

    OUT.mkdir(parents=True, exist_ok=True)
    old_refs = OUT / "original_references"
    new_refs = OUT / "new_references"
    old_refs.mkdir(exist_ok=True)
    new_refs.mkdir(exist_ok=True)
    baseline = {x["task_id"]: x for x in json.loads(OLD_REVIEW.read_text(encoding="utf-8"))}
    audit = {}

    for target in TARGETS:
        payload = json.loads(target.read_text(encoding="utf-8"))
        for index, sample in enumerate(payload["samples"]):
            task_id = sample["task_id"]
            if task_id not in R:
                continue
            filename, subject, requirement, scenario, title, title_zh = R[task_id]
            old_subject = sample.get("reference_subject", "")
            old_requirement = sample.get("image_requirement", "")
            old_scenario = sample.get("constraint_annotations", {}).get("domain_scenario", "")
            old_title = sample.get("task_title", "")
            pairs = [(old_scenario, scenario.rstrip(".")), (old_subject, subject), (old_requirement, requirement), (old_title, title)]
            revised = replace_all(sample, [(old, new) for old, new in pairs if old and old != new])
            revised = normalize_periods(revised, scenario)
            revised["reference_subject"] = subject
            revised["image_requirement"] = requirement
            revised["constraint_annotations"]["domain_scenario"] = scenario.rstrip(".")
            revised["constraint_annotations"]["image_requirement"] = requirement
            revised["constraint_annotations"]["task_title"] = title
            revised["constraint_annotations"]["task_title_zh"] = title_zh
            revised["task_title"] = title
            revised["task_title_zh"] = title_zh
            revised["video_generation_prompt"] = (
                "Use the reference image as the exact first frame. Create a 5-second photorealistic industrial video. "
                + scenario + " Camera: " + camera_clause(sample) + ". "
                "Preserve every visible subject's identity, count, geometry, material, lighting, background, and all non-event regions. "
                "Do not add people, vehicles, tools, loads, text, logos, or other objects not already visible; avoid cuts, global regeneration, flicker, warping, disappearance, penetration, floating motion, and identity swaps."
            )
            payload["samples"][index] = revised
            audit.setdefault(task_id, {"before_prompt": baseline.get(task_id, {}).get("prompt_en", sample["video_generation_prompt"])})["after_prompt"] = revised["video_generation_prompt"]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    canonical_payload = json.loads(TARGETS[1].read_text(encoding="utf-8"))
    canonical = {x["task_id"]: x for x in canonical_payload["samples"]}
    for task_id, (filename, *_rest) in R.items():
        destination = ROOT / canonical[task_id]["image_path"]
        if not (old_refs / f"{task_id}.jpg").exists():
            old_candidates = list((ROOT / "reports" / "prompt_alignment_review_460" / "references").glob(f"{task_id}.*"))
            if len(old_candidates) != 1:
                raise FileNotFoundError(f"Could not recover original reference for {task_id}")
            save_jpeg(old_candidates[0], old_refs / f"{task_id}.jpg")
        save_jpeg(NEW / filename, destination)
        save_jpeg(NEW / filename, new_refs / f"{task_id}.jpg")
        package_image = PACKAGE / "images" / f"{task_id}.jpg"
        if package_image.is_file():
            save_jpeg(NEW / filename, package_image)
        audit[task_id].update({"source_candidate": filename, "image_path": canonical[task_id]["image_path"]})

    prompts_jsonl = PACKAGE / "prompts.jsonl"
    rows = [json.loads(line) for line in prompts_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in rows:
        if row["task_id"] in canonical:
            row["video_generation_prompt"] = canonical[row["task_id"]]["video_generation_prompt"]
    prompts_jsonl.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")

    resolution = json.loads(RESOLUTION.read_text(encoding="utf-8"))
    for row in resolution["regeneration"]:
        if row["task_id"] in R:
            row["action"] = "reference_replaced_ready_to_regenerate"
            row["replacement_source"] = R[row["task_id"]][0]
            row["new_image_path"] = canonical[row["task_id"]]["image_path"]
    RESOLUTION.write_text(json.dumps(resolution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    changed = sorted(set(resolution["changed_prompt_tasks"]) | set(R))
    cards = []
    for number, task_id in enumerate(changed, 1):
        sample = canonical[task_id]
        base = baseline.get(task_id, {})
        before_prompt = audit.get(task_id, {}).get("before_prompt", base.get("prompt_en", ""))
        after_prompt = sample["video_generation_prompt"]
        replaced = task_id in R
        if replaced:
            visuals = f'<figure><figcaption>原参考图</figcaption><img loading="lazy" src="original_references/{task_id}.jpg"></figure><figure><figcaption>最终替换图</figcaption><img loading="lazy" src="new_references/{task_id}.jpg"></figure>'
        else:
            source_ref = ROOT / sample["image_path"]
            review_ref = new_refs / f"{task_id}.jpg"
            if not review_ref.exists():
                if not source_ref.is_file():
                    candidates = list((ROOT / "reports" / "prompt_alignment_review_460" / "references").glob(f"{task_id}.*"))
                    if len(candidates) != 1:
                        raise FileNotFoundError(f"Could not locate review reference for {task_id}")
                    source_ref = candidates[0]
                save_jpeg(source_ref, review_ref)
            visuals = f'<figure class="single"><figcaption>当前参考图（图片未改）</figcaption><img loading="lazy" src="new_references/{task_id}.jpg"></figure>'
        kinds = "换图 + 提示词修改" if replaced else "提示词修改"
        chinese = core_prompt_zh(sample)
        cards.append(f'''<article class="card" id="{task_id}" data-task="{task_id}" data-kind="{'image' if replaced else 'prompt'}"><header><span>{number}/{len(changed)}</span><h2>{task_id}</h2><code>{html.escape(sample['scene_id'])}</code><b>{kinds}</b></header><section class="prompt main-zh"><h3>中文核心提示词</h3><p>{html.escape(chinese)}</p></section><div class="visuals">{visuals}</div><section class="prompt"><h3>修改前（英文原文）</h3><p>{html.escape(before_prompt)}</p></section><section class="prompt after"><h3>修改后（英文数据）</h3><p>{html.escape(after_prompt)}</p></section><div class="review"><label><input type="radio" name="s-{task_id}" value="pass">通过</label><label><input type="radio" name="s-{task_id}" value="revise">还需修改</label><label><input type="radio" name="s-{task_id}" value="unreviewed" checked>未检查</label></div><textarea rows="2" placeholder="记录问题或修改建议"></textarea></article>''')

    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FORGE 所有改动题目最终复核</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#f3f5f7;color:#17202a;font-family:system-ui,"Microsoft YaHei",sans-serif}}.toolbar{{position:sticky;top:0;z-index:3;padding:12px;background:#17202a;color:white;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}button,input,select{{font:inherit;padding:8px}}button{{background:#2f81f7;color:white;border:0;border-radius:5px}}main{{max-width:1500px;margin:auto}}.card{{background:white;margin:14px;padding:16px;border-radius:9px;box-shadow:0 1px 5px #0002}}header{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}h2{{margin:0}}header b{{background:#ddf4ff;padding:4px 8px;border-radius:20px}}.visuals{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}}figure{{margin:0}}figure.single{{grid-column:1/-1;max-width:720px}}img{{width:100%;height:420px;object-fit:contain;background:#111}}.prompt{{padding:10px 12px;margin-top:10px;background:#fff4e5;border-left:5px solid #fb8c00}}.prompt.after{{background:#edf8ee;border-color:#2e7d32}}.prompt h3,.prompt p{{margin:4px 0}}.prompt p{{line-height:1.55}}.review{{display:flex;gap:15px;margin:12px 0;flex-wrap:wrap}}textarea{{width:100%;padding:8px;font:inherit}}.hidden{{display:none}}@media(max-width:720px){{.visuals{{grid-template-columns:1fr}}img{{height:auto;max-height:480px}}.card{{margin:7px;padding:10px}}}}</style></head><body><div class="toolbar"><b>FORGE 最终改动复核</b><input id="q" placeholder="搜索 task ID"><select id="kind"><option value="">全部改动</option><option value="image">换图 + 提示词</option><option value="prompt">仅提示词</option></select><button id="export">导出检查结果</button><span id="progress"></span></div><main>{''.join(cards)}</main><script>const cards=[...document.querySelectorAll('.card')],key='forge-final-changes-review-v1';let state=JSON.parse(localStorage.getItem(key)||'{{}}');for(const c of cards){{let s=state[c.dataset.task]||{{status:'unreviewed',note:''}};c.querySelector(`input[value="${{s.status}}"]`).checked=true;c.querySelector('textarea').value=s.note;c.querySelectorAll('input').forEach(x=>x.onchange=()=>save(c));c.querySelector('textarea').oninput=()=>save(c)}}function save(c){{state[c.dataset.task]={{status:c.querySelector('input:checked').value,note:c.querySelector('textarea').value}};localStorage.setItem(key,JSON.stringify(state));update()}}function update(){{let q=document.querySelector('#q').value.toLowerCase(),k=document.querySelector('#kind').value,shown=0,done=0;for(const c of cards){{let hit=(!q||c.dataset.task.includes(q))&&(!k||c.dataset.kind===k);c.classList.toggle('hidden',!hit);shown+=hit;done+=(state[c.dataset.task]?.status||'unreviewed')!=='unreviewed'}}document.querySelector('#progress').textContent=`已检查 ${{done}}/{len(changed)} · 当前显示 ${{shown}}`}}document.querySelector('#q').oninput=update;document.querySelector('#kind').onchange=update;document.querySelector('#export').onclick=()=>{{let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)],{{type:'application/json'}}));a.download='final_review_results.json';a.click()}};update()</script></body></html>'''
    (OUT / "review.html").write_text(page, encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps({"total_changed": len(changed), "replacement_count": len(R), "tasks": changed, "replacements": audit}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"replacements": len(R), "all_changed": len(changed), "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
