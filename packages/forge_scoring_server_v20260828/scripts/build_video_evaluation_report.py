#!/usr/bin/env python3
"""Build auditable 5+1 artifacts from immutable per-sample evaluation JSON."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from eval.axis_registry import APPLICATION_USEFULNESS, TECHNICAL_AXES
from scoring.aggregate import aggregate_sample_results


CSV_FIELDS = [
    "task_id", "model_id", "sample_status", "protocol_version", "protocol_sha256",
    *TECHNICAL_AXES, APPLICATION_USEFULNESS, "technical_score", "application_score",
    "ranking_score", "observable_event_coverage", "task_realization_score",
    "task_success", "conditional_quality", "visual_quality_score",
    "reasoning_alignment_accuracy", "domain", "task_category", "motion_type",
]


def _row(result: dict) -> dict:
    scored = result.get("scored") or {}
    axes = scored.get("axis_scores") or {}
    status = result.get("sample_status") or ("model_output_invalid" if result.get("skipped") else "valid")
    technical = scored.get("technical_score")
    application = scored.get("application_score")
    ranking = result.get("ranking_score")
    if ranking is None and status == "valid" and technical is not None and application is not None:
        ranking = 0.8 * float(technical) + 0.2 * float(application)
    event = result.get("observable_event_coverage", scored.get("observable_event_coverage"))
    industrial = axes.get(TECHNICAL_AXES[0])
    reference = axes.get(TECHNICAL_AXES[4])
    realization = None if None in (event, industrial, reference) else (float(event) + float(industrial) + float(reference)) / 3
    success = None if realization is None else all(float(v) >= 60 for v in (event, industrial, reference))
    quality_axes = [axes.get(axis) for axis in TECHNICAL_AXES[1:]]
    conditional = None if any(v is None for v in quality_axes) else sum(map(float, quality_axes)) / 4
    row = {
        "task_id": result.get("task_id"), "model_id": result.get("model_id"), "sample_status": status,
        "protocol_version": result.get("protocol_version"), "protocol_sha256": result.get("protocol_sha256"),
        **{axis: axes.get(axis) for axis in TECHNICAL_AXES}, APPLICATION_USEFULNESS: application,
        "technical_score": technical, "application_score": application, "ranking_score": ranking,
        "observable_event_coverage": event, "task_realization_score": realization, "task_success": success,
        "conditional_quality": conditional, "visual_quality_score": result.get("visual_quality_score"),
        "reasoning_alignment_accuracy": result.get("reasoning_alignment_score"), "domain": result.get("domain"),
        "task_category": result.get("task_category"), "motion_type": result.get("motion_type"),
    }
    if status == "model_output_invalid":
        row["ranking_score"] = 0.0
    elif status == "evaluator_invalid":
        row["ranking_score"] = None
    return row


def build(input_path: Path, output_dir: Path) -> dict:
    results = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(results, dict):
        results = results.get("per_sample", results.get("results", []))
    rows = [_row(item) for item in results]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "per_sample.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output_dir / "scores.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    aggregate = aggregate_sample_results(results)
    aggregate["csv_recalculation"] = {
        "ranking_score": None if any(row["ranking_score"] is None for row in rows) else sum(float(row["ranking_score"]) for row in rows) / len(rows) if rows else None,
        "row_count": len(rows),
    }
    (output_dir / "aggregate.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Video evaluation report", "", f"- Ranking status: {aggregate.get('ranking_status')}", f"- Ranking score: {aggregate.get('ranking_score')}", f"- Samples: {len(rows)}"]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.input, args.output)


if __name__ == "__main__":
    main()
