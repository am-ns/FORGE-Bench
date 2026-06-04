#!/usr/bin/env python3
"""Targeted candidate image backfill for hard FORGE scenes.

This is separate from the broad bulk downloader. It uses short, hand-written
queries and Commons categories because the prompt-derived long queries have low
hit rates for several late-stage scenes.
"""

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
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
LOC_API = "https://www.loc.gov/photos/"
NARA_API = "https://catalog.archives.gov/api/v1/"
USER_AGENT = "FORGE-Bench targeted candidate backfill v2/1.0"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

BLOCKED_TERMS = {
    "book", "cover", "diagram", "drawing", "render", "rendering", "map",
    "chart", "graph", "poster", "logo", "manual", "catalog", "catalogue",
    "journal", "magazine", "newspaper", "volume", "page", "plate", "pdf",
    "djvu", "svg", "blueprint", "schematic", "flowchart", "icon", "symbol",
    "toy", "miniature", "model", "illustration", "infographic", "cartoon",
    "patent", "presentation", "slide", "screenshot", "clipart", "vector",
    "silhouette", "template", "floor plan", "site plan", "cross section",
    "cutaway", "animation", "3d model", "scale model", "diorama", "lego",
    "simulation", "cad", "cfd", "finite element", "residential", "house",
    "home", "apartment", "condominium", "villa", "mansion", "cottage",
    "bedroom", "kitchen", "bathroom", "living room", "real estate", "hotel",
    "church", "cathedral", "castle", "palace", "school", "museum",
    "restaurant", "garden", "park", "forest", "tree", "flower", "leaf",
    "botanical", "zoo", "aquarium", "pet", "dog", "cat", "horse", "cow",
    "sheep", "goat", "bird", "fish", "insect", "butterfly", "wildlife",
    "nature", "portrait", "selfie", "wedding", "fashion", "artwork",
    "painting", "sculpture", "statue", "coin", "stamp", "flag",
    "coat of arms",
}

REALWORLD_QUERY_SUFFIXES = [
    "industrial site photo",
    "factory floor photo",
    "worksite equipment photo",
    "field inspection photo",
    "real world industrial equipment",
]

SOURCE_NEGATIVE_TERMS = [
    "diagram", "schematic", "drawing", "illustration", "render", "rendering",
    "cartoon", "logo", "icon", "map", "chart", "graph", "manual", "poster",
    "toy", "model", "house", "home", "residential", "garden", "tree",
    "flower", "bird", "cat", "dog", "wildlife",
]


