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
from scripts import rollback_imported_candidate_samples


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
        candidate_url_claim_dir=str(tmp_path / "candidate_url_claims"),
        candidate_url_claim_stale_seconds=86400.0,
        history_reports_root=str(tmp_path / "reports"),
        history_candidate_root=str(tmp_path / "history_candidates"),
        min_host_interval=0.0,
        target_new=target_new,
        per_scene=per_scene,
        download_workers=4,
        timeout=1.0,
        sleep_between_scenes=0.0,
        duplicate_hamming_distance=0,
        duplicate_dhash_distance=0,
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
    monkeypatch.setattr(fast_multisource_image_backfill, "_dhash", fake_hash)

    fast_multisource_image_backfill.run(args)

    rows = list(csv.DictReader(open(args.manifest, encoding="utf-8")))
    assert sum(row["status"] == "accepted" for row in rows) == expected
    assert len(list((tmp_path / "candidates").iterdir())) == expected


def test_fast_backfill_skips_historical_url_but_keeps_searching_for_new_image(monkeypatch, tmp_path):
    args = _backfill_args(tmp_path, per_scene=1, target_new=0)
    reports = tmp_path / "reports" / "fast_multisource_old"
    reports.mkdir(parents=True)
    (reports / "worker.csv").write_text(
        "status,image_url\naccepted,https://example.test/old.jpg\n",
        encoding="utf-8",
    )
    candidates = [
        fast_multisource_image_backfill.Candidate(
            "commons", "scene_one", "old", "https://example.test/old.jpg", "", "", "query"
        ),
        fast_multisource_image_backfill.Candidate(
            "commons", "scene_one", "new", "https://example.test/new.jpg", "", "", "query"
        ),
    ]

    monkeypatch.setattr(fast_multisource_image_backfill, "_collect_candidates", lambda *unused: (candidates, []))
    monkeypatch.setattr(fast_multisource_image_backfill, "_passes_quality", lambda *unused: (True, "accepted"))

    def fake_download(candidate, dest, timeout):
        Image.new("RGB", (8, 8), (120, 80, 40)).save(dest)
        return candidate.image_url

    monkeypatch.setattr(fast_multisource_image_backfill, "_download_candidate", fake_download)
    fast_multisource_image_backfill.run(args)

    rows = list(csv.DictReader(open(args.manifest, encoding="utf-8")))
    assert any(row["reason"] == "historical_duplicate_url" for row in rows)
    assert sum(row["status"] == "accepted" for row in rows) == 1
    assert next(row for row in rows if row["status"] == "accepted")["image_url"] == "https://example.test/new.jpg"


def test_historical_candidate_hashes_include_previous_run_folders(tmp_path):
    history_root = tmp_path / "images_candidates"
    previous = history_root / "fast_multisource_previous"
    current = history_root / "fast_multisource_current"
    previous.mkdir(parents=True)
    current.mkdir()
    Image.new("RGB", (16, 16), (120, 80, 40)).save(previous / "scene_one__commons__0001.jpg")

    hashes = fast_multisource_image_backfill._historical_candidate_hashes(history_root, current)

    assert list(hashes) == ["scene_one"]
    assert len(hashes["scene_one"]) == 1


def test_collect_candidates_prioritizes_queries_and_scales_request_budget(monkeypatch):
    args = argparse.Namespace(
        providers="commons,commons_category",
        queries_per_scene=8,
        categories_per_scene=4,
        search_limit=24,
        search_pages=3,
        provider_workers=2,
        timeout=1.0,
        log_search_diagnostics=False,
        min_semantic_score=3,
        progress_log="",
    )
    monkeypatch.setattr(
        fast_multisource_image_backfill,
        "SCENE_BANK",
        {"scene_one": {"queries": ["specific"], "categories": ["broad", "unused"]}},
    )
    calls = []

    def fake_search(scene, query, limit, pages, timeout):
        calls.append(("query", query, limit, pages))
        return [fast_multisource_image_backfill.Candidate("commons", scene, query, f"https://example.test/{query}.jpg", "", "", query)]

    def fake_category(scene, query, limit, pages, timeout):
        calls.append(("category", query, limit, pages))
        return [fast_multisource_image_backfill.Candidate("commons_category", scene, query, f"https://example.test/{query}.jpg", "", "", query)]

    monkeypatch.setattr(fast_multisource_image_backfill, "_commons_search", fake_search)
    monkeypatch.setattr(fast_multisource_image_backfill, "_commons_category", fake_category)

    candidates, _ = fast_multisource_image_backfill._collect_candidates("scene_one", {}, args, remaining_needed=1)

    assert [candidate.query for candidate in candidates] == ["specific", "specific industrial site photo", "broad"]
    assert sorted(calls) == [
        ("category", "broad", 8, 1),
        ("query", "specific", 8, 1),
        ("query", "specific industrial site photo", 8, 1),
    ]


