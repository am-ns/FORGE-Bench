#!/usr/bin/env python3
"""Build a self-contained HTML Feishu-style document from feishu_scene_reference_report.md.

Reads the markdown table, completes truncated prompts, embeds reference images
as base64, and writes reports/feishu_scene_report.html.
"""

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_MD = ROOT / "reports" / "feishu_scene_reference_report.md"
OUT_HTML = ROOT / "reports" / "feishu_scene_report.html"
IMAGES_DIR = ROOT / "dataset" / "images"
VIDEO_DIR = ROOT / "reports" / "feishu_videos"

# Scenes to exclude entirely from the report
SKIP_SCENES = {
    "hload_tunnel_pipe_burst_mud_surge",    # 图是盾构机，不是泥水涌出
    "pdef_cutting_fluid_spray",             # 价值低
    "vsec_pedestrian_forklift_near_miss",   # 与叉车超速场景重复
    "emerg_dam_or_retaining_wall_breach",   # 价值低
    "vsec_unregistered_vehicle_intrusion",  # 图文不匹配：图是门禁/车辆，文案改成了叉车侧倾
    "emerg_cooling_tower_plume_failure",    # 图文不匹配：图是冷却塔，文案改成了电弧炉溅射
    "erob_cobot_human_handover",            # 牵强：机器人减速是控制系统行为，视频里无法客观评测"减速是否正确"
    "vsec_smoke_alarm_evacuation",          # 牵强：去掉疏散后只剩"烟雾上升+灯闪"，这是通用场景而非工业专属约束
}

