"""Build a self-contained HF video-path and canonical-scoring package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "FORGE_HF_VIDEO_PATHS_AND_SCORING_20260911"
ZIP = OUT.with_suffix(".zip")
REPO_ID = "aaaabcd/FORGE-Bench"
REVISION = "main"

VIDEO_ROOTS = (
    ROOT / ".hf-upload-all-models-5s",
    ROOT / ".hf-upload-5s-main",
)

TASK_FIELDS = (
    "task_id",
    "domain",
    "scene_id",
    "task_category",
    "motion_type",
    "viewpoint_motion_target",
    "topology_type",
    "primary_topology",
    "sub_topology",
    "difficulty_profile",
    "constraint_annotations",
    "axis_weights",
    "axis_rubric",
    "failure_target",
    "industrial_logic_questions",
    "application_type",
    "application_value",
    "application_objective",
    "event_graph",
    "required_observable_events",
    "decision_relevant_elements",
    "application_success_criteria",
    "misleading_failure_modes",
    "reasoning_alignment_questions",
    "difficulty_level",
    "implicit_rule_type",
    "challenge_difficulty_level",
    "content_difficulty_score",
    "content_difficulty_factors",
)

CANONICAL_FILES = (
    "PROJECT_STATUS.md",
    "README.md",
    "BENCHMARK_CARD.md",
    "SUBMISSION.md",
    "dataset/HUGGING_FACE_DATASET_CARD.md",
    "dataset/annotations/README.md",
    "dataset/annotations/DATASET.md",
    "docs/SCORING_METHOD.md",
    "docs/CODEBASE_GUIDE.md",
    "docs/OPERATOR_EVIDENCE.md",
    "docs/FORGE_COMPLETE_EVALUATION_HANDOFF.json",
    "requirements.txt",
    "local_video_judge.py",
)

SOURCE_TREES = ("eval", "scoring")
SOURCE_SUFFIXES = {".py", ".json", ".md", ".yaml", ".yml"}
PAPER_SUFFIXES = {".tex", ".bib", ".md"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists() or ZIP.exists():
        if "--force" not in sys.argv:
            raise FileExistsError(f"Refusing to overwrite existing output: {OUT} or {ZIP}")
        if OUT.exists():
            shutil.rmtree(OUT)
        if ZIP.exists():
            ZIP.unlink()
    OUT.mkdir(parents=True)

    annotation_path = ROOT / "dataset/annotations/video_generation_500_samples.json"
    annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
    tasks = annotation["samples"]
    by_id = {row["task_id"]: row for row in tasks}
    if len(tasks) != 500 or len(by_id) != 500:
        raise RuntimeError("Canonical annotation must contain 500 unique tasks")

    videos: dict[str, Path] = {}
    for base in VIDEO_ROOTS:
        for path in base.rglob("*.mp4"):
            rel = path.relative_to(base).as_posix()
            if rel in videos:
                raise RuntimeError(f"Duplicate published path: {rel}")
            videos[rel] = path

    rows = []
    model_tasks: dict[str, set[str]] = {}
    for rel, path in sorted(videos.items()):
        model, _, _ = rel.partition("/")
        task_id = path.stem
        if task_id not in by_id:
            raise RuntimeError(f"Unknown task ID in video path: {rel}")
        model_tasks.setdefault(model, set()).add(task_id)
        encoded_rel = "/".join(quote(part) for part in rel.split("/"))
        rows.append(
            {
                "model": model,
                "task_id": task_id,
                "domain": by_id[task_id]["domain"],
                "task_category": by_id[task_id]["task_category"],
                "motion_type": by_id[task_id]["motion_type"],
                "hf_repo": REPO_ID,
                "hf_revision": REVISION,
                "hf_repo_path": rel,
                "hf_uri": f"hf://datasets/{REPO_ID}/{rel}",
                "download_url": (
                    f"https://huggingface.co/datasets/{REPO_ID}/resolve/"
                    f"{REVISION}/{encoded_rel}?download=true"
                ),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    expected = set(by_id)
    if len(model_tasks) != 10 or len(rows) != 5000:
        raise RuntimeError(f"Expected 10 models/5000 videos, got {len(model_tasks)}/{len(rows)}")
    for model, ids in model_tasks.items():
        if ids != expected:
            raise RuntimeError(f"{model}: missing={len(expected-ids)}, extra={len(ids-expected)}")

    fields = list(rows[0])
    with (OUT / "hf_video_paths_5000.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (OUT / "hf_video_paths_5000.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT / "task_scoring_metrics_500.jsonl").open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps({key: task.get(key) for key in TASK_FIELDS}, ensure_ascii=False) + "\n")

    shutil.copy2(annotation_path, OUT / annotation_path.name)
    source_dir = OUT / "canonical_scoring_sources"
    for rel in CANONICAL_FILES:
        source = ROOT / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        target = source_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for tree in SOURCE_TREES:
        for source in sorted((ROOT / tree).rglob("*")):
            if not source.is_file() or source.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            target = source_dir / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    paper_root = ROOT / "paper/forge_bench_draft"
    for source in sorted(paper_root.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in PAPER_SUFFIXES:
            continue
        target = OUT / "paper" / source.relative_to(paper_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    reference_source = ROOT / "reports/video_generation_500_package/images"
    reference_target = OUT / "reference_images_500"
    reference_files = [path for path in reference_source.iterdir() if path.is_file()]
    reference_by_id: dict[str, Path] = {}
    for source in reference_files:
        if source.stem in reference_by_id:
            raise RuntimeError(f"Duplicate reference-image task ID: {source.stem}")
        reference_by_id[source.stem] = source
    if set(reference_by_id) != expected:
        raise RuntimeError(
            f"Reference images do not match tasks: missing={len(expected-set(reference_by_id))}, "
            f"extra={len(set(reference_by_id)-expected)}"
        )
    reference_target.mkdir()
    for task_id, source in sorted(reference_by_id.items()):
        shutil.copy2(source, reference_target / source.name)

    config = json.loads((ROOT / "scoring/forge_v4_config.json").read_text(encoding="utf-8"))
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "hf_repo": REPO_ID,
        "hf_revision": REVISION,
        "models": {model: len(ids) for model, ids in sorted(model_tasks.items())},
        "model_count": len(model_tasks),
        "tasks_per_model": 500,
        "video_count": len(rows),
        "reference_image_count": len(reference_by_id),
        "identical_task_id_sets": all(ids == expected for ids in model_tasks.values()),
        "scoring_policy_version": config["version"],
        "headline_axes": config["headline_axes"],
        "technical_axes": config["technical_axes"],
        "application_axis": config["application_axis"],
        "headline_aggregation": config["headline_aggregation"],
        "event_coverage_gate": config["event_coverage_gate"],
        "operator_axis_caps": config["operator_axis_caps"],
        "canonical_config_sha256": sha256(ROOT / "scoring/forge_v4_config.json"),
        "annotation_sha256": sha256(annotation_path),
    }
    write_json(OUT / "package_manifest.json", summary)

    readme = f"""# FORGE Hugging Face 视频路径与完整评分指标包

