"""Frozen source of truth for the canonical FORGE six-axis scoring policy."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("forge_v4_config.json")


def load_policy(path: str | Path = CONFIG_PATH) -> dict:
    raw = Path(path).read_bytes()
    config = json.loads(raw.decode("utf-8"))
    required = {
        "version", "headline_axes", "technical_axes", "application_axis",
        "headline_aggregation", "strict_axis_threshold", "event_coverage_gate",
        "event_coverage_cap_axes", "operator_min_confidence", "operator_axis_caps",
        "bootstrap_iterations", "bootstrap_seed", "invalid_policy", "gate_policy",
        "input_validation", "operator_flag_policy", "cache_migration",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"six-axis scoring policy missing keys: {missing}")
    if len(config["technical_axes"]) != 5 or len(set(config["technical_axes"])) != 5:
        raise ValueError("technical_axes must contain five unique axes")
    expected_axes = list(config["technical_axes"]) + [config["application_axis"]]
    if config["headline_axes"] != expected_axes:
        raise ValueError("headline_axes must be the five technical axes followed by application_axis")
    if config["headline_aggregation"] != "unweighted_arithmetic_mean_after_caps":
        raise ValueError("headline_aggregation must be unweighted_arithmetic_mean_after_caps")
    if config["event_coverage_gate"] != "direct_cap_all_headline_axes":
        raise ValueError("event_coverage_gate must be direct_cap_all_headline_axes")
    if config["event_coverage_cap_axes"] != config["headline_axes"]:
        raise ValueError("event_coverage_cap_axes must exactly match headline_axes")
    if config["application_axis"] in config["technical_axes"]:
        raise ValueError("application_axis must be distinct from technical_axes")
    for key in ("strict_axis_threshold",):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError(f"invalid policy threshold: {key}")
    config["config_sha256"] = hashlib.sha256(raw).hexdigest()
    return config


CONFIG = load_policy()


def valid_score(value: object, upper: float = 100.0) -> bool:
    """JSON scores must be finite numbers, never booleans or coerced strings."""
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value) and 0 <= value <= upper)


def operator_caps(evidence: dict | None) -> list[tuple[str, float, str]]:
    """One shared, strictly typed implementation of the formal operator rules."""
    operators = evidence.get("operators", {}) if isinstance(evidence, dict) else {}
    if not isinstance(operators, dict):
        return []
    caps = CONFIG["operator_axis_caps"]
    rules = []
    def eligible(name):
        payload = operators.get(name)
        return payload if (
            isinstance(payload, dict)
            and payload.get("used_for_axis_cap") is True
            and payload.get("validity") in (None, "valid")
            and valid_score(payload.get("confidence"), 1.0)
            and payload["confidence"] >= CONFIG["operator_min_confidence"]
        ) else {}
    local = eligible("local_region_lock")
    if local.get("risk") == "global_regeneration":
        rules.extend([
            ("reference_and_motion_fidelity", caps["global_regeneration_reference"], "operator_global_regeneration"),
            ("temporal_consistency", caps["global_regeneration_temporal"], "operator_global_regeneration"),
        ])
    elif valid_score(local.get("changed_fraction"), 1.0) and local["changed_fraction"] > 0.25:
        rules.append(("reference_and_motion_fidelity", caps["large_nonlocal_change_reference"], "operator_large_nonlocal_change"))
    temporal = eligible("temporal_break")
    if temporal.get("abrupt_transition") is True:
        late = temporal.get("late_break") is True
        rules.append(("temporal_consistency", caps["late_abrupt_temporal_break" if late else "abrupt_temporal_transition"],
                      "operator_late_abrupt_temporal_break" if late else "operator_abrupt_temporal_transition"))
    if eligible("rigid_joint_tracking").get("risk") == "rigid_drift":
        rules.append(("geometric_integrity", caps["rigid_drift_geometry"], "operator_rigid_drift"))
    return rules


def publication_issue(aggregate: dict) -> str | None:
    """Reject incomplete or obsolete aggregates at every publication entry point."""
    if aggregate.get("ranking_publishable") is not True or aggregate.get("ranking_status") != "complete":
        return "non_publishable"
    policy = aggregate.get("scoring_policy") or {}
    if policy.get("version") != CONFIG["version"]:
        return "obsolete_or_missing_scoring_version"
    if policy.get("config_sha256") != CONFIG["config_sha256"]:
        return "scoring_config_mismatch"
    score = aggregate.get("ranking_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        return "invalid_ranking_score"
    return None
