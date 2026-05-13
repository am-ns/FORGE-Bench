# FORGE-Bench

Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation.

FORGE-Bench evaluates image-to-video generation for industrial use cases where
functional fidelity matters more than visual appeal. A video can look realistic
while still being unusable: a missing gear tooth, merged PCB traces, distorted
robot joints, or a camera orbit that ignores the requested angle is a functional
failure even if the clip is perceptually plausible.

The benchmark combines deterministic computer-vision checks with VLM judging.
The intent is strict but not degenerate scoring: failures should be penalized
strongly, while floor values prevent all-zero reports that are hard to analyze.

## Current Dataset

The repository currently contains:

| Item | Count |
|------|------:|
| Samples | 208 |
| Domains | 11 |
| IKA questions | 624 |
| Primary topology classes | 4 |
| Sub-topology classes | 7 |

Domain distribution:

| Domain | Samples |
|--------|--------:|
| construction | 30 |
| robotics | 28 |
| mining | 27 |
| maritime | 23 |
| aerospace | 20 |
| manufacturing | 20 |
| electronics | 20 |
| chemical | 19 |
| energy_renewable | 9 |
| energy_power | 7 |
| oil_gas | 5 |

Primary topology distribution from `primary_topology`:

| Primary topology | Samples |
|------------------|--------:|
| kinematic | 74 |
| lattice | 62 |
| surface | 45 |
| flexible | 27 |

Sub-topology distribution:

| Sub-topology | Samples |
|--------------|--------:|
| articulated | 42 |
| 3d_spatial | 37 |
| rotational | 32 |
| cable_hose | 27 |
| aerodynamic | 25 |
| 2d_planar | 25 |
| rigid_housing | 20 |

Motion distribution:

| Motion | Samples |
|--------|--------:|
| orbit | 107 |
| pan | 48 |
| crane | 30 |
| dolly | 23 |

## Evaluation Axes

| Axis | Meaning | Main implementation | Scale | Floor |
|------|---------|---------------------|------:|------:|
| IKA | Industrial Knowledge Alignment | yes/no industrial questions, exact match plus superlative pass | 0-100 | 5 |
| TC | Temporal Consistency | LLM or fallback temporal coherence scoring | 0-100 | 5 |
| PP | Physical Plausibility | LLM 1-5 score converted to 0-100 | 0-100 | 5 |
| VF | Visual Fidelity | reference-image structural fidelity, SSIM/histogram plus optional LLM | 0-100 | 5 |
| GI | Geometric Integrity | topology-dispatched CV metrics | 0-100 | 8 |
| IC | Industrial Constraints | hard invariant checkers mixed into GI and included as an axis | 0-100 | 8 |
| VFA | View-point Fidelity Angle | RANSAC affine angle estimate scored against target | 0-100 fidelity; raw angle retained | 0 |

VFA is both an axis and a gate. A static video against an orbit target may
receive `vfa_score = 0`, but other axes retain floors so the report still
contains useful diagnostic signal.

## Pipeline

```text
Video Frames
  Uniformly sampled from model-generated .mp4
  Expected naming: {task_id}.mp4
        |
        +--> CV TRACK: deterministic, no LLM
        |     |
        |     +--> GI module, dispatched by sub_topology
        |     |     articulated   -> kinematic proxy + bilateral symmetry
        |     |     rotational    -> polar / rotational symmetry
        |     |     aerodynamic   -> contour Chamfer distance
        |     |     rigid_housing -> SIFT keypoint proxy
        |     |     2d_planar     -> Fourier spectral integrity
        |     |     3d_spatial    -> SIFT homography / inlier ratio
        |     |     cable_hose    -> optical-flow continuity proxy
        |     |
        |     +--> IC checkers
        |     |     count_invariant
        |     |     kinematic_coupling
        |     |     periodic_structure
        |     |     topology_merge_detector
        |     |
        |     +--> VFA module
        |           RANSAC affine estimate from anchor to final frame
        |           raw vfa angle plus target-fidelity score
        |
        +--> LLM TRACK: enabled when ANTHROPIC_API_KEY is set
              |
              +--> IKA: 3 adversarial yes/no questions per sample
              +--> TC: temporal coherence
              +--> PP: physical plausibility
              +--> VF: visual/reference fidelity
        |
        v
Per-sample scoring
  - Floor enforcement
  - IC normalized to 0-100 and mixed into GI at 30% weight
  - Weighted axis sum
  - RIF = geometric mean of IKA, GI, and VF
        |
        v
Aggregate engine
  - Relax Score: mean per-sample weighted score
  - Strict Pass Rate: fraction of samples passing all present axis thresholds
  - Gated Score: per-sample weighted score multiplied by VFA fidelity gate
        |
        v
Outputs
  - {task_id}.json for each sample
  - per_sample.json
  - aggregate.json
  - report.json
```

