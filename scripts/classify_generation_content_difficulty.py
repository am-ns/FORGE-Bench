#!/usr/bin/env python3
"""Classify current video-generation samples by content difficulty.

This script does not edit prompts or source samples. It writes a separate
difficulty overlay for reporting and stratified analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
DEFAULT_OVERLAY = ROOT / "reports" / "video_generation_500_content_difficulty_overlay.json"
DEFAULT_CSV = ROOT / "reports" / "video_generation_500_content_difficulty.csv"
DEFAULT_SUMMARY = ROOT / "reports" / "video_generation_500_content_difficulty_summary.json"

MOTION_SCORE = {
    "static": 0.0,
    "pan": 1.0,
    "dolly": 1.1,
    "crane": 1.2,
    "orbit": 1.4,
}

TASK_SCORE = {
    "spatial_exploration_and_viewpoint": 0.9,
    "industrial_logic_and_compliance": 1.35,
    "rigid_body_kinematics_and_coupling": 1.45,
    "topology_mutation_and_failure": 1.55,
    "fluid_dynamics_and_thermodynamics": 1.7,
}

KEYWORD_GROUPS = {
    "multi_entity_or_human_interaction": {
        "weight": 0.9,
        "patterns": [
            r"\bworker\b",
            r"\bperson\b",
            r"\bpedestrian\b",
            r"\bhuman\b",
            r"\bforklift\b",
            r"\bagv\b",
            r"\bamr\b",
            r"\bvehicle\b",
            r"\btruck\b",
            r"\bcrane\b",
            r"\brobot\b",
            r"\bcobot\b",
        ],
    },
    "causal_safety_response": {
        "weight": 0.8,
        "patterns": [
            r"\balarm\b",
            r"\bstop\b",
            r"\bbrak",
            r"\bevacuat",
            r"\blockout\b",
            r"\binterlock\b",
            r"\bwarning\b",
            r"\bresponse\b",
            r"\bescalation\b",
        ],
    },
    "fluid_heat_or_pressure": {
        "weight": 1.15,
        "patterns": [
            r"\bsmoke\b",
            r"\bfire\b",
            r"\bflame\b",
            r"\bsteam\b",
            r"\bleak\b",
            r"\bfluid\b",
            r"\bwater\b",
            r"\bgas\b",
            r"\bplume\b",
            r"\bpressure\b",
            r"\bthermal\b",
            r"\bexplosion\b",
            r"\bdeflagration\b",
            r"\bdust\b",
            r"\bignite",
            r"\bignition\b",
            r"\bpropagation\b",
            r"\bgrowth\b",
            r"\bhot work\b",
        ],
    },
    "precision_local_geometry": {
        "weight": 1.0,
        "patterns": [
            r"\bcrack\b",
            r"\bchip",
            r"\bporosity\b",
            r"\bscratch\b",
            r"\bsolder\b",
            r"\bpin\b",
            r"\bgear\b",
            r"\bweld\b",
            r"\bblade\b",
            r"\bflange\b",
            r"\brope\b",
            r"\bjoint\b",
            r"\btooth\b",
        ],
    },
    "coupled_motion_or_contact": {
        "weight": 0.95,
        "patterns": [
            r"\bcontact\b",
            r"\bgrasp\b",
            r"\blift\b",
            r"\bcollision\b",
            r"\bswing\b",
            r"\bbuckle\b",
            r"\bdeform\b",
            r"\btilt\b",
            r"\bpenetrat",
            r"\bcoupl",
            r"\bkinematic\b",
            r"\bhydraulic\b",
        ],
    },
    "occlusion_or_tight_framing": {
        "weight": 0.55,
        "patterns": [
            r"\bmacro\b",
            r"\bclose\b",
            r"\btight\b",
            r"\bborescope\b",
            r"\bendoscope\b",
            r"\bblind\b",
            r"\bocclusion\b",
            r"\binterior\b",
        ],
    },
}

TIER_LAYOUT = [
    ("easy", 0.20),
    ("medium", 0.30),
    ("hard", 0.30),
    ("adversarial", 0.20),
]


def load_samples(path: Path) -> tuple[dict, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    samples = payload["samples"] if isinstance(payload, dict) else payload
    return payload if isinstance(payload, dict) else {}, samples


def match_group(text: str, patterns: list[str]) -> list[str]:
    matched = []
    for pattern in patterns:
        if re.search(pattern, text):
            matched.append(pattern.strip(r"\b").replace("\\", ""))
    return matched


def target_motion_pressure(sample: dict) -> float:
    motion_type = str(sample.get("motion_type") or "static").lower()
    target = sample.get("viewpoint_motion_target")
    if not isinstance(target, (int, float)):
        return 0.0
    if motion_type == "static":
        return 0.0
    if motion_type in {"pan", "orbit", "crane"}:
        return min(0.7, abs(float(target)) / 90.0)
    if motion_type == "dolly":
        return min(0.7, abs(float(target)))
    return min(0.5, abs(float(target)) / 100.0)


def score_sample(sample: dict) -> dict:
    prompt = str(sample.get("video_generation_prompt") or "")
    scene = str(sample.get("scene_id") or "")
    task = str(sample.get("task_category") or "")
    text = " ".join([prompt, scene, task]).lower()

    motion_type = str(sample.get("motion_type") or "static").lower()
    factors: dict[str, float] = {
        "motion_control": MOTION_SCORE.get(motion_type, 0.8) + target_motion_pressure(sample),
        "task_family": TASK_SCORE.get(task, 1.2),
    }
    evidence: dict[str, list[str]] = {}

    for group, config in KEYWORD_GROUPS.items():
        matches = match_group(text, list(config["patterns"]))
        if matches:
            factors[group] = float(config["weight"])
            evidence[group] = sorted(set(matches))[:8]

    required_events = sample.get("required_observable_events") or []
    if isinstance(required_events, list) and len(required_events) > 2:
        factors["multi_step_required_events"] = min(0.8, 0.25 * (len(required_events) - 2))

    questions = sample.get("reasoning_alignment_questions") or sample.get("industrial_logic_questions") or []
    if isinstance(questions, list) and len(questions) >= 4:
        factors["questioned_hidden_constraints"] = min(0.7, 0.12 * len(questions))

    score = round(sum(factors.values()), 3)
    return {
        "task_id": sample.get("task_id"),
        "domain": sample.get("domain"),
        "scene_id": sample.get("scene_id"),
        "task_category": task,
        "motion_type": motion_type,
        "viewpoint_motion_target": sample.get("viewpoint_motion_target"),
        "content_difficulty_score": score,
        "content_difficulty_factors": factors,
        "content_difficulty_evidence": evidence,
        "original_difficulty_level": sample.get("challenge_difficulty_level", sample.get("difficulty_level")),
    }


def assign_relative_tiers(rows: list[dict]) -> None:
    ranked = sorted(
        rows,
        key=lambda row: (
            row["content_difficulty_score"],
            str(row["motion_type"]),
            str(row["task_category"]),
            str(row["task_id"]),
        ),
    )
    total = len(ranked)
    start = 0
    for index, (tier, fraction) in enumerate(TIER_LAYOUT):
        if index == len(TIER_LAYOUT) - 1:
            end = total
        else:
            end = start + round(total * fraction)
        for row in ranked[start:end]:
            row["content_difficulty_level"] = tier
        start = end


def summarize(rows: list[dict], source_payload: dict) -> dict:
    by_tier = Counter(row["content_difficulty_level"] for row in rows)
    tier_domain = defaultdict(Counter)
    tier_task = defaultdict(Counter)
    tier_motion = defaultdict(Counter)
    tier_scores = defaultdict(list)
    for row in rows:
        tier = row["content_difficulty_level"]
        tier_domain[tier][row["domain"]] += 1
        tier_task[tier][row["task_category"]] += 1
        tier_motion[tier][row["motion_type"]] += 1
        tier_scores[tier].append(row["content_difficulty_score"])

    score_ranges = {
        tier: {
            "min": min(scores),
            "max": max(scores),
            "mean": round(sum(scores) / len(scores), 3),
        }
        for tier, scores in sorted(tier_scores.items())
    }
    return {
        "source_split_id": source_payload.get("split_id"),
        "source_samples_json": str(DEFAULT_SAMPLES),
        "classification_policy": {
            "prompt_mutation": "none",
            "basis": "relative content difficulty over the current 500 generation prompts",
            "tier_layout": dict(TIER_LAYOUT),
            "note": "easy means lower generation load inside this industrial set, not generally easy video generation.",
        },
        "counts": dict(sorted(by_tier.items())),
        "score_ranges": score_ranges,
        "by_tier_domain": {tier: dict(counter) for tier, counter in sorted(tier_domain.items())},
        "by_tier_task_category": {tier: dict(counter) for tier, counter in sorted(tier_task.items())},
        "by_tier_motion_type": {tier: dict(counter) for tier, counter in sorted(tier_motion.items())},
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "task_id",
        "content_difficulty_level",
        "content_difficulty_score",
        "original_difficulty_level",
        "domain",
        "task_category",
        "scene_id",
        "motion_type",
        "viewpoint_motion_target",
        "content_difficulty_factors",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: str(item["task_id"])):
            out = {field: row.get(field) for field in fields}
            out["content_difficulty_factors"] = json.dumps(
                row["content_difficulty_factors"],
                ensure_ascii=False,
                sort_keys=True,
            )
            writer.writerow(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-json", default=str(DEFAULT_SAMPLES))
    parser.add_argument("--overlay", default=str(DEFAULT_OVERLAY))
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument(
        "--promote-to-samples",
        action="store_true",
        help="Make content difficulty official while preserving the legacy label.",
    )
    args = parser.parse_args()

    source_payload, samples = load_samples(Path(args.samples_json))
    rows = [score_sample(sample) for sample in samples]
    assign_relative_tiers(rows)
    if args.promote_to_samples:
        by_id = {str(row["task_id"]): row for row in rows}
        for sample in samples:
            row = by_id[str(sample["task_id"])]
            if "challenge_difficulty_level" not in sample:
                sample["challenge_difficulty_level"] = sample.get("difficulty_level")
            sample["difficulty_level"] = row["content_difficulty_level"]
            sample["content_difficulty_score"] = row["content_difficulty_score"]
            sample["content_difficulty_factors"] = row["content_difficulty_factors"]
        Path(args.samples_json).write_text(
            json.dumps(source_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = summarize(rows, source_payload)

    overlay = {
        "source_samples_json": args.samples_json,
        "summary": summary,
        "samples": sorted(rows, key=lambda row: str(row["task_id"])),
    }

    overlay_path = Path(args.overlay)
    summary_path = Path(args.summary)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(Path(args.csv), rows)

    print(json.dumps({
        "overlay": str(overlay_path),
        "csv": args.csv,
        "summary": str(summary_path),
        "counts": summary["counts"],
        "score_ranges": summary["score_ranges"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