# ---------------------------------------------------------------------------
# Chinese task summaries (1-2 sentences)
# ---------------------------------------------------------------------------
ZH_SUMMARY = {
    # Visual Security
    "vsec_unregistered_vehicle_intrusion":
        "测试模型能否生成未报备车辆穿越门禁道闸进入限制区的完整违规链路，评估违规触发、报警响应与车辆轨迹的因果一致性。",
    "vsec_missing_ppe_at_height":
        "评估模型对高空作业缺失防护装备场景的生成能力，重点考察人员身份稳定性及合规违规后果的逻辑连贯性。",
    "vsec_forklift_overspeed_pallet_shift":
        "要求模型生成叉车超速转弯导致货物向外侧滑的物理过程，考察刚体惯性、接触力学与货物姿态变化的真实性。",
    "vsec_crane_unsafe_swing_near_people":
        "测试模型能否正确模拟吊装载荷摆动接近人员的危险场景，评估吊索路径、摆动动力学与紧急停止响应的逻辑闭环。",
    "vsec_surveillance_blind_spot_sweep":
        "考察模型对 PTZ 摄像头平移扫视盲区的视角运动生成质量，要求目标出现时机与摄像头扫视轨迹严格对应。",
    "vsec_perimeter_fence_breach":
        "测试模型能否在保持围栏整体拓扑不变的前提下，生成局部受撞击后形成缺口的真实形变过程。",
    "vsec_dangerous_goods_liquid_leak":
        "评估模型对危化品液体在装卸区地面扩散过程的流体动力学生成能力，考察重力方向、扩散路径与危险边界的物理合理性。",
    "vsec_pedestrian_forklift_near_miss":
        "要求模型生成行人误入叉车通道后触发制动的近失事故全过程，考察制动因果链与安全距离的时序逻辑。",
    "vsec_smoke_alarm_evacuation":
        "测试模型生成工业烟雾报警到人员疏散完整因果链的能力，重点评估烟雾演化、报警触发与疏散行为的时间连续性。",
    "vsec_guard_removed_conveyor":
        "评估模型在设备拓扑基本不变的条件下，生成传送带防护罩缺失并暴露危险部位的场景，考察合规判断逻辑。",
    # Embodied Robotics
    "erob_robot_arm_precision_grasp":
        "测试模型对多轴机械臂精密抓取过程的运动学建模能力，评估关节耦合、末端轨迹与工具-工件接触关系的几何一致性。",
    "erob_cobot_human_handover":
        "评估模型能否正确生成协作机器人减速-交接-恢复的完整安全交互序列，考察人机距离感知与合规逻辑。",
    "erob_tracked_robot_rubble":
        "测试模型对履带机器人在不规则地形上越障过程的动力学仿真质量，重点考察履带-地面接触变形与姿态稳定性。",
    "erob_quadruped_stairs_rubble_fpv":
        "要求模型从机器人第一视角生成四足机器人通过楼梯或废墟的连续运动，评估视角运动流畅性与足端接触合理性。",
    "erob_amr_warehouse_navigation":
        "测试模型对 AMR 在仓库货架间自主导航的路径规划与避障行为的生成质量，考察底盘运动的物理连续性。",
    "erob_light_curtain_emergency_stop":
        "评估模型能否正确生成光幕触发到机器人立即停机的完整因果链，重点考察触发-制动-锁定的时序逻辑。",
    "erob_robot_tool_contact_force":
        "测试模型对机器人末端工具施加接触力进行打磨或焊接的过程建模，评估力的方向、工具不穿透约束与表面稳定性。",
    "erob_multi_robot_coordination":
        "评估模型在多机器人共享空间中生成协同避碰的能力，重点考察机器人身份保持与路径时序的逻辑一致性。",
    "erob_gripper_failure_recovery":
        "测试模型对夹爪局部失效导致工件姿态偏移及后续恢复抓取全过程的建模能力，评估故障检测与恢复逻辑。",
    # Heavy Load Construction
    "hload_dual_crawler_crane_lift":
        "测试模型对双履带吊协同吊装的运动学同步性建模，评估吊索角度、载荷平衡与两台起重机运动的物理一致性。",
    "hload_wire_rope_overload_snap":
        "评估模型能否生成钢丝绳局部过载断裂的渐进失效过程，考察断裂拓扑变化与未受损区域保持不变的约束。",
    "hload_mining_truck_muddy_slope":
        "测试模型对矿用重载卡车在泥泞坡道爬坡时轮胎沉陷与牵引力的动力学建模能力。",
    "hload_gantry_wind_disturbance":
        "评估模型对龙门吊在强风作用下结构扰动与悬挂载荷摆动的动力学仿真质量，考察结构弹性响应的物理合理性。",
    "hload_bridge_segment_alignment_drone":
        "测试模型生成无人机绕桥梁节段轨道飞行并保持几何一致的视角运动，评估尺度稳定性与多角度几何保持。",
    "hload_excavator_linkage_loading":
        "评估模型对挖掘机动臂-斗杆-铲斗三连杆液压耦合运动的建模精度，考察关节中心固定与土方接触的物理合理性。",
    "hload_ground_settlement_outrigger":
        "测试模型能否生成吊车支腿在软土中渐进沉陷并导致机体倾斜的因果过程，评估支撑状态变化与重心漂移的一致性。",
    "hload_tunnel_pipe_burst_mud_surge":
        "评估模型对施工破坏地下管线后泥水向上喷涌并在基坑扩散的流体动力学建模，考察压力方向与流体边界约束。",
    "hload_hoist_collision_near_structure":
        "测试模型能否生成吊物靠近结构物触发报警并在接触前完成制动的安全响应场景，评估摆动衰减与载荷稳定性。",
    "hload_formwork_collapse_local":
        "评估模型对脚手架/模板局部支撑失效后渐进坍塌过程的拓扑建模，重点考察失效传播路径与邻近结构的稳定性。",
    # Precision Defect Gen
    "pdef_pcb_solder_bridge_short":
        "测试模型在不改变周围元件和走线的前提下，精确生成 PCB 相邻焊盘桥连短路缺陷的局部变化能力。",
    "pdef_engine_endoscope_crack":
        "评估模型从内窥镜视角生成叶片或管壁微裂纹检测画面的质量，考察圆形视野、内腔几何与裂纹定位的稳定性。",
    "pdef_gear_tooth_missing_wear":
        "测试模型在保持齿轮周期结构不变的前提下，生成局部缺齿或严重磨损缺陷的精度，评估齿数计数一致性。",
    "pdef_cnc_curved_surface_cutting":
        "评估模型对五轴 CNC 多轴联动切削曲面的运动学建模能力，考察主轴姿态、刀具路径与工件接触的几何一致性。",
    "pdef_cutting_fluid_spray":
        "测试模型生成高速切削液喷溅与切屑飞散的流体动力学过程，评估液滴轨迹方向与刀具旋转方向的物理一致性。",
    "pdef_weld_porosity_crack":
        "评估模型在不改变整体焊缝形态的前提下，精确生成局部气孔或裂纹缺陷，考察缺陷形态的局域性约束。",
    "pdef_surface_scratch_inspection":
        "测试模型在特定方向光照下生成抛光表面局部划痕的反光特征，评估细节保持与周围光洁表面不变的约束。",
    "pdef_tube_bundle_endoscopy":
        "评估模型生成内窥镜穿越换热管束端面的视角运动，考察重复圆管阵列的计数一致性与视角连续性。",
    "pdef_connector_pin_bent":
        "测试模型在保持其余针脚对齐不变的前提下，精确生成密集连接器单根针脚弯曲或桥接的局部缺陷。",
    "pdef_precision_assembly_misalignment":
        "评估模型展示精密装配微小错位的能力，要求错位量小但可见，且零件身份在相机绕轨过程中保持稳定。",
    # Extreme Emergency
    "emerg_flange_high_pressure_leak":
        "测试模型生成法兰密封失效后高压气液喷射的流体动力学过程，评估喷射方向、热扭曲形态与管道结构稳定性。",
    "emerg_storage_tank_flash_fire":
        "评估模型对储罐区闪燃沿管线蔓延过程的热力学建模，考察火焰传播路径与边界条件的物理合理性。",
    "emerg_transmission_tower_icing_collapse":
        "测试模型对覆冰输电铁塔在重力与冰荷载下渐进屈曲坍塌的拓扑建模，评估桁架失效传播与重力方向的一致性。",
    "emerg_dust_explosion_confined_space":
        "评估模型对受限空间粉尘爆炸爆燃过程与应急响应链的生成能力，考察压力波形态与人员疏散时序逻辑。",
    "emerg_reactor_runaway_pressure_release":
        "测试模型能否生成反应釜压力升高、安全阀开启到泄放喷射的完整因果过程，评估压力状态演化的逻辑闭环。",
    "emerg_battery_thermal_runaway":
        "评估模型对电池热失控从单一模块向邻近模块扩散并触发抑制响应的热扩散建模，考察局域故障的空间约束。",
    "emerg_tunnel_fire_smoke_layering":
        "测试模型生成隧道火灾烟气分层结构的热流体动力学过程，评估上层烟气与下层可视区的稳定分层约束。",
    "emerg_crane_load_drop_evacuation":
        "评估模型能否生成吊载失稳坠落并触发人员成功撤离的完整应急响应链，考察载荷动力学与疏散行为的因果时序。",
    "emerg_cooling_tower_plume_failure":
        "测试模型对冷却塔风机故障导致羽流形态改变的热湿动力学建模，评估羽流方向与热梯度变化的物理一致性。",
    "emerg_dam_or_retaining_wall_breach":
        "评估模型生成挡墙/尾矿坝局部溃口渐进扩展与水/浆体外泄过程的流体-结构耦合建模能力。",
}

