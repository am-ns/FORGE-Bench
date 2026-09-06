from scoring.failure_heatmap import build_matrix_for_display, failure_heatmap_report
from scoring.report import generate_diagnostic_report


def test_any_failure_rate_counts_samples_not_labels():
    samples = [
        {
            "task_id": "a",
            "application_type": "safety_training",
            "application_usefulness_details": {
                "failure_modes": ["missing_required_event", "misleading_safety_response"]
            },
        },
        {"task_id": "b", "application_type": "safety_training"},
    ]

    row = build_matrix_for_display(samples)["matrix"]["safety_training"]

    assert row["any_failure_count"] == 1
    assert row["any_failure_rate"] == 0.5
    assert row["failure_label_count"] == 2
    assert row["mean_failure_labels_per_sample"] == 1.0
    assert row["any_failure_rate"] <= 1.0


def test_worst_application_type_uses_sample_failure_rate():
    samples = [
        {
            "application_type": "safety_training",
            "application_usefulness_details": {
                "failure_modes": ["missing_required_event", "misleading_safety_response"]
            },
        },
        {"application_type": "safety_training"},
        {
            "application_type": "robotic_operation",
            "application_usefulness_details": {"failure_modes": ["missing_required_event"]},
        },
    ]

    report = failure_heatmap_report(samples)

    assert report["worst_application_types_by_failure_rate"][0] == "robotic_operation"


def test_failure_taxonomy_separates_task_intent_from_observed_failure():
    samples = [{
        "task_id": "task-1",
        "task_category": "topology_mutation_and_failure",
        "application_type": "safety_training",
        "risk_intensity": "high",
        "motion_type": "dolly",
        "application_usefulness_details": {
            "required_event_checks": [{"name": "collapse", "present": False}],
            "failure_modes": ["misleading_safety_response"],
        },
        "scored": {
            "axis_scores": {
                "geometric_integrity": 20,
                "physical_plausibility": 80,
                "temporal_consistency": 80,
                "reference_and_motion_fidelity": 80,
                "industrial_logic_and_fact_alignment": 20,
            },
            "application_usefulness_score": 20,
        },
    }]

    taxonomy = generate_diagnostic_report("model", {}, samples)["failure_taxonomy"]
    intent = taxonomy["task_intent"]["dimensions"]
    diagnosis = taxonomy["observed_failures"]["diagnostics"]["geometric_or_topological_failure"]

    assert set(intent) == {
        "industrial_logic_and_fact_alignment", "geometric_integrity",
        "physical_plausibility", "temporal_consistency",
        "reference_and_motion_fidelity", "application_usefulness",
    }
    assert diagnosis["dimension"] == "geometric_integrity"
    assert diagnosis["severity"]["severe_count"] == 1
    assert diagnosis["evidence_sources"] == ["axis_scores.geometric_integrity"]
    assert diagnosis["applicability"]["applicable_sample_count"] == 1
    assert diagnosis["examples"] == ["task-1"]
