# FORGE Operator Evidence Methodology

FORGE uses computer-vision operators as auditable evidence for model-led
judging. Operators are not independent replacements for the VLM judge. They
produce structured observations, confidence, validity, and risk flags. A signal
can cap a public axis only when the task plan marks it as cap-eligible, the
operator reports `valid`, and confidence passes the scoring threshold.

## Evidence Tiers

| Tier | Meaning | Headline Effect |
|---|---|---|
| `axis_cap` | Strong task-conditioned evidence for a failure mode. | May cap a public axis or ranking score when confidence and validity pass. |
| `judge_evidence` | Useful structured evidence with known ambiguity. | Given to the judge; may cap only when explicitly marked and high-confidence. |
| `diagnostic` | Report-only evidence. | Never directly caps headline scoring. |

## Operators

| Operator | Scientific Role | Cap Policy | Known Limits |
|---|---|---|---|
| `local_region_lock` | Detects global regeneration versus localized change after affine alignment. | Cap-eligible for reference/temporal axes on static or local-change tasks. Disabled when camera motion confounds alignment. | Pixel-difference based; cannot identify semantic object masks. |
| `temporal_break` | Measures abrupt adjacent-frame discontinuity using intensity and histogram deltas. | Cap-eligible for temporal consistency when discontinuity is severe. | Fast intended events can raise the signal; judge context remains required. |
| `rigid_joint_tracking` | Tracks corner features and checks camera-compensated pairwise stability, affine inliers, and spatial coverage. | Conditional cap for geometry only when enough tracks, coverage, validity, and confidence are present. | Sparse/textureless scenes may be invalid rather than failed. It is not a full articulated-pose solver. |
| `fluid_diffusion` | Tracks foreground event area, centroid continuity, component count, and jitter for fluid/smoke/fire diagnostics. | Diagnostic/judge evidence only; no direct hard cap by default. | Foreground masks are not semantic fluid masks. It can support but not prove physical correctness. |
| `safety_compliance_motion` | Measures coarse early/late optical-flow change as weak stop/slowdown evidence. | Diagnostic/judge evidence only. | Cannot verify alarms, intent, or rule compliance without VLM reasoning. |
| `viewpoint_motion_fidelity` | Estimates requested camera motion and static-task violations. | Cap-eligible for viewpoint/static-control failures. | Uses image motion proxies; low-texture or low-parallax footage may reduce validity. |

## Reporting Requirements

Every result should preserve:

- the operator plan used for the sample;
- each operator's `target`, `expected_signal`, `tier`, `used_for_axis_cap`,
  `confidence`, and `validity`;
- risk flags and cap reasons in `aggregate.json` and `report.json`;
- diagnostic-only status for `fluid_diffusion`, `safety_compliance_motion`, and
  `visual_quality_score`.

This makes the evidence layer falsifiable: a paper reader can see whether a
score changed because of a model judge, a deterministic cap, missing event
coverage, or a diagnostic signal that did not affect the headline score.
