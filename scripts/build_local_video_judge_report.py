#!/usr/bin/env python3
"""Build an auditable 0-100 diagnostic report from local video-judge JSONL.

This report is deliberately not the canonical FORGE 5+1 leaderboard. It
performs an exact unit conversion (0-10 to 0-100), never imputes missing axes,
and marks incomplete inputs as non-publishable.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import statistics
from pathlib import Path


AXES = ("visual_quality", "motion_naturalness", "temporal_coherence", "prompt_alignment", "overall_score")
SCHEMA_VERSION = "local-video-judge-diagnostic-v1"


def _valid_score(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and 0 <= float(value) <= 10


def _ci95(values: list[float], *, seed: int = 20260902, replicates: int = 2000) -> dict | None:
    if not values:
        return None
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(replicates))
    return {"mean": statistics.mean(values), "ci95_low": means[int(0.025 * replicates)], "ci95_high": means[int(0.975 * replicates)]}


def build(input_path: Path, output_dir: Path, expected: int | None = None) -> dict:
    latest: dict[str, dict] = {}
    history_count = malformed = 0
    with input_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            history_count += 1
            try:
                item = json.loads(line)
                latest[item["video"]] = item
            except (json.JSONDecodeError, KeyError, TypeError):
                malformed += 1

    rows = []
    issue_counts = {"remote_error": 0, "missing_required_axis": 0, "score_out_of_range": 0, "overall_alignment_contradiction": 0}
    for video, item in sorted(latest.items()):
        scores = item.get("scores") if isinstance(item.get("scores"), dict) else {}
        missing = [axis for axis in AXES if scores.get(axis) is None]
        invalid = [axis for axis in AXES if scores.get(axis) is not None and not _valid_score(scores.get(axis))]
        if item.get("error"):
            issue_counts["remote_error"] += 1
        if missing:
            issue_counts["missing_required_axis"] += 1
        if invalid:
            issue_counts["score_out_of_range"] += 1
        alignment = scores.get("prompt_alignment")
        overall = scores.get("overall_score")
        contradiction = _valid_score(alignment) and _valid_score(overall) and float(alignment) <= 4 and float(overall) >= 8
        if contradiction:
            issue_counts["overall_alignment_contradiction"] += 1
        valid = not item.get("error") and not missing and not invalid
        row = {
            "video": video,
            "status": "valid" if valid else "evaluator_invalid",
            **{f"{axis}_raw_0_10": scores.get(axis) for axis in AXES},
            **{f"{axis}_0_100": (10 * float(scores[axis]) if _valid_score(scores.get(axis)) else None) for axis in AXES},
            "audio_quality_raw_0_10": scores.get("audio_quality"),
            "overall_alignment_contradiction": contradiction,
            "validation_errors": "|".join((["remote_error"] if item.get("error") else []) + [f"missing:{x}" for x in missing] + [f"invalid:{x}" for x in invalid]),
        }
        rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["video", "status"]
    with (output_dir / "scores_0_100.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    valid_rows = [row for row in rows if row["status"] == "valid"]
    expected_count = expected if expected is not None else len(rows)
    complete = malformed == 0 and len(rows) == expected_count and len(valid_rows) == expected_count
    overall_values = [row["overall_score_0_100"] for row in valid_rows]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "score_scale": "0-100 (exactly raw 0-10 multiplied by 10; no floor or imputation)",
        "role": "auxiliary diagnostic; not the canonical FORGE 5+1 leaderboard score",
        "source": str(input_path),
        "source_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "history_rows": history_count,
        "unique_videos": len(rows),
        "expected_videos": expected_count,
        "valid_videos": len(valid_rows),
        "malformed_rows": malformed,
        "issue_counts": issue_counts,
        "overall_score_0_100": _ci95(overall_values),
        "ranking_publishable": complete,
        "non_publishable_reasons": [] if complete else [
            reason for condition, reason in (
                (malformed > 0, "malformed_jsonl_rows"),
                (len(rows) != expected_count, "unexpected_sample_count"),
                (len(valid_rows) != expected_count, "incomplete_or_invalid_required_scores"),
            ) if condition
        ],
    }
    (output_dir / "audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Local video-judge diagnostic report",
        "",
        f"- Valid samples: {len(valid_rows)}/{expected_count}",
        f"- Mean reported overall (0-100): {payload['overall_score_0_100']['mean']:.2f}" if overall_values else "- Mean reported overall: unavailable",
        f"- Publishable as a complete diagnostic table: {str(complete).lower()}",
        "- This is not the canonical FORGE 5+1 leaderboard score.",
        "",
        "## Audit issues",
        "",
        *[f"- {key}: {value}" for key, value in issue_counts.items()],
    ]
    (output_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected", type=int)
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output, args.expected), indent=2))


if __name__ == "__main__":
    main()
