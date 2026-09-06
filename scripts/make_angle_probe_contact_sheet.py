#!/usr/bin/env python3
"""Create a first/middle/last-frame contact sheet for the angle probe videos."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports" / "minimax_angle_probe_manifest.jsonl"
VIDEO_DIR = ROOT / "results" / "minimax_angle_probe" / "videos"
OUT_PATH = ROOT / "reports" / "minimax_angle_probe_review" / "contact_sheet_first_mid_last.jpg"


def make_thumb(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    scale = 220 / max(h, w)
    frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
    canvas = np.full((240, 240, 3), 245, np.uint8)
    y = (canvas.shape[0] - frame.shape[0]) // 2
    x = (canvas.shape[1] - frame.shape[1]) // 2
    canvas[y : y + frame.shape[0], x : x + frame.shape[1]] = frame
    return canvas


def main() -> None:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    strips = []

    for row in rows:
        cap = cv2.VideoCapture(str(VIDEO_DIR / f"{row['task_id']}.mp4"))
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        indices = [0, max(0, n_frames // 2), max(0, n_frames - 1)]
        frames = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                frame = np.zeros((240, 320, 3), np.uint8)
            frames.append(make_thumb(frame))

        cap.release()
        strip = np.concatenate(frames, axis=1)
        label = f"{row['task_id']} {row['motion_type']} {row['viewpoint_motion_target']}"
        cv2.putText(strip, label, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        strips.append(strip)

    width = max(strip.shape[1] for strip in strips)
    padded = []
    for strip in strips:
        if strip.shape[1] < width:
            pad = np.full((strip.shape[0], width - strip.shape[1], 3), 245, np.uint8)
            strip = np.concatenate([strip, pad], axis=1)
        padded.append(strip)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT_PATH), np.concatenate(padded, axis=0))
    print(OUT_PATH)


if __name__ == "__main__":
    main()
