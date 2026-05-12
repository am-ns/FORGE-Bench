#!/usr/bin/env python3
"""Aggregate results from multiple models into a ranked leaderboard.

Scans a results directory for MODEL_NAME/aggregate.json files, ranks models
by overall score, and writes leaderboard.md + leaderboard.json.
"""

import json
import os
import sys

from scoring.aggregate import vfa_tier


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
            with open(agg_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARNING: could not load {agg_path}: {exc}", file=sys.stderr)
            continue

        models.append({
            "model": entry,
            "overall": data.get("overall", 0.0),
            "axis_scores": data.get("axis_scores", {}),
            "vfa_tier": data.get("vfa_tier", "unknown"),
            "rif": data.get("rif"),
            "rif_gated": data.get("rif_gated"),
            "num_samples_completed": data.get("num_samples_completed"),
            "num_samples_total": data.get("num_samples_total"),
            "raw": data,
        })

    return models


def _format_axis(axis_scores: dict, axis: str) -> str:
    """Format a single axis score for the markdown table, or em-dash if absent."""
    val = axis_scores.get(axis)
    if val is None:
        return "—"
    return f"{val:.1f}"


def _generate_markdown(models: list[dict]) -> str:
    """Build a markdown leaderboard table from ranked model list."""
    lines = [
        "# FORGE-Bench Leaderboard",
        "",
        "| Rank | Model | Overall | IKA | TC | PP | VF | GI | VFA Tier | RIF |",
        "|------|-------|---------|-----|----|----|----|----|---------:|-----|",
    ]

    for rank, m in enumerate(models, 1):
        ax = m["axis_scores"]
        rif_str = f"{m['rif']:.1f}" if m["rif"] is not None else "—"
        lines.append(
            f"| {rank} | {m['model']} | {m['overall']:.1f} | "
            f"{_format_axis(ax, 'ika')} | {_format_axis(ax, 'tc')} | "
            f"{_format_axis(ax, 'pp')} | {_format_axis(ax, 'vf')} | "
            f"{_format_axis(ax, 'gi')} | {m['vfa_tier']} | {rif_str} |"
        )

    lines.append("")
    lines.append(
        f"*Generated from {len(models)} model(s) in the results directory.*"
    )
    lines.append("")
    return "\n".join(lines)


def build_leaderboard(results_dir: str) -> dict:
    """Build a ranked leaderboard from all models in *results_dir*.

    Scans for MODEL_NAME/aggregate.json, ranks by overall score descending,
    and writes leaderboard.md and leaderboard.json into *results_dir*.

    Args:
        results_dir: Path to the directory containing per-model subdirectories.

    Returns:
        dict with keys: models (ranked list), num_models, generated_files.
    """
    models = _load_model_results(results_dir)
    models.sort(key=lambda m: m["overall"], reverse=True)

    # Assign ranks
    for i, m in enumerate(models, 1):
        m["rank"] = i

    # Strip raw aggregate from the serialised output
    serializable = []
    for m in models:
        entry = {k: v for k, v in m.items() if k != "raw"}
        serializable.append(entry)

    leaderboard = {
        "models": serializable,
        "num_models": len(models),
    }

    # Write JSON
    json_path = os.path.join(results_dir, "leaderboard.json")
    with open(json_path, "w") as f:
        json.dump(leaderboard, f, indent=2, default=str)

    # Write markdown
    md_path = os.path.join(results_dir, "leaderboard.md")
    md_content = _generate_markdown(models)
    with open(md_path, "w") as f:
        f.write(md_content)

    leaderboard["generated_files"] = [json_path, md_path]
    print(f"Leaderboard written: {json_path}, {md_path}", file=sys.stderr)
    return leaderboard


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build FORGE-Bench leaderboard")
    parser.add_argument(
        "results_dir",
        help="Directory containing MODEL_NAME/aggregate.json files",
    )
    args = parser.parse_args()
    result = build_leaderboard(args.results_dir)
    print(json.dumps(result, indent=2, default=str))
