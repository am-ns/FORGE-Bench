import cv2
from pathlib import Path

ROOT  = Path("C:/Users/assd/S_I_Eval")
PREV  = ROOT / "dataset/videos_preview"
PREV.mkdir(exist_ok=True)

video_dir = ROOT / "dataset/videos"
idx = 0
for mp4 in sorted(video_dir.rglob("*.mp4")):
    if mp4.parent.name == "veo-3.1":
        continue
    cap = cv2.VideoCapture(str(mp4))
    ret, frame = cap.read()
    cap.release()
    out = PREV / f"frame_{idx:02d}_{mp4.parent.name}.jpg"
    if ret:
        cv2.imwrite(str(out), frame)
        print(f"[{idx}] {mp4.parent.name} | {mp4.name[:50]} -> {out.name}")
    idx += 1
