import json

from scripts.build_formal_judge_retry_manifest import build


def test_retry_manifest_deduplicates_tasks_and_axes(tmp_path):
    shard = tmp_path / "shard"
    shard.mkdir()
    sample = {
        "task_id": "vsec_001",
        "sample_status": "valid",
        "scoring_validity": {"invalid_judge_outputs": ["temporal_consistency", "temporal_consistency"]},
    }
    (shard / "vsec_001.json").write_text(json.dumps(sample), encoding="utf-8")
    summary = build([shard], tmp_path / "out")
    assert summary["num_tasks"] == 1
    assert summary["axis_retry_counts"] == {"temporal_consistency": 1}
    row = json.loads((tmp_path / "out" / "retry_manifest.jsonl").read_text(encoding="utf-8"))
    assert row["invalid_axes"] == ["temporal_consistency"]