Crane motion is represented with a deterministic VFA estimator based on robust
vertical image translation. The estimator maps first-to-last vertical pixel
travel to an approximate camera-rise angle using an assumed 60 degree vertical
field of view, then scores that angle against the target.

## Scoring Outputs

For each model, `eval/run_eval.py` writes outputs under:

```text
{output_dir}/{model}/
  aggregate.json
  report.json
  per_sample.json
  {task_id}.json
```

`aggregate.json` contains leaderboard-level metrics:

| Field | Meaning |
|-------|---------|
| `relax_score` | Mean per-sample weighted score |
| `strict_pass_rate` | Fraction of completed samples where every present axis clears threshold |
| `gated_score` | Mean weighted score after applying the VFA fidelity gate |
| `overall` | Alias for `gated_score`, used for leaderboard ranking |
| `axis_scores` | Mean floored axis scores |
| `vfa_tier` | Raw-angle tier: none, weak, moderate, full |
| `rif` / `rif_gated` | Rotation-sensitive integrity factor |

`report.json` is the diagnostic report. It is designed to answer what the model
failed at, not just how low it scored. It includes:

| Section | What it reports |
|---------|-----------------|
| `summary.weakest_axes` | Lowest mean axes and low-score rates |
| `axis_statistics` | Mean, median, min, max, count, and low-score rate per axis |
| `breakdowns.by_domain` | Mean score and low-score rate by industrial domain |
| `breakdowns.by_primary_topology` | Weak topology families |
| `breakdowns.by_sub_topology` | Weak sub-topology operators |
| `breakdowns.by_motion_type` | Motion classes that fail most often |
| `vfa_diagnostics` | target-angle errors, static-video count, uncalculable count |
| `ic_diagnostics` | IC checker coverage and violation counts |
| `ika_weakness_diagnostics` | IKA accuracy by W2-W7 weakness target |
| `worst_samples` | Lowest-scoring samples with weakest axis and violations |

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run CV-only evaluation:

```bash
python eval/run_eval.py \
  --model my_model \
  --video_dir /path/to/model_outputs \
  --samples_json dataset/annotations/samples.json \
  --output_dir results \
  --no_llm
```

Run with the LLM track enabled:

```bash
set ANTHROPIC_API_KEY=your_key_here
python eval/run_eval.py \
  --model my_model \
  --video_dir /path/to/model_outputs \
  --samples_json dataset/annotations/samples.json \
  --output_dir results
```

Optional IKA answer file:

```bash
python eval/run_eval.py \
  --model my_model \
  --video_dir /path/to/model_outputs \
  --samples_json dataset/annotations/samples.json \
  --output_dir results \
  --model_answers /path/to/answers.json
```

Expected answer JSON format:

```json
{
  "aero_001:q1": "yes",
  "aero_001:q2": "no"
}
```

Validate the dataset:

```bash
python dataset/validate.py
```

Run tests:

```bash
python -m pytest -q
```

## Repository Layout

```text
dataset/
  annotations/
    samples.json
    DATASET.md
    README.md
  images/
  schema.json
  validate.py

eval/
  run_eval.py
  preflight.py
  calibration/
  domain_alignment/
  geometric_integrity/
  industrial_constraints/
  physical_plausibility/
  temporal_coherence/
  visual_fidelity/
  vfa/

scoring/
  aggregate.py
  leaderboard.py
  per_sample.py
  report.py

tests/
  test_pipeline_smoke.py
```

## Current Limitations

- Crane-specific VFA is an image-translation estimate, not a calibrated camera
  reconstruction. It is deterministic and useful for gating, but exact crane
  kinematics still depend on unknown focal length and scene depth.
- TC, PP, and VF have fallback scorers when the LLM track is disabled or an LLM
  call fails. These fallback values are useful for smoke testing but should not
  be treated as final benchmark-quality judgments.
- Some legacy samples use symbolic VFA targets such as `orbit_cw_45deg` or
  `horizontal_pan_lr`. Numeric targets are preferred for strict VFA scoring.
- The benchmark is intentionally strict. High visual quality alone should not
  guarantee a high score if geometry, topology, count invariants, or requested
  camera motion are wrong.

## Citation

```bibtex
@article{forgebench2026,
  title={FORGE-Bench: Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation},
  author={TBD},
  journal={TBD},
  year={2026}
}
```
