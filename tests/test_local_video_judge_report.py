import csv
import json

from scripts.build_local_video_judge_report import build


def test_report_scales_without_floor_and_rejects_missing_axis(tmp_path):
    source = tmp_path / "scores.jsonl"
    rows = [
        {"video": "a.mp4", "scores": {"visual_quality": 3, "motion_naturalness": 2, "temporal_coherence": 4, "prompt_alignment": 1, "audio_quality": None, "overall_score": 2.5}},
        {"video": "b.mp4", "scores": {"visual_quality": 8, "motion_naturalness": 8, "temporal_coherence": 8, "prompt_alignment": None, "audio_quality": None, "overall_score": 8}},
    ]
    source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    payload = build(source, tmp_path / "report", expected=2)
    assert payload["valid_videos"] == 1
    assert payload["ranking_publishable"] is False
    assert payload["issue_counts"]["missing_required_axis"] == 1
    with (tmp_path / "report" / "scores_0_100.csv").open(encoding="utf-8-sig") as handle:
        output = list(csv.DictReader(handle))
    assert float(output[0]["overall_score_0_100"]) == 25.0


def test_report_latest_result_wins(tmp_path):
    source = tmp_path / "scores.jsonl"
    good = {"visual_quality": 7, "motion_naturalness": 7, "temporal_coherence": 7, "prompt_alignment": 7, "audio_quality": None, "overall_score": 7}
    source.write_text("\n".join([
        json.dumps({"video": "a.mp4", "error": "timeout"}),
        json.dumps({"video": "a.mp4", "scores": good}),
    ]), encoding="utf-8")
    payload = build(source, tmp_path / "report", expected=1)
    assert payload["history_rows"] == 2
    assert payload["valid_videos"] == 1
    assert payload["ranking_publishable"] is True
