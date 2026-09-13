"""Losslessly trim the Seedance and Veo benchmark video sets to 5.000 seconds."""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
SETS = {
    ROOT / "dataset/six_model_video_dataset_3000/cogvideox1.5": ROOT / "dataset/cogvideox1.5-5s",
    ROOT / "dataset/six_model_video_dataset_3000/hunyuan1.5": ROOT / "dataset/hunyuan1.5-5s",
    ROOT / "dataset/six_model_video_dataset_3000/hunyuan1.5-distill": ROOT / "dataset/hunyuan1.5-distill-5s",
    ROOT / "dataset/six_model_video_dataset_3000/wan2.1": ROOT / "dataset/wan2.1-5s",
    ROOT / "dataset/six_model_video_dataset_3000/wan2.2": ROOT / "dataset/wan2.2-5s",
    ROOT / "dataset/forge_minimax_h3_500": ROOT / "dataset/forge_minimax_h3_500-5s",
    ROOT / "dataset/kling3.0-standard": ROOT / "dataset/kling3.0-standard-5s",
    ROOT / "dataset/seedance2.5": ROOT / "dataset/seedance2.5-5s",
    ROOT / "dataset/seedance2.5-regeneration-50": ROOT / "dataset/seedance2.5-regeneration-50-5s",
    ROOT / "dataset/veo3.1-fast": ROOT / "dataset/veo3.1-fast-5s",
}
def video_shape(path: Path) -> tuple[float, int]:
    capture = cv2.VideoCapture(str(path))
    try:
        return capture.get(cv2.CAP_PROP_FPS), int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        capture.release()


def valid_output(path: Path, expected_fps: float, expected_frames: int) -> bool:
    if not path.exists() or path.stat().st_size < 100_000:
        return False
    with path.open("rb") as handle:
        if b"ftyp" not in handle.read(64):
            return False
    fps, frames = video_shape(path)
    return abs(fps - expected_fps) < 0.01 and frames == expected_frames


def trim_one(ffmpeg: str, source: Path, destination: Path) -> tuple[str, str]:
    fps, _ = video_shape(source)
    expected_frames = round(fps * 5)
    if fps <= 0 or expected_frames <= 0:
        raise RuntimeError(f"{source}: invalid source frame rate {fps}")
    if valid_output(destination, fps, expected_frames):
        return "skipped", source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".part.mp4")
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source),
        "-map", "0:v:0", "-c:v", "copy", "-frames:v", str(expected_frames),
        "-avoid_negative_ts", "make_zero", "-movflags", "+faststart", "-y", str(temporary),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f"{source}: {completed.stderr.strip()}")
    if not valid_output(temporary, fps, expected_frames):
        output_fps, frames = video_shape(temporary)
        raise RuntimeError(f"{source}: trimmed output is not exactly 5 seconds (fps={output_fps}, frames={frames})")
    temporary.replace(destination)
    return "trimmed", source.name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    jobs = []
    for source_dir, output_dir in SETS.items():
        for source in sorted(source_dir.rglob("*.mp4")):
            jobs.append((source, output_dir / source.relative_to(source_dir)))
    counts = {"trimmed": 0, "skipped": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(trim_one, ffmpeg, source, destination): source for source, destination in jobs}
        for index, future in enumerate(as_completed(futures), 1):
            try:
                status, name = future.result()
                counts[status] += 1
            except Exception as exc:
                counts["failed"] += 1
                print(f"FAILED {exc}", flush=True)
            if index % 50 == 0 or index == len(jobs):
                print(f"progress={index}/{len(jobs)} trimmed={counts['trimmed']} skipped={counts['skipped']} failed={counts['failed']}", flush=True)
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