def test_collect_candidates_rejects_category_drift(monkeypatch):
    args = argparse.Namespace(
        providers="commons_category",
        queries_per_scene=2,
        categories_per_scene=1,
        search_limit=40,
        search_pages=3,
        provider_workers=1,
        timeout=1.0,
        log_search_diagnostics=True,
        min_semantic_score=3,
        progress_log="",
    )

    def fake_category(scene, category, limit, pages, timeout):
        return [
            fast_multisource_image_backfill.Candidate(
                "commons_category",
                scene,
                "File:Italian automotive engineering Alfa Romeo carbon fiber chassis.jpg",
                "https://upload.wikimedia.org/example/alfa_chassis.jpg",
                "https://commons.wikimedia.org/wiki/File:Alfa_chassis.jpg",
                "cc-by",
                category,
            ),
            fast_multisource_image_backfill.Candidate(
                "commons_category",
                scene,
                "File:Acetylene torch cutting pipe at industrial worksite.jpg",
                "https://upload.wikimedia.org/example/acetylene_cutting_pipe.jpg",
                "https://commons.wikimedia.org/wiki/File:Acetylene_cutting_pipe.jpg",
                "cc-by",
                category,
            ),
        ]

    monkeypatch.setattr(fast_multisource_image_backfill, "_commons_category", fake_category)

    candidates, diagnostics = fast_multisource_image_backfill._collect_candidates(
        "emerg_hot_work_spark_combustible_fire",
        {},
        args,
        remaining_needed=2,
    )

    assert [candidate.title for candidate in candidates] == [
        "File:Acetylene torch cutting pipe at industrial worksite.jpg"
    ]
    assert any(
        row["reason"].startswith("semantic_mismatch") and "Alfa Romeo" in row["source_title"]
        for row in diagnostics
    )


def test_scene_claim_is_exclusive_until_released(tmp_path):
    root = tmp_path / "claims"
    claim = fast_multisource_image_backfill._claim_scene(root, "scene_one")
    assert claim is not None
    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is None
    fast_multisource_image_backfill._release_scene_claim(claim, completed=False)
    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is not None


def test_scene_claim_is_released_after_completion(tmp_path):
    root = tmp_path / "claims"
    claim = fast_multisource_image_backfill._claim_scene(root, "scene_one")
    fast_multisource_image_backfill._release_scene_claim(claim)

    assert fast_multisource_image_backfill._claim_scene(root, "scene_one") is not None


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


def test_scene_claim_reclaims_dead_owner_without_waiting(monkeypatch, tmp_path):
    root = tmp_path / "claims"
    digest = hashlib.sha1(b"scene_one").hexdigest()[:16]
    claim = root / f"{digest}.claim"
    claim.mkdir(parents=True)
    (claim / "scene.txt").write_text("scene_one\n", encoding="utf-8")
    (claim / fast_multisource_image_backfill.CLAIM_OWNER_FILENAME).write_text(
        json.dumps({"pid": 12345}),
        encoding="utf-8",
    )
    monkeypatch.setattr(fast_multisource_image_backfill, "_process_is_alive", lambda unused: False)

    reclaimed = fast_multisource_image_backfill._claim_scene(root, "scene_one")

    assert reclaimed == claim
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


