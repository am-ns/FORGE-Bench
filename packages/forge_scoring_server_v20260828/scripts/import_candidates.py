"""
Import validated candidate images into dataset/images/, update samples.json,
and build a flat video-generation package (images + prompts).
"""
import json, shutil, copy, os
from pathlib import Path

ROOT        = Path(__file__).parent.parent
CAND_ROOT   = ROOT / "dataset" / "images_candidates"
IMG_ROOT    = ROOT / "dataset" / "images"
ANN_PATH    = ROOT / "dataset" / "annotations" / "samples.json"
PKG_DIR     = ROOT / "reports" / "video_gen_package"

# ── 1. Define imports: (src_candidate_name, dest_name, scene_id) ─────────────
# Format: {scene_id: [(src_filename, dest_filename), ...]}
IMPORTS = {
    "erob_cobot_human_handover": [
        ("ref_08.jpg", "ref_05.jpg"),
        ("ref_09.jpg", "ref_06.jpg"),
        ("ref_10.jpg", "ref_07.jpg"),
    ],
    "emerg_dust_explosion_confined_space": [
        ("ref_07.jpg", "ref_07.jpg"),
        ("ref_08.jpg", "ref_08.jpg"),
        ("ref_09.jpg", "ref_09.jpg"),
        ("ref_10.jpg", "ref_10.jpg"),
    ],
    "emerg_reactor_runaway_pressure_release": [
        ("ref_06.jpg", "ref_06.jpg"),
        ("ref_07.jpg", "ref_07.jpg"),
        ("ref_09.jpg", "ref_08.jpg"),
        ("ref_11.jpg", "ref_09.jpg"),
    ],
    "hload_formwork_collapse_local": [
        ("ref_02.jpg", "ref_09.jpg"),
    ],
    "hload_ground_settlement_outrigger": [
        ("ref_01.jpg", "ref_12.jpg"),
    ],
    "hload_hoist_collision_near_structure": [
        ("ref_05.jpg", "ref_05.jpg"),
        ("ref_06.jpg", "ref_06.jpg"),
        ("ref_07.jpg", "ref_07.jpg"),
    ],
    "hload_tunnel_pipe_burst_mud_surge": [
        ("ref_06.jpg", "ref_06.jpg"),
        ("ref_07.jpg", "ref_07.jpg"),
        ("ref_08.jpg", "ref_08.jpg"),
        ("ref_09.jpg", "ref_09.jpg"),
        ("ref_10.jpg", "ref_10.jpg"),
    ],
    "hload_wire_rope_overload_snap": [
        ("ref_04.jpg", "ref_04.jpg"),
        ("ref_05.jpg", "ref_05.jpg"),
        ("ref_07.jpg", "ref_06.jpg"),
        ("ref_08.jpg", "ref_07.jpg"),
    ],
    "vsec_guard_removed_conveyor": [
        ("ref_05.jpg", "ref_05.jpg"),
        ("ref_08.jpg", "ref_06.jpg"),
        ("ref_11.jpg", "ref_07.jpg"),
        ("ref_12.jpg", "ref_08.jpg"),
    ],
    "vsec_missing_ppe_at_height": [
        ("ref_09.jpg", "ref_06.jpg"),
        ("ref_10.jpg", "ref_07.jpg"),
        ("ref_11.jpg", "ref_08.jpg"),
    ],
    "vsec_pedestrian_forklift_near_miss": [
        ("ref_06.jpg", "ref_05.jpg"),
        ("ref_07.jpg", "ref_06.jpg"),
        ("ref_09.jpg", "ref_07.jpg"),
        ("ref_10.jpg", "ref_08.jpg"),
        ("ref_11.jpg", "ref_09.jpg"),
    ],
    "vsec_smoke_alarm_evacuation": [
        ("ref_09.jpg", "ref_03.jpg"),
    ],
}

DOMAIN_MAP = {
    "erob": "embodied_robotics",
    "emerg": "extreme_emergency",
    "hload": "heavy_load_construction",
    "pdef": "precision_defect_gen",
    "vsec": "visual_security",
}

SCENE_DOMAIN = {
    "erob_cobot_human_handover": "embodied_robotics",
    "emerg_dust_explosion_confined_space": "extreme_emergency",
    "emerg_reactor_runaway_pressure_release": "extreme_emergency",
    "hload_formwork_collapse_local": "heavy_load_construction",
    "hload_ground_settlement_outrigger": "heavy_load_construction",
    "hload_hoist_collision_near_structure": "heavy_load_construction",
    "hload_tunnel_pipe_burst_mud_surge": "heavy_load_construction",
    "hload_wire_rope_overload_snap": "heavy_load_construction",
    "vsec_guard_removed_conveyor": "visual_security",
    "vsec_missing_ppe_at_height": "visual_security",
    "vsec_pedestrian_forklift_near_miss": "visual_security",
    "vsec_smoke_alarm_evacuation": "visual_security",
}

