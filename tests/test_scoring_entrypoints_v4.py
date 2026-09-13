import copy
import csv
import json

import pytest

from scoring.aggregate import compute_sample_ranking_score
from scoring.compare import compare_paired
from scoring.discriminative_power import _extract_score
from scoring.per_sample import score_sample
from scoring.policy import CONFIG
from scoring.report import _worst_samples
from scripts.analyze_judge_robustness import _score
from scripts.build_video_evaluation_report import _row, build
from scripts.summarize_low_score_reasons import sample_score
from eval.calibration.difficulty_report import compute_bucket_scores, load_model_results
from scoring.report import _group_scores
from scripts.reaggregate_cached_results import reaggregate_result_dir
from scripts.retry_formal_incomplete import invalid_task_ids


def sample(coverage=35):
    return {
        "task_id": "sample", "sample_status": "valid", "ranking_score": 99,
        "observable_event_coverage": coverage,
        "scored": {
            **score_sample({axis: 80 for axis in CONFIG["headline_axes"]}),
            "ranking_score": 98, "constraint_adjusted_score": 97,
            "weighted_score": 96,
        },
    }


@pytest.mark.parametrize("reader", [compute_sample_ranking_score, _extract_score, _score, sample_score, lambda r: _row(r)["ranking_score"]])
def test_consumers_ignore_stale_totals(reader):
    assert reader(sample()) == 35
    assert reader(sample(0)) == 0


@pytest.mark.parametrize("reader", [compute_sample_ranking_score, _extract_score, _score, sample_score, lambda r: _row(r)["ranking_score"]])
def test_consumers_do_not_fallback_for_incomplete_or_failed_judges(reader):
    row = sample()
    del row["scored"]["axis_scores"][CONFIG["technical_axes"][0]]
    assert reader(row) is None
    row = sample()
    row["sample_status"] = "evaluator_invalid"
    assert reader(row) is None


def test_report_csv_matches_recomputed_aggregate(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps([sample()]), encoding="utf-8")
    out = tmp_path / "report"
    aggregate = build(source, out)
    with (out / "scores.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert float(rows[0]["ranking_score"]) == aggregate["ranking_score"] == 35
    assert aggregate["csv_recalculation"]["ranking_score"] == 35


def test_comparison_default_uses_current_score(tmp_path):
    for name, coverage in [("a", 35), ("b", 70)]:
        directory = tmp_path / name
        directory.mkdir()
        (directory / "per_sample.json").write_text(json.dumps([sample(coverage)]), encoding="utf-8")
    result = compare_paired(tmp_path / "a", tmp_path / "b", iterations=10)
    assert result["score_key"] == "ranking_score"


def test_worst_samples_use_current_ranking():
    low, high = sample(10), sample(70)
    high["task_id"] = "high"
    high["scored"]["weighted_score"] = 0
    rows = _worst_samples([high, low])
    assert rows[0]["task_id"] == "sample"
    assert rows[0]["ranking_score"] == 10


def test_diagnostic_groups_and_difficulty_use_current_score(tmp_path):
    row = sample(0)
    row["domain"] = "factory"
    assert _group_scores([row], "domain")["factory"]["mean_ranking_score"] == 0
    (tmp_path / "per_sample.json").write_text(json.dumps([row]), encoding="utf-8")
    results = load_model_results(str(tmp_path))
    buckets = compute_bucket_scores({"sample": {"difficulty_profile": {"geometry": "hard"}}}, results)
    assert buckets["hard"] == [0]


def test_cached_aggregate_is_refreshed_and_incomplete_is_not_publishable(tmp_path):
    row = sample()
    (tmp_path / "per_sample.json").write_text(json.dumps([row]), encoding="utf-8")
    (tmp_path / "aggregate.json").write_text('{"ranking_score": 99}', encoding="utf-8")
    assert reaggregate_result_dir(tmp_path)["ranking_score"] == 35
    row["sample_status"] = "evaluator_invalid"
    (tmp_path / "per_sample.json").write_text(json.dumps([row]), encoding="utf-8")
    assert reaggregate_result_dir(tmp_path)["ranking_publishable"] is False


def test_retry_uses_evidence_not_cached_completion_flags():
    valid = sample()
    valid["scoring_complete"] = False
    invalid = sample()
    invalid["task_id"] = "invalid"
    invalid["scoring_complete"] = True
    del invalid["scored"]["axis_scores"][CONFIG["technical_axes"][0]]
    assert invalid_task_ids([valid, invalid, {"task_id": "rejected", "sample_status": "model_output_invalid"}]) == ["invalid"]


def test_skipped_judge_failure_is_not_zero_in_csv():
    row = sample()
    del row["sample_status"]
    row["skipped"] = True
    assert _row(row)["ranking_score"] is None
