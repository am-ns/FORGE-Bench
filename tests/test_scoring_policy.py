import json

import pytest

from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
)
from scoring.aggregate import aggregate_sample_results, compute_sample_ranking_score
from scoring.per_sample import score_sample
from scoring.policy import CONFIG, load_policy, publication_issue


@pytest.mark.parametrize("mutation,expected", [
    ({"version": "forge-video-v3.1"}, "obsolete_or_missing_scoring_version"),
    ({"config_sha256": "outdated"}, "scoring_config_mismatch"),
])
def test_publication_rejects_old_policy_despite_complete_flag(mutation, expected):
    aggregate = aggregate_sample_results([_result(score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 80.0}))])
    assert publication_issue(aggregate) is None
    aggregate["scoring_policy"].update(mutation)
    assert publication_issue(aggregate) == expected


def test_zero_scores_are_never_raised_by_retired_floors():
    scored = score_sample({axis: 0.0 for axis in CONFIG["headline_axes"]})
    aggregate = aggregate_sample_results([_result(scored)])
    assert aggregate["ranking_score"] == 0.0
    assert "floored_axis_scores" not in scored
    assert "floored_axis_scores" not in aggregate


TECHNICAL_80 = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80.0,
    GEOMETRIC_INTEGRITY: 80.0,
    PHYSICAL_PLAUSIBILITY: 80.0,
    TEMPORAL_CONSISTENCY: 80.0,
    REFERENCE_AND_MOTION_FIDELITY: 80.0,
}


def _result(scored, **extra):
    return {"task_id": "sample", "skipped": False, "scored": scored, **extra}


def test_frozen_policy_is_exact_six_axis_capped_mean():
    assert len(CONFIG["technical_axes"]) == 5
    assert CONFIG["application_axis"] == APPLICATION_USEFULNESS
    assert len(CONFIG["headline_axes"]) == 6
    assert CONFIG["headline_aggregation"] == "unweighted_arithmetic_mean_after_caps"
    assert CONFIG["event_coverage_cap_axes"] == CONFIG["headline_axes"]
    assert len(CONFIG["config_sha256"]) == 64


def test_policy_rejects_incomplete_headline_axes(tmp_path):
    broken = dict(CONFIG)
    broken.pop("config_sha256", None)
    broken["headline_axes"] = broken["headline_axes"][:-1]
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="headline_axes"):
        load_policy(path)


def test_policy_rejects_partial_event_cap_axes(tmp_path):
    config = dict(CONFIG)
    config.pop("config_sha256", None)
    config["event_coverage_cap_axes"] = config["event_coverage_cap_axes"][:-1]
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="event_coverage_cap_axes"):
        load_policy(path)


def test_event_coverage_caps_all_axes_before_simple_mean():
    scored = score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 100.0}, observable_event_coverage=0.0)
    result = _result(scored)
    assert scored["application_score"] == 0.0
    assert compute_sample_ranking_score(result) == pytest.approx(0.0)
    aggregate = aggregate_sample_results([result])
    assert aggregate["linear_ranking_score"] == pytest.approx(0.0)
    assert aggregate["ranking_score"] == pytest.approx(0.0)
    assert all(value == 0.0 for value in scored["axis_scores"].values())


def test_operator_gate_changes_axes_but_is_not_applied_twice():
    evidence = {
        "operators": {
            "local_region_lock": {
                "risk": "global_regeneration", "localized_change": False,
                "used_for_axis_cap": True, "confidence": 0.9, "validity": "valid",
            },
            "temporal_break": {
                "abrupt_transition": True, "late_break": True,
                "used_for_axis_cap": True, "confidence": 0.9, "validity": "valid",
            },
        }
    }
    scored = score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 100.0}, operator_evidence=evidence)
    assert scored["axis_scores"][REFERENCE_AND_MOTION_FIDELITY] == 35.0
    assert scored["axis_scores"][TEMPORAL_CONSISTENCY] == 25.0
    result = _result(scored, operator_evidence=evidence)
    aggregate = aggregate_sample_results([result])
    assert aggregate["ranking_score"] == pytest.approx((35 + 25 + 80 + 80 + 80 + 100) / 6)
    assert aggregate["constraint_adjustment_summary"]["samples_with_cap"] == 0
    reasons = aggregate["constraint_adjustment_summary"]["cap_reason_counts"]
    assert "operator_gate_already_applied_to_axis" not in reasons


def test_task_realization_is_diagnostic_not_an_alternative_total():
    scored = score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 100.0}, observable_event_coverage=60.0)
    aggregate = aggregate_sample_results([_result(scored)])
    task = aggregate["task_realization"]
    assert task["task_success_rate"] == 1.0
    assert task["task_realization_mean"] == pytest.approx(60.0)
    assert task["conditional_quality_success_only"] == pytest.approx(60.0)
    assert aggregate["linear_ranking_score"] == pytest.approx(60.0)
    assert aggregate["ranking_score"] == pytest.approx(60.0)


def test_incomplete_manifest_is_not_publishable():
    scored = score_sample(TECHNICAL_80)
    aggregate = aggregate_sample_results([_result(scored)])
    assert aggregate["ranking_score"] is None
    assert aggregate["overall"] is None
    assert aggregate["ranking_status"] == "incomplete"
    assert aggregate["ranking_publishable"] is False
