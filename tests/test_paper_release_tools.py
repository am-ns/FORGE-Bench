import json
from pathlib import Path

import pytest

from eval.axis_registry import (
    APPLICATION_USEFULNESS,
    GEOMETRIC_INTEGRITY,
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT,
    PHYSICAL_PLAUSIBILITY,
    REFERENCE_AND_MOTION_FIDELITY,
    TEMPORAL_CONSISTENCY,
)
from scoring.compare import compare_paired
from scoring.aggregate import aggregate_sample_results
from scripts.reproduce_paper_tables import build_tables
from eval.llm_judge import _parse_score_0_100 as parse_anthropic_score
from eval.llm_judge_openai import _parse_score_0_100 as parse_openai_score


AXES = {
    INDUSTRIAL_LOGIC_AND_FACT_ALIGNMENT: 80.0,
    GEOMETRIC_INTEGRITY: 80.0,
    PHYSICAL_PLAUSIBILITY: 80.0,
    REFERENCE_AND_MOTION_FIDELITY: 80.0,
    TEMPORAL_CONSISTENCY: 80.0,
}


def _sample(task_id: str, weighted_score: float, app_score: float = 100.0) -> dict:
    axis_scores = dict(AXES)
    axis_scores[GEOMETRIC_INTEGRITY] = weighted_score
    return {
        "task_id": task_id,
        "scene_id": "vsec_test_scene",
        "task_category": "rigid_body_kinematics_and_coupling",
        "skipped": False,
        "observable_event_coverage": app_score,
        "scored": {
            "weighted_score": weighted_score,
            "axis_scores": axis_scores,
            "axis_weights": {axis: 1.0 for axis in axis_scores},
            "application_usefulness_score": app_score,
            "application_axis_scores": {APPLICATION_USEFULNESS: app_score},
            "observable_event_coverage": app_score,
        },
    }


def _write_per_sample(root: Path, name: str, rows: list[dict]) -> Path:
    model_dir = root / name
    model_dir.mkdir()
    (model_dir / "per_sample.json").write_text(json.dumps(rows), encoding="utf-8")
    return model_dir


def test_compare_supports_paper_ranking_score(tmp_path):
    model_a = _write_per_sample(tmp_path, "model_a", [_sample("vsec_001", 90.0), _sample("vsec_002", 80.0)])
    model_b = _write_per_sample(tmp_path, "model_b", [_sample("vsec_001", 70.0), _sample("vsec_002", 60.0)])

    result = compare_paired(model_a, model_b, score_key="ranking_score", iterations=100, seed=1)

    assert result["score_key"] == "ranking_score"
    assert result["n_paired_samples"] == 2
    assert result["bootstrap_type"] == "paired_cluster"
    assert result["n_paired_clusters"] == 1
    assert result["mean_a_minus_b"] > 0


def test_compare_supports_paper_technical_score(tmp_path):
    model_a = _write_per_sample(tmp_path, "model_a", [_sample("vsec_001", 85.0)])
    model_b = _write_per_sample(tmp_path, "model_b", [_sample("vsec_001", 65.0)])

    result = compare_paired(model_a, model_b, score_key="technical_score", iterations=10, seed=1)

    assert result["score_key"] == "technical_score"
    assert result["mean_a_minus_b"] > 0


def test_aggregate_headline_score_uses_complete_required_axes_only():
    complete = _sample("vsec_001", 90.0)
    incomplete = _sample("vsec_002", 10.0)
    incomplete["scored"]["axis_scores"].pop(TEMPORAL_CONSISTENCY)

    result = aggregate_sample_results([complete, incomplete])

    assert result["num_samples_completed"] == 2
    assert result["num_samples_complete_required_axes"] == 1
    assert result["ranking_score"] == pytest.approx(85.6)
    assert result["linear_all_sample_score"] == pytest.approx(77.8)
    assert result["scoring_validity"]["missing_required_axis_counts"][TEMPORAL_CONSISTENCY] == 1


def test_aggregate_headline_score_applies_zero_event_coverage_cap():
    sample = _sample("vsec_001", 90.0)
    sample["observable_event_coverage"] = 0.0
    sample["scored"]["observable_event_coverage"] = 0.0
    sample["scored"]["application_usefulness_score"] = 100.0
    sample["scored"]["application_axis_scores"][APPLICATION_USEFULNESS] = 100.0

    result = aggregate_sample_results([sample])

    assert result["linear_ranking_score"] == pytest.approx(79.6)
    assert result["ranking_score"] == pytest.approx(30.0)
    assert result["constraint_adjustment_summary"]["samples_with_application_event_cap"] == 1
    assert result["constraint_adjustment_summary"]["cap_reason_counts"]["zero_observable_event_coverage"] == 1


def test_judge_score_parser_does_not_recover_from_later_frame_numbers():
    assert parse_anthropic_score("Score: 82\nFrames 1 and 5 show evidence.") == 82
    assert parse_openai_score('{"score": 64, "reasoning": "ok"}') == 64
    assert parse_anthropic_score("The score is unclear.\nFrame 8 shows a defect.") is None
    assert parse_openai_score("Evidence: frame 5 is bad. Score should be low.") is None


def test_reproduce_paper_tables_sorts_and_warns_on_incomplete_runs(tmp_path):
    results_dir = tmp_path / "results"
    high = results_dir / "high_model"
    low = results_dir / "low_model"
    high.mkdir(parents=True)
    low.mkdir()
    (high / "aggregate.json").write_text(
        json.dumps({
            "ranking_score": 75.0,
            "technical_score": 82.0,
            "application_score_strict": 90.0,
            "num_samples_completed": 902,
            "num_samples_total": 902,
            "num_samples_skipped": 0,
        }),
        encoding="utf-8",
    )
    (low / "aggregate.json").write_text(
        json.dumps({
            "ranking_score": 50.0,
            "technical_score": 70.0,
            "application_score_strict": 80.0,
            "num_samples_completed": 900,
            "num_samples_total": 902,
            "num_samples_skipped": 2,
        }),
        encoding="utf-8",
    )

    payload = build_tables(results_dir, ["ranking_score", "technical_score"])

    assert [row["model"] for row in payload["models"]] == ["high_model", "low_model"]
    assert any("low_model:incomplete_run:900/902" in warning for warning in payload["warnings"])
    assert any("low_model:skipped_samples:2" in warning for warning in payload["warnings"])


def test_release_control_files_are_ascii():
    checked = [
        Path("dataset/validate.py"),
        Path("eval/run_eval.py"),
        Path("tests/test_pipeline_smoke.py"),
    ]
    for path in checked:
        path.read_text(encoding="ascii")
