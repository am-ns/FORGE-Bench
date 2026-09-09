#!/usr/bin/env python3
"""Apply the 460-item human prompt/image alignment review consistently."""

from __future__ import annotations

import json
import csv
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "reports/prompt_review_460.json"
TARGETS = (
    ROOT / "dataset/annotations/samples.json",
    ROOT / "dataset/annotations/video_generation_500_samples.json",
)
OUT = ROOT / "reports/prompt_review_460_resolution.json"
PACKAGE = ROOT / "reports/video_generation_500_package"
REPLACEMENT_MD = ROOT / "reports/prompt_review_460_replacement_requirements.md"
REGEN_JSONL = ROOT / "reports/prompt_review_460_regeneration_manifest.jsonl"

# These references cannot support the benchmark task without inventing absent
# objects. They require a replacement reference and a newly generated video.
REPLACE_IMAGE = {
    "erob_015", "erob_027", "erob_032", "erob_033", "erob_034", "erob_035",
    "erob_037", "erob_052", "erob_146", "erob_147", "erob_222", "erob_245",
    "erob_260", "emerg_221", "emerg_294", "emerg_305", "emerg_306", "emerg_314",
    "hload_023", "hload_058", "hload_069", "hload_109", "hload_215", "hload_225",
    "hload_226", "hload_248", "pdef_108", "pdef_128", "pdef_134", "pdef_136",
    "pdef_143", "pdef_153", "pdef_181", "vsec_029", "vsec_043", "vsec_111",
    "vsec_116", "vsec_167", "vsec_169", "vsec_203", "erob_028", "erob_082",
    "erob_083", "erob_084",
}

# User-approved wording changes, expressed in the English canonical data.  Each
# replacement is applied recursively so judge prompts, event graphs, questions,
# and generation prompts do not drift apart.
RULES: dict[str, list[tuple[str, str]]] = {}

def add(ids: str, old: str, new: str) -> None:
    for task_id in ids.split():
        RULES.setdefault(task_id, []).append((old, new))

add("erob_001 erob_002", "completes a precise grasp", "performs a controlled end-effector manipulation near the workpiece")
add("erob_024 erob_259 erob_260", "rubble", "uneven ground")
add("erob_045 erob_046", "autonomous mobile robot warehouse", "forklift operating area")
add("erob_045 erob_046", "AMR navigates around pallets", "the visible forklift maneuvers through the available space")
add("erob_056", "robot cell", "automated equipment")
add("erob_056", "Worker crosses light curtain", "A worker approaches the automated equipment safety boundary")
add("erob_072 erob_073 erob_074 erob_075", "Two mobile robots", "Mobile robots")
add("erob_076 erob_077", "Two mobile robots", "Two robot arms")
add("erob_086 erob_100", " or one suction cup fails", "")
add("erob_092", "Cobot slows and yields during human handover", "Robot arm slows during movement")
add("erob_092", "during human handover", "during movement")
add("erob_093", "slows and yields", "slows")
add("erob_095", "warehouse", "")
add("erob_095", "pallets", "visible obstacles")
add("erob_156", " in its marked path", "")
add("erob_156", "slows or stops and proceeds only after the path is clear", "slows when approaching the visible obstacle")
add("erob_193", "robot gripper", "mechanical structure")
add("erob_193", "suction cup", "connection point")
add("erob_230", "roll-up door", "door")
add("emerg_004", "valve connection", "storage tank")
add("emerg_036 emerg_149 emerg_151 emerg_154 emerg_257 emerg_261", "silo dust collection area", "storage tank")
add("emerg_153", "silo dust collection area", "equipment enclosure")
add("emerg_061", "industrial tunnel", "enclosed rail car")
add("emerg_092 emerg_094 emerg_231 emerg_232 emerg_234 emerg_236", "retaining wall or bund", "bund")
add("emerg_093", " or bund", "")
add("emerg_158", "central valve connection", "valve")
add("emerg_167", "pipeline connection", "trailer")
add("emerg_167 emerg_168 emerg_169", "along the adjacent pipeline", "")
add("emerg_168 emerg_169 emerg_170", "pipeline connection", "industrial equipment")
add("emerg_212", "storage tank pipeline connection", "factory area")
add("emerg_228", "transmission tower", "utility pole")
add("emerg_270", "dust collection or process equipment", "industrial equipment")
add("emerg_299 emerg_300 emerg_304 emerg_307 emerg_323", "dust collection or process equipment", "industrial equipment")
add("emerg_299 emerg_300 emerg_304 emerg_307 emerg_323", ", triggering a clear shutdown response", "")
add("emerg_302", "ice-laden ", "")
add("emerg_308", "one battery module inside a battery energy storage container", "a storage tank")
add("emerg_315 emerg_316", "valve", "pipe")
add("emerg_327", "at the far end of an enclosed passage", "in the factory area")
add("emerg_328", "at the far end", "")
add("emerg_329", "at the far end of an enclosed passage", "at a closed factory gate")
add("hload_021 hload_141", "muddy", "firm")
add("hload_021 hload_141", "sink", "roll")
add("hload_022 hload_239", "climbs a muddy slope", "travels along a muddy road")
add("hload_051", "through hydraulic linkage", "")
add("hload_071 hload_076 hload_219", "underground pipe in a construction trench", "pipe")
add("hload_077", "underground pipe in a construction trench", "storage tank")
add("hload_115", "suspended precast bridge segment", "building under construction")
add("hload_120", "crane", "lift")
add("hload_120", "suspended ", "")
add("hload_214", "loaded bucket", "bucket")
add("hload_228 hload_230 hload_233", "unequal-angle ", "")
add("hload_236", "outrigger pad", "outrigger")
add("hload_284", "existing wire rope under overload", "wire rope")
add("pdef_011 pdef_012 pdef_015 pdef_018", "The borescope approaches an existing internal ", "The camera approaches a ")
add("pdef_031", ", with the spindle, tool, and workpiece fixture maintaining a credible relationship", "")
add("pdef_054 pdef_056 pdef_057 pdef_058", "pipe ", "")
add("pdef_065 pdef_094", "precision ", "")
add("pdef_071 pdef_072", "borescope", "camera")
add("pdef_074", "The borescope moves through a heat-exchanger tube bundle", "The camera moves forward")
add("pdef_107 pdef_129 pdef_130", "5-axis CNC ", "")
add("pdef_137 pdef_150 pdef_151", "fixture or pallet", "equipment")
add("pdef_144 pdef_145", "fixture or pallet", "instrument")
add("pdef_156 pdef_157 pdef_211", "During precision assembly, ", "")
add("pdef_159", "heat exchanger ", "")
add("pdef_165 pdef_166", "sprays toward the high-speed cutting tool", "sprays outward")
add("pdef_175 pdef_176", "borescope and internal ", "camera and ")
add("pdef_191", "fixture or pallet", "pipe")
add("pdef_216 pdef_217", "borescope moves through a heat-exchanger tube bundle", "camera moves forward")
add("pdef_216 pdef_217", "internal ", "")
add("pdef_226", "existing pipe weld seam", "gear")
add("vsec_011 vsec_012 vsec_014 vsec_151 vsec_152", " or safety harness", "")
add("vsec_031 vsec_032", "existing ", "")
add("vsec_061 vsec_069 vsec_115 vsec_159", "hazardous-goods loading area ", "")
add("vsec_141", "existing ", "")
add("vsec_171 vsec_227 vsec_228 vsec_229 vsec_232 vsec_233", "warehouse ", "")
add("vsec_173 vsec_175 vsec_176 vsec_187", " or vehicle", "")
add("vsec_178", "personnel or ", "")