# ---------------------------------------------------------------------------
# Full prompts keyed by scene_id
# ---------------------------------------------------------------------------
FULL_PROMPTS = {
    "vsec_unregistered_vehicle_intrusion": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An unregistered third-party truck enters a marked restricted industrial zone through a controlled entrance; the barrier or gate boundary is clearly shown, a detection alert activates, and a security response begins.",
    "vsec_missing_ppe_at_height": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A construction worker performs high-altitude tasks on scaffolding or an elevated work platform without a safety helmet or harness; the missing PPE is visually conspicuous, and a compliance violation response or supervisor escalation follows.",
    "vsec_forklift_overspeed_pallet_shift": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A forklift takes a sharp corner in a warehouse aisle at excessive speed; the loaded pallet shifts laterally under centrifugal force, with cargo visibly sliding or tipping outward.",
    "vsec_crane_unsafe_swing_near_people": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An overhead bridge crane slews while carrying a suspended load; the load swings outward under the slewing motion, the cable angle deviates visibly from vertical, and an anti-collision or proximity alarm activates automatically.",
    "vsec_surveillance_blind_spot_sweep": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A ceiling-mounted PTZ surveillance camera performs a slow pan across a large warehouse or factory blind spot; as the camera sweeps, a person or vehicle that was previously hidden comes into view in the restricted area.",
    "vsec_perimeter_fence_breach": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An industrial restricted-zone perimeter wire fence is damaged by external impact; a localized section buckles or opens, creating a visible gap while the rest of the fence remains intact.",
    "vsec_dangerous_goods_liquid_leak": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An unknown chemical liquid leaks from a container or pipe fitting in a dangerous-goods loading zone and spreads across the floor, following gravity and ground slope toward the containment boundary.",
    "vsec_pedestrian_forklift_near_miss": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A pedestrian accidentally steps into an active forklift or AGV traffic lane; the vehicle detects the intrusion, applies emergency braking, and stops just short of the pedestrian while an alarm sounds.",
    "vsec_smoke_alarm_evacuation": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Smoke begins rising from an electrical cabinet or industrial machine; it thickens and spreads upward under buoyancy, the smoke detector overhead triggers, and strobe alarm lights activate automatically.",
    "vsec_guard_removed_conveyor": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A production conveyor or rotating machine is shown operating with its safety guard cover missing or displaced, exposing the moving nip point or drive mechanism as a visible hazard.",
    "erob_robot_arm_precision_grasp": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A multi-axis industrial robot arm extends toward a precision workpiece, closes its end-effector with stable contact, and lifts the part while maintaining kinematic coupling across all joints.",
    "erob_cobot_human_handover": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A collaborative robot (cobot) decelerates as a human worker's hand enters the shared workspace, completes a safe part handover at reduced speed, and confirms the transfer before returning to home.",
    "erob_tracked_robot_rubble": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A tracked ground robot drives over broken concrete rubble or pipe obstacles, its tracks conforming to uneven terrain while the chassis maintains attitude stability.",
    "erob_quadruped_stairs_rubble_fpv": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. From a first-person head-mounted camera on a quadruped robot, the view moves through stairs, rubble, or an industrial facility, with visible foot contacts and smooth body motion.",
    "erob_amr_warehouse_navigation": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An autonomous mobile robot navigates between storage racks and pallets in a warehouse, smoothly decelerating around a parked obstacle and continuing its route to the destination.",
    "erob_light_curtain_emergency_stop": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A worker's hand or body crosses the safety light curtain at a robot cell boundary; the robot arm immediately halts mid-motion, all status indicators switch to red, and the cell locks out.",
    "erob_robot_tool_contact_force": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An industrial robot applies a grinding wheel or welding torch to a metal workpiece surface with controlled contact force; sparks or weld pool scatter in the physically correct direction and the tool maintains surface contact without penetrating.",
    "erob_multi_robot_coordination": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Two mobile robots or robot arms operate in a shared workspace and perform coordinated path adjustments to avoid collision, each maintaining its own identity and completing its assigned task.",
    "erob_gripper_failure_recovery": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. One suction cup or jaw of a robot gripper partially loses grip, causing the workpiece to tilt or shift; the robot detects the error, pauses, re-grasps, and successfully restabilizes the part.",
    "hload_dual_crawler_crane_lift": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Two crawler cranes perform a tandem lift of a heavy steel module, with synchronized boom angles and balanced load sharing; the module clears the ground and rises steadily as both cranes track the same vertical rate.",
    "hload_wire_rope_overload_snap": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A crane wire rope or lifting sling is subjected to progressive overload; individual wire strands deform and begin to snap at a localized failure zone while the rope above and below remains intact.",
    "hload_mining_truck_muddy_slope": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A heavy mining haul truck climbs a steep muddy ramp; tires sink visibly into soft earth with each rotation, mud is thrown backward, and the drivetrain strains to maintain upward progress.",
    "hload_gantry_wind_disturbance": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A tall gantry or ship-to-shore crane sways slightly under strong wind loading; the suspended load swings as a pendulum, the hoist rope angle shifts with each gust, and the structure returns toward plumb during lulls.",
    "hload_bridge_segment_alignment_drone": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A drone orbits a precast bridge segment at a construction site, maintaining constant standoff distance; the camera reveals the surface texture, alignment marks, and cross-section profile from multiple angles.",
    "hload_excavator_linkage_loading": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An excavator performs a loaded dig-and-swing cycle; boom rises, arm curls, bucket closes around earth, then the machine swings to deposit the load—all three links moving in coupled hydraulic articulation.",
    "hload_ground_settlement_outrigger": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A mobile crane outrigger pad progressively sinks into soft soil, causing the crane body to tilt; cracks appear in the ground around the sinking pad and the operator initiates an emergency stop.",
    "hload_tunnel_pipe_burst_mud_surge": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Excavation work ruptures an underground water main; muddy water surges upward through the open trench, spreading laterally along the trench floor and over the excavated edge.",
    "hload_hoist_collision_near_structure": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A crane's suspended load swings toward a scaffolding frame or steel structure; a proximity alarm triggers, the hoist brake engages, and the load decelerates to rest just short of contact.",
    "hload_formwork_collapse_local": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A section of temporary formwork or scaffolding support fails at a local joint, causing a progressive partial collapse; the failing section folds downward while adjacent bays remain standing.",
    "pdef_pcb_solder_bridge_short": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Under magnified inspection lighting, a solder bridge gradually forms between two adjacent fine-pitch PCB pads; surrounding traces and components remain unchanged while the bridged zone clearly shows the short.",
    "pdef_engine_endoscope_crack": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A borescope advances slowly through a turbine engine or pipe interior; the camera centers on a blade or wall surface where a hairline crack is visible, with surrounding metal remaining stable.",
    "pdef_gear_tooth_missing_wear": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. The gear rotates slowly under inspection lighting; a chipped or missing tooth passes the camera, its broken profile contrasting sharply with the uniform intact teeth on either side.",
    "pdef_cnc_curved_surface_cutting": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A 5-axis CNC machining center sweeps the cutting tool across a complex curved workpiece surface; all five axes move simultaneously, the tool remains tangent to the surface, and coolant mist sprays at the contact zone.",
    "pdef_cutting_fluid_spray": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A high-speed CNC cutter contacts a metal workpiece; coolant streams arc outward in the correct centrifugal direction while metal chips scatter in the cutting plane, both behaviors consistent with tool rotation.",
    "pdef_weld_porosity_crack": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. The camera tracks along a completed weld seam at close range; a porosity void appears in the bead, and a hairline crack extends from it, while the surrounding weld and base metal remain undisturbed.",
    "pdef_surface_scratch_inspection": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Under raking inspection light, fine scratches appear on a polished metal, wafer, or bearing surface; the scratches reflect differently from the mirror finish while the surrounding area maintains its uniform sheen.",
    "pdef_tube_bundle_endoscopy": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A borescope enters a heat exchanger tube bundle end-face; the circular tube openings scroll past as the probe advances, and the camera briefly dwells in one tube revealing scale deposits on the interior wall.",
    "pdef_connector_pin_bent": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A macro view reveals a high-density connector pin array; one pin is bent toward its neighbor, forming a bridge contact, while all adjacent pins maintain their parallel alignment.",
    "pdef_precision_assembly_misalignment": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. The camera circles a precision assembly (bearing on shaft, coupling, or fixture) at close range; a slight angular offset between mating faces becomes apparent from a specific viewpoint while both components retain their identity.",
    "emerg_flange_high_pressure_leak": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A high-pressure pipeline flange joint develops a leak; gas or liquid jets from the gap, creating a visible plume with heat shimmer or condensation, while the flange faces and bolts remain structurally visible.",
    "emerg_storage_tank_flash_fire": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A flash fire ignites at the base of a storage tank or pipeline and propagates along the fuel path to adjacent equipment; the flame front moves at ground level and secondary ignition occurs at the next bund or tank.",
    "emerg_transmission_tower_icing_collapse": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Ice-laden conductors pull the tower's crossarm progressively downward; a lattice member buckles at a diagonal, and the structure folds inward toward the ground under gravitational collapse.",
    "emerg_dust_explosion_confined_space": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An ignition source ignites a suspended dust cloud inside a grain silo or industrial facility; a deflagration expands outward with a pressure wave venting through relief panels, warping them outward.",
    "emerg_reactor_runaway_pressure_release": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. Reactor pressure climbs into the red zone on a visible gauge; the relief valve pops open and a jet of steam or process gas vents upward through the discharge pipe while the pressure indicator drops after relief.",
    "emerg_battery_thermal_runaway": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. One battery module in a rack enters thermal runaway, producing smoke and venting gas; heat and smoke spread to adjacent modules while the cabinet fire suppression system activates overhead.",
    "emerg_tunnel_fire_smoke_layering": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A fire inside a tunnel generates a stratified hot smoke layer that accumulates near the ceiling; ventilation drives the layer toward the portal while the lower zone remains relatively clear.",
    "emerg_crane_load_drop_evacuation": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A crane hoist rope suddenly loses tension and the load drops in free fall; the rope goes slack, the hook descends rapidly, and the load impacts the ground with a visible deformation or scatter of material.",
    "emerg_cooling_tower_plume_failure": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A cooling tower's vapor plume changes abruptly due to fan failure or reduced water flow; the plume collapses, shifts direction with ambient wind, or becomes denser, all consistent with the thermal gradient change.",
    "emerg_dam_or_retaining_wall_breach": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A local breach forms in an industrial containment wall or tailings dam; water or slurry escapes through the opening with plausible erosion widening the gap progressively while the remaining wall structure stays intact.",
}

