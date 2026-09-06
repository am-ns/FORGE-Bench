from __future__ import annotations

import csv
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
VIDEO_ROOT = ROOT / "dataset" / "organized_videos"


def main() -> None:
    videos = sorted(VIDEO_ROOT.rglob("*.mp4"))
    rows: list[dict[str, object]] = []
    for index, path in enumerate(videos, 1):
        capture = cv2.VideoCapture(str(path))
        opened = capture.isOpened()
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if opened else 0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) if opened else 0
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) if opened else 0
        fps = float(capture.get(cv2.CAP_PROP_FPS)) if opened else 0.0
        sampled = []
        if opened and frame_count > 0:
            for frame_index in sorted({0, frame_count // 2, frame_count - 1}):
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ok, frame = capture.read()
                sampled.append(bool(ok and frame is not None and frame.size > 0))
        capture.release()
        ok = opened and frame_count > 0 and width > 0 and height > 0 and fps > 0 and all(sampled)
        rows.append({
            "path": str(path.relative_to(VIDEO_ROOT)),
            "decode_sample_ok": str(ok).lower(),
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "fps": f"{fps:.6f}",
            "sampled_frames": len(sampled),
        })
        if index % 100 == 0:
            print(f"checked={index}/{len(videos)}", flush=True)

    report = VIDEO_ROOT / "decode_validation.csv"
    with report.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if row["decode_sample_ok"] != "true"]
    print(f"checked={len(rows)} failures={len(failures)} report={report}")
    if failures:
        for row in failures[:20]:
            print(f"FAIL {row['path']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
