# FORGE-Bench: Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation

**The first benchmark measuring Functional Fidelity — not perceptual quality — in image-to-video generation for industrial domains.**

---

## Abstract

State-of-the-art image-to-video (I2V) generation models are evaluated almost exclusively on *perceptual fidelity*: does the output look realistic? For consumer content, this is sufficient — a cat with an extra toe is aesthetically odd but functionally irrelevant. Industrial content operates under a fundamentally different standard: *functional fidelity*, where structural invariants are hard constraints, not aesthetic preferences. A gear with one missing tooth, two merged PCB traces, or a robotic arm with misaligned inverse kinematics are not aesthetic failures — they are physical system failures that no amount of visual realism can mask.

FORGE-Bench is the first evaluation framework explicitly designed to measure functional fidelity in I2V generation. It exposes a class of failures that are systematically invisible to perception-based judges (including state-of-the-art vision-language models): high-frequency periodic structure collapse, topology merges at sub-component boundaries, kinematic chain constraint violations, and camera motion fidelity under large orbit angles. The benchmark spans 10 industrial domains with 200 samples and 600 adversarial questions, evaluated along 5 axes through a hybrid CV + LLM scoring pipeline with topology-type dispatch, enforced floor values, and a VFA quality gate.

---

## Motivation: Why Perceptual Fidelity Is Not Enough

Existing video generation benchmarks — VBench, EvalCrafter, DOVER, and their successors — share a common implicit assumption: *a video is good if it looks good*. This assumption is valid for the consumer media domain these benchmarks were designed for. It breaks completely for industrial applications.

### The Perceptual–Functional Gap

| Scenario | Perceptual Judge | Functional Reality |
|----------|------------------|--------------------|
| Cat video, one extra toe | "Looks fine, minor artifact" | Irrelevant to function |
| Gear animation, one missing tooth | "Looks mostly correct" | Complete mechanical failure |
| PCB fly-through, two traces merged | "Beautiful detail, high fidelity" | Short circuit — board is dead |
| Wind turbine rotation, blade pitch inconsistency | "Smooth, realistic rotation" | Aerodynamic instability |
| Robotic arm orbit, shoulder joint drift | "Natural motion" | IK chain is broken |

In each industrial case, the generated video can score near-perfectly on perceptual metrics (SSIM, LPIPS, aesthetic scores, LLM visual quality ratings) while simultaneously containing a physical failure that would render the depicted system non-functional. We call this the **perceptual–functional gap**, and it is the central problem FORGE-Bench is designed to measure.

### Why LLM-as-a-Judge is Structurally Insufficient

The rise of VLM-as-Judge evaluation (using GPT-4V, Gemini, or similar models to score video quality) has dramatically simplified benchmark construction. For industrial video, it introduces a structural blind spot.

LLMs evaluate videos by holistic visual impression from sampled frames. Industrial functional failures are dominated by *high-frequency*, *microscale*, and *hard-constraint* violations that are imperceptible at the frame level:

- **Periodic structure collapse**: A turbine blade array where 3 of 47 blades have merged at 720p looks identical to a correct rendering to a visual judge. A Fourier spectral integrity check over the blade-row signal detects the collapse immediately.
- **Topology merge**: Two adjacent PCB traces that merge for 4 pixels across 8 frames are invisible to GPT-4V at standard resolution. A topology merge detector with sub-pixel tracking finds it in frame 3.
- **Kinematic coupling violation**: A scissor-lift where the upper platform drifts 8° from horizontal during extension looks "roughly correct" to a visual judge. A bilateral symmetry checker flags it as a hard violation.
- **VFA under large orbit**: An I2V model that generates a visually stunning orbit video but only rotates the camera 12° instead of the prompted 90° scores perfectly on IKA, TC, PP, and VF — because the frames look excellent. The VFA gate (RANSAC affine estimation) catches the motion fidelity failure and collapses the composite score.

