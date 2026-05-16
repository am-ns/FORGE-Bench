# Domain and Task Taxonomy

FORGE-Bench now treats `domain` as a scenario-capability domain, not a legacy
industry label. Each domain has 100 samples and is scored through abstract task
categories that determine the highest-weight axis, increased axes, prompt
requirements, and report grouping.

## Domains

| Domain | Samples | Core Evaluation Role |
|---|---:|---|
| `visual_security` | 100 | Industrial security, violation monitoring, access control, protective-equipment compliance, and consequence reasoning. |
| `embodied_robotics` | 100 | Robot manipulation, locomotion, embodied viewpoint, tool contact, and safety interlocks. |
| `heavy_load_construction` | 100 | Construction machinery, cranes, gantries, trucks, wire ropes, load paths, and large-scale contact or failure. |
| `precision_defect_gen` | 100 | Micro-defects, dense structures, endoscopy, gears, CNC cutting, and localized defect generation. |
| `extreme_emergency` | 100 | Chemical leaks, fire spread, structural overload collapse, dust explosion, and emergency response. |

## Evaluation Axes

| Axis | Focus | Badcase Examples | Methodology |
|---|---|---|---|
| `industrial_logic_and_fact_alignment` | Causality and states | Triggered emergency stop ignored; violation has no consequence; equipment role changes without cause. | IndustrialLogicQAJudge with adversarial state-machine questions. |
| `geometric_integrity` | Topology and structure | Joint centers drift; pipes or PCB traces merge; gear tooth count changes. | KinematicChainOperator, TopologyMergeDetector, PeriodicStructureCounter, and industrial constraint operators. |
| `physical_plausibility` | Dynamics and physics | Suspended load floats; leakage ignores pressure direction; robot links pass through objects. | PhysicalDynamicsVLMJudge focused on forces, flow, heat, gravity, and contact. |
| `temporal_consistency` | Continuity and identity | Parts flicker; repeated structures melt; robot model identity changes between frames. | TemporalConsistencyVLMJudge and StructuralSimilarityFrameOperator. |
| `reference_and_motion_fidelity` | Spatial mapping and control | Static video for an orbit task; background collapses during a local defect; reference perspective drifts. | ViewpointMotionEstimator, StaticVideoGate, MaskedReferenceFidelityOperator, and model judgment. |

`viewpoint_motion_fidelity` is a gate component folded into
`reference_and_motion_fidelity`. The industrial constraint score is folded into
`geometric_integrity`.

## Task Categories

### `rigid_body_kinematics_and_coupling`

Highest-weight axis: `geometric_integrity`.

Increased axes: `physical_plausibility`, `temporal_consistency`.

Use for forklifts, robot arms, CNC tools, excavators, cranes, gantries, and
multi-link mechanisms. The video must preserve rigid links, joint centers,
support points, load paths, and feasible multi-axis coupling. Passing videos do
not bend rigid members, detach tools, drift joints, or let bodies interpenetrate.

### `topology_mutation_and_failure`

Highest-weight axis: `geometric_integrity`.

Increased axes: `reference_and_motion_fidelity`, `temporal_consistency`.

Use for short circuits, solder bridges, cracks, broken barriers, wire-rope
failure, gear tooth loss, structural yielding, and local collapse. The requested
mutation must be localized and precise. Non-mutated background and equipment
regions must remain locked to the reference instead of being regenerated.

### `fluid_dynamics_and_thermodynamics`

Highest-weight axis: `physical_plausibility`.

Increased axes: `temporal_consistency`, `industrial_logic_and_fact_alignment`.

Use for chemical leakage, high-pressure spray, mud-water surges, cutting-fluid
splash, smoke, flame, flash fire, dust explosion, and thermal propagation. The
event must obey pressure direction, gravity, diffusion, containment boundaries,
heat or flame spread, and the industrial disaster state implied by the prompt.

### `spatial_exploration_and_viewpoint`

Highest-weight axis: `reference_and_motion_fidelity` as a gate.

Increased axes: `geometric_integrity`, `temporal_consistency`.

Use for surveillance sweeps, robot first-person view, drone orbit, bridge
alignment inspection, tube-bundle endoscopy, dolly moves, pans, cranes, and
orbits. Static substitutions are gated down. Perspective changes must preserve
the reference identity and stable geometry.

### `industrial_logic_and_compliance`

Highest-weight axis: `industrial_logic_and_fact_alignment`.

Increased axes: `temporal_consistency`, `physical_plausibility`.

Use for restricted-zone intrusion, missing safety equipment, light-curtain
triggers, emergency braking, alarms, evacuations, unauthorized hot work, and
compliance consequences. The generated video must form a complete causal loop:
violation, trigger, state change, and consequence.

## Domain and Task Matrix

| Domain | Rigid Kinematics | Topology Failure | Fluid and Thermo | Spatial Viewpoint | Logic and Compliance |
|---|---|---|---|---|---|
| `visual_security` | Forklift overspeed turn and cargo sliding | Broken restricted-zone fence | Chemical liquid leak in dangerous-goods zone | Surveillance sweep across blind spot | Unauthorized vehicle or missing helmet at height |
| `embodied_robotics` | Multi-axis arm grasp and tool contact | Not used | Not used | Quadruped first-person rubble traversal | Worker triggers light curtain and emergency stop |
| `heavy_load_construction` | Excavator linkage or crane load-path motion | Wire-rope extreme deformation and snapping | Broken underground pipe and muddy surge | Drone orbit around bridge precast segment | Not used |
| `precision_defect_gen` | CNC multi-axis curved-surface cutting | PCB solder bridge, gear tooth loss, crack defects | Cutting-fluid spray from high-speed tool | Endoscope through tube bundle | Not used |
| `extreme_emergency` | Not used | Iced transmission tower yielding and collapse | Storage-tank flash fire and pipeline flame spread | Not used | Illegal hot work causing dust explosion |

## Prompt Fields

Each sample prompt includes:

1. task objective;
2. core scenario;
3. reference subject;
4. motion requirement and viewpoint-motion target;
5. industrial logic and fact alignment check;
6. geometric integrity check;
7. physical plausibility check;
8. temporal consistency check;
9. reference and motion fidelity check;
10. execution constraints and scoring emphasis.

For generation, use `video_generation_prompt`. That field is intentionally
shorter and directly instructs an image-to-video model to use the reference
image as the first frame, execute the camera/action requirement, preserve the
industrial scene identity, and avoid known generation failures.
