"""Frozen source of truth for the canonical FORGE 5+1 scoring policy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("forge_5plus1_config.json")


def load_policy(path: str | Path = CONFIG_PATH) -> dict:
    raw = Path(path).read_bytes()
    config = json.loads(raw.decode("utf-8"))
    required = {
        "version", "technical_axes", "technical_weight", "application_axis",
        "application_weight", "strict_axis_threshold", "zero_event_coverage_cap",
        "partial_event_coverage_cap", "severe_motion_threshold",
        "severe_motion_cap", "hard_application_failure_penalty",
        "operator_min_confidence", "operator_axis_caps", "bootstrap_iterations",
        "bootstrap_seed", "invalid_policy", "gate_policy",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"5+1 scoring policy missing keys: {missing}")
    if len(config["technical_axes"]) != 5 or len(set(config["technical_axes"])) != 5:
        raise ValueError("technical_axes must contain five unique axes")
    if abs(float(config["technical_weight"]) + float(config["application_weight"]) - 1.0) > 1e-9:
        raise ValueError("technical_weight and application_weight must sum to 1")
    config["config_sha256"] = hashlib.sha256(raw).hexdigest()
    return config


CONFIG = load_policy()
