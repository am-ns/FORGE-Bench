import copy
import json

import pytest

from scoring.aggregate import aggregate_sample_results, compute_sample_ranking_score
from scoring.migration import rebuild_cached_result
from scoring.per_sample import score_sample
from scoring.policy import CONFIG, publication_issue
from scripts.reaggregate_cached_results import reaggregate_result_dir


def sample():
    return {"task_id": "audit", "scored": score_sample({a: 80.0 for a in CONFIG["headline_axes"]})}


@pytest.mark.parametrize("value", [200, -1, True, False, "80", float("nan"), float("inf"), None])
@pytest.mark.parametrize("axis", CONFIG["headline_axes"])
def test_invalid_judgments_never_publish(value, axis):
    axes = {a: 80.0 for a in CONFIG["headline_axes"]}
    axes[axis] = value
    row = {"task_id": "invalid", "scored": score_sample(axes)}
    assert row["scored"]["input_errors"]
    assert compute_sample_ranking_score(row) is None
    aggregate = aggregate_sample_results([sample(), row])
    assert aggregate["ranking_publishable"] is False
    assert publication_issue(aggregate) == "non_publishable"


@pytest.mark.parametrize("value", [200, True, "80", float("nan"), float("inf")])
def test_invalid_cached_axes_and_coverage_are_rejected(value):
    for key in ("axis", "coverage", "application"):
        row = sample()
        if key == "axis":
            row["scored"]["axis_scores"][CONFIG["technical_axes"][0]] = value
        elif key == "coverage":
            row["observable_event_coverage"] = value
        else:
            row["scored"]["application_usefulness_score"] = value
        assert compute_sample_ranking_score(row) is None
        assert aggregate_sample_results([row])["ranking_publishable"] is False


@pytest.mark.parametrize("field,value", [
    ("abrupt_transition", "false"), ("abrupt_transition", 1),
    ("used_for_axis_cap", "true"), ("used_for_axis_cap", 1),
    ("confidence", "0.9"), ("confidence", True), ("confidence", float("inf")),
    ("confidence", 2), ("confidence", "bad"),
])
def test_operator_rules_identical_at_both_boundaries(field, value):
    payload = {"used_for_axis_cap": True, "confidence": 0.9, "validity": "valid", "abrupt_transition": True}
    payload[field] = value
    evidence = {"operators": {"temporal_break": payload}}
    axes = {a: 80.0 for a in CONFIG["headline_axes"]}
    direct = {"scored": score_sample(axes, operator_evidence=evidence), "operator_evidence": evidence}
    cached = {"scored": score_sample(axes), "operator_evidence": evidence}
    assert direct["scored"]["axis_scores"]["temporal_consistency"] == 80
    assert compute_sample_ranking_score(direct) == compute_sample_ranking_score(cached) == 80
    assert aggregate_sample_results([cached])["ranking_score"] == 80


def test_migration_removes_legacy_transforms_and_preserves_evidence(tmp_path):
    row = sample()
    row["scored"]["axis_scores"] = {a: 15 for a in CONFIG["technical_axes"]}
    row["scored"]["application_usefulness_score"] = 15
    row["scored"]["scoring_policy"] = {"version": "v3"}
    row["scored"]["score_floor_applied"] = True
    row["ranking_score"] = 99
    original = copy.deepcopy(row)
    assert compute_sample_ranking_score(row) is None
    rebuilt = rebuild_cached_result(row)
    assert row == original
    assert compute_sample_ranking_score(rebuilt) == 80
    assert rebuild_cached_result(rebuilt) == rebuilt
    path = tmp_path / "per_sample.json"
    path.write_text(json.dumps([row]), encoding="utf-8")
    assert reaggregate_result_dir(tmp_path)["ranking_score"] == 80
    assert json.loads((tmp_path / "per_sample.before_v4_migration.json").read_text())[0] == original
    assert json.loads(path.read_text())[0]["scored"]["axis_scores"] == rebuilt["scored"]["axis_scores"]


def test_migration_missing_original_application_fails_closed():
    row = sample()
    del row["scored"]["raw_application_usefulness_score"]
    rebuilt = rebuild_cached_result(row)
    assert rebuilt["scoring_migration_error"]
    assert compute_sample_ranking_score(rebuilt) is None
    assert aggregate_sample_results([rebuilt])["ranking_publishable"] is False


def test_migration_cannot_erase_invalid_coverage():
    row = {"task_id": "invalid", "scored": score_sample(
        {a: 80 for a in CONFIG["headline_axes"]}, observable_event_coverage="bad")}
    rebuilt = rebuild_cached_result(row)
    assert rebuilt["scored"]["input_errors"]
    assert compute_sample_ranking_score(rebuilt) is None


def test_missing_shards_remain_in_requested_population():
    from scripts.combine_eval_shards import align_results_to_manifest
    rows = align_results_to_manifest({"audit": sample()}, ["audit", "missing"])
    aggregate = aggregate_sample_results(rows)
    assert len(rows) == 2
    assert rows[1]["skip_reason"] == "missing_shard_result"
    assert aggregate["ranking_publishable"] is False
    with pytest.raises(ValueError, match="Duplicate"):
        align_results_to_manifest({"audit": sample()}, ["audit", "audit"])
