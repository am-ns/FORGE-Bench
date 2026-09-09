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
        "event_coverage_calibration", "motion_calibration", "null_baseline",
        "null_baseline_policy",
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
    if config["event_coverage_gate"] != "continuous_axis_calibration":
        raise ValueError("event_coverage_gate must be continuous_axis_calibration")
    event = config["event_coverage_calibration"]
    if set(event) != {"floor", "scale", "exponent", "affected_axes"}:
        raise ValueError("event_coverage_calibration has unexpected keys")
    if not (0.0 <= float(event["floor"]) <= 1.0):
        raise ValueError("event calibration floor must be in [0, 1]")
    if abs(float(event["floor"]) + float(event["scale"]) - 1.0) > 1e-9:
        raise ValueError("event calibration floor and scale must sum to 1")
    if float(event["exponent"]) <= 0.0:
        raise ValueError("event calibration exponent must be positive")
    if not set(event["affected_axes"]).issubset(set(config["technical_axes"]) | {config["application_axis"]}):
        raise ValueError("event calibration contains an unknown axis")
    motion = config["motion_calibration"]
    if set(motion) != {"floor", "scale", "exponent", "affected_axis"}:
        raise ValueError("motion_calibration has unexpected keys")
    if not (0.0 <= float(motion["floor"]) <= 1.0):
        raise ValueError("motion calibration floor must be in [0, 1]")
    if abs(float(motion["floor"]) + float(motion["scale"]) - 1.0) > 1e-9:
        raise ValueError("motion calibration floor and scale must sum to 1")
    if float(motion["exponent"]) <= 0.0:
        raise ValueError("motion calibration exponent must be positive")
    if motion["affected_axis"] not in config["technical_axes"]:
        raise ValueError("motion calibration contains an unknown axis")
    baseline = float(config["null_baseline"])
    if not 0.0 <= baseline < 100.0:
        raise ValueError("null_baseline must be in [0, 100)")
    config["config_sha256"] = hashlib.sha256(raw).hexdigest()
    return config


CONFIG = load_policy()
