#!/usr/bin/env python3
"""Retry incomplete formal samples in four shards and rebuild the combined view."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECIAL = {"aggregate", "per_sample", "report", "run_metadata"}


def invalid_task_ids(per_sample: list[dict]) -> list[str]:
    ids = []
    for item in per_sample:
        validity = item.get("scoring_validity") or {}
        if (
            item.get("sample_status") != "valid"
            or not item.get("scoring_complete")
            or validity.get("missing_required_axes")
            or validity.get("invalid_judge_outputs")
        ):
            ids.append(item["task_id"])
    return sorted(set(ids))


def prior_retry_result_dirs(run_root: Path, model: str) -> list[Path]:
    """Return all existing retry outputs in deterministic overwrite order."""
    retry_root = run_root / "retries" / model
    if not retry_root.is_dir():
        return []
    result_dirs = []
    for retry_attempt in sorted(p for p in retry_root.iterdir() if p.is_dir()):
        for index in range(4):
            result_dir = retry_attempt / f"shard_{index}" / model
            if result_dir.is_dir():
                result_dirs.append(result_dir)
    return result_dirs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--video-dir", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    combined = run_root / "combined" / args.model
    rows = json.loads((combined / "per_sample.json").read_text(encoding="utf-8"))
    retry_ids = invalid_task_ids(rows)
    if not retry_ids:
        print(json.dumps({"retry_samples": 0, "ranking_publishable": True}))
        return 0

    frozen_path = run_root / "manifests" / "frozen_samples.json"
    payload = json.loads(frozen_path.read_text(encoding="utf-8"))
    by_id = {item["task_id"]: item for item in payload["samples"]}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    attempt = run_root / "retries" / args.model / stamp
    manifest_dir = attempt / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifests = []
    for index in range(4):
        path = manifest_dir / f"shard_{index}.json"
        shard_ids = retry_ids[index::4]
        path.write_text(json.dumps({"split_id": f"retry_{stamp}_{index}", "samples": [by_id[x] for x in shard_ids]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifests.append(path)

    processes = []
    retry_result_dirs = []
    log_dir = attempt / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    for index, manifest in enumerate(manifests):
        shard_root = attempt / f"shard_{index}"
        retry_result_dirs.append(shard_root / args.model)
        out = (log_dir / f"shard_{index}.log").open("w", encoding="utf-8")
        err = (log_dir / f"shard_{index}.err.log").open("w", encoding="utf-8")
        command = [sys.executable, "-m", "eval.run_eval", "--model", args.model,
                   "--video_dir", str(args.video_dir.resolve()), "--samples_json", str(manifest),
                   "--output_dir", str(shard_root), "--llm_provider", "openai_compat"]
        processes.append((subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err), out, err))
    codes = []
    for process, out, err in processes:
        codes.append(process.wait())
        out.close(); err.close()
    if any(codes):
        print(json.dumps({"retry_samples": len(retry_ids), "return_codes": codes, "attempt": str(attempt)}))
        return 1

    original_dirs = [run_root / "shards" / args.model / f"shard_{i}" / args.model for i in range(4)]
    # Rebuild from the immutable original shards plus every retry attempt in
    # chronological order.  Later retry files overwrite earlier versions of
    # the same task.  Using only the current attempt would discard fixes made
    # by previous attempts and can make completeness go backwards.
    all_retry_dirs = prior_retry_result_dirs(run_root, args.model)
    command = [sys.executable, str(ROOT / "scripts" / "combine_eval_shards.py"),
               "--samples_json", str(frozen_path), "--output_dir", str(combined), "--model", args.model,
               *map(str, [*original_dirs, *all_retry_dirs])]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (log_dir / "combine.log").write_text(result.stdout, encoding="utf-8")
    (log_dir / "combine.err.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode:
        return result.returncode
    aggregate = json.loads((combined / "aggregate.json").read_text(encoding="utf-8"))
    summary = {"retry_samples": len(retry_ids), "attempt": str(attempt), "return_codes": codes,
               "ranking_publishable": aggregate.get("ranking_publishable"),
               "ranking_score": aggregate.get("ranking_score"),
               "complete_required_axes": aggregate.get("num_samples_complete_required_axes")}
    (attempt / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if aggregate.get("ranking_publishable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
