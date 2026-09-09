#!/usr/bin/env python3
"""Build the self-contained package for every approved video regeneration task."""

from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/video_regeneration_final_package_50"
ZIP = ROOT / "reports/FORGE_50_VIDEO_REGENERATION_FINAL.zip"
DATA = ROOT / "dataset/annotations/video_generation_500_samples.json"
RESOLUTION = ROOT / "reports/prompt_review_460_resolution.json"

CAMERA_ZH = {
    "static": "相机保持完全固定",
    "orbit": "相机以恒定半径绕主体平滑环绕45度",
    "dolly": "相机保持主体入镜并平滑向前推进",
    "pan": "相机从左向右平滑巡检平移，不环绕主体",
}

def chinese_prompt(sample: dict) -> str:
    title = sample.get("task_title_zh") or sample.get("constraint_annotations", {}).get("task_title_zh") or sample["task_title"]
    return (
        f"以参考图片作为严格首帧，生成一段5秒的写实工业视频。核心任务：{title}。"
        f"{CAMERA_ZH[sample['motion_type']]}。只执行核心任务指定的局部动作；保持已有主体的身份、数量、"
        "几何结构、材质、光照、背景和非事件区域不变。不得凭空增加人员、车辆、工具、载荷、文字或其他物体。"
    )

def main() -> None:
    resolution = json.loads(RESOLUTION.read_text(encoding="utf-8"))
    task_ids = sorted({row["task_id"] for row in resolution["regeneration"]})
    samples = {x["task_id"]: x for x in json.loads(DATA.read_text(encoding="utf-8"))["samples"]}
    if len(task_ids) != 50:
        raise RuntimeError(f"Expected 50 regeneration tasks, found {len(task_ids)}")

    images = OUT / "images"
    images.mkdir(parents=True, exist_ok=True)
    rows = []
    for task_id in task_ids:
        sample = samples[task_id]
        source = ROOT / sample["image_path"]
        if not source.is_file():
            source = ROOT / "reports/video_generation_500_package/images" / f"{task_id}.jpg"
        if not source.is_file():
            source = ROOT / "reports/modified_tasks_final_review/new_references" / f"{task_id}.jpg"
        if not source.is_file():
            raise FileNotFoundError(f"No packaged reference found for {task_id}")
        destination = images / f"{task_id}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        rows.append({
            "task_id": task_id,
            "scene_id": sample["scene_id"],
            "image": f"images/{destination.name}",
            "motion_type": sample["motion_type"],
            "prompt_en": sample["video_generation_prompt"],
            "prompt_zh": chinese_prompt(sample),
        })

    (OUT / "prompts.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    with (OUT / "prompts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "manifest.json").write_text(json.dumps({"count": len(rows), "tasks": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "使用说明.txt").write_text(
        "FORGE 视频重新生成最终包\n\n"
        "共 50 道。每道题使用 images 文件夹中同名图片作为严格首帧，使用 prompts.jsonl 或 prompts.csv 中的 prompt_en 生成5秒视频。\n"
        "prompt_zh 是中文核对文本，不要代替英文生成提示词。输出视频建议命名为 task_id.mp4。\n",
        encoding="utf-8-sig",
    )

    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, Path(OUT.name) / path.relative_to(OUT))
    print(json.dumps({"tasks": len(rows), "folder": str(OUT), "zip": str(ZIP), "zip_bytes": ZIP.stat().st_size}, ensure_ascii=False))

if __name__ == "__main__":
    main()
