# Weakness Targets v2

The frozen taxonomy identifier is `forge-weakness-targets-v2.0.0`; the attached
diagnostic object schema is `2.0.0`. Any semantic change, target rename, mapping
change, threshold change, or denominator change requires a new taxonomy version.

Task intent comes only from annotations. Observed failure comes only from
evaluation evidence. Direct tagged binary judgments have priority, followed by
required-event checks, dedicated scores, and axis-score proxies. Missing evidence
is `unknown`, never a pass; inapplicable checks are `not_applicable`.

The nine auditable targets are organized under the benchmark's canonical 5+1
dimensions: industrial logic and fact alignment, geometric integrity, physical
plausibility, temporal consistency, reference and motion fidelity, plus the
separate application-usefulness dimension. Causal/event/safety targets belong
to industrial logic; reference preservation and camera execution belong to the
shared reference-and-motion dimension.

Newly discovered failure targets must be attached to one of these six dimensions
instead of creating a parallel direction. Adding or semantically changing a
target requires a taxonomy version bump; adding a new evidence label beneath an
existing target does not.

```powershell
python scripts/weakness_targets.py taxonomy
python scripts/weakness_targets.py validate dataset/annotations/samples.json dataset/annotations/video_generation_500_samples.json
python scripts/weakness_targets.py backfill reports/old/per_sample.json reports/old/per_sample.with_weakness_targets.json --summary reports/old/weakness_targets.json
python scripts/weakness_targets.py compare model_a=reports/a model_b=reports/b --output reports/weakness_targets_compare.json
```

Each target reports applicable, evidenced, pass, fail, unknown, not-applicable,
and severe counts; evidence sources and examples; evidence coverage; and failure
rate. Failure rate uses evidenced applicable samples. Diagnostics never alter
axis scores, weighted score, ranking score, gates, or the 235B process.
