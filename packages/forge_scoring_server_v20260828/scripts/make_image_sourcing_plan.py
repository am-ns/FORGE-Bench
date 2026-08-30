#!/usr/bin/env python3
"""Create an image matching and sourcing plan for the current taxonomy."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "samples.json"
DEFAULT_CSV = ROOT / "reports" / "image_sourcing_plan.csv"
DEFAULT_MD = ROOT / "reports" / "image_sourcing_plan.md"

IMAGE_DIRS = [
    ROOT / "dataset" / "images",
    ROOT / "dataset" / "images_hq",
]

TASK_IMAGE_REQUIREMENTS = {
    "rigid_body_kinematics_and_coupling": (
        "Use a clear industrial photo with visible joints, rigid links, axes, "
        "supports, load path, tool contact, or coupled mechanism geometry."
    ),
    "topology_mutation_and_failure": (
        "Use a photo where the defect or failure area can be localized: dense "
        "PCB traces, gear teeth, rope/cable, crack-prone structure, fence, or truss."
    ),
    "fluid_dynamics_and_thermodynamics": (
        "Use a scene with pipes, tanks, fluid source, cutting zone, mud/water, "
        "smoke/fire path, pressure boundary, or containment context."
    ),
    "spatial_exploration_and_viewpoint": (
        "Use a photo with meaningful spatial depth or occlusion: surveillance "
        "blind spot, endoscope tube path, drone-inspection subject, bridge segment, or robot POV."
    ),
    "industrial_logic_and_compliance": (
        "Use a scene where the rule and trigger are visible: restricted zone, "
        "worker proximity, missing protective equipment, light curtain, vehicle intrusion, or hot-work hazard."
    ),
}

DOMAIN_KEYWORDS = {
    "visual_security": "industrial security surveillance restricted zone worker ppe forklift vehicle intrusion",
    "embodied_robotics": "robot arm quadruped mobile robot gripper sensor light curtain automated line",
    "heavy_load_construction": "crawler crane excavator gantry bridge segment haul truck wire rope construction load",
    "precision_defect_gen": "pcb solder bridge gear crack endoscope cnc cutting tool tube bundle defect inspection",
    "extreme_emergency": "chemical leak fire explosion transmission tower ice collapse emergency response industrial plant",
}


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _extract_core_scenario(prompt: str) -> str:
    match = re.search(r"Core scenario:\s*(.*?)(?=\s+Reference subject:|$)", prompt)
    return " ".join(match.group(1).split()) if match else ""


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^a-z0-9]+", text.lower())
        if len(token) >= 3 and token not in {"the", "and", "for", "with", "from", "into"}
    }


def _image_inventory() -> list[dict]:
    images = []
    for base in IMAGE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            rel = path.relative_to(ROOT).as_posix()
            searchable = " ".join(path.with_suffix("").parts[-3:])
            images.append({"path": rel, "tokens": _tokenize(searchable)})
    return images


def _local_candidates(sample: dict, inventory: list[dict], limit: int = 5) -> list[str]:
    scenario = _extract_core_scenario(sample.get("prompt", ""))
    query_text = " ".join([
        sample.get("domain", ""),
        sample.get("task_category", ""),
        scenario,
        DOMAIN_KEYWORDS.get(sample.get("domain", ""), ""),
    ])
    query_tokens = _tokenize(query_text)
    ranked = []
    current = sample.get("image_path", "")
    for item in inventory:
        score = len(query_tokens & item["tokens"])
        if item["path"] == current:
            score += 3
        if score:
            ranked.append((score, item["path"]))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return [path for _, path in ranked[:limit]]


def build_rows(samples: list[dict]) -> list[dict]:
    inventory = _image_inventory()
    reuse_counts = Counter(sample.get("image_path", "") for sample in samples)
    rows = []
    for sample in samples:
        image_path = sample.get("image_path", "")
        scenario = _extract_core_scenario(sample.get("prompt", ""))
        exists = bool(image_path and (ROOT / image_path).exists())
        search_query = " ".join([
            scenario,
            DOMAIN_KEYWORDS.get(sample.get("domain", ""), ""),
            sample.get("task_category", "").replace("_", " "),
            "real industrial photo high resolution",
        ]).strip()
        rows.append({
            "task_id": sample.get("task_id", ""),
            "domain": sample.get("domain", ""),
            "task_category": sample.get("task_category", ""),
            "core_scenario": scenario,
            "current_image_path": image_path,
            "image_exists": "yes" if exists else "no",
            "current_image_reuse_count": reuse_counts[image_path],
            "image_requirement": TASK_IMAGE_REQUIREMENTS.get(sample.get("task_category", ""), ""),
            "recommended_search_query": search_query,
            "local_candidate_images": " | ".join(_local_candidates(sample, inventory)),
            "video_generation_prompt": sample.get("video_generation_prompt", ""),
        })
    return rows


def write_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "task_id",
        "domain",
        "task_category",
        "core_scenario",
        "current_image_path",
        "image_exists",
        "current_image_reuse_count",
        "image_requirement",
        "recommended_search_query",
        "local_candidate_images",
        "video_generation_prompt",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Image Sourcing Plan",
        "",
        "This file helps replace reused reference images without deleting the existing image pool.",
        "",
    ]
    for row in rows:
        if row["current_image_reuse_count"] <= 1 and row["image_exists"] == "yes":
            continue
        lines.append(f"## `{row['task_id']}`")
        lines.append("")
        lines.append(f"- domain: `{row['domain']}`")
        lines.append(f"- task_category: `{row['task_category']}`")
        lines.append(f"- current_image_path: `{row['current_image_path']}`")
        lines.append(f"- current_image_reuse_count: `{row['current_image_reuse_count']}`")
        lines.append(f"- scenario: {row['core_scenario']}")
        lines.append(f"- requirement: {row['image_requirement']}")
        lines.append(f"- recommended_search_query: `{row['recommended_search_query']}`")
        lines.append(f"- local_candidate_images: `{row['local_candidate_images']}`")
        lines.append("")
        lines.append("```text")
        lines.append(row["video_generation_prompt"])
        lines.append("```")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate image matching and sourcing plans.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument("--markdown", default=str(DEFAULT_MD))
    args = parser.parse_args()

    samples = _load_samples(Path(args.samples))
    rows = build_rows(samples)
    write_csv(rows, Path(args.csv))
    write_markdown(rows, Path(args.markdown))
    missing = sum(1 for row in rows if row["image_exists"] == "no")
    reused = sum(1 for row in rows if row["current_image_reuse_count"] > 1)
    print(f"wrote {len(rows)} rows to {args.csv}")
    print(f"wrote review markdown to {args.markdown}")
    print(f"missing images: {missing}; rows using reused images: {reused}")


if __name__ == "__main__":
    main()