FORGE-Bench's GI axis and IC checkers exist precisely because functional failures in industrial video are structurally below the resolution floor of VLM-as-Judge. The following table quantifies this blind spot on our pilot evaluation (Hailuo 2.3, 9 samples):

| Sample | LLM axes mean (IKA/TC/PP/VF) | GI (CV) | Failure caught by |
|--------|------------------------------|---------|-------------------|
| aero_surf_001 | 93.75 | 0.0 | GI only — 120° actual orbit vs 45° prompt, Chamfer collapse |
| robo_kin_001 | 87.5 | 0.0 | GI only — dark background suppresses global optical flow, static misdetection |
| ener_lat_001 | 98.5 | 66.3 | GI partial — SIFT inlier ratio drops as lattice rotates out of overlap |
| mfg_kin_001 | 100.0 | 100.0 | Both agree — scissor lift bilateral symmetry preserved perfectly |

The first two rows represent cases where a pure LLM judge would report near-perfect scores on a functionally failed video. GI is the only signal catching the failure.

---

## Evaluation Dimensions

Each axis is designed to capture a specific facet of functional fidelity. IKA tests whether the model preserves the engineering knowledge encoded in the structure (e.g., blade count, joint topology). TC and PP test whether the generated motion is physically coherent over time. VFA enforces that the camera followed the prompt's kinematic specification — not just that the frames look good. GI is the pure-CV axis that catches sub-perceptual structural failures that LLMs systematically miss.

| Axis | Full Name | Scoring Method | Scale | What It Measures | Floor |
|------|-----------|---------------|-------|------------------|-------|
| **IKA** | Industrial Knowledge Alignment | LLM (exact-match + superlative pass) | 0–100 | Correctness of answers to adversarial industrial questions about structural invariants | 5.0 |
| **TC** | Temporal Consistency | LLM | 0–100 | Frame-to-frame coherence of structural elements, absence of drift, merge, or morphing artifacts | 5.0 |
| **PP** | Physical Plausibility | LLM (1–5 → 0–100) | 0–100 | Whether generated motion obeys physical laws — gravity, rigidity, realistic trajectories | 5.0 |
| **VFA** | View-point Fidelity Angle | CV (RANSAC affine) | 0–180° | Accuracy of camera orbit/crane angle vs. the target specified in the prompt | 0.0 (gate) |
| **GI** | Geometric Integrity | CV (SIFT / kinematic / lattice) | 0–100 | Preservation of geometric structure — keypoint stability, lattice periodicity, kinematic chain integrity | 8.0 |

Floor values: LLM-scored axes (IKA, TC, PP, VF) are floored at 5.0; CV-scored axes (GI, IC) at 8.0; VFA at 0.0 (it is a quality gate, not a quality score).

---

## Dataset Overview

| Domain | Chinese Name | Samples | Dominant Sub-topology | Example Equipment |
|--------|-------------|---------|----------------------|-------------------|
| robotics | 机器人 | 28 | articulated, cable_hose | KUKA arm, NAO biped, PR2, Spot, PackBot EOD, surgical robot |
| manufacturing | 制造业 | 20 | rotational, rigid_housing | CNC lathe, conveyor belt, 3D printer, hydraulic press |
| construction | 建筑工程 | 30 | articulated, 3d_spatial | Tower crane, TBM, concrete pump truck, lattice boom crane |
| mining | 矿业 | 27 | rotational, 3d_spatial | Mining haul truck, ball mill, underground drill jumbo |
| maritime | 船舶海工 | 23 | aerodynamic, 3d_spatial | Cargo ship, offshore crane, jack-up rig, drydock propeller |
| aerospace | 航空航天 | 20 | aerodynamic, 2d_planar | Boeing 747, turbine engine, CCD sensor wafer |
| electronics | 电子制造 | 20 | 2d_planar, articulated | PCB, pick-and-place machine, wire bonder, CCD pixel array |
| chemical | 化工 | 19 | 3d_spatial, rigid_housing | Distillation column, heat exchanger, reactor, autoclave |
| energy_renewable | 可再生能源 | 9 | rotational | Wind turbine, solar tracker, offshore wind farm |
| energy_power | 传统能源 | 7 | rigid_housing, rotational | Gas turbine, nuclear plant, hydroelectric penstock |
| oil_gas | 油气 | 5 | 3d_spatial, aerodynamic | Offshore oil platform, pipeline manifold, FPSO vessel |

