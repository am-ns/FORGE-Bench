from pathlib import Path

from scripts.retry_formal_incomplete import invalid_task_ids, prior_retry_result_dirs


def test_invalid_task_ids_selects_only_incomplete_or_invalid_samples():
    rows = [
        {"task_id": "ok", "sample_status": "valid", "scoring_complete": True, "scoring_validity": {}},
        {"task_id": "missing", "sample_status": "evaluator_invalid", "scoring_complete": False,
         "scoring_validity": {"missing_required_axes": ["geometric_integrity"]}},
        {"task_id": "parse", "sample_status": "valid", "scoring_complete": True,
         "scoring_validity": {"invalid_judge_outputs": ["temporal_consistency"]}},
    ]
    assert invalid_task_ids(rows) == ["missing", "parse"]


def test_prior_retry_result_dirs_are_chronological_and_existing(tmp_path: Path):
    retry_root = tmp_path / "retries" / "model"
    expected = []
    for stamp in ("20260101T020000Z", "20260101T010000Z"):
        for shard in (2, 0):
            path = retry_root / stamp / f"shard_{shard}" / "model"
            path.mkdir(parents=True)
    for stamp in ("20260101T010000Z", "20260101T020000Z"):
        for shard in (0, 2):
            expected.append(retry_root / stamp / f"shard_{shard}" / "model")

    assert prior_retry_result_dirs(tmp_path, "model") == expected
