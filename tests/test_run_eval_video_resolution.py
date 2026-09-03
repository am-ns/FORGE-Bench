from pathlib import Path

import pytest

from eval.run_eval import resolve_video_path


def test_resolve_video_path_supports_nested_categories(tmp_path):
    expected = tmp_path / "category" / "task_001.mp4"
    expected.parent.mkdir()
    expected.write_bytes(b"video")
    assert resolve_video_path(str(tmp_path), "task_001") == expected


def test_resolve_video_path_rejects_duplicate_task_ids(tmp_path):
    for category in ("a", "b"):
        path = tmp_path / category / "task_001.mp4"
        path.parent.mkdir()
        path.write_bytes(b"video")
    with pytest.raises(RuntimeError, match="Ambiguous video"):
        resolve_video_path(str(tmp_path), "task_001")
