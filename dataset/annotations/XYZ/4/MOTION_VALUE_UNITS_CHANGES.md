# target motion value 单位补全变更记录

## 摘要

- 更新时间（UTC）：2026-05-18T15:44:21.190075+00:00
- 修改文件：`dataset/annotations/samples.json`
- 修改字段：`prompt`、`video_generation_prompt`
- 修改 task 数：**400**

## 规则

| 条件 | 写法示例 |
|------|----------|
| `motion_type=dolly`，或数值 &lt; 10 | `target motion value 1.5` → `target motion value 1.5x` |
| `motion_type=orbit/pan`，或数值 ≥ 10 | `target motion value 45.0` → `target motion value 45°` |

## 替换统计

| 修改前 | 修改后 | 次数 |
|--------|--------|-----:|
| `target motion value 45.0` | `target motion value 45°` | 398 |
| `target motion value 75.0` | `target motion value 75°` | 206 |
| `target motion value 1.5` | `target motion value 1.5x` | 196 |

## 修改 task_id 列表

```text
emerg_001, emerg_002, emerg_003, emerg_004, emerg_005, emerg_006, emerg_007, emerg_008, emerg_009, emerg_010, emerg_011, emerg_012, emerg_013, emerg_014, emerg_015, emerg_016, emerg_017, emerg_018, emerg_019, emerg_020, emerg_021, emerg_022, emerg_023, emerg_024, emerg_025, emerg_026, emerg_027, emerg_028, emerg_029, emerg_030, emerg_031, emerg_032, emerg_033, emerg_034, emerg_035, emerg_036, emerg_037, emerg_038, emerg_039, emerg_040, emerg_041, emerg_042, emerg_043, emerg_044, emerg_045, emerg_046, emerg_047, emerg_048, emerg_049, emerg_050, emerg_051, emerg_052, emerg_053, emerg_054, emerg_055, emerg_056, emerg_057, emerg_058, emerg_059, emerg_060, emerg_061, emerg_062, emerg_063, emerg_064, emerg_065, emerg_066, emerg_067, erob_001, erob_002, erob_004, erob_005, erob_006, erob_008, erob_009, erob_010, erob_012, erob_013, erob_014, erob_016, erob_017, erob_018, erob_020, erob_021, erob_022, erob_024, erob_025, erob_026, erob_028, erob_029, erob_030, erob_032, erob_033, erob_034, erob_035, erob_036, erob_037, erob_038, erob_039, erob_040, erob_041, erob_042, erob_043, erob_044, erob_045, erob_046, erob_047, erob_048, erob_049, erob_050, erob_051, erob_052, erob_053, erob_054, erob_055, erob_056, erob_057, erob_058, erob_059, erob_060, erob_061, erob_062, erob_063, erob_064, erob_065, erob_066, erob_067, hload_001, hload_002, hload_003, hload_004, hload_005, hload_006, hload_007, hload_008, hload_009, hload_010, hload_011, hload_012, hload_013, hload_014, hload_015, hload_016, hload_017, hload_018, hload_019, hload_020, hload_021, hload_022, hload_023, hload_024, hload_025, hload_026, hload_027, hload_028, hload_029, hload_030, hload_031, hload_032, hload_033, hload_034, hload_035, hload_036, hload_037, hload_038, hload_039, hload_040, hload_041, hload_042, hload_043, hload_044, hload_045, hload_046, hload_047, hload_048, hload_049, hload_050, hload_051, hload_052, hload_053, hload_054, hload_055, hload_056, hload_057, hload_058, hload_059, hload_060, hload_061, hload_062, hload_063, hload_064, hload_065, hload_066, hload_067, hload_068, hload_069, hload_070, hload_071, hload_072, hload_073, hload_074, hload_075, hload_076, hload_077, hload_078, hload_079, hload_080, hload_081, hload_082, hload_083, hload_084, hload_085, hload_086, hload_087, hload_088, hload_089, hload_090, hload_091, hload_092, hload_093, hload_094, hload_095, hload_096, hload_097, hload_098, hload_099, hload_100, pdef_001, pdef_002, pdef_003, pdef_004, pdef_005, pdef_006, pdef_007, pdef_008, pdef_009, pdef_010, pdef_011, pdef_012, pdef_013, pdef_014, pdef_015, pdef_016, pdef_017, pdef_018, pdef_019, pdef_020, pdef_021, pdef_022, pdef_023, pdef_024, pdef_025, pdef_026, pdef_027, pdef_028, pdef_030, pdef_031, pdef_032, pdef_034, pdef_035, pdef_036, pdef_038, pdef_039, pdef_040, pdef_042, pdef_043, pdef_044, pdef_046, pdef_047, pdef_048, pdef_050, pdef_051, pdef_052, pdef_053, pdef_054, pdef_055, pdef_056, pdef_057, pdef_058, pdef_059, pdef_060, pdef_061, pdef_062, pdef_063, pdef_064, pdef_065, pdef_066, pdef_067, pdef_068, pdef_069, pdef_070, pdef_071, pdef_072, pdef_073, pdef_074, pdef_075, pdef_076, pdef_077, pdef_078, pdef_079, pdef_080, pdef_081, pdef_082, pdef_083, pdef_084, pdef_085, pdef_086, pdef_087, pdef_088, pdef_089, pdef_090, pdef_091, pdef_092, pdef_093, pdef_094, pdef_095, pdef_096, pdef_097, pdef_098, pdef_099, pdef_100, vsec_001, vsec_002, vsec_003, vsec_004, vsec_005, vsec_006, vsec_007, vsec_008, vsec_009, vsec_010, vsec_011, vsec_012, vsec_013, vsec_014, vsec_015, vsec_016, vsec_017, vsec_018, vsec_019, vsec_020, vsec_021, vsec_022, vsec_023, vsec_024, vsec_025, vsec_026, vsec_027, vsec_028, vsec_029, vsec_030, vsec_031, vsec_032, vsec_033, vsec_034, vsec_035, vsec_036, vsec_037, vsec_038, vsec_039, vsec_040, vsec_041, vsec_042, vsec_043, vsec_044, vsec_045, vsec_046, vsec_047, vsec_048, vsec_049, vsec_050, vsec_051, vsec_052, vsec_053, vsec_054, vsec_055, vsec_056, vsec_057, vsec_058, vsec_059, vsec_060, vsec_061, vsec_062, vsec_063, vsec_064, vsec_065, vsec_066, vsec_067, vsec_068, vsec_069, vsec_070, vsec_071, vsec_072, vsec_073, vsec_074, vsec_075, vsec_076, vsec_077, vsec_078, vsec_079, vsec_080
```

