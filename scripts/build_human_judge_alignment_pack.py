#!/usr/bin/env python3
"""Build a compact, blind, all-model pairwise human-alignment review pack."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "dataset/annotations/video_generation_500_samples.json"
OUTPUT = ROOT / "reports/human_judge_alignment_pack_20"

MODELS = {
    "cogvideox1.5": ROOT / "dataset/six_model_video_dataset_3000/cogvideox1.5",
    "hunyuan1.5": ROOT / "dataset/six_model_video_dataset_3000/hunyuan1.5",
    "hunyuan1.5-distill": ROOT / "dataset/six_model_video_dataset_3000/hunyuan1.5-distill",
    "minimax-hailuo-2.3": ROOT / "dataset/six_model_video_dataset_3000/minimax",
    "wan2.1": ROOT / "dataset/six_model_video_dataset_3000/wan2.1",
    "wan2.2": ROOT / "dataset/six_model_video_dataset_3000/wan2.2",
    "minimax-h3": ROOT / "dataset/forge_minimax_h3_500",
    "kling3.0-standard": ROOT / "dataset/kling3.0-standard",
    "seedance2.5": ROOT / "dataset/seedance2.5",
    "wan3.0": ROOT / "dataset/wan3.0",
}

REPORTS = {
    "hunyuan1.5": ROOT / "reports/formal_235b_contactsheet_20260903/combined/hunyuan1.5/per_sample.json",
    "hunyuan1.5-distill": ROOT / "reports/formal_235b_hunyuan15_distill_20260904/combined/hunyuan1.5-distill/per_sample.json",
    "minimax-hailuo-2.3": ROOT / "reports/formal_235b_minimax_20260904/combined/minimax/per_sample.json",
}

DOMAIN_DIRS = {"precision_defect_gen": "precision_defect_generation"}
DOMAINS = (
    "embodied_robotics",
    "extreme_emergency",
    "heavy_load_construction",
    "precision_defect_gen",
    "visual_security",
)

# Manually rejected after contact-sheet inspection because the visible source
# scene does not directly support the task wording. High diagnostic variance
# never overrides prompt-image compatibility.
EXCLUDED_TASKS = {
    "erob_076", "erob_241", "emerg_022", "hload_022", "hload_137",
    "hload_241", "pdef_062", "pdef_217",
}

AXES = (
    "industrial_logic_and_fact_alignment",
    "geometric_integrity",
    "physical_plausibility",
    "temporal_consistency",
    "reference_and_motion_fidelity",
)

ASPECT_ZH = {
    "industrial_logic_and_compliance": "工业逻辑与事件因果",
    "fluid_dynamics_and_thermodynamics": "流体、烟火或热过程的物理合理性",
    "rigid_body_kinematics_and_coupling": "刚体运动、连接关系与载荷传递",
    "spatial_exploration_and_viewpoint": "相机运动、空间揭示与参考保持",
    "topology_mutation_and_failure": "拓扑变化、断裂或局部缺陷真实性",
}

def zh_prompt(subject: str, camera: str, event: str) -> str:
    return (
        f"以参考画面作为严格首帧，生成一段5秒的写实工业视频。场景：{subject}。"
        f"相机：{camera}。{event}。"
        "保持主体身份、部件数量、材质、光照、背景和非事件区域一致；仅允许指定事件及相机视角发生变化。"
        "不得添加文字、标志、水印或无关实体；不得出现全局重生成、闪烁、扭曲、消失、穿透、漂浮运动或身份替换。"
    )


TRANSLATIONS: dict[str, str] = {
    "erob_007": zh_prompt("多轴工业机械臂以稳定关节中心和可靠的工具—工件接触完成精密抓取", "以恒定半径绕主体环绕45度", "清楚展示抓取动作的因果过程，并在结尾呈现明确的接触、抓取或放置终态"),
    "erob_241": zh_prompt("仓库AGV驶近关闭的卷帘门；联锁应使车辆等待，直到门打开且通道清空", "固定监控视角，不移动", "清楚展示接近、等待、开门及安全通行之间的正确先后关系"),
    "erob_037": zh_prompt("四足机器人穿越工业楼梯和复杂碎石区域，机身身份保持稳定，足端接触必须合理", "平滑地从左向右巡检平移，不得环绕", "展示机器人稳定通过障碍的连续过程以及可信的落脚和接触"),
    "erob_016": zh_prompt("协作机器人工作站中，机械臂在人机交接时减速并主动让行", "固定视角，不移动", "展示人的接近如何触发机器人减速或让行，并呈现安全的交接终态"),
    "erob_245": zh_prompt("协作机器人工作站中，机械臂在人机交接时减速并主动让行", "固定视角，不移动", "展示人的接近如何触发机器人减速或让行，并呈现安全的交接终态"),
    "erob_140": zh_prompt("仓库中的两台移动机器人协调交接或主动避让", "以恒定半径绕主体环绕45度", "展示两台机器人之间可判断的协调、交接或避让过程，并保持各自身份与接触关系稳定"),
    "emerg_052": zh_prompt("电池储能集装箱内一个电池模组发生热失控", "平滑地从左向右巡检平移，不得环绕", "展示热失控从局部开始及其传播方向和增长过程，结尾保留遏制、疏散或继续升级的可判断线索"),
    "emerg_022": zh_prompt("覆冰输电塔按照桁架支撑拓扑发生局部屈服和倒塌", "保持主体入镜并平滑向前推进", "展示载荷作用、局部屈服到倒塌的连续因果过程，未受影响的塔体结构保持稳定"),
    "emerg_301": zh_prompt("工业除尘器或工艺设备连接处出现局部烟尘，并出现报警、隔离或停机响应", "固定视角，不移动", "展示烟尘的明确设备来源、传播方向以及随后发生的处置响应，设备布局不得改变"),
    "emerg_133": zh_prompt("冷却塔蒸汽羽流因风机或流量故障发生变化", "固定视角，不移动", "展示羽流从正常到异常的连续变化、合理流动方向及可判断的最终状态"),
    "emerg_091": zh_prompt("工业挡土墙或围堰形成局部缺口，水或浆液从开口逸出并造成合理冲蚀", "保持主体入镜并平滑向前推进", "展示局部破口形成、流体逸出方向、冲蚀增长以及结尾的遏制或继续升级状态"),
    "hload_137": zh_prompt("两台履带起重机协同吊装同一钢结构模块", "以恒定半径绕主体环绕45度", "展示两台起重机协调运动、吊索受力和载荷姿态，并在结尾呈现稳定或风险升级状态"),
    "hload_083": zh_prompt("施工现场的悬吊载荷逐渐接近附近结构", "固定视角，不移动", "展示载荷接近、间隙变化及最终稳定或碰撞风险，吊索和载荷关系必须保持合理"),
    "hload_241": zh_prompt("施工沟槽内破裂的地下管道引发泥水喷涌", "固定视角，不移动", "展示明确破口、压力方向、重力流动和围挡边界，并在结尾呈现风险是否受到控制"),
    "hload_072": zh_prompt("施工沟槽内破裂的地下管道引发泥水喷涌", "平滑地从左向右巡检平移，不得环绕", "展示明确破口、压力方向、重力流动和围挡边界，并在结尾呈现风险是否受到控制"),
    "hload_141": zh_prompt("重型矿用卡车爬上泥泞坡道，轮胎产生下陷和接触变形", "以恒定半径绕主体环绕45度", "展示车轮转动、泥地接触、下陷和车辆爬坡之间的连续耦合关系"),
    "hload_160": zh_prompt("集装箱堆场中的龙门起重机或悬吊载荷受到强风扰动", "以恒定半径绕主体环绕45度", "展示风扰、结构或载荷摆动以及最终稳定或风险升级状态，起重机拓扑和吊挂关系保持可信"),
    "pdef_041": zh_prompt("高速刀具旁的切削液喷嘴喷出切削液", "固定视角，不移动", "展示连贯的液滴轨迹和局部喷射过程，机床及周围结构不得发生融化或整体变形"),
    "pdef_062": zh_prompt("抛光金属精密表面出现细小划痕，未受影响的表面纹理与光照保持稳定", "保持主体入镜并平滑向前推进", "通过前后变化明确定位局部划痕，不得用全局纹理或整体变形伪造缺陷"),
    "pdef_217": zh_prompt("内窥镜在换热器管束内部移动检查", "平滑地从左向右巡检平移，不得环绕", "展示管束之间连续可信的空间移动，并揭示新的检查区域而不丢失管道身份"),
    "pdef_036": zh_prompt("五轴数控铣床加工曲面，主轴与刀具耦合运动，工件装夹稳定", "平滑地从左向右巡检平移，不得环绕", "展示合理的五轴加工运动和稳定的刀具—工件接触，周围机床结构保持不变"),
    "pdef_022": zh_prompt("工业齿轮齿面特写中，一个轮齿出现崩缺或严重磨损", "保持主体入镜并平滑向前推进", "缺陷只能出现在指定轮齿并持续可见，其他齿形、材质和周围结构保持稳定"),
    "pdef_009": zh_prompt("PCB电路板相邻焊点或走线之间形成局部焊锡桥接短路", "保持主体入镜并平滑向前推进", "清楚展示局部焊锡桥接的出现或持续存在，附近元件数量与正常区域保持不变"),
    "vsec_069": zh_prompt("危险品装卸区发生未知化学液体泄漏，并沿地面扩散", "固定视角，不移动", "展示明确泄漏源、符合重力的流动方向、扩散边界以及结尾的遏制或继续升级状态"),
    "vsec_002": zh_prompt("未登记的第三方卡车驶入有明确标记的工业限制区域", "固定视角，不移动", "展示车辆进入如何触发报警、警告或停止响应，并在结尾明确风险是否仍然存在"),
    "vsec_243": zh_prompt("工业限制区外围围栏或大门受到撞击后局部破损", "保持主体入镜并平滑向前推进", "展示撞击、局部断裂以及随后的报警或防护响应，围栏其他部分保持稳定"),
    "vsec_121": zh_prompt("工人或车辆接近尚未隔离的工业轨道检修坑或轨道通道", "固定视角，不移动", "展示接近行为以及在进入危险区域前建立警告、停止或物理隔离的正确顺序"),
}

CANDIDATE_JUDGES = [
    {
        "model": "Qwen3-VL-235B-A22B-Instruct-FP8",
        "role": "现有可复现大规模开放权重基线",
    },
    {
        "model": "NVIDIA Cosmos-Reason2-32B",
        "role": "物理AI、工业视频与时空推理专项候选",
    },
    {
        "model": "Gemini 3.1 Pro",
        "role": "闭源原生视频能力上界候选",
    },
]


def load_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else payload["samples"]


def video_path(model_root: Path, domain: str, task_id: str) -> Path:
    direct = model_root / DOMAIN_DIRS.get(domain, domain) / f"{task_id}.mp4"
    if direct.is_file():
        return direct
    matches = list(model_root.rglob(f"{task_id}.mp4"))
    return matches[0] if len(matches) == 1 else direct


def sane_video(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    cap = cv2.VideoCapture(str(path))
    ok = cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) >= 8
    ok = ok and int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) >= 256
    ok = ok and int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) >= 256
    cap.release()
    return bool(ok)


def report_index() -> dict[str, dict[str, dict]]:
    return {
        model: {str(row["task_id"]): row for row in load_rows(path)}
        for model, path in REPORTS.items()
    }


def diagnostic_score(task_id: str, reports: dict[str, dict[str, dict]]) -> tuple[float, str]:
    rows = [reports[m][task_id] for m in REPORTS if task_id in reports[m]]
    ranges: dict[str, float] = {}
    for axis in AXES:
        values = [float((row.get("scored") or {}).get("axis_scores", {}).get(axis, 0.0)) for row in rows]
        ranges[axis] = max(values) - min(values)
    event = [float(row.get("observable_event_coverage") or 0.0) for row in rows]
    app = [float(row.get("application_usefulness_score") or 0.0) for row in rows]
    strongest_axis = max(ranges, key=ranges.get)
    score = ranges[strongest_axis] + 0.45 * (max(event) - min(event)) + 0.25 * (max(app) - min(app))
    return score, strongest_axis


def select_tasks(rows: list[dict], reports: dict[str, dict[str, dict]]) -> list[dict]:
    candidates: list[dict] = []
    for row in rows:
        task_id = str(row["task_id"])
        domain = str(row["domain"])
        if task_id in EXCLUDED_TASKS:
            continue
        if any(task_id not in reports[m] for m in REPORTS):
            continue
        paths = {model: video_path(base, domain, task_id) for model, base in MODELS.items()}
        if not all(path.is_file() and path.stat().st_size >= 1024 for path in paths.values()):
            continue
        score, axis = diagnostic_score(task_id, reports)
        candidate = dict(row)
        candidate["diagnostic_score"] = score
        candidate["diagnostic_axis"] = axis
        candidate["all_video_paths"] = paths
        candidates.append(candidate)

    selected: list[dict] = []
    for domain in DOMAINS:
        pool = sorted((x for x in candidates if x["domain"] == domain), key=lambda x: -x["diagnostic_score"])
        used_scenes: set[str] = set()
        used_categories: set[str] = set()
        chosen: list[dict] = []
        for row in pool:
            scene = str(row.get("scene_id"))
            category = str(row.get("task_category"))
            if scene in used_scenes:
                continue
            # Prefer category diversity for the first three slots.
            if len(chosen) < 3 and category in used_categories:
                continue
            chosen.append(row)
            used_scenes.add(scene)
            used_categories.add(category)
            if len(chosen) == 4:
                break
        if len(chosen) < 4:
            for row in pool:
                if row in chosen or str(row.get("scene_id")) in used_scenes:
                    continue
                chosen.append(row)
                used_scenes.add(str(row.get("scene_id")))
                if len(chosen) == 4:
                    break
        if len(chosen) != 4:
            raise RuntimeError(f"Could not select four valid tasks for {domain}; eligible pool={len(pool)}")
        selected.extend(chosen)
    return selected


def balanced_edges(models: list[str]) -> list[tuple[str, str]]:
    # A 4-regular circulant graph: every one of ten models appears exactly four times.
    edges: set[tuple[str, str]] = set()
    for i, model in enumerate(models):
        for distance in (1, 2):
            other = models[(i + distance) % len(models)]
            edges.add(tuple(sorted((model, other))))
    return sorted(edges)


def swap(pair_id: str) -> bool:
    return bool(hashlib.sha256(f"forge-human-alignment-v1:{pair_id}".encode()).digest()[0] & 1)


def sample_frames(path: Path, count: int = 10) -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(path))
    total = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    frames = []
    for index in np.linspace(0, total - 1, count).round().astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        width = 220
        frames.append(cv2.resize(frame, (width, round(h * width / w)), interpolation=cv2.INTER_AREA))
    cap.release()
    return frames


def write_reference_proxy(path: Path, output: Path) -> None:
    cap = cv2.VideoCapture(str(path))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not extract first frame from {path}")
    cv2.imwrite(str(output), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])


def contact_sheet(a: Path, b: Path, output: Path) -> None:
    rows = []
    for label, path in (("A", a), ("B", b)):
        frames = sample_frames(path)
        if len(frames) != 10:
            raise RuntimeError(f"Could not sample {path}")
        row = cv2.hconcat(frames)
        cv2.rectangle(row, (0, 0), (52, 34), (0, 0, 0), -1)
        cv2.putText(row, label, (10, 27), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
        rows.append(row)
    cv2.imwrite(str(output), cv2.vconcat(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])


def build() -> None:
    rows = load_rows(ANNOTATIONS)
    reports = report_index()
    selected = select_tasks(rows, reports)
    selected.sort(key=lambda x: (DOMAINS.index(x["domain"]), -x["diagnostic_score"]))
    edges = balanced_edges(list(MODELS))
    if len(edges) != len(selected):
        raise AssertionError((len(edges), len(selected)))

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "videos").mkdir(parents=True)
    (OUTPUT / "references").mkdir()
    (OUTPUT / "contact_sheets").mkdir()

    public: list[dict] = []
    private: list[dict] = []
    cards: list[str] = []
    for index, (task, edge) in enumerate(zip(selected, edges), 1):
        pair_id = f"pair_{index:02d}"
        model_a, model_b = edge
        if swap(pair_id):
            model_a, model_b = model_b, model_a
        pair_dir = OUTPUT / "videos" / pair_id
        pair_dir.mkdir()
        src_a = task["all_video_paths"][model_a]
        src_b = task["all_video_paths"][model_b]
        if not sane_video(src_a) or not sane_video(src_b):
            raise RuntimeError(f"Selected pair failed decode validation: {pair_id}")
        dst_a, dst_b = pair_dir / "A.mp4", pair_dir / "B.mp4"
        shutil.copy2(src_a, dst_a)
        shutil.copy2(src_b, dst_b)
        ref_dst = OUTPUT / "references" / f"{task['task_id']}_first_frame_proxy.jpg"
        write_reference_proxy(task["all_video_paths"]["hunyuan1.5"], ref_dst)
        sheet = OUTPUT / "contact_sheets" / f"{pair_id}.jpg"
        contact_sheet(dst_a, dst_b, sheet)
        aspect = ASPECT_ZH.get(str(task.get("task_category")), "任务完成与工业可信度")
        zh = TRANSLATIONS.get(str(task["task_id"]), "【待人工确认中文翻译】")
        row = {
            "pair_id": pair_id,
            "task_id": task["task_id"],
            "domain": task["domain"],
            "primary_aspect_zh": aspect,
            "prompt_zh": zh,
            "prompt_en": task["video_generation_prompt"],
            "required_observable_events": task.get("required_observable_events") or [],
            "reference_image": str(ref_dst.relative_to(OUTPUT)).replace("\\", "/"),
            "reference_image_note_zh": "原始参考图当前不在工作区；此图为固定基准视频的首帧代理，仅用于核对任务与画面语义是否匹配。",
            "video_a": str(dst_a.relative_to(OUTPUT)).replace("\\", "/"),
            "video_b": str(dst_b.relative_to(OUTPUT)).replace("\\", "/"),
            "question_zh": f"在“{aspect}”方面，A和B哪个更符合任务？",
            "allowed_labels": ["A", "B", "tie", "both_invalid"],
            "allowed_labels_zh": {"A": "A更好", "B": "B更好", "tie": "平局", "both_invalid": "两者都不合格"},
        }
        public.append(row)
        private.append({"pair_id": pair_id, "task_id": task["task_id"], "model_a": model_a, "model_b": model_b,
                        "diagnostic_score": round(task["diagnostic_score"], 4), "diagnostic_axis": task["diagnostic_axis"]})
        cards.append(
            f"<section><h2>{pair_id} · {html.escape(aspect)}</h2>"
            f"<p><b>中文任务：</b>{html.escape(zh)}</p>"
            f"<p><b>评审问题：</b>{html.escape(row['question_zh'])}</p>"
            f"<img class='ref' src='{row['reference_image']}'><img class='sheet' src='contact_sheets/{pair_id}.jpg'>"
            f"<div class='pair'><div><h3>A</h3><video controls src='{row['video_a']}'></video></div>"
            f"<div><h3>B</h3><video controls src='{row['video_b']}'></video></div></div></section>"
        )

    (OUTPUT / "blind_manifest.json").write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "private_model_key.json").write_text(json.dumps(private, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "candidate_judges.json").write_text(
        json.dumps(CANDIDATE_JUDGES, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (OUTPUT / "human_labels.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["pair_id", "human_label", "reviewer_id", "confidence", "reason", "both_reasonable"])
        for row in public:
            writer.writerow([row["pair_id"], "", "", "", "", ""])
    (OUTPUT / "README_中文.md").write_text(
        "# FORGE 裁判模型人类对齐包\n\n候选裁判固定为 Qwen3-VL-235B-A22B-Instruct-FP8、"
        "NVIDIA Cosmos-Reason2-32B 和 Gemini 3.1 Pro。\n\n共20组盲化A/B、40个视频，十个生成模型各出现4次，五个场景域各4组。"
        "先确认首帧代理与任务匹配；不匹配时不要评价并在CSV的both_reasonable列填no。其余样本在human_label列填写A、B、tie或both_invalid，"
        "并在both_reasonable列填写yes。"
        "不要根据画面华丽程度推断任务完成，必须以可见事件、物理过程和终态为准。\n",
        encoding="utf-8",
    )
    review = """<!doctype html><meta charset='utf-8'><title>FORGE 人类对齐盲测</title>
<style>body{font-family:sans-serif;max-width:1500px;margin:auto}section{border-bottom:2px solid #bbb;padding:18px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}video,.sheet{width:100%}.ref{max-width:420px;max-height:300px}</style>
<h1>FORGE 裁判模型人类对齐盲测</h1><p>先检查参考图与中文任务是否匹配，再观看A/B。只评价题目指定方面。</p>
""" + "\n".join(cards)
    (OUTPUT / "blind_review.html").write_text(review, encoding="utf-8")
    summary = {
        "pairs": len(public), "videos": len(public) * 2,
        "model_appearances": dict(sorted((m, sum(m in (r["model_a"], r["model_b"]) for r in private)) for m in MODELS)),
        "domain_pairs": dict(sorted((d, sum(r["domain"] == d for r in public)) for d in DOMAINS)),
        "translation_complete": all(r["prompt_zh"] != "【待人工确认中文翻译】" for r in public),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    zip_path = OUTPUT.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in OUTPUT.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(OUTPUT.parent))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(zip_path)


if __name__ == "__main__":
    build()