**Total: 208 samples, 11 domains, 4 topology types, 7 sub-categories, 624 adversarial questions.**

---

## Scoring Pipeline

```
┌──────────────────┐
│   Video Frames   │  (uniformly sampled from model-generated .mp4, 1920×1080)
└────────┬─────────┘
         │
         ├─────────────────────────────────────────────────────────────────────┐
         │  CV TRACK  (deterministic, no LLM)                                  │
         │                                                                     │
         │  ┌─── GI Module (topology-type dispatch) ──────────────────────┐   │
         │  │    ├── articulated   → Kinematic chain MAD + bilateral sym.  │   │
         │  │    ├── rotational    → Polar symmetry / RCI                  │   │
         │  │    ├── aerodynamic   → Chamfer distance on contours          │   │
         │  │    ├── rigid_housing → SIFT keypoint proxy (first↔last)      │   │
         │  │    ├── 2d_planar     → Fourier Spectral Integrity (FSI)      │   │
         │  │    ├── 3d_spatial    → SIFT homography inlier ratio          │   │
         │  │    └── cable_hose    → Optical flow continuity               │   │
         │  └─────────────────────────────┬────────────────────────────────┘   │
         │                                │ gi_score                           │
         │  ┌─── IC Checkers (augment GI with ic_score) ──────────────────┐   │
         │  │    ├── count_invariant      (element count stability)        │   │
         │  │    ├── kinematic_coupling   (rigid-body coupling check)      │   │
         │  │    ├── periodic_structure   (lattice / array preservation)   │   │
         │  │    └── topology_merge_detector (component merge detection)   │   │
         │  └─────────────────────────────┬────────────────────────────────┘   │
         │                                │ ic_score (augments gi_score)       │
         │                                │                                    │
         │  ┌─── VFA Module (RANSAC affine, anchor→final frame) ──────────┐   │
         │  │    • Estimates actual camera rotation angle                  │   │
         │  │    • vfa ≈ 0  →  static video gate (penalizes orbit prompts) │   │
         │  └─────────────────────────────┬────────────────────────────────┘   │
         │                                │ vfa_score  +  gate_flag            │
         │                                                                     │
         ├─────────────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────────────────────┐
         │  LLM TRACK  (VLM judge — Claude Sonnet with CoT + visual prompting) │
         │                                                                     │
         │  ┌─── IKA  (Industrial Knowledge Alignment) ────────────────────┐  │
         │  │    3 adversarial yes/no Qs per sample — structural invariants  │  │
         │  │    CoT JSON output + SIFT-annotated frames → exact-match +    │  │
         │  │    superlative-pass scoring                                   │  │
         │  └─────────────────────────────┬────────────────────────────────┘  │
         │                                │ ika_score                         │
         │  ┌─── TC  (Temporal Consistency) ────────────────────────────────┐  │
         │  │    Frame-to-frame coherence, no drift / merge / morphing      │  │
         │  └─────────────────────────────┬────────────────────────────────┘  │
         │                                │ tc_score                          │
         │  ┌─── PP  (Physical Plausibility) ────────────────────────────────┐ │
         │  │    Gravity, rigidity, realistic motion trajectories  1–5 scale │ │
         │  └─────────────────────────────┬────────────────────────────────┘  │
         │                                │ pp_score                          │
         │  ┌─── VF  (Visual Fidelity) ──────────────────────────────────────┐ │
         │  │    Structural preservation vs. reference image (SSIM + LLM)   │ │
         │  └─────────────────────────────┬────────────────────────────────┘  │
         │                                │ vf_score                          │
         └─────────────────────────────────────────────────────────────────────┘
                    │           │           │           │           │
                 gi+ic        vfa         ika          tc+pp       vf
                    │           │           │           │           │
                    └───────────┴─────────────────┬─────┴───────────┘
                                                  ▼
                                    ┌─────────────────────────┐
                                    │   Per-Sample Scoring    │
                                    │   • Floor enforcement   │
                                    │     (IKA/TC/PP/VF ≥ 5) │
                                    │     (GI/IC ≥ 8)        │
                                    │   • Weighted sum        │
                                    │   • RIF = ∛(IKA·GI·VF) │
                                    └────────────┬────────────┘
                                                 │
                                    ┌────────────▼────────────┐
                                    │   Aggregate Engine      │
                                    │   • Relax Score         │
                                    │     (mean weighted axes)│
                                    │   • Strict Pass Rate    │
                                    │     (all axes pass)     │
                                    │   • Gated Score         │
                                    │     (VFA gate applied)  │
                                    └────────────┬────────────┘
                                                 │
                                    ┌────────────▼────────────┐
                                    │  report.json            │
                                    │  aggregate.json         │
                                    │  per_sample.json        │
                                    └─────────────────────────┘
```

