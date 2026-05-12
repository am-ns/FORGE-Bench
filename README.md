# FORGE-Bench: Factory-Oriented Reasoning and Generation Evaluation for Industrial Video Generation

A 200-sample, 10-domain benchmark for evaluating image-to-video (I2V) models on industrial structural fidelity through adversarial knowledge-grounded questions, CV + LLM hybrid scoring, and topology-preserving constraint checkers.

---

## Abstract

FORGE-Bench is a comprehensive evaluation framework for assessing whether image-to-video generation models can produce industrially faithful video sequences. Unlike generic video quality benchmarks, FORGE-Bench targets the unique challenges of industrial domains — rigid-body kinematics, periodic lattice structures, surface topology preservation, and domain-specific physical constraints. The benchmark spans 10 industrial domains (aerospace, maritime, mining, chemical, construction, electronics, manufacturing, energy/power, energy/renewable, and oil & gas) with 200 samples totaling 600 adversarial questions. Each sample is evaluated along 5 axes: Industrial Knowledge Alignment (IKA), Temporal Consistency (TC), Physical Plausibility (PP), View-point Fidelity Angle (VFA), and Geometric Integrity (GI). Scoring combines deterministic CV-based metrics (optical flow, SIFT keypoint matching, topology merge detection) with calibrated LLM judgment, producing a per-sample composite score with enforced floor values to prevent degenerate zero-scores.

---

## Evaluation Dimensions

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

| Domain | Chinese Name | Primary Topology | Samples | Example Equipment |
|--------|-------------|------------------|---------|-------------------|
| manufacturing | 制造业 | kinematic | 40 | Industrial robot arm, CNC lathe, hydraulic press |
| construction | 建筑工程 | kinematic | 30 | Tower crane, concrete pump truck, tunnel boring machine |
| mining | 矿业 | kinematic | 27 | Mining haul truck, ball mill, underground drill jumbo |
| maritime | 船舶海工 | surface | 23 | Cargo ship, offshore crane, submarine hull |
| aerospace | 航空航天 | kinematic | 20 | Boeing 747, turbine engine, satellite solar array |
| electronics | 电子制造 | kinematic | 20 | PCB circuit board, pick-and-place machine, wire bonder |
| chemical | 化工 | lattice | 20 | Distillation column, heat exchanger, reactor vessel |
| energy_renewable | 可再生能源 | kinematic | 9 | Wind turbine, solar tracker, wave energy converter |
| energy_power | 传统能源 | kinematic | 6 | Gas turbine, steam boiler, cooling tower |
| oil_gas | 油气 | surface | 5 | Offshore oil platform, pipeline manifold, FPSO vessel |

**Total: 200 samples, 3 topology types, 600 adversarial questions.**

---

## Scoring Pipeline

```
┌─────────────┐
│ Video Frames │  (extracted from model output .mp4)
└──────┬──────┘
       │
       ├──► GI Module ──────────────────────────────────────┐
       │    ├── kinematic (static camera detection)          │
       │    ├── lattice (SIFT keypoint matching)             │
       │    └── surface (SIFT proxy for point-cloud GI)      │
       │                                                     │
       ├──► IC Checkers (augment GI result) ─────────────────┤
       │    ├── count_invariant                              │
       │    ├── kinematic_coupling                           │
       │    ├── periodic_structure                           │
       │    └── topology_merge_detector                      │
       │                                                     ▼
       │                                          ┌──────────────────┐
       ├──► VFA Module (RANSAC affine rotation) ──►│  Per-Sample      │
       │                                           │  Scoring Engine  │
       └──► IKA Module (LLM answer match) ────────►│  (score_sample)  │
                                                    └────────┬─────────┘
                                                             │
                                                    ┌────────▼─────────┐
                                                    │ Aggregate Engine │
                                                    │ (floor + RIF +   │
                                                    │  VFA tiering)    │
                                                    └────────┬─────────┘
                                                             │
                                                    ┌────────▼─────────┐
                                                    │ report.json      │
                                                    │ aggregate.json   │
                                                    └──────────────────┘
```

**Flow:** Video frames are extracted and routed through three parallel evaluators. GI uses topology-type dispatch (kinematic / lattice / surface). IC checkers are domain-specific invariant tests that augment the GI result with an `ic_score`. VFA computes camera motion fidelity via anchor-to-final RANSAC affine estimation. IKA compares model answers to ground-truth via exact-match with superlative-pass handling. All axis scores feed into `score_sample()` which applies floor enforcement, computes RIF (Rotational Integrity Factor from IKA/GI/VFA), and produces the final weighted score.

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
pip install opencv-python numpy tqdm

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
│   └── images/
│       ├── aerospace/            # Boeing 747, turbine engine, ...
│       ├── chemical/             # Distillation column, heat exchanger, ...
│       ├── construction/         # Tower crane, concrete pump, ...
│       ├── electronics/          # PCB board, pick-and-place machine, ...
│       ├── energy/               # (alias for energy_power/energy_renewable)
│       ├── energy_power/         # Gas turbine, steam boiler, ...
│       ├── energy_renewable/     # Wind turbine, solar tracker, ...
│       ├── manufacturing/        # Robot arm, CNC lathe, ...
│       ├── maritime/             # Cargo ship, offshore crane, ...
│       ├── microelectronics/     # (alias for electronics)
│       ├── mining/               # Mining truck, ball mill, ...
│       ├── oil_gas/              # Offshore platform, pipeline, ...
│       ├── robotics/             # (alias for manufacturing)
│       ├── vehicle/              # (alias for construction/mining vehicles)
│       └── vehicles/             # (alias)
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
│   │   ├── symmetry_mech.py      # Symmetry mechanism evaluation
│   │   ├── rotary.py             # Rotary element evaluation
│   │   └── track_chain.py        # Track chain / tread evaluation
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
├── download_images.py            # Image acquisition script
└── download_missing_images.py    # Fill missing images from dataset
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

| Topology | Count | Percentage |
|----------|-------|------------|
| kinematic | 95 | 47.5% |
| surface | 70 | 35.0% |
| lattice | 35 | 17.5% |

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

All 200 samples use camera orbit motion. VFA targets range from 0° to 180° (mean: 136.4°).

### Questions Per Sample

Every sample contains exactly 3 adversarial IKA questions (600 total), each tagged with a weakness target (W2–W7).

### Sensitivity Variants

Every sample includes 2 sensitivity variants (easy + hard), yielding 400 additional prompt configurations for ablation studies.

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
