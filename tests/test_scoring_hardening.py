import json
from pathlib import Path

from eval.llm_judge import _parse_judge_json
from eval.run_eval import _candidate_reference_paths
from scoring.leaderboard import build_leaderboard
from scoring.policy import CONFIG


def test_reference_candidates_never_substitute_another_scene_image(tmp_path: Path):
    requested = tmp_path / "ref_01.jpg"
    unrelated = tmp_path / "ref_02.jpg"
    unrelated.write_bytes(b"not-the-reference")

    candidates = _candidate_reference_paths(str(requested))

    assert unrelated not in candidates
    assert candidates == [requested]


def test_scalar_judge_requires_structured_json():
    assert _parse_judge_json("83\nlooks good") is None
    parsed = _parse_judge_json(
        '{"score": 83, "reasoning": "visible continuity", '
        '"failure_modes": [], "confidence": 0.8, "evidence_frames": [0, 8]}'
    )
    assert parsed is not None
    assert parsed["score"] == 83


def test_leaderboard_excludes_incomplete_and_legacy_fallbacks(tmp_path: Path):
    complete = tmp_path / "complete"
    incomplete = tmp_path / "incomplete"
    legacy = tmp_path / "legacy"
    for path in (complete, incomplete, legacy):
        path.mkdir()

    (complete / "aggregate.json").write_text(json.dumps({
        "ranking_publishable": True,
        "ranking_status": "complete",
        "ranking_score": 61.0,
        "scoring_policy": {"version": CONFIG["version"], "config_sha256": CONFIG["config_sha256"]},
        "axis_scores": {},
    }), encoding="utf-8")
    (incomplete / "aggregate.json").write_text(json.dumps({
        "ranking_publishable": False,
        "ranking_status": "incomplete",
        "ranking_score": 99.0,
    }), encoding="utf-8")
    (legacy / "aggregate.json").write_text(json.dumps({
        "ranking_publishable": True,
        "ranking_status": "complete",
        "overall": 88.0,
    }), encoding="utf-8")

    leaderboard = build_leaderboard(str(tmp_path))

    assert [row["model"] for row in leaderboard["models"]] == ["complete"]
