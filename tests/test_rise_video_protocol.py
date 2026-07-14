import hashlib
import json

from scripts.eval_rise_video_qwen import PROTOCOL, PROTOCOL_PATH, load_protocol, rise_sampling_indices


def test_protocol_is_hash_bound_and_versioned():
    raw = PROTOCOL_PATH.read_bytes()
    protocol = load_protocol()
    assert protocol["protocol_version"] == "forge-rise-video-protocol-v1.0"
    assert protocol["protocol_sha256"] == hashlib.sha256(raw).hexdigest()
    assert json.loads(raw)["invalid_policy"]["assign_zero_score"] is False


def test_rise_dimension_specific_sampling_is_frozen():
    indices = rise_sampling_indices(total=61, fps=30.0)
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
