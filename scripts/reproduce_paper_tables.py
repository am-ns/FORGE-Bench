#!/usr/bin/env python3
"""Reproduce paper-facing result tables from FORGE-Bench aggregate files.

This script is intentionally read-only with respect to model results and the
dataset. It scans result directories, extracts predeclared paper metrics, and
writes auditable JSON/CSV/Markdown tables for manuscript use.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_METRICS = [
    "ranking_score",
    "technical_score",
    "application_score_strict",
    "strict_pass_rate",
    "functional_pass_rate",
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _ci_to_text(ci: object) -> str:
    if not isinstance(ci, dict):
        return ""
    low = ci.get("ci95_low")
    high = ci.get("ci95_high")
    if low is None or high is None:
        return ""
    return f"[{float(low):.2f}, {float(high):.2f}]"


def _git_commit(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _discover_aggregates(results_dir: Path) -> list[Path]:
    if not results_dir.is_dir():
        return []
    return sorted(path for path in results_dir.glob("*/aggregate.json") if path.is_file())


def _row_from_aggregate(model_dir: Path, aggregate: dict[str, Any], metrics: list[str]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "model": model_dir.name,
        "num_samples_completed": aggregate.get("num_samples_completed"),
        "num_samples_total": aggregate.get("num_samples_total"),
        "num_samples_skipped": aggregate.get("num_samples_skipped"),
        "num_samples_complete_required_axes": aggregate.get("num_samples_complete_required_axes"),
        "judge_model": (aggregate.get("run_metadata") or {}).get("judge_model"),
        "llm_provider": (aggregate.get("run_metadata") or {}).get("llm_provider"),
        "samples_json_sha256": (aggregate.get("run_metadata") or {}).get("samples_json_sha256"),
        "eval_code_sha256": (aggregate.get("run_metadata") or {}).get("eval_code_sha256"),
        "scoring_code_sha256": (aggregate.get("run_metadata") or {}).get("scoring_code_sha256"),
    }
    for metric in metrics:
        value = aggregate.get(metric)
        row[metric] = float(value) if isinstance(value, (int, float)) else value
        row[f"{metric}_ci95"] = _ci_to_text(aggregate.get(f"{metric}_ci95"))
    return row


def build_tables(results_dir: Path, metrics: list[str]) -> dict[str, Any]:
    aggregates = _discover_aggregates(results_dir)
    rows = [_row_from_aggregate(path.parent, _load_json(path), metrics) for path in aggregates]
    rows.sort(key=lambda item: float(item.get("ranking_score") or 0.0), reverse=True)
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank

    totals = sorted({row.get("num_samples_total") for row in rows if row.get("num_samples_total") is not None})
    warnings = []
    if len(totals) > 1:
        warnings.append(f"inconsistent_num_samples_total:{totals}")
    for row in rows:
        completed = row.get("num_samples_completed")
        total = row.get("num_samples_total")
        skipped = row.get("num_samples_skipped")
        if completed is not None and total is not None and completed != total:
            warnings.append(f"{row['model']}:incomplete_run:{completed}/{total}")
        if skipped not in (None, 0):
            warnings.append(f"{row['model']}:skipped_samples:{skipped}")

    return {
        "schema_version": "forge-paper-tables-v1",
        "results_dir": str(results_dir),
        "metrics": metrics,
        "num_models": len(rows),
        "warnings": warnings,
        "models": rows,
    }


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    preferred = [
        "rank",
        "model",
        "ranking_score",
        "ranking_score_ci95",
        "technical_score",
        "technical_score_ci95",
        "application_score_strict",
        "application_score_strict_ci95",
        "num_samples_completed",
        "num_samples_total",
        "num_samples_skipped",
    ]
    ordered = [field for field in preferred if field in fieldnames]
    ordered.extend(field for field in fieldnames if field not in ordered)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ordered)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    metrics = payload["metrics"]
    headers = ["Rank", "Model", *metrics, "Completed", "Skipped"]
    lines = [
        "# FORGE-Bench Paper Results",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in payload["models"]:
        values = [
            str(row.get("rank", "")),
            str(row.get("model", "")),
        ]
        for metric in metrics:
            value = row.get(metric)
            values.append(f"{float(value):.2f}" if isinstance(value, (int, float)) else str(value or ""))
        values.extend([
            str(row.get("num_samples_completed", "")),
            str(row.get("num_samples_skipped", "")),
        ])
        lines.append("| " + " | ".join(values) + " |")
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper result tables from FORGE-Bench aggregates.")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/paper_reproduction"))
    parser.add_argument("--metrics", nargs="+", default=DEFAULT_METRICS)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    payload = build_tables(args.results_dir, list(args.metrics))
    payload["git_commit"] = _git_commit(repo_root)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "paper_tables.json"
    csv_path = args.output_dir / "paper_model_summary.csv"
    md_path = args.output_dir / "paper_model_summary.md"

    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    _write_csv(payload["models"], csv_path)
    _write_markdown(payload, md_path)

    print(json.dumps({
        "num_models": payload["num_models"],
        "warnings": payload["warnings"],
        "outputs": [str(json_path), str(csv_path), str(md_path)],
    }, indent=2))


if __name__ == "__main__":
    main()