## 逐条明细

### `emerg_001`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_002`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_003`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_004`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_005`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_006`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_007`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_008`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_009`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_010`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_011`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_012`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_013`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_014`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_015`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_016`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_017`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_018`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_019`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_020`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_021`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_022`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_023`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_024`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_025`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_026`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_027`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_028`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_029`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_030`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_031`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_032`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_033`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_034`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `emerg_035`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_036`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_037`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_038`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_039`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_040`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_041`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_042`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_043`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_044`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_045`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_046`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_047`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_048`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_049`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_050`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_051`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_052`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_053`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_054`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_055`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_056`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_057`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_058`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_059`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_060`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_061`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_062`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_063`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_064`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_065`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_066`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `emerg_067`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_001`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_002`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_004`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_005`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_006`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_008`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_009`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_010`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_012`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_013`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_014`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_016`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_017`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_018`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_020`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_021`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_022`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_024`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_025`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_026`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_028`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_029`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_030`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_032`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_033`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_034`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `erob_035`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_036`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_037`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_038`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_039`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_040`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_041`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_042`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_043`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_044`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_045`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_046`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_047`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_048`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_049`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_050`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_051`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_052`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_053`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_054`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_055`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_056`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_057`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_058`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_059`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_060`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_061`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_062`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_063`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_064`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_065`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_066`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `erob_067`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_001`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_002`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_003`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_004`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_005`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_006`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_007`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_008`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_009`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_010`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_011`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_012`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_013`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_014`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_015`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_016`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_017`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_018`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_019`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_020`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_021`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_022`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_023`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_024`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_025`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_026`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_027`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_028`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_029`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_030`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_031`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_032`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_033`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_034`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_035`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_036`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_037`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_038`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_039`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_040`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_041`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_042`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_043`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_044`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_045`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_046`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_047`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_048`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_049`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_050`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `hload_051`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_052`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_053`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_054`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_055`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_056`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_057`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_058`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_059`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_060`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_061`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_062`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_063`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_064`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_065`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_066`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_067`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_068`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_069`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_070`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_071`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_072`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_073`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_074`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_075`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `hload_076`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_077`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_078`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_079`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_080`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_081`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_082`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_083`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_084`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_085`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_086`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_087`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_088`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_089`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_090`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_091`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_092`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_093`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_094`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_095`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_096`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_097`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_098`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_099`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `hload_100`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_001`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_002`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_003`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_004`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_005`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_006`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_007`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_008`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_009`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_010`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_011`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_012`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_013`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_014`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_015`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_016`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_017`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_018`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_019`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_020`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_021`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_022`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_023`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_024`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_025`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_026`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_027`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_028`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_030`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_031`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_032`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_034`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_035`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_036`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_038`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_039`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_040`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_042`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_043`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_044`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_046`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_047`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_048`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_050`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `pdef_051`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_052`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_053`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_054`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_055`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_056`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_057`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_058`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_059`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_060`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_061`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_062`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_063`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_064`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_065`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_066`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_067`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_068`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_069`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_070`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_071`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_072`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_073`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_074`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_075`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `pdef_076`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_077`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_078`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_079`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_080`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_081`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_082`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_083`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_084`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_085`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_086`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_087`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_088`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_089`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_090`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_091`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_092`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_093`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_094`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_095`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_096`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_097`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_098`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_099`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `pdef_100`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_001`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_002`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_003`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_004`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_005`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_006`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_007`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_008`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_009`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_010`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_011`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_012`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_013`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_014`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_015`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_016`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_017`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_018`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_019`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_020`

