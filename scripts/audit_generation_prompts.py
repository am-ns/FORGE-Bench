#!/usr/bin/env python3
"""Audit generation prompts for scoreable events and package consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_minimax_video_batch import compact_text


def load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["samples"] if isinstance(data, dict) else data


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def authoritative_event(sample: dict) -> str:
    title = compact_text(sample.get("task_title"))
    annotations = sample.get("constraint_annotations") or {}
    scenario = compact_text(annotations.get("domain_scenario"))
    return title or scenario


def run(samples_path: Path, canonical_path: Path, package_path: Path | None) -> dict:
    samples = load_samples(samples_path)
    canonical = {sample["task_id"]: sample for sample in load_samples(canonical_path)}
    missing_event = []
    subject_tautology = []
    over_limit = []
    canonical_mismatch = []
    for sample in samples:
        task_id = sample["task_id"]
        prompt = str(sample.get("video_generation_prompt") or "")
        event = authoritative_event(sample)
        subject = str(sample.get("reference_subject") or "")
        if not event or event not in prompt:
            missing_event.append(task_id)
        if subject and f": {subject}.".lower() in prompt.lower():
            subject_tautology.append(task_id)
        if len(prompt) > 900:
            over_limit.append(task_id)
        if task_id not in canonical or canonical[task_id].get("video_generation_prompt") != prompt:
            canonical_mismatch.append(task_id)

    package_mismatch: list[str] = []
    if package_path is not None:
        package = {row["task_id"]: row for row in load_jsonl(package_path)}
        package_mismatch = [
            sample["task_id"]
            for sample in samples
            if sample["task_id"] not in package
            or package[sample["task_id"]].get("video_generation_prompt")
            != sample.get("video_generation_prompt")
        ]

    lengths = [len(str(sample.get("video_generation_prompt") or "")) for sample in samples]
    report = {
        "samples": len(samples),
        "unique_task_ids": len({sample["task_id"] for sample in samples}),
        "min_prompt_chars": min(lengths, default=0),
        "max_prompt_chars": max(lengths, default=0),
        "missing_authoritative_event": missing_event,
        "subject_only_tautology": subject_tautology,
        "over_900_chars": over_limit,
        "canonical_prompt_mismatch": canonical_mismatch,
        "package_prompt_mismatch": package_mismatch,
    }
    report["valid"] = not any(
        report[key]
        for key in (
            "missing_authoritative_event",
            "subject_only_tautology",
            "over_900_chars",
            "canonical_prompt_mismatch",
            "package_prompt_mismatch",
        )
    ) and report["samples"] == report["unique_task_ids"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--canonical", type=Path, default=ROOT / "dataset/annotations/samples.json")
    parser.add_argument("--package-jsonl", type=Path)
    args = parser.parse_args()
    report = run(args.samples, args.canonical, args.package_jsonl)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
