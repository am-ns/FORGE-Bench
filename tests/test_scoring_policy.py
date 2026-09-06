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
from scoring.policy import CONFIG, load_policy


TECHNICAL_80 = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80.0,
    GEOMETRIC_INTEGRITY: 80.0,
    PHYSICAL_PLAUSIBILITY: 80.0,
    TEMPORAL_CONSISTENCY: 80.0,
    REFERENCE_AND_MOTION_FIDELITY: 80.0,
}


def _result(scored, **extra):
    return {"task_id": "sample", "skipped": False, "scored": scored, **extra}


def test_frozen_policy_is_exact_5plus1():
    assert len(CONFIG["technical_axes"]) == 5
    assert CONFIG["technical_weight"] == pytest.approx(0.8)
    assert CONFIG["application_weight"] == pytest.approx(0.2)
    assert CONFIG["application_axis"] == APPLICATION_USEFULNESS
    assert len(CONFIG["config_sha256"]) == 64


def test_policy_rejects_invalid_weights(tmp_path):
    broken = dict(CONFIG)
    broken.pop("config_sha256", None)
    broken["technical_weight"] = 0.9
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="must sum to 1"):
        load_policy(path)


def test_5plus1_base_formula_and_event_gate_are_separate():
    scored = score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 100.0}, observable_event_coverage=0.0)
    result = _result(scored)
    assert scored["application_score"] == 100.0
    assert compute_sample_ranking_score(result) == 0.0
    aggregate = aggregate_sample_results([result])
    assert aggregate["linear_ranking_score"] == pytest.approx(84.0)
    assert aggregate["ranking_score"] == pytest.approx(0.0)
    ledger = aggregate["constraint_adjustment_summary"]["per_sample_gate_ledger"][0]["gates"]
    event = next(row for row in ledger if row["gate"] == "observable_event_coverage")
    assert event == {
        "gate": "observable_event_coverage",
        "action": "cap",
        "value": 0.0,
        "reasons": ["zero_observable_event_coverage"],
        "applied": True,
    }


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
    assert scored["axis_scores"][REFERENCE_AND_MOTION_FIDELITY] == 60.0
    assert scored["axis_scores"][TEMPORAL_CONSISTENCY] == 50.0
    result = _result(scored, operator_evidence=evidence)
    aggregate = aggregate_sample_results([result])
    # Frozen task-category weights produce a 74.4 linear 5+1 score. No second cap.
    assert aggregate["linear_ranking_score"] == pytest.approx(74.4)
    assert aggregate["ranking_score"] == pytest.approx(74.4)
    assert aggregate["constraint_adjustment_summary"]["samples_with_cap"] == 0
    reasons = aggregate["constraint_adjustment_summary"]["cap_reason_counts"]
    assert reasons["operator_gate_already_applied_to_axis"] == 1


def test_task_realization_is_diagnostic_not_an_alternative_total():
    scored = score_sample({**TECHNICAL_80, APPLICATION_USEFULNESS: 100.0}, observable_event_coverage=60.0)
    aggregate = aggregate_sample_results([_result(scored)])
    task = aggregate["task_realization"]
    assert task["task_success_rate"] == 1.0
    assert task["task_realization_mean"] == pytest.approx((60 + 80 + 80) / 3)
    assert task["conditional_quality_success_only"] == pytest.approx(80.0)
    assert aggregate["linear_ranking_score"] == pytest.approx(84.0)
    # Coverage 60 is incomplete (<100), so the canonical event gate caps at 40.
    assert aggregate["ranking_score"] == pytest.approx(40.0)


def test_incomplete_manifest_is_not_publishable():
    scored = score_sample(TECHNICAL_80)
    aggregate = aggregate_sample_results([_result(scored)])
    assert aggregate["ranking_score"] is None
    assert aggregate["overall"] is None
    assert aggregate["ranking_status"] == "incomplete"
    assert aggregate["ranking_publishable"] is False
