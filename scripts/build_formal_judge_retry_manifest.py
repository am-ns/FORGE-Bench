#!/usr/bin/env python3
"""Build a deterministic retry manifest for persisted invalid judge axes."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


SPECIAL = {"aggregate", "per_sample", "report", "run_metadata"}
SCHEMA_VERSION = "forge-invalid-judge-retry-v1"


def build(shard_dirs: list[Path], output_dir: Path) -> dict:
    by_task: dict[str, dict] = {}
    for shard in sorted(shard_dirs, key=str):
        for path in sorted(shard.glob("*.json")):
            if path.stem in SPECIAL:
                continue
            item = json.loads(path.read_text(encoding="utf-8"))
            task_id = item.get("task_id") or path.stem
            invalid = sorted(set((item.get("scoring_validity") or {}).get("invalid_judge_outputs") or []))
            if not invalid and item.get("sample_status") != "evaluator_invalid":
                continue
            by_task[task_id] = {
                "task_id": task_id,
                "invalid_axes": invalid,
                "sample_status": item.get("sample_status", "valid"),
                "source_result": path.as_posix(),
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

    rows = [by_task[key] for key in sorted(by_task)]
    axis_counts = Counter(axis for row in rows for axis in row["invalid_axes"])
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "retry_manifest.jsonl"
    manifest.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    summary = {
        "schema_version": SCHEMA_VERSION,
        "num_tasks": len(rows),
        "axis_retry_counts": dict(sorted(axis_counts.items())),
        "evaluator_invalid_samples": sum(row["sample_status"] == "evaluator_invalid" for row in rows),
        "manifest": manifest.as_posix(),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "publishable_before_retry": False if rows else True,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("shard_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.shard_dirs, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