DOMAIN_PREFIX = {
    "embodied_robotics": "erob",
    "extreme_emergency": "emerg",
    "heavy_load_construction": "hload",
    "precision_defect_gen": "pdef",
    "visual_security": "vsec",
}

# ── 2. Load existing annotations ─────────────────────────────────────────────
with open(ANN_PATH, encoding="utf-8") as f:
    data = json.load(f)

existing = data["samples"]

# Get max task_id per domain
domain_max = {}
for s in existing:
    dom = s["domain"]
    num = int(s["task_id"].split("_")[-1])
    domain_max[dom] = max(domain_max.get(dom, 0), num)

print("Current max IDs:", domain_max)

# Build template lookup: scene_id → sample template
templates = {}
for s in existing:
    sid = s["scene_id"]
    if sid not in templates:
        templates[sid] = s

# ── 3. Process each import ────────────────────────────────────────────────────
new_samples = []
copy_log = []

for scene_id, pairs in IMPORTS.items():
    domain = SCENE_DOMAIN[scene_id]
    prefix = DOMAIN_PREFIX[domain]
    tmpl = templates[scene_id]

    src_dir = CAND_ROOT / domain / scene_id
    dst_dir = IMG_ROOT / domain / scene_id
    dst_dir.mkdir(parents=True, exist_ok=True)

    for src_name, dst_name in pairs:
        src = src_dir / src_name
        dst = dst_dir / dst_name
        if not src.exists():
            print(f"  MISSING: {src}")
            continue

        # copy file
        shutil.copy2(src, dst)
        copy_log.append((str(src), str(dst)))

        # assign new task_id
        domain_max[domain] = domain_max.get(domain, 0) + 1
        task_id = f"{prefix}_{domain_max[domain]:03d}"

        # build new sample by cloning template
        ns = copy.deepcopy(tmpl)
        ns["task_id"] = task_id
        ns["image_path"] = f"dataset/images/{domain}/{scene_id}/{dst_name}"

        # update sensitivity_variants ids
        for sv in ns.get("sensitivity_variants", []):
            base = sv["id"].rsplit("_", 1)[0]  # strip easy/hard suffix
            suffix = sv["id"].rsplit("_", 1)[1]
            # rebuild from new task_id
            sv["id"] = f"{task_id}_{suffix}"

        # update industrial_logic_questions ids (keep content, reset ids)
        for i, q in enumerate(ns.get("industrial_logic_questions", []), 1):
            q["id"] = f"q{i}"

        new_samples.append(ns)
        print(f"  {src_name} → {dst_name}  [{task_id}]")

# ── 4. Append new samples and save ───────────────────────────────────────────
data["samples"].extend(new_samples)
with open(ANN_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\nsamples.json updated: {len(existing)} → {len(data['samples'])} samples")

# ── 5. Build video-generation package ─────────────────────────────────────────
PKG_DIR.mkdir(parents=True, exist_ok=True)
pkg_img = PKG_DIR / "images"
pkg_img.mkdir(exist_ok=True)

jsonl_path = PKG_DIR / "prompts.jsonl"
md_path    = PKG_DIR / "prompts.md"

with open(jsonl_path, "w", encoding="utf-8") as jf, \
     open(md_path,    "w", encoding="utf-8") as mf:

    mf.write("# FORGE-Bench Video Generation Package\n\n")
    mf.write(f"Total samples: {len(data['samples'])}\n\n---\n\n")

    for s in data["samples"]:
        img_src = ROOT / s["image_path"]
        if not img_src.exists():
            continue
        ext = img_src.suffix
        flat_name = f"{s['task_id']}{ext}"
        flat_dst  = pkg_img / flat_name
        shutil.copy2(img_src, flat_dst)

        record = {
            "task_id":   s["task_id"],
            "image":     f"images/{flat_name}",
            "scene_id":  s["scene_id"],
            "domain":    s["domain"],
            "prompt":    s["video_generation_prompt"],
        }
        jf.write(json.dumps(record, ensure_ascii=False) + "\n")

        mf.write(f"## {s['task_id']} — {s.get('task_title','')}\n")
        mf.write(f"**Image**: `images/{flat_name}`\n\n")
        mf.write(f"**Prompt**:\n> {s['video_generation_prompt']}\n\n---\n\n")

img_count = len(list(pkg_img.iterdir()))
print(f"\nVideo-gen package: {PKG_DIR}")
print(f"  images/: {img_count} files")
print(f"  prompts.jsonl: {jsonl_path.stat().st_size//1024} KB")
print(f"  prompts.md:    {md_path.stat().st_size//1024} KB")
print("\nDone.")
