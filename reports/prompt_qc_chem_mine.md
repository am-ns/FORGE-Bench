# Prompt QC — chem_* / mine_* & chemical/mining images

Automated checks against senior requirements:
- clear motion verb (`orbit` / `pan` / `dolly` / `crane`)
- quantified target (45°/90°/2x or explicit target value)
- structure/component visibility hints
- `No zoom.` suffix on `video_generation_prompt`
- evaluation prompt 10-section structure
- `motion_type` consistency
- chem/mine sensitivity variant delta consistency

| Metric | Count |
|---|---:|
| Total samples | 500 |
| Priority scope (chem/mine variants or chemical/mining image) | 204 |
| Flagged in priority scope | 204 |
| Flagged across all samples | 500 |

## Flag counts (priority scope)

- `missing_no_zoom_suffix`: 204
- `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 4
- `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 4
- `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_pan`: 4
- `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_pan`: 4
- `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 3
- `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 3
- `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_pan`: 3
- `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_pan`: 3
- `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 3
- `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 3
- `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_static`: 2
- `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_static`: 2
- `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_static`: 2
- `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_static`: 2
- `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_pan`: 2
- `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_pan`: 2
- `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_dolly`: 1
- `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_pan`: 1
- `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_static`: 1
- `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_static`: 1

---

## `emerg_001`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_002`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/energy_renewable/wind_turbine.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_003`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_004`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_008`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_011`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_012`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_016`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_020`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_024`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_026`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/energy_renewable/wind_turbine.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_027`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_028`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_029`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_032`
- domain: `extreme_emergency` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `emerg_035`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_036`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_037`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_038`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_039`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_040`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_042`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_043`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_044`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_046`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_047`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_048`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_050`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_051`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_052`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_053`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_054`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_055`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_056`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_058`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_059`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_060`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_062`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_063`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_064`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_066`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/distillation_column_array.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_067`
- domain: `extreme_emergency` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `emerg_070`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_071`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_074`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_075`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_078`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_079`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_080`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_081`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/assembly_line.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_082`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_083`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_086`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_087`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_089`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/assembly_line.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_090`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_091`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_094`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_095`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_098`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `emerg_099`
- domain: `extreme_emergency` / task: `industrial_logic_and_compliance`
- image: `dataset/images/mining/surface_blast_pattern.jpg`
- motion: `static` / target: `0.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `erob_003`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/parallel_kinematic_hexapod.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_004`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_005`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/industrial_robot_arm.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_013`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/industrial_robot_arm.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_014`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/collaborative_robot.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_029`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/industrial_robot_arm.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_030`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/collaborative_robot.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_031`
- domain: `embodied_robotics` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/robotics/parallel_kinematic_hexapod.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `erob_039`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_040`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_055`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_056`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_057`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_065`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_066`
- domain: `embodied_robotics` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `erob_081`
- domain: `embodied_robotics` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/cobot_assembly_station.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `erob_082`
- domain: `embodied_robotics` / task: `industrial_logic_and_compliance`
- image: `dataset/images/robotics/collaborative_robot.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `erob_083`
- domain: `embodied_robotics` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `erob_091`
- domain: `embodied_robotics` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `erob_092`
- domain: `embodied_robotics` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/assembly_line.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `hload_004`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_008`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_012`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_016`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_019`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/construction/mobile_crane_telescoping.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_020`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_021`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/construction/excavator.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_022`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_024`
- domain: `heavy_load_construction` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `hload_029`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_030`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_033`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_037`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_041`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_045`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_046`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_047`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/tower_crane_luffing.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_048`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_049`
- domain: `heavy_load_construction` / task: `topology_mutation_and_failure`
- image: `dataset/images/mining/mine_hoist_headframe.jpg`
- motion: `dolly` / target: `1.5`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `hload_053`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_054`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_056`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/construction/tunnel_boring_machine.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_057`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_058`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_061`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_062`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_065`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_066`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_069`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_070`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_071`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_072`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/construction/tunnel_boring_machine.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_073`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_074`
- domain: `heavy_load_construction` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/mining/thickener_tank_farm.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `hload_082`
- domain: `heavy_load_construction` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `hload_097`
- domain: `heavy_load_construction` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `hload_098`
- domain: `heavy_load_construction` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `hload_099`
- domain: `heavy_load_construction` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `hload_100`
- domain: `heavy_load_construction` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_010`
- domain: `precision_defect_gen` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `pdef_011`
- domain: `precision_defect_gen` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `pdef_012`
- domain: `precision_defect_gen` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `pdef_020`
- domain: `precision_defect_gen` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `pdef_021`
- domain: `precision_defect_gen` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/manufacturing/cnc_machine.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `pdef_036`
- domain: `precision_defect_gen` / task: `topology_mutation_and_failure`
- image: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `pdef_037`
- domain: `precision_defect_gen` / task: `topology_mutation_and_failure`
- image: `dataset/images/electronics/wire_bonding_machine.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `pdef_038`
- domain: `precision_defect_gen` / task: `topology_mutation_and_failure`
- image: `dataset/images/electronics/pcb_circuit_board.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `pdef_046`
- domain: `precision_defect_gen` / task: `topology_mutation_and_failure`
- image: `dataset/images/electronics/pcb_circuit_board.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `pdef_047`
- domain: `precision_defect_gen` / task: `topology_mutation_and_failure`
- image: `dataset/images/electronics/micro_009.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `pdef_053`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_057`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_061`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_062`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_002_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_surf_002_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_063`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/manufacturing/cnc_machine.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_001_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_lat_001_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_064`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/manufacturing/industrial_washing_line.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_009_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_lat_009_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_065`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_069`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_072`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/manufacturing/industrial_washing_line.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_kin_010_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_kin_010_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_073`
- domain: `precision_defect_gen` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/centrifuge_battery.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_lat_004_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_lat_004_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `pdef_076`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_077`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_079`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_080`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_082`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_083`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_085`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_086`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_088`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_surf_002_easy`, `chem_surf_002_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_089`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_lat_001_easy`, `mine_lat_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_090`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_lat_009_easy`, `chem_lat_009_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_091`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_092`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_094`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_095`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_097`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_098`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_kin_010_easy`, `mine_kin_010_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_099`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_lat_004_easy`, `mine_lat_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `pdef_100`
- domain: `precision_defect_gen` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- motion: `orbit` / target: `75.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_002`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/heavy_haul_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_004`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/articulated_dump_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_006`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/heavy_haul_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_008`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/articulated_dump_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_010`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/heavy_haul_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_012`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/articulated_dump_truck.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_013`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/construction/veh_014.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_014`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/heavy_haul_truck.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_015`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/construction/road_train_coupling_system.jpg`
- motion: `orbit` / target: `45.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_016`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/articulated_dump_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_018`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/heavy_haul_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_020`
- domain: `visual_security` / task: `rigid_body_kinematics_and_coupling`
- image: `dataset/images/mining/articulated_dump_truck.jpg`
- motion: `orbit` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 45_

## `vsec_023`
- domain: `visual_security` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `vsec_038`
- domain: `visual_security` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `vsec_039`
- domain: `visual_security` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `vsec_040`
- domain: `visual_security` / task: `topology_mutation_and_failure`
- image: `dataset/images/construction/aerial_work_platform_boom.jpg`
- motion: `dolly` / target: `1.5`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_dolly`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_dolly`
- camera excerpt: _perform a controlled dolly-in toward the local defect or failure region; target motion value 1_

## `vsec_041`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_042`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_043`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_044`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/solvent_extraction_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_045`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_046`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_047`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_048`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/solvent_extraction_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_049`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_mine_surf_003_easy_delta_mentions_orbit_but_motion_type_is_pan`
  - `variant_mine_surf_003_hard_delta_mentions_orbit_but_motion_type_is_pan`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_050`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_051`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_052`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/solvent_extraction_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_053`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_054`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_055`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_056`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/solvent_extraction_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_057`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/piping_manifold.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_058`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/chemical_storage_tanks.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_059`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/pressure_vessel_farm.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_060`
- domain: `visual_security` / task: `fluid_dynamics_and_thermodynamics`
- image: `dataset/images/chemical/solvent_extraction_battery.jpg`
- motion: `pan` / target: `45.0`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45_

## `vsec_064`
- domain: `visual_security` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_065`
- domain: `visual_security` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/manufacturing/assembly_line.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_066`
- domain: `visual_security` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_067`
- domain: `visual_security` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/concrete_batching_plant.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_075`
- domain: `visual_security` / task: `spatial_exploration_and_viewpoint`
- image: `dataset/images/construction/concrete_batching_plant.jpg`
- motion: `orbit` / target: `75.0`
- chem/mine variants: `mine_surf_003_easy`, `mine_surf_003_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _perform a smooth constant-radius orbit around the subject; target motion value 75_

