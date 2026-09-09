#!/usr/bin/env python3
"""Build an offline image/prompt/video-frame audit page for the 460 unreviewed tasks."""

from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "dataset/annotations/video_generation_500_samples.json"
REVIEWED_MANIFEST = ROOT / "reports/human_judge_alignment_pack_40/blind_manifest.json"
SOURCE_IMAGES = ROOT / "reports/video_generation_500_package/images"
VIDEO_ROOT = ROOT / "dataset/six_model_video_dataset_3000/hunyuan1.5"
OUTPUT = ROOT / "reports/prompt_alignment_review_460"

DOMAIN_ZH = {
    "embodied_robotics": "具身机器人",
    "extreme_emergency": "极端应急",
    "heavy_load_construction": "重载施工",
    "precision_defect_gen": "精密缺陷",
    "visual_security": "视觉安全",
}

CATEGORY_ZH = {
    "industrial_logic_and_compliance": "工业逻辑与合规",
    "fluid_dynamics_and_thermodynamics": "流体与热过程",
    "rigid_body_kinematics_and_coupling": "刚体运动与耦合",
    "spatial_exploration_and_viewpoint": "空间探索与视角",
    "topology_mutation_and_failure": "拓扑变化与失效",
}

SCENE_ZH = {
    "emerg_battery_thermal_runaway": "电池储能集装箱内的一个电池模组发生热失控。",
    "emerg_cooling_tower_plume_failure": "冷却塔蒸汽羽流因风机或流量故障发生明显变化。",
    "emerg_crane_load_drop_evacuation": "施工场地中起重机的悬吊载荷开始危险下落。",
    "emerg_dam_or_retaining_wall_breach": "挡土墙或围堰形成局部缺口，泥水从缺口流出并造成局部冲蚀。",
    "emerg_dust_explosion_confined_space": "粮仓除尘区域的违规动火点燃局部粉尘云。",
    "emerg_flange_high_pressure_leak": "中央阀门接头喷出方向固定的狭窄白色蒸汽。",
    "emerg_hot_work_spark_combustible_fire": "工业除尘或工艺设备处出现局部烟雾，并触发明确的停机响应。",
    "emerg_reactor_runaway_pressure_release": "化学反应器超压后开启泄压阀，气体沿泄压路径排出。",
    "emerg_smoke_evacuation_route_visibility": "封闭通道远端出现薄烟，画面中的人员沿可见通道向近端移动。",
    "emerg_storage_tank_flash_fire": "储罐区管线连接处发生局部闪火，火焰沿邻近管线短距离传播。",
    "emerg_transmission_tower_icing_collapse": "覆冰输电塔的局部桁架受载屈曲并发生局部倒塌。",
    "emerg_tunnel_fire_smoke_layering": "工业隧道内的火源产生沿顶棚移动的分层烟气。",
    "erob_agv_rollup_door_interlock": "AGV接近关闭的卷帘门，在门完全打开且通道清空前停车等待。",
    "erob_amr_charger_smoke_abort": "AMR在既有行驶路径中遇到障碍后减速停车，并在路径清空后继续。",
    "erob_amr_warehouse_navigation": "AMR绕过仓库中的托盘，车轮路径合理且底盘几何保持稳定。",
    "erob_cobot_human_handover": "协作机器人在人机交接过程中减速让行，避免发生接触。",
    "erob_cobot_safety_scanner_slowdown": "人员进入受防护的机器作业区后，机器触发保护停机并保持停止。",
    "erob_gripper_failure_recovery": "机器人夹具发生局部滑移，一个已有吸盘失效。",
    "erob_light_curtain_emergency_stop": "人员穿过机器人单元的安全光幕后，机器立即停止并保持停止。",
    "erob_multi_robot_coordination": "两台移动机器人完成一次协调避让，彼此不发生碰撞。",
    "erob_quadruped_stairs_rubble_fpv": "四足机器人连续穿越楼梯或碎石，机身身份和足端接触保持合理。",
    "erob_robot_arm_precision_grasp": "多轴工业机械臂完成一次精密抓取，关节和工具—工件接触保持稳定。",
    "erob_robot_tool_contact_force": "机器人将已有工具压向工件并保持可信的接触力。",
    "erob_tracked_robot_rubble": "履带巡检机器人越过碎石障碍，履带接触和障碍几何保持稳定。",
    "hload_blind_lift_spotter_view": "镜头揭示起重机吊钩、吊臂和邻近结构之间的实际间隙。",
    "hload_bridge_segment_alignment_drone": "镜头环绕检查正在吊装的预制桥梁节段，节段几何和尺度保持稳定。",
    "hload_dual_crawler_crane_lift": "一台履带起重机缓慢提升已有吊钩和钢索，不添加第二台起重机或新吊物。",
    "hload_excavator_linkage_loading": "挖掘机通过液压连杆完成一次带载铲斗动作。",
    "hload_formwork_collapse_local": "施工模板支撑体系的一处局部构件受载失效。",
    "hload_gantry_wind_disturbance": "强风使龙门起重机的已有悬吊载荷发生小幅摆动。",
    "hload_ground_settlement_outrigger": "起重机支腿垫板局部陷入软土，车体和吊臂保持刚性。",
    "hload_hoist_collision_near_structure": "起重机已有悬吊载荷缓慢接近邻近建筑结构并保留可见间隙。",
    "hload_mining_truck_muddy_slope": "重型矿用卡车爬升泥泞坡道，轮胎转动、下陷和车身运动连续耦合。",
    "hload_sling_angle_center_of_gravity": "不等角吊索使已有载荷发生合理倾斜，吊钩和吊索保持连接。",
    "hload_tunnel_pipe_burst_mud_surge": "施工沟槽内的地下管道破裂并喷出沿重力方向流动的泥水。",
    "hload_wire_rope_overload_snap": "起重机已有钢丝绳在过载下局部变形并断裂。",
    "pdef_cnc_curved_surface_cutting": "五轴数控机床加工曲面，主轴、刀具和工件夹具保持可信关系。",
    "pdef_connector_pin_bent": "电连接器特写中，一个已有插针发生局部弯曲。",
    "pdef_cutting_fluid_spray": "切削液从已有喷嘴喷向高速刀具，液滴轨迹连续。",
    "pdef_engine_endoscope_crack": "内窥镜靠近已有内部表面的一条微裂纹，内部几何保持稳定。",
    "pdef_flange_seal_micro_leak": "已有管接头处出现一处局部微小泄漏，周围管路几何保持稳定。",
    "pdef_gauge_level_valve_anomaly": "巡检镜头横向移动并揭示已有夹具或托盘的一处小定位偏差。",
    "pdef_gear_tooth_missing_wear": "工业齿轮特写中，一个已有轮齿发生局部崩缺。",
    "pdef_pcb_solder_bridge_short": "PCB相邻焊盘之间形成一处局部焊锡桥，附近元件数量保持不变。",
    "pdef_precision_assembly_misalignment": "精密装配过程中，一个已有零件出现轻微定位偏差。",
    "pdef_surface_scratch_inspection": "精密金属表面出现一条细小划痕，其他纹理和光照保持稳定。",
    "pdef_tube_bundle_endoscopy": "内窥镜在换热器管束中移动并连续揭示新的内部空间。",
    "pdef_weld_porosity_crack": "已有管道焊缝上形成一处局部气孔缺陷。",
    "vsec_conveyor_jam_loto_clearance": "人员或车辆接近未隔离的工业检修通道前，现场建立明确的物理隔离。",
    "vsec_crane_unsafe_swing_near_people": "起重机已有悬吊载荷转动并过度接近画面中已有人员。",
    "vsec_dangerous_goods_liquid_leak": "危险品装卸区的一处已有连接点泄漏液体，液体沿地面局部扩散。",
    "vsec_electrical_cabinet_smoke_isolation": "工业电气柜的一处连接点冒出局部烟雾，柜体身份保持不变。",
    "vsec_forklift_overspeed_pallet_shift": "叉车快速转弯时，已有托盘货物在惯性作用下向外侧滑动。",
    "vsec_guard_removed_conveyor": "输送机旁的一块已有安全护罩发生局部移位。",
    "vsec_missing_ppe_at_height": "画面中已有高空作业人员缺少安全帽或安全带。",
    "vsec_pedestrian_forklift_near_miss": "画面中已有行人进入叉车通道，叉车制动并在接触前停车。",
    "vsec_perimeter_fence_breach": "工业限制区围栏受局部撞击后发生一处破损。",
    "vsec_smoke_alarm_evacuation": "壁挂式报警控制柜下缘冒出局部薄烟，上方红色警铃闪烁。",
    "vsec_surveillance_blind_spot_sweep": "监控镜头扫过仓库盲区并揭示画面中已有的受限区域进入行为。",
    "vsec_unregistered_vehicle_intrusion": "画面中已有车辆驶入标记清楚的工业限制区域并触发警示。",
}

