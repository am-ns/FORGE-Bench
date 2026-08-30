from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dataset" / "generated_videos_ult_windows"
ANNOTATIONS = ROOT / "dataset" / "annotations" / "video_generation_500_samples.json"
REPORT = ROOT / "dataset" / "organized_videos" / "WAN21_FULL_VALIDATION.csv"


def main() -> None:
    data = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    samples = data["samples"]
    expected = [f"{sample['task_id']}.mp4" for sample in samples]
    actual = sorted(path.name for path in SOURCE.glob("*.mp4"))
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    duplicate_expected = sorted(name for name, count in Counter(expected).items() if count > 1)

    rows: list[dict[str, object]] = []
    decode_failures: list[str] = []
    duration_failures: list[str] = []
    for index, name in enumerate(expected, 1):
        path = SOURCE / name
        capture = cv2.VideoCapture(str(path))
        opened = capture.isOpened()
        declared_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if opened else 0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) if opened else 0
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) if opened else 0
        fps = float(capture.get(cv2.CAP_PROP_FPS)) if opened else 0.0
        decoded_frames = 0
        while opened:
            ok, frame = capture.read()
            if not ok:
                break
            if frame is None or frame.size == 0:
                break
            decoded_frames += 1
        capture.release()
        duration = decoded_frames / fps if fps > 0 else 0.0
        decode_ok = (
            opened and declared_frames > 0 and decoded_frames == declared_frames
            and width > 0 and height > 0 and fps > 0
        )
        # Every generation prompt explicitly requests a 5–8 second video.
        duration_ok = 5.0 <= duration <= 8.0
        if not decode_ok:
            decode_failures.append(name)
        if not duration_ok:
            duration_failures.append(name)
        rows.append({
            "filename": name,
            "bytes": path.stat().st_size if path.exists() else 0,
            "decode_all_frames_ok": str(decode_ok).lower(),
            "declared_frames": declared_frames,
            "decoded_frames": decoded_frames,
            "width": width,
            "height": height,
            "fps": f"{fps:.6f}",
            "duration_seconds": f"{duration:.6f}",
            "duration_5_to_8_seconds_ok": str(duration_ok).lower(),
        })
        if index % 25 == 0:
            print(f"checked={index}/{len(expected)}", flush=True)

    with REPORT.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    domains = Counter(name.split("_", 1)[0] for name in actual)
    print(f"expected={len(expected)} actual={len(actual)}")
    print(f"missing={len(missing)} extra={len(extra)} duplicate_expected={len(duplicate_expected)}")
    print("domains=" + ",".join(f"{key}:{domains[key]}" for key in sorted(domains)))
    print(f"full_decode_failures={len(decode_failures)} duration_failures={len(duration_failures)}")
    print(f"report={REPORT}")
    if missing or extra or duplicate_expected or decode_failures or duration_failures:
        if missing:
            print("MISSING " + " ".join(missing))
        if extra:
            print("EXTRA " + " ".join(extra))
        if decode_failures:
            print("DECODE_FAIL " + " ".join(decode_failures))
        if duration_failures:
            print("DURATION_FAIL " + " ".join(duration_failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