生成时间：{summary['generated_at_utc']}

## 内容

- `canonical_scoring_sources/PROJECT_STATUS.md`：当前项目里程碑、已完成项、待办项与分数有效性说明。
- `hf_video_paths_5000.csv`：Excel 友好的 UTF-8 BOM 表格，含模型、任务、HF 路径、下载 URL、大小和 SHA-256。
- `hf_video_paths_5000.jsonl`：同一份 5000 视频清单的机器可读版本。
- `task_scoring_metrics_500.jsonl`：500 个任务的完整逐任务评分指标、权重、rubric、失败目标、逻辑问题、应用价值和难度字段。
- `video_generation_500_samples.json`：正式 500 任务完整标注原文。
- `reference_images_500/`：与 500 个任务 ID 一一对应的原始参考图片。
- `canonical_scoring_sources/`：完整 `eval/`、`scoring/` 正式源码、配置、说明文档及本地 Judge 入口（不含缓存）。
- `paper/`：与本次发布状态对齐的中英文论文源文件。
- `package_manifest.json`：版本、数量与源文件哈希。
- `SHA256SUMS.txt`：包内所有文件的校验和。

## 数据结论

- Hugging Face 数据集：`{REPO_ID}`（revision `{REVISION}`）
- 模型数：10
- 每模型任务数：500
- 视频总数：5000
- 原始参考图片：500
- 10 个模型任务 ID 集合完全一致：是
- 评分政策：`{config['version']}`

## 路径用法

清单中的 `hf_repo_path` 是仓库内相对路径；`hf_uri` 可用于支持 HF URI 的工具；`download_url` 是浏览器/API 可直接下载地址。

评分唯一规范以 `canonical_scoring_sources/scoring/forge_v4_config.json` 及其 SHA-256 为准。逐任务权重与 rubric 以 `task_scoring_metrics_500.jsonl` 为准。
"""
    (OUT / "README_zh.md").write_text(readme, encoding="utf-8")

    packaged_files = sorted(path for path in OUT.rglob("*") if path.is_file())
    sums = "".join(f"{sha256(path)}  {path.relative_to(OUT).as_posix()}\n" for path in packaged_files)
    (OUT / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")

    result = {**summary, "output": str(OUT)}
    if "--zip" in sys.argv:
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
                archive.write(path, (Path(OUT.name) / path.relative_to(OUT)).as_posix())
        result.update({"zip": str(ZIP), "zip_bytes": ZIP.stat().st_size})

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