def test_deficit_plan_prioritizes_empty_and_low_count_scenes(tmp_path):
    samples = tmp_path / "samples.json"
    samples.write_text(
        json.dumps({
            "samples": [
                {"scene_id": "scene_full", "domain": "visual_security"},
                {"scene_id": "scene_low", "domain": "visual_security"},
                {"scene_id": "scene_empty", "domain": "visual_security"},
            ]
        }),
        encoding="utf-8",
    )
    for scene, count in (("scene_full", 2), ("scene_low", 1)):
        scene_dir = tmp_path / "images" / "visual_security" / scene
        scene_dir.mkdir(parents=True)
        for index in range(count):
            Image.new("RGB", (16, 16), (index, 80, 40)).save(scene_dir / f"ref_{index + 1:02d}.jpg")
    out_dir = tmp_path / "plan"
    args = argparse.Namespace(
        samples=str(samples),
        image_root=str(tmp_path / "images"),
        out_dir=str(out_dir),
        target_per_scene=2,
        shards=1,
        max_scenes=0,
        lock_stale_seconds=3600.0,
    )

    build_image_deficit_plan.run(args)

    selected = json.loads((out_dir / "selected_scenes.json").read_text(encoding="utf-8"))
    assert selected["scenes"] == ["scene_empty", "scene_low"]


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


def test_images_only_import_does_not_exceed_formal_scene_target(monkeypatch, tmp_path):
    monkeypatch.setattr(import_screened_image_candidates, "REPO_ROOT", tmp_path)
    image_root = tmp_path / "dataset" / "images"
    scene_dir = image_root / "visual_security" / "scene_one"
    scene_dir.mkdir(parents=True)
    Image.new("RGB", (32, 32), (120, 80, 40)).save(scene_dir / "ref_01.jpg")
    candidates = tmp_path / "dataset" / "images_candidates" / "batch"
    candidates.mkdir(parents=True)
    Image.new("RGB", (32, 32), (20, 160, 220)).save(candidates / "scene_one__candidate.jpg")
    samples = tmp_path / "dataset" / "annotations" / "samples.json"
    samples.parent.mkdir(parents=True)
    samples.write_text(
        json.dumps({"samples": [{"task_id": "vsec_001", "scene_id": "scene_one", "domain": "visual_security"}]}),
        encoding="utf-8",
    )
    report = tmp_path / "report.csv"
    args = argparse.Namespace(
        candidate_root=str(candidates),
        image_root=str(image_root),
        samples=str(samples),
        report=str(report),
        dry_run=True,
        delete_rejected=False,
        images_only=True,
        max_per_scene=0,
        formal_target_per_scene=1,
        min_width=0,
        min_height=0,
        min_short_side=0,
        min_pixels=0,
        min_laplacian=0,
        max_edge_density=1,
        max_background_edge_density=1,
        ahash_distance=0,
        dhash_distance=0,
    )

    import_screened_image_candidates.run(args)

    rows = list(csv.DictReader(report.open(encoding="utf-8")))
    assert rows[0]["reason"] == "formal_scene_target_reached"


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


def test_images_only_rollback_dry_run_does_not_move_files(tmp_path):
    image = tmp_path / "dataset" / "images" / "visual_security" / "scene_one" / "ref_01.jpg"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (16, 16), (120, 80, 40)).save(image)
    samples = tmp_path / "dataset" / "annotations" / "samples.json"
    samples.parent.mkdir(parents=True)
    samples.write_text(json.dumps({"samples": []}), encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "status,dest_path,task_id,source_path,scene_id,domain\n"
        "accepted,dataset/images/visual_security/scene_one/ref_01.jpg,,candidate.jpg,scene_one,visual_security\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        repo_root=str(tmp_path),
        samples="dataset/annotations/samples.json",
        manifests=["manifest.csv"],
        review_root="reports/quarantine",
        report="reports/rollback.csv",
        dry_run=True,
    )

    rollback_imported_candidate_samples.run(args)

    assert image.exists()
    assert not (tmp_path / "reports" / "quarantine" / "dataset" / "images" / "visual_security" / "scene_one" / "ref_01.jpg").exists()