**Flow:** Video frames (1920×1080) are routed through two parallel tracks. The **CV track** dispatches to the correct GI sub-evaluator based on `sub_topology` (7 types), then augments the result with IC checker scores. The VFA module independently estimates actual camera motion via RANSAC affine estimation and acts as both a numeric score and a quality gate. The **LLM track** runs IKA (with CoT chain-of-thought reasoning and SIFT-annotated frames), TC, PP, and VF through Claude Sonnet. All five axis scores (gi, vfa, ika, tc, pp, vf) feed into `score_sample()`, which enforces per-axis floors, computes **RIF = ∛(IKA × GI × VF)** as a rotation-sensitive integrity factor, and produces the per-sample composite score. The aggregate engine then computes Relax Score, Strict Pass Rate, and VFA-Gated Score across all samples.

---

## Industrial Constraint Checkers (IC)

Four specialized checkers enforce domain-specific hard invariants beyond generic CV metrics:

| Checker | What It Tests | Domains |
|---------|---------------|---------|
| **count_invariant** | Element count stability across frames (e.g., engine blades, via holes, track links) | aerospace, chemical, electronics, mining, maritime, energy |
| **kinematic_coupling** | Rigid-body coupling consistency in mechanisms (conveyor, scissor lift, robotic arm) | construction, maritime, chemical, mining, oil_gas, manufacturing, robotics |
| **periodic_structure** | Preservation of periodic patterns (lattice jackets, PCB traces, turbine arrays) | aerospace, chemical, construction, mining, energy, oil_gas, electronics, manufacturing |
| **topology_merge_detector** | Detection of unintended topology merges between distinct structural components | All domains with surface or kinematic topology |

Checkers are dispatched via a `(domain, topology_type)` lookup table. Each checker returns a score (0.0–1.0) and a list of violations. The mean of all applicable checker scores becomes the sample's `ic_score`.

---

## Difficulty System

Each sample has a `difficulty_profile` assigning one of four levels per evaluation axis:

| Level | Description |
|-------|-------------|
| **easy** | Simple geometry, small camera motion, minimal structural complexity |
| **medium** | Moderate motion, multiple structural elements, standard industrial equipment |
| **hard** | Large orbit angles, complex mechanisms, fine periodic structures, known model failure modes |
| **adversarial** | Extreme motion + worst-case geometry specifically targeting known I2V model weaknesses |

### Weakness Targeting (W2–W7)

Questions are tagged with weakness targets that map to known systematic failures in current I2V generation models:

