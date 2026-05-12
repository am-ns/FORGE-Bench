# DATASET.md — FORGE-Bench samples.json Schema Reference

Full field-by-field documentation for `samples.json`, the primary annotation file for the FORGE-Bench benchmark.

---

## Top-Level Structure

`samples.json` is a JSON object with a single key:

```json
{
  "samples": [ ... ]
}
```

`"samples"` is an array of 200 sample objects. Each sample represents one evaluation task: an input image, a camera-motion prompt, ground-truth questions, and metadata for difficulty and constraint checking.

---

## Sample Object Fields

### `task_id` (string, required)

Unique sample identifier. Pattern: `^[a-z]{2,8}(_[a-z]+)?_[0-9]{3}$` (e.g., `aero_001`, `mining_truck_003`).

- The prefix encodes the domain (e.g., `aero_` for aerospace, `chem_` for chemical).
- The suffix is a zero-padded sequence number.
- Used as the key for video file naming (`{task_id}.mp4`) and result file naming (`{task_id}.json`).

---

### `domain` (string, required)

Industrial domain classification. One of:

| Value | Chinese Name | Sample Count |
|-------|-------------|--------------|
| `aerospace` | 航空航天 | 20 |
| `chemical` | 化工 | 20 |
| `construction` | 建筑工程 | 30 |
| `electronics` | 电子制造 | 20 |
| `energy_power` | 传统能源 | 6 |
| `energy_renewable` | 可再生能源 | 9 |
| `manufacturing` | 制造业 | 40 |
| `maritime` | 船舶海工 | 23 |
| `mining` | 矿业 | 27 |
| `oil_gas` | 油气 | 5 |

The `domain` field drives the industrial constraint checker dispatch table. Each domain maps to a set of applicable IC checkers.

---

### `image_path` (string, required)

Relative path to the reference image from the repository root. Always prefixed with `dataset/images/`.

Example: `"dataset/images/aerospace/boeing_747_400.jpg"`

The image serves as the first frame anchor for I2V generation and as the reference for IKA question evaluation.

---

### `prompt` (string, required)

Camera-motion instruction for the I2V model. Describes:
1. **Subject**: What the equipment/object is and its key structural features.
2. **Camera motion**: Orbit angle (degrees), direction (clockwise/counter-clockwise), arc type (smooth/linear), and optional vertical rise.
3. **Structural preservation constraints**: Explicit instructions about what must NOT change (e.g., "Do not add or remove engines").

Example:
```
"Boeing 747-400 wide-body airliner with four underwing turbofan engines
and distinctive upper-deck hump. Camera orbits 41° counter-clockwise
around the subject at constant radius, medium smooth arc. Do not add
or remove engines, wings, or control surfaces."
```

---

### `vfa_target` (float, required)

Target View-point Fidelity Angle in degrees. Range: `0.0` – `180.0`.

The VFA module measures the actual camera rotation angle in the generated video via RANSAC affine estimation, then compares it to this target. A `vfa_target` of `0.0` means a static camera; `180.0` means a full half-orbit.

Across the 200 samples: min = 0.0°, max = 180.0°, mean = 136.4°.

---

### `topology_type` (string, required)

Geometric topology classification for GI routing. One of:

| Value | Count | Description | GI Method |
|-------|-------|-------------|-----------|
| `kinematic` | 95 | Articulated mechanisms with moving joints | Static camera detection + kinematic chain analysis |
| `surface` | 70 | Continuous surfaces (fuselages, hulls, platforms) | SIFT keypoint matching (first-to-last frame) |
| `lattice` | 35 | Periodic/repeating structures (PCB traces, lattice jackets) | SIFT + Fourier periodicity analysis |

The `topology_type` determines which GI sub-evaluator runs and which IC checkers are dispatched.

---

### `questions` (array, required)

Array of exactly 3 adversarial IKA (Industrial Knowledge Alignment) questions. Each question object has:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Question identifier within this sample (e.g., `"q1"`, `"q2"`, `"q3"`) |
| `text` | string | The adversarial question text, phrased to probe specific structural invariants |
| `answer` | string | Ground-truth answer: `"yes"` or `"no"` |
| `weakness_target` | string | Weakness tag (W2–W7) indicating which known I2V model failure mode this question targets |

**Weakness targets:**

