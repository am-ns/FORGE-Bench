import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "eval_hailuo_qwen_omni.py"
SPEC = importlib.util.spec_from_file_location("eval_hailuo_qwen_omni", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _sample():
    return {
        "task_id": "example_001",
        "domain": "industrial",
        "task_category": "motion",
        "motion_type": "pan",
        "viewpoint_motion_target": "machine",
        "video_generation_prompt": "Show the machine moving.",
    }


def test_prompts_do_not_anchor_scores_to_zero():
    prompts = [
        MODULE.score_output_contract(),
        MODULE.axis_review_prompt(_sample(), "all_axes_zero"),
        *(MODULE.single_axis_prompt(_sample(), axis) for axis in MODULE.AXES),
    ]

    for prompt in prompts:
        compact = prompt.replace(" ", "")
        assert '"score":0' not in compact
        assert '"confidence":0' not in compact
        assert all(f'"{axis}":0' not in compact for axis in MODULE.AXES)


def test_degenerate_detection_preserves_independent_axis_policy():
    all_zero = {axis: 0 for axis in MODULE.AXES}
    all_eighty = {axis: 80 for axis in MODULE.AXES}
    independent = {axis: 20 + index * 10 for index, axis in enumerate(MODULE.AXES)}

    assert MODULE.degenerate_axis_pattern(all_zero) == "all_axes_zero"
    assert MODULE.degenerate_axis_pattern(all_eighty) == "all_axes_identical"
    assert MODULE.degenerate_axis_pattern(independent) is None


def test_parse_json_normalizes_explicit_nested_axis_scores():
    payload = {axis: {"score": 40 + index} for index, axis in enumerate(MODULE.AXES)}
    parsed = MODULE.parse_json(json.dumps(payload))
    assert parsed[MODULE.AXES[0]] == 40.0
    assert parsed[MODULE.AXES[-1]] == 45.0


def _application_payload(**overrides):
    assessment = {
        "core_event_realization": 4,
        "causal_and_outcome_completeness": 4,
        "decision_value": 4,
        "observability_and_localization": 4,
        "industrial_credibility": 4,
        "required_event_checks": [
            {"event": "trigger", "visible": True, "complete": True, "evidence_frame": 1},
            {"event": "result", "visible": True, "complete": True, "evidence_frame": 8},
        ],
        "wrong_object": False,
        "causal_order_correct": True,
        "result_visible": True,
        "decision_usable": True,
        "severe_business_error": False,
        "all_hard_constraints_pass": True,
    }
    assessment.update(overrides)
    return {"application_assessment": assessment}


def test_strict_application_score_requires_observable_prerequisites():
    score, audit = MODULE.strict_application_score(_application_payload(result_visible=False))
    assert score == 40.0
    assert (40.0, "result_not_visible") in audit["caps"]

    score, audit = MODULE.strict_application_score(
        _application_payload(core_event_realization=0)
    )
    assert score == 0.0
    assert (0.0, "core_event_missing") in audit["caps"]

    score, audit = MODULE.strict_application_score(
        _application_payload(), expected_event_count=3
    )
    assert score == 30.0
    assert (30.0, "required_event_checks_incomplete") in audit["caps"]


def test_strict_application_score_uses_frozen_component_weights():
    score, audit = MODULE.strict_application_score(
        _application_payload(
            core_event_realization=3,
            causal_and_outcome_completeness=2,
            decision_value=2,
            observability_and_localization=3,
            industrial_credibility=3,
        )
    )
    assert score == pytest.approx(63.75)
    assert audit["required_event_completion"] == 1.0
