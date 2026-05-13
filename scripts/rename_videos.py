import shutil, os
from pathlib import Path

ROOT = Path("C:/Users/assd/S_I_Eval/dataset/videos")

renames = [
    # Hailuo
    ("hailuo-2.3", "海螺_视频_Camera orb_510235020380852230.mp4", "SA03.mp4"),
    ("hailuo-2.3", "海螺_视频_Camera orb_510235434027315201.mp4", "SA02.mp4"),
    ("hailuo-2.3", "海螺_视频_Camera orb_510236028959948801.mp4", "SA01.mp4"),
    ("hailuo-2.3", "海螺_视频_Camera pan_510233695412805638.mp4", "micro_lat_001.mp4"),
    # Hunyuan
    ("hunyuan-i2v-1.0",
     "Camera orbits smoothly 45 degrees clockwise around a Su-27in level flight against sky.The aircraft is in digital blue-grey camouflage with underwing stores. Slow, constant-radius orbit. No zoom.mp4",
     "aero_surf_001.mp4"),
    # Kling
    ("kling-2.6", "kling_20260511_作品_A_red_scis_5433_0.mp4", "mfg_kin_001.mp4"),
]

for model, old_name, new_name in renames:
    src = ROOT / model / old_name
    dst = ROOT / model / new_name
    if src.exists():
        src.rename(dst)
        print(f"  OK  {model}/{new_name}  ({dst.stat().st_size//1024}KB)")
    else:
        print(f"  MISSING: {model}/{old_name}")

print("\nFinal structure:")
for model_dir in sorted(ROOT.iterdir()):
    files = [f.name for f in model_dir.iterdir() if f.suffix == '.mp4']
    if files:
        print(f"  {model_dir.name}/")
        for f in sorted(files):
            print(f"    {f}")