| Tag | Failure Mode |
|-----|-------------|
| W2 | Aspect ratio / cross-section deformation during orbit |
| W3 | Sub-component count drift (elements appearing/disappearing) |
| W4 | Periodic structure blurring (gear teeth, PCB traces, track links) |
| W5 | Bilateral symmetry violation after extended motion |
| W6 | Fine surface detail loss / panel gap artifacts |
| W7 | Sub-component geometry drift during orbit |

Questions with `answer: "no"` and failure-predictive keywords (e.g., "merging", "disappearing", "distortion") are eligible for the **superlative pass** mechanism: if a model answers "yes" but provides explicit structural-correctness reasoning, the answer is scored as correct.

---

### `constraint_annotations` (object, required)

Engineering constraint metadata. Fields:

| Field | Type | Description |
|-------|------|-------------|
| `topology_type` | string | Duplicate of the top-level `topology_type` (used by IC dispatch) |
| `hard_constraints` | array of strings | Engineering invariants that must hold (e.g., `"engine_count_invariant_across_frames"`) |
| `failure_modes` | array of strings | Expected failure modes if constraints are violated (e.g., `"engine_nacelle_count_drift"`) |
| `element_count` | integer | Number of discrete structural elements relevant to count_invariant checks (e.g., 4 engines, 8 track links) |

`hard_constraints` are injected into the PP (Physical Plausibility) LLM prompt as sample-specific failure-mode checklists, so the LLM evaluates concrete observable constraints rather than generic physics principles.

---

### `difficulty_profile` (object, required)

Per-axis difficulty level assignment. Keys are evaluation axis names; values are difficulty strings.

| Axis | Possible Values | Description |
|------|----------------|-------------|
| `ika` | `easy`, `medium`, `hard` | Difficulty of IKA questions |
| `tc` | `medium`, `hard` | Temporal consistency challenge |
| `pp` | `easy`, `medium`, `hard` | Physical plausibility challenge |
| `vf` | `easy`, `medium`, `hard` | View-point fidelity challenge |
| `gi` | `easy`, `medium`, `hard` | Geometric integrity challenge |
| `vfa` | `easy`, `medium`, `hard`, `adversarial` | VFA target difficulty (adversarial = extreme orbit angles) |

Note: `adversarial` appears only in the `vfa` axis (142 of 200 samples). Other axes use `easy`/`medium`/`hard`.

---

### `sensitivity_variants` (array, required)

Exactly 2 sensitivity variants per sample for ablation studies. Each variant object:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Variant identifier (e.g., `"aero_001_easy"`, `"aero_001_hard"`) |
| `difficulty` | string | `"easy"` or `"hard"` |
| `prompt_delta` | string | Human-readable description of how the prompt changes (e.g., `"Reduce orbit to 26.7° with slower, smoother arc"`) |
| `vfa_target_delta` | float | Numeric change to `vfa_target` (negative = smaller orbit, positive = larger orbit) |

Variants allow measuring model sensitivity to motion complexity without changing the subject matter.

---

### `failure_target` (string, optional, 48 samples)

Natural-language description of the expected failure mode when constraints are violated. Used for qualitative analysis and error taxonomy.

Example: `"I2V model fails to maintain the Boeing 747 nose-up pitch attitude (typical 10-15 degrees during initial climb), causing fuselage longitudinal axis to oscillate or drift to level flight mid-generation"`

---

### `motion_type` (string, optional, 130 samples)

Camera motion classification. Values observed: `"pan"`, `"orbit"`, `"crane"`, `"zoom"`.

When present, used by the VFA module to select the appropriate estimation method. Crane motion currently requires a VLM fallback (not yet implemented).

---

### `reverse` (boolean, optional, 48 samples)

When `true`, indicates the sample tests reversed constraint direction (e.g., expansion instead of contraction, clockwise instead of counter-clockwise). Used to probe directional bias in I2V models.

---

### `extra_frame` (integer, optional, 48 samples)

Additional frame index for multi-frame evaluation. When present, indicates that the sample requires evaluation beyond the standard first-to-last frame comparison.

---

### `ika_questions` (array, optional, 130 samples)

Additional IKA question objects beyond the standard 3 in `questions`. Same schema as `questions` entries. When present, extends the IKA evaluation to more than 3 questions for this sample.

---

## Complete Annotated Example