# ---------------------------------------------------------------------------
# Scene concept overrides: reframe weak scenes toward real industrial value
# Keys must match scene_id from the markdown table
# Each entry overrides: display title (zh/en), zh_summary, and full_prompt
# ---------------------------------------------------------------------------
SCENE_CONCEPT_OVERRIDES = {
    "vsec_unregistered_vehicle_intrusion": {
        "title_zh": "叉车超载侧倾预警联动",
        "title_en": "Forklift Overload Tipping Warning",
        "zh_summary": "一台叉车在仓库通道内以偏高速度转弯，因超载导致重心偏移，一侧驱动轮离地出现侧倾预兆，安全系统触发声光报警并锁止行驶。测评重点：刚体倾覆力矩的物理合理性、倾斜角与载荷的对应关系、报警触发时机的因果逻辑。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A forklift carrying an overloaded pallet takes a corner in a warehouse aisle; the excess load shifts the center of gravity so that one drive wheel lifts clear of the floor, the mast tilts visibly outward, and the onboard overload alarm activates with strobes and a buzzer.",
    },
    "vsec_surveillance_blind_spot_sweep": {
        "title_zh": "热成像摄像头扫描设备过热异常",
        "title_en": "Thermal Camera Scan Detects Equipment Overheating",
        "zh_summary": "厂房内红外热成像摄像头在夜间缓慢平移扫描设备区，发现某台电气柜或电机存在局部温度异常（热点），触发温度报警系统。测评重点：热成像色温梯度的视觉合理性、异常热点的空间定位稳定性、摄像头运动与目标显现的时序逻辑。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A pan-tilt thermal camera slowly sweeps across an industrial equipment bay at night; as the field of view crosses a specific electrical cabinet or motor, a localised hot spot appears in high-temperature colour (orange/white) against the cooler background, and a temperature-threshold alarm triggers on the monitoring overlay.",
    },
    "hload_bridge_segment_alignment_drone": {
        "title_zh": "预制箱梁精确落梁对位",
        "title_en": "Precast Box Girder Precision Lowering and Alignment",
        "zh_summary": "起重机缓慢下降一段预制混凝土箱梁，使其逐渐与桥墩支座上的对位标记贴合，施工人员在旁指挥微调，最终完成毫米级精度的落梁就位。测评重点：大型构件在下降过程中的几何姿态保持、支座接触前后的位移连续性、多人协作指挥下的因果响应链。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A precast concrete box girder descends slowly by crane toward the bridge pier bearing pads; alignment marks on the girder soffit and the bearing centerlines converge as the element lowers, until the bearing surfaces make contact precisely at the target position.",
    },
    "erob_amr_warehouse_navigation": {
        "title_zh": "货架局部倒塌触发AMR紧急规避",
        "title_en": "AMR Emergency Avoidance After Partial Shelf Collapse",
        "zh_summary": "仓库内一列货架因局部超载发生倒塌，正在附近执行任务的AMR实时感知障碍物并进行路径重规划，绕行至安全区域后停止并上报异常。测评重点：突发障碍触发-感知-重规划的因果时序、AMR底盘运动学的物理合理性、障碍物倒塌过程的拓扑变化。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. An AMR is navigating a warehouse aisle when a nearby shelf section collapses under overload, spilling boxes into the aisle; the AMR immediately decelerates, stops short of the debris, and reroutes around the obstruction to reach a safe holding position.",
    },
    "hload_ground_settlement_outrigger": {
        "title_zh": "起重机吊装超载自动限制器触发停机",
        "title_en": "Crane Load Limiter Automatic Stop on Overload",
        "zh_summary": "移动式起重机在吊装作业中载荷逐渐超过额定值，力矩限制器检测到超载后自动切断起升动作并发出报警，操作员须确认卸载后才能恢复。测评重点：载荷力矩的渐进变化、限制器触发与动作切断的因果时序、操作响应的合规逻辑。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. A mobile crane hoists a load that is slightly above its rated capacity for the current boom angle; as the hoist continues, the load moment indicator climbs into the red zone, the automatic safe-load indicator cuts the hoist motion, alarm lights and horn activate, and the hoist motion cuts out completely with the load held suspended at that height.",
    },
    "emerg_cooling_tower_plume_failure": {
        "title_zh": "电弧炉出钢口钢水溅射与热辐射",
        "title_en": "Electric Arc Furnace Taphole Steel Splash and Thermal Radiation",
        "zh_summary": "炼钢电弧炉在出钢过程中，出钢口发生钢水溅射，高温液态钢水沿抛物线轨迹飞散，产生强烈热辐射光晕，操作人员迅速后退至安全距离。测评重点：高温液体的飞溅轨迹物理合理性、热辐射光晕的视觉扩散、人员安全距离响应的因果链。",
        "full_prompt": "Use the provided reference image as the first frame. Generate a 5-8 second realistic industrial video. During electric arc furnace tapping, molten steel splashes from the taphole; incandescent droplets follow parabolic trajectories outward from the pour stream, and a bright thermal halo blooms and pulses around the splash zone.",
    },
}