## `vsec_090`
- domain: `visual_security` / task: `industrial_logic_and_compliance`
- image: `dataset/images/manufacturing/assembly_line.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_kin_001_easy`, `chem_kin_001_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `vsec_091`
- domain: `visual_security` / task: `industrial_logic_and_compliance`
- image: `dataset/images/construction/veh_008.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `mine_kin_004_easy`, `mine_kin_004_hard`
- **flags:**
  - `missing_no_zoom_suffix`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `vsec_092`
- domain: `visual_security` / task: `industrial_logic_and_compliance`
- image: `dataset/images/construction/mobile_crane_outrigger_system.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_lat_005_easy`, `chem_lat_005_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_lat_005_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_lat_005_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_

## `vsec_093`
- domain: `visual_security` / task: `industrial_logic_and_compliance`
- image: `dataset/images/construction/aerial_work_platform_boom.jpg`
- motion: `static` / target: `0.0`
- chem/mine variants: `chem_surf_006_easy`, `chem_surf_006_hard`
- **flags:**
  - `missing_no_zoom_suffix`
  - `variant_chem_surf_006_easy_delta_mentions_orbit_but_motion_type_is_static`
  - `variant_chem_surf_006_hard_delta_mentions_orbit_but_motion_type_is_static`
- camera excerpt: _hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger_
