#!/usr/bin/env python3
"""Report generation: serialize benchmark results to JSON with float sanitization."""

import json
import math
import sys

# -- Tunable thresholds -------------------------------------------------------
CONFIG = {
    "indent": 2,                      # JSON indentation level for readability
}


def _sanitize_value(value):
    """Recursively replace NaN and Inf float values with None.

    Args:
        value: Any JSON-serialisable value (dict, list, float, etc.).

    Returns:
        The value with NaN/Inf replaced by None.
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    return value


def generate_report(results: dict, path: str | None = None) -> str:
    """Generate a JSON report from benchmark results.

    Sanitizes float values by replacing math.nan and math.inf with None
    before json.dumps to prevent serialization errors.

    Args:
        results: Benchmark results dict.
        path: Optional file path to write the JSON report.

    Returns:
        JSON string of the sanitized report.
    """
    sanitized = _sanitize_value(results)

    try:
        report_json = json.dumps(sanitized, indent=CONFIG["indent"], default=str)
    except (TypeError, ValueError) as exc:
        print(f"ERROR: JSON serialization failed: {exc}", file=sys.stderr)
        report_json = json.dumps({"error": str(exc)}, indent=CONFIG["indent"])

    if path is not None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(report_json)
        except OSError as exc:
            print(f"ERROR: could not write report to {path}: {exc}", file=sys.stderr)

    return report_json