CAMERA_ZH = {
    "static": "相机保持完全固定。",
    "orbit": "相机以恒定半径绕主体平滑环绕45度。",
    "dolly": "相机保持主体入镜并平滑向前推进。",
    "pan": "相机从左向右平滑巡检平移，不得环绕主体。",
}


def load_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else payload["samples"]


def find_video(task_id: str) -> Path:
    matches = list(VIDEO_ROOT.rglob(f"{task_id}.mp4"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one Hunyuan1.5 video for {task_id}, found {len(matches)}")
    return matches[0]


def prompt_zh(row: dict) -> str:
    scene = SCENE_ZH.get(str(row["scene_id"]))
    if not scene:
        raise KeyError(f"Missing Chinese scene translation: {row['scene_id']}")
    camera = CAMERA_ZH.get(str(row["motion_type"]))
    if not camera:
        raise KeyError(f"Missing Chinese camera translation: {row['motion_type']}")
    return (
        "以原始参考图作为严格首帧，生成一段5秒的写实工业视频。任务："
        + scene + camera
        + "保持画面中已有主体的身份、数量、几何结构、材质、光照、背景和非事件区域不变；只执行明确指定的动作。"
        "不得引入提示词未明确要求的人员、车辆、工具、载荷、文字、标志或其他物体。"
        "不得出现剪切、全局重生成、闪烁、扭曲、消失、穿透、漂浮运动或身份替换。"
    )


def extract_strip(video: Path, output: Path, count: int = 6) -> list[float]:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {video}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS)) or 1.0
    if total < count:
        cap.release()
        raise RuntimeError(f"Too few frames in {video}: {total}")
    frames: list[np.ndarray] = []
    indices = np.linspace(0, total - 1, count).round().astype(int)
    for index in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
        ok, frame = cap.read()
        if not ok:
            cap.release()
            raise RuntimeError(f"Could not decode frame {index} from {video}")
        h, w = frame.shape[:2]
        width = 300
        frames.append(cv2.resize(frame, (width, round(h * width / w)), interpolation=cv2.INTER_AREA))
    cap.release()
    height = min(x.shape[0] for x in frames)
    frames = [x[:height, :] for x in frames]
    strip = cv2.hconcat(frames)
    if not cv2.imwrite(str(output), strip, [cv2.IMWRITE_JPEG_QUALITY, 82]):
        raise RuntimeError(f"Could not write {output}")
    return [round(float(i) / fps, 2) for i in indices]


