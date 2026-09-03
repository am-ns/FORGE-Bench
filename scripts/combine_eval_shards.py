#!/usr/bin/env python3
"""Combine sharded FORGE evaluation result directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.axis_registry import MODEL_EVALUATION_AXES, PHYSICAL_PLAUSIBILITY, GEOMETRIC_INTEGRITY
from scoring.aggregate import aggregate_sample_results
from scoring.report import generate_diagnostic_report, generate_report
from eval.metadata import build_run_metadata


SPECIAL = {"aggregate", "per_sample", "report", "run_metadata"}


def load_sample_results(shard_dirs: list[Path]) -> dict[str, dict]:
    results: dict[str, dict] = {}

    def quality(result: dict) -> tuple:
        validity = result.get("scoring_validity") or {}
        present = validity.get("present_axes") or []
        missing = validity.get("missing_required_axes") or []
        invalid = validity.get("invalid_judge_outputs") or []
        return (
            bool(result.get("scoring_complete")),
            result.get("sample_status") == "valid",
            not bool(result.get("skipped")),
            len(present),
            -len(missing),
            -len(invalid),
        )

    for shard_dir in shard_dirs:
        for path in shard_dir.glob("*.json"):
            if path.stem in SPECIAL:
                continue
            with path.open(encoding="utf-8") as f:
                result = json.load(f)
            task_id = result.get("task_id") or path.stem
            previous = results.get(task_id)
            # A transport failure in a later retry must never overwrite a
            # more complete earlier judgment. Equal-quality later retries do
            # replace earlier ones, preserving deterministic retry semantics.
            if previous is None or quality(result) >= quality(previous):
                results[task_id] = result
    return results


def load_shard_metadata(shard_dirs: list[Path]) -> list[dict]:
    metadata = []
    for shard_dir in shard_dirs:
        path = shard_dir / "run_metadata.json"
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as f:
            metadata.append(json.load(f))
    return metadata


def aggregate_group(results: list[dict]) -> dict:
    aggregate = aggregate_sample_results(results)
    axis_means = aggregate.get("axis_scores", {})
    aggregate["num_samples"] = len(results)
    aggregate["low_fidelity_flags"] = {
        "physical_plausibility_low": axis_means.get(PHYSICAL_PLAUSIBILITY, 100.0) < 35.0,
        "geometric_integrity_low": axis_means.get(GEOMETRIC_INTEGRITY, 100.0) < 35.0,
    }
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples_json", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("shard_dirs", nargs="+")
    args = parser.parse_args()

    shard_dirs = [Path(p) for p in args.shard_dirs]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_by_id = load_sample_results(shard_dirs)
    with open(args.samples_json, encoding="utf-8") as f:
        sample_order = [s["task_id"] for s in json.load(f)["samples"]]
    all_results = [results_by_id[task_id] for task_id in sample_order if task_id in results_by_id]

    for result in all_results:
        task_id = result["task_id"]
        with (output_dir / f"{task_id}.json").open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

    aggregate = aggregate_sample_results(all_results)
    shard_metadata = load_shard_metadata(shard_dirs)
    base_metadata = shard_metadata[0] if shard_metadata else {}
    run_metadata = build_run_metadata(
        model_name=args.model,
        video_dir=base_metadata.get("video_dir", ""),
        samples_json=args.samples_json,
        output_dir=str(output_dir),
        llm_provider=base_metadata.get("llm_provider", "openai_compat"),
        use_llm=bool(base_metadata.get("llm_enabled", True)),
        model_answers_path=base_metadata.get("model_answers_path"),
    )
    run_metadata["combined_from_shards"] = [str(p) for p in shard_dirs]
    run_metadata["source_shard_metadata"] = shard_metadata
    aggregate["run_metadata"] = run_metadata
    completed = [r for r in all_results if not r.get("skipped")]
    if completed:
        aggregate["domain_breakdown"] = {
            domain: aggregate_group([r for r in completed if r.get("domain") == domain])
            for domain in sorted({r.get("domain") for r in completed})
        }
        aggregate["task_breakdown"] = {
            task: aggregate_group([r for r in completed if r.get("task_category") == task])
            for task in sorted({r.get("task_category") for r in completed})
        }
        aggregate["difficulty_breakdown"] = {
            level: aggregate_group([r for r in completed if r.get("difficulty_level") == level])
            for level in sorted({r.get("difficulty_level") for r in completed if r.get("difficulty_level")})
        }
        aggregate["model_evaluation_axes"] = MODEL_EVALUATION_AXES
        aggregate["low_fidelity_summary"] = {
            "domains_physical_low": [
                domain
                for domain, item in aggregate["domain_breakdown"].items()
                if item["low_fidelity_flags"]["physical_plausibility_low"]
            ],
            "domains_geometric_low": [
                domain
                for domain, item in aggregate["domain_breakdown"].items()
                if item["low_fidelity_flags"]["geometric_integrity_low"]
            ],
        }

    aggregate["combined_from_shards"] = [str(p) for p in shard_dirs]
    aggregate["num_unique_sample_files"] = len(results_by_id)

    with (output_dir / "per_sample.json").open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    with (output_dir / "aggregate.json").open("w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2, default=str)
    with (output_dir / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(run_metadata, f, indent=2, default=str)
    report = generate_report(generate_diagnostic_report(args.model, aggregate, all_results))
    with (output_dir / "report.json").open("w", encoding="utf-8") as f:
        f.write(report)

    print(json.dumps({
        "output_dir": str(output_dir),
        "num_results": len(all_results),
        "num_unique_sample_files": len(results_by_id),
        "completed": aggregate.get("num_samples_completed"),
        "skipped": aggregate.get("num_samples_skipped"),
        "overall": aggregate.get("overall"),
        "ranking_score": aggregate.get("ranking_score"),
    }, indent=2))


if __name__ == "__main__":
    main()
