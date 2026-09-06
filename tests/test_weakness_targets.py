import json
from pathlib import Path

from eval.reasoning_alignment import build_reasoning_alignment_questions
from eval.weakness_targets import (
    WEAKNESS_TARGETS,
    WEAKNESS_TARGET_TO_RULE_TYPE,
    complete_sample_weakness_targets,
)
from scoring.weakness_targets import (
    TAXONOMY_VERSION,
    backfill_result,
    compare_model_summaries,
    diagnose_result,
    summarize_results,
    taxonomy_manifest,
    validate_sample_targets,
)


def _sample():
    return {
        "task_id": "demo_001",
        "motion_type": "static",
        "viewpoint_motion_target": 0.0,
        "constraint_annotations": {"domain_scenario": "a valve closes after an alarm"},
        "required_observable_events": ["the valve visibly closes"],
        "application_success_criteria": ["an operator can verify isolation"],
        "industrial_logic_questions": [{
            "id": "custom",
            "text": "Does the curated causal event occur?",
            "answer": "yes",
            "weakness_target": "causal_chain_completeness",
        }],
    }


def test_completion_is_full_idempotent_and_preserves_curated_text():
    sample = complete_sample_weakness_targets(_sample())
    first = json.dumps(sample, sort_keys=True)
    complete_sample_weakness_targets(sample)

    assert json.dumps(sample, sort_keys=True) == first
    assert [q["weakness_target"] for q in sample["industrial_logic_questions"]] == list(WEAKNESS_TARGETS)
    assert sample["industrial_logic_questions"][0]["text"] == "Does the curated causal event occur?"
    assert len(sample["reasoning_alignment_questions"]) == 9


def test_reasoning_mapping_covers_every_weakness_target():
    sample = complete_sample_weakness_targets(_sample())
    questions = build_reasoning_alignment_questions(sample)

    assert {q["weakness_target"] for q in questions} == set(WEAKNESS_TARGETS)
    assert all(
        q["implicit_rule_type"] == WEAKNESS_TARGET_TO_RULE_TYPE[q["weakness_target"]]
        for q in questions
    )


def test_executable_annotation_files_have_complete_target_coverage():
    root = Path(__file__).resolve().parents[1]
    for relative in (
        "dataset/annotations/samples.json",
        "dataset/annotations/video_generation_500_samples.json",
    ):
        data = json.loads((root / relative).read_text(encoding="utf-8"))
        samples = data.get("samples", data)
        for sample in samples:
            assert [q["weakness_target"] for q in sample["industrial_logic_questions"]] == list(WEAKNESS_TARGETS)
            assert [q["weakness_target"] for q in sample["reasoning_alignment_questions"]] == list(WEAKNESS_TARGETS)


def test_frozen_taxonomy_uses_five_plus_one_dimensions_and_nine_targets():
    manifest = taxonomy_manifest()
    assert manifest["taxonomy_version"] == TAXONOMY_VERSION
    assert manifest["dimensions"] == [
        "industrial_logic_and_fact_alignment",
        "geometric_integrity",
        "physical_plausibility",
        "temporal_consistency",
        "reference_and_motion_fidelity",
        "application_usefulness",
    ]
    assert list(manifest["targets"]) == list(WEAKNESS_TARGETS)


def test_validator_rejects_duplicate_missing_and_wrong_rule_mapping():
    sample = complete_sample_weakness_targets(_sample())
    sample["reasoning_alignment_questions"][0]["implicit_rule_type"] = "temporal_order"
    sample["industrial_logic_questions"][1]["weakness_target"] = WEAKNESS_TARGETS[0]
    errors = validate_sample_targets(sample)
    assert any("rule type does not match" in error for error in errors)
    assert any("missing targets" in error for error in errors)
    assert any("duplicate targets" in error for error in errors)


def test_legacy_backfill_is_diagnostic_only_and_uses_priority_order():
    old = {
        "task_id": "old-1", "motion_type": "pan", "application_type": "safety_training",
        "scored": {"weighted_score": 71.25, "motion_control_score": 20, "application_usefulness_score": 80,
            "axis_scores": {"industrial_logic_and_fact_alignment": 10, "geometric_integrity": 90,
                "physical_plausibility": 90, "temporal_consistency": 90, "reference_and_motion_fidelity": 90}},
        "reasoning_alignment_details": {"per_question": [
            {"id": "q1", "correct": True}, {"id": "q2", "correct": False}, {"id": "q3", "correct": True}]},
    }
    filled = backfill_result(old)
    assert old.get("weakness_target_diagnostics") is None
    assert filled["scored"] == old["scored"]
    targets = filled["weakness_target_diagnostics"]["targets"]
    assert targets["causal_chain_completeness"]["status"] == "pass"
    assert targets["required_observable_event_presence"]["status"] == "fail"
    assert targets["camera_motion_execution"]["severity"] == "severe"


def test_unknown_is_not_a_pass_and_rate_uses_evidenced_denominator():
    rows = [{"task_id": "known", "scored": {"axis_scores": {"physical_plausibility": 20}}},
            {"task_id": "unknown", "scored": {"axis_scores": {}}}]
    item = summarize_results(rows)["targets"]["physical_plausibility"]
    assert (item["failure_count"], item["unknown_count"], item["evidenced_sample_count"]) == (1, 1, 1)
    assert item["failure_rate_among_evidenced"] == 1.0
    assert item["evidence_coverage_rate"] == 0.5


def test_cross_model_report_keeps_counts_and_coverage_next_to_rates():
    report = compare_model_summaries({
        "a": [{"task_id": "a", "scored": {"axis_scores": {"temporal_consistency": 10}}}],
        "b": [{"task_id": "b", "scored": {"axis_scores": {"temporal_consistency": 90}}}],
    })
    row = report["by_target"]["temporal_consistency"]
    assert row["a"]["failure_rate_among_evidenced"] == 1.0
    assert row["b"]["failure_rate_among_evidenced"] == 0.0
    assert row["a"]["evidenced_sample_count"] == 1


def test_diagnosis_marks_non_applicable_separately_from_unknown():
    targets = diagnose_result({"task_id": "x", "scored": {"axis_scores": {}}})["targets"]
    assert targets["camera_motion_execution"]["status"] == "not_applicable"
    assert targets["physical_plausibility"]["status"] == "unknown"
