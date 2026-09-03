import json

from scripts.run_full_formal_4gpu import build_shards


def test_build_shards_is_deterministic_and_complete(tmp_path):
    samples = [{"task_id": f"task_{index:03d}"} for index in range(10)]
    source = tmp_path / "samples.json"
    source.write_text(json.dumps({"samples": samples}), encoding="utf-8")
    paths = build_shards(source, tmp_path / "manifests", count=4)
    split = [json.loads(path.read_text(encoding="utf-8"))["samples"] for path in paths]
    assert [len(items) for items in split] == [3, 3, 2, 2]
    recovered = {item["task_id"] for items in split for item in items}
    assert recovered == {item["task_id"] for item in samples}
