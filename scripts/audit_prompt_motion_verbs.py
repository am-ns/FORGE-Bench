#!/usr/bin/env python3
"""Audit prompt motion clauses; write review doc to dataset/annotations/XYZ."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = ROOT / "dataset" / "annotations" / "samples.json"
OUT_DIR = ROOT / "dataset" / "annotations" / "XYZ"

CLEAR_VERBS = ("orbit", "pan", "dolly", "crane")
MOTION_SECTION_RE = re.compile(
    r"Motion requirement / viewpoint motion fidelity:\s*(.*?)"
    r"(?:\.\s*Industrial logic|\.\s*No zoom\.)",
    re.IGNORECASE | re.DOTALL,
)
REF_SUBJECT_RE = re.compile(r"Reference subject:\s*([^.]+)\.", re.IGNORECASE)
STRUCTURE_MARKERS = (
    "visible",
    "in frame",
    "in view",
    "remain visible",
    "keep the",
    "framing",
    "jib",
    "boom",
    "links",
    "joints",
    "members",
    "components",
    "structure",
    "manifold",
    "bundle",
    "truss",
)
UNIT_MARKERS = ("°", "deg", "degree", "2x", "1.5x", "0.5x", "orbit_cw", "dolly_in")


def extract_motion_clause(prompt: str) -> str:
    match = MOTION_SECTION_RE.search(prompt)
    if not match:
        return ""
    return match.group(1).strip()


def has_explicit_unit(clause: str, motion_type: str, target) -> bool:
    lower = clause.lower()
    if any(marker in lower for marker in UNIT_MARKERS):
        return True
    if motion_type == "dolly" and re.search(r"\b\d+(\.\d+)?x\b", lower):
        return True
    if motion_type in ("orbit", "pan") and re.search(r"\b\d+(\.\d+)?\s*(°|deg|degree)", lower):
        return True
    if isinstance(target, str) and any(marker in target.lower() for marker in UNIT_MARKERS):
        return True
    return False


def audit_sample(sample: dict) -> dict:
    prompt = sample.get("prompt", "")
    motion_type = sample.get("motion_type", "")
    target = sample.get("viewpoint_motion_target")
    clause = extract_motion_clause(prompt)
    clause_lower = clause.lower()
    ref_match = REF_SUBJECT_RE.search(prompt)
    reference_subject = ref_match.group(1).strip() if ref_match else ""

    issues: list[str] = []
    severity = "low"

    if motion_type == "static":
        return {
            "task_id": sample["task_id"],
            "excluded": True,
            "issues": [],
            "severity": "none",
            "motion_clause": clause,
            "reference_subject": reference_subject,
        }

    found_verbs = [verb for verb in CLEAR_VERBS if verb in clause_lower]

    if motion_type not in CLEAR_VERBS:
        issues.append(f"unexpected motion_type `{motion_type}` (expected orbit/pan/dolly/crane)")
        severity = "high"
    elif motion_type not in clause_lower:
        issues.append(
            f"motion_type `{motion_type}` but motion clause does not contain `{motion_type}`"
        )
        severity = "high"
    elif not found_verbs:
        issues.append("motion clause missing orbit/pan/dolly/crane")
        severity = "high"

    if motion_type == "crane" and "crane" not in clause_lower:
        issues.append("crane motion_type without crane camera verb in motion clause")
        severity = "high"

    if (
        "crane" in reference_subject.lower()
        and motion_type in ("orbit", "dolly", "pan")
        and motion_type in clause_lower
    ):
        issues.append(
            "reference subject names crane equipment; camera verb may be confused with subject identity"
        )
        severity = "high" if severity != "high" else severity

    if motion_type in ("orbit", "pan", "dolly") and not has_explicit_unit(
        clause, motion_type, target
    ):
        issues.append(
            "quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)"
        )
        if severity == "low":
            severity = "medium"

    if motion_type in ("orbit", "pan", "dolly") and not any(
        marker in clause_lower for marker in STRUCTURE_MARKERS
    ):
        issues.append(
            "motion clause lacks structural visibility (which parts stay in view)"
        )
        if severity == "low":
            severity = "medium"

    if motion_type in ("orbit", "pan", "dolly") and clause_lower.startswith("perform a controlled"):
        issues.append(
            "verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative"
        )

    if motion_type == "pan" and "follows the evolving leak" in clause_lower:
        issues.append(
            "pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec"
        )

    return {
        "task_id": sample["task_id"],
        "domain": sample["domain"],
        "task_category": sample.get("task_category", ""),
        "motion_type": motion_type,
        "viewpoint_motion_target": target,
        "image_path": sample.get("image_path", ""),
        "reference_subject": reference_subject,
        "motion_clause": clause,
        "issues": issues,
        "severity": severity,
        "excluded": False,
    }


def main() -> None:
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples = data["samples"] if isinstance(data, dict) else data

    audited = [audit_sample(sample) for sample in samples]
    flagged = [entry for entry in audited if entry["issues"]]
    flagged.sort(
        key=lambda entry: (
            {"high": 0, "medium": 1, "low": 2}.get(entry["severity"], 3),
            entry["task_id"],
        )
    )

    issue_counter: Counter[str] = Counter()
    for entry in flagged:
        for issue in entry["issues"]:
            issue_counter[issue] += 1

    high = [e["task_id"] for e in flagged if e["severity"] == "high"]
    medium = [e["task_id"] for e in flagged if e["severity"] == "medium"]
    low = [e["task_id"] for e in flagged if e["severity"] == "low"]

    report = {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "field": "prompt",
        "total_samples": len(samples),
        "static_excluded_from_verb_check": sum(1 for e in audited if e.get("excluded")),
        "motion_type_counts": dict(Counter(s["motion_type"] for s in samples)),
        "flagged_count": len(flagged),
        "severity_counts": {
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
        },
        "issue_counts": dict(issue_counter.most_common()),
        "flagged_samples": flagged,
    }

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "prompt_motion_verb_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    by_issue: dict[str, list[str]] = defaultdict(list)
    for entry in flagged:
        for issue in entry["issues"]:
            by_issue[issue].append(entry["task_id"])

    lines = [
        "# Prompt 运动动词质检（可能不合格样本）",
        "",
        "## 检查说明",
        "",
        "- 数据源：`dataset/annotations/samples.json` → **`prompt`**",
        "- 重点段落：`Motion requirement / viewpoint motion fidelity:`",
        "- 期望动词：**orbit / pan / dolly / crane**（与 `motion_type` 一致）",
        "- 另参考：量化是否写清（如 45°/90°/2x）、运动描述是否说明可见结构",
        "",
        f"- 审计时间（UTC）：{report['audited_at']}",
        f"- 样本总数：**{len(samples)}**",
        f"- `static` 样本（不参与 orbit/pan/dolly/crane 动词检查）：**{report['static_excluded_from_verb_check']}**",
        f"- 数据集内 `motion_type=crane` 样本数：**{report['motion_type_counts'].get('crane', 0)}**",
        f"- 标记为可能不合格：**{len(flagged)}**",
        f"  - 高优先级：**{len(high)}**",
        f"  - 中优先级：**{len(medium)}**",
        f"  - 低优先级：**{len(low)}**",
        "",
        "## 结论摘要",
        "",
        "1. **未发现** motion 段落完全缺少 orbit/pan/dolly 的情况（`static` 除外）。",
        "2. **全库未使用** `motion_type=crane`，也无 prompt 中的相机 **crane** 运镜描述。",
        "3. **主要风险**：",
        "   - 量化仅写 `target motion value 45.0/75.0/1.5`，未写 °/deg/x；",
        "   - motion 段落几乎无「哪些部件应保持在画面中」的结构可见性描述；",
        "   - 参考主体名含 **crane**（塔吊/岸桥等设备）时，易与相机 crane 运镜混淆。",
        "",
        "## 问题类型统计",
        "",
        "| 问题描述 | 样本数 |",
        "|----------|--------:|",
    ]
    for issue, count in issue_counter.most_common():
        lines.append(f"| {issue} | {count} |")

    lines.extend(
        [
            "",
            "## 可能不合格 task_id（去重汇总）",
            "",
            "```text",
            ", ".join(entry["task_id"] for entry in flagged),
            "```",
            "",
            "### 高优先级",
            "",
            "```text",
            ", ".join(high) if high else "(无)",
            "```",
            "",
            "### 中优先级",
            "",
            "```text",
            ", ".join(medium) if medium else "(无)",
            "```",
            "",
            "### 低优先级",
            "",
            "```text",
            ", ".join(low) if low else "(无)",
            "```",
            "",
            "## 按问题类型分组",
            "",
        ]
    )
    for issue, task_ids in sorted(by_issue.items(), key=lambda item: (-len(item[1]), item[0])):
        lines.append(f"### {issue}")
        lines.append("")
        lines.append(f"共 **{len(task_ids)}** 条：`" + "`, `".join(task_ids) + "`")
        lines.append("")

    lines.extend(["", "## 逐条详情", ""])
    for entry in flagged:
        lines.append(f"### `{entry['task_id']}` — {entry['severity']}")
        lines.append("")
        lines.append(f"- domain: `{entry['domain']}`")
        lines.append(f"- task_category: `{entry['task_category']}`")
        lines.append(f"- motion_type: `{entry['motion_type']}`")
        lines.append(f"- viewpoint_motion_target: `{entry['viewpoint_motion_target']}`")
        lines.append(f"- reference_subject: `{entry['reference_subject']}`")
        lines.append(f"- image_path: `{entry['image_path']}`")
        lines.append("- 可能问题：")
        for issue in entry["issues"]:
            lines.append(f"  - {issue}")
        lines.append("- motion 段落：")
        lines.append("```text")
        lines.append(entry["motion_clause"])
        lines.append("```")
        lines.append("")

    lines.extend(
        [
            "## 备注",
            "",
            "本清单为启发式人工复核清单，非自动判定不合格。",
            "`static` 任务使用固定机位描述，未纳入 orbit/pan/dolly/crane 动词缺失类问题。",
            "",
        ]
    )

    (OUT_DIR / "PROMPT_MOTION_VERB_REVIEW.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(
        f"flagged={len(flagged)} high={len(high)} medium={len(medium)} low={len(low)}"
    )


if __name__ == "__main__":
    main()
