# Prompt 结构可见性质检

## 检查说明

- 数据源：`dataset/annotations/samples.json` → **`prompt`**
- 检查目标：除 `Reference subject` 外，**Motion requirement** 是否写明运镜时**哪些部件/结构应在画面中**
- 不计入：Geometric integrity 等轴段中的通用 “joints / members” 评测约束用语

- 审计时间（UTC）：2026-05-19T10:32:13.085085+00:00
- 样本总数：**486**
- 可能缺少结构可见性描述：**486**
-  motion 段已有明确描述：**0**

## 状态统计

| 状态 | 含义 | 数量 |
|------|------|-----:|
| `pass_motion` | motion 段含可见性/部件取景描述 | 0 |
| `weak_motion` | 仅 subject / defect / leak 等笼统目标 | 400 |
| `fail_motion` | motion 段无结构可见性描述 | 86 |

## 按 motion_type（可能不合格）

- `orbit`：**199**
- `pan`：**103**
- `dolly`：**98**
- `static`：**86**

## 可能不合格 task_id

```text
emerg_001, emerg_002, emerg_003, emerg_004, emerg_005, emerg_006, emerg_007, emerg_008, emerg_009, emerg_010, emerg_011, emerg_012, emerg_013, emerg_014, emerg_015, emerg_016, emerg_017, emerg_018, emerg_019, emerg_020, emerg_021, emerg_022, emerg_023, emerg_024, emerg_025, emerg_026, emerg_027, emerg_028, emerg_029, emerg_030, emerg_031, emerg_032, emerg_033, emerg_034, emerg_035, emerg_036, emerg_037, emerg_038, emerg_039, emerg_040, emerg_041, emerg_042, emerg_043, emerg_044, emerg_045, emerg_046, emerg_047, emerg_048, emerg_049, emerg_050, emerg_051, emerg_052, emerg_053, emerg_054, emerg_055, emerg_056, emerg_057, emerg_058, emerg_059, emerg_060, emerg_061, emerg_062, emerg_063, emerg_064, emerg_065, emerg_066, emerg_067, emerg_068, emerg_069, emerg_070, emerg_071, emerg_072, emerg_073, emerg_074, emerg_075, emerg_076, emerg_077, emerg_078, emerg_079, emerg_080, emerg_081, emerg_082, emerg_083, emerg_084, emerg_085, emerg_086, emerg_087, emerg_088, emerg_089, emerg_090, emerg_091, emerg_092, emerg_093, emerg_094, emerg_095, emerg_096, emerg_097, emerg_098, emerg_099, emerg_100, erob_001, erob_002, erob_004, erob_005, erob_006, erob_008, erob_009, erob_010, erob_012, erob_013, erob_014, erob_016, erob_017, erob_018, erob_020, erob_021, erob_022, erob_024, erob_025, erob_026, erob_028, erob_029, erob_030, erob_032, erob_033, erob_034, erob_035, erob_036, erob_037, erob_038, erob_039, erob_040, erob_041, erob_042, erob_043, erob_044, erob_045, erob_046, erob_047, erob_048, erob_049, erob_050, erob_051, erob_052, erob_053, erob_054, erob_055, erob_056, erob_057, erob_058, erob_059, erob_060, erob_061, erob_062, erob_063, erob_064, erob_065, erob_066, erob_067, erob_068, erob_069, erob_070, erob_071, erob_072, erob_073, erob_074, erob_075, erob_076, erob_077, erob_078, erob_079, erob_080, erob_081, erob_082, erob_083, erob_084, erob_085, erob_086, erob_087, erob_088, erob_089, erob_090, erob_091, erob_092, erob_093, erob_094, erob_095, erob_096, erob_097, erob_098, erob_099, erob_100, hload_001, hload_002, hload_003, hload_004, hload_005, hload_006, hload_007, hload_008, hload_009, hload_010, hload_011, hload_012, hload_013, hload_014, hload_015, hload_016, hload_017, hload_018, hload_019, hload_020, hload_021, hload_022, hload_023, hload_024, hload_025, hload_026, hload_027, hload_028, hload_029, hload_030, hload_031, hload_032, hload_033, hload_034, hload_035, hload_036, hload_037, hload_038, hload_039, hload_040, hload_041, hload_042, hload_043, hload_044, hload_045, hload_046, hload_047, hload_048, hload_049, hload_050, hload_051, hload_052, hload_053, hload_054, hload_055, hload_056, hload_057, hload_058, hload_059, hload_060, hload_061, hload_062, hload_063, hload_064, hload_065, hload_066, hload_067, hload_068, hload_069, hload_070, hload_071, hload_072, hload_073, hload_074, hload_075, hload_076, hload_077, hload_078, hload_079, hload_080, hload_081, hload_082, hload_083, hload_084, hload_085, hload_086, hload_087, hload_088, hload_089, hload_090, hload_091, hload_092, hload_093, hload_094, hload_095, hload_096, hload_097, hload_098, hload_099, hload_100, pdef_001, pdef_002, pdef_003, pdef_004, pdef_005, pdef_006, pdef_007, pdef_008, pdef_009, pdef_010, pdef_011, pdef_012, pdef_013, pdef_014, pdef_015, pdef_016, pdef_017, pdef_018, pdef_019, pdef_020, pdef_021, pdef_022, pdef_023, pdef_024, pdef_025, pdef_026, pdef_027, pdef_028, pdef_030, pdef_031, pdef_032, pdef_034, pdef_035, pdef_036, pdef_038, pdef_039, pdef_040, pdef_042, pdef_043, pdef_044, pdef_046, pdef_047, pdef_048, pdef_050, pdef_051, pdef_052, pdef_053, pdef_054, pdef_055, pdef_056, pdef_057, pdef_058, pdef_059, pdef_060, pdef_061, pdef_062, pdef_063, pdef_064, pdef_065, pdef_066, pdef_067, pdef_068, pdef_069, pdef_070, pdef_071, pdef_072, pdef_073, pdef_074, pdef_075, pdef_076, pdef_077, pdef_078, pdef_079, pdef_080, pdef_081, pdef_082, pdef_083, pdef_084, pdef_085, pdef_086, pdef_087, pdef_088, pdef_089, pdef_090, pdef_091, pdef_092, pdef_093, pdef_094, pdef_095, pdef_096, pdef_097, pdef_098, pdef_099, pdef_100, vsec_001, vsec_002, vsec_003, vsec_004, vsec_005, vsec_006, vsec_007, vsec_008, vsec_009, vsec_010, vsec_011, vsec_012, vsec_013, vsec_014, vsec_015, vsec_016, vsec_017, vsec_018, vsec_019, vsec_020, vsec_021, vsec_022, vsec_023, vsec_024, vsec_025, vsec_026, vsec_027, vsec_028, vsec_029, vsec_030, vsec_031, vsec_032, vsec_033, vsec_034, vsec_035, vsec_036, vsec_037, vsec_038, vsec_039, vsec_040, vsec_041, vsec_042, vsec_043, vsec_044, vsec_045, vsec_046, vsec_047, vsec_048, vsec_049, vsec_050, vsec_051, vsec_052, vsec_053, vsec_054, vsec_055, vsec_056, vsec_057, vsec_058, vsec_059, vsec_060, vsec_061, vsec_062, vsec_063, vsec_064, vsec_065, vsec_066, vsec_067, vsec_068, vsec_069, vsec_070, vsec_071, vsec_072, vsec_073, vsec_074, vsec_075, vsec_076, vsec_077, vsec_078, vsec_079, vsec_080, vsec_081, vsec_082, vsec_083, vsec_084, vsec_085, vsec_086, vsec_087, vsec_088, vsec_089, vsec_090, vsec_091, vsec_092, vsec_093, vsec_094, vsec_095, vsec_096, vsec_097, vsec_098, vsec_099, vsec_100
```