# ---------------------------------------------------------------------------
# Image overrides: scene_id -> path relative to IMAGES_DIR parent (ROOT)
# Used to replace problematic images without editing the source markdown
# ---------------------------------------------------------------------------
IMAGE_OVERRIDES = {
    # excavator: ref_01 is B&W, use the generic colour stock excavator image
    "hload_excavator_linkage_loading":
        "dataset/images/heavy_load_construction/construction__excavator.jpg",

    # crane load drop: use tower crane luffing jib from same domain
    "emerg_crane_load_drop_evacuation":
        "dataset/images/extreme_emergency/construction__tower_crane_luffing_jib.jpg",
    # multi-robot: welding cell typically has multiple robot arms
    "erob_multi_robot_coordination":
        "dataset/images/embodied_robotics/manufacturing__robotic_welding_cell.jpg",
    # bridge drone: use strict_1 which should show the segment more clearly
    "hload_bridge_segment_alignment_drone":
        "dataset/images/heavy_load_construction/hload_bridge_segment_alignment_drone/strict_1.jpg",
    # --- still needs manual image from user ---
    # "vsec_unregistered_vehicle_intrusion": gate + vehicle photo
}

# ---------------------------------------------------------------------------
# Parse markdown table
# ---------------------------------------------------------------------------
def parse_md_table(md_path: Path) -> list[dict]:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines:
        if not line.startswith("|") or line.startswith("| 大类") or line.startswith("|---"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 6:
            continue
        scene_id = cols[2].strip("`")
        rows.append({
            "domain": cols[0],
            "task_category": cols[1],
            "scene_id": scene_id,
            "title_zh": cols[3],
            "image_path": cols[4].strip("`"),
            "prompt_truncated": cols[5],
        })
    return rows

# ---------------------------------------------------------------------------
# Find the actual image file for a scene
# ---------------------------------------------------------------------------
def find_image(image_path_str: str, scene_id: str = "") -> Path | None:
    # Check override table first
    if scene_id and scene_id in IMAGE_OVERRIDES:
        override = ROOT / IMAGE_OVERRIDES[scene_id]
        if override.exists():
            return override
    # Try the exact path first
    p = ROOT / image_path_str
    if p.exists():
        return p
    # Try to find any __ref file for this scene
    stem = Path(image_path_str).stem  # e.g. vsec_unregistered_vehicle_intrusion__ref_01
    domain_dir = ROOT / Path(image_path_str).parent
    if domain_dir.exists():
        # Try exact
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = domain_dir / (stem + ext)
            if candidate.exists():
                return candidate
        # Fall back to first __ref file for the scene_id prefix
        scene_prefix = stem.split("__")[0]
        for f in sorted(domain_dir.iterdir()):
            if f.stem.startswith(scene_prefix) and "__ref" in f.stem:
                return f
    return None

def img_to_b64(path: Path) -> str:
    data = path.read_bytes()
    ext = path.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{base64.b64encode(data).decode()}"

def find_video(scene_id: str) -> Path | None:
    for ext in (".mp4", ".webm", ".mov", ".mkv"):
        candidate = VIDEO_DIR / f"{scene_id}{ext}"
        if candidate.exists():
            return candidate
    return None

def video_tag(scene_id: str) -> str:
    video_path = find_video(scene_id)
    if not video_path:
        return ""
    rel = video_path.relative_to(OUT_HTML.parent).as_posix()
    return f"""
          <div class="video-box">
            <div class="video-label">Generated Video</div>
            <video controls preload="metadata" src="{rel}"></video>
            <div class="video-caption">{video_path.name}</div>
          </div>"""

# ---------------------------------------------------------------------------
# Build HTML
# ---------------------------------------------------------------------------
DOMAIN_COLORS = {
    "visual_security": "#1a73e8",
    "embodied_robotics": "#0f9d58",
    "heavy_load_construction": "#f4b400",
    "precision_defect_gen": "#ab47bc",
    "extreme_emergency": "#e53935",
}
DOMAIN_LABELS = {
    "visual_security": "Visual Security 视觉安防",
    "embodied_robotics": "Embodied Robotics 具身机器人",
    "heavy_load_construction": "Heavy Load Construction 重型载荷",
    "precision_defect_gen": "Precision Defect Gen 精密制造",
    "extreme_emergency": "Extreme Emergency 极端工况",
}

ARCHITECTURE_HTML = """
  <section class="overview-card">
    <h2>项目架构总览</h2>
    <p class="overview-lead">FORGE-Bench 当前按“场景域 -> 抽象任务 -> 参考图 -> 可执行视频 Prompt -> 任务专属评分权重 -> 领域/任务维度报告”的链路组织，用来评测工业视频生成模型是否真正理解工业结构、物理过程和安全逻辑，而不是只生成表面合理的画面。</p>
    <div class="flow-row">
      <span>场景域</span><b>-></b><span>抽象任务</span><b>-></b><span>参考图</span><b>-></b><span>生成 Prompt</span><b>-></b><span>轴权重</span><b>-></b><span>报告</span>
    </div>
    <table class="compact-table">
      <thead><tr><th>层级</th><th>当前设计</th><th>作用</th></tr></thead>
      <tbody>
        <tr><td>五个场景域</td><td>visual_security, embodied_robotics, heavy_load_construction, precision_defect_gen, extreme_emergency</td><td>覆盖安防合规、机器人、重载施工、精密缺陷、极端事故五类工业能力边界。</td></tr>
        <tr><td>五类抽象任务</td><td>刚体运动、拓扑失效、流体热力、空间视角、工业逻辑合规</td><td>决定样本的主要难点、最高权重评分轴和报告分组。</td></tr>
        <tr><td>参考图与 Prompt</td><td>每个样本绑定参考图、短生成 Prompt、完整评测 Prompt</td><td>参考图提供首帧和几何锚点，Prompt 明确动作、物理、逻辑、视角和约束。</td></tr>
        <tr><td>评分流水线</td><td>几何/工业约束算子 + 视角运动门控 + 多轴模型裁判 + per-sample 加权 + aggregate 汇总</td><td>输出 relax_score、strict_pass_rate、gated_score、domain_breakdown、task_breakdown 和低保真摘要。</td></tr>
      </tbody>
    </table>
  </section>

  <section class="overview-card">
    <h2>统一评分轴</h2>
    <table class="compact-table">
      <thead><tr><th>评分轴</th><th>评什么</th><th>典型扣分点</th></tr></thead>
      <tbody>
        <tr><td>industrial_logic_and_fact_alignment</td><td>工业因果、设备状态、告警、停机、疏散、合规后果是否闭环。</td><td>违规发生但无响应；急停触发后设备继续运动；人员/设备角色无因果切换。</td></tr>
        <tr><td>geometric_integrity</td><td>拓扑、刚体结构、关节中心、重复结构、局部缺陷边界是否稳定。</td><td>关节漂移；管线/电路/钢丝绳错误融合；齿轮、管束、针脚数量变化。</td></tr>
        <tr><td>physical_plausibility</td><td>重力、接触、载荷、压力、流动、热扩散、火焰和应急动力学是否合理。</td><td>吊载漂浮；泄漏逆压力方向扩散；机器人或刀具穿透实体。</td></tr>
        <tr><td>temporal_consistency</td><td>对象身份、材质、背景、状态和事件链在全视频中是否连续。</td><td>零件闪烁；材料融化变形；设备型号或缺陷位置中途变掉。</td></tr>
        <tr><td>reference_and_motion_fidelity</td><td>是否保留参考图主体、布局和非变化区域，并执行指定视角运动。</td><td>移动镜头任务提交静态视频；局部缺陷导致全局背景重绘；参考透视漂移。</td></tr>
      </tbody>
    </table>
    <p class="note-text">补充规则：viewpoint_motion_fidelity 作为运动门控并入 reference_and_motion_fidelity；industrial_constraint_score 作为硬约束成分并入 geometric_integrity。单样本得分按任务权重加权，空间视角任务还会被静态视频门控拉低。</p>
  </section>

  <section class="overview-card">
    <h2>每类 Task 评分标准</h2>
    <table class="rubric-table">
      <thead><tr><th>Task 类别</th><th>最高权重/门控</th><th>轴权重</th><th>合格标准</th></tr></thead>
      <tbody>
        <tr>
          <td><b>rigid_body_kinematics_and_coupling</b><br>刚体运动与多轴耦合</td>
          <td>geometric_integrity</td>
          <td>逻辑 1.10 / 几何 1.70 / 物理 1.45 / 时序 1.25 / 参考运动 0.85</td>
          <td>连杆、关节、轴线、支撑点、吊索/载荷路径保持刚性一致；运动符合可达姿态、载荷方向和接触约束；同一机构在全视频中不软化、不穿模、不换身份。</td>
        </tr>
        <tr>
          <td><b>topology_mutation_and_failure</b><br>拓扑突变与局部失效</td>
          <td>geometric_integrity</td>
          <td>逻辑 1.10 / 几何 1.80 / 物理 1.05 / 时序 1.25 / 参考运动 1.35</td>
          <td>短路、裂纹、断绳、缺齿、破损护栏等变化必须局部、精确、可持续；未变化区域的边界、数量和背景锁定参考图；不能用全局重绘代替局部缺陷演化。</td>
        </tr>
        <tr>
          <td><b>fluid_dynamics_and_thermodynamics</b><br>流体动力学与热力学</td>
          <td>physical_plausibility</td>
          <td>逻辑 1.25 / 几何 1.05 / 物理 1.85 / 时序 1.30 / 参考运动 0.95</td>
          <td>泄漏、喷射、泥水、烟、火、热失控必须符合压力方向、重力、扩散、边界和热传播；流体/火焰/烟雾连续演化，不瞬移、不重置；事故状态与工业原因一致。</td>
        </tr>
        <tr>
          <td><b>spatial_exploration_and_viewpoint</b><br>空间探索与视角运动</td>
          <td>reference_and_motion_fidelity 门控</td>
          <td>逻辑 1.00 / 几何 1.35 / 物理 1.00 / 时序 1.25 / 参考运动 1.75</td>
          <td>必须执行指定 orbit、pan、dolly、crane、内窥镜、无人机或机器人第一视角运动；静态替代应被明显降分；视角变化中设备几何、尺度、背景和参考身份保持稳定。</td>
        </tr>
        <tr>
          <td><b>industrial_logic_and_compliance</b><br>工业逻辑与安全合规</td>
          <td>industrial_logic_and_fact_alignment</td>
          <td>逻辑 1.85 / 几何 1.05 / 物理 1.25 / 时序 1.35 / 参考运动 0.95</td>
          <td>违规、触发、告警、停机、制动、疏散或处置必须形成完整因果闭环；人员、车辆、区域、告警和设备状态保持身份连续；应急制动、入侵、爆炸或坠落响应具备物理可行性。</td>
        </tr>
      </tbody>
    </table>
  </section>
"""

TASK_SCORING_CARDS = {
    "rigid_body_kinematics_and_coupling": {
        "title": "刚体运动与多轴耦合评分标准",
        "priority": "最高权重：geometric_integrity；重点提高 physical_plausibility 和 temporal_consistency。",
        "weights": "逻辑 1.10 / 几何 1.70 / 物理 1.45 / 时序 1.25 / 参考运动 0.85",
        "criteria": [
            "刚性结构、关节中心、轴线、支撑点、吊索或载荷路径不能漂移、断裂、软化或错误融合。",
            "运动必须符合可达姿态、载荷方向、接触关系和多轴联动，不允许悬浮、穿模或无支撑运动。",
            "同一设备、工具、工件和背景在全视频中保持身份连续，不能中途换型或闪烁。",
        ],
    },
    "topology_mutation_and_failure": {
        "title": "拓扑突变与局部失效评分标准",
        "priority": "最高权重：geometric_integrity；重点提高 reference_and_motion_fidelity 和 temporal_consistency。",
        "weights": "逻辑 1.10 / 几何 1.80 / 物理 1.05 / 时序 1.25 / 参考运动 1.35",
        "criteria": [
            "短路、裂纹、断绳、缺齿、破损护栏等变化必须局部、精确、边界清楚。",
            "未发生失效的结构、数量、纹理和背景必须锁定参考图，不能全局重绘或整体变形。",
            "缺陷或失效状态要连续演化并持续存在，不能跳变、消失或扩散到无关区域。",
        ],
    },
    "fluid_dynamics_and_thermodynamics": {
        "title": "流体动力学与热力学评分标准",
        "priority": "最高权重：physical_plausibility；重点提高 temporal_consistency 和 industrial_logic_and_fact_alignment。",
        "weights": "逻辑 1.25 / 几何 1.05 / 物理 1.85 / 时序 1.30 / 参考运动 0.95",
        "criteria": [
            "泄漏、喷射、泥水、烟、火、热扩散必须符合压力方向、重力、边界、风向和热传播规律。",
            "流体、火焰、烟雾或高温飞溅要随时间连续变化，不能瞬移、重置或凭空出现。",
            "事故触发、扩散路径、报警或抑制响应要符合对应工业场景的因果链。",
        ],
    },
    "spatial_exploration_and_viewpoint": {
        "title": "空间探索与视角运动评分标准",
        "priority": "门控轴：reference_and_motion_fidelity；静态替代会被 viewpoint_motion_fidelity 明显拉低。",
        "weights": "逻辑 1.00 / 几何 1.35 / 物理 1.00 / 时序 1.25 / 参考运动 1.75",
        "criteria": [
            "必须执行指定 orbit、pan、dolly、crane、内窥镜、无人机或机器人第一视角运动。",
            "视角变化过程中参考主体、尺度、空间关系、内部结构和背景不能漂移或坍缩。",
            "镜头运动要服务于检查目标，不能用无关裁切、缩放或局部抖动冒充空间探索。",
        ],
    },
    "industrial_logic_and_compliance": {
        "title": "工业逻辑与安全合规评分标准",
        "priority": "最高权重：industrial_logic_and_fact_alignment；重点提高 temporal_consistency 和 physical_plausibility。",
        "weights": "逻辑 1.85 / 几何 1.05 / 物理 1.25 / 时序 1.35 / 参考运动 0.95",
        "criteria": [
            "违规、触发、告警、停机、制动、疏散或处置必须形成完整因果闭环。",
            "人员、车辆、设备、区域、告警灯和停机状态必须保持身份与状态连续。",
            "应急制动、避让、爆炸、坠落或报警响应要有物理可行性，不能只出现符号化效果。",
        ],
    },
}

def scoring_card_html(task_category: str) -> str:
    scoring = TASK_SCORING_CARDS.get(task_category)
    if not scoring:
        return ""
    criteria = "".join(f"<li>{item}</li>" for item in scoring["criteria"])
    return f"""
          <div class="score-box">
            <div class="score-title">{scoring["title"]}</div>
            <div class="score-meta">{scoring["priority"]}</div>
            <div class="score-weights">{scoring["weights"]}</div>
            <ul>{criteria}</ul>
          </div>"""

def extract_domain_key(domain_str: str) -> str:
    m = re.search(r"(visual_security|embodied_robotics|heavy_load_construction|precision_defect_gen|extreme_emergency)", domain_str)
    return m.group(1) if m else ""

def build_html(rows: list[dict]) -> str:
    cards_html = []
    current_domain = None

    for row in rows:
        if row["scene_id"] in SKIP_SCENES:
            continue
        domain_key = extract_domain_key(row["domain"])
        color = DOMAIN_COLORS.get(domain_key, "#555")
        domain_label = DOMAIN_LABELS.get(domain_key, row["domain"])

        # Domain header
        if domain_key != current_domain:
            current_domain = domain_key
            cards_html.append(f"""
    <div class="domain-header" style="border-left:6px solid {color};">
      <h2 style="color:{color};margin:0;">{domain_label}</h2>
    </div>""")

        scene_id = row["scene_id"]
        # Apply scene concept override if present
        concept = SCENE_CONCEPT_OVERRIDES.get(scene_id, {})
        title_zh   = concept.get("title_zh",   row["title_zh"])
        full_prompt = concept.get("full_prompt", FULL_PROMPTS.get(scene_id, row["prompt_truncated"]))
        zh_summary  = concept.get("zh_summary",  ZH_SUMMARY.get(scene_id, ""))

        img_path = find_image(row["image_path"], scene_id)
        if img_path:
            img_tag = f'<img src="{img_to_b64(img_path)}" alt="{scene_id}" style="width:100%;max-width:520px;border-radius:6px;display:block;margin:0 auto;">'
        else:
            img_tag = f'<div style="width:100%;height:200px;background:#eee;display:flex;align-items:center;justify-content:center;color:#999;border-radius:6px;">图片未找到: {row["image_path"]}</div>'

        task_cat_clean = re.sub(r"（.*?）", "", row["task_category"]).strip()
        score_card = scoring_card_html(task_cat_clean)
        scene_video = video_tag(scene_id)
        # Mark overridden scenes
        revised_badge = ' <span style="font-size:11px;background:rgba(255,255,255,0.25);padding:2px 6px;border-radius:3px;">✎ 重构</span>' if scene_id in SCENE_CONCEPT_OVERRIDES else ""

        cards_html.append(f"""
    <div class="scene-card">
      <div class="card-header" style="background:{color};">
        <span class="scene-id">{scene_id}</span>
        <span class="scene-title">{title_zh}{revised_badge}</span>
      </div>
      <div class="card-body">
        <div class="img-col">
          {img_tag}
          <p class="img-caption">{Path(row["image_path"]).name}</p>
        </div>
        <div class="text-col">
          <div class="meta-row">
            <span class="tag" style="background:{color}22;color:{color};">{domain_label}</span>
            <span class="tag tag-gray">{task_cat_clean}</span>
          </div>
          <div class="zh-summary">{zh_summary}</div>
          {scene_video}
          {score_card}
          <div class="prompt-box">
            <div class="prompt-label">Video Generation Prompt</div>
            <div class="prompt-text">{full_prompt}</div>
          </div>
        </div>
      </div>
    </div>""")

    cards = "\n".join(cards_html)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FORGE-Bench 场景参考图与 Prompt 报告</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
          background: #f5f6f7; color: #1a1a1a; line-height: 1.6; }}
  .page {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px; }}
  h1 {{ font-size: 26px; font-weight: 700; margin-bottom: 6px; }}
  .subtitle {{ color: #555; font-size: 14px; margin-bottom: 32px; }}
  .overview-card {{ background: #fff; border-radius: 10px; padding: 20px 22px;
                    margin-bottom: 20px; box-shadow: 0 1px 6px rgba(0,0,0,.1); }}
  .overview-card h2 {{ font-size: 20px; margin-bottom: 12px; }}
  .overview-lead {{ color: #333; font-size: 14px; margin-bottom: 14px; }}
  .flow-row {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
               background: #f8f9fa; border-radius: 8px; padding: 10px 12px;
               margin-bottom: 14px; font-size: 13px; color: #333; }}
  .flow-row span {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 6px;
                    padding: 4px 8px; }}
  .compact-table, .rubric-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  .compact-table th, .compact-table td, .rubric-table th, .rubric-table td {{
    border: 1px solid #e5e7eb; padding: 8px 10px; vertical-align: top;
  }}
  .compact-table th, .rubric-table th {{ background: #f3f4f6; text-align: left; color: #333; }}
  .compact-table td:first-child, .rubric-table td:first-child {{ white-space: nowrap; }}
  .note-text {{ color: #555; font-size: 12px; margin-top: 10px; }}
  .domain-header {{ background: #fff; border-radius: 8px; padding: 14px 20px;
                    margin: 36px 0 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .scene-card {{ background: #fff; border-radius: 10px; margin-bottom: 20px;
                 box-shadow: 0 1px 6px rgba(0,0,0,.1); overflow: hidden; }}
  .card-header {{ padding: 10px 18px; display: flex; align-items: center; gap: 12px; }}
  .scene-id {{ font-family: monospace; font-size: 12px; background: rgba(255,255,255,.25);
               color: #fff; padding: 2px 8px; border-radius: 4px; }}
  .scene-title {{ font-size: 16px; font-weight: 600; color: #fff; }}
  .card-body {{ display: flex; gap: 0; }}
  .img-col {{ width: 320px; min-width: 220px; padding: 16px; border-right: 1px solid #f0f0f0;
              display: flex; flex-direction: column; align-items: center; gap: 8px; }}
  .img-caption {{ font-size: 11px; color: #888; text-align: center; font-family: monospace;
                  word-break: break-all; }}
  .text-col {{ flex: 1; padding: 16px 20px; display: flex; flex-direction: column; gap: 12px; }}
  .meta-row {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .tag {{ font-size: 12px; padding: 3px 10px; border-radius: 20px; font-weight: 500; }}
  .tag-gray {{ background: #f0f0f0; color: #555; }}
  .video-box {{ background: #111; border-radius: 8px; overflow: hidden; border: 1px solid #222; }}
  .video-label {{ color: #ddd; font-size: 11px; font-weight: 700; letter-spacing: .06em;
                  text-transform: uppercase; padding: 8px 10px 0; }}
  .video-box video {{ display: block; width: 100%; max-height: 360px; background: #000; margin-top: 8px; }}
  .video-caption {{ color: #aaa; font-size: 11px; padding: 6px 10px 8px; font-family: monospace;
                    word-break: break-all; }}
  .score-box {{ background: #fffdf7; border: 1px solid #f2e3bd; border-radius: 8px;
                padding: 12px 14px; }}
  .score-title {{ font-size: 13px; font-weight: 700; color: #6b4e16; margin-bottom: 4px; }}
  .score-meta {{ font-size: 12px; color: #5f6368; margin-bottom: 4px; }}
  .score-weights {{ font-size: 12px; color: #333; font-family: monospace;
                    background: #fff7df; border-radius: 4px; padding: 4px 6px; margin-bottom: 6px; }}
  .score-box ul {{ margin-left: 18px; color: #444; font-size: 12px; line-height: 1.65; }}
  .prompt-box {{ background: #f8f9fa; border-radius: 8px; padding: 14px 16px; }}
  .zh-summary {{ font-size: 13px; color: #444; line-height: 1.65;
                 border-left: 3px solid #ddd; padding-left: 10px; }}
  .prompt-label {{ font-size: 11px; font-weight: 700; color: #888; letter-spacing: .06em;
                   text-transform: uppercase; margin-bottom: 8px; }}
  .prompt-text {{ font-size: 13px; color: #333; line-height: 1.7; }}
  @media (max-width: 700px) {{
    .card-body {{ flex-direction: column; }}
    .img-col {{ width: 100%; border-right: none; border-bottom: 1px solid #f0f0f0; }}
  }}
</style>
</head>
<body>
<div class="page">
  <h1>FORGE-Bench 场景参考图与 Prompt 报告</h1>
  <p class="subtitle">每个场景选取代表参考图（__ref），配套完整 Video Generation Prompt。共 {len(rows)} 个场景。</p>
  {ARCHITECTURE_HTML}
  {cards}
</div>
</body>
</html>"""


def main():
    rows = parse_md_table(SRC_MD)
    print(f"Parsed {len(rows)} scenes")
    html = build_html(rows)
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    size_mb = OUT_HTML.stat().st_size / 1024 / 1024
    print(f"Written: {OUT_HTML}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
