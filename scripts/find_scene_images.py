#!/usr/bin/env python3
"""Find 2 open-license reference images for each of the 48 FORGE scenarios.

Searches Wikimedia Commons and Openverse. For each scenario, tries multiple
query variants until 2 accepted images are found. Writes images to
dataset/images/{domain}/{scene_id}_1.jpg and _2.jpg, and writes a manifest
to reports/scene_image_manifest.csv plus prompts to reports/scene_prompts.json.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "dataset" / "images"
MANIFEST_PATH = ROOT / "reports" / "scene_image_manifest.csv"
PROMPTS_PATH = ROOT / "reports" / "scene_prompts.json"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
USER_AGENT = "FORGE-Bench/1.0 (open-license research; scene image finder)"

MIN_WIDTH = 1280
MIN_HEIGHT = 720
MIN_SHORT_SIDE = 900
MIN_LAPLACIAN_VAR = 50.0
MAX_EDGE_DENSITY = 0.26
MAX_BG_EDGE_DENSITY = 0.22
IMAGES_PER_SCENE = 2

ALLOWED_LICENSE_HINTS = ("cc0", "public domain", "pd-", "cc-by", "cc by", "cc-by-sa", "cc by-sa")
BLOCKED_TITLE_TERMS = (
    "logo", "icon", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "sign", "symbol", "flag", "animation",
    "cartoon", "model", "toy", "miniature", "screenshot", "blueprint",
    # book/document scan blocklist
    "volume", "monthly", "weekly", "annual", "journal", "magazine",
    "newspaper", "register", "press", "gazette", "bulletin", "proceedings",
    "transactions", "handbook", "manual", "catalogue", "catalog",
    "encyclopedia", "dictionary", "atlas", "album", "yearbook",
    ".pdf", ".djvu", ".epub",
)
ALLOWED_MIME = ("image/jpeg", "image/png", "image/webp", "image/tiff")
BLOCKED_URL_TERMS = ("archive.org", "books.google", "hathitrust")


# ---------------------------------------------------------------------------
# Scene definitions
# ---------------------------------------------------------------------------

@dataclass
class Scene:
    scene_id: str
    domain: str
    name_zh: str
    name_en: str
    reference_subject: str
    core_scenario: str
    task_category: str
    eval_focus: str
    query_variants: list[str]
    video_generation_prompt: str = ""

    def full_prompt(self) -> str:
        weights = TASK_WEIGHTS[self.task_category]
        w_str = ", ".join(f"{k}={v}" for k, v in weights.items())
        return (
            f"Task objective: {self.domain} for {self.task_category}. "
            f"Core scenario: {self.core_scenario}. "
            f"Reference subject: {self.reference_subject}. "
            f"Industrial logic and fact alignment check: preserve the causal chain, "
            f"equipment roles, personnel or vehicle states, compliance triggers, alarms, "
            f"stops, and consequences described by the scenario. "
            f"Geometric integrity check: preserve topology, rigid joints, load-bearing members, "
            f"local defect boundaries, repeated structures, component counts, and spatial "
            f"relationships; only the requested failure or defect region may change. "
            f"Physical plausibility check: obey gravity, contact, rigid-body coupling, load "
            f"paths, pressure direction, fluid diffusion, heat or flame propagation, and "
            f"feasible emergency dynamics. "
            f"Temporal consistency check: maintain object identity, material state, background, "
            f"local event state, and cause-effect continuity across all frames without flicker, "
            f"melting, or role switching. "
            f"Reference and motion fidelity check: execute the requested viewpoint control while "
            f"locking the reference identity, perspective, non-mutated regions, and background details. "
            f"Execution constraints: do not add or remove functional parts; do not change component "
            f"counts; do not merge separate structures unless the requested failure requires it. "
            f"Evaluation focus: {self.eval_focus}. "
            f"Scoring emphasis: {w_str}."
        )


TASK_WEIGHTS = {
    "rigid_body_kinematics_and_coupling": {
        "geometric_integrity": 1.70, "physical_plausibility": 1.45,
        "temporal_consistency": 1.25, "industrial_logic_and_fact_alignment": 1.10,
        "reference_and_motion_fidelity": 0.85,
    },
    "topology_mutation_and_failure": {
        "geometric_integrity": 1.70, "reference_and_motion_fidelity": 1.40,
        "temporal_consistency": 1.30, "physical_plausibility": 1.00,
        "industrial_logic_and_fact_alignment": 0.85,
    },
    "fluid_dynamics_and_thermodynamics": {
        "physical_plausibility": 1.65, "temporal_consistency": 1.35,
        "industrial_logic_and_fact_alignment": 1.30, "geometric_integrity": 1.00,
        "reference_and_motion_fidelity": 0.85,
    },
    "spatial_exploration_and_viewpoint": {
        "reference_and_motion_fidelity": 1.70, "geometric_integrity": 1.30,
        "temporal_consistency": 1.25, "physical_plausibility": 1.00,
        "industrial_logic_and_fact_alignment": 0.85,
    },
    "industrial_logic_and_compliance": {
        "industrial_logic_and_fact_alignment": 1.65, "temporal_consistency": 1.35,
        "physical_plausibility": 1.25, "geometric_integrity": 1.00,
        "reference_and_motion_fidelity": 0.85,
    },
}

SCENES: list[Scene] = [
    # ── Visual Security ──────────────────────────────────────────────────────
    Scene(
        scene_id="vsec_s01",
        domain="visual_security",
        name_zh="未报备车辆闯入禁区",
        name_en="Unauthorized Vehicle Entering Restricted Zone",
        reference_subject="factory gate with vehicle access control barrier",
        core_scenario="an unregistered third-party vehicle drives through a factory or warehouse restricted-zone entrance past a lowered barrier",
        task_category="industrial_logic_and_compliance",
        eval_focus="violation detection, alarm trigger, vehicle trajectory, access boundary integrity",
        query_variants=[
            "factory gate vehicle access control barrier industrial",
            "warehouse entrance barrier restricted zone vehicle",
            "industrial facility gate security checkpoint vehicle",
            "factory perimeter gate boom barrier car",
        ],
        video_generation_prompt="An unregistered vehicle pushes through the lowered barrier at a factory restricted-zone gate; security alarm activates and the vehicle trajectory is tracked across the access boundary.",
    ),
    Scene(
        scene_id="vsec_s02",
        domain="visual_security",
        name_zh="高空作业缺PPE",
        name_en="Height Work Without PPE",
        reference_subject="worker on elevated platform or scaffolding without safety helmet",
        core_scenario="a construction worker performs tasks at height on scaffolding or an elevated platform without a safety helmet or safety harness",
        task_category="industrial_logic_and_compliance",
        eval_focus="person identity stability, PPE violation consequence, compliance logic",
        query_variants=[
            "worker scaffolding height without helmet safety violation",
            "construction worker elevated platform no hard hat",
            "industrial worker height work safety compliance",
            "worker scaffold elevated no PPE industrial",
        ],
        video_generation_prompt="A worker on scaffolding performs overhead tasks without a safety helmet; the missing PPE is visually conspicuous against the industrial background, and a compliance alarm response follows.",
    ),
    Scene(
        scene_id="vsec_s03",
        domain="visual_security",
        name_zh="叉车超速转弯货物滑移",
        name_en="Forklift Overspeed Turn Cargo Slide",
        reference_subject="forklift carrying loaded pallet in warehouse aisle",
        core_scenario="a forklift takes a sharp turn at excessive speed causing pallet cargo to slide outward under centrifugal force",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="rigid body motion, load inertia, contact relationship between pallet and forks",
        query_variants=[
            "forklift warehouse aisle pallet load",
            "forklift carrying pallet industrial warehouse",
            "forklift turning aisle cargo pallet warehouse",
            "warehouse forklift loaded forks pallet",
        ],
        video_generation_prompt="A loaded forklift takes a sharp corner in a warehouse aisle at overspeed; the pallet cargo slides laterally off the forks under centrifugal force.",
    ),
    Scene(
        scene_id="vsec_s04",
        domain="visual_security",
        name_zh="吊装载荷靠近人员",
        name_en="Crane Load Approaching Personnel",
        reference_subject="overhead bridge crane with suspended load in factory",
        core_scenario="an overhead crane or bridge crane swings its suspended load close to workers on the factory floor, triggering an emergency stop",
        task_category="industrial_logic_and_compliance",
        eval_focus="sling load path, danger zone boundary, emergency stop response",
        query_variants=[
            "overhead bridge crane suspended load factory floor",
            "crane lifting load workers factory industrial",
            "bridge crane hook load industrial hall",
            "overhead crane load swing factory",
        ],
        video_generation_prompt="An overhead crane's suspended load swings toward workers on the factory floor; the proximity triggers an emergency stop and workers respond to the danger zone.",
    ),
    Scene(
        scene_id="vsec_s05",
        domain="visual_security",
        name_zh="CCTV盲区巡检",
        name_en="CCTV Blind-Spot Patrol",
        reference_subject="PTZ surveillance camera on factory or warehouse ceiling",
        core_scenario="a PTZ surveillance camera performs a slow pan across a large warehouse or factory floor blind spot, revealing obscured areas",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="viewpoint motion continuity, spatial consistency, target appearance in blind spot",
        query_variants=[
            "PTZ surveillance camera factory warehouse ceiling",
            "CCTV camera industrial building interior",
            "security camera warehouse ceiling mount",
            "surveillance camera industrial facility",
        ],
        video_generation_prompt="A ceiling-mounted PTZ camera pans steadily across the warehouse floor, sweeping from a visible area into the blind spot where targets gradually come into view.",
    ),
    Scene(
        scene_id="vsec_s06",
        domain="visual_security",
        name_zh="围栏/护栏破损入侵",
        name_en="Fence Breach Intrusion",
        reference_subject="industrial perimeter fence or safety barrier at factory boundary",
        core_scenario="a restricted-area perimeter wire fence is locally damaged by external impact, creating a visible gap in the boundary",
        task_category="topology_mutation_and_failure",
        eval_focus="local topology change, boundary integrity, surrounding fence unchanged",
        query_variants=[
            "industrial perimeter wire mesh fence factory boundary",
            "factory security fence perimeter industrial",
            "wire fence industrial restricted area",
            "chain link fence factory perimeter",
        ],
        video_generation_prompt="A section of the factory's perimeter wire fence deforms and breaks open under external impact, creating a visible gap while the surrounding fence structure stays intact.",
    ),
    Scene(
        scene_id="vsec_s07",
        domain="visual_security",
        name_zh="危化品装卸区液体泄漏",
        name_en="Hazmat Loading Area Liquid Spill",
        reference_subject="chemical loading dock or hazardous goods unloading area with drums or tanks",
        core_scenario="an unknown chemical liquid leaks from a container and spreads across the floor of a dangerous-goods loading zone",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="fluid direction, ground spread pattern, hazard zone boundary",
        query_variants=[
            "chemical loading dock hazardous goods drums industrial",
            "hazmat unloading area chemical barrels industrial",
            "dangerous goods storage loading area chemical",
            "chemical warehouse loading zone drums containers",
        ],
        video_generation_prompt="Chemical liquid leaks from a drum in the hazmat loading zone and spreads across the concrete floor, following the ground slope and pooling near the containment boundary.",
    ),
    Scene(
        scene_id="vsec_s08",
        domain="visual_security",
        name_zh="人车混行近失事故",
        name_en="Pedestrian-Vehicle Near-Miss",
        reference_subject="forklift or AGV operating in marked warehouse aisle near pedestrian walkway",
        core_scenario="a pedestrian accidentally enters a forklift or AGV traffic lane and a near-miss occurs with emergency braking",
        task_category="industrial_logic_and_compliance",
        eval_focus="braking response, avoidance maneuver, causal chain from intrusion to stop",
        query_variants=[
            "forklift AGV warehouse aisle pedestrian zone",
            "warehouse forklift aisle pedestrian marking",
            "AGV autonomous mobile robot warehouse aisle",
            "forklift pedestrian crossing warehouse industrial",
        ],
        video_generation_prompt="A pedestrian steps into the AGV lane; the vehicle detects the intrusion and applies emergency braking, stopping just short of the pedestrian while an alarm sounds.",
    ),
    Scene(
        scene_id="vsec_s09",
        domain="visual_security",
        name_zh="烟雾报警与疏散",
        name_en="Smoke Alarm and Evacuation",
        reference_subject="industrial machine or electrical cabinet emitting smoke in factory",
        core_scenario="electrical equipment or an industrial machine begins emitting smoke, triggering the smoke alarm and initiating personnel evacuation",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="smoke evolution, alarm response timing, evacuation continuity",
        query_variants=[
            "factory smoke alarm industrial machine fire",
            "electrical cabinet smoke industrial facility",
            "industrial machine smoke fire alarm factory",
            "smoke detector factory alarm industrial equipment",
        ],
        video_generation_prompt="Smoke begins rising from an electrical cabinet on the factory floor; the smoke alarm activates, strobe lights flash, and workers evacuate the area in an orderly sequence.",
    ),
    Scene(
        scene_id="vsec_s10",
        domain="visual_security",
        name_zh="传送带防护罩缺失",
        name_en="Conveyor Guard Missing",
        reference_subject="industrial conveyor belt with safety guard cover in factory",
        core_scenario="a rotating conveyor or production machine is found operating with its safety guard cover missing or displaced, exposing moving parts",
        task_category="topology_mutation_and_failure",
        eval_focus="equipment topology, exposed hazard zone, compliance assessment",
        query_variants=[
            "conveyor belt safety guard industrial factory",
            "industrial conveyor belt guard cover production line",
            "production line conveyor belt guard protective cover",
            "factory conveyor belt rotating machinery guard",
        ],
        video_generation_prompt="The conveyor belt safety guard is shown missing or shifted, exposing the rotating drive mechanism; the camera slowly reveals the hazard zone while the machine continues to run.",
    ),

    # ── Embodied Robotics ────────────────────────────────────────────────────
    Scene(
        scene_id="robo_s01",
        domain="embodied_robotics",
        name_zh="多轴机械臂精密抓取",
        name_en="Multi-Axis Robot Arm Precision Grasping",
        reference_subject="industrial robot arm grasping a workpiece in automation cell",
        core_scenario="a multi-axis industrial robot arm reaches for and grasps a precision workpiece while maintaining stable tool-contact geometry",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="joint coupling, end-effector trajectory, contact stability",
        query_variants=[
            "industrial robot arm grasping workpiece automation",
            "robotic arm pick place industrial cell",
            "6-axis robot arm industrial manufacturing",
            "robot arm end effector gripper workpiece",
        ],
        video_generation_prompt="A 6-axis robot arm extends toward a precision workpiece, closes its gripper with stable contact, and lifts the part while maintaining kinematic coupling across all joints.",
    ),
    Scene(
        scene_id="robo_s02",
        domain="embodied_robotics",
        name_zh="协作机器人与人交接",
        name_en="Cobot Human Handover",
        reference_subject="collaborative robot arm near human worker in shared workspace",
        core_scenario="a collaborative robot (cobot) slows down and safely hands a workpiece directly to a human worker in a shared workspace",
        task_category="industrial_logic_and_compliance",
        eval_focus="safety deceleration, human-robot distance, compliance logic",
        query_variants=[
            "collaborative robot cobot human worker handover",
            "cobot human collaboration industrial workspace",
            "collaborative robot human interaction factory",
            "robot human shared workspace industrial cobot",
        ],
        video_generation_prompt="A cobot decelerates as a human worker's hand enters the shared zone, completes the part handover at reduced speed, and confirms the transfer before returning to its home position.",
    ),
    Scene(
        scene_id="robo_s03",
        domain="embodied_robotics",
        name_zh="履带机器人废墟越障",
        name_en="Tracked Robot Rubble Traversal",
        reference_subject="tracked ground robot on rough terrain or rubble",
        core_scenario="a tracked ground robot navigates across rubble, broken concrete, or pipe obstacles in a disaster or industrial search scenario",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="terrain contact, track motion, attitude stability across uneven ground",
        query_variants=[
            "tracked ground robot rubble terrain navigation",
            "crawler robot rough terrain industrial",
            "UGV tracked robot debris terrain",
            "ground robot crawler rubble disaster",
        ],
        video_generation_prompt="A tracked robot drives over broken concrete rubble, its tracks conforming to the terrain while the chassis remains level; it crosses a pipe obstacle and continues forward.",
    ),
    Scene(
        scene_id="robo_s04",
        domain="embodied_robotics",
        name_zh="四足机器人第一视角巡检",
        name_en="Quadruped Robot First-Person Inspection",
        reference_subject="quadruped legged robot walking in industrial or construction environment",
        core_scenario="a quadruped robot walks through an industrial facility, stairway, or construction site, with a first-person camera viewpoint showing foot contact and path",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="viewpoint motion, foot-ground contact, spatial continuity",
        query_variants=[
            "quadruped robot legged industrial inspection",
            "four legged robot factory inspection walking",
            "legged robot industrial facility stairs",
            "spot robot quadruped industrial environment",
        ],
        video_generation_prompt="From a first-person viewpoint mounted on a quadruped robot, the camera moves steadily through the factory floor, capturing foot contacts on the surface and spatial transitions at each step.",
    ),
    Scene(
        scene_id="robo_s05",
        domain="embodied_robotics",
        name_zh="AMR仓储导航",
        name_en="AMR Warehouse Navigation",
        reference_subject="autonomous mobile robot navigating between warehouse shelves",
        core_scenario="an autonomous mobile robot navigates between storage racks and pallets in a warehouse, avoiding dynamic obstacles",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="path planning continuity, obstacle avoidance, chassis stability",
        query_variants=[
            "autonomous mobile robot AMR warehouse shelves navigation",
            "mobile robot warehouse logistics navigation",
            "AMR logistics robot warehouse aisle",
            "autonomous robot warehouse storage rack",
        ],
        video_generation_prompt="An AMR glides between tall warehouse racks, smoothly decelerates around a forklift parked in the aisle, and continues its route to the destination station without collision.",
    ),
    Scene(
        scene_id="robo_s06",
        domain="embodied_robotics",
        name_zh="光幕触发紧急制动",
        name_en="Light Curtain Emergency Stop",
        reference_subject="safety light curtain or laser barrier at robot cell entry",
        core_scenario="a worker's hand crosses the safety light curtain at a robot cell boundary, triggering an immediate emergency stop of the robot arm",
        task_category="industrial_logic_and_compliance",
        eval_focus="trigger-brake-stop causal chain, response timing",
        query_variants=[
            "safety light curtain robot cell industrial",
            "laser safety barrier robot industrial cell",
            "light curtain safety fence robot industrial",
            "industrial robot safety light barrier fence",
        ],
        video_generation_prompt="A worker's hand breaks the light curtain beam at the robot cell boundary; the robot arm immediately halts mid-motion, all status lights switch to red, and the cell locks out.",
    ),
    Scene(
        scene_id="robo_s07",
        domain="embodied_robotics",
        name_zh="机器人打磨/焊接接触力",
        name_en="Robot Grinding or Welding Contact Force",
        reference_subject="industrial robot performing grinding or welding on metal workpiece",
        core_scenario="an industrial robot applies a grinding wheel or welding torch to a metal workpiece surface with controlled contact force",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="force direction, tool non-penetration, surface stability",
        query_variants=[
            "robot arm grinding welding metal workpiece industrial",
            "industrial robot welding metal part",
            "robot grinding wheel metal surface industrial",
            "robotic welding arm torch workpiece",
        ],
        video_generation_prompt="A robot arm presses a grinding wheel against the metal workpiece surface at a controlled angle, sparks scatter in the correct direction, and the tool maintains surface contact without penetrating.",
    ),
    Scene(
        scene_id="robo_s08",
        domain="embodied_robotics",
        name_zh="多机器人协同避让",
        name_en="Multi-Robot Cooperative Avoidance",
        reference_subject="two industrial robots or AMRs operating in shared workspace",
        core_scenario="two AMRs or robot arms operate in a shared space and perform coordinated path adjustments to avoid collision while completing their tasks",
        task_category="industrial_logic_and_compliance",
        eval_focus="identity preservation, path collision avoidance, timing logic",
        query_variants=[
            "multiple robots collaboration industrial workspace",
            "two robot arms shared workspace industrial",
            "dual AMR robots cooperation warehouse",
            "multi-robot industrial cell cooperation",
        ],
        video_generation_prompt="Two AMRs approach the same intersection from perpendicular aisles; one slows to yield while the other passes, then both resume their routes without any identity swap.",
    ),
    Scene(
        scene_id="robo_s09",
        domain="embodied_robotics",
        name_zh="管道爬行机器人巡检",
        name_en="Pipe Crawling Robot Inspection",
        reference_subject="pipe inspection robot inside or on pipeline conduit",
        core_scenario="a pipe-crawling robot enters a pipeline or conduit, advancing with an endoscopic viewpoint to inspect the interior wall for defects",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="endoscopic viewpoint, cylindrical geometry, local defect visibility",
        query_variants=[
            "pipe inspection robot inside pipeline",
            "crawling robot pipeline interior inspection",
            "endoscope pipe robot inspection industrial",
            "pipeline robot crawler inspection tube",
        ],
        video_generation_prompt="The pipe-crawling robot advances through a cylindrical conduit; the onboard camera shows the circular interior wall scrolling past with occasional surface markings and a local corrosion patch.",
    ),
    Scene(
        scene_id="robo_s10",
        domain="embodied_robotics",
        name_zh="夹爪局部失效恢复",
        name_en="Gripper Partial Failure Recovery",
        reference_subject="robot gripper or suction cup holding a workpiece",
        core_scenario="one suction cup or jaw of a robot gripper partially loses grip, causing the workpiece to shift, while the robot detects the error and recovers",
        task_category="topology_mutation_and_failure",
        eval_focus="local failure detection, object pose change, robot stability during recovery",
        query_variants=[
            "robot gripper suction cup holding workpiece industrial",
            "robotic suction cup gripper part picking",
            "robot hand gripper industrial pick place",
            "vacuum gripper robot industrial part",
        ],
        video_generation_prompt="One suction cup of the robot's gripper loses vacuum; the workpiece tilts noticeably, the robot pauses and re-attempts the grasp, successfully restabilizing the part.",
    ),

    # ── Heavy Load Construction ──────────────────────────────────────────────
    Scene(
        scene_id="hlc_s01",
        domain="heavy_load_construction",
        name_zh="双履带吊协同吊装",
        name_en="Dual Crawler Crane Tandem Lift",
        reference_subject="two crawler cranes lifting a large steel structure module together",
        core_scenario="two crawler cranes perform a tandem lift of a heavy steel structure, with synchronized boom angles and balanced load sharing",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="sling angle, load balance, synchronized motion",
        query_variants=[
            "dual crawler crane tandem lift steel structure",
            "two crawler cranes lifting heavy module",
            "tandem crane lift construction heavy",
            "crawler crane pair lifting steel industrial",
        ],
        video_generation_prompt="Two crawler cranes lift a heavy steel module in tandem; the sling angles equalize as the load clears the ground, and both cranes track the same vertical ascent rate.",
    ),
    Scene(
        scene_id="hlc_s02",
        domain="heavy_load_construction",
        name_zh="钢丝绳过载变形/断裂",
        name_en="Wire Rope Overload Failure",
        reference_subject="wire rope or sling under tension on crane hook or rigging",
        core_scenario="a crane wire rope or lifting sling is subjected to overload, causing visible strand deformation and partial wire breakage at the failure zone",
        task_category="topology_mutation_and_failure",
        eval_focus="local topology destruction, tension path, adjacent strands unchanged",
        query_variants=[
            "wire rope crane sling tension industrial",
            "crane wire rope rigging close up",
            "steel wire rope sling hook crane",
            "lifting wire rope rigging industrial close",
        ],
        video_generation_prompt="The crane wire rope shows progressive strand deformation under overload; individual wires begin to snap at the failure zone while the rope above and below remains intact.",
    ),
    Scene(
        scene_id="hlc_s03",
        domain="heavy_load_construction",
        name_zh="矿卡泥泞坡道爬坡",
        name_en="Mining Truck Muddy Slope Climb",
        reference_subject="large mining haul truck on muddy or unpaved road",
        core_scenario="a large mining haul truck drives up a steep muddy ramp, with tires sinking into soft ground and the drivetrain straining for traction",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="tire sinkage, traction force, ground contact deformation",
        query_variants=[
            "mining haul truck muddy road slope",
            "dump truck mine muddy terrain slope",
            "large mining truck unpaved road mud",
            "haul truck mining slope dirt road",
        ],
        video_generation_prompt="A heavy mining haul truck climbs a steep muddy ramp; the tires sink visibly into the soft earth with each rotation, throwing mud as the truck grinds upward.",
    ),
    Scene(
        scene_id="hlc_s04",
        domain="heavy_load_construction",
        name_zh="龙门吊强风扰动",
        name_en="Gantry Crane Wind Disturbance",
        reference_subject="large gantry crane or container crane at port or construction site",
        core_scenario="a gantry or container crane structure sways under strong wind loading, with the suspended load oscillating on its hoist rope",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="wind load, structural sway, suspended load oscillation",
        query_variants=[
            "gantry crane port container industrial large",
            "container crane port terminal industrial",
            "large gantry crane construction site",
            "port gantry crane steel structure large",
        ],
        video_generation_prompt="A tall gantry crane sways slightly in strong wind; the suspended load swings as a pendulum, the hoist rope angle changes with each gust, and the structure returns to plumb during lulls.",
    ),
    Scene(
        scene_id="hlc_s05",
        domain="heavy_load_construction",
        name_zh="桥梁节段无人机巡检",
        name_en="Bridge Segment Drone Inspection",
        reference_subject="precast bridge segment or bridge span at construction site",
        core_scenario="a drone orbits around a precast bridge segment or completed bridge span to inspect alignment and surface condition",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="viewpoint motion, scale consistency, geometric preservation",
        query_variants=[
            "precast bridge segment construction site concrete",
            "bridge segment construction precast concrete",
            "bridge construction precast segment alignment",
            "concrete bridge girder segment construction",
        ],
        video_generation_prompt="A drone orbits a precast bridge segment, maintaining constant standoff distance; the camera reveals surface texture, alignment marks, and the full cross-section profile from multiple angles.",
    ),
    Scene(
        scene_id="hlc_s06",
        domain="heavy_load_construction",
        name_zh="挖掘机多连杆装载",
        name_en="Excavator Multi-Link Loading",
        reference_subject="excavator with boom, arm, and bucket in operation at construction site",
        core_scenario="an excavator performs a multi-link dig-and-load cycle, with the boom, arm, and bucket moving in coupled hydraulic articulation",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="joint center tracking, hydraulic arm coupling, soil contact",
        query_variants=[
            "excavator boom arm bucket construction site",
            "excavator digging loading construction",
            "hydraulic excavator arm bucket soil",
            "excavator construction site digging",
        ],
        video_generation_prompt="The excavator's boom rises while the arm curls inward and the bucket closes around a load of earth; all three links move in coupled sequence as hydraulic pressure shifts.",
    ),
    Scene(
        scene_id="hlc_s07",
        domain="heavy_load_construction",
        name_zh="吊车支腿地基沉陷",
        name_en="Crane Outrigger Ground Sinkage",
        reference_subject="mobile crane outrigger pad on soft ground at construction site",
        core_scenario="a mobile crane outrigger pad sinks progressively into soft soil, causing the crane body to tilt as the support fails",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="support state change, center of gravity shift, local ground deformation",
        query_variants=[
            "crane outrigger pad ground construction site",
            "mobile crane outrigger soft ground",
            "crane stabilizer outrigger construction",
            "mobile crane outrigger pad soil",
        ],
        video_generation_prompt="One of the crane's outrigger pads slowly sinks into the soft ground; the crane body tilts gradually, cracks appear in the soil around the pad, and the operator initiates an emergency stop.",
    ),
    Scene(
        scene_id="hlc_s08",
        domain="heavy_load_construction",
        name_zh="地下管线破裂泥水喷涌",
        name_en="Underground Pipe Burst Water Surge",
        reference_subject="construction excavation trench with exposed underground pipes",
        core_scenario="excavation work accidentally ruptures an underground water main, causing muddy water to gush upward through the trench",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="pressure direction, fluid diffusion, trench wall boundary",
        query_variants=[
            "excavation trench underground pipe construction",
            "underground pipe excavation trench water",
            "construction site trench pipeline exposed",
            "excavation underground utility pipe trench",
        ],
        video_generation_prompt="A ruptured water main sends a column of muddy water surging upward through the open trench; the flow spreads laterally along the trench floor and over the excavated edge.",
    ),
    Scene(
        scene_id="hlc_s09",
        domain="heavy_load_construction",
        name_zh="吊物接近结构紧急停止",
        name_en="Load Approaching Structure Emergency Stop",
        reference_subject="crane load approaching scaffolding or steel structure",
        core_scenario="a crane's suspended load swings toward a scaffolding structure, triggering an emergency stop before contact",
        task_category="industrial_logic_and_compliance",
        eval_focus="safety response, swing damping, load stability after stop",
        query_variants=[
            "crane load scaffolding construction steel structure",
            "crane lifting load near structure construction",
            "suspended load crane near scaffold building",
            "crane lift steel frame structure close",
        ],
        video_generation_prompt="A crane load pendulums toward the scaffolding frame; a proximity alarm triggers an emergency stop, the hoist brake engages, and the load oscillates to rest just short of contact.",
    ),
    Scene(
        scene_id="hlc_s10",
        domain="heavy_load_construction",
        name_zh="模板/脚手架局部坍塌",
        name_en="Formwork Scaffold Partial Collapse",
        reference_subject="construction formwork or scaffolding structure at building site",
        core_scenario="a section of temporary formwork or scaffolding fails at a local support, causing a progressive partial collapse",
        task_category="topology_mutation_and_failure",
        eval_focus="local structural failure, support topology change, progressive collapse",
        query_variants=[
            "construction scaffolding formwork building site",
            "scaffolding construction building temporary support",
            "formwork scaffold construction site concrete",
            "scaffold construction building frame temporary",
        ],
        video_generation_prompt="A support joint in the scaffolding buckles under load; the local section folds downward progressively, pulling adjacent bracing, while the outer scaffold rows remain standing.",
    ),

    # ── Precision Defect Gen ─────────────────────────────────────────────────
    Scene(
        scene_id="pdg_s01",
        domain="precision_defect_gen",
        name_zh="PCB焊锡桥短路",
        name_en="PCB Solder Bridge Short Circuit",
        reference_subject="close-up of populated PCB with fine-pitch solder joints",
        core_scenario="a solder bridge forms between adjacent fine-pitch pads on a densely populated PCB, creating a short circuit visible under inspection",
        task_category="topology_mutation_and_failure",
        eval_focus="local defect appearance, trace and pad count stability, unchanged surrounding region",
        query_variants=[
            "PCB circuit board close up solder joints",
            "printed circuit board fine pitch SMD components close",
            "PCB solder inspection close up traces",
            "circuit board SMT component close up macro",
        ],
        video_generation_prompt="Under magnified inspection lighting, a solder bridge gradually forms between two adjacent PCB pads; surrounding traces and components remain unchanged while the bridged region clearly shows the short.",
    ),
    Scene(
        scene_id="pdg_s02",
        domain="precision_defect_gen",
        name_zh="发动机/管道内窥裂纹",
        name_en="Engine or Pipe Borescope Crack",
        reference_subject="borescope view inside turbine engine or pipe interior",
        core_scenario="a borescope inspection of a turbine blade or pipe interior wall reveals a hairline crack propagating from a stress concentration point",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="endoscopic viewpoint, micro-crack localization, geometric stability",
        query_variants=[
            "borescope inspection turbine blade interior",
            "endoscope engine inspection interior blade",
            "borescope pipe interior inspection defect",
            "turbine engine borescope internal inspection",
        ],
        video_generation_prompt="The borescope advances slowly through the turbine interior; the camera centers on a blade surface where a hairline crack is visible, with the surrounding metal surface texture remaining stable.",
    ),
    Scene(
        scene_id="pdg_s03",
        domain="precision_defect_gen",
        name_zh="齿轮缺齿/严重磨损",
        name_en="Gear Tooth Missing or Worn",
        reference_subject="industrial gear with visible teeth in close-up",
        core_scenario="a gear undergoes wear or impact damage causing one or more teeth to chip or break off, visible as a local topology change in the tooth profile",
        task_category="topology_mutation_and_failure",
        eval_focus="periodic structure count, local topology change, undamaged teeth unchanged",
        query_variants=[
            "industrial gear close up teeth macro",
            "gear teeth industrial close up metal",
            "mechanical gear macro industrial",
            "gearbox gear teeth close inspection",
        ],
        video_generation_prompt="The gear rotates slowly; a chipped tooth passes the inspection camera, its broken edge contrasting sharply with the uniform profile of adjacent intact teeth.",
    ),
    Scene(
        scene_id="pdg_s04",
        domain="precision_defect_gen",
        name_zh="五轴CNC曲面切削",
        name_en="5-Axis CNC Surface Machining",
        reference_subject="5-axis CNC machining center with cutting tool on complex workpiece",
        core_scenario="a 5-axis CNC machine tools a complex curved surface, with all five axes moving in coordinated interpolation and coolant spraying",
        task_category="rigid_body_kinematics_and_coupling",
        eval_focus="multi-axis coupling, fixture stability, tool-surface contact",
        query_variants=[
            "5-axis CNC machining center complex surface",
            "CNC milling machine 5 axis industrial",
            "CNC machining center metal cutting industrial",
            "five axis machining center tool workpiece",
        ],
        video_generation_prompt="The 5-axis CNC head sweeps across the curved workpiece surface in a coordinated toolpath; all axes move simultaneously, the cutting tool stays tangent to the surface, and coolant mist sprays at the contact zone.",
    ),
    Scene(
        scene_id="pdg_s05",
        domain="precision_defect_gen",
        name_zh="切削液喷溅",
        name_en="Cutting Fluid Splash",
        reference_subject="CNC machine cutting zone with coolant spray and chips",
        core_scenario="a high-speed CNC cutter generates intense coolant spray and metal chip scatter during aggressive cutting",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="droplet trajectory, rotation direction consistency, fluid continuity",
        query_variants=[
            "CNC cutting coolant spray chips machining",
            "machining coolant spray cutting industrial",
            "metal cutting CNC coolant splash chips",
            "CNC milling coolant chip ejection",
        ],
        video_generation_prompt="The cutting tool spins at high RPM against the metal workpiece; coolant streams arc outward in the expected direction while metal chips scatter in the cutting plane.",
    ),
    Scene(
        scene_id="pdg_s06",
        domain="precision_defect_gen",
        name_zh="焊缝气孔/裂纹",
        name_en="Weld Defect Porosity or Crack",
        reference_subject="close-up of metal weld seam on industrial structure",
        core_scenario="a completed weld seam on a metal structure exhibits porosity holes or a surface crack visible on the bead face",
        task_category="topology_mutation_and_failure",
        eval_focus="metal boundary, local defect geometry, global weld unchanged",
        query_variants=[
            "weld seam close up metal industrial",
            "weld bead metal close up inspection",
            "metal weld seam macro industrial quality",
            "welding bead close up steel industrial",
        ],
        video_generation_prompt="The camera moves along the weld seam at close range; a porosity void appears in the bead center, and a hairline crack extends from it, while the surrounding weld and base metal remain undisturbed.",
    ),
    Scene(
        scene_id="pdg_s07",
        domain="precision_defect_gen",
        name_zh="精密表面划痕",
        name_en="Precision Surface Scratch",
        reference_subject="polished metal, wafer, or bearing surface under inspection lighting",
        core_scenario="a precision polished surface (metal, silicon wafer, or bearing race) develops a visible scratch defect under directional inspection lighting",
        task_category="topology_mutation_and_failure",
        eval_focus="fine detail preservation, local texture change, surrounding surface unchanged",
        query_variants=[
            "polished metal surface close up macro industrial",
            "precision surface inspection metal polished",
            "bearing race surface polished metal macro",
            "silicon wafer surface inspection close up",
        ],
        video_generation_prompt="Under raking inspection light, a fine scratch line appears on the polished metal surface; the scratch reflects differently from the mirror finish while the surrounding area maintains its uniform sheen.",
    ),
    Scene(
        scene_id="pdg_s08",
        domain="precision_defect_gen",
        name_zh="管束内窥巡检",
        name_en="Tube Bundle Borescope Inspection",
        reference_subject="heat exchanger tube bundle end face with multiple tube openings",
        core_scenario="a borescope advances through the tube bundle of a heat exchanger, inspecting each tube's interior for scale, corrosion, or cracks",
        task_category="spatial_exploration_and_viewpoint",
        eval_focus="repeated tube count stability, viewpoint motion continuity",
        query_variants=[
            "heat exchanger tube bundle end face close up",
            "tube bundle heat exchanger inspection industrial",
            "shell tube heat exchanger tube openings",
            "heat exchanger tube sheet industrial inspection",
        ],
        video_generation_prompt="The borescope enters a tube bundle end-face; the circular tube openings scroll past as the probe advances, and the camera briefly lingers in one tube revealing scale deposits on the interior wall.",
    ),
    Scene(
        scene_id="pdg_s09",
        domain="precision_defect_gen",
        name_zh="连接器针脚弯曲/桥接",
        name_en="Connector Pin Bent or Bridged",
        reference_subject="high-density electrical connector with closely spaced pins",
        core_scenario="a high-density connector with many fine pins has one or more pins bent or bridged to an adjacent pin, visible under macro inspection",
        task_category="topology_mutation_and_failure",
        eval_focus="pin count stability, local deformation, unchanged surrounding pins",
        query_variants=[
            "electrical connector pins close up macro",
            "high density connector fine pitch pins",
            "IC connector pins close up inspection",
            "connector terminal pins dense macro industrial",
        ],
        video_generation_prompt="A macro lens reveals the connector pin array; one pin is visibly bent and touching its neighbor, forming a bridge, while adjacent pins maintain their parallel alignment.",
    ),
    Scene(
        scene_id="pdg_s10",
        domain="precision_defect_gen",
        name_zh="精密装配轻微错位",
        name_en="Precision Assembly Slight Misalignment",
        reference_subject="precision mechanical assembly with bearing, shaft, or fixture components",
        core_scenario="a precision assembly shows a slight angular or positional misalignment between a bearing and shaft, visible as a small offset from the nominal position",
        task_category="topology_mutation_and_failure",
        eval_focus="small pose error, component identity stability, misalignment localization",
        query_variants=[
            "precision bearing shaft assembly close up industrial",
            "bearing shaft assembly alignment industrial",
            "precision machined parts assembly industrial",
            "shaft bearing coupling industrial close up",
        ],
        video_generation_prompt="The camera circles the precision assembly at close range; a slight angular offset between the bearing face and shaft shoulder becomes apparent from a specific viewpoint, while both components retain their identity.",
    ),

    # ── Extreme Emergency ────────────────────────────────────────────────────
    Scene(
        scene_id="eem_s01",
        domain="extreme_emergency",
        name_zh="法兰高压泄漏",
        name_en="Flange High-Pressure Leak",
        reference_subject="industrial pipe flange joint with bolts under pressure",
        core_scenario="a high-pressure pipeline flange joint develops a leak, ejecting gas or liquid in a visible jet and causing local visual distortion from heat or pressure",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="pressure direction, jet shape, local distortion boundary",
        query_variants=[
            "industrial pipe flange joint bolts high pressure",
            "pipe flange industrial metal bolted",
            "pipeline flange connection industrial pressure",
            "industrial piping flange joint steel",
        ],
        video_generation_prompt="Gas jets from the pipe flange gap under high pressure; the ejected stream creates a plume that shimmers with heat distortion, while the bolts and flange faces remain structurally visible.",
    ),
    Scene(
        scene_id="eem_s02",
        domain="extreme_emergency",
        name_zh="储罐区闪燃蔓延",
        name_en="Storage Tank Flash Fire Spread",
        reference_subject="industrial storage tank farm or pipeline corridor at chemical plant",
        core_scenario="a flash fire ignites at a storage tank or pipeline corridor and propagates along the fuel path to adjacent equipment",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="flame propagation path, thermal diffusion, boundary preservation",
        query_variants=[
            "industrial storage tank farm chemical plant",
            "oil storage tank farm industrial pipeline",
            "chemical plant storage tank industrial",
            "petroleum storage tank farm industrial facility",
        ],
        video_generation_prompt="A flash fire erupts at the base of one storage tank and spreads along the adjacent pipeline; the flame front moves at ground level, and secondary ignition occurs at the next tank's bund.",
    ),
    Scene(
        scene_id="eem_s03",
        domain="extreme_emergency",
        name_zh="输电铁塔覆冰垮塌",
        name_en="Transmission Tower Ice Load Collapse",
        reference_subject="high-voltage transmission tower with ice-covered wires in winter",
        core_scenario="ice accumulation on transmission line conductors causes progressive mechanical failure of a lattice transmission tower, leading to collapse",
        task_category="topology_mutation_and_failure",
        eval_focus="truss topology, local buckling, gravity direction, progressive collapse",
        query_variants=[
            "transmission tower ice covered winter power line",
            "electricity pylon ice storm winter",
            "high voltage tower ice winter power",
            "power transmission tower ice covered",
        ],
        video_generation_prompt="Ice-laden conductors pull the transmission tower's crossarm downward; the lattice begins to buckle at a diagonal member, and the structure progressively folds inward toward the ground.",
    ),
    Scene(
        scene_id="eem_s04",
        domain="extreme_emergency",
        name_zh="粉尘爆炸与应急响应",
        name_en="Dust Explosion and Emergency Response",
        reference_subject="grain silo, flour mill, or industrial dust-generating facility",
        core_scenario="ignition of a suspended dust cloud inside a grain silo or industrial facility causes a deflagration with a pressure wave and emergency evacuation",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="deflagration dynamics, pressure wave, alarm and evacuation sequence",
        query_variants=[
            "grain silo dust industrial explosion hazard",
            "industrial dust collection system factory",
            "flour mill grain elevator dust industrial",
            "industrial dust hazard factory silo",
        ],
        video_generation_prompt="A dust cloud inside the silo ignites; the deflagration expands outward with a pressure wave that vents through panels while personnel outside begin emergency evacuation and alarms sound.",
    ),
    Scene(
        scene_id="eem_s05",
        domain="extreme_emergency",
        name_zh="反应釜超压泄放",
        name_en="Reactor Overpressure Relief",
        reference_subject="industrial chemical reactor vessel with pressure relief valve",
        core_scenario="pressure inside a chemical reactor exceeds the set point, causing the relief valve to open and vent process gas or steam",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="pressure release direction, valve path, state evolution",
        query_variants=[
            "chemical reactor vessel pressure relief valve industrial",
            "reactor pressure vessel industrial chemical",
            "chemical plant reactor vessel industrial",
            "pressure vessel reactor industrial chemical plant",
        ],
        video_generation_prompt="The reactor pressure gauge climbs into the red zone; the relief valve pops open and a jet of steam and process gas vents upward through the discharge pipe while the pressure indicator drops.",
    ),
    Scene(
        scene_id="eem_s06",
        domain="extreme_emergency",
        name_zh="电池热失控",
        name_en="Battery Thermal Runaway",
        reference_subject="battery energy storage cabinet or battery pack rack",
        core_scenario="a cell within a battery energy storage system enters thermal runaway, producing smoke and venting gas that spreads to adjacent modules",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="thermal diffusion, smoke evolution, local module fault",
        query_variants=[
            "battery energy storage system cabinet rack industrial",
            "lithium battery energy storage industrial cabinet",
            "ESS battery cabinet energy storage system",
            "industrial battery storage rack system",
        ],
        video_generation_prompt="Smoke begins seeping from one battery module in the rack; the thermal runaway spreads to adjacent cells, the cabinet vents open, and the fire suppression system activates overhead.",
    ),
    Scene(
        scene_id="eem_s07",
        domain="extreme_emergency",
        name_zh="隧道火灾烟气分层",
        name_en="Tunnel Fire Smoke Stratification",
        reference_subject="road or railway tunnel interior with lighting and ventilation infrastructure",
        core_scenario="a fire inside a tunnel generates a stratified smoke layer that accumulates near the ceiling while the lower portion remains clearer, driven by ventilation",
        task_category="fluid_dynamics_and_thermodynamics",
        eval_focus="smoke stratification layer, ventilation direction, visibility gradient",
        query_variants=[
            "road tunnel interior lighting ventilation",
            "tunnel interior road emergency lighting",
            "highway tunnel interior concrete ventilation",
            "underground tunnel interior emergency",
        ],
        video_generation_prompt="Smoke from a vehicle fire fills the upper third of the tunnel; the buoyant layer stratifies clearly at ceiling level while the lower zone remains visible; ventilation fans push the smoke layer toward the portal.",
    ),
    Scene(
        scene_id="eem_s08",
        domain="extreme_emergency",
        name_zh="吊载坠落应急撤离",
        name_en="Load Drop Emergency Evacuation",
        reference_subject="crane or hoist with suspended heavy load over work area",
        core_scenario="a crane's suspended load becomes unstable and begins to fall, triggering emergency alarms and immediate evacuation of the work area below",
        task_category="industrial_logic_and_compliance",
        eval_focus="load dynamics, alarm trigger, evacuation sequence",
        query_variants=[
            "crane suspended load construction workers below",
            "overhead crane load factory floor workers",
            "crane hoist load industrial work area",
            "crane lift heavy load construction site workers",
        ],
        video_generation_prompt="The crane hoist rope suddenly goes slack and the load drops; alarms blare instantly and workers scatter away from the drop zone before the load impacts the ground.",
    ),
]


# ---------------------------------------------------------------------------
# Image search / download utilities (reused from find_reference_images.py)
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    title: str
    pageid: int
    imageinfo: dict
    source: str = "commons"


def _url_json(url: str, params: dict, sleep_s: float = 1.0) -> dict:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read()
            if sleep_s:
                time.sleep(sleep_s)
            return json.loads(payload.decode("utf-8"))
        except Exception as exc:
            if "429" in str(exc) or "Too Many" in str(exc):
                wait = 15 * (2 ** attempt)
                print(f"    rate-limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("max retries exceeded")


def _commons_search(query: str, limit: int = 20) -> list[Candidate]:
    params = {
        "action": "query", "format": "json",
        "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    data = _url_json(COMMONS_API, params)
    pages = data.get("query", {}).get("pages", {})
    return [
        Candidate(p.get("title", ""), int(p.get("pageid", 0)), (p.get("imageinfo") or [{}])[0], "commons")
        for p in pages.values() if p.get("imageinfo")
    ]


def _openverse_search(query: str, limit: int = 20) -> list[Candidate]:
    params = {
        "q": query,
        "page_size": str(min(limit, 20)),
        "mature": "false",
        "source": "flickr,wikimedia,stocksnap,rawpixel",
    }
    data = _url_json(OPENVERSE_API, params)
    out = []
    for item in data.get("results", []):
        image_url = item.get("url") or item.get("thumbnail") or ""
        if not image_url:
            continue
        license_name = str(item.get("license") or "")
        imageinfo = {
            "url": image_url, "thumburl": image_url,
            "descriptionurl": item.get("foreign_landing_url") or "",
            "width": int(item.get("width") or 0),
            "height": int(item.get("height") or 0),
            "mime": item.get("mime_type") or "",
            "extmetadata": {
                "LicenseShortName": {"value": license_name},
                "UsageTerms": {"value": str(item.get("license_version") or "")},
                "License": {"value": str(item.get("license_url") or "")},
            },
            "creator": item.get("creator") or "",
            "provider": item.get("provider") or "",
            "license_url": item.get("license_url") or "",
        }
        out.append(Candidate(str(item.get("title") or ""), 0, imageinfo, "openverse"))
    return out


ALLOWED_LICENSE_HINTS = ("cc0", "public domain", "pd-", "cc-by", "cc by", "cc-by-sa", "cc by-sa")


def _license_ok(info: dict) -> tuple[bool, str]:
    meta = info.get("extmetadata", {})
    fields = [
        meta.get("LicenseShortName", {}).get("value", ""),
        meta.get("UsageTerms", {}).get("value", ""),
        meta.get("License", {}).get("value", ""),
    ]
    text = " ".join(fields).lower()
    if any(h in text for h in ALLOWED_LICENSE_HINTS):
        return True, " | ".join(fields)
    if re.search(r"(^|[^a-z])by($|[^a-z])", text) or "by-sa" in text:
        return True, " | ".join(fields)
    return False, " | ".join(fields)


def _title_ok(title: str) -> bool:
    low = title.lower()
    return not any(t in low for t in BLOCKED_TITLE_TERMS)


def _url_ok(url: str) -> bool:
    low = url.lower()
    return not any(t in low for t in BLOCKED_URL_TERMS)


def _mime_ok(mime: str) -> bool:
    return any(mime.startswith(m) for m in ALLOWED_MIME)


def _download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        path.write_bytes(resp.read())


def _image_metrics(path: Path) -> dict:
    with Image.open(path) as pil:
        w, h = pil.size
        pil.verify()
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError("opencv cannot decode image")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 180)
    edge_density = float(np.count_nonzero(edges) / edges.size)
    hh, ww = gray.shape
    border = np.zeros_like(edges, dtype=np.uint8)
    my = max(1, int(hh * 0.18)); mx = max(1, int(ww * 0.18))
    border[:my, :] = 1; border[-my:, :] = 1
    border[:, :mx] = 1; border[:, -mx:] = 1
    bg_edge = float(np.count_nonzero(edges[border == 1]) / max(1, np.count_nonzero(border)))
    return {
        "width": w, "height": h,
        "laplacian_var": lap_var,
        "edge_density": edge_density,
        "background_edge_density": bg_edge,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _passes(m: dict) -> tuple[bool, str]:
    if m["width"] < MIN_WIDTH or m["height"] < MIN_HEIGHT:
        return False, "resolution_too_low"
    if min(m["width"], m["height"]) < MIN_SHORT_SIDE:
        return False, "short_side_too_small"
    if m["laplacian_var"] < MIN_LAPLACIAN_VAR:
        return False, "too_blurry"
    if m["edge_density"] > MAX_EDGE_DENSITY:
        return False, "too_cluttered"
    if m["background_edge_density"] > MAX_BG_EDGE_DENSITY:
        return False, "background_too_cluttered"
    return True, "accepted"


def _average_hash(path: Path, size: int = 8) -> str:
    with Image.open(path) as img:
        img = img.convert("L").resize((size, size), Image.Resampling.LANCZOS)
        arr = np.asarray(img, dtype=np.float32)
    bits = arr > arr.mean()
    v = 0
    for b in bits.flatten():
        v = (v << 1) | int(b)
    return f"{v:0{size * size // 4}x}"


def _hamming(a: str, b: str) -> int:
    n = int(a, 16) ^ int(b, 16)
    return bin(n).count("1")


# ---------------------------------------------------------------------------
# Main search loop
# ---------------------------------------------------------------------------

def find_images_for_scene(
    scene: Scene,
    out_dir: Path,
    seen_hashes: list[str],
    verbose: bool = True,
) -> list[dict]:
    """Search and download up to IMAGES_PER_SCENE images for a scene."""
    # Skip slots that already have files on disk
    results: list[dict] = []
    for idx in range(1, IMAGES_PER_SCENE + 1):
        for ext in (".jpg", ".png", ".webp"):
            p = out_dir / f"{scene.scene_id}_{idx}{ext}"
            if p.exists():
                results.append({"scene_id": scene.scene_id, "img_index": idx,
                                 "local_path": str(p), "source": "existing",
                                 "source_title": "", "source_url": "", "image_url": "",
                                 "license": "", "width": 0, "height": 0,
                                 "laplacian_var": "", "edge_density": "", "sha256": ""})
                break
    if len(results) >= IMAGES_PER_SCENE:
        print(f"  -> already have {len(results)}/{IMAGES_PER_SCENE}, skipping")
        return results
    target = IMAGES_PER_SCENE

    for query in scene.query_variants:
        if len(results) >= target:
            break
        for provider, search_fn in [("openverse", _openverse_search), ("commons", _commons_search)]:
            if len(results) >= target:
                break
            if verbose:
                print(f"  [{scene.scene_id}] {provider}: {query!r}")
            try:
                candidates = search_fn(query)
            except Exception as exc:
                print(f"    search error: {exc}")
                continue

            for cand in candidates:
                if len(results) >= target:
                    break
                info = cand.imageinfo
                ok_lic, lic_text = _license_ok(info)
                if not ok_lic:
                    continue
                if not _title_ok(cand.title):
                    continue
                mime = info.get("mime", "")
                if mime and not _mime_ok(mime):
                    continue
                url_check = info.get("thumburl") or info.get("url", "")
                if not _url_ok(url_check):
                    continue
                if int(info.get("width", 0)) < MIN_WIDTH or int(info.get("height", 0)) < MIN_HEIGHT:
                    continue

                img_idx = len(results) + 1
                suffix = ".jpg" if "jpeg" in info.get("mime", "").lower() else ".png"
                local_path = out_dir / f"{scene.scene_id}_{img_idx}{suffix}"
                url = info.get("thumburl") or info.get("url", "")
                if not url:
                    continue
                try:
                    _download(url, local_path)
                    metrics = _image_metrics(local_path)
                    ahash = _average_hash(local_path)
                    ok_img, reason = _passes(metrics)
                    if ok_img and any(_hamming(ahash, h) <= 4 for h in seen_hashes):
                        ok_img, reason = False, "near_duplicate"
                    if not ok_img:
                        local_path.unlink(missing_ok=True)
                        if verbose:
                            print(f"    rejected ({reason}): {cand.title}")
                        continue
                    seen_hashes.append(ahash)
                    results.append({
                        "scene_id": scene.scene_id,
                        "img_index": img_idx,
                        "local_path": local_path.as_posix(),
                        "source": provider,
                        "source_title": cand.title,
                        "source_url": info.get("descriptionurl", ""),
                        "image_url": url,
                        "license": lic_text,
                        "width": metrics["width"],
                        "height": metrics["height"],
                        "laplacian_var": f"{metrics['laplacian_var']:.1f}",
                        "edge_density": f"{metrics['edge_density']:.4f}",
                        "sha256": metrics["sha256"],
                    })
                    print(f"    ACCEPTED [{img_idx}/{target}]: {local_path.name}  ({metrics['width']}x{metrics['height']})")
                except Exception as exc:
                    local_path.unlink(missing_ok=True)
                    if verbose:
                        print(f"    download/metric error: {exc}")

    return results


def write_manifest(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_prompts(scenes: list[Scene], image_rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_scene: dict[str, list[dict]] = {}
    for r in image_rows:
        by_scene.setdefault(r["scene_id"], []).append(r)

    out = []
    for scene in scenes:
        imgs = by_scene.get(scene.scene_id, [])
        out.append({
            "scene_id": scene.scene_id,
            "domain": scene.domain,
            "name_zh": scene.name_zh,
            "name_en": scene.name_en,
            "reference_subject": scene.reference_subject,
            "core_scenario": scene.core_scenario,
            "task_category": scene.task_category,
            "eval_focus": scene.eval_focus,
            "video_generation_prompt": scene.video_generation_prompt,
            "full_evaluation_prompt": scene.full_prompt(),
            "reference_images": [
                {"index": r["img_index"], "path": r["local_path"], "source": r["source_title"]}
                for r in imgs
            ],
        })
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Find 2 reference images per FORGE scene.")
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--scenes", nargs="*", help="limit to specific scene_ids")
    args = parser.parse_args()

    scenes = SCENES
    if args.scenes:
        scene_set = set(args.scenes)
        scenes = [s for s in SCENES if s.scene_id in scene_set]

    all_rows: list[dict] = []
    seen_hashes: list[str] = []

    for scene in scenes:
        out_dir = IMAGES_DIR / scene.domain
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {scene.scene_id}: {scene.name_zh} ({scene.name_en}) ===")
        rows = find_images_for_scene(scene, out_dir, seen_hashes, verbose=args.verbose)
        all_rows.extend(rows)
        found = len(rows)
        print(f"  -> found {found}/{IMAGES_PER_SCENE} images")

    write_manifest(all_rows, MANIFEST_PATH)
    write_prompts(SCENES, all_rows, PROMPTS_PATH)

    total = len(all_rows)
    scenes_with_both = sum(
        1 for s in SCENES
        if sum(1 for r in all_rows if r["scene_id"] == s.scene_id) >= 2
    )
    print(f"\nDone. {total} images downloaded, {scenes_with_both}/{len(SCENES)} scenes have 2 images.")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Prompts:  {PROMPTS_PATH}")


if __name__ == "__main__":
    main()
