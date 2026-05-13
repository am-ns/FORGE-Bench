import cv2, os
from pathlib import Path

videos_dir = Path("C:/Users/assd/S_I_Eval/dataset/videos")
out_dir = Path("C:/Users/assd/S_I_Eval/dataset/videos_preview")
out_dir.mkdir(exist_ok=True)

for vf in sorted(videos_dir.glob("*.mp4")):
    cap = cv2.VideoCapture(str(vf))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ret, frame = cap.read()
    cap.release()
    if ret:
        out = out_dir / f"{vf.stem}_frame0.jpg"
        cv2.imwrite(str(out), frame)
        print(f"{vf.name}: {w}x{h} {fps:.0f}fps {total}frames ({total/fps:.1f}s) -> {out.name}")
    else:
        print(f"{vf.name}: CANNOT READ")
