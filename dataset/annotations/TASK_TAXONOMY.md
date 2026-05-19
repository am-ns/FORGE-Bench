# Domain and Task Taxonomy

FORGE-Bench treats `domain` as a scenario-capability domain, not a legacy
industry label. The benchmark is organized as a Domain x Task orthogonal matrix:
the X axis is where the industrial data and visual context come from, while the
Y axis is the abstract capability being tested. This allows cross-attribution of
model weaknesses instead of only reporting a single average score.

## Domains

| Domain | Samples | Core Evaluation Role |
|---|---:|---|
| `visual_security` | 100 | Industrial security, violation monitoring, access control, protective-equipment compliance, and consequence reasoning. |
| `embodied_robotics` | 90 | Robot manipulation, locomotion, embodied viewpoint, tool contact, and safety interlocks. |
| `heavy_load_construction` | 100 | Construction machinery, cranes, gantries, trucks, wire ropes, load paths, and large-scale contact or failure. |
| `precision_defect_gen` | 100 | Micro-defects, dense structures, endoscopy, gears, CNC cutting, and localized defect generation. |
| `extreme_emergency` | 100 | Chemical leaks, fire spread, structural overload collapse, dust explosion, and emergency response. |

## Evaluation Axes

| Axis | Focus | Badcase Examples | Methodology |
|---|---|---|---|
| `industrial_logic_and_fact_alignment` | Causality and states | Triggered emergency stop ignored; violation has no consequence; equipment role changes without cause. | State-machine adversarial QA checks causal closure, conditional triggers, compliance state, and industrial fact progression. |
| `geometric_integrity` | Topology and structure | Joint centers drift; pipes or PCB traces merge; gear tooth count changes. | Spatial topology, local micro-structure measurement, joint-center anti-drift, dense periodic-structure stability, and topology mutation validation. |
| `physical_plausibility` | Dynamics and physics | Suspended load floats; leakage ignores pressure direction; robot links pass through objects. | Mechanics and dynamics validation for gravity, rigid-body contact, pressure direction, fluid spread, heat propagation, and load paths. |
| `temporal_consistency` | Continuity and identity | Parts flicker; repeated structures melt; robot model identity changes between frames. | Long-horizon identity, material, state, anti-deformation, anti-melting, and anti-flicker checks. |
| `reference_and_motion_fidelity` | Spatial mapping and control | Static video for an orbit task; background collapses during a local defect; reference perspective drifts. | Reference locking, camera-control execution, static-video gating, and region-isolated fidelity for local events. |

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

This is the core diagnostic matrix. Domain answers "which industrial context
failed"; task answers "which underlying capability failed".

| Domain | Rigid Kinematics | Topology Failure | Fluid and Thermo | Spatial Viewpoint | Logic and Compliance |
|---|---|---|---|---|---|
| `visual_security` | Forklift overspeed and crane swing | Fence breach and missing guards | Dangerous-goods leak and smoke alarm | CCTV blind-spot sweep | Intrusion, PPE, near-miss, alarm response |
| `embodied_robotics` | Robot grasp, AMR path, tool contact | Gripper local failure | Safety-cell event dynamics | Tracked/quadruped robot viewpoint | Cobot handover and light-curtain stop |
| `heavy_load_construction` | Crane, excavator, truck, gantry load paths | Wire rope, outrigger, formwork failure | Tunnel pipe burst and mud surge | Bridge/drone alignment inspection | Hoist stop before collision |
| `precision_defect_gen` | CNC cutting and assembly misalignment | PCB bridge, gear wear, weld/scratch/pin defects | Cutting-fluid spray | Endoscope and tube-bundle navigation | Inspection logic through localized constraints |
| `extreme_emergency` | Emergency crane/load dynamics | Tower icing and wall breach | Flange leak, flash fire, reactor, battery, tunnel, plume | Emergency spatial continuity | Dust explosion, evacuation, response chain |

## Scoring Formula

```text
FORGE_final =
  WeightedAverage(
    industrial_logic_and_fact_alignment,
    temporal_consistency,
    physical_plausibility,
    reference_and_motion_fidelity,
    geometric_integrity
  )
```

Weights are selected dynamically from the abstract task category. Mechanism and
robotics tasks emphasize geometry and physics; periodic/local-defect tasks
emphasize geometry and temporal continuity; spatial-inspection tasks emphasize
reference/motion fidelity and geometry.

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
