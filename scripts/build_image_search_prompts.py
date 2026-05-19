#!/usr/bin/env python3
"""Build strict reference-image search prompts for every FORGE sample."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_JSONL = ROOT / "reports" / "image_search_prompts.jsonl"
DEFAULT_CSV = ROOT / "reports" / "image_search_prompts.csv"
DEFAULT_MD = ROOT / "reports" / "image_search_prompts.md"

TASK_REQUIREMENTS = {
    "rigid_body_kinematics_and_coupling": (
        "a clear rigid mechanism with visible joints, links, supports, wheels, "
        "load path, tool contact, or coupled industrial motion geometry"
    ),
    "topology_mutation_and_failure": (
        "a localized inspection target such as PCB traces, gear teeth, cable, "
        "rope, fence, truss, crack-prone structure, or other precise failure region"
    ),
    "fluid_dynamics_and_thermodynamics": (
        "pipes, tanks, vessels, spray source, fluid path, pressure boundary, "
        "smoke or flame path, containment, or thermal process equipment"
    ),
    "spatial_exploration_and_viewpoint": (
        "a subject with readable depth, occlusion, corridors, inspection access, "
        "bridge span, robot viewpoint, tube bundle, or drone-orbit geometry"
    ),
    "industrial_logic_and_compliance": (
        "a visible rule or trigger context such as restricted zone, PPE area, "
        "worker-machine proximity, light curtain, vehicle path, alarm, or hot-work hazard"
    ),
}

DOMAIN_CONTEXT = {
    "visual_security": "industrial security monitoring, restricted access, PPE compliance, vehicle safety",
    "embodied_robotics": "robot arm, mobile robot, quadruped robot, automation cell, gripper, sensor",
    "heavy_load_construction": "construction machinery, crane, excavator, bridge segment, gantry, haul truck",
    "precision_defect_gen": "precision inspection, PCB, gear, CNC, tube bundle, crack, micro defect",
    "extreme_emergency": "industrial emergency, chemical plant, fire, leak, explosion, structural collapse",
}

STRICT_VISUAL_RULES = (
    "real photo only; no render, drawing, diagram, collage, poster, screenshot, logo, "
    "text-heavy image, map, close crowd, showroom, toy, miniature, or heavily edited image; "
    "main subject must occupy roughly 25-75 percent of the frame; background must be simple "
    "enough for image-to-video evaluation, with no dense unrelated clutter"
)

SCENARIO_SUBJECT_HINTS = (
    "forklift",
    "heavy haul truck",
    "road train",
    "articulated dump truck",
    "restricted-zone fence",
    "chemical liquid leak",
    "surveillance camera",
    "robotic arm",
    "robot arm",
    "mobile robot",
    "quadruped robot",
    "light curtain",
    "excavator",
    "crawler crane",
    "wire rope",
    "underground pipe",
    "bridge precast segment",
    "pcb traces",
    "circuit board",
    "gear teeth",
    "cnc machine",
    "cutting-fluid spray",
    "tube bundle",
    "storage tank",
    "pipeline",
    "flash fire",
    "transmission tower",
    "dust explosion",
)


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return " ".join(match.group(1).split()) if match else ""


def _fallback_subject(image_path: str) -> str:
    stem = Path(image_path).stem
    if "__" in stem:
        stem = stem.split("__", 1)[1]
    return stem.replace("_", " ")


def _clean_subject(subject: str, scenario: str) -> str:
    subject = subject.strip().strip(".:; ")
    generic_id = re.fullmatch(r"(veh|mfg|rob|micro|eng|aero|sa)[ _-]?\d+", subject.lower())
    if generic_id or not subject:
        lowered = scenario.lower()
        for hint in SCENARIO_SUBJECT_HINTS:
            if hint in lowered:
                return hint
        return " ".join(scenario.split()[:6]).strip(".:; ")
    return subject


def _clean_sentence(text: str) -> str:
    return " ".join(text.split()).strip().strip(".:; ")


def build_prompt_row(sample: dict) -> dict:
    prompt = sample.get("prompt", "")
    scenario = _clean_sentence(_extract(r"Core scenario:\s*(.*?)(?=\s+Reference subject:|$)", prompt))
    subject = sample.get("reference_subject", "")
    if not subject:
        subject = _extract(r"Reference subject:\s*(.*?)(?=\s+Motion requirement|$)", prompt)
    if not subject:
        subject = _fallback_subject(sample.get("image_path", ""))
    subject = _clean_subject(subject, scenario)
    task = sample.get("task_category", "")
    domain = sample.get("domain", "")
    task_requirement = TASK_REQUIREMENTS.get(task, "a clear industrial subject matching the scenario")
    domain_context = DOMAIN_CONTEXT.get(domain, "industrial scene")

    query_parts = [
        scenario,
        domain_context,
        task_requirement,
        "real industrial photo high resolution",
    ]
    if subject.lower() not in scenario.lower():
        query_parts.insert(0, subject)
    search_query = " ".join(query_parts)
    search_query = re.sub(r"\s+", " ", search_query).strip()

    negative_prompt = (
        "Reject if the image is decorative, synthetic, low resolution, blurry, "
        "too dark, too crowded, text-dominated, unrelated to the equipment, or "
        "missing the requested industrial subject."
    )
    evaluator_prompt = (
        f"Find one open-license reference image for {sample['task_id']}. "
        f"Domain: {domain}. Task: {task}. Scenario: {scenario}. "
        f"Required subject: {subject}. The image must show {task_requirement}. "
        f"Strict visual rules: {STRICT_VISUAL_RULES}. {negative_prompt}"
    )

    return {
        "task_id": sample.get("task_id", ""),
        "domain": domain,
        "task_category": task,
        "reference_subject": subject,
        "core_scenario": scenario,
        "task_visual_requirement": task_requirement,
        "strict_visual_rules": STRICT_VISUAL_RULES,
        "search_query": search_query,
        "negative_prompt": negative_prompt,
        "evaluator_prompt": evaluator_prompt,
    }


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict], path: Path) -> None:
    lines = [
        "# Strict Image Search Prompts",
        "",
        "One prompt per benchmark sample. These prompts target open-license, high-resolution, low-clutter industrial reference photos.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## `{row['task_id']}`",
            "",
            f"- domain: `{row['domain']}`",
            f"- task_category: `{row['task_category']}`",
            f"- reference_subject: `{row['reference_subject']}`",
            f"- core_scenario: {row['core_scenario']}",
            f"- search_query: `{row['search_query']}`",
            "",
            "```text",
            row["evaluator_prompt"],
            "```",
            "",
        ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build strict image search prompts.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument("--markdown", default=str(DEFAULT_MD))
    args = parser.parse_args()

    rows = [build_prompt_row(sample) for sample in _load_samples(Path(args.samples))]
    write_jsonl(rows, Path(args.jsonl))
    write_csv(rows, Path(args.csv))
    write_markdown(rows, Path(args.markdown))
    print(f"wrote {len(rows)} image search prompts")
    print(args.jsonl)
    print(args.csv)
    print(args.markdown)


if __name__ == "__main__":
    main()