| Tag | Weakness Target | Count |
|-----|-----------------|-------|
| W2 | Aspect ratio / cross-section deformation during orbit | 52 |
| W3 | Sub-component count drift (elements appearing/disappearing) | 180 |
| W4 | Periodic structure blurring (gear teeth, PCB traces, track links) | 75 |
| W5 | Bilateral symmetry violation after extended motion | 93 |
| W6 | Fine surface detail loss / panel gap artifacts | 130 |
| W7 | Sub-component geometry drift during orbit | 70 |

Each sample carries exactly 3 IKA questions, distributed across weakness targets to maximize failure-mode coverage.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
# requirements: opencv-python-headless numpy tqdm anthropic pillow scipy

# Run evaluation against a model output directory
python eval/run_eval.py \
    --model my_model \
    --video_dir /path/to/model_outputs/ \
    --samples_json dataset/annotations/samples.json \
    --output_dir results/

# Optional: provide model answers for IKA evaluation
python eval/run_eval.py \
    --model my_model \
    --video_dir /path/to/model_outputs/ \
    --samples_json dataset/annotations/samples.json \
    --output_dir results/ \
    --model_answers /path/to/answers.json
```

Expected video naming: `{task_id}.mp4` (e.g., `aero_001.mp4`) placed in `--video_dir`.

Model answers JSON format: `{"task_id:question_id": "answer_text", ...}` (e.g., `{"aero_001:q1": "yes"}`).

---

## Dataset Structure

```
FORGE-Bench/
├── dataset/
│   ├── annotations/
│   │   ├── samples.json          # 200 annotated evaluation samples
│   │   ├── DATASET.md            # Full schema documentation
│   │   └── README.md             # Schema field reference
│   └── images/                   # Reference images (one per sample, 1280×720 JPEG)
│       ├── aerospace/            # Boeing 747, turbine engine, satellite, ...
│       ├── chemical/             # Distillation column, heat exchanger, reactor, ...
│       ├── construction/         # Tower crane, TBM, concrete pump, ...
│       ├── electronics/          # PCB board, pick-and-place machine, wire bonder, ...
│       ├── energy_power/         # Gas turbine, steam boiler, nuclear plant, ...
│       ├── energy_renewable/     # Wind turbine, solar tracker, offshore wind farm, ...
│       ├── manufacturing/        # Robot arm, CNC lathe, hydraulic press, ...
│       ├── maritime/             # Cargo ship, offshore crane, submarine, ...
│       ├── mining/               # Mining truck, ball mill, underground drill, ...
│       └── oil_gas/              # Offshore platform, pipeline manifold, FPSO, ...
├── eval/
│   ├── run_eval.py               # Main evaluation entry point
│   ├── preflight.py              # Frame count validation
│   ├── calibration/
│   │   ├── floor_enforcer.py     # Score floor enforcement (5.0 LLM / 8.0 CV)
│   │   └── difficulty_report.py  # Per-sample difficulty analysis
│   ├── domain_alignment/
│   │   └── eval.py               # IKA evaluation (exact match + superlative pass)
│   ├── geometric_integrity/
│   │   ├── __init__.py           # GI routing + IC augmentation
│   │   ├── kinematic.py          # Static camera / kinematic chain detection
│   │   ├── lattice.py            # SIFT keypoint lattice evaluation
│   │   ├── lattice_fourier.py    # Fourier-based periodicity analysis
│   │   ├── surface.py            # Surface topology evaluation
│   │   ├── symmetry_mech.py      # Bilateral symmetry mechanism evaluation
│   │   ├── rotary.py             # Rotary element evaluation
│   │   └── track_chain.py        # Track chain / tread periodicity evaluation
│   ├── industrial_constraints/
│   │   ├── __init__.py           # IC dispatch table + evaluate_industrial_constraints()
│   │   ├── count_invariant.py    # Element count stability checker
│   │   ├── kinematic_coupling.py # Rigid-body coupling checker
│   │   ├── periodic_structure.py # Periodic pattern preservation checker
│   │   └── topology_merge_detector.py # Topology merge detection
│   ├── physical_plausibility/
│   │   └── eval.py               # PP evaluation via LLM (1–5 scale)
│   └── vfa/
│       └── eval.py               # VFA via anchor-to-final RANSAC affine
├── scoring/
│   ├── per_sample.py             # Per-sample weighted scoring + RIF
│   ├── aggregate.py              # Cross-sample aggregation + VFA tiering
│   └── report.py                 # JSON report generation with float sanitization
├── scripts/                      # Operational and data management utilities
│   ├── batch_download_candidates.py  # Batch image download from Wikimedia Commons
│   └── check_status.py           # Remote agent status monitoring
└── tests/                        # End-to-end smoke tests
```

---

## Benchmark Statistics

### Per-Domain Sample Counts

| Domain | Samples | kinematic | surface | lattice |
|--------|---------|-----------|---------|---------|
| manufacturing | 40 | 20 | 16 | 4 |
| construction | 30 | 19 | 6 | 5 |
| mining | 27 | 15 | 8 | 4 |
| maritime | 23 | 7 | 12 | 4 |
| aerospace | 20 | 11 | 7 | 2 |
| electronics | 20 | 8 | 7 | 5 |
| chemical | 20 | 5 | 6 | 9 |
| energy_renewable | 9 | 4 | 3 | 2 |
| energy_power | 6 | 4 | 2 | 0 |
| oil_gas | 5 | 2 | 3 | 0 |

### Topology Type Distribution

FORGE-Bench uses a two-level topology taxonomy. The primary type (`primary_topology`) determines the GI evaluation pipeline; the sub-type (`sub_topology`) provides finer-grained characterization for analysis and rebalancing.

| Primary | Sub-category | Count | % | Primary CV Operator | Key Failure Mode |
|---------|-------------|-------|---|--------------------|--------------------|
| **kinematic** | articulated | 36 | 18.0% | Kinematic chain MAD | Joint dislocation / limb drift |
| **kinematic** | rotational | 32 | 16.0% | Polar symmetry (RCI) | Rotational axis wander |
| **surface** | aerodynamic | 25 | 12.5% | Chamfer distance | Fuselage / hull curvature distortion |
| **surface** | rigid_housing | 20 | 10.0% | Max-contour AR | Aspect ratio / panel-gap deformation |
| **lattice** | 2d_planar | 25 | 12.5% | Fourier spectral integrity (FSI) | Trace merge / texture collapse |
| **lattice** | 3d_spatial | 37 | 18.5% | SIFT homography inlier ratio | Perspective-induced lattice distortion |
| **flexible** | cable_hose | 25 | 12.5% | Topology continuity + non-intersection | Cable snap / hose penetration artifact |
| | **Total** | **200** | **100%** | | |

The `flexible` topology class is new to FORGE-Bench and has no equivalent in prior I2V benchmarks. It targets a systematic failure mode of diffusion-based generation: flexible structures (robot wire harnesses, crane stay cables, hydraulic hoses) exhibit non-physical intersections, discontinuities, or disappearance during motion generation that rigid-body metrics cannot detect.

### Difficulty Distribution (per axis)

| Axis | easy | medium | hard | adversarial |
|------|------|--------|------|-------------|
| IKA | 6 | 76 | 118 | 0 |
| TC | 0 | 90 | 110 | 0 |
| PP | 7 | 122 | 71 | 0 |
| VF | 17 | 114 | 69 | 0 |
| GI | 1 | 55 | 144 | 0 |
| VFA | 21 | 15 | 22 | 142 |

### Motion Type Distribution

| Motion Type | Count | % | Description |
|-------------|-------|---|-------------|
| orbit | 103 | 51.5% | Camera circles subject at constant radius (primary VFA test) |
| pan | 46 | 23.0% | Lateral camera translation across structure |
| crane | 29 | 14.5% | Vertical camera rise / descend |
| dolly | 22 | 11.0% | Camera approach / recede along optical axis |

Orbit samples carry quantitative VFA targets (15°–120°) for the SE(3) equivariance test. Pan and dolly samples target the VAE Nyquist failure mode under close-range lattice structures.

### Questions Per Sample

Every sample contains exactly 3 adversarial IKA questions (600 total), each tagged with a weakness target (W2–W7). Questions are generated per-sample against the specific structural invariants of the depicted equipment — not generic templates.

### Sensitivity Variants

Sensitivity variant groups (SA01–SA03, SB01–SB03, SC01–SC03) provide monotonically increasing motion magnitude across 3 difficulty levels within the same subject, enabling ablation of the VFA threshold effect.

---

## Root Cause Taxonomy: Why SOTA I2V Models Fail on Industrial Content

FORGE-Bench is designed to expose a specific set of failure modes that are **structurally impossible to detect with perceptual metrics**. The following taxonomy classifies these failures by their technical root cause — the precise point in the generation pipeline where a statistical prior conflicts with a physical invariant. Each pathology maps to one or more FORGE-Bench evaluation axes and adversarial weakness targets (W2–W7).

### I. Representation Layer Deficits

| # | Pathology | Root Mechanism | FORGE Topology | Primary Axis | W-Tag | Key FORGE Operator |
|---|-----------|---------------|----------------|-------------|-------|-------------------|
| 1 | **VAE Nyquist Failure** — Spatial downsampling (8×8 or higher) in the latent space aliases high-frequency industrial lattice structures into low-frequency noise. Safe for natural textures; fatal for PCB differential traces, heat-exchanger tube banks, and turbine blade rows. | High-frequency signal aliasing in VAE compression | lattice / 2d_planar | GI | W4, W6 | Fourier Spectral Integrity (FSI) |
| 2 | **Non-homeomorphic Latent Mapping** — The latent space is not homeomorphic to ℝ³. A rigid-body orbit in 3D Euclidean space corresponds to a nonlinear trajectory through latent channels, causing smooth surfaces to exhibit wave-like deformation artifacts as the camera rotates. | Latent-to-physical space topology mismatch | surface / aerodynamic | GI, TC | W2, W7 | SIFT homography inlier ratio, Chamfer distance |

### II. Architecture Inductive Bias Deficits

| # | Pathology | Root Mechanism | FORGE Topology | Primary Axis | W-Tag | Key FORGE Operator |
|---|-----------|---------------|----------------|-------------|-------|-------------------|
| 3 | **Graph-Structure Blindness** — Self-attention computes dense O(N²) pairwise similarities over flattened tokens. Industrial kinematic chains (robot arms, scissor lifts, excavator linkages) are sparse tree/graph structures with hard Jacobian constraints. DiT has no concept of joint coupling — it cannot enforce that elbow position is a deterministic function of shoulder angle. | No inductive bias for sparse kinematic graph topology | kinematic / articulated | IKA, GI | W5 | Bilateral symmetry (MBS), kinematic chain MAD, adjacency-matrix variance |
| 4 | **SE(3) Equivariance Failure** — Large-angle orbit shots require the model to apply an SE(3) group transformation to the scene. Decoupled 3D RoPE positional encodings approximate, but do not guarantee, rotational equivariance. The model interpolates from its 2D viewpoint distribution rather than computing the correct 3D perspective transform, producing aspect-ratio distortions and sub-component drift at orbit angles >45°. | Lack of SE(3) equivariance in positional encoding | surface / aerodynamic, kinematic / articulated | VFA, GI | W2, W7 | VFA (RANSAC affine angle estimation) |

### III. Optimization vs. Physical Dynamics Conflicts

| # | Pathology | Root Mechanism | FORGE Topology | Primary Axis | W-Tag | Key FORGE Operator |
|---|-----------|---------------|----------------|-------------|-------|-------------------|
| 5 | **Score Matching vs. Hamiltonian Systems** — Diffusion/flow-matching loss minimizes pixel-space MSE or vector-field matching error — a purely statistical objective. Industrial dynamics obey Euler-Lagrange equations: energy conservation, momentum conservation, and topological invariants (elements cannot spontaneously appear or disappear). Generating one extra turbine blade or chain link costs nearly zero in MSE; it costs infinity in physical consistency. | Statistical loss function incompatible with conservation laws | kinematic / rotational, lattice / 3d_spatial | IKA, GI | W3 | count_invariant checker, periodic_structure checker, track-chain periodicity (TCP) |
| 6 | **Temporal Context Disconnection & Phase Amnesia** — Long video generation relies on sliding-window or autoregressive temporal attention. Once the window slides past the anchor frame, the model loses its absolute phase reference and extrapolates using only local Markov state. Bilateral symmetry and periodic motion phase drift gradually rather than catastrophically — undetectable per-frame, measurable over 8-frame windows. | Finite temporal receptive field causes phase reference loss | kinematic / articulated | TC, GI | W5 | Bilateral symmetry (MBS), temporal coherence LLM scoring |

### IV. Modality Alignment Deficits

| # | Pathology | Root Mechanism | FORGE Topology | Primary Axis | W-Tag | Key FORGE Operator |
|---|-----------|---------------|----------------|-------------|-------|-------------------|
| 7 | **Semantic Collapse of Continuous Parameters** — T5/CLIP tokenization maps continuous geometric parameters ("orbit clockwise 60 degrees at constant radius") to discrete high-dimensional semantic tokens. The text latent space cannot faithfully represent SE(3) numerical integrals — quantitative motion specifications collapse into qualitative semantic intentions. The model "understands orbit" but cannot control the angle. | Continuous kinematic parameters lost in discrete tokenization | all topologies (camera motion) | VFA | — | VFA score (actual vs. target angle delta) |

### Pathology–Benchmark Coverage Matrix

| Pathology | FORGE Detects? | Perceptual Metric Detects? | Why Perception Fails |
|-----------|---------------|--------------------------|----------------------|
| VAE lattice aliasing (P1) | **Yes** — FSI drops when blade/trace frequencies merge | No | SSIM, LPIPS average over spatial regions; merged traces look "smooth" |
| Latent surface deformation (P2) | **Yes** — GI Chamfer distance rises under large orbit | No | Perceptual similarity remains high if texture is preserved |
| Kinematic chain violation (P3) | **Yes** — IKA Q&A + kinematic chain MAD | Partial | LLM-as-judge misses subtle joint drift; hard-constraint test does not |
| SE(3) orbit distortion (P4) | **Yes** — VFA gate collapses composite score | No | A visually beautiful orbit video with wrong angle scores perfectly on aesthetics |
| Count drift (P5) | **Yes** — count_invariant checker | No | An extra blade is imperceptible at 720p to both humans and LLMs |
| Phase amnesia (P6) | **Yes** — TC + bilateral symmetry | Partial | LLM-as-judge may notice, but cannot quantify drift magnitude |
| Continuous parameter collapse (P7) | **Yes** — VFA numerical gate | No | Models that "look like orbiting" but rotate 8° instead of 60° pass all perceptual tests |

> **Design principle**: every axis and IC checker in FORGE-Bench was designed to target at least one of these pathologies. The GI axis + IC checkers form the CV layer that catches P1–P3 and P5–P6. The VFA quality gate addresses P4 and P7. IKA adversarial questions probe P3 and P5 with domain-specific structural knowledge that LLMs cannot hallucinate past.

---

## Citation

```bibtex
@article{forgebench2026,
  title={FORGE-Bench: Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation},
  author={TBD},
  journal={TBD},
  year={2026}
}
```