## 典型 motion 段落模式（当前数据）

多数样本 motion 段为模板句，例如：

- dolly：`perform a controlled dolly-in toward the local defect or failure region`
- orbit：`perform a smooth constant-radius orbit around the subject`
- pan：`perform a controlled lateral pan that follows the evolving leak, spray, smoke...`

上述写法**未点名**应保持在画面中的具体部件（如 jib、pipe rack、linkage 等）。

## 逐条详情（可能不合格）

### `emerg_001`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_002`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_003`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_004`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_005`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_006`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_007`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_008`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_009`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_010`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_011`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_012`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_013`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_014`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_015`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_016`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_017`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_018`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_019`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_020`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_021`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_022`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_023`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_024`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_025`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_026`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_027`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_028`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_029`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_030`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_031`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_032`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_033`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `high voltage transformer yard`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_034`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `wind turbine`
- core_scenario: `transmission tower overloaded by ice and snow until the load-bearing structure yields and collapses`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `emerg_035`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_036`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_037`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_038`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_039`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_040`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_041`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_042`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_043`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_044`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_045`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_046`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_047`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_048`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_049`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_050`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_051`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_052`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_053`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_054`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_055`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_056`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_057`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_058`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_059`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_060`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_061`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_062`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_063`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_064`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_065`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `offshore oil platform`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_066`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `distillation column array`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_067`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `chemical storage-tank flash fire with flame propagating along an industrial pipe network`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `emerg_068`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_069`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_070`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_071`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_072`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_073`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_074`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_075`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_076`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_077`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_078`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_079`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_080`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_081`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_082`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_083`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_084`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_085`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_086`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_087`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_088`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_089`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_090`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_091`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_092`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_093`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_094`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_095`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_096`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_097`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_098`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `pressure vessel farm`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_099`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `surface blast pattern`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `emerg_100`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `illegal hot work in a confined space directly triggering a dust explosion and emergency response`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_001`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_002`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_004`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_005`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_006`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_008`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_009`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_010`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_012`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_013`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_014`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_016`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_017`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_018`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_020`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_021`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_022`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_024`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_025`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_026`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_028`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_029`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_030`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_032`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `surgical robot instrument arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_033`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `industrial robot arm`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_034`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `collaborative robot`
- core_scenario: `multi-axis robotic arm performing high-precision grasping with tool-environment contact`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `erob_035`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_036`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_037`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_038`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_039`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_040`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_041`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_042`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_043`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_044`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_045`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_046`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_047`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_048`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_049`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_050`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_051`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_052`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_053`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_054`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_055`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_056`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_057`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_058`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_059`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_060`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_061`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_062`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_063`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_064`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic pipe crawler`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_065`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `snake robot inspection unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_066`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `agv fleet navigation unit`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_067`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `autonomous mobile robot`
- core_scenario: `quadruped robot head camera moving through complex rubble from a first-person viewpoint`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `erob_068`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_069`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_070`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_071`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_072`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_073`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_074`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_075`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_076`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_077`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_078`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_079`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_080`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_081`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_082`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_083`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_084`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_085`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_086`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_087`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_088`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_089`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_090`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_091`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_092`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_093`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_094`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_095`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_096`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_097`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `cobot assembly station`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_098`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `collaborative robot`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_099`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `robotic welding cell`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `erob_100`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `worker approaching an automated line and triggering a light curtain that forces emergency braking`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `hload_001`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_002`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_003`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_004`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_005`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_006`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_007`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_008`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_009`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_010`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_011`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_012`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_013`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_014`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_015`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_016`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_017`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_018`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_019`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_020`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_021`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_022`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_023`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `mobile crane telescoping`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_024`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `hydraulic shovel loading`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_025`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `excavator`
- core_scenario: `excavator multi-link loading motion or synchronized crawler-crane hoisting with visible load path`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `hload_026`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_027`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_028`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_029`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_030`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_031`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_032`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_033`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_034`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_035`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_036`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_037`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_038`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_039`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_040`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_041`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_042`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_043`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_044`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_045`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_046`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_047`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_048`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `cable laying ship drum`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_049`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `mine hoist headframe`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_050`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `overloaded crawler crane causing wire-rope extreme deformation and possible snapping`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `hload_051`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_052`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_053`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_054`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_055`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_056`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_057`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_058`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_059`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_060`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_061`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_062`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_063`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_064`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_065`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_066`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_067`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_068`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_069`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_070`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_071`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_072`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `tunnel boring machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_073`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_074`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `thickener tank farm`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_075`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `trenchless pipe jacking machine`
- core_scenario: `underground water pipe accidentally broken at a construction site causing muddy water to surge upward`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `hload_076`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_077`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_078`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_079`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_080`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_081`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_082`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_083`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_084`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_085`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_086`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_087`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_088`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_089`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_090`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_091`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_092`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_093`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_094`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_095`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_096`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_097`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_098`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `precast yard stacking gantry`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_099`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `container terminal quay crane`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `hload_100`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cable stayed bridge deck segment`
- core_scenario: `drone orbiting a hundred-ton bridge precast segment to inspect hoisting alignment`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_001`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_002`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_003`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_004`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_005`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_006`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_007`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_008`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_009`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_010`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_011`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_012`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_013`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_014`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_015`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_016`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_017`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_018`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_019`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_020`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_021`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_022`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `five axis machining center`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_023`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gear hobbing machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_024`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `automated grinding cell`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_025`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `cnc machine`
- core_scenario: `CNC machine performing multi-axis coupled cutting on a complex curved surface`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `pdef_026`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_027`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_028`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_030`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_031`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_032`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_034`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_035`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_036`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_038`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_039`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_040`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_042`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_043`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_044`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_046`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_047`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `micro 009`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_048`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `gear hobbing machine`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_050`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `pcb circuit board`
- core_scenario: `dense PCB traces forming solder-bridge short circuits, missing gear teeth, or severe gear wear`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `pdef_051`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_052`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_053`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_054`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_055`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_056`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_057`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_058`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_059`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_060`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_061`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_062`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_063`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_064`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_065`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_066`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_067`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_068`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_069`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_070`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_071`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_072`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `industrial washing line`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_073`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `centrifuge battery`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_074`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `automated grinding cell`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_075`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `cnc machine`
- core_scenario: `cutting fluid splashing from a high-speed rotating tool with coherent spray trajectories`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `pdef_076`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_077`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_078`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_079`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_080`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_081`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_082`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_083`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_084`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_085`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_086`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_087`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_088`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_089`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_090`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_091`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_092`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_093`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_094`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_095`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_096`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_097`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_098`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `piping manifold`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_099`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `gas turbine compressor section`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `pdef_100`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heat exchanger bundle`
- core_scenario: `endoscope moving through a complex tube bundle while preserving pipe-wall geometry`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_001`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `veh 014`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_002`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heavy haul truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_003`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `road train coupling system`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_004`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `articulated dump truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_005`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `veh 014`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_006`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heavy haul truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_007`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `road train coupling system`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_008`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `articulated dump truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_009`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `veh 014`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_010`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heavy haul truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_011`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `road train coupling system`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_012`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `articulated dump truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_013`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `veh 014`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_014`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heavy haul truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_015`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `road train coupling system`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_016`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `articulated dump truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_017`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `veh 014`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_018`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `heavy haul truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_019`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `road train coupling system`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_020`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `articulated dump truck`
- core_scenario: `forklift overspeed during a tight turn causing pallet cargo to slide outward under centrifugal force`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45°
```

### `vsec_021`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `formwork climbing system`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_022`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_023`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_024`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `aerial work platform boom`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_025`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `formwork climbing system`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_026`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_027`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_028`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `aerial work platform boom`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_029`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `formwork climbing system`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_030`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_031`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_032`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `aerial work platform boom`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_033`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `formwork climbing system`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_034`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_035`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_036`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `aerial work platform boom`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_037`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `formwork climbing system`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_038`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `tower crane luffing jib`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_039`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `lattice boom crawler crane`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_040`

