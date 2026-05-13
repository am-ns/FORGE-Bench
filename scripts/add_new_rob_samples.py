"""Add rob_021-rob_028 to samples.json with full metadata."""
import json
from pathlib import Path

raw = json.loads(Path("dataset/annotations/samples.json").read_text(encoding="utf-8"))
samples = raw["samples"]

# Check none already exist
existing = {s["task_id"] for s in samples}

new_samples = [
    {
        "task_id": "rob_021",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_021.jpg",
        "prompt": "Camera performs a slow dolly-in approach toward a NAO humanoid robot in a laboratory, revealing the multi-segment neck joint, spherical shoulder actuators, ear speaker grilles, and chest panel geometry. Camera at robot eye level, smooth approach. No rotation. No zoom.",
        "vfa_target": "dolly_in_2x",
        "motion_type": "dolly",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "kinematic_chain_integrity",
        "difficulty_profile": {"IKA": "medium", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "medium"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["shoulder_joint_hemispherical_geometry", "neck_joint_alignment", "chest_panel_proportions"]},
        "ika_questions": [
            {"id": "q1", "text": "Do the spherical shoulder joint housings maintain their correct hemispherical geometry without non-physical flattening during the dolly approach?", "answer": "yes"},
            {"id": "q2", "text": "Does the multi-DOF neck joint linkage maintain correct concentric ring alignment throughout the motion?", "answer": "yes"},
            {"id": "q3", "text": "Does the chest panel geometry remain dimensionally consistent with correct proportions from first to last frame?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_022",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_022.jpg",
        "prompt": "Camera orbits clockwise 45 degrees around a KUKA IR161 6-axis industrial robot arm in a factory cell, showing the shoulder joint housing, upper arm link, elbow joint, forearm, and cable harness routing. Slow, constant-radius orbit at arm mid-height. No zoom.",
        "vfa_target": "orbit_cw_45deg",
        "motion_type": "orbit",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "kinematic_chain_integrity",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["joint_housing_count", "cable_harness_routing", "base_rotation_axis"]},
        "ika_questions": [
            {"id": "q1", "text": "Do the six rotary joint housings maintain their correct circular cross-section geometry without deformation from first to last frame?", "answer": "yes"},
            {"id": "q2", "text": "Is the cable harness routing preserved along the arm without non-physical intersection or disappearance during the orbit?", "answer": "yes"},
            {"id": "q3", "text": "Does the base rotation-axis housing maintain geometrically consistent proportions throughout the orbit?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_023",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_023.jpg",
        "prompt": "Camera orbits clockwise 45 degrees around a PR2 mobile manipulation robot showing the dual 7-DOF arm configuration with both arms extended, sensor head with stereo cameras, and mobile base platform. Static scene, even orbit at torso height. No zoom.",
        "vfa_target": "orbit_cw_45deg",
        "motion_type": "orbit",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "bilateral_symmetry",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["dual_arm_bilateral_symmetry", "sensor_head_mounting", "forearm_link_proportions"]},
        "ika_questions": [
            {"id": "q1", "text": "Do both wrist roll joint housings maintain bilateral geometric symmetry without one arm drifting relative to the other throughout the orbit?", "answer": "yes"},
            {"id": "q2", "text": "Does the sensor head mounting geometry remain consistent without lateral drift or non-physical rotation?", "answer": "yes"},
            {"id": "q3", "text": "Do the forearm link proportions maintain bilateral consistency from the first to last frame?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_024",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_024.jpg",
        "prompt": "Camera pans laterally left-to-right past a KUKA industrial robot arm performing a writing-demonstration task, showing the tool-center-point, wrist joint articulation geometry, link proportions, and servo housing details. Camera at tool level. Smooth horizontal pan. No zoom.",
        "vfa_target": "horizontal_pan_lr",
        "motion_type": "pan",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "kinematic_chain_integrity",
        "difficulty_profile": {"IKA": "medium", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "medium"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["end_effector_geometry", "wrist_joint_cross_section", "link_bending_constraint"]},
        "ika_questions": [
            {"id": "q1", "text": "Does the end-effector tool geometry maintain consistent proportions without non-physical distortion throughout the pan?", "answer": "yes"},
            {"id": "q2", "text": "Do the wrist joint servo housings maintain their correct circular cross-section without deformation?", "answer": "yes"},
            {"id": "q3", "text": "Is the link-to-joint connection geometry preserved throughout the pan without non-physical bending along link mid-sections?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_025",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_025.jpg",
        "prompt": "Camera pans slowly left-to-right past an Ekso NR lower-limb exoskeleton, revealing the hip joint actuator housing, knee actuator assembly with servo motor, cabling harness routing along the structural frame, and foot platform interface geometry. Camera at knee height. No zoom.",
        "vfa_target": "horizontal_pan_lr",
        "motion_type": "pan",
        "topology_type": "flexible",
        "primary_topology": "flexible",
        "sub_topology": "cable_hose",
        "failure_target": "cable_continuity",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "cable_hose",
                                    "key_invariants": ["knee_actuator_housing_geometry", "cable_harness_continuity", "frame_parallelism"]},
        "ika_questions": [
            {"id": "q1", "text": "Does the knee joint actuator housing maintain its correct geometry without non-physical flattening throughout the pan?", "answer": "yes"},
            {"id": "q2", "text": "Is the cable harness routing preserved along the structural frame without topology merge or disappearance during the pan?", "answer": "yes"},
            {"id": "q3", "text": "Do the structural frame guide rails maintain consistent parallelism without non-physical convergence or crossing?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_026",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_026.jpg",
        "prompt": "Camera orbits clockwise 45 degrees around a Boston Dynamics Spot quadruped robot in static standing pose, showing the hip abduction joints, upper leg actuators, knee joints, lower leg links, and foot pads. Slow, constant-radius orbit at chassis height. No zoom.",
        "vfa_target": "orbit_cw_45deg",
        "motion_type": "orbit",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "kinematic_chain_integrity",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["quadruped_leg_count", "hip_joint_geometry", "bilateral_leg_symmetry"]},
        "ika_questions": [
            {"id": "q1", "text": "Do all four leg assemblies maintain geometrically consistent joint housing proportions from first to last frame?", "answer": "yes"},
            {"id": "q2", "text": "Does the hip abduction joint housing maintain its correct circular cross-section geometry throughout the orbit?", "answer": "yes"},
            {"id": "q3", "text": "Is bilateral symmetry between the left and right leg pairs preserved in the final frame without one side drifting?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_027",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_027.jpg",
        "prompt": "Camera performs a slow crane rise from table level to overhead revealing a laparoscopic surgical robot showing the multi-arm instrument mounting, cable routing along each arm, wrist mechanism geometry, and sterile interface. Smooth, even rise. No rotation.",
        "vfa_target": "crane_up_30deg",
        "motion_type": "crane",
        "topology_type": "flexible",
        "primary_topology": "flexible",
        "sub_topology": "cable_hose",
        "failure_target": "cable_continuity",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "cable_hose",
                                    "key_invariants": ["instrument_arm_count", "cable_routing_continuity", "wrist_mechanism_geometry"]},
        "ika_questions": [
            {"id": "q1", "text": "Do the cable bundles at each arm-to-instrument junction maintain their routing without intersection or topology merge?", "answer": "yes"},
            {"id": "q2", "text": "Are the instrument arm mounting brackets consistent in both count and relative positioning throughout the crane rise?", "answer": "yes"},
            {"id": "q3", "text": "Does the wrist mechanism linkage geometry maintain correct proportional preservation without non-physical deformation?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
    {
        "task_id": "rob_028",
        "domain": "robotics",
        "image_path": "dataset/images/robotics/rob_028.jpg",
        "prompt": "Camera orbits counterclockwise 45 degrees around a PackBot EOD robot showing the 4-DOF manipulator arm joints, tracked chassis geometry, gripper mechanism, and cable conduit routing along the arm. Slow orbit at arm mid-height on flat terrain. No zoom.",
        "vfa_target": "orbit_ccw_45deg",
        "motion_type": "orbit",
        "topology_type": "kinematic",
        "primary_topology": "kinematic",
        "sub_topology": "articulated",
        "failure_target": "kinematic_chain_integrity",
        "difficulty_profile": {"IKA": "hard", "TC": "medium", "PP": "medium", "VF": "medium", "GI": "hard"},
        "constraint_annotations": {"topology_class": "articulated",
                                    "key_invariants": ["manipulator_arm_link_proportions", "track_tread_periodicity", "gripper_jaw_geometry"]},
        "ika_questions": [
            {"id": "q1", "text": "Does the manipulator arm maintain correct proportional link lengths throughout the orbit without non-physical elongation?", "answer": "yes"},
            {"id": "q2", "text": "Do the track tread segments maintain their correct pitch periodicity without topology merge during the orbit?", "answer": "yes"},
            {"id": "q3", "text": "Is the gripper jaw geometry preserved without non-physical deformation or asymmetry in the final frame?", "answer": "yes"},
        ],
        "sensitivity_variants": [],
    },
]

added = 0
for ns in new_samples:
    if ns["task_id"] not in existing:
        samples.append(ns)
        added += 1
    else:
        print(f"SKIP {ns['task_id']} (already exists)")

raw["samples"] = samples
Path("dataset/annotations/samples.json").write_text(
    json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
)

total = len(samples)
robotics = sum(1 for s in samples if s["domain"] == "robotics")
manufacturing = sum(1 for s in samples if s["domain"] == "manufacturing")
print(f"Added {added} new samples")
print(f"Total: {total}  robotics: {robotics}  manufacturing: {manufacturing}")
