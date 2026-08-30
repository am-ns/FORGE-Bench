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
        "application_weight", "strict_axis_threshold", "severe_motion_threshold",
        "severe_motion_cap", "hard_application_failure_penalty", "event_coverage_gate",
        "event_coverage_caps",
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
    if config["event_coverage_gate"] != "tiered_caps":
        raise ValueError("event_coverage_gate must be tiered_caps")
    event_caps = config["event_coverage_caps"]
    if set(event_caps) != {"zero", "below_strict", "incomplete"}:
        raise ValueError("event_coverage_caps must define zero, below_strict, and incomplete")
    cap_values = [float(event_caps[key]) for key in ("zero", "below_strict", "incomplete")]
    if not (0.0 <= cap_values[0] <= cap_values[1] <= cap_values[2] <= 100.0):
        raise ValueError("event_coverage_caps must be monotonic values in [0, 100]")
    config["config_sha256"] = hashlib.sha256(raw).hexdigest()
    return config


CONFIG = load_policy()