- status: `weak_motion`
- motion_type: `dolly`
- reference_subject: `aerial work platform boom`
- core_scenario: `factory perimeter wire fence broken by external impact with a visible gap in the restricted boundary`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5x
```

### `vsec_041`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_042`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_043`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `pressure vessel farm`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_044`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `solvent extraction battery`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_045`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_046`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_047`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `pressure vessel farm`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_048`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `solvent extraction battery`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_049`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_050`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_051`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `pressure vessel farm`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_052`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `solvent extraction battery`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_053`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_054`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_055`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `pressure vessel farm`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_056`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `solvent extraction battery`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_057`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `piping manifold`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_058`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `chemical storage tanks`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_059`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `pressure vessel farm`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_060`

- status: `weak_motion`
- motion_type: `pan`
- reference_subject: `solvent extraction battery`
- core_scenario: `unknown chemical liquid leaking and spreading across a dangerous-goods loading zone`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45°
```

### `vsec_061`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `assembly line`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_062`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `server rack row in data center`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_063`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `concrete batching plant`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_064`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic welding cell`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_065`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `assembly line`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_066`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `server rack row in data center`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_067`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `concrete batching plant`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_068`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic welding cell`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_069`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `assembly line`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_070`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `server rack row in data center`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_071`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `concrete batching plant`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_072`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic welding cell`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_073`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `assembly line`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_074`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `server rack row in data center`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_075`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `concrete batching plant`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_076`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic welding cell`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_077`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `assembly line`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_078`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `server rack row in data center`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_079`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `concrete batching plant`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_080`

