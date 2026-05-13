import shutil, os
from pathlib import Path

ROOT = Path("C:/Users/assd/S_I_Eval")
SRC  = ROOT / "dataset/videos"
VID  = ROOT / "dataset/videos"

# All model folders to create
models = [
    "veo-3.1",          # Google Veo (closed)
    "hailuo-2.3",       # Hailuo (closed)
    "sora-2",           # Sora (closed)
    "wan-2.6",          # Wan (closed)
    "kling-2.6",        # Kling (closed)
    "seedance-1.5pro",  # Seedance (closed)
    "wan2.2-i2v-a14b",  # Wan open
    "hunyuanvideo-1.5", # HunyuanVideo (open)
    "hunyuanvideo-1.5d",
    "wan2.2-ti2v-1.5b",
    "cogvideox1.5-5b",
]

for m in models:
    (VID / m).mkdir(parents=True, exist_ok=True)

print("Created model folders:", models)

# Rename and move the 3 Veo videos
mapping = {
    "mp_.mp4":                                  "aero_surf_001.mp4",
    "T_f_f_f_oil_platform_orbitmp_.mp4":        "ener_lat_001.mp4",
    "videomp_.mp4":                             "def_surf_001.mp4",
}

veo_dir = VID / "veo-3.1"
for src_name, dst_name in mapping.items():
    src = SRC / src_name
    dst = veo_dir / dst_name
    if src.exists():
        shutil.copy2(src, dst)
        os.remove(src)
        print(f"  {src_name} -> veo-3.1/{dst_name}  ({dst.stat().st_size//1024}KB)")
    else:
        print(f"  MISSING: {src_name}")

print(f"\nveo-3.1/ now has: {[f.name for f in veo_dir.iterdir()]}")
