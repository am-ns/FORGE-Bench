# Scenario Blueprint

This blueprint expands the benchmark from repeated sample variants into
practical scenario families. Each row defines a scene family, the intended
task category, the reference-image requirement, and an example task. A complete
490-sample dataset should allocate roughly 10 samples to each scene family.

## Design Rules

- Prefer real industrial value over visually dramatic but unverifiable events.
- Every scene needs a clear reference image target before prompt generation.
- Backgrounds should be readable and not cluttered; the main subject should be
  large enough for geometry, defect, or compliance judgment.
- Each domain should cover all relevant failure modes: compliance, physical
  dynamics, topology, viewpoint control, and temporal continuity.
- Image search should use the `image_requirement` as a hard acceptance rule,
  not just a keyword hint.

## Visual Security

| Scene ID | Task Category | Samples | Image Requirement | Example Task |
|---|---|---:|---|---|
| `vsec_unregistered_vehicle_intrusion` | `industrial_logic_and_compliance` | 10 | Gate, loading dock, factory road, or restricted lane with clear vehicle path and access boundary. | Unregistered third-party truck enters a marked restricted industrial zone; show detection, alarm, and security response. |
| `vsec_missing_ppe_at_height` | `industrial_logic_and_compliance` | 10 | Elevated work platform, scaffold, roof edge, or harness zone with visible worker safety context. | Worker performs high-altitude work without helmet or harness; show violation recognition and stoppage/escalation. |
| `vsec_forklift_overspeed_pallet_shift` | `rigid_body_kinematics_and_coupling` | 10 | Forklift or pallet truck carrying visible load in warehouse or yard, with uncluttered turning space. | Forklift turns too fast and pallet cargo slides outward under inertia while truck geometry stays rigid. |
| `vsec_crane_unsafe_swing_near_people` | `rigid_body_kinematics_and_coupling` | 10 | Mobile crane, tower crane, or suspended hook/load with visible exclusion zone. | Crane slews a suspended load too close to personnel; preserve cable/load path and show unsafe swing consequence. |
| `vsec_surveillance_blind_spot_sweep` | `spatial_exploration_and_viewpoint` | 10 | CCTV-style view of warehouse aisle, gate, loading bay, or blind corner with depth cues. | Surveillance camera pans across a blind spot and reveals a person or vehicle entering a restricted area. |
| `vsec_perimeter_fence_breach` | `topology_mutation_and_failure` | 10 | Industrial fence, gate, barrier, or guardrail with localized area for damage. | Restricted-zone fence is broken by impact; only the damaged section opens while the rest of the barrier stays fixed. |
| `vsec_dangerous_goods_liquid_leak` | `fluid_dynamics_and_thermodynamics` | 10 | Chemical storage/loading area with pipes, drums, tanks, containment curb, or marked hazardous zone. | Unknown chemical liquid leaks and spreads across a dangerous-goods loading zone with plausible gravity flow. |
| `vsec_pedestrian_forklift_near_miss` | `industrial_logic_and_compliance` | 10 | Warehouse aisle or yard intersection with forklifts/pedestrian route and readable right-of-way context. | Pedestrian enters forklift lane; show warning, braking, and near-miss avoidance without identity swaps. |
| `vsec_smoke_alarm_evacuation` | `fluid_dynamics_and_thermodynamics` | 10 | Industrial corridor, workshop, battery room, or equipment bay with alarm/exit context. | Smoke emerges from equipment, alarm triggers, and workers evacuate following a plausible causal chain. |
| `vsec_guard_removed_conveyor` | `topology_mutation_and_failure` | 10 | Conveyor, rotating machinery, guard cover, or exposed pinch-point area. | A machine guard is missing or displaced near a conveyor; preserve machine topology and show the unsafe exposed zone. |

## Embodied Robotics