- status: `weak_motion`
- motion_type: `orbit`
- reference_subject: `robotic welding cell`
- core_scenario: `surveillance camera sweeping across a large blind spot near a restricted area`
- 问题：
  - only generic target (subject/defect/leak), no named parts in view
  - reference subject not tied to motion/framing clause
  - only Reference subject names equipment; motion clause does not say which parts stay visible
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75°
```

### `vsec_081`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `aerial work platform boom`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_082`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_083`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `veh 008`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_084`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `mobile crane outrigger system`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_085`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `aerial work platform boom`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_086`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_087`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `veh 008`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_088`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `mobile crane outrigger system`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_089`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `aerial work platform boom`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_090`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_091`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `veh 008`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_092`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `mobile crane outrigger system`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_093`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `aerial work platform boom`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_094`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_095`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `veh 008`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_096`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `mobile crane outrigger system`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_097`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `aerial work platform boom`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_098`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `assembly line`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_099`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `veh 008`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

### `vsec_100`

- status: `fail_motion`
- motion_type: `static`
- reference_subject: `mobile crane outrigger system`
- core_scenario: `unregistered social vehicle entering a no-parking restricted zone or a worker at height missing a safety helmet`
- 问题：
  - motion clause has no structural visibility description
  - reference subject not tied to motion/framing clause
  - prompt lacks scenario-specific structural visibility (what components remain in frame)
  - generic geometric-integrity boilerplate mentions members/joints but is not a shot-framing spec
- motion 段落：
```text
hold a fixed monitoring view; no camera movement; the scene state must still evolve according to the safety or emergency trigger
```

## 建议改写方向（供人工处理）

在 **Motion requirement** 中补充与 `Reference subject` 对应的可见部件，例如：

- `...orbit 45° while keeping the luffing jib, hook block, and load line in frame`
- `...dolly in 1.5x toward the defect while keeping surrounding truss bays visible`

改写后请更新 `samples.json` 并在此目录追加新的变更日志（若需要）。
