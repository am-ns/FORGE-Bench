#!/usr/bin/env python3
"""Reproducibility metadata for FORGE-Bench evaluation runs."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from eval import llm_judge, llm_judge_openai
from eval.operator_evidence import CONFIG as OPERATOR_EVIDENCE_CONFIG
from eval.viewpoint_motion_fidelity.eval import CONFIG as VIEWPOINT_MOTION_CONFIG
from scoring.aggregate import CONFIG as AGGREGATE_CONFIG
from scoring.per_sample import CONFIG as PER_SAMPLE_CONFIG


METHODOLOGY_VERSION = "forge-bench-paper-v4.2.1"


def file_sha256(path: str | Path) -> str | None:
    """Return the SHA-256 digest for a file, or None when absent."""
    fpath = Path(path)
    if not fpath.is_file():
        return None
    h = hashlib.sha256()
    with fpath.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_fingerprint(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tree_fingerprint(root: str | Path, suffix: str = ".py") -> str:
    """Return a deterministic hash of source files under a directory."""
    base = Path(root)
    h = hashlib.sha256()
    if not base.is_dir():
        return ""
    for path in sorted(p for p in base.rglob(f"*{suffix}") if p.is_file()):
        rel = path.relative_to(base).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        digest = file_sha256(path)
        if digest:
            h.update(digest.encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def build_run_metadata(
    *,
    model_name: str,
    video_dir: str,
    samples_json: str,
    output_dir: str,
    llm_provider: str,
    use_llm: bool,
    model_answers_path: str | None = None,
) -> dict:
    """Build a compact metadata block that makes a run auditable."""
    if llm_provider == "openai_compat":
        judge_model = llm_judge_openai.CONFIG.get("default_model")
        judge_base_url = os.environ.get("OPENAI_COMPAT_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    else:
        judge_model = llm_judge.CONFIG.get("default_model")
        judge_base_url = "anthropic"

    config_snapshot = {
        "scoring_per_sample": PER_SAMPLE_CONFIG,
        "scoring_aggregate": AGGREGATE_CONFIG,
        "viewpoint_motion_fidelity": VIEWPOINT_MOTION_CONFIG,
        "operator_evidence": OPERATOR_EVIDENCE_CONFIG,
        "llm_judge": llm_judge_openai.CONFIG if llm_provider == "openai_compat" else llm_judge.CONFIG,
    }

    return {
        "schema_version": "forge-bench-result-v2",
        "methodology_version": METHODOLOGY_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
        "evaluated_model_name": model_name,
        "generator_model": model_name,
        "video_dir": video_dir,
        "samples_json": samples_json,
        "samples_json_sha256": file_sha256(samples_json),
        "eval_code_sha256": _tree_fingerprint("eval"),
        "scoring_code_sha256": _tree_fingerprint("scoring"),
        "model_answers_path": model_answers_path,
        "model_answers_sha256": file_sha256(model_answers_path) if model_answers_path else None,
        "output_dir": output_dir,
        "llm_provider": llm_provider,
        "llm_enabled": bool(use_llm),
        "judge_model": judge_model,
        "judge_provider": llm_provider,
        "judge_base_url": judge_base_url,
        "judge_temperature": config_snapshot["llm_judge"].get("judge_temperature"),
        "judge_model_is_floating_alias": "latest" in str(judge_model).lower(),
        "paper_reproducibility_warning": (
            "OPENAI_COMPAT_MODEL contains 'latest'; set a fixed judge model id for paper runs."
            if "latest" in str(judge_model).lower() else None
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "opencv": cv2.__version__,
            "numpy": np.__version__,
        },
        "config_snapshot": config_snapshot,
        "config_sha256": _json_fingerprint(config_snapshot),
    }
