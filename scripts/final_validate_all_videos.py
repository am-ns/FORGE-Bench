from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
VIDEOS = DATASET / "organized_videos"
ANNOTATIONS = DATASET / "annotations" / "video_generation_500_samples.json"
COMPLETE = ("wan2.1", "hunyuan1.5", "cogvideox1.5")
DOMAINS = {
    "emerg": "extreme_emergency",
    "erob": "embodied_robotics",
    "hload": "heavy_load_construction",
    "pdef": "precision_defect_generation",
    "vsec": "visual_security",
}


def decode_all(path: Path) -> dict[str, object]:
    cap = cv2.VideoCapture(str(path))
    opened = cap.isOpened()
    declared = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if opened else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if opened else 0
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if opened else 0
    fps = float(cap.get(cv2.CAP_PROP_FPS)) if opened else 0.0
    decoded = 0
    while opened:
        ok, frame = cap.read()
        if not ok:
            break
        if frame is None or frame.size == 0:
            break
        decoded += 1
    cap.release()
    duration = decoded / fps if fps > 0 else 0.0
    return {
        "decode_all_frames_ok": opened and declared > 0 and decoded == declared,
        "declared_frames": declared,
        "decoded_frames": decoded,
        "width": width,
        "height": height,
        "fps": fps,
        "duration_seconds": duration,
    }


def main() -> None:
    samples = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))["samples"]
    expected = {f"{sample['task_id']}.mp4" for sample in samples}
    rows: list[dict[str, object]] = []
    set_issues: list[str] = []

    for collection in COMPLETE:
        files = sorted((VIDEOS / collection).rglob("*.mp4"))
        actual = {path.name for path in files}
        missing, extra = expected - actual, actual - expected
        if len(files) != 500 or missing or extra or len(actual) != len(files):
            set_issues.append(
                f"{collection}: files={len(files)} unique={len(actual)} "
                f"missing={len(missing)} extra={len(extra)}"
            )
        counts = Counter(path.name.split("_", 1)[0] for path in files)
        if any(counts[prefix] != 100 for prefix in DOMAINS):
            set_issues.append(f"{collection}: domain counts {dict(counts)}")

    targets = []
    for collection_dir in sorted(path for path in VIDEOS.iterdir() if path.is_dir()):
        if collection_dir.name == "_quarantine_partial":
            continue
        targets.extend((collection_dir.name, path) for path in sorted(collection_dir.rglob("*.mp4")))

    for index, (collection, path) in enumerate(targets, 1):
        media = decode_all(path)
        relative = path.relative_to(VIDEOS)
        expected_domain = DOMAINS.get(path.name.split("_", 1)[0].lstrip("."))
        domain_path_ok = expected_domain is None or expected_domain in relative.parts
        duration_required = collection in COMPLETE
        duration_ok = 5.0 <= float(media["duration_seconds"]) <= 8.0
        rows.append({
            "collection": collection,
            "path": str(relative),
            "bytes": path.stat().st_size,
            "domain_path_ok": str(domain_path_ok).lower(),
            "decode_all_frames_ok": str(media["decode_all_frames_ok"]).lower(),
            "declared_frames": media["declared_frames"],
            "decoded_frames": media["decoded_frames"],
            "width": media["width"],
            "height": media["height"],
            "fps": f"{float(media['fps']):.6f}",
            "duration_seconds": f"{float(media['duration_seconds']):.6f}",
            "duration_required": str(duration_required).lower(),
            "duration_ok": str(duration_ok if duration_required else True).lower(),
        })
        if index % 50 == 0:
            print(f"checked={index}/{len(targets)}", flush=True)

    failures = [
        row for row in rows
        if row["bytes"] == 0 or row["domain_path_ok"] != "true"
        or row["decode_all_frames_ok"] != "true" or row["duration_ok"] != "true"
    ]
    csv_path = VIDEOS / "FINAL_FULL_VALIDATION.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    incomplete_files = sorted((VIDEOS / "wan2.2_incomplete").rglob("*.mp4"))
    incomplete_ids = {path.name for path in incomplete_files}
    wan22_missing = expected - incomplete_ids
    partials = list((VIDEOS / "_quarantine_partial").rglob("*.mp4"))
    report = [
        "# Final video validation",
        "",
        f"- Fully checked non-partial videos: {len(rows)}",
        f"- Full-frame decode failures: {sum(r['decode_all_frames_ok'] != 'true' for r in rows)}",
        f"- Classification-path failures: {sum(r['domain_path_ok'] != 'true' for r in rows)}",
        f"- Complete-set/duration issues: {len(set_issues) + sum(r['duration_ok'] != 'true' for r in rows)}",
        "",
        "## Complete 500-video sets",
        "",
        *[f"- {name}: 500/500, exact task-ID match, five domains x 100" for name in COMPLETE],
        "",
        "## Other material",
        "",
        f"- wan2.2_incomplete: {len(incomplete_files)} complete files; {len(wan22_missing)} task IDs missing",
        f"- wan_legacy_named: {len(list((VIDEOS / 'wan_legacy_named').rglob('*.mp4')))} archived videos",
        f"- _quarantine_partial: {len(partials)} excluded partial files",
        "",
        "## Failures",
        "",
        *(set_issues or ["- None"]),
    ]
    (VIDEOS / "FINAL_VALIDATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"checked={len(rows)} failures={len(failures)} set_issues={len(set_issues)}")
    print(f"wan2.2_missing={len(wan22_missing)} partials={len(partials)}")
    if failures or set_issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