SCENE_BANK: dict[str, dict[str, object]] = {
    "vsec_unregistered_vehicle_intrusion": {
        "domain": "visual_security",
        "tokens": "gate truck checkpoint industrial security vehicle restricted barrier access control loading dock",
        "queries": [
            "industrial facility gate truck checkpoint",
            "factory security gate truck entrance barrier",
            "warehouse loading dock gate truck access control",
            "restricted industrial road vehicle gate barrier",
            "truck at factory gate guardhouse",
            "industrial checkpoint vehicle barrier",
        ],
        "categories": ["Security gates", "Factory gates", "Access control", "Truck gates", "Industrial buildings"],
    },
    "vsec_missing_ppe_at_height": {
        "domain": "visual_security",
        "tokens": "aerial platform worker height harness scaffold construction roof edge fall arrest boom lift",
        "queries": [
            "construction worker aerial work platform harness",
            "worker boom lift industrial site harness",
            "worker at height scaffold fall arrest",
            "construction roof edge worker harness",
            "scaffold worker safety harness industrial",
            "elevated work platform worker factory",
        ],
        "categories": ["Aerial work platforms", "Fall arrest", "Construction safety", "Scaffolding", "Boom lifts"],
    },
    "vsec_forklift_overspeed_pallet_shift": {
        "domain": "visual_security",
        "tokens": "forklift pallet warehouse cargo",
        "queries": ["forklift pallet warehouse", "forklift carrying pallets", "warehouse forklift cargo"],
        "categories": ["Forklifts", "Pallets", "Warehouses"],
    },
    "vsec_crane_unsafe_swing_near_people": {
        "domain": "visual_security",
        "tokens": "crane suspended load workers construction",
        "queries": ["crane suspended load construction workers", "construction crane lifting load workers"],
        "categories": ["Cranes", "Construction cranes", "Construction workers"],
    },
    "vsec_surveillance_blind_spot_sweep": {
        "domain": "visual_security",
        "tokens": "cctv surveillance camera warehouse security aisle loading bay blind corner",
        "queries": [
            "warehouse aisle security camera view",
            "industrial cctv camera overlooking loading bay",
            "factory surveillance camera blind corner",
            "warehouse security camera aisle forklift",
            "loading dock cctv surveillance view",
            "PTZ camera ceiling warehouse",
            "dome camera factory ceiling",
            "security camera industrial building interior",
            "CCTV dome camera warehouse",
            "ceiling mounted security camera industrial",
        ],
        "categories": ["Surveillance cameras", "Security cameras", "Warehouses", "Loading docks", "CCTV cameras", "Closed-circuit television"],
    },
    "vsec_perimeter_fence_breach": {
        "domain": "visual_security",
        "tokens": "fence gate perimeter industrial barrier security mesh damaged restricted yard",
        "queries": [
            "industrial perimeter fence gate security",
            "factory security fence barrier yard",
            "industrial chain link fence gate",
            "security fence industrial site access road",
            "damaged perimeter fence industrial",
            "warehouse yard security fence",
        ],
        "categories": ["Security fences", "Perimeter fences", "Industrial fences", "Factory gates"],
    },
    "vsec_dangerous_goods_liquid_leak": {
        "domain": "visual_security",
        "tokens": "chemical liquid leak tank pipe containment industrial",
        "queries": ["chemical plant piping containment", "industrial chemical tank piping", "chemical loading area"],
        "categories": ["Chemical plants", "Chemical storage tanks", "Industrial piping"],
    },
    "vsec_pedestrian_forklift_near_miss": {
        "domain": "visual_security",
        "tokens": "forklift pedestrian warehouse lane",
        "queries": ["forklift pedestrian warehouse", "forklift warehouse worker", "factory forklift worker"],
        "categories": ["Forklifts", "Warehouses", "Factory floors"],
    },
    "vsec_smoke_alarm_evacuation": {
        "domain": "visual_security",
        "tokens": "industrial fire alarm smoke detector corridor factory emergency exit evacuation alarm strobe",
        "queries": [
            "industrial corridor fire alarm emergency exit",
            "factory fire alarm strobe corridor",
            "warehouse smoke detector emergency exit sign",
            "industrial building fire alarm pull station",
            "workshop evacuation exit alarm corridor",
            "battery room fire alarm detector",
        ],
        "categories": ["Fire alarms", "Smoke detectors", "Emergency exits", "Industrial corridors", "Fire alarm systems"],
    },
    "vsec_guard_removed_conveyor": {
        "domain": "visual_security",
        "tokens": "conveyor belt guard machine industrial pinch point roller exposed safety cover",
        "queries": [
            "industrial conveyor belt machine guard",
            "factory conveyor roller guard safety",
            "conveyor pinch point guard industrial",
            "exposed conveyor roller machine guard",
            "belt conveyor safety guard factory",
        ],
        "categories": ["Conveyor belts", "Industrial conveyors", "Machine guards", "Machine safety"],
    },
    "erob_robot_arm_precision_grasp": {
        "domain": "embodied_robotics",
        "tokens": "robot arm gripper industrial end effector workpiece picking assembly cell",
        "queries": [
            "industrial robot arm gripper workpiece",
            "robot arm picking part factory gripper",
            "robot gripper assembly cell close up",
            "robot end effector holding component",
            "industrial manipulator gripper workcell",
            "KUKA robot arm factory",
            "ABB robot arm industrial cell",
            "Fanuc robot arm manufacturing",
            "robot arm automation factory floor",
        ],
        "categories": ["Industrial robots", "Robotic arms", "Robot grippers", "End effectors", "KUKA robots", "ABB robots", "Automation"],
    },
    "erob_cobot_human_handover": {
        "domain": "embodied_robotics",
        "tokens": "collaborative robot cobot worker factory handover workstation shared table",
        "queries": [
            "collaborative robot worker workstation",
            "cobot human handover table factory",
            "human robot collaboration assembly workstation",
            "collaborative robot beside worker industrial",
            "cobot picking part with operator",
        ],
        "categories": ["Collaborative robots", "Human-robot interaction", "Industrial robots", "Assembly lines"],
    },
    "erob_tracked_robot_rubble": {
        "domain": "embodied_robotics",
        "tokens": "tracked robot crawler rubble inspection rescue pipe tunnel uneven terrain",
        "queries": [
            "tracked inspection robot rubble",
            "search rescue tracked robot debris",
            "tracked robot industrial pipe inspection",
            "crawler inspection robot tunnel",
            "tracked robot uneven terrain inspection",
            "bomb disposal tracked robot industrial",
        ],
        "categories": ["Tracked robots", "Search and rescue robots", "Inspection robots", "Robots"],
    },
    "erob_quadruped_stairs_rubble_fpv": {
        "domain": "embodied_robotics",
        "tokens": "quadruped robot stairs rubble legged industrial inspection plant tunnel",
        "queries": [
            "quadruped robot stairs inspection",
            "legged robot rubble industrial",
            "quadruped robot factory inspection",
            "robot dog industrial stairs",
            "legged robot construction site inspection",
            "quadruped robot tunnel inspection",
            "Boston Dynamics Spot robot",
            "Spot robot inspection industrial",
            "legged robot walking stairs",
            "four legged robot outdoor terrain",
        ],
        "categories": ["Quadrupedal robots", "Legged robots", "Inspection robots", "Robots", "Boston Dynamics"],
    },
    "erob_amr_warehouse_navigation": {
        "domain": "embodied_robotics",
        "tokens": "mobile robot warehouse amr autonomous pallet agv aisle shelf logistics",
        "queries": [
            "autonomous mobile robot warehouse aisle",
            "warehouse amr robot pallets shelves",
            "agv mobile robot logistics warehouse",
            "warehouse robot navigating pallet station",
            "automated guided vehicle warehouse aisle",
            "mobile robot shelf warehouse logistics",
            "Mir robot warehouse",
            "Fetch robot warehouse aisle",
            "autonomous forklift warehouse",
            "logistics robot floor shelves",
        ],
        "categories": ["Autonomous mobile robots", "Automated guided vehicles", "Warehouse robots", "Warehouses", "Mobile robots", "Logistics robots"],
    },
    "erob_light_curtain_emergency_stop": {
        "domain": "embodied_robotics",
        "tokens": "robot cell light curtain safety factory guarding emergency stop yellow safety scanner",
        "queries": [
            "robot cell light curtain safety fence",
            "industrial robot safety light curtain",
            "machine safety light curtain factory line",
            "robot workcell safety scanner emergency stop",
            "robot cell safety fence light curtain",
            "safety light barrier industrial machine",
            "optoelectronic safety barrier factory",
            "machine guarding safety fence robot",
            "robot safety enclosure factory",
            "Sick safety scanner robot cell",
        ],
        "categories": ["Light curtains", "Machine safety", "Robot safety", "Industrial robots", "Machine guarding", "Safety fences"],
    },
    "erob_robot_tool_contact_force": {
        "domain": "embodied_robotics",
        "tokens": "robot welding sanding polishing drilling tool contact industrial workpiece force",
        "queries": [
            "robot welding torch workpiece close up",
            "industrial robot sanding workpiece",
            "robot polishing tool contact surface",
            "robot drilling tool workpiece industrial",
            "robot deburring tool contact metal part",
            "robot grinding tool workpiece",
        ],
        "categories": ["Robot welding", "Robotic machining", "Industrial robots", "Robotic arms", "Grinding machines"],
    },
    "erob_multi_robot_coordination": {
        "domain": "embodied_robotics",
        "tokens": "multiple robots warehouse mobile fleet coordinated amr agv swarm automated logistics",
        "queries": [
            "multiple autonomous mobile robots warehouse",
            "warehouse robot fleet multiple amr",
            "automated guided vehicles fleet warehouse",
            "multiple warehouse robots logistics floor",
            "agv fleet factory floor robots",
            "robot fleet coordination warehouse",
        ],
        "categories": ["Autonomous mobile robots", "Warehouse robots", "Automated guided vehicles", "Mobile robots"],
    },
    "erob_gripper_failure_recovery": {
        "domain": "embodied_robotics",
        "tokens": "robot gripper suction cup vacuum end effector object industrial pick failure",
        "queries": [
            "robot suction cup gripper object",
            "industrial robot vacuum gripper workpiece",
            "robot gripper holding part close up",
            "vacuum end effector picking object",
            "robot gripper failed pick industrial",
            "suction cup robot pick place",
            "robot hand grasping part",
            "pneumatic gripper robot industrial",
            "robot vacuum cup picking",
            "end effector robot arm close up",
        ],
        "categories": ["Robot grippers", "End effectors", "Vacuum grippers", "Industrial robots", "Robotic arms", "Automation"],
    },
    "hload_dual_crawler_crane_lift": {
        "domain": "heavy_load_construction",
        "tokens": "crawler crane heavy lift construction",
        "queries": ["crawler crane heavy lift construction", "two crawler cranes lifting", "heavy lift crane construction"],
        "categories": ["Crawler cranes", "Construction cranes", "Cranes"],
    },
    "hload_wire_rope_overload_snap": {
        "domain": "heavy_load_construction",
        "tokens": "wire rope crane hook block sling sheave hoist cable tension rigging",
        "queries": [
            "crane wire rope hook block close up",
            "hoist wire rope sheave block construction",
            "crane lifting sling hook block",
            "wire rope crane rigging load",
            "construction crane cable hook block",
        ],
        "categories": ["Wire ropes", "Crane hooks", "Crane blocks", "Rigging", "Hoists"],
    },
    "hload_mining_truck_muddy_slope": {
        "domain": "heavy_load_construction",
        "tokens": "mining truck dump truck muddy road",
        "queries": ["mining truck muddy road", "haul truck mine road", "dump truck muddy construction"],
        "categories": ["Mining trucks", "Dump trucks", "Muddy roads"],
    },
    "hload_gantry_wind_disturbance": {
        "domain": "heavy_load_construction",
        "tokens": "gantry crane container yard",
        "queries": ["gantry crane container yard", "container crane terminal", "rail mounted gantry crane"],
        "categories": ["Gantry cranes", "Container cranes", "Container terminals"],
    },
    "hload_bridge_segment_alignment_drone": {
        "domain": "heavy_load_construction",
        "tokens": "bridge segment construction crane precast",
        "queries": ["bridge segment lifting crane", "precast bridge segment construction", "bridge construction crane"],
        "categories": ["Bridge construction", "Precast concrete", "Construction cranes"],
    },
    "hload_excavator_linkage_loading": {
        "domain": "heavy_load_construction",
        "tokens": "excavator bucket hydraulic arm",
        "queries": ["excavator bucket loading", "hydraulic excavator bucket", "excavator arm construction"],
        "categories": ["Excavators", "Hydraulic excavators", "Excavator buckets"],
    },
    "hload_ground_settlement_outrigger": {
        "domain": "heavy_load_construction",
        "tokens": "crane outrigger support pad ground",
        "queries": ["crane outrigger pad", "mobile crane outrigger", "crane support pad construction"],
        "categories": ["Mobile cranes", "Crane outriggers", "Construction sites"],
    },
    "hload_tunnel_pipe_burst_mud_surge": {
        "domain": "heavy_load_construction",
        "tokens": "pipe trench construction tunnel pipeline excavation muddy water underground burst",
        "queries": [
            "pipeline trench construction muddy water",
            "broken pipe construction trench water",
            "underground pipe construction excavation",
            "utility trench pipe repair muddy",
            "tunnel pipe construction water ingress",
        ],
        "categories": ["Pipeline construction", "Trenches", "Pipe laying", "Excavations"],
    },
    "hload_hoist_collision_near_structure": {
        "domain": "heavy_load_construction",
        "tokens": "hoist suspended load construction crane hook near structure scaffold building",
        "queries": [
            "construction hoist suspended load near building",
            "crane hook load near scaffold",
            "lifting load construction site structure",
            "tower crane hook block near building",
            "hoisted load close to steel structure",
        ],
        "categories": ["Hoists", "Construction cranes", "Suspended loads", "Construction sites"],
    },
    "hload_formwork_collapse_local": {
        "domain": "heavy_load_construction",
        "tokens": "formwork shoring scaffold construction",
        "queries": ["construction formwork shoring", "concrete formwork construction", "construction scaffold shoring"],
        "categories": ["Formwork", "Scaffolding", "Construction sites"],
    },
    "pdef_pcb_solder_bridge_short": {
        "domain": "precision_defect_gen",
        "tokens": "pcb circuit board solder component",
        "queries": ["pcb solder joints close up", "printed circuit board components closeup", "circuit board solder"],
        "categories": ["Printed circuit boards", "Surface-mount technology"],
    },
    "pdef_engine_endoscope_crack": {
        "domain": "precision_defect_gen",
        "tokens": "borescope turbine engine pipe inspection internal crack blade cavity endoscope",
        "queries": [
            "borescope turbine blade inspection close up",
            "aircraft engine borescope turbine blade",
            "industrial borescope pipe internal inspection",
            "endoscope view pipe wall crack",
            "borescope inspection engine blade defect",
            "internal pipe inspection camera corrosion",
        ],
        "categories": ["Borescopes", "Endoscopy", "Aircraft engine maintenance", "Turbine blades", "Pipe inspection"],
    },
    "pdef_gear_tooth_missing_wear": {
        "domain": "precision_defect_gen",
        "tokens": "gear teeth close up industrial gearbox sprocket worn chipped tooth",
        "queries": [
            "industrial gear teeth close up",
            "gear wheel teeth macro inspection",
            "worn gear tooth close up",
            "chipped gear tooth inspection",
            "gearbox gear teeth close up",
            "sprocket teeth wear closeup",
        ],
        "categories": ["Gears", "Gear wheels", "Sprockets", "Gearboxes"],
    },
    "pdef_cnc_curved_surface_cutting": {
        "domain": "precision_defect_gen",
        "tokens": "cnc milling machine tool workpiece",
        "queries": ["cnc milling machine cutting", "five axis cnc milling", "machine tool milling workpiece"],
        "categories": ["CNC machines", "Milling machines", "Machine tools"],
    },
    "pdef_cutting_fluid_spray": {
        "domain": "precision_defect_gen",
        "tokens": "cutting fluid cnc machine tool coolant nozzle spray chips milling lathe",
        "queries": [
            "cnc machine coolant nozzle cutting fluid",
            "machine tool coolant spray milling",
            "cnc milling cutting fluid chips",
            "lathe coolant nozzle workpiece",
            "metal cutting coolant spray close up",
        ],
        "categories": ["Cutting fluids", "Metalworking fluids", "CNC machines", "Machine tools"],
    },
    "pdef_weld_porosity_crack": {
        "domain": "precision_defect_gen",
        "tokens": "weld seam pipe close up bead crack porosity defect inspection steel",
        "queries": [
            "pipe weld seam close up defect",
            "weld bead crack close up inspection",
            "weld porosity defect close up",
            "steel plate weld seam macro",
            "welded joint inspection closeup",
            "pipe welding bead inspection",
        ],
        "categories": ["Weld defects", "Welded joints", "Pipe welding", "Welding inspection"],
    },
    "pdef_surface_scratch_inspection": {
        "domain": "precision_defect_gen",
        "tokens": "metal surface scratch inspection close up polished wafer bearing race defect",
        "queries": [
            "polished metal surface scratch close up",
            "machined surface scratch inspection macro",
            "bearing race scratch inspection",
            "wafer surface scratch inspection",
            "metal scratch defect closeup",
        ],
        "categories": ["Scratches", "Surface finishing", "Metal surfaces", "Bearings"],
    },
    "pdef_tube_bundle_endoscopy": {
        "domain": "precision_defect_gen",
        "tokens": "heat exchanger tube bundle tube sheet repeated pipes borescope endoscopy",
        "queries": [
            "heat exchanger tube bundle close up",
            "tube sheet heat exchanger many tubes",
            "shell tube heat exchanger tube sheet",
            "borescope inside heat exchanger tube",
            "industrial tube bundle inspection",
        ],
        "categories": ["Heat exchangers", "Tube bundles", "Tube sheets", "Borescopes"],
    },
    "pdef_connector_pin_bent": {
        "domain": "precision_defect_gen",
        "tokens": "electrical connector pins close up pin header socket bent terminal block macro",
        "queries": [
            "electrical connector pins close up macro",
            "pin header connector macro inspection",
            "bent connector pins close up",
            "terminal block pins close up",
            "electronic socket pins macro",
        ],
        "categories": ["Electrical connectors", "Connectors", "Pin headers", "Terminal blocks"],
    },
    "pdef_precision_assembly_misalignment": {
        "domain": "precision_defect_gen",
        "tokens": "bearing shaft assembly fixture precision jig alignment dial indicator",
        "queries": [
            "bearing shaft assembly fixture",
            "precision assembly jig shaft bearing",
            "machine bearing shaft alignment",
            "dial indicator shaft alignment fixture",
            "precision mechanical assembly fixture",
        ],
        "categories": ["Bearings", "Shafts", "Machine tools", "Jigs and fixtures"],
    },
    "emerg_flange_high_pressure_leak": {
        "domain": "extreme_emergency",
        "tokens": "pipe flange valve chemical plant refinery gasket bolted joint pressure piping",
        "queries": [
            "industrial pipe flange valve close up",
            "chemical plant pipe flange bolted joint",
            "refinery pipe rack valve flange",
            "pressure piping flange gasket valve",
            "industrial pipeline flange joint",
            "process plant valve station flange",
        ],
        "categories": ["Pipe flanges", "Industrial piping", "Valves", "Chemical plants", "Refineries"],
    },
    "emerg_storage_tank_flash_fire": {
        "domain": "extreme_emergency",
        "tokens": "storage tank refinery piping tank farm",
        "queries": ["storage tank farm refinery piping", "industrial storage tanks pipes", "refinery tank farm"],
        "categories": ["Storage tanks", "Tank farms", "Refineries"],
    },
    "emerg_transmission_tower_icing_collapse": {
        "domain": "extreme_emergency",
        "tokens": "transmission tower power line snow ice lattice pylon high voltage corridor",
        "queries": [
            "transmission tower snow ice power line",
            "high voltage pylon ice storm",
            "power lines ice accumulation tower",
            "electricity transmission tower winter snow",
            "lattice transmission tower snow corridor",
        ],
        "categories": ["Transmission towers", "Power lines in snow", "Ice storms", "Electric power transmission"],
    },
    "emerg_dust_explosion_confined_space": {
        "domain": "extreme_emergency",
        "tokens": "grain silo dust collector industrial",
        "queries": ["grain silo dust collector", "industrial dust collector", "grain elevator silo"],
        "categories": ["Grain silos", "Dust collectors", "Grain elevators"],
    },
    "emerg_reactor_runaway_pressure_release": {
        "domain": "extreme_emergency",
        "tokens": "chemical reactor pressure vessel valve plant",
        "queries": ["chemical reactor pressure vessel", "industrial pressure vessel valve", "chemical plant reactor"],
        "categories": ["Chemical reactors", "Pressure vessels", "Chemical plants"],
    },
    "emerg_battery_thermal_runaway": {
        "domain": "extreme_emergency",
        "tokens": "battery energy storage lithium container",
        "queries": ["battery energy storage container", "lithium battery storage system", "battery room industrial"],
        "categories": ["Battery energy storage systems", "Lithium-ion batteries", "Battery rooms"],
    },
    "emerg_tunnel_fire_smoke_layering": {
        "domain": "extreme_emergency",
        "tokens": "tunnel corridor industrial underground",
        "queries": ["industrial tunnel corridor", "underground tunnel corridor", "utility tunnel"],
        "categories": ["Tunnels", "Utility tunnels", "Underground corridors"],
    },
    "emerg_crane_load_drop_evacuation": {
        "domain": "extreme_emergency",
        "tokens": "crane suspended load construction yard",
        "queries": ["crane suspended load construction yard", "construction crane lifting load", "crane load construction site"],
        "categories": ["Cranes", "Construction cranes", "Suspended loads"],
    },
    "emerg_cooling_tower_plume_failure": {
        "domain": "extreme_emergency",
        "tokens": "cooling tower steam plume power plant",
        "queries": ["cooling tower steam plume", "power plant cooling tower", "cooling tower plume"],
        "categories": ["Cooling towers", "Power plants", "Steam plumes"],
    },
    "emerg_dam_or_retaining_wall_breach": {
        "domain": "extreme_emergency",
        "tokens": "retaining wall dam containment berm industrial",
        "queries": ["retaining wall industrial", "containment berm wall", "dam retaining wall"],
        "categories": ["Retaining walls", "Dams", "Earthworks"],
    },
    "emerg_hot_work_spark_combustible_fire": {
        "domain": "extreme_emergency",
        "tokens": "industrial welding hot work sparks workshop combustible fire safety",
        "queries": ["industrial welding sparks workshop", "hot work welding sparks factory", "welder sparks industrial site"],
        "categories": ["Welding", "Welders", "Hot work", "Industrial fires"],
    },
    "emerg_smoke_evacuation_route_visibility": {
        "domain": "extreme_emergency",
        "tokens": "industrial corridor tunnel stairwell emergency exit smoke evacuation passage",
        "queries": ["industrial corridor emergency exit", "tunnel evacuation passage", "factory stairwell emergency exit"],
        "categories": ["Emergency exits", "Tunnels", "Industrial corridors", "Stairwells"],
    },
    "erob_agv_rollup_door_interlock": {
        "domain": "embodied_robotics",
        "tokens": "warehouse agv automated guided vehicle roll up door loading dock barrier",
        "queries": ["warehouse agv loading dock door", "automated guided vehicle warehouse door", "warehouse roll up door forklift"],
        "categories": ["Automated guided vehicles", "Loading docks", "Warehouse doors", "Warehouses"],
    },
    "erob_amr_charger_smoke_abort": {
        "domain": "embodied_robotics",
        "tokens": "warehouse autonomous mobile robot agv charging station battery charger",
        "queries": ["warehouse amr charging station", "agv battery charging station factory", "mobile robot charger warehouse"],
        "categories": ["Automated guided vehicles", "Battery chargers", "Warehouse robots", "Warehouses"],
    },
    "erob_cobot_safety_scanner_slowdown": {
        "domain": "embodied_robotics",
        "tokens": "collaborative robot cobot worker safety scanner factory workstation",
        "queries": [
            "collaborative robot worker safety scanner",
            "cobot factory workstation worker",
            "robot workcell safety scanner",
            "UR robot cobot worker beside",
            "Universal Robots cobot assembly",
            "cobot human collaboration workstation",
            "human robot shared workspace factory",
            "collaborative robot arm worker side",
        ],
        "categories": ["Collaborative robots", "Machine safety", "Industrial robots", "Assembly lines", "Universal Robots", "Human-robot interaction"],
    },
    "hload_blind_lift_spotter_view": {
        "domain": "heavy_load_construction",
        "tokens": "crane suspended load spotter signal worker blind lift construction",
        "queries": ["crane lift spotter signal worker", "construction crane suspended load worker", "rigger signaling crane lift"],
        "categories": ["Cranes", "Riggers", "Construction workers", "Hand signals"],
    },
    "hload_sling_angle_center_of_gravity": {
        "domain": "heavy_load_construction",
        "tokens": "crane sling spreader beam rigging suspended load lifting",
        "queries": ["crane sling suspended load rigging", "spreader beam lifting sling", "construction lift rigging slings"],
        "categories": ["Rigging", "Cranes", "Slings", "Lifting equipment"],
    },
    "pdef_flange_seal_micro_leak": {
        "domain": "precision_defect_gen",
        "tokens": "industrial pipe flange gasket bolted joint valve close up",
        "queries": ["industrial pipe flange gasket close up", "bolted pipe flange valve", "pipeline flange joint close up"],
        "categories": ["Flanges", "Industrial piping", "Valves", "Gaskets"],
    },
    "pdef_gauge_level_valve_anomaly": {
        "domain": "precision_defect_gen",
        "tokens": "industrial pressure gauge level gauge valve tank instrumentation close up",
        "queries": ["industrial pressure gauge valve close up", "tank level gauge valve", "industrial instrumentation gauge piping"],
        "categories": ["Pressure gauges", "Valves", "Industrial instrumentation", "Storage tanks"],
    },
    "vsec_conveyor_jam_loto_clearance": {
        "domain": "visual_security",
        "tokens": "industrial conveyor belt roller machine guard factory maintenance lockout",
        "queries": ["industrial conveyor belt roller guard", "factory conveyor maintenance", "belt conveyor machine guard"],
        "categories": ["Conveyor belts", "Industrial conveyors", "Machine guards", "Machine safety"],
    },
    "vsec_electrical_cabinet_smoke_isolation": {
        "domain": "visual_security",
        "tokens": "industrial electrical cabinet switchgear control panel factory close up",
        "queries": ["industrial electrical cabinet switchgear", "factory electrical control panel cabinet", "electrical switchgear room cabinet"],
        "categories": ["Electrical cabinets", "Switchgear", "Control panels", "Electrical rooms"],
    },
}


