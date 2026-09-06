"""Compare model-agnostic gate settings on frozen per-sample judgments."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scoring import aggregate as aggregate_module  # noqa: E402


RESULTS = {
    "hunyuan1.5": ROOT / "reports/formal_235b_contactsheet_20260903/combined/hunyuan1.5/per_sample.json",
    "hunyuan1.5-distill": ROOT / "reports/formal_235b_hunyuan15_distill_20260904/combined/hunyuan1.5-distill/per_sample.json",
    "minimax-hailuo-2.3": ROOT / "reports/formal_235b_minimax_20260904/combined/minimax/per_sample.json",
}

# Ordered from the frozen v2.1 policy to increasingly strict alternatives.
CANDIDATES = [
    ((10.0, 30.0, 40.0), 0.50),
    ((0.0, 30.0, 40.0), 0.50),
    ((0.0, 25.0, 40.0), 0.45),
    ((0.0, 20.0, 40.0), 0.40),
    ((5.0, 20.0, 35.0), 0.40),
    ((0.0, 15.0, 30.0), 0.35),
    ((0.0, 10.0, 25.0), 0.30),
    ((0.0, 5.0, 20.0), 0.25),
]


def load_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    return payload.get("results", payload.get("samples", []))


def main() -> None:
    rows = {name: load_rows(path) for name, path in RESULTS.items()}
    # Confidence intervals are irrelevant to this deterministic sensitivity pass.
    aggregate_module.CONFIG["bootstrap_iterations"] = 10
    aggregate_module.SCORING_POLICY["bootstrap_iterations"] = 10

    print("zero/below/incomplete | safety multiplier | model scores | range | maximum")
    for caps, penalty in CANDIDATES:
        aggregate_module.SCORING_POLICY["event_coverage_caps"] = dict(
            zip(("zero", "below_strict", "incomplete"), caps)
        )
        aggregate_module.SCORING_POLICY["hard_application_failure_penalty"] = penalty
        aggregate_module.CONFIG["hard_application_failure_penalty"] = penalty
        scores = {
            name: aggregate_module.aggregate_sample_results(model_rows)["ranking_score"]
            for name, model_rows in rows.items()
        }
        spread = max(scores.values()) - min(scores.values())
        rendered = ", ".join(f"{name}={score:.3f}" for name, score in scores.items())
        print(
            f"{caps} | {penalty:.2f} | {rendered} | "
            f"{spread:.3f} | {max(scores.values()):.3f}"
        )

    print("\nCurrent gate trigger counts")
    for name, model_rows in rows.items():
        gates: Counter[str] = Counter()
        reasons: Counter[str] = Counter()
        for row in model_rows:
            adjustment = aggregate_module._constraint_adjustment(row)
            for gate in adjustment["gate_ledger"]:
                if gate["applied"]:
                    gates[gate["gate"]] += 1
                    reasons.update(gate.get("reasons") or [])
        print(f"{name}: gates={dict(gates)} reasons={dict(reasons)}")


if __name__ == "__main__":
    main()