| Scene ID | Task Category | Samples | Image Requirement | Example Task |
|---|---|---:|---|---|
| `erob_robot_arm_precision_grasp` | `rigid_body_kinematics_and_coupling` | 10 | Industrial robot arm with gripper/tool and reachable workpiece. | Multi-axis robot arm performs precision grasping with stable joint centers and tool-workpiece contact. |
| `erob_cobot_human_handover` | `industrial_logic_and_compliance` | 10 | Collaborative robot workstation with human proximity or handover table. | Cobot slows and yields during human handover; show safe speed change and no unsafe contact. |
| `erob_tracked_robot_rubble` | `spatial_exploration_and_viewpoint` | 10 | Tracked robot, inspection crawler, or rescue robot near debris, pipes, or uneven terrain. | Tracked robot climbs rubble while first-person camera maintains stable depth and obstacle geometry. |
| `erob_quadruped_stairs_rubble_fpv` | `spatial_exploration_and_viewpoint` | 10 | Quadruped robot or legged robot in industrial stairs, tunnel, plant, or debris setting. | Quadruped head camera traverses complex rubble/stairs without body identity changes or impossible foot contacts. |
| `erob_amr_warehouse_navigation` | `rigid_body_kinematics_and_coupling` | 10 | Autonomous mobile robot or AGV in warehouse aisle with shelves or pallet stations. | AMR navigates around pallets with physically plausible wheel path and stable chassis geometry. |
| `erob_light_curtain_emergency_stop` | `industrial_logic_and_compliance` | 10 | Robotic cell, press, or automated line with light curtain or safety boundary. | Worker crosses light curtain; robot or machine performs emergency stop and remains stopped. |
| `erob_robot_tool_contact_force` | `rigid_body_kinematics_and_coupling` | 10 | Robot sanding, welding, drilling, or polishing tool in contact with surface. | Robot applies tool contact force to a workpiece; avoid tool penetration, floating force, and surface drift. |
| `erob_multi_robot_coordination` | `rigid_body_kinematics_and_coupling` | 10 | Multiple AMRs, robotic arms, or coordinated automation stations with clear spacing. | Two robots coordinate handoff or avoidance; maintain identities, paths, and collision-free timing. |
| `erob_gripper_failure_recovery` | `topology_mutation_and_failure` | 10 | Gripper, suction cup, end effector, or robot tool with visible grasped object. | Gripper partially slips or one suction cup fails; local failure appears while the robot structure remains rigid. |

## Heavy Load Construction

| Scene ID | Task Category | Samples | Image Requirement | Example Task |
|---|---|---:|---|---|
| `hload_dual_crawler_crane_lift` | `rigid_body_kinematics_and_coupling` | 10 | Two cranes, tandem lift, spreader beam, or heavy suspended module with visible rigging. | Two crawler cranes coordinate a steel module lift; preserve sling angles, hook positions, and load balance. |
| `hload_wire_rope_overload_snap` | `topology_mutation_and_failure` | 10 | Crane wire rope, sling, hoist cable, or hook block with visible tension path. | Overloaded wire rope deforms and snaps locally; unchanged crane/load regions stay locked to reference. |
| `hload_mining_truck_muddy_slope` | `rigid_body_kinematics_and_coupling` | 10 | Mining haul truck, articulated dump truck, mud, ramp, tire/track contact, or haul road. | Heavy truck climbs muddy slope with tire sinkage and contact deformation; no floating or sliding uphill without traction. |
| `hload_gantry_wind_disturbance` | `rigid_body_kinematics_and_coupling` | 10 | Gantry crane, container crane, bridge crane, or large portal frame in open yard. | Strong wind disturbs gantry crane or suspended load; show plausible sway and structural resistance. |
| `hload_bridge_segment_alignment_drone` | `spatial_exploration_and_viewpoint` | 10 | Bridge precast segment, viaduct beam, pier cap, or hoisting alignment target. | Drone orbits a bridge segment during alignment inspection while geometry and scale remain consistent. |
| `hload_excavator_linkage_loading` | `rigid_body_kinematics_and_coupling` | 10 | Excavator, loader, hydraulic arm, bucket, or soil pile with clear boom/stick joints. | Excavator performs loaded bucket motion; hydraulic linkage and bucket contact obey rigid-body coupling. |
| `hload_ground_settlement_outrigger` | `topology_mutation_and_failure` | 10 | Crane outrigger, support pad, soft ground, or temporary foundation. | Crane outrigger pad sinks into soft ground, changing support state while boom and chassis stay coherent. |
| `hload_tunnel_pipe_burst_mud_surge` | `fluid_dynamics_and_thermodynamics` | 10 | Construction trench, tunnel, underground pipe, muddy water source, or excavation pit. | Broken underground pipe causes muddy water surge with pressure direction, gravity, and containment boundaries. |
| `hload_hoist_collision_near_structure` | `industrial_logic_and_compliance` | 10 | Hoist, hook, lifted load, scaffold, formwork, or nearby structure with exclusion zone. | Lifted load approaches a structure; signaler triggers stop and load stabilizes before collision. |
| `hload_formwork_collapse_local` | `topology_mutation_and_failure` | 10 | Formwork, scaffold, temporary support, shoring tower, or concrete pouring support. | Local formwork support fails under load; collapse remains localized and follows support topology. |

## Precision Defect Generation

