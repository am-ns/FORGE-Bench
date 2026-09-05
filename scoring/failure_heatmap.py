#!/usr/bin/env python3
"""Application type × failure mode heatmap for FORGE-Bench.

Produces a JSON cross-tabulation matrix and optional PNG for paper inclusion.
Deliberately self-contained: no imports from sibling scoring modules to avoid
circular dependencies.
"""

from collections import defaultdict
from pathlib import Path

APPLICATION_FAILURE_LABELS = {
    "missing_required_event",
    "unclear_hazard_source",
    "unobservable_decision_element",
    "misleading_safety_response",
    "incomplete_event_loop",
    "ambiguous_spatial_relationship",
    "application_objective_not_supported",
}

APPLICATION_TYPES_ORDERED = [
    "safety_training",
    "emergency_rehearsal",
    "robotic_operation",
    "inspection_and_maintenance",
    "heavy_operation_risk",
    "defect_generation",
]

FAILURE_MODES_ORDERED = [
    "missing_required_event",
    "unclear_hazard_source",
    "unobservable_decision_element",
    "misleading_safety_response",
    "incomplete_event_loop",
    "ambiguous_spatial_relationship",
    "application_objective_not_supported",
]

_LOW_SCORE_THRESHOLD = 60.0


def _canonicalize_failure(raw: str) -> str | None:
    label = str(raw).strip().lower().replace(" ", "_").replace("-", "_")
    if label in APPLICATION_FAILURE_LABELS:
        return label
    if "missing" in label and "event" in label:
        return "missing_required_event"
    if "hazard" in label or ("unclear" in label and "source" in label):
        return "unclear_hazard_source"
    if "decision" in label or "unobservable" in label:
        return "unobservable_decision_element"
    if "mislead" in label or ("safety" in label and "response" in label):
        return "misleading_safety_response"
    if "incomplete" in label or ("event" in label and "loop" in label):
        return "incomplete_event_loop"
    if "spatial" in label or "relationship" in label or "ambiguous" in label:
        return "ambiguous_spatial_relationship"
    if "objective" in label or "unsupported" in label:
        return "application_objective_not_supported"
    return None


def _event_coverage(result: dict) -> float | None:
    scored = result.get("scored") or {}
    cov = scored.get("observable_event_coverage", result.get("observable_event_coverage"))
    if cov is not None:
        return float(cov)
    details = result.get("application_usefulness_details") or {}
    checks = details.get("required_event_checks") or []
    if checks:
        return 100.0 * sum(1 for c in checks if c.get("present") is True) / len(checks)
    return None


def _application_usefulness(result: dict) -> float | None:
    scored = result.get("scored") or {}
    v = scored.get("application_usefulness_score", result.get("application_usefulness_score"))
    if v is None:
        v = (scored.get("application_axis_scores") or {}).get("application_usefulness")
    return float(v) if v is not None else None


def _infer_failures(result: dict) -> list[str]:
    """Infer application failure labels from a single sample result."""
    labels: set[str] = set()

    details = result.get("application_usefulness_details") or {}
    for mode in details.get("failure_modes") or []:
        canonical = _canonicalize_failure(str(mode))
        if canonical:
            labels.add(canonical)

    checks = details.get("required_event_checks") or []
    if any(c.get("present") is False for c in checks):
        labels.add("missing_required_event")

    coverage = _event_coverage(result)
    if coverage is not None and coverage < _LOW_SCORE_THRESHOLD:
        labels.add("incomplete_event_loop")

    usefulness = _application_usefulness(result)
    if usefulness is not None and usefulness < _LOW_SCORE_THRESHOLD and not labels:
        labels.add("application_objective_not_supported")

    return sorted(labels)


def _ordered_app_types(totals: dict[str, int]) -> list[str]:
    ordered = [a for a in APPLICATION_TYPES_ORDERED if a in totals]
    extras = sorted(a for a in totals if a not in APPLICATION_TYPES_ORDERED)
    return ordered + extras