def build() -> None:
    rows = load_rows(ANNOTATIONS)
    reviewed = {str(x["task_id"]) for x in load_rows(REVIEWED_MANIFEST)}
    remaining = sorted((x for x in rows if str(x["task_id"]) not in reviewed), key=lambda x: (x["domain"], x["task_id"]))
    if len(rows) != 500 or len(reviewed) != 40 or len(remaining) != 460:
        raise RuntimeError((len(rows), len(reviewed), len(remaining)))
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    refs = OUTPUT / "references"
    strips = OUTPUT / "video_strips"
    refs.mkdir(parents=True)
    strips.mkdir()

    manifest: list[dict] = []
    cards: list[str] = []
    for index, row in enumerate(remaining, 1):
        task_id = str(row["task_id"])
        image_matches = [x for x in SOURCE_IMAGES.glob(f"{task_id}.*") if x.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        if len(image_matches) != 1:
            raise RuntimeError(f"Expected one source image for {task_id}, found {image_matches}")
        source_image = image_matches[0]
        ref_dst = refs / f"{task_id}{source_image.suffix.lower()}"
        shutil.copy2(source_image, ref_dst)
        strip_dst = strips / f"{task_id}.jpg"
        video = find_video(task_id)
        timestamps = extract_strip(video, strip_dst)
        zh = prompt_zh(row)
        item = {
            "index": index,
            "task_id": task_id,
            "domain": row["domain"],
            "domain_zh": DOMAIN_ZH[row["domain"]],
            "task_category": row["task_category"],
            "category_zh": CATEGORY_ZH[row["task_category"]],
            "scene_id": row["scene_id"],
            "reference_image": ref_dst.relative_to(OUTPUT).as_posix(),
            "video_strip": strip_dst.relative_to(OUTPUT).as_posix(),
            "video_source": "hunyuan1.5",
            "timestamps_seconds": timestamps,
            "prompt_zh": zh,
            "prompt_en": row["video_generation_prompt"],
        }
        manifest.append(item)
        cards.append(f"""
<article class="card" id="{task_id}" data-task="{task_id}" data-domain="{row['domain']}" data-status="unreviewed">
  <header><span class="num">{index}/460</span><h2>{task_id}</h2><code>{html.escape(str(row['scene_id']))}</code><span class="tag">{DOMAIN_ZH[row['domain']]}</span><span class="tag">{CATEGORY_ZH[row['task_category']]}</span></header>
  <div class="visuals"><figure><figcaption>原始参考图</figcaption><img loading="lazy" src="{item['reference_image']}"></figure><figure class="strip"><figcaption>Hunyuan1.5 视频截图 · {', '.join(map(str, timestamps))} 秒</figcaption><img loading="lazy" src="{item['video_strip']}"></figure></div>
  <section class="prompt zh"><b>中文提示词</b><p>{html.escape(zh)}</p></section>
  <details><summary>查看原始英文 prompt</summary><p class="prompt-en">{html.escape(str(row['video_generation_prompt']))}</p></details>
  <div class="review" role="group" aria-label="审核结论">
    <label><input type="radio" name="status-{task_id}" value="keep"> 保留</label>
    <label><input type="radio" name="status-{task_id}" value="revise"> 需修改</label>
    <label><input type="radio" name="status-{task_id}" value="mismatch"> 严重错配</label>
    <label><input type="radio" name="status-{task_id}" value="unreviewed" checked> 未审核</label>
  </div>
  <textarea rows="2" placeholder="记录具体问题或建议的新提示词……"></textarea>
</article>""")

    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUTPUT / "review_results.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["task_id", "status", "note"])
        writer.writerows((x["task_id"], "", "") for x in manifest)

    page = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FORGE 460条图像—提示词质检</title><style>
:root{color-scheme:light;font-family:Inter,"Microsoft YaHei",sans-serif}*{box-sizing:border-box}body{margin:0;background:#f3f5f7;color:#17202a}.toolbar{position:sticky;top:0;z-index:5;background:#17202a;color:white;padding:12px 18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}.toolbar h1{font-size:18px;margin:0 18px 0 0}.toolbar input,.toolbar select,.toolbar button{font:inherit;padding:8px 10px;border-radius:6px;border:1px solid #768390}.toolbar button{cursor:pointer;background:#2f81f7;color:white;border:0}.progress{font-weight:700}.cards{max-width:1800px;margin:auto}.card{background:white;margin:16px;padding:18px;border-radius:10px;box-shadow:0 1px 5px #0002}.card header{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.card h2{margin:0}.num{font-weight:700;color:#57606a}.tag{background:#eaeef2;padding:4px 8px;border-radius:99px}.visuals{display:grid;grid-template-columns:minmax(260px,32%) 1fr;gap:16px;margin-top:12px}figure{margin:0}figcaption{font-weight:700;margin-bottom:6px}figure img{width:100%;max-height:520px;object-fit:contain;background:#111}.strip img{object-position:left center}.prompt{margin-top:12px;padding:12px;border-left:5px solid #2f81f7;background:#f6f8fa}.prompt p{margin:6px 0;line-height:1.65}.prompt-en{line-height:1.5;color:#424a53}.review{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0}.review label{padding:7px 10px;border-radius:6px;background:#eef1f4}textarea{width:100%;font:inherit;padding:10px}.hidden{display:none}@media(max-width:900px){.visuals{grid-template-columns:1fr}.card{margin:8px;padding:12px}}
</style></head><body><div class="toolbar"><h1>FORGE · 剩余460条质检</h1><input id="search" placeholder="搜索 task / scene"><select id="domain"><option value="">全部领域</option><option value="embodied_robotics">具身机器人</option><option value="extreme_emergency">极端应急</option><option value="heavy_load_construction">重载施工</option><option value="precision_defect_gen">精密缺陷</option><option value="visual_security">视觉安全</option></select><select id="status"><option value="">全部状态</option><option value="unreviewed">未审核</option><option value="keep">保留</option><option value="revise">需修改</option><option value="mismatch">严重错配</option></select><button id="exportJson">导出JSON</button><button id="exportCsv">导出CSV</button><span class="progress" id="progress"></span></div><main class="cards">""" + "\n".join(cards) + """</main><script>
const cards=[...document.querySelectorAll('.card')],key='forge-prompt-audit-460-v1';let state=JSON.parse(localStorage.getItem(key)||'{}');
function save(){localStorage.setItem(key,JSON.stringify(state));update()}
for(const c of cards){const id=c.dataset.task,s=state[id]||{status:'unreviewed',note:''};c.querySelector(`input[value="${s.status}"]`).checked=true;c.querySelector('textarea').value=s.note;c.dataset.status=s.status;c.querySelectorAll('input').forEach(x=>x.onchange=()=>{state[id]={status:x.value,note:c.querySelector('textarea').value};c.dataset.status=x.value;save()});c.querySelector('textarea').oninput=e=>{state[id]={status:c.querySelector('input:checked').value,note:e.target.value};save()}}
function update(){const q=document.querySelector('#search').value.toLowerCase(),d=document.querySelector('#domain').value,s=document.querySelector('#status').value;let shown=0,done=0;for(const c of cards){const hit=(!q||c.dataset.task.includes(q)||c.querySelector('code').textContent.toLowerCase().includes(q))&&(!d||c.dataset.domain===d)&&(!s||c.dataset.status===s);c.classList.toggle('hidden',!hit);shown+=hit;done+=c.dataset.status!=='unreviewed'}document.querySelector('#progress').textContent=`已审核 ${done}/460 · 当前显示 ${shown}`}
document.querySelectorAll('#search,#domain,#status').forEach(x=>x.addEventListener(x.tagName==='INPUT'?'input':'change',update));
function rows(){return cards.map(c=>({task_id:c.dataset.task,status:c.dataset.status,note:c.querySelector('textarea').value}))}function download(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();URL.revokeObjectURL(a.href)}
document.querySelector('#exportJson').onclick=()=>download('prompt_review_460.json',JSON.stringify(rows(),null,2),'application/json');document.querySelector('#exportCsv').onclick=()=>{const esc=x=>'"'+String(x).replaceAll('"','""')+'"';download('prompt_review_460.csv','\ufefftask_id,status,note\n'+rows().map(r=>[r.task_id,r.status,r.note].map(esc).join(',')).join('\n'),'text/csv')};update();
</script></body></html>"""
    (OUTPUT / "review.html").write_text(page, encoding="utf-8")
    (OUTPUT / "README_中文.md").write_text(
        "# FORGE 460条图像—提示词质检\n\n双击 `review.html`。审核选择和备注自动保存在当前浏览器；完成或中途备份时点击导出JSON或导出CSV。\n",
        encoding="utf-8",
    )
    print(json.dumps({"tasks": len(manifest), "source_model": "hunyuan1.5", "frames_per_video": 6}, ensure_ascii=False))
    print(OUTPUT)


if __name__ == "__main__":
    build()
