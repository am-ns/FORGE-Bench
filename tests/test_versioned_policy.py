import pytest

from scoring.versioned_policy import arbitrate_score, deduplicate_failure_penalty, extract_independent_evidence, resolve_config, rescore_sample, score_reasoning_detail
from scripts.eval_hailuo_qwen_omni import axis_evidence_contradictions, degenerate_axis_pattern, normalized_binary_pattern


def test_conflict_requires_valid_confident_independent_evidence():
    cfg = resolve_config()
    assert arbitrate_score(90, {"score": 10, "confidence": .9, "validity": "invalid"}, cfg)["score"] == 90
    row = arbitrate_score(90, {"score": 10, "confidence": .9, "validity": "valid"}, cfg)
    assert row["conflict"] is True
    assert 10 < row["score"] < 90


def test_duplicate_failure_family_is_deduplicated_without_headline_penalty():
    row = deduplicate_failure_penalty(["missing_event", "missing_consequence", "geometry_warp"], resolve_config())
    assert row["duplicate_count"] == 1
    assert row["penalty"] == 0
    assert row["distinct_family_count"] == 2


def test_reasoning_detail_uses_only_binary_question_accuracy():
    result = score_reasoning_detail({"per_question": [{"id": "q1", "correct": True}, {"id": "q2", "correct": False}]})
    assert result["score"] == 50
    assert result["available"] is True


def test_reasoning_detail_is_unavailable_without_complete_binary_answers():
    assert score_reasoning_detail(None)["score"] is None
    incomplete = score_reasoning_detail({"per_question": [{"id": "q1", "answer": "yes"}]})
    assert incomplete["score"] is None
    assert incomplete["unavailable_reason"] == "incomplete_binary_answers"


def test_rescore_is_versioned_bounded_and_deterministic():
    sample = {"scores": {"industrial_logic_and_fact_alignment": 80, "geometric_integrity": 80, "physical_plausibility": 80, "temporal_consistency": 80, "reference_and_motion_fidelity": 80, "application_usefulness": 60}, "reasoning": "Frames show visible evidence.", "failure_modes": [], "confidence": .8}
    first = rescore_sample(sample); second = rescore_sample(sample)
    assert first == second
    assert first["policy_version"] == "forge-bench-paper-v4.2.2"
    assert len(first["scoring_config"]["source_config_sha256"]) == 64
    assert len(first["scoring_config"]["resolved_config_sha256"]) == 64
    assert first["scoring_config"]["source_config_sha256"] != first["scoring_config"]["resolved_config_sha256"]
    assert 0 <= first["headline_score_v4"] <= 100


def test_reasoning_cannot_rescue_zero_quality_sample():
    sample = {"scores": {axis: 0 for axis in resolve_config()["axis_weights"]} | {"application_usefulness": 0}, "reasoning": "Frames clearly show visible evidence because every failure is carefully explained.", "failure_modes": ["missing_event"], "confidence": 1.0}
    assert rescore_sample(sample)["headline_score_v4"] == 0


def test_reasoning_is_diagnostic_only_and_not_in_headline():
    scores = {axis: 80 for axis in resolve_config()["axis_weights"]} | {"application_usefulness": 60}
    weak = rescore_sample({"scores": scores, "reasoning": "bad", "failure_modes": []})
    strong = rescore_sample({"scores": scores, "reasoning": "Frames show visible causal evidence because the event completes.", "failure_modes": []})
    assert weak["headline_score_v4"] == strong["headline_score_v4"] == pytest.approx(60.8)


def test_zero_event_coverage_triggers_original_cap():
    scores = {axis: 90 for axis in resolve_config()["axis_weights"]} | {"application_usefulness": 90}
    result = rescore_sample({"scores": scores, "observable_event_coverage": 0, "failure_modes": []})
    assert result["base_quality_score"] == 90
    assert result["headline_score_v4"] == 0
    assert "zero_observable_event_coverage" in result["gate_adjustment"]["gate_reasons"]
    assert result["gate_adjustment"]["event_coverage_gate"] == 0


def test_partial_event_coverage_triggers_original_cap():
    scores = {axis: 90 for axis in resolve_config()["axis_weights"]} | {"application_usefulness": 90}
    result = rescore_sample({"scores": scores, "observable_event_coverage": 40, "failure_modes": []})
    assert result["headline_score_v4"] == pytest.approx(34.2)
    assert result["gate_adjustment"]["gate_applied"] is True


def test_operator_evidence_is_mapped_to_axis_arbitration():
    sample = {"operator_evidence": {"operators": {"temporal_break": {"result_score": 0.2, "confidence": 0.9, "validity": "valid"}}}}
    evidence = extract_independent_evidence(sample)
    assert evidence["temporal_consistency"]["score"] == 20.0


def test_degenerate_axis_pattern_detection():
    assert degenerate_axis_pattern({axis: 0 for axis in ("industrial_logic_and_fact_alignment", "geometric_integrity", "physical_plausibility", "temporal_consistency", "reference_and_motion_fidelity", "application_usefulness")}) == "all_axes_zero"


def test_binary_review_scale_is_rejected():
    axes = ("industrial_logic_and_fact_alignment", "geometric_integrity", "physical_plausibility", "temporal_consistency", "reference_and_motion_fidelity", "application_usefulness")
    assert normalized_binary_pattern({axis: 1 for axis in axes}) is True
    assert normalized_binary_pattern({axis: 0 for axis in axes}) is False
    assert normalized_binary_pattern({axis: 60 for axis in axes}) is False


def test_positive_axis_evidence_cannot_pair_with_near_zero_score():
    parsed = {"geometric_integrity": 0, "axis_evidence": {"geometric_integrity": "Geometry remains preserved and consistent across frames."}}
    assert axis_evidence_contradictions(parsed) == ["geometric_integrity"]
