#!/usr/bin/env python3
"""Renumber formal image library and refresh sample prompts from blueprint.

This script is intentionally conservative:
- it only uses scenes declared in dataset/annotations/SCENE_BLUEPRINT.md;
- it never invents new scenario text;
- if a sample references a deleted image, it reassigns that sample to an
  existing image from the same scene in round-robin order.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
BLUEPRINT_PATH = ROOT / "dataset" / "annotations" / "SCENE_BLUEPRINT.md"
IMAGES_ROOT = ROOT / "dataset" / "images"
REPORT_DIR = ROOT / "reports" / "image_library_renumber"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

DOMAIN_PREFIX = {
    "visual_security": "vsec",
    "embodied_robotics": "erob",
    "heavy_load_construction": "hload",
    "precision_defect_gen": "pdef",
    "extreme_emergency": "emerg",
}

HEADING_DOMAIN = {
    "Visual Security": "visual_security",
    "Embodied Robotics": "embodied_robotics",
    "Heavy Load Construction": "heavy_load_construction",
    "Precision Defect Generation": "precision_defect_gen",
    "Extreme Emergency": "extreme_emergency",
}

ACTION_BY_TASK = {
    "rigid_body_kinematics_and_coupling": (
        "Show the requested rigid mechanism or load interaction with all links, "
        "joints, supports, contact points, and load paths staying physically coupled."
    ),
    "topology_mutation_and_failure": (
        "Generate only the requested local break, defect, deformation, missing "
        "element, or structural failure while untouched regions remain locked."
    ),
    "fluid_dynamics_and_thermodynamics": (
        "Show the fluid, vapor, smoke, flame, heat, pressure release, or spray "
        "evolving with plausible direction, gravity, diffusion, and containment."
    ),
    "spatial_exploration_and_viewpoint": (
        "Execute the requested camera or embodied viewpoint motion while keeping "
        "equipment identity, spatial scale, and visible geometry stable."
    ),
    "industrial_logic_and_compliance": (
        "Show the violation or trigger followed by the correct industrial response "
        "such as alarm, braking, stop, evacuation, lockout, or escalation."
    ),
}

AXIS_CHECKS = {
    "industrial_logic_and_fact_alignment": (
        "use state-machine style reasoning to verify causal closure, conditional "
        "triggers such as alarms or braking, compliance state, equipment roles, "
        "personnel/vehicle states, and industrial fact progression"
    ),
    "geometric_integrity": (
        "preserve topology, rigid joints, load-bearing members, joint centers, dense "
        "periodic counts and spacing, local defect boundaries, component counts, and "
        "spatial relationships"
    ),
    "physical_plausibility": (
        "obey gravity, contact, rigid-body coupling, load paths, pressure direction, "
        "fluid diffusion, heat/flame propagation, and feasible emergency dynamics"
    ),
    "temporal_consistency": (
        "maintain object identity, material state, background, local event state, and "
        "cause-effect continuity without flicker, melting, role switching, or "
        "untriggered deformation"
    ),
    "reference_and_motion_fidelity": (
        "execute the requested camera or viewpoint control while locking the reference "
        "identity, perspective, non-mutated regions, and background; apply static-video "
        "gating and region-isolated fidelity where relevant"
    ),
}


def clean(text: str) -> str:
    return " ".join(text.replace("`", "").split()).strip().rstrip(".")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_blueprint(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    current_domain = ""
    pattern = re.compile(
        r"^\| `(?P<scene>[^`]+)` \| `(?P<task>[^`]+)` \| (?P<samples>\d+) \| "
        r"(?P<requirement>.*?) \| (?P<example>.*?) \|$"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_domain = HEADING_DOMAIN.get(line[3:].strip(), current_domain)
            continue
        match = pattern.match(line)
        if not match:
            continue
        scene_id = match.group("scene")
        rows[scene_id] = {
            "scene_id": scene_id,
            "domain": current_domain,
            "task_category": match.group("task"),
            "image_requirement": clean(match.group("requirement")),
            "scenario": clean(match.group("example")),
        }
    return rows


def image_sort_key(path: Path) -> tuple[int, int, str]:
    stem = path.stem.lower()
    match = re.search(r"(?:ref|feishu|img|image|candidate)[_\- ]?(\d+)$", stem)
    if match:
        return (0, int(match.group(1)), path.name.lower())
    match = re.search(r"(\d+)", stem)
    if match:
        return (1, int(match.group(1)), path.name.lower())
    return (2, 9999, path.name.lower())


def scene_images(scene_dir: Path) -> list[Path]:
    if not scene_dir.exists():
        return []
    return sorted(
        [p for p in scene_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=image_sort_key,
    )


def renumber_images(blueprint: dict[str, dict], dry_run: bool) -> tuple[dict[str, str], dict[str, list[str]], list[dict]]:
    old_to_new: dict[str, str] = {}
    images_by_scene: dict[str, list[str]] = {}
    rows: list[dict] = []

    for scene_id, row in blueprint.items():
        scene_dir = IMAGES_ROOT / row["domain"] / scene_id
        images = scene_images(scene_dir)
        temp_pairs = []
        final_pairs = []
        for index, src in enumerate(images, 1):
            temp = scene_dir / f".__renumber_tmp_{index:04d}{src.suffix.lower()}"
            final = scene_dir / f"ref_{index:02d}{src.suffix.lower()}"
            temp_pairs.append((src, temp))
            final_pairs.append((temp, final, src))

        if not dry_run:
            for src, temp in temp_pairs:
                if src != temp:
                    src.rename(temp)
            for temp, final, _src in final_pairs:
                if temp != final:
                    temp.rename(final)

        final_rels: list[str] = []
        for temp, final, src in final_pairs:
            old_rel = rel(src)
            new_rel = rel(final)
            old_to_new[old_rel] = new_rel
            final_rels.append(new_rel)
            rows.append(
                {
                    "scene_id": scene_id,
                    "domain": row["domain"],
                    "old_image_path": old_rel,
                    "new_image_path": new_rel,
                    "changed": str(old_rel != new_rel).lower(),
                }
            )
        images_by_scene[scene_id] = final_rels
    return old_to_new, images_by_scene, rows


def motion(task_category: str, variant: int) -> tuple[str, float | str, str]:
    if task_category == "industrial_logic_and_compliance":
        return "static", 0.0, "hold a fixed monitoring view; no camera movement"
    if task_category == "topology_mutation_and_failure":
        return "dolly", 1.5, "perform a controlled dolly-in toward the local defect or failure region"
    if task_category == "fluid_dynamics_and_thermodynamics":
        options = [
            ("static", 0.0, "hold a fixed process-safety view"),
            ("pan", "horizontal_pan_lr", "perform a slow horizontal pan following the flow or plume"),
        ]
        return options[variant % len(options)]
    if task_category == "spatial_exploration_and_viewpoint":
        options = [
            ("pan", "horizontal_pan_lr", "perform a smooth left-to-right inspection pan"),
            ("orbit", 45.0, "perform a controlled orbit around the inspection subject"),
            ("dolly", 1.5, "perform a slow dolly-in revealing the inspection target"),
        ]
        return options[variant % len(options)]
    options = [
        ("orbit", 45.0, "perform a smooth constant-radius orbit around the subject"),
        ("pan", "horizontal_pan_lr", "perform a slow horizontal pan while the mechanism operates"),
    ]
    return options[variant % len(options)]


def build_prompts(sample: dict, row: dict, variant: int) -> tuple[str, str, str, float | str, str]:
    task_category = row["task_category"]
    motion_type, motion_target, motion_text = motion(task_category, variant)
    scenario = row["scenario"]
    subject = sample.get("reference_subject") or row["scene_id"].replace("_", " ")
    weights = sample.get("axis_weights") or {}
    weight_text = ", ".join(f"{axis}={value:.2f}" for axis, value in sorted(weights.items()))
    action = ACTION_BY_TASK[task_category]
    prompt = (
        "FORGE-Bench evaluation prompt. "
        f"Domain x Task cell: domain={row['domain']}; abstract_task={task_category}. "
        f"Task objective: test {task_category} capability inside the {row['domain']} industrial domain. "
        f"Scene family: {row['scene_id']}. "
        f"Core scenario: {scenario}. "
        f"Reference subject: {subject}. "
        f"Motion requirement / viewpoint motion fidelity: {motion_text}; target motion value {motion_target}. "
        "Evaluation dimensions: industrial_logic_and_fact_alignment, geometric_integrity, physical_plausibility, temporal_consistency, reference_and_motion_fidelity. "
        f"Industrial logic and fact alignment: {AXIS_CHECKS['industrial_logic_and_fact_alignment']}. "
        f"Geometric integrity: {AXIS_CHECKS['geometric_integrity']}; only the requested failure or defect region may change. "
        f"Physical plausibility: {AXIS_CHECKS['physical_plausibility']}. "
        f"Temporal consistency: {AXIS_CHECKS['temporal_consistency']}. "
        f"Reference and motion fidelity: {AXIS_CHECKS['reference_and_motion_fidelity']}. "
        "Single-sample scoring gates: trigger floor vetoes for broken core logic, impossible physics, geometry collapse, static substitution on a motion task, or global regeneration outside the permitted local event region. "
        f"Image requirement: {row['image_requirement']}. "
        "Execution constraints: do not add text overlays, subtitles, logos, watermarks, extra machines, or unrelated people; do not change component counts; do not replace the industrial scene with a different object. "
        f"Dynamic scoring weights: {weight_text}."
    )
    video_prompt = (
        "Use the provided reference image as the first frame and visual anchor. "
        "Generate a 5-8 second realistic industrial video. "
        f"FORGE-Bench Domain x Task cell: {row['domain']} x {task_category}. "
        f"Scene: {scenario}. Reference subject: {subject}. "
        f"Camera: {motion_text}; target motion value {motion_target}. "
        f"Action: {action} "
        "Optimize for the five evaluation dimensions: industrial logic, geometry, physics, temporal consistency, and reference/motion fidelity. "
        "Keep the same equipment identity, layout, colors, materials, background, and perspective cues from the reference image. "
        "Do not add text overlays, subtitles, logos, watermarks, extra machines, or unrelated people. "
        "Avoid melting, flicker, identity swaps, component-count changes, impossible floating loads, rigid-body bending, and accidental global scene changes."
    )
    return prompt, video_prompt, motion_type, motion_target, motion_text


def update_samples(
    blueprint: dict[str, dict],
    old_to_new: dict[str, str],
    images_by_scene: dict[str, list[str]],
    dry_run: bool,
) -> tuple[list[dict], list[dict]]:
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples = data["samples"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        grouped[sample["scene_id"]].append(sample)

    rows: list[dict] = []
    for scene_id, scene_samples in grouped.items():
        if scene_id not in blueprint:
            continue
        row = blueprint[scene_id]
        images = images_by_scene.get(scene_id) or []
        if not images:
            raise FileNotFoundError(f"No formal images remain for scene {scene_id}")

        for index, sample in enumerate(scene_samples):
            old_path = sample.get("image_path", "")
            mapped_path = old_to_new.get(old_path, old_path)
            assigned_path = images[index % len(images)]
            reason = "unchanged"
            if old_path in old_to_new and mapped_path != old_path:
                reason = "renamed"
            if not (ROOT / mapped_path).exists():
                mapped_path = assigned_path
                reason = "reassigned_deleted_reference"
            elif assigned_path != mapped_path:
                mapped_path = assigned_path
                reason = "redistributed_scene_image"

            title_en = row["scenario"].split(";")[0].strip().rstrip(".")
            title_zh = sample.get("task_title_zh") or scene_id.replace("_", " ")
            prompt, video_prompt, motion_type, motion_target, _motion_text = build_prompts(sample, row, index)

            sample["domain"] = row["domain"]
            sample["scene_id"] = scene_id
            sample["task_category"] = row["task_category"]
            sample["image_requirement"] = row["image_requirement"]
            sample["image_path"] = mapped_path
            sample["task_title"] = title_en
            sample["task_title_zh"] = title_zh
            sample["prompt"] = prompt
            sample["video_generation_prompt"] = video_prompt
            sample["motion_type"] = motion_type
            sample["viewpoint_motion_target"] = motion_target

            ann = sample.setdefault("constraint_annotations", {})
            ann["domain_scenario"] = row["scenario"]
            ann["scene_id"] = scene_id
            ann["abstract_task_category"] = row["task_category"]
            ann["image_requirement"] = row["image_requirement"]
            ann["task_title"] = title_en
            ann["task_title_zh"] = title_zh

            rows.append(
                {
                    "task_id": sample.get("task_id", ""),
                    "scene_id": scene_id,
                    "old_image_path": old_path,
                    "new_image_path": mapped_path,
                    "reason": reason,
                    "task_title": title_en,
                }
            )

    if not dry_run:
        SAMPLES_PATH.write_text(
            json.dumps({"samples": samples}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return samples, rows


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    blueprint = parse_blueprint(BLUEPRINT_PATH)
    old_to_new, images_by_scene, image_rows = renumber_images(blueprint, args.dry_run)
    samples, sample_rows = update_samples(blueprint, old_to_new, images_by_scene, args.dry_run)

    write_csv(
        REPORT_DIR / "image_renumber_map.csv",
        image_rows,
        ["scene_id", "domain", "old_image_path", "new_image_path", "changed"],
    )
    write_csv(
        REPORT_DIR / "sample_image_prompt_update.csv",
        sample_rows,
        ["task_id", "scene_id", "old_image_path", "new_image_path", "reason", "task_title"],
    )

    missing = [s for s in samples if not (ROOT / s["image_path"]).exists()]
    reassigned = [r for r in sample_rows if r["reason"] == "reassigned_deleted_reference"]
    changed_images = [r for r in image_rows if r["changed"] == "true"]
    total_images = sum(len(paths) for paths in images_by_scene.values())
    print(f"dry_run={args.dry_run}")
    print(f"formal_images={total_images}")
    print(f"renamed_images={len(changed_images)}")
    print(f"samples={len(samples)}")
    print(f"reassigned_deleted_sample_refs={len(reassigned)}")
    print(f"missing_sample_image_paths={len(missing)}")
    print(f"reports={REPORT_DIR.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
