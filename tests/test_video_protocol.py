import copy

from eval.video_protocol import (
    PROTOCOL, dynamic_local_indices, evaluation_cache_key, sampling_manifest,
    task_progress_indices, validate_axis_judgment, visual_quality_indices,
)


def test_sampling_views_are_deterministic_and_obey_boundaries():
    first = sampling_manifest(101, 25.0)
    assert first == sampling_manifest(101, 25.0)
    assert first["task_progress"][0] == 0
    assert first["task_progress"][-1] == 100
    assert all(window == list(range(window[0], window[0] + len(window))) for window in first["dynamic_local"])
    assert 0 not in first["visual_quality"] and 100 not in first["visual_quality"]


def test_short_video_and_bad_fps_have_defined_behavior():
    assert task_progress_indices(1, 0) == [0]
    assert dynamic_local_indices(3) == [[0, 1, 2]]
    assert visual_quality_indices(2) == []
    assert task_progress_indices(5, float("nan")) == [0, 1, 2, 3, 4]


def test_cache_key_invalidates_every_frozen_input():
    args = dict(video_sha256="v", reference_sha256="r", sample={"task_id": "a"}, judge_model="j", judge_model_version="1")
    base, identity = evaluation_cache_key(**args)
    for field, value in (("video_sha256", "v2"), ("reference_sha256", "r2"), ("sample", {"task_id": "b"}), ("judge_model_version", "2")):
        changed = copy.deepcopy(args)
        changed[field] = value
        assert evaluation_cache_key(**changed)[0] != base
    assert identity["protocol_version"] == PROTOCOL["version"]
    assert len(identity["protocol_sha256"]) == 64


def test_axis_contract_requires_locatable_evidence_at_extremes():
    good = {"score": 50, "evidence": [{"timestamp": 1.25, "observation": "break"}], "failure_modes": [], "confidence": 0.8}
    assert validate_axis_judgment(good) == []
    bad = {"score": 90, "evidence": [], "failure_modes": [], "confidence": 0.8}
    assert "required_evidence_missing" in validate_axis_judgment(bad)