def build_matrix_for_display(sample_results: list[dict]) -> dict:
    """Build application_type x failure_mode count and rate matrix."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    totals: dict[str, int] = defaultdict(int)
    failed_samples: dict[str, int] = defaultdict(int)
    failure_label_totals: dict[str, int] = defaultdict(int)

    for result in sample_results:
        app_type = str(result.get("application_type") or "unknown")
        totals[app_type] += 1
        failures = _infer_failures(result)
        if failures:
            failed_samples[app_type] += 1
        failure_label_totals[app_type] += len(failures)
        for failure in failures:
            counts[app_type][failure] += 1

    app_types = _ordered_app_types(totals)
    failure_modes = FAILURE_MODES_ORDERED
    n_completed = sum(totals.values())

    rows: dict[str, dict] = {}
    for app_type in app_types:
        total = totals[app_type]
        row_counts = counts[app_type]
        rows[app_type] = {
            "total_samples": total,
            "failures": {
                mode: {
                    "count": row_counts.get(mode, 0),
                    "rate": round(row_counts.get(mode, 0) / total, 4) if total else 0.0,
                }
                for mode in failure_modes
            },
            "any_failure_count": failed_samples[app_type],
            "any_failure_rate": round(failed_samples[app_type] / total, 4) if total else 0.0,
            "failure_label_count": failure_label_totals[app_type],
            "mean_failure_labels_per_sample": round(
                failure_label_totals[app_type] / total, 4
            ) if total else 0.0,
        }

    col_totals = {
        mode: sum(counts.get(a, {}).get(mode, 0) for a in app_types)
        for mode in failure_modes
    }

    return {
        "matrix": rows,
        "column_totals": {
            mode: {
                "count": col_totals[mode],
                "rate": round(col_totals[mode] / n_completed, 4) if n_completed else 0.0,
            }
            for mode in failure_modes
        },
        "n_completed": n_completed,
        "application_types": app_types,
        "failure_modes": failure_modes,
        "interpretation": (
            "per-mode rate and any_failure_rate are sample proportions; "
            "mean_failure_labels_per_sample is label incidence and may exceed 1"
        ),
    }


def save_heatmap_png(matrix_data: dict, path: str | Path) -> bool:
    """Render heatmap as PNG. Returns False if matplotlib is not available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    app_types = matrix_data["application_types"]
    failure_modes = matrix_data["failure_modes"]
    matrix = matrix_data["matrix"]

    data = [
        [
            matrix.get(a, {}).get("failures", {}).get(m, {}).get("rate", 0.0)
            for m in failure_modes
        ]
        for a in app_types
    ]

    fig, ax = plt.subplots(figsize=(14, max(4, len(app_types) * 0.8 + 2)))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd", vmin=0.0, vmax=1.0)

    ax.set_xticks(range(len(failure_modes)))
    ax.set_xticklabels(
        [m.replace("_", "\n") for m in failure_modes],
        fontsize=8, ha="center"
    )
    ax.set_yticks(range(len(app_types)))
    ax.set_yticklabels([a.replace("_", " ") for a in app_types], fontsize=9)

    for i, a in enumerate(app_types):
        for j, m in enumerate(failure_modes):
            rate = data[i][j]
            count = matrix.get(a, {}).get("failures", {}).get(m, {}).get("count", 0)
            color = "white" if rate > 0.5 else "black"
            ax.text(
                j, i, f"{rate:.0%}\n({count})",
                ha="center", va="center", fontsize=7, color=color,
            )

    plt.colorbar(im, ax=ax, label="Failure rate")
    ax.set_xlabel("Failure mode", fontsize=10)
    ax.set_ylabel("Application type", fontsize=10)
    ax.set_title(
        "FORGE-Bench: Application Failure Rate\n"
        "Application Type × Failure Mode",
        fontsize=11, pad=12,
    )
    plt.tight_layout()
    plt.savefig(str(path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


def failure_heatmap_report(
    sample_results: list[dict],
    png_path: str | Path | None = None,
) -> dict:
    """Full failure heatmap report with optional PNG output.

    Args:
        sample_results: Per-sample evaluation results (single model).
        png_path: If given, save PNG visualization here.

    Returns:
        Dict with cross-tabulation matrix, hotspots, and PNG status.
    """
    completed = [r for r in sample_results if not r.get("skipped")]
    matrix_data = build_matrix_for_display(completed)

    app_types = matrix_data["application_types"]
    failure_modes = matrix_data["failure_modes"]
    matrix = matrix_data["matrix"]

    hotspots = []
    for app_type in app_types:
        for mode in failure_modes:
            entry = matrix.get(app_type, {}).get("failures", {}).get(mode, {})
            rate = entry.get("rate", 0.0)
            count = entry.get("count", 0)
            if count > 0:
                hotspots.append({
                    "application_type": app_type,
                    "failure_mode": mode,
                    "rate": rate,
                    "count": count,
                })
    hotspots.sort(key=lambda x: x["rate"], reverse=True)

    # Which application_type has the most overall failures?
    worst_app_types = sorted(
        app_types,
        key=lambda a: matrix.get(a, {}).get("any_failure_rate", 0.0),
        reverse=True,
    )

    png_saved = False
    if png_path is not None:
        png_saved = save_heatmap_png(matrix_data, png_path)

    return {
        **matrix_data,
        "top_hotspots": hotspots[:10],
        "worst_application_types_by_failure_rate": worst_app_types,
        "png_saved": png_saved,
        "png_path": str(png_path) if png_path else None,
    }
