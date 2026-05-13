import cv2
from pathlib import Path

ROOT = Path("C:/Users/assd/S_I_Eval")
PREV = ROOT / "dataset/videos_preview"

orb_files = sorted((ROOT / "dataset/videos/hailuo-2.3").glob("*orb*.mp4"))
for i, mp4 in enumerate(orb_files):
    cap = cv2.VideoCapture(str(mp4))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total - 1)
    ret, frame = cap.read()
    cap.release()
    out = PREV / f"last_{i:02d}_hailuo_orb.jpg"
    if ret:
        cv2.imwrite(str(out), frame)
        print(f"[{i}] {mp4.name[:50]} -> last frame saved")
