#!/usr/bin/env python3
"""Aggregate results from multiple models into a ranked leaderboard."""

import json
import os
import sys

from eval.axis_registry import (
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
)


LEADERBOARD_AXES = [
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    TEMPORAL_CONSISTENCY,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    GEOMETRIC_INTEGRITY,
]


def _load_model_results(results_dir: str) -> list[dict]:
    """Scan *results_dir* for MODEL_NAME/aggregate.json and load each."""
    models = []
    if not os.path.isdir(results_dir):
        print(f"WARNING: results_dir not found: {results_dir}", file=sys.stderr)
        return models

    for entry in sorted(os.listdir(results_dir)):
        agg_path = os.path.join(results_dir, entry, "aggregate.json")
        if not os.path.isfile(agg_path):
            continue
        try:
            with open(agg_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARNING: could not load {agg_path}: {exc}", file=sys.stderr)
            continue

        models.append({
            "model": entry,
            "overall": data.get("overall", 0.0),
            "axis_scores": data.get("axis_scores", {}),
            "viewpoint_motion_tier": data.get("viewpoint_motion_tier", "unknown"),
            "rif": data.get("rif"),
            "rif_gated": data.get("rif_gated"),
            "num_samples_completed": data.get("num_samples_completed"),
            "num_samples_total": data.get("num_samples_total"),
            "raw": data,
        })

    return models


def _format_axis(axis_scores: dict, axis: str) -> str:
    """Format a single axis score for the markdown table."""
    val = axis_scores.get(axis)
    if val is None:
        return "-"
    return f"{float(val):.1f}"


def _generate_markdown(models: list[dict]) -> str:
    """Build a markdown leaderboard table from ranked model list."""
    header = [
        "Rank",
        "Model",
        "Overall",
        *LEADERBOARD_AXES,
        "viewpoint_motion_tier",
        "rotation_integrity_factor",
    ]
    lines = [
        "# FORGE-Bench Leaderboard",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]

    for rank, item in enumerate(models, 1):
        axis_scores = item["axis_scores"]
        rif_str = f"{float(item['rif']):.1f}" if item["rif"] is not None else "-"
        row = [
            str(rank),
            item["model"],
            f"{float(item['overall']):.1f}",
            *[_format_axis(axis_scores, axis) for axis in LEADERBOARD_AXES],
            item["viewpoint_motion_tier"],
            rif_str,
        ]
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append(f"Generated from {len(models)} model(s) in the results directory.")
    lines.append("")
    return "\n".join(lines)


def build_leaderboard(results_dir: str) -> dict:
    """Build a ranked leaderboard from all model aggregate files."""
    models = _load_model_results(results_dir)
    models.sort(key=lambda m: m["overall"], reverse=True)

    for index, item in enumerate(models, 1):
        item["rank"] = index

    serializable = [{k: v for k, v in item.items() if k != "raw"} for item in models]
    leaderboard = {"models": serializable, "num_models": len(models)}

    json_path = os.path.join(results_dir, "leaderboard.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, indent=2, default=str)

    md_path = os.path.join(results_dir, "leaderboard.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(_generate_markdown(models))

    leaderboard["generated_files"] = [json_path, md_path]
    print(f"Leaderboard written: {json_path}, {md_path}", file=sys.stderr)
    return leaderboard


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build FORGE-Bench leaderboard")
    parser.add_argument("results_dir", help="Directory containing MODEL_NAME/aggregate.json files")
    args = parser.parse_args()
    print(json.dumps(build_leaderboard(args.results_dir), indent=2, default=str))
