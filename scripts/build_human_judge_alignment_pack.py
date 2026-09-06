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
OUTPUT = ROOT / "reports/human_judge_alignment_pack_40"

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

# These reviewer-approved tasks must survive score-based reselection.
PINNED_TASKS = {"hload_001", "vsec_081", "vsec_119", "vsec_030"}

# Manually rejected after contact-sheet inspection because the visible source
# scene does not directly support the task wording. High diagnostic variance
# never overrides prompt-image compatibility.
EXCLUDED_TASKS = {
    "erob_022", "erob_037", "erob_044", "erob_045", "erob_076", "erob_140",
    "erob_093", "erob_147", "erob_233", "erob_241", "erob_245",
    "emerg_022", "emerg_133", "hload_022", "hload_137", "hload_141",
    "hload_123", "hload_241", "pdef_022", "pdef_062", "pdef_151",
    "pdef_054", "pdef_142", "pdef_147", "pdef_217", "vsec_121", "vsec_169", "vsec_232",
    # Rejected by the human reviewer after inspecting the actual first frame.
    "erob_163", "erob_035", "erob_193", "erob_154", "erob_054", "erob_246", "erob_084",
    "emerg_225", "hload_237", "pdef_072", "vsec_155", "vsec_152",
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

# Faithful reviewer-facing paraphrases.  These clarify the target event but do
# not change its semantics; the original English generation prompt is retained
# beside every Chinese prompt in the blind manifest.
ZH_TASK_SUMMARIES = {
    "erob_007": "多轴工业机械臂完成精密抓取，关节中心稳定，工具与工件可靠接触。绕主体等半径环绕45度。",
    "erob_163": "工人进入设有安全防护的机器作业区后，机器应保持停机或触发保护停机，直至区域清空。固定机位。",
    "erob_035": "四足机器人穿越工业楼梯或碎石障碍，机身身份稳定，足端接触符合物理规律。绕主体等半径环绕45度。",
    "erob_193": "机器人吸盘夹具发生局部滑移或单个吸盘失效，清楚呈现接触状态的变化。平滑向前推进。",
    "erob_154": "仓库AMR在标记路径中遇到行人或临时障碍后减速或停车，并仅在道路清空后继续。固定机位。",
    "erob_054": "工人穿过机器人工作单元的安全光幕，并触发可判断的安全响应。固定机位。",
    "erob_179": "机器人以打磨或焊接工具对工件施加接触力，工具、工件及接触关系保持可信。绕主体等半径环绕45度。",
    "erob_246": "协作机器人在人机交接过程中减速并让行，呈现清楚的动作因果和安全交接状态。固定机位。",
    "emerg_280": "封闭通道内烟雾扩散，人员沿可见疏散路线撤离；烟源、传播方向和能见度变化应合理。固定机位。",
    "emerg_028": "覆冰输电塔在载荷作用下发生局部屈曲或倒塌，展示连续因果过程，未受影响部分保持稳定。平滑向前推进。",
    "emerg_225": "起重机悬吊载荷突然下落或摆动，吊索受力、载荷运动和最终风险状态符合物理规律。绕主体环绕45度。",
    "emerg_011": "罐区管线发生闪火，明确火源、传播方向以及最终受控或升级状态。固定机位。",
    "emerg_001": "法兰连接处发生局部压力泄漏喷射，喷口、喷射方向及扩散过程清晰可信。固定机位。",
    "hload_149": "施工模板或支撑体系发生局部失效，展示载荷传递、变形发展及最终稳定或升级状态。平滑向前推进。",
    "hload_001": "两台履带起重机协同吊装同一钢结构构件，保持吊索受力和载荷姿态可信。绕主体环绕45度。",
    "hload_140": "重型矿用卡车爬升泥泞坡道，车轮转动、下陷和车身运动连续耦合。绕主体环绕45度。",
    "hload_237": "起重机支腿垫板局部下沉，呈现受力、沉降及最终风险状态，车辆结构保持刚性。平滑向前推进。",
    "hload_213": "镜头横向巡检并揭示塔吊吊钩滑轮组、吊臂与邻近结构之间的净空，随后动作继续。不得环绕。",
    "pdef_072": "内窥镜在换热器管束中移动，连续揭示新的内部空间，管束身份和几何结构保持一致。绕主体环绕45度。",
    "pdef_016": "内窥镜接近涡轮叶片或管道内的微裂纹，同时保持内部圆柱几何和缺陷位置稳定。平滑向前推进。",
    "pdef_192": "巡检镜头扫过夹具或托盘并揭示细小定位偏差，零件和夹具身份保持一致。由左向右平移，不得环绕。",
    "pdef_154": "管接头或阀门连接处出现局部微小泄漏或残留物，周围管路几何保持稳定。平滑向前推进。",
    "pdef_063": "精密抛光金属表面出现细小划痕，光照和未受影响表面纹理保持稳定。平滑向前推进。",
    "vsec_155": "起重机转动悬吊载荷并过度接近人员，呈现警告、停止或防护响应以及最终风险状态。绕主体环绕45度。",
    "vsec_081": "工业走廊设备冒烟、报警触发并引导人员疏散，完整呈现可信的因果链。固定机位。",
    "vsec_119": "行人进入仓库叉车通道，呈现报警、停车或警告响应及最终风险是否解除。固定机位。",
    "vsec_152": "高空作业平台上的人员未佩戴安全帽或安全带，并出现可判断的警告或保护响应。固定机位。",
    "vsec_030": "叉车过快转弯，托盘货物因惯性向外滑动，同时叉车几何保持刚性。镜头由左向右平移，不得环绕。",
    "emerg_052": "电池储能集装箱内一个电池模组发生局部热失控，清楚展示传播方向、增长过程及最终遏制或升级状态。由左向右平移，不得环绕。",
    "emerg_091": "工业挡土墙或围堰形成局部缺口，水或浆液从开口逸出并造成合理冲蚀。平滑向前推进。",
    "emerg_301": "工业除尘器或工艺设备连接处出现局部烟尘，并出现报警、隔离或停机响应。固定机位。",
    "hload_083": "施工现场的悬吊载荷逐渐接近邻近结构，清楚展示间隙变化及最终稳定或碰撞风险。固定机位。",
    "hload_072": "施工沟槽内破裂的地下管道引发泥水喷涌，喷口、压力方向、重力流动及围挡边界清楚可信。由左向右平移，不得环绕。",
    "hload_160": "集装箱堆场中的龙门起重机或悬吊载荷受到强风扰动，展示可信摆动及最终稳定或风险升级状态。绕主体环绕45度。",
    "pdef_041": "高速刀具旁的切削液喷嘴喷出切削液，液滴轨迹和局部喷射连续，机床结构保持稳定。固定机位。",
    "pdef_036": "五轴数控铣床加工曲面，主轴与刀具耦合运动、工件装夹和接触关系保持可信。由左向右平移，不得环绕。",
    "pdef_009": "PCB相邻焊点或走线之间形成局部焊锡桥接短路，缺陷保持可见，附近元件不变。平滑向前推进。",
    "vsec_069": "危险品装卸区发生未知化学液体泄漏并沿地面扩散，展示泄漏源、流向、边界及最终遏制或升级状态。固定机位。",
    "vsec_002": "未登记的第三方卡车驶入有明确标记的工业限制区域，触发报警、警告或停止响应。固定机位。",
    "vsec_243": "工业限制区外围围栏或大门受撞击后局部破损，并出现报警或防护响应。平滑向前推进。",
}

# Manual first-frame-grounded repairs. Each instruction names only entities
# that are already visible and requests one deterministic, observable motion.
TASK_REWRITES = {
    "erob_016": (
        "Two collaborative robot arms slowly bow the cello already centered between them; the bow moves horizontally across the strings while both robot bases and the cello remain fixed. Camera: locked static camera.",
        "两台协作机械臂缓慢演奏画面中央已有的大提琴；琴弓沿琴弦水平移动，两台机械臂底座和大提琴位置保持固定。固定机位。",
    ),
    "erob_026": (
        "The small tracked inspection robot already visible drives straight forward a short distance on the flat floor; both tracks rotate consistently and no obstacles are added. Camera: smooth dolly forward.",
        "画面中已有的小型履带巡检机器人沿平整地面直线缓慢前进一小段；两侧履带同步转动，不添加障碍物。镜头平滑向前推进。",
    ),
    "erob_195": (
        "The existing overhead lifting clamp raises the long white panel vertically by a small distance; the visible worker keeps one hand on the guide handle and remains in place. Camera: locked static camera.",
        "现有的上方吊装夹具将白色长板竖直提升一小段；画面中的工人单手扶住导向把手并保持原位。固定机位。",
    ),
    "erob_182": (
        "The robot inside the existing mesh safety enclosure makes one slow controlled arm movement and stops, while the visible worker remains outside the fence. Camera: locked static camera.",
        "现有网状安全围栏内的机器人完成一次缓慢、受控的机械臂动作后停止；画面中的工人始终位于围栏外。固定机位。",
    ),
    "erob_168": (
        "The camera slowly inspects the existing foil-wrapped industrial duct and hose connections, revealing their joints without changing or deforming the insulation. Camera: smooth dolly forward.",
        "镜头缓慢检查画面中已有的铝箔保温工业管道和软管接头，逐步揭示连接处；保温层不得变形或改变。镜头平滑向前推进。",
    ),
    "erob_152": (
        "The yellow automated guided vehicle already parked beside the tank container moves forward slowly and stops before reaching the container support, leaving a clearly visible gap. Camera: locked static camera.",
        "罐式集装箱旁已有的黄色自动导引车缓慢向前移动，并在接触集装箱支架前停车，最终保留清晰可见的间隙。固定机位。",
    ),
    "emerg_219": (
        "The single visible crane remains fixed while its hanging cables develop a small wind-driven sway and then settle; do not add a suspended load or people. Camera: locked static camera.",
        "画面中唯一可见的起重机保持固定，悬垂钢索在风中产生小幅摆动后逐渐稳定；不得添加吊物或人员。固定机位。",
    ),
    "emerg_091": (
        "A short local section of the existing corrugated excavation wall bends inward and releases a narrow stream of muddy water into the contained work area; the rest of the wall remains fixed. Camera: smooth dolly forward.",
        "现有波纹钢基坑围护墙的一小段局部向内弯曲，一股狭窄泥水流进入围护区域；其余墙体保持固定。镜头平滑向前推进。",
    ),
    "emerg_301": (
        "A thin localized plume of gray smoke emerges from the seam beside the existing square vent on the metal air duct and steadily grows slightly denser. Camera: locked static camera.",
        "一股局部灰色薄烟从金属风管现有方形风口旁的接缝冒出，并逐渐略微变浓。固定机位。",
    ),
    "emerg_280": (
        "A thin layer of smoke appears at the far end of the existing train carriage; the visible passengers stand and move slowly toward the near end while all seats and poles remain fixed. Camera: locked static camera.",
        "一层薄烟从现有列车车厢远端出现；画面中的乘客起身并缓慢向近端移动，所有座椅和扶杆保持固定。固定机位。",
    ),
    "emerg_001": (
        "A narrow jet of white vapor begins at the existing central valve connection and continues in one fixed direction; all surrounding pipes and valves remain unchanged. Camera: locked static camera.",
        "一股狭窄白色蒸汽从现有中央阀门接头喷出，并始终沿同一方向流动；周围管道和阀门保持不变。固定机位。",
    ),
    "hload_001": (
        "One crawler crane slowly raises its existing hook and hoist lines; the crane body stays stationary and no second crane or new load is added. Camera: constant-radius 45-degree orbit around the crane.",
        "一台履带起重机缓慢提升其已有吊钩和起升钢索；起重机车体保持静止，不得添加第二台起重机或新的吊物。镜头绕该起重机等半径环绕45度。",
    ),
    "hload_126": (
        "The already suspended precast bridge segments rise together by a small distance, with all hoist lines taut and the segments staying aligned. Camera: locked static camera.",
        "画面中已经悬吊的预制桥梁节段整体小幅上升；所有吊索保持绷紧，各节段之间继续对齐。固定机位。",
    ),
    "hload_117": (
        "The existing excavator slowly curls its empty bucket inward and lifts it slightly above the soil; the tracks and upper body remain stationary. Camera: locked static camera.",
        "画面中已有的挖掘机缓慢向内收拢空铲斗并将其略微抬离地面；履带和上部车体保持静止。固定机位。",
    ),
    "hload_213": (
        "The camera pans slowly from left to right across the existing dock crane, keeping its boom, hanging hook lines, and nearby structures in frame and geometrically stable. Camera: smooth left-to-right pan, not orbit.",
        "镜头从左向右缓慢扫过现有码头起重机，使吊臂、悬垂吊钩钢索和邻近结构持续入镜并保持几何稳定。不得环绕。",
    ),
    "pdef_091": (
        "The camera moves closer to inspect the existing rusted bearing housing, keeping the circular cover, bolts, paint loss, and corrosion pattern unchanged. Camera: smooth dolly forward.",
        "镜头靠近检查画面中已有的锈蚀轴承座；圆形端盖、螺栓、掉漆区域和锈蚀纹理保持不变。镜头平滑向前推进。",
    ),
    "pdef_016": (
        "The camera moves closer to the existing heat-exchanger tube sheet and centers on the two tube openings already marked by white arrows; the tube pattern and markings remain unchanged. Camera: smooth dolly forward.",
        "镜头靠近现有换热器管板，并对准白色箭头已经标出的两个管孔；管孔排列和标记保持不变。镜头平滑向前推进。",
    ),
    "pdef_192": (
        "The existing loose coil spring is inserted vertically into the open brass valve housing, followed by the round valve stem; all other parts remain in their original positions. Camera: locked static camera.",
        "现有的松散螺旋弹簧被竖直放入打开的黄铜阀体，随后放入圆形阀杆；其余零件保持原位。固定机位。",
    ),
    "pdef_154": (
        "The camera moves closer to inspect the existing rusted vessel flange and bolt holes, keeping the corrosion pattern, vessel geometry, and surrounding vegetation unchanged. Camera: smooth dolly forward.",
        "镜头靠近检查现有锈蚀容器法兰和螺栓孔；锈蚀纹理、容器几何形状和周围植被保持不变。镜头平滑向前推进。",
    ),
    "pdef_036": (
        "The existing circular multi-station machine rotates clockwise by one station and stops; its tool heads, cables, base, and neighboring enclosure remain rigid. Camera: locked static camera.",
        "现有圆形多工位设备顺时针转动一个工位后停止；各加工头、电缆、底座和相邻机罩保持刚性。固定机位。",
    ),
    "vsec_081": (
        "A thin localized wisp of smoke emerges from the lower seam of the existing wall-mounted alarm control cabinet; the red alarm bell above it flashes. Camera: locked static camera.",
        "少量局部烟雾从现有壁挂式报警控制柜的下缘缝隙冒出，柜体上方的红色警铃同步闪烁。固定机位。",
    ),
    "vsec_119": (
        "The existing forklift approaches the stacked pallet directly ahead at low speed, brakes, and stops with a clearly visible gap; do not add pedestrians. Camera: locked static camera.",
        "画面中已有的叉车低速接近正前方堆叠托盘，随后制动，并在接触前停车，最终间隙清晰可见；不得添加行人。固定机位。",
    ),
    "vsec_030": (
        "The unloaded foreground forklift makes one slow left turn along the existing warehouse aisle; its empty forks, wheels, mast, and chassis remain rigid and coherent. Do not add pallet cargo. Camera: smooth left-to-right pan, not orbit.",
        "前景中未载货的叉车沿现有仓库通道缓慢左转一次；空货叉、车轮、门架和车身保持刚性一致，不得添加托盘货物。镜头由左向右平移，不得环绕。",
    ),
    "vsec_160": (
        "A faint localized wisp of smoke emerges from one connection inside the existing electrical instrument cabinet, while all meters, switches, and the glass enclosure remain unchanged. Camera: locked static camera.",
        "少量局部烟雾从现有电气仪表柜内的一处连接点冒出；所有仪表、开关和玻璃柜体保持不变。固定机位。",
    ),
    "vsec_241": (
        "The existing closed sliding security gate opens horizontally just wide enough for one vehicle lane and then stops; no vehicle or person enters. Camera: locked static camera.",
        "现有的封闭式滑动安全门沿水平方向打开至一条车道宽度后停止；不得有车辆或人员进入。固定机位。",
    ),
    "vsec_062": (
        "A small localized liquid drip begins at the lower pipe connection of the existing horizontal storage tank and forms a limited wet patch directly below it; do not add people or vehicles. Camera: locked static camera.",
        "少量液体从现有卧式储罐的下部管道接头局部滴漏，并仅在正下方形成有限湿痕；不得添加人员或车辆。固定机位。",
    ),
    "vsec_153": (
        "The empty work platform already mounted on the rail maintenance vehicle rises vertically by a small distance and stops; do not add a worker. Camera: locked static camera.",
        "轨道检修车上已有的空作业平台竖直上升一小段后停止；不得添加作业人员。固定机位。",
    ),
}


def generation_prompt(task: dict) -> str:
    task_id = str(task["task_id"])
    if task_id in TASK_REWRITES:
        instruction = TASK_REWRITES[task_id][0]
    else:
        repaired_prefix = "Use the reference image as the exact first frame. Create a 5-second photorealistic industrial video. "
        existing = str(task["video_generation_prompt"])
        if existing.startswith(repaired_prefix):
            return existing
        # Retain the task-specific scene/action/camera portion, but remove the
        # old category boilerplate containing open alternatives such as
        # "stability/escalation" or "hazard contained/active".
        instruction = existing.split(" Show a localized", 1)[0]
        prefix = "Use the reference image as the exact first frame and create a 5-second photorealistic industrial video of "
        if instruction.startswith(prefix):
            instruction = instruction[len(prefix):]
    protected_objects = (
        "vehicles, tools, loads, text, logos, or objects"
        if task_id == "vsec_081"
        else "people, vehicles, tools, loads, text, logos, or objects"
    )
    return (
        "Use the reference image as the exact first frame. Create a 5-second photorealistic industrial video. "
        + instruction.strip()
        + " Preserve all visible identities, object counts, geometry, materials, lighting, background, and non-event regions. "
        f"Perform only the stated action. Do not introduce any unrequested {protected_objects}. "
        "Avoid cuts, global regeneration, flicker, warping, disappearance, penetration, floating motion, and identity swaps."
    )


def reviewer_zh(task_id: str) -> str:
    if task_id in TASK_REWRITES:
        summary = TASK_REWRITES[task_id][1]
    else:
        summary = ZH_TASK_SUMMARIES.get(task_id)
    if not summary:
        return "【待人工确认中文翻译】"
    return (
        "以参考画面作为严格首帧，生成一段5秒的写实工业视频。任务：" + summary
        + " 保持主体身份、部件数量、材质、光照、背景和非事件区域一致；仅允许指定事件和相机视角变化。"
        "不得添加文字、标志、水印或无关实体；不得出现全局重生成、闪烁、扭曲、消失、穿透、漂浮运动或身份替换。"
    )

CANDIDATE_JUDGES = [
    {
        "model": "Qwen3-VL-235B-A22B-Instruct-FP8",
        "role": "现有可复现的大规模开放权重基线",
    },
    {
        "model": "NVIDIA Cosmos-Reason2-32B",
        "role": "面向物理 AI、工业视频与时空推理的专项候选",
    },
    {
        "model": "Gemini 3.1 Pro",
        "role": "闭源原生视频理解能力的上界候选",
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
        chosen = [x for x in pool if x["task_id"] in PINNED_TASKS]
        used_scenes = {str(x.get("scene_id")) for x in chosen}
        used_categories = {str(x.get("task_category")) for x in chosen}
        for row in pool:
            scene = str(row.get("scene_id"))
            category = str(row.get("task_category"))
            if scene in used_scenes:
                continue
            # Prefer category diversity for the first four slots.
            if len(chosen) < 4 and category in used_categories:
                continue
            chosen.append(row)
            used_scenes.add(scene)
            used_categories.add(category)
            if len(chosen) == 8:
                break
        if len(chosen) < 8:
            for row in pool:
                if row in chosen or str(row.get("scene_id")) in used_scenes:
                    continue
                chosen.append(row)
                used_scenes.add(str(row.get("scene_id")))
                if len(chosen) == 8:
                    break
        if len(chosen) != 8:
            raise RuntimeError(f"Could not select eight valid tasks for {domain}; eligible pool={len(pool)}")
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
    edges = balanced_edges(list(MODELS)) * 2
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
        zh = reviewer_zh(str(task["task_id"]))
        row = {
            "pair_id": pair_id,
            "task_id": task["task_id"],
            "domain": task["domain"],
            "primary_aspect_zh": aspect,
            "prompt_zh": zh,
            "prompt_en": generation_prompt(task),
            "required_observable_events": [
                (TASK_REWRITES[str(task["task_id"])][0] if str(task["task_id"]) in TASK_REWRITES
                 else str(task["video_generation_prompt"]).split(" Camera:", 1)[0])
            ],
            "reference_image": str(ref_dst.relative_to(OUTPUT)).replace("\\", "/"),
            "reference_image_note_zh": "原始参考图当前不在工作区；此图为固定基准视频的首帧代理，仅用于核对任务与画面语义是否匹配。",
            "video_a": str(dst_a.relative_to(OUTPUT)).replace("\\", "/"),
            "video_b": str(dst_b.relative_to(OUTPUT)).replace("\\", "/"),
            "question_zh": f"在“{aspect}”方面，A和B哪个更符合任务？",
            "allowed_labels": ["A", "B", "tie", "both_invalid"],
            "allowed_labels_zh": {"A": "A更好", "B": "B更好", "tie": "平局", "both_invalid": "两者都不合格"},
        }
        public.append(row)
        private.append({
            "pair_id": pair_id,
            "task_id": task["task_id"],
            "model_a": model_a,
            "model_b": model_b,
            "diagnostic_score": round(task["diagnostic_score"], 4),
            "diagnostic_axis": task["diagnostic_axis"],
            "prompt_manually_rewritten": str(task["task_id"]) in TASK_REWRITES,
            "original_generation_prompt": task["video_generation_prompt"],
            "review_prompt": generation_prompt(task),
            "provenance_note": (
                "Videos predate the review-prompt repair; use this pack for judge-selection analysis, "
                "not as evidence that generation followed the repaired prompt."
            ),
        })
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
        "NVIDIA Cosmos-Reason2-32B 和 Gemini 3.1 Pro。\n\n共40组盲化A/B、80个视频，十个生成模型各出现8次，五个场景域各8组。"
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
    reviewer_text = json.dumps(public, ensure_ascii=False) + json.dumps(CANDIDATE_JUDGES, ensure_ascii=False)
    if "�" in reviewer_text or not summary["translation_complete"]:
        raise RuntimeError("Reviewer-facing Chinese text is incomplete or contains replacement characters")
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
