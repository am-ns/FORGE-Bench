#!/usr/bin/env python3
"""Summarize low-score causes from FORGE-Bench result files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.axis_registry import (
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
    canonicalize_axis_dict,
)


DEFAULT_OUT = ROOT / "reports" / "low_score_summaries"
TECHNICAL_AXES = [
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    GEOMETRIC_INTEGRITY,
    PHYSICAL_PLAUSIBILITY,
    TEMPORAL_CONSISTENCY,
    REFERENCE_AND_MOTION_FIDELITY,
]
LOW_AXIS_THRESHOLD = 60.0
SEVERE_AXIS_THRESHOLD = 35.0

REASON_LABELS = {
    "low_geometric_integrity": "geometry/topology instability",
    "severe_geometric_integrity": "severe geometry/topology collapse",
    "low_physical_plausibility": "implausible physics or dynamics",
    "severe_physical_plausibility": "severe physical implausibility",
    "low_temporal_consistency": "temporal flicker or identity break",
    "severe_temporal_consistency": "severe temporal instability",
    "low_reference_and_motion_fidelity": "reference drift or motion-control failure",
    "severe_reference_and_motion_fidelity": "severe reference or motion failure",
    "low_industrial_logic_and_fact_alignment": "industrial logic or compliance failure",
    "severe_industrial_logic_and_fact_alignment": "severe industrial logic failure",
    "low_application_usefulness": "low industrial application usefulness",
    "zero_observable_event_coverage": "required events absent",
    "partial_observable_event_coverage": "required events only partially visible",
    "motion_under_execution": "requested camera motion under-executed",
    "operator_global_regeneration": "operator detected global scene regeneration",
    "operator_abrupt_temporal_transition": "operator detected abrupt temporal break",
    "operator_rigid_drift": "operator detected rigid-structure drift",
    "operator_fluid_discontinuity": "operator detected fluid/plume discontinuity",
    "geometric_operator_vlm_conflict": "geometry operator/VLM conflict",
}


def repo_path(path: str | Path | None) -> Path | None:
    if path is None:
        return None
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path | None, default):
    if path is None or not path.exists():
        return default
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def model_name_from_path(result_dir: Path | None, per_sample: Path | None) -> str:
    if result_dir is not None:
        return result_dir.name
    if per_sample is not None and per_sample.parent.name:
        return per_sample.parent.name
    return "model"


def result_paths(args: argparse.Namespace) -> tuple[Path | None, Path, Path | None, Path | None, str]:
    result_dir = repo_path(args.result_dir)
    per_sample = repo_path(args.per_sample) if args.per_sample else None
    aggregate = repo_path(args.aggregate) if args.aggregate else None
    report = repo_path(args.report) if args.report else None
    if result_dir is not None:
        per_sample = per_sample or result_dir / "per_sample.json"
        aggregate = aggregate or result_dir / "aggregate.json"
        report = report or result_dir / "report.json"
    if per_sample is None:
        raise SystemExit("Provide a result_dir or --per-sample")
    model = args.model or model_name_from_path(result_dir, per_sample)
    return result_dir, per_sample, aggregate, report, model


def axis_scores(sample: dict) -> dict[str, float]:
    scored = sample.get("scored") or {}
    scores = scored.get("axis_scores") or sample.get("axis_scores") or {}
    out = {}
    for axis, value in canonicalize_axis_dict(scores).items():
        try:
            out[axis] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def sample_score(sample: dict) -> float | None:
    candidates = [
        (sample.get("scored") or {}).get("ranking_score"),
        (sample.get("scored") or {}).get("weighted_score"),
        (sample.get("scored") or {}).get("technical_score"),
        sample.get("ranking_score"),
        sample.get("weighted_score"),
    ]
    for value in candidates:
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    scores = axis_scores(sample)
    values = [scores[axis] for axis in TECHNICAL_AXES if axis in scores]
    return mean(values) if values else None


def application_details(sample: dict) -> dict:
    return (
        sample.get("application_usefulness_details")
        or sample.get("application_details")
        or (sample.get("scored") or {}).get("application_usefulness_details")
        or {}
    )


def application_score(sample: dict) -> float | None:
    scored = sample.get("scored") or {}
    candidates = [
        scored.get("application_usefulness_score"),
        scored.get("application_score"),
        sample.get("application_usefulness_score"),
        sample.get("application_score"),
        application_details(sample).get("score"),
    ]
    for value in candidates:
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return None


def observable_event_coverage(sample: dict) -> float | None:
    scored = sample.get("scored") or {}
    details = application_details(sample)
    candidates = [
        scored.get("observable_event_coverage"),
        sample.get("observable_event_coverage"),
        details.get("observable_event_coverage"),
    ]
    for value in candidates:
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return None


def normalize_reason(label: str) -> str:
    return REASON_LABELS.get(label, label.replace("_", " "))


def add_reason(counter: Counter[str], examples: dict[str, list[dict]], label: str, sample: dict, detail: str = "") -> None:
    counter[label] += 1
    if len(examples[label]) < 8:
        examples[label].append({
            "task_id": sample.get("task_id"),
            "domain": sample.get("domain"),
            "task_category": sample.get("task_category"),
            "score": round(sample_score(sample), 4) if sample_score(sample) is not None else None,
            "detail": detail,
        })


def collect_sample_reasons(sample: dict) -> list[str]:
    scores = axis_scores(sample)
    reasons = []
    for axis, score in scores.items():
        if score < LOW_AXIS_THRESHOLD:
            reasons.append(f"low_{axis}")
        if score < SEVERE_AXIS_THRESHOLD:
            reasons.append(f"severe_{axis}")

    app = application_score(sample)
    if app is not None and app < LOW_AXIS_THRESHOLD:
        reasons.append("low_application_usefulness")
    coverage = observable_event_coverage(sample)
    if coverage is not None:
        if coverage <= 0:
            reasons.append("zero_observable_event_coverage")
        elif coverage < LOW_AXIS_THRESHOLD:
            reasons.append("partial_observable_event_coverage")

    motion_score = (
        (sample.get("scored") or {}).get("motion_control_score")
        or (sample.get("scored") or {}).get("viewpoint_motion_score")
        or sample.get("viewpoint_motion_score")
    )
    try:
        if motion_score is not None and float(motion_score) < LOW_AXIS_THRESHOLD:
            reasons.append("motion_under_execution")
    except (TypeError, ValueError):
        pass

    details = application_details(sample)
    for mode in details.get("failure_modes", []) or []:
        reasons.append(f"application_failure:{mode}")

    for axis, adjustments in ((sample.get("scored") or {}).get("constraint_axis_adjustments") or {}).items():
        for adjustment in adjustments or []:
            reason = adjustment.get("reason")
            if reason:
                reasons.append(str(reason))

    conflict = sample.get("geometric_integrity_conflict_details") or {}
    if conflict.get("conflict") is True:
        reasons.append("geometric_operator_vlm_conflict")

    operators = (sample.get("operator_evidence") or {}).get("operators") or {}
    if (operators.get("local_region_lock") or {}).get("risk") == "global_regeneration":
        reasons.append("operator_global_regeneration")
    if (operators.get("temporal_break") or {}).get("abrupt_transition") is True:
        reasons.append("operator_abrupt_temporal_transition")
    if (operators.get("rigid_joint_tracking") or {}).get("risk") == "rigid_drift":
        reasons.append("operator_rigid_drift")
    if (operators.get("fluid_diffusion") or {}).get("plausible_continuity") is False:
        reasons.append("operator_fluid_discontinuity")

    return sorted(set(reasons))


def summarize(per_sample: list[dict], aggregate: dict, report: dict, model: str, top_n: int) -> dict:
    completed = [sample for sample in per_sample if not sample.get("skipped")]
    reason_counts: Counter[str] = Counter()
    reason_examples: dict[str, list[dict]] = defaultdict(list)
    domain_low: Counter[str] = Counter()
    task_low: Counter[str] = Counter()
    axis_values: dict[str, list[float]] = defaultdict(list)
    per_sample_reasons = {}

    for sample in completed:
        scores = axis_scores(sample)
        for axis, score in scores.items():
            axis_values[axis].append(score)
        reasons = collect_sample_reasons(sample)
        per_sample_reasons[str(sample.get("task_id"))] = reasons
        if reasons:
            if sample.get("domain"):
                domain_low[str(sample["domain"])] += 1
            if sample.get("task_category"):
                task_low[str(sample["task_category"])] += 1
        for reason in reasons:
            add_reason(reason_counts, reason_examples, reason, sample)

    worst_samples = []
    for sample in sorted(
        (sample for sample in completed if sample_score(sample) is not None),
        key=lambda item: sample_score(item) or 0.0,
    )[:top_n]:
        scores = axis_scores(sample)
        weakest_axis = min(scores, key=scores.get) if scores else None
        worst_samples.append({
            "task_id": sample.get("task_id"),
            "domain": sample.get("domain"),
            "task_category": sample.get("task_category"),
            "scene_id": sample.get("scene_id"),
            "motion_type": sample.get("motion_type"),
            "score": round(sample_score(sample) or 0.0, 4),
            "weakest_axis": weakest_axis,
            "weakest_axis_score": round(scores[weakest_axis], 4) if weakest_axis else None,
            "reasons": [
                {"code": reason, "label": normalize_reason(reason)}
                for reason in per_sample_reasons.get(str(sample.get("task_id")), [])[:8]
            ],
        })

    axis_summary = {}
    for axis, values in sorted(axis_values.items()):
        axis_summary[axis] = {
            "mean": round(mean(values), 4) if values else None,
            "min": round(min(values), 4) if values else None,
            "low_count": sum(value < LOW_AXIS_THRESHOLD for value in values),
            "severe_count": sum(value < SEVERE_AXIS_THRESHOLD for value in values),
        }

    top_reasons = [
        {
            "code": reason,
            "label": normalize_reason(reason),
            "count": count,
            "examples": reason_examples.get(reason, []),
        }
        for reason, count in reason_counts.most_common(top_n)
    ]

    return {
        "model": model,
        "num_samples_total": len(per_sample),
        "num_samples_completed": len(completed),
        "headline_scores": {
            "ranking_score": aggregate.get("ranking_score") or aggregate.get("overall"),
            "technical_score": aggregate.get("technical_score"),
            "application_score_strict": aggregate.get("application_score_strict"),
            "strict_pass_rate": aggregate.get("strict_pass_rate"),
            "functional_pass_rate": aggregate.get("functional_pass_rate"),
        },
        "top_low_score_reasons": top_reasons,
        "axis_summary": axis_summary,
        "low_score_domains": dict(domain_low.most_common()),
        "low_score_task_categories": dict(task_low.most_common()),
        "worst_samples": worst_samples,
        "source_report_failure_taxonomy": report.get("failure_taxonomy", {}),
        "source_constraint_adjustment_summary": aggregate.get("constraint_adjustment_summary", {}),
    }


def render_markdown(summary: dict) -> str:
    lines = [
        f"# Low-Score Reason Summary: {summary['model']}",
        "",
        "## Headline",
        "",
    ]
    scores = summary["headline_scores"]
    for key in ("ranking_score", "technical_score", "application_score_strict", "strict_pass_rate", "functional_pass_rate"):
        lines.append(f"- `{key}`: {scores.get(key)}")

    lines.extend(["", "## Main Low-Score Reasons", ""])
    if summary["top_low_score_reasons"]:
        for index, item in enumerate(summary["top_low_score_reasons"], start=1):
            examples = ", ".join(str(ex["task_id"]) for ex in item.get("examples", []) if ex.get("task_id"))
            lines.append(f"{index}. **{item['label']}** (`{item['code']}`): {item['count']} sample(s)")
            if examples:
                lines.append(f"   Examples: {examples}")
    else:
        lines.append("No low-score reasons were detected from the available result fields.")

    lines.extend(["", "## Weakest Axes", "", "| Axis | Mean | Min | Low Count | Severe Count |", "|---|---:|---:|---:|---:|"])
    for axis, stats in sorted(summary["axis_summary"].items(), key=lambda item: (item[1]["mean"] is None, item[1]["mean"] or 999)):
        lines.append(
            f"| `{axis}` | {stats['mean']} | {stats['min']} | {stats['low_count']} | {stats['severe_count']} |"
        )

    lines.extend(["", "## Low-Score Concentration", ""])
    lines.append("Domains:")
    for domain, count in summary["low_score_domains"].items():
        lines.append(f"- `{domain}`: {count}")
    lines.append("")
    lines.append("Task categories:")
    for task, count in summary["low_score_task_categories"].items():
        lines.append(f"- `{task}`: {count}")

    lines.extend(["", "## Worst Samples", "", "| Task | Score | Domain | Task Category | Weakest Axis | Reasons |", "|---|---:|---|---|---|---|"])
    for sample in summary["worst_samples"]:
        reasons = "; ".join(reason["label"] for reason in sample.get("reasons", []))
        lines.append(
            f"| `{sample.get('task_id')}` | {sample.get('score')} | `{sample.get('domain')}` | "
            f"`{sample.get('task_category')}` | `{sample.get('weakest_axis')}`={sample.get('weakest_axis_score')} | {reasons} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", nargs="?", help="Directory containing per_sample.json, aggregate.json, and report.json")
    parser.add_argument("--per-sample", help="Path to per_sample.json")
    parser.add_argument("--aggregate", help="Path to aggregate.json")
    parser.add_argument("--report", help="Path to report.json")
    parser.add_argument("--model", help="Model name for output titles")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--top-n", type=int, default=12)
    args = parser.parse_args()

    _, per_sample_path, aggregate_path, report_path, model = result_paths(args)
    per_sample = load_json(per_sample_path, [])
    aggregate = load_json(aggregate_path, {})
    report = load_json(report_path, {})
    if not isinstance(per_sample, list):
        raise SystemExit("per_sample.json must contain a list")

    summary = summarize(per_sample, aggregate, report, model, args.top_n)
    output_dir = repo_path(args.output_dir) or DEFAULT_OUT
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in model)
    json_path = output_dir / f"{stem}_low_score_summary.json"
    md_path = output_dir / f"{stem}_low_score_summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({
        "model": model,
        "json": display_path(json_path),
        "markdown": display_path(md_path),
        "top_reason_count": len(summary["top_low_score_reasons"]),
        "worst_sample_count": len(summary["worst_samples"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