Below is a fully annotated sample from the dataset (`aero_001`):

```json
{
  // ─── Sample Identity ────────────────────────────────────────────────────
  "task_id": "aero_001",               // Unique ID: domain prefix + sequence
  "domain": "aerospace",               // Industrial domain (1 of 10)
  "image_path": "dataset/images/aerospace/boeing_747_400.jpg",  // Input image

  // ─── Generation Prompt ──────────────────────────────────────────────────
  "prompt": "Boeing 747-400 wide-body airliner with four underwing turbofan engines and distinctive upper-deck hump. Camera orbits 41° counter-clockwise around the subject at constant radius, medium smooth arc. Do not add or remove engines, wings, or control surfaces. No morphological changes to fuselage profile. Landing gear strut count and wheel arrangement must be preserved in every frame.",
  // Subject description + camera motion + structural preservation constraints

  // ─── VFA Target ─────────────────────────────────────────────────────────
  "vfa_target": 41.0,                  // Expected camera rotation: 41 degrees

  // ─── Topology ───────────────────────────────────────────────────────────
  "topology_type": "surface",          // Continuous surface (fuselage, wings)

  // ─── IKA Questions ──────────────────────────────────────────────────────
  "questions": [
    {
      "id": "q1",                      // Question ID (used in model_answers key)
      "text": "Does the count of four underwing turbofan engines remain the same between the first and final frame?",
      // Probes: element count invariance across frames
      "answer": "yes",                 // Ground truth: engines should NOT appear/disappear
      "weakness_target": "W3"          // Targets: sub-component count drift
    },
    {
      "id": "q2",
      "text": "Does the fuselage width-to-height ratio remain within 10% of its initial value throughout the camera orbit?",
      // Probes: cross-section deformation under orbit
      "answer": "no",                  // Ground truth: some deformation IS expected
      "weakness_target": "W2"          // Targets: aspect ratio deformation
    },
    {
      "id": "q3",
      "text": "Do the wings remain free of panel gap artifacts and maintain continuous surface topology throughout the video?",
      // Probes: fine surface detail preservation
      "answer": "yes",                 // Ground truth: wings should stay smooth
      "weakness_target": "W6"          // Targets: fine surface detail loss
    }
  ],

  // ─── Constraint Annotations ─────────────────────────────────────────────
  "constraint_annotations": {
    "topology_type": "surface",        // Redundant with top-level (used by IC dispatch)
    "hard_constraints": [
      "fuselage_cross_section_must_not_deform",   // Physical invariant #1
      "engine_count_invariant_across_frames"       // Physical invariant #2
    ],
    "failure_modes": [
      "engine_nacelle_count_drift",               // Expected failure if W3 violated
      "wing_sweep_angle_inconsistency"             // Expected failure if geometry drifts
    ],
    "element_count": 4                 // 4 engines → used by count_invariant checker
  },

  // ─── Difficulty Profile ─────────────────────────────────────────────────
  "difficulty_profile": {
    "ika": "easy",                     // Questions are straightforward
    "tc": "medium",                    // Moderate temporal consistency challenge
    "pp": "medium",                    // Moderate physical plausibility challenge
    "vf": "medium",                    // Moderate view-point fidelity
    "gi": "medium",                    // Moderate geometric integrity
    "vfa": "easy"                      // 41° is a small orbit angle
  },

  // ─── Sensitivity Variants ───────────────────────────────────────────────
  "sensitivity_variants": [
    {
      "id": "aero_001_easy",           // Easy variant ID
      "difficulty": "easy",
      "prompt_delta": "Reduce orbit to 26.7° with slower, smoother arc",
      // Instruction to modify the prompt for this variant
      "vfa_target_delta": -14.3        // New VFA target: 41.0 - 14.3 = 26.7°
    },
    {
      "id": "aero_001_hard",           // Hard variant ID
      "difficulty": "hard",
      "prompt_delta": "Increase orbit to 57.4° and add simultaneous 8° vertical rise",
      "vfa_target_delta": 16.4         // New VFA target: 41.0 + 16.4 = 57.4°
    }
  ]
}
```

---

## Schema Validation

Run the validation script to check all samples against the schema:

```bash
python3 dataset/validate.py
```

This verifies required fields, type constraints, value ranges, and cross-field consistency (e.g., `constraint_annotations.topology_type` matches `topology_type`).
