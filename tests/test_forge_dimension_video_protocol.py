import hashlib
import json

from scripts.eval_forge_dimension_video_qwen import PROTOCOL, PROTOCOL_PATH, load_protocol, dimension_sampling_indices, paper_metrics


def test_protocol_is_hash_bound_and_versioned():
    raw = PROTOCOL_PATH.read_bytes()
    protocol = load_protocol()
    assert protocol["protocol_version"] == "forge-dimension-video-protocol-v1.1"
    assert protocol["protocol_sha256"] == hashlib.sha256(raw).hexdigest()
    assert json.loads(raw)["invalid_policy"]["assign_zero_score"] is False


def test_dimension_specific_sampling_is_frozen():
    indices = dimension_sampling_indices(total=61, fps=30.0)
    assert indices["reasoning_alignment_2fps"] == [0, 15, 30, 45, 60]
    assert len(indices["temporal_consistency_uniform16"]) == 16
    assert len(indices["physical_rationality_uniform16"]) == 16
    quality = indices["visual_quality_uniform6_no_boundaries"]
    assert len(quality) == 6
    assert 0 not in quality and 60 not in quality


def test_methodological_settings_cannot_be_runtime_overridden():
    assert PROTOCOL["reasoning_alignment"]["fps"] == 2.0
    assert PROTOCOL["temporal_consistency"]["frames"] == 16
    assert PROTOCOL["physical_rationality"]["frames"] == 16
    assert PROTOCOL["visual_quality"]["frames"] == 6
    assert PROTOCOL["conflict_arbitration"]["absolute_delta_threshold"] == 35.0

def test_paper_metrics_separate_task_success_from_generation_quality():
    scores = {"industrial_logic_and_fact_alignment": 20.0, "geometric_integrity": 90.0, "physical_plausibility": 80.0, "temporal_consistency": 70.0, "reference_and_motion_fidelity": 90.0, "application_usefulness": 10.0}
    result = paper_metrics(scores, event_coverage=20.0, visual_quality_level=3)
    assert result["task_success"] is False
    assert result["conditional_quality_score"] == 86.0
    assert result["overall_utility_score"] == 0.0


def test_paper_metrics_apply_one_binary_utility_gate_after_success():
    scores = {"industrial_logic_and_fact_alignment": 60.0, "geometric_integrity": 80.0, "physical_plausibility": 80.0, "temporal_consistency": 80.0, "reference_and_motion_fidelity": 60.0, "application_usefulness": 1.0}
    result = paper_metrics(scores, event_coverage=60.0, visual_quality_level=2)
    assert result["task_success"] is True
    assert result["conditional_quality_score"] == 70.0
    assert result["overall_utility_score"] == 70.0
