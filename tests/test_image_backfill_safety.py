import argparse
import csv
import hashlib
import json
import os
import re

import pytest
from PIL import Image

from scripts import build_image_deficit_plan
from scripts import audit_image_library_duplicates
from scripts import clean_image_candidates_strict
from scripts import fast_multisource_image_backfill
from scripts import import_screened_image_candidates


def _backfill_args(tmp_path, *, per_scene, target_new):
    samples = tmp_path / "samples.json"
    samples.write_text(
        json.dumps({"samples": [{"scene_id": "scene_one", "domain": "visual_security"}]}),
        encoding="utf-8",
    )
    scenes = tmp_path / "scenes.json"
    scenes.write_text(json.dumps({"scenes": ["scene_one"]}), encoding="utf-8")
    return argparse.Namespace(
        samples=str(samples),
        scenes_file=str(scenes),
        domains="",
        image_root=str(tmp_path / "images"),
        formal_target_per_scene=0,
        shards=1,
        shard_index=0,
        max_scenes=0,
        output_dir=str(tmp_path / "candidates"),
        manifest=str(tmp_path / "manifest.csv"),
        host_lock_dir=str(tmp_path / "host_locks"),
        scene_claim_dir=str(tmp_path / "scene_claims"),
        scene_claim_stale_seconds=86400.0,
        min_host_interval=0.0,
        target_new=target_new,
        per_scene=per_scene,
        download_workers=4,
        timeout=1.0,
        sleep_between_scenes=0.0,
        duplicate_hamming_distance=0,
    )


@pytest.mark.parametrize(
    ("per_scene", "target_new", "expected"),
    [(2, 0, 2), (5, 2, 2)],
)
def test_fast_backfill_respects_accept_limits(monkeypatch, tmp_path, per_scene, target_new, expected):
    args = _backfill_args(tmp_path, per_scene=per_scene, target_new=target_new)
    candidates = [
        fast_multisource_image_backfill.Candidate(
            "commons", "scene_one", f"title-{index}", f"https://example.test/{index}.jpg", "", "", "query"
        )
        for index in range(8)
    ]

    monkeypatch.setattr(fast_multisource_image_backfill, "_collect_candidates", lambda *unused: (candidates, []))
    monkeypatch.setattr(fast_multisource_image_backfill, "_passes_quality", lambda *unused: (True, "accepted"))

    def fake_download(candidate, dest, timeout):
        Image.new("RGB", (8, 8), (120, 80, 40)).save(dest)
        return candidate.image_url

    def fake_hash(path):
        index = int(re.search(r"(\d+)$", path.stem).group(1))
        return f"{index:016x}"

    monkeypatch.setattr(fast_multisource_image_backfill, "_download_candidate", fake_download)
    monkeypatch.setattr(fast_multisource_image_backfill, "_average_hash", fake_hash)

    fast_multisource_image_backfill.run(args)

    rows = list(csv.DictReader(open(args.manifest, encoding="utf-8")))
    assert sum(row["status"] == "accepted" for row in rows) == expected
    assert len(list((tmp_path / "candidates").iterdir())) == expected


def test_scene_claim_is_exclusive_until_released(tmp_path):
    root = tmp_path / "claims"
    claim = fast_multisource_image_backfill._claim_scene(root, "scene_one")
    assert claim is not None
    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is None
    fast_multisource_image_backfill._release_scene_claim(claim, completed=False)
    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is not None


def test_scene_claim_keeps_recent_completion_marker(tmp_path):
    root = tmp_path / "claims"
    claim = fast_multisource_image_backfill._claim_scene(root, "scene_one")
    fast_multisource_image_backfill._release_scene_claim(claim)

    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is None


def test_scene_claim_reclaims_stale_lock(tmp_path):
    root = tmp_path / "claims"
    claim = root / "stale.claim"
    claim.mkdir(parents=True)
    (claim / "scene.txt").write_text("scene_one\n", encoding="utf-8")
    os.utime(claim, (0, 0))
    digest = hashlib.sha1(b"scene_one").hexdigest()[:16]
    digest_claim = root / f"{digest}.claim"
    claim.rename(digest_claim)

    reclaimed = fast_multisource_image_backfill._claim_scene(root, "scene_one", stale_seconds=1.0)

    assert reclaimed == digest_claim
    fast_multisource_image_backfill._release_scene_claim(reclaimed)


def test_deficit_plan_removes_stale_shards(tmp_path):
    samples = tmp_path / "samples.json"
    samples.write_text(
        json.dumps({"samples": [{"scene_id": "scene_one", "domain": "visual_security"}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "plan"
    out_dir.mkdir()
    (out_dir / "selected_scenes_shard_5.json").write_text("{}", encoding="utf-8")
    args = argparse.Namespace(
        samples=str(samples),
        image_root=str(tmp_path / "images"),
        out_dir=str(out_dir),
        target_per_scene=1,
        shards=2,
        max_scenes=0,
        lock_stale_seconds=3600.0,
    )

    build_image_deficit_plan.run(args)

    assert not (out_dir / "selected_scenes_shard_5.json").exists()
    assert (out_dir / "selected_scenes_shard_0.json").exists()
    assert (out_dir / "selected_scenes_shard_1.json").exists()


def test_clean_pool_rejects_output_outside_candidate_root(tmp_path):
    with pytest.raises(ValueError):
        clean_image_candidates_strict._require_within(tmp_path / "outside", tmp_path / "candidates", "output-root")


def test_import_lock_rejects_second_writer(tmp_path):
    lock = tmp_path / "samples.json.import.lock"
    with import_screened_image_candidates._exclusive_lock(lock):
        with pytest.raises(RuntimeError):
            with import_screened_image_candidates._exclusive_lock(lock):
                pass


def test_import_lock_reclaims_stale_lock(tmp_path):
    lock = tmp_path / "samples.json.import.lock"
    lock.write_text("stale\n", encoding="ascii")
    os.utime(lock, (0, 0))

    with import_screened_image_candidates._exclusive_lock(lock, stale_seconds=1.0):
        assert lock.exists()

    assert not lock.exists()


def test_duplicate_audit_allows_reuse_across_scenes(tmp_path):
    image_root = tmp_path / "images"
    for scene in ("scene_one", "scene_two"):
        scene_dir = image_root / "domain" / scene
        scene_dir.mkdir(parents=True)
        Image.new("RGB", (16, 16), (120, 80, 40)).save(scene_dir / "ref_01.jpg")
    report = tmp_path / "duplicates.csv"
    args = argparse.Namespace(
        image_root=str(image_root),
        report=str(report),
        ahash_distance=0,
        dhash_distance=0,
    )

    audit_image_library_duplicates.run(args)

    assert list(csv.DictReader(report.open(encoding="utf-8"))) == []


def test_duplicate_audit_rejects_reuse_within_scene(tmp_path):
    scene_dir = tmp_path / "images" / "domain" / "scene_one"
    scene_dir.mkdir(parents=True)
    for name in ("ref_01.jpg", "ref_02.jpg"):
        Image.new("RGB", (16, 16), (120, 80, 40)).save(scene_dir / name)
    report = tmp_path / "duplicates.csv"
    args = argparse.Namespace(
        image_root=str(tmp_path / "images"),
        report=str(report),
        ahash_distance=0,
        dhash_distance=0,
    )

    audit_image_library_duplicates.run(args)

    rows = list(csv.DictReader(report.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["image_path"].endswith("scene_one/ref_02.jpg")