CUSTOM = {
    "emerg_178": "A distant chemical reactor opens its relief valve after overpressure, releasing a visible gas plume while the reactor and surrounding structures remain stable.",
    "erob_099": "The visible mechanical gripper develops a small local slip at its existing contact point, pauses, and stabilizes without adding suction cups or a new workpiece.",
    "erob_246": "The visible robot arm performs one slow, controlled joint movement while preserving every link, joint center, and surrounding object.",
    "erob_261": "The single visible robot arm performs one slow, controlled joint movement while preserving its identity, link count, and workspace clearance.",
    "pdef_075": "An external inspection camera orbits slowly at constant radius around the visible heat-exchanger tube-bundle face, revealing tube openings, spacing, and surface condition while the bundle remains rigid and unchanged.",
}

def walk(value, pairs):
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
        return " ".join(value.split())
    if isinstance(value, list):
        return [walk(x, pairs) for x in value]
    if isinstance(value, dict):
        structural = {"task_id", "scene_id", "image_path", "source_image_path", "failure_target", "id"}
        return {k: (v if k in structural else walk(v, pairs)) for k, v in value.items()}
    return value

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-package-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if OUT.exists() and not args.sync_package_only and not args.force:
        raise SystemExit("Review already applied; use --sync-package-only (or remove the resolution file for a deliberate rebuild).")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    reviewed = {x["task_id"]: x for x in review}
    changed = set()
    for path in (() if args.sync_package_only else TARGETS):
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, sample in enumerate(data["samples"]):
            task_id = sample["task_id"]
            if task_id in RULES:
                data["samples"][i] = walk(sample, RULES[task_id])
                changed.add(task_id)
            if task_id in CUSTOM:
                s = data["samples"][i]
                camera = s["video_generation_prompt"].split(" Camera:", 1)[1].split(" Show ", 1)[0]
                s["video_generation_prompt"] = (
                    "Use the reference image as the exact first frame. Create a 5-second photorealistic industrial video. "
                    + CUSTOM[task_id] + " Camera:" + camera
                    + " Preserve visible identities, counts, geometry, materials, lighting, background, and non-event regions. "
                    "Do not add unrequested objects, text, logos, or watermarks; avoid cuts, global regeneration, flicker, warping, disappearance, penetration, floating motion, and identity swaps."
                )
                changed.add(task_id)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Incrementally sync prompt artifacts. The full exporter is intentionally
    # not used here because historical source paths may no longer exist even
    # though the self-contained package images are present.
    canonical_data = json.loads(TARGETS[1].read_text(encoding="utf-8"))
    canonical = {x["task_id"]: x for x in canonical_data["samples"]}
    if args.sync_package_only and OUT.is_file():
        resolution_ids = set(json.loads(OUT.read_text(encoding="utf-8"))["changed_prompt_tasks"])
        # Make custom repairs authoritative for both generation and judging.
        for target in TARGETS:
            payload = json.loads(target.read_text(encoding="utf-8"))
            for index, sample in enumerate(payload["samples"]):
                task_id = sample["task_id"]
                if task_id in CUSTOM:
                    old = str((sample.get("constraint_annotations") or {}).get("domain_scenario") or "")
                    if old and old != CUSTOM[task_id]:
                        payload["samples"][index] = walk(sample, [(old, CUSTOM[task_id])])
                        payload["samples"][index]["constraint_annotations"]["domain_scenario"] = CUSTOM[task_id]
            target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        canonical_data = json.loads(TARGETS[1].read_text(encoding="utf-8"))
        canonical = {x["task_id"]: x for x in canonical_data["samples"]}
        full = json.loads(TARGETS[0].read_text(encoding="utf-8"))
        for sample in full["samples"]:
            if sample["task_id"] in resolution_ids:
                sample["video_generation_prompt"] = canonical[sample["task_id"]]["video_generation_prompt"]
        TARGETS[0].write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    jsonl_path = PACKAGE / "prompts.jsonl"
    package_rows = [json.loads(x) for x in jsonl_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for row in package_rows:
        if row["task_id"] in canonical:
            row["video_generation_prompt"] = canonical[row["task_id"]]["video_generation_prompt"]
    jsonl_path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in package_rows) + "\n", encoding="utf-8")
    csv_path = PACKAGE / "prompts.csv"
    if csv_path.is_file():
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
            fields = list(csv_rows[0]) if csv_rows else []
        for row in csv_rows:
            if row["task_id"] in canonical and "video_generation_prompt" in row:
                row["video_generation_prompt"] = canonical[row["task_id"]]["video_generation_prompt"]
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader(); writer.writerows(csv_rows)

    if args.sync_package_only:
        if OUT.is_file():
            resolution = json.loads(OUT.read_text(encoding="utf-8"))
            for row in resolution.get("regeneration", []):
                sample = canonical.get(row["task_id"], {})
                row["current_image_path"] = sample.get("image_path")
                row["required_replacement_image"] = sample.get("image_requirement")
                row["scene_id"] = sample.get("scene_id")
            OUT.write_text(json.dumps(resolution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            replacement_rows = [x for x in resolution.get("regeneration", []) if x["action"] == "replace_reference_and_regenerate"]
            REGEN_JSONL.write_text("\n".join(json.dumps({
                "task_id": x["task_id"],
                "scene_id": x.get("scene_id"),
                "current_image_path": x.get("current_image_path"),
                "required_replacement_image": x.get("required_replacement_image"),
                "video_generation_prompt": canonical[x["task_id"]]["video_generation_prompt"],
                "status": "awaiting_replacement_image",
                "review_note": x["note"],
            }, ensure_ascii=False) for x in replacement_rows) + "\n", encoding="utf-8")
            lines = ["# Prompt Review 460：换图与重生成清单", "", f"共 {len(replacement_rows)} 条。新图片必须与下列规格一致，且不能复用其他任务的参考图。", ""]
            for x in replacement_rows:
                lines += [f"## {x['task_id']} — {x.get('scene_id')}", "", f"- 审核原因：{x['note']}", f"- 需要的图片：{x.get('required_replacement_image')}", f"- 当前图片：`{x.get('current_image_path')}`", "- 后续动作：替换参考图后，单独重新生成该任务视频；旧视频不得继续用于正式评分。", ""]
            REPLACEMENT_MD.write_text("\n".join(lines), encoding="utf-8")
        print(f"synced_package_rows={len(package_rows)}")
        return

    unresolved = []
    for task_id, row in reviewed.items():
        if task_id in REPLACE_IMAGE:
            unresolved.append({"task_id": task_id, "action": "replace_reference_and_regenerate", "note": row["note"]})
        elif row["status"] != "keep" and task_id not in changed and not row["note"].strip():
            unresolved.append({"task_id": task_id, "action": "manual_review_required", "note": row["note"]})
    OUT.write_text(json.dumps({"changed_prompt_tasks": sorted(changed), "regeneration": unresolved}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"changed={len(changed)} regeneration_or_manual={len(unresolved)}")

if __name__ == "__main__":
    main()