- motion_type: `orbit`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_021`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_022`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_023`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_024`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_025`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_026`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_027`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_028`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_029`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_030`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_031`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_032`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_033`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_034`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_035`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_036`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_037`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_038`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_039`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_040`

- motion_type: `dolly`
- viewpoint_motion_target: `1.5`

**prompt**

- `target motion value 1.5` → `target motion value 1.5x`

**video_generation_prompt**

- `target motion value 1.5` → `target motion value 1.5x`

### `vsec_041`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_042`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_043`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_044`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_045`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_046`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_047`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_048`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_049`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_050`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_051`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_052`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_053`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_054`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_055`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_056`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_057`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_058`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_059`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_060`

- motion_type: `pan`
- viewpoint_motion_target: `45.0`

**prompt**

- `target motion value 45.0` → `target motion value 45°`

**video_generation_prompt**

- `target motion value 45.0` → `target motion value 45°`

### `vsec_061`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_062`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_063`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_064`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_065`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_066`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_067`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_068`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_069`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_070`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_071`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_072`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_073`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_074`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_075`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_076`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_077`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_078`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_079`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`

### `vsec_080`

- motion_type: `orbit`
- viewpoint_motion_target: `75.0`

**prompt**

- `target motion value 75.0` → `target motion value 75°`

**video_generation_prompt**

- `target motion value 75.0` → `target motion value 75°`