def _url_json(url: str, params: dict[str, str], sleep_s: float, timeout: float) -> dict:
    if sleep_s:
        time.sleep(sleep_s)
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _commons_search(query: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": _search_query(query),
        "gsrnamespace": "6",
        "gsrlimit": str(min(limit, 50)),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    data = _url_json(COMMONS_API, params, sleep_s, timeout)
    out = []
    for page in data.get("query", {}).get("pages", {}).values():
        infos = page.get("imageinfo") or []
        if infos:
            out.append({"provider": "commons_search", "title": page.get("title", ""), "info": infos[0], "source_query": query})
    return out


def _commons_category(category: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmnamespace": "6",
        "gcmtype": "file",
        "gcmlimit": str(min(limit, 50)),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    data = _url_json(COMMONS_API, params, sleep_s, timeout)
    out = []
    for page in data.get("query", {}).get("pages", {}).values():
        infos = page.get("imageinfo") or []
        if infos:
            out.append({"provider": "commons_category", "title": page.get("title", ""), "info": infos[0], "source_query": category})
    return out


def _openverse_search(query: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    params = {"q": _search_query(query), "page_size": str(min(limit, 20)), "mature": "false"}
    data = _url_json(OPENVERSE_API, params, sleep_s, timeout)
    out = []
    for item in data.get("results", []):
        image_url = str(item.get("url") or item.get("thumbnail") or "")
        if not image_url:
            continue
        license_url = str(item.get("license_url") or "")
        info = {
            "url": image_url,
            "thumburl": image_url,
            "descriptionurl": str(item.get("foreign_landing_url") or item.get("url") or ""),
            "width": int(item.get("width") or 0),
            "height": int(item.get("height") or 0),
            "mime": item.get("mime_type") or "",
            "extmetadata": {
                "LicenseShortName": {"value": str(item.get("license") or "")},
                "UsageTerms": {"value": str(item.get("license_version") or "")},
                "License": {"value": license_url},
            },
        }
        out.append({"provider": "openverse", "title": str(item.get("title") or ""), "info": info, "source_query": query})
    return out


def _loc_search(query: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    params = {
        "fo": "json",
        "c": str(min(limit, 100)),
        "q": _search_query(query),
        "fa": "online-format:image",
    }
    data = _url_json(LOC_API, params, sleep_s, timeout)
    out = []
    for item in data.get("results", []):
        image_urls = item.get("image_url") or []
        if isinstance(image_urls, str):
            image_urls = [image_urls]
        image_url = ""
        for url in reversed(image_urls):
            if isinstance(url, str) and url.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_url = url
                break
        if not image_url and image_urls:
            image_url = str(image_urls[-1])
        if not image_url:
            continue
        rights = " ".join(str(item.get(key, "")) for key in ("rights", "rights_advisory", "access_restricted"))
        if rights and not any(hint in rights.lower() for hint in ("no known", "public domain", "unrestricted", "not restricted")):
            continue
        info = {
            "url": image_url,
            "thumburl": image_url,
            "descriptionurl": str(item.get("url") or ""),
            "width": 0,
            "height": 0,
            "mime": "image/jpeg",
            "extmetadata": {
                "LicenseShortName": {"value": "LOC public/no-known-restrictions"},
                "UsageTerms": {"value": rights or "Library of Congress record"},
                "License": {"value": str(item.get("url") or "")},
            },
        }
        out.append({
            "provider": "loc",
            "title": str(item.get("title") or ""),
            "info": info,
            "source_query": query,
        })
    return out


def _nara_search(query: str, limit: int, sleep_s: float, timeout: float) -> list[dict]:
    params = {
        "q": _search_query(query),
        "rows": str(min(limit, 100)),
        "resultTypes": "item",
        "objectType": "Photographs and other Graphic Materials",
        "availableOnline": "true",
    }
    data = _url_json(NARA_API, params, sleep_s, timeout)
    hits = data.get("body", {}).get("hits", {}).get("hits", [])
    out = []
    for hit in hits:
        item = hit.get("_source", {})
        desc = item.get("description", {})
        title = ""
        if isinstance(desc, dict):
            title = str(desc.get("title") or desc.get("scopeAndContentNote") or "")
        objects = item.get("objects") or []
        if isinstance(objects, dict):
            objects = [objects]
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            image_url = str(obj.get("file", {}).get("@url") if isinstance(obj.get("file"), dict) else obj.get("url") or "")
            if not image_url:
                image_url = str(obj.get("thumbnail", {}).get("@url") if isinstance(obj.get("thumbnail"), dict) else "")
            if not image_url:
                continue
            info = {
                "url": image_url,
                "thumburl": image_url,
                "descriptionurl": str(desc.get("naId", "") if isinstance(desc, dict) else ""),
                "width": 0,
                "height": 0,
                "mime": "image/jpeg",
                "extmetadata": {
                    "LicenseShortName": {"value": "NARA public archive"},
                    "UsageTerms": {"value": "National Archives Catalog"},
                    "License": {"value": "https://catalog.archives.gov/"},
                },
            }
            out.append({
                "provider": "nara",
                "title": title,
                "info": info,
                "source_query": query,
            })
            break
    return out


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) >= 3}


def _search_query(query: str) -> str:
    negatives = " ".join(f'-"{term}"' if " " in term else f"-{term}" for term in SOURCE_NEGATIVE_TERMS)
    return f"{query} {negatives}".strip()


def _scene_queries(scene: str) -> list[str]:
    bank = SCENE_BANK[scene]
    queries = [str(query) for query in bank["queries"]]
    tokens = str(bank.get("tokens") or "").strip()
    if tokens:
        queries.append(tokens)
    expanded = []
    for query in queries:
        expanded.append(query)
        words = query.lower()
        if not any(term in words for term in ("photo", "factory", "industrial", "worksite", "site")):
            for suffix in REALWORLD_QUERY_SUFFIXES:
                expanded.append(f"{query} {suffix}")
    compact = []
    for query in expanded:
        query = re.sub(r"\s+", " ", query).strip()
        if query and query.lower() not in {old.lower() for old in compact}:
            compact.append(query)
    return compact


def _source_ok(text: str) -> tuple[bool, str]:
    lowered = text.lower()
    for term in sorted(BLOCKED_TERMS, key=len, reverse=True):
        if " " in term and term in lowered:
            return False, "blocked_term:" + term.replace(" ", "_")
    tokens = _tokens(text)
    blocked = sorted(tokens & BLOCKED_TERMS)
    if blocked:
        return False, "blocked_term:" + blocked[0]
    for hint in (".pdf", ".djvu", "/pdf/", "/book/", "/books/", "/poster/", "/diagram/"):
        if hint in lowered:
            return False, "blocked_url:" + hint
    return True, ""


def _score(scene: str, candidate: dict) -> int:
    bank = SCENE_BANK[scene]
    source_text = " ".join([
        str(candidate.get("title", "")),
        str(candidate.get("source_query", "")),
        str(candidate["info"].get("descriptionurl", "")),
        str(candidate["info"].get("url", "")),
    ])
    return len(_tokens(str(bank["tokens"])) & _tokens(source_text))


def _image_url(info: dict) -> str:
    return str(info.get("thumburl") or info.get("url") or "")


def _bit_count(value: int) -> int:
    return value.bit_count() if hasattr(value, "bit_count") else bin(value).count("1")


def _near_duplicate(ahash: str, seen_hashes: list[str], max_distance: int) -> bool:
    return any(_bit_count(_hamming_hex(ahash, old)) <= max_distance for old in seen_hashes)


def _hashes(root: Path) -> list[str]:
    hashes = []
    if not root.exists():
        return hashes
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                hashes.append(_average_hash(path))
            except Exception:
                pass
    return hashes


def _scene_count(candidate_root: Path, scene: str) -> int:
    if not candidate_root.exists():
        return 0
    return sum(
        1 for path in candidate_root.rglob(f"{scene}/*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _next_path(output_dir: Path, domain: str, scene: str, suffix: str) -> Path:
    scene_dir = output_dir / domain / scene
    scene_dir.mkdir(parents=True, exist_ok=True)
    max_idx = 0
    for path in scene_dir.iterdir():
        if path.is_file() and path.stem.startswith("ref_"):
            try:
                max_idx = max(max_idx, int(path.stem.split("_", 1)[1]))
            except ValueError:
                pass
    return scene_dir / f"ref_{max_idx + 1:02d}{suffix.lower()}"


def _write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def _load_scenes(args: argparse.Namespace) -> list[str]:
    scenes = list(SCENE_BANK)
    if args.scenes_file:
        data = json.loads(Path(args.scenes_file).read_text(encoding="utf-8"))
        wanted = set(data["scenes"] if isinstance(data, dict) else data)
        scenes = [scene for scene in scenes if scene in wanted]
    if args.domains:
        domains = {item.strip() for item in args.domains.split(",") if item.strip()}
        scenes = [scene for scene in scenes if str(SCENE_BANK[scene]["domain"]) in domains]
    if args.shards > 1:
        scenes = [scene for idx, scene in enumerate(scenes) if idx % args.shards == args.shard_index]
    return scenes


def _iter_candidates(scene: str, args: argparse.Namespace) -> tuple[list[dict], list[str]]:
    bank = SCENE_BANK[scene]
    candidates = []
    errors = []
    if "commons" in args.providers:
        for category in bank["categories"]:
            try:
                candidates.extend(_commons_category(str(category), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"commons_category:{category}:{exc}")
        for query in _scene_queries(scene):
            try:
                candidates.extend(_commons_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"commons_search:{query}:{exc}")
    if "openverse" in args.providers:
        for query in _scene_queries(scene):
            try:
                candidates.extend(_openverse_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"openverse:{query}:{exc}")
    if "loc" in args.providers:
        for query in _scene_queries(scene):
            try:
                candidates.extend(_loc_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"loc:{query}:{exc}")
    if "nara" in args.providers:
        for query in _scene_queries(scene):
            try:
                candidates.extend(_nara_search(str(query), args.limit, args.sleep, args.timeout))
            except Exception as exc:
                errors.append(f"nara:{query}:{exc}")
    return candidates, errors


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    manifest = Path(args.manifest)
    candidate_root = Path(args.candidate_root)
    seen_hashes = _hashes(Path("dataset/images")) + _hashes(candidate_root) + _hashes(output_dir)
    rows: list[dict[str, str]] = []
    accepted_total = 0

    for scene in _load_scenes(args):
        domain = str(SCENE_BANK[scene]["domain"])
        current = _scene_count(candidate_root, scene)
        if current >= args.target_per_scene:
            continue
        accepted_scene = 0
        needed = args.target_per_scene - current
        candidates, errors = _iter_candidates(scene, args)
        for error in errors:
            rows.append({"status": "search_error", "scene": scene, "domain": domain, "reason": error})
            _write_manifest(rows, manifest)
        if not candidates:
            continue
        candidates.sort(key=lambda item: _score(scene, item), reverse=True)
        for candidate in candidates:
            if accepted_scene >= needed or accepted_total >= args.target_new:
                break
            info = candidate["info"]
            image_url = _image_url(info)
            source_url = str(info.get("descriptionurl", ""))
            title = str(candidate.get("title", ""))
            row = {
                "status": "rejected",
                "reason": "",
                "scene": scene,
                "domain": domain,
                "provider": str(candidate.get("provider", "")),
                "source_query": str(candidate.get("source_query", "")),
                "source_title": title,
                "source_url": source_url,
                "image_url": image_url,
                "score": str(_score(scene, candidate)),
                "local_path": "",
                "width": str(info.get("width", "")),
                "height": str(info.get("height", "")),
            }
            ok, reason = _source_ok(" ".join([title, source_url, image_url]))
            if not ok:
                row["reason"] = reason
                rows.append(row)
                _write_manifest(rows, manifest)
                continue
            if int(row["score"]) < args.min_score:
                row["reason"] = "score_below_min"
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
            if not _mime_ok(str(info.get("mime", ""))):
                row["reason"] = "blocked_mime"
                rows.append(row)
                _write_manifest(rows, manifest)
                continue
            if not _url_ok(source_url) or not _url_ok(image_url):
                row["reason"] = "blocked_url"
                rows.append(row)
                _write_manifest(rows, manifest)
                continue
            source_width = int(info.get("width", 0) or 0)
            source_height = int(info.get("height", 0) or 0)
            if (
                source_width > 0
                and source_height > 0
                and (source_width < args.min_width or source_height < args.min_height)
            ):
                row["reason"] = "source_resolution_below_min"
                rows.append(row)
                _write_manifest(rows, manifest)
                continue
            suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
            if suffix not in IMAGE_SUFFIXES:
                suffix = ".jpg"
            dst = _next_path(output_dir, domain, scene, suffix)
            try:
                _download(image_url, dst)
                with Image.open(dst) as image:
                    image.verify()
                metrics = _image_metrics(dst)
                if metrics["width"] < args.min_width or metrics["height"] < args.min_height:
                    dst.unlink(missing_ok=True)
                    row["reason"] = "downloaded_resolution_below_min"
                    rows.append(row)
                    _write_manifest(rows, manifest)
                    continue
                if metrics["laplacian_var"] < args.min_laplacian:
                    dst.unlink(missing_ok=True)
                    row["reason"] = "too_blurry"
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
            accepted_scene += 1
            accepted_total += 1
            row.update({
                "status": "accepted",
                "reason": "accepted",
                "local_path": dst.as_posix(),
                "width": str(metrics["width"]),
                "height": str(metrics["height"]),
                "laplacian_var": f"{metrics['laplacian_var']:.2f}",
            })
            rows.append(row)
            _write_manifest(rows, manifest)
            print(f"accepted\t{accepted_total}\t{scene}\t{dst.as_posix()}", flush=True)
        if accepted_total >= args.target_new:
            break
    _write_manifest(rows, manifest)
    print(f"accepted_total={accepted_total}")
    print(manifest.as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", default="dataset/images_candidates/scene_expansion_bulk_resume_400")
    parser.add_argument("--output-dir", default="dataset/images_candidates/scene_expansion_bulk_resume_400/worker_targeted_v2")
    parser.add_argument("--manifest", default="reports/scene_expansion_bulk_resume_400/targeted_v2.csv")
    parser.add_argument("--target-per-scene", type=int, default=8)
    parser.add_argument("--target-new", type=int, default=120)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--providers", default="commons,openverse")
    parser.add_argument("--domains", default="")
    parser.add_argument("--scenes-file", default="")
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--min-width", type=int, default=900)
    parser.add_argument("--min-height", type=int, default=600)
    parser.add_argument("--min-laplacian", type=float, default=35.0)
    parser.add_argument("--duplicate-hamming-distance", type=int, default=4)
    args = parser.parse_args()
    args.providers = {item.strip() for item in args.providers.split(",") if item.strip()}
    run(args)


if __name__ == "__main__":
    main()
