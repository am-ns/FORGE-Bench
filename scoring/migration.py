"""Rebuild cached scores from original judgments without reusing old transforms."""

from copy import deepcopy

from eval.axis_registry import APPLICATION_USEFULNESS, TECHNICAL_AXES, canonicalize_axis_dict
from scoring.per_sample import score_sample
from scoring.policy import CONFIG, valid_score


def rebuild_cached_result(result: dict) -> dict:
    """Preserve evidence; fail closed if original judgments cannot be recovered."""
    row = deepcopy(result)
    scored = row.get("scored") or {}
    if row.get("skipped") or not scored or scored.get("input_errors"):
        return row
    raw = scored.get("raw_axis_scores")
    application = scored.get("raw_application_usefulness_score")
    if application is None:
        application = (row.get("application_usefulness_details") or {}).get("score")
    if application is None:
        application = row.get("application_usefulness_score")
    if isinstance(raw, dict):
        raw = canonicalize_axis_dict(raw)
        if application is None:
            application = raw.get(APPLICATION_USEFULNESS)
    if (not isinstance(raw, dict) or any(not valid_score(raw.get(a)) for a in TECHNICAL_AXES)
            or not valid_score(application)):
        row["scoring_migration_error"] = "original_six_axis_judgments_missing_or_invalid; rerun_judges"
        row["scoring_complete"] = False
        return row
    coverage = row.get("observable_event_coverage")
    if coverage is None:
        coverage = scored.get("observable_event_coverage")
    if coverage is None:
        checks = (row.get("application_usefulness_details") or {}).get("required_event_checks") or []
        if checks:
            coverage = 100.0 * sum(item.get("present") is True for item in checks) / len(checks)
    rebuilt = score_sample(
        {**raw, APPLICATION_USEFULNESS: application},
        observable_event_coverage=coverage,
        operator_evidence=row.get("operator_evidence"),
        axis_weights=scored.get("axis_weights"),
        axis_rubric=scored.get("axis_rubric"),
        task_category=row.get("task_category", scored.get("task_category")),
        viewpoint_motion=row.get("viewpoint_motion"),
        industrial_constraint_score=scored.get("industrial_constraint_score"),
    )
    row["scored"] = rebuilt
    row.pop("scoring_migration_error", None)
    for key in ("ranking_score", "overall", "paper_score", "constraint_adjusted_score", "scoring_complete"):
        row.pop(key, None)
    row["scoring_policy"] = {"version": CONFIG["version"], "config_sha256": CONFIG["config_sha256"]}
    row["scoring_migration"] = "rebuilt_from_original_judgments; video_identity_not_revalidated"
    return row
