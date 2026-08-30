#!/usr/bin/env python3
"""Add paper-facing implicit-rule reasoning fields to FORGE sample JSON files."""

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.reasoning_alignment import build_reasoning_alignment_questions, infer_implicit_rule_type


TARGETS = [
    REPO_ROOT / "dataset" / "annotations" / "samples.json",
    REPO_ROOT / "dataset" / "annotations" / "video_generation_500_samples.json",
]


ARTICLE_FIXES = {
    " a emergency ": " an emergency ",
    " a inspection ": " an inspection ",
    " a industrial ": " an industrial ",
    " a embodied ": " an embodied ",
    " a extreme ": " an extreme ",
}


def _clean_question_text(text: str) -> str:
    out = str(text)
    padded = f" {out} "
    for src, dst in ARTICLE_FIXES.items():
        padded = padded.replace(src, dst)
    return padded.strip()


def _samples_container(payload):
    if isinstance(payload, dict):
        return payload.get("samples", [])
    return payload


def update_file(path: Path) -> tuple[int, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    samples = _samples_container(payload)
    changed = 0
    for sample in samples:
        implicit_rule_type = infer_implicit_rule_type(sample)
        questions = build_reasoning_alignment_questions({
            **sample,
            "implicit_rule_type": sample.get("implicit_rule_type", implicit_rule_type),
        })
        for question in questions:
            question["text"] = _clean_question_text(question.get("text", ""))
        if sample.get("implicit_rule_type") != implicit_rule_type:
            sample["implicit_rule_type"] = implicit_rule_type
            changed += 1
        if sample.get("reasoning_alignment_questions") != questions:
            sample["reasoning_alignment_questions"] = questions
            changed += 1
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(samples), changed


def main() -> None:
    for path in TARGETS:
        count, changed = update_file(path)
        print(f"{path.relative_to(REPO_ROOT)}: {count} samples, {changed} field updates")


if __name__ == "__main__":
    main()
