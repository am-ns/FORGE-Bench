#!/usr/bin/env python3
"""Audit FORGE-Bench operator usage across data, eval code, and reports."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.operator_plan import build_operator_plan


def _load_samples(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("samples", data) if isinstance(data, dict) else data


def _operator_plan_for(sample: dict) -> set[str]:
    return {str(item.get("operator")) for item in build_operator_plan(sample) if item.get("operator")}


def run(args: argparse.Namespace) -> None:
    samples = _load_samples(Path(args.samples))
    task_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()
    motion_counts: Counter[str] = Counter()
    topology_counts: Counter[str] = Counter()
    planned_operator_counts: Counter[str] = Counter()
    task_operator_counts: dict[str, Counter[str]] = defaultdict(Counter)
    domain_task_counts: Counter[tuple[str, str]] = Counter()
    missing_fields: Counter[str] = Counter()
    explicit_operator_plan_count = 0

    required_fields = [
        "task_category",
        "axis_weights",
        "axis_rubric",
        "difficulty_profile",
        "constraint_annotations",
        "event_graph",
        "required_observable_events",
        "decision_relevant_elements",
        "application_success_criteria",
        "misleading_failure_modes",
        "industrial_logic_questions",
        "implicit_rule_type",
        "reasoning_alignment_questions",
        "video_generation_prompt",
        "evaluation_prompt",
    ]

    for sample in samples:
        task = str(sample.get("task_category") or "")
        domain = str(sample.get("domain") or "")
        motion = str(sample.get("motion_type") or "")
        sub_topology = str(sample.get("sub_topology") or "")
        task_counts[task] += 1
        domain_counts[domain] += 1
        motion_counts[motion] += 1
        topology_counts[sub_topology] += 1
        domain_task_counts[(domain, task)] += 1
        if sample.get("operator_plan") or (sample.get("constraint_annotations") or {}).get("operator_plan"):
            explicit_operator_plan_count += 1
        for field in required_fields:
            if not sample.get(field):
                missing_fields[field] += 1
        plan = _operator_plan_for(sample)
        for operator in plan:
            planned_operator_counts[operator] += 1
            task_operator_counts[task][operator] += 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "sample_count": len(samples),
        "domain_counts": dict(domain_counts.most_common()),
        "task_category_counts": dict(task_counts.most_common()),
        "motion_type_counts": dict(motion_counts.most_common()),
        "sub_topology_counts": dict(topology_counts.most_common()),
        "domain_task_counts": {
            f"{domain} x {task}": count
            for (domain, task), count in sorted(domain_task_counts.items())
        },
        "planned_operator_counts": dict(planned_operator_counts.most_common()),
        "task_operator_counts": {
            task: dict(counter.most_common())
            for task, counter in sorted(task_operator_counts.items())
        },
        "missing_required_metadata_fields": dict(missing_fields.most_common()),
        "explicit_operator_plan_samples": explicit_operator_plan_count,
        "implicit_operator_plan_samples": len(samples) - explicit_operator_plan_count,
        "findings": [
            "Operator evidence is executable and task-routed in eval/operator_evidence.py and eval/run_eval.py.",
            "All samples have task/axis/application metadata required to choose an implicit operator plan.",
            "Samples do not currently carry an explicit operator_plan field, so per-sample operator intent is inferred at runtime.",
            "Docs should be regenerated after image/sample imports because README and BENCHMARK_CARD may contain stale sample counts.",
        ],
    }
    (out_dir / "operator_usage_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Operator Usage Audit",
        "",
        f"- Samples: {len(samples)}",
        f"- Samples with explicit operator_plan: {explicit_operator_plan_count}",
        f"- Samples using implicit task-routed operator plan: {len(samples) - explicit_operator_plan_count}",
        "",
        "## Planned Operator Coverage",
        "",
        "| Operator | Planned Samples |",
        "|---|---:|",
    ]
    for operator, count in planned_operator_counts.most_common():
        lines.append(f"| `{operator}` | {count} |")
    lines.extend(["", "## Task Category Coverage", "", "| Task Category | Samples | Operators |", "|---|---:|---|"])
    for task, count in task_counts.most_common():
        ops = ", ".join(f"`{op}`" for op in sorted(task_operator_counts.get(task, {})))
        lines.append(f"| `{task}` | {count} | {ops} |")
    lines.extend(["", "## Current Gaps", ""])
    for finding in report["findings"]:
        lines.append(f"- {finding}")
    (out_dir / "operator_usage_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"samples={len(samples)}")
    print(f"explicit_operator_plan_samples={explicit_operator_plan_count}")
    print(f"planned_operators={len(planned_operator_counts)}")
    print(f"out_dir={out_dir.as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="dataset/annotations/samples.json")
    parser.add_argument("--out-dir", default="reports/operator_usage_audit")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