| Scene ID | Task Category | Samples | Image Requirement | Example Task |
|---|---|---:|---|---|
| `pdef_pcb_solder_bridge_short` | `topology_mutation_and_failure` | 10 | High-density PCB, solder joints, IC pins, fine traces, or macro electronics view. | Generate a localized solder bridge short between adjacent PCB traces without changing nearby component counts. |
| `pdef_engine_endoscope_crack` | `spatial_exploration_and_viewpoint` | 10 | Engine borescope/endoscope view, turbine blade, pipe wall, or inner cavity inspection. | Endoscope moves toward a micro crack on turbine or pipe wall while preserving cylindrical/internal geometry. |
| `pdef_gear_tooth_missing_wear` | `topology_mutation_and_failure` | 10 | Gear teeth, gearbox, sprocket, rack, or machined periodic teeth with clear counts. | One gear tooth chips or wears severely; tooth count and neighboring geometry remain stable. |
| `pdef_cnc_curved_surface_cutting` | `rigid_body_kinematics_and_coupling` | 10 | CNC milling center, 5-axis machine, tool, fixture, and workpiece. | 5-axis CNC cuts a curved surface with coupled spindle/tool motion and stable workpiece fixturing. |
| `pdef_cutting_fluid_spray` | `fluid_dynamics_and_thermodynamics` | 10 | Machining zone with coolant nozzle, rotating tool, metal chips, or enclosed CNC window. | Cutting fluid sprays from a high-speed tool with coherent droplet trajectory and no scene-wide melting. |
| `pdef_weld_porosity_crack` | `topology_mutation_and_failure` | 10 | Weld seam, pipe weld, steel plate, bead, or inspection close-up with localized defect area. | Weld seam develops porosity or a fine crack; defect is localized and reference metal boundaries stay fixed. |
| `pdef_surface_scratch_inspection` | `topology_mutation_and_failure` | 10 | Polished metal, wafer, optical lens, bearing race, or machined surface. | Fine scratches appear on a precision surface while lighting and unaffected surface texture remain stable. |
| `pdef_tube_bundle_endoscopy` | `spatial_exploration_and_viewpoint` | 10 | Heat exchanger tube bundle, borescope tunnel, dense repeated circular pipes. | Endoscope navigates through tube bundle; repeated pipe openings keep count and perspective consistency. |
| `pdef_connector_pin_bent` | `topology_mutation_and_failure` | 10 | Dense electrical connector, pins, sockets, wire bond pads, or terminal block. | One connector pin bends or bridges adjacent pins; nearby pins remain aligned and count-stable. |
| `pdef_precision_assembly_misalignment` | `rigid_body_kinematics_and_coupling` | 10 | Bearing, shaft, fixture, precision assembly jig, or robotic inspection station. | Precision component is slightly misaligned during assembly; evaluate small pose error without changing part identity. |

## Extreme Emergency

| Scene ID | Task Category | Samples | Image Requirement | Example Task |
|---|---|---:|---|---|
| `emerg_flange_high_pressure_leak` | `fluid_dynamics_and_thermodynamics` | 10 | Pipe flange, valve station, refinery pipe rack, or chemical pipeline with visible joint. | High-pressure flange leak sprays vapor/liquid and causes local visual distortion; flow follows pressure and wind direction. |
| `emerg_storage_tank_flash_fire` | `fluid_dynamics_and_thermodynamics` | 10 | Storage tank farm, bund wall, pipe network, or refinery tank area. | Local flash fire starts at storage tank piping and propagates along nearby pipe route with plausible heat spread. |
| `emerg_transmission_tower_icing_collapse` | `topology_mutation_and_failure` | 10 | Transmission tower, lattice pylon, ice/snow load context, or high-voltage corridor. | Ice-loaded transmission tower yields and collapses locally according to lattice support topology. |
| `emerg_dust_explosion_confined_space` | `industrial_logic_and_compliance` | 10 | Grain silo, dust collector, workshop, confined hot-work zone, or powder handling area. | Illegal hot work ignites dust cloud; show flash, pressure wave, alarm, and emergency response chain. |
| `emerg_reactor_runaway_pressure_release` | `fluid_dynamics_and_thermodynamics` | 10 | Reactor vessel, pressure relief valve, chemical plant piping, or control platform. | Reactor overpressure opens relief path; plume direction, pressure release, and operator response remain plausible. |
| `emerg_battery_thermal_runaway` | `fluid_dynamics_and_thermodynamics` | 10 | Battery energy storage container, EV battery pack, charging bay, or battery room. | One battery module enters thermal runaway; smoke/heat spreads locally and suppression response follows. |
| `emerg_tunnel_fire_smoke_layering` | `fluid_dynamics_and_thermodynamics` | 10 | Road tunnel, mine tunnel, conveyor tunnel, or enclosed industrial corridor. | Fire creates stratified smoke layer moving along tunnel ceiling; visibility and evacuation evolve consistently. |
| `emerg_crane_load_drop_evacuation` | `industrial_logic_and_compliance` | 10 | Crane lift zone, suspended load, hook block, exclusion area, or construction yard. | Load begins to drop or swing dangerously; alarms trigger evacuation and exclusion-zone response. |
| `emerg_cooling_tower_plume_failure` | `fluid_dynamics_and_thermodynamics` | 10 | Cooling tower, steam plume, industrial HVAC/thermal plant, or condenser equipment. | Cooling plume changes due to fan or flow failure; vapor expansion follows airflow and temperature gradient. |
| `emerg_dam_or_retaining_wall_breach` | `topology_mutation_and_failure` | 10 | Industrial retaining wall, tailings dam face, containment berm, or flood barrier. | Local breach forms in containment wall and water/slurry escapes through the opening with plausible erosion. |
