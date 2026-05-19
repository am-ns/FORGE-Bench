# Prompt 运动动词质检（可能不合格样本）

## 检查说明

- 数据源：`dataset/annotations/samples.json` → **`prompt`**
- 重点段落：`Motion requirement / viewpoint motion fidelity:`
- 期望动词：**orbit / pan / dolly / crane**（与 `motion_type` 一致）
- 另参考：量化是否写清（如 45°/90°/2x）、运动描述是否说明可见结构

- 审计时间（UTC）：2026-05-18T15:28:03.091921+00:00
- 样本总数：**486**
- `static` 样本（不参与 orbit/pan/dolly/crane 动词检查）：**86**
- 数据集内 `motion_type=crane` 样本数：**0**
- 标记为可能不合格：**400**
  - 高优先级：**51**
  - 中优先级：**349**
  - 低优先级：**0**

## 结论摘要

1. **未发现** motion 段落完全缺少 orbit/pan/dolly 的情况（`static` 除外）。
2. **全库未使用** `motion_type=crane`，也无 prompt 中的相机 **crane** 运镜描述。
3. **主要风险**：
   - 量化仅写 `target motion value 45.0/75.0/1.5`，未写 °/deg/x；
   - motion 段落几乎无「哪些部件应保持在画面中」的结构可见性描述；
   - 参考主体名含 **crane**（塔吊/岸桥等设备）时，易与相机 crane 运镜混淆。

## 问题类型统计

| 问题描述 | 样本数 |
|----------|--------:|
| quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x) | 400 |
| motion clause lacks structural visibility (which parts stay in view) | 400 |
| verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative | 201 |
| pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec | 103 |
| reference subject names crane equipment; camera verb may be confused with subject identity | 51 |

## 可能不合格 task_id（去重汇总）

```text
emerg_003, emerg_007, emerg_011, emerg_015, emerg_019, emerg_023, emerg_027, emerg_031, hload_002, hload_003, hload_006, hload_007, hload_010, hload_011, hload_014, hload_015, hload_018, hload_019, hload_022, hload_023, hload_026, hload_027, hload_030, hload_031, hload_034, hload_035, hload_038, hload_039, hload_042, hload_043, hload_046, hload_047, hload_050, hload_078, hload_081, hload_084, hload_087, hload_090, hload_093, hload_096, hload_099, vsec_022, vsec_023, vsec_026, vsec_027, vsec_030, vsec_031, vsec_034, vsec_035, vsec_038, vsec_039, emerg_001, emerg_002, emerg_004, emerg_005, emerg_006, emerg_008, emerg_009, emerg_010, emerg_012, emerg_013, emerg_014, emerg_016, emerg_017, emerg_018, emerg_020, emerg_021, emerg_022, emerg_024, emerg_025, emerg_026, emerg_028, emerg_029, emerg_030, emerg_032, emerg_033, emerg_034, emerg_035, emerg_036, emerg_037, emerg_038, emerg_039, emerg_040, emerg_041, emerg_042, emerg_043, emerg_044, emerg_045, emerg_046, emerg_047, emerg_048, emerg_049, emerg_050, emerg_051, emerg_052, emerg_053, emerg_054, emerg_055, emerg_056, emerg_057, emerg_058, emerg_059, emerg_060, emerg_061, emerg_062, emerg_063, emerg_064, emerg_065, emerg_066, emerg_067, erob_001, erob_002, erob_004, erob_005, erob_006, erob_008, erob_009, erob_010, erob_012, erob_013, erob_014, erob_016, erob_017, erob_018, erob_020, erob_021, erob_022, erob_024, erob_025, erob_026, erob_028, erob_029, erob_030, erob_032, erob_033, erob_034, erob_035, erob_036, erob_037, erob_038, erob_039, erob_040, erob_041, erob_042, erob_043, erob_044, erob_045, erob_046, erob_047, erob_048, erob_049, erob_050, erob_051, erob_052, erob_053, erob_054, erob_055, erob_056, erob_057, erob_058, erob_059, erob_060, erob_061, erob_062, erob_063, erob_064, erob_065, erob_066, erob_067, hload_001, hload_004, hload_005, hload_008, hload_009, hload_012, hload_013, hload_016, hload_017, hload_020, hload_021, hload_024, hload_025, hload_028, hload_029, hload_032, hload_033, hload_036, hload_037, hload_040, hload_041, hload_044, hload_045, hload_048, hload_049, hload_051, hload_052, hload_053, hload_054, hload_055, hload_056, hload_057, hload_058, hload_059, hload_060, hload_061, hload_062, hload_063, hload_064, hload_065, hload_066, hload_067, hload_068, hload_069, hload_070, hload_071, hload_072, hload_073, hload_074, hload_075, hload_076, hload_077, hload_079, hload_080, hload_082, hload_083, hload_085, hload_086, hload_088, hload_089, hload_091, hload_092, hload_094, hload_095, hload_097, hload_098, hload_100, pdef_001, pdef_002, pdef_003, pdef_004, pdef_005, pdef_006, pdef_007, pdef_008, pdef_009, pdef_010, pdef_011, pdef_012, pdef_013, pdef_014, pdef_015, pdef_016, pdef_017, pdef_018, pdef_019, pdef_020, pdef_021, pdef_022, pdef_023, pdef_024, pdef_025, pdef_026, pdef_027, pdef_028, pdef_030, pdef_031, pdef_032, pdef_034, pdef_035, pdef_036, pdef_038, pdef_039, pdef_040, pdef_042, pdef_043, pdef_044, pdef_046, pdef_047, pdef_048, pdef_050, pdef_051, pdef_052, pdef_053, pdef_054, pdef_055, pdef_056, pdef_057, pdef_058, pdef_059, pdef_060, pdef_061, pdef_062, pdef_063, pdef_064, pdef_065, pdef_066, pdef_067, pdef_068, pdef_069, pdef_070, pdef_071, pdef_072, pdef_073, pdef_074, pdef_075, pdef_076, pdef_077, pdef_078, pdef_079, pdef_080, pdef_081, pdef_082, pdef_083, pdef_084, pdef_085, pdef_086, pdef_087, pdef_088, pdef_089, pdef_090, pdef_091, pdef_092, pdef_093, pdef_094, pdef_095, pdef_096, pdef_097, pdef_098, pdef_099, pdef_100, vsec_001, vsec_002, vsec_003, vsec_004, vsec_005, vsec_006, vsec_007, vsec_008, vsec_009, vsec_010, vsec_011, vsec_012, vsec_013, vsec_014, vsec_015, vsec_016, vsec_017, vsec_018, vsec_019, vsec_020, vsec_021, vsec_024, vsec_025, vsec_028, vsec_029, vsec_032, vsec_033, vsec_036, vsec_037, vsec_040, vsec_041, vsec_042, vsec_043, vsec_044, vsec_045, vsec_046, vsec_047, vsec_048, vsec_049, vsec_050, vsec_051, vsec_052, vsec_053, vsec_054, vsec_055, vsec_056, vsec_057, vsec_058, vsec_059, vsec_060, vsec_061, vsec_062, vsec_063, vsec_064, vsec_065, vsec_066, vsec_067, vsec_068, vsec_069, vsec_070, vsec_071, vsec_072, vsec_073, vsec_074, vsec_075, vsec_076, vsec_077, vsec_078, vsec_079, vsec_080
```

### 高优先级

```text
emerg_003, emerg_007, emerg_011, emerg_015, emerg_019, emerg_023, emerg_027, emerg_031, hload_002, hload_003, hload_006, hload_007, hload_010, hload_011, hload_014, hload_015, hload_018, hload_019, hload_022, hload_023, hload_026, hload_027, hload_030, hload_031, hload_034, hload_035, hload_038, hload_039, hload_042, hload_043, hload_046, hload_047, hload_050, hload_078, hload_081, hload_084, hload_087, hload_090, hload_093, hload_096, hload_099, vsec_022, vsec_023, vsec_026, vsec_027, vsec_030, vsec_031, vsec_034, vsec_035, vsec_038, vsec_039
```

### 中优先级

```text
emerg_001, emerg_002, emerg_004, emerg_005, emerg_006, emerg_008, emerg_009, emerg_010, emerg_012, emerg_013, emerg_014, emerg_016, emerg_017, emerg_018, emerg_020, emerg_021, emerg_022, emerg_024, emerg_025, emerg_026, emerg_028, emerg_029, emerg_030, emerg_032, emerg_033, emerg_034, emerg_035, emerg_036, emerg_037, emerg_038, emerg_039, emerg_040, emerg_041, emerg_042, emerg_043, emerg_044, emerg_045, emerg_046, emerg_047, emerg_048, emerg_049, emerg_050, emerg_051, emerg_052, emerg_053, emerg_054, emerg_055, emerg_056, emerg_057, emerg_058, emerg_059, emerg_060, emerg_061, emerg_062, emerg_063, emerg_064, emerg_065, emerg_066, emerg_067, erob_001, erob_002, erob_004, erob_005, erob_006, erob_008, erob_009, erob_010, erob_012, erob_013, erob_014, erob_016, erob_017, erob_018, erob_020, erob_021, erob_022, erob_024, erob_025, erob_026, erob_028, erob_029, erob_030, erob_032, erob_033, erob_034, erob_035, erob_036, erob_037, erob_038, erob_039, erob_040, erob_041, erob_042, erob_043, erob_044, erob_045, erob_046, erob_047, erob_048, erob_049, erob_050, erob_051, erob_052, erob_053, erob_054, erob_055, erob_056, erob_057, erob_058, erob_059, erob_060, erob_061, erob_062, erob_063, erob_064, erob_065, erob_066, erob_067, hload_001, hload_004, hload_005, hload_008, hload_009, hload_012, hload_013, hload_016, hload_017, hload_020, hload_021, hload_024, hload_025, hload_028, hload_029, hload_032, hload_033, hload_036, hload_037, hload_040, hload_041, hload_044, hload_045, hload_048, hload_049, hload_051, hload_052, hload_053, hload_054, hload_055, hload_056, hload_057, hload_058, hload_059, hload_060, hload_061, hload_062, hload_063, hload_064, hload_065, hload_066, hload_067, hload_068, hload_069, hload_070, hload_071, hload_072, hload_073, hload_074, hload_075, hload_076, hload_077, hload_079, hload_080, hload_082, hload_083, hload_085, hload_086, hload_088, hload_089, hload_091, hload_092, hload_094, hload_095, hload_097, hload_098, hload_100, pdef_001, pdef_002, pdef_003, pdef_004, pdef_005, pdef_006, pdef_007, pdef_008, pdef_009, pdef_010, pdef_011, pdef_012, pdef_013, pdef_014, pdef_015, pdef_016, pdef_017, pdef_018, pdef_019, pdef_020, pdef_021, pdef_022, pdef_023, pdef_024, pdef_025, pdef_026, pdef_027, pdef_028, pdef_030, pdef_031, pdef_032, pdef_034, pdef_035, pdef_036, pdef_038, pdef_039, pdef_040, pdef_042, pdef_043, pdef_044, pdef_046, pdef_047, pdef_048, pdef_050, pdef_051, pdef_052, pdef_053, pdef_054, pdef_055, pdef_056, pdef_057, pdef_058, pdef_059, pdef_060, pdef_061, pdef_062, pdef_063, pdef_064, pdef_065, pdef_066, pdef_067, pdef_068, pdef_069, pdef_070, pdef_071, pdef_072, pdef_073, pdef_074, pdef_075, pdef_076, pdef_077, pdef_078, pdef_079, pdef_080, pdef_081, pdef_082, pdef_083, pdef_084, pdef_085, pdef_086, pdef_087, pdef_088, pdef_089, pdef_090, pdef_091, pdef_092, pdef_093, pdef_094, pdef_095, pdef_096, pdef_097, pdef_098, pdef_099, pdef_100, vsec_001, vsec_002, vsec_003, vsec_004, vsec_005, vsec_006, vsec_007, vsec_008, vsec_009, vsec_010, vsec_011, vsec_012, vsec_013, vsec_014, vsec_015, vsec_016, vsec_017, vsec_018, vsec_019, vsec_020, vsec_021, vsec_024, vsec_025, vsec_028, vsec_029, vsec_032, vsec_033, vsec_036, vsec_037, vsec_040, vsec_041, vsec_042, vsec_043, vsec_044, vsec_045, vsec_046, vsec_047, vsec_048, vsec_049, vsec_050, vsec_051, vsec_052, vsec_053, vsec_054, vsec_055, vsec_056, vsec_057, vsec_058, vsec_059, vsec_060, vsec_061, vsec_062, vsec_063, vsec_064, vsec_065, vsec_066, vsec_067, vsec_068, vsec_069, vsec_070, vsec_071, vsec_072, vsec_073, vsec_074, vsec_075, vsec_076, vsec_077, vsec_078, vsec_079, vsec_080
```

### 低优先级

```text
(无)
```

## 按问题类型分组

### motion clause lacks structural visibility (which parts stay in view)

共 **400** 条：`emerg_003`, `emerg_007`, `emerg_011`, `emerg_015`, `emerg_019`, `emerg_023`, `emerg_027`, `emerg_031`, `hload_002`, `hload_003`, `hload_006`, `hload_007`, `hload_010`, `hload_011`, `hload_014`, `hload_015`, `hload_018`, `hload_019`, `hload_022`, `hload_023`, `hload_026`, `hload_027`, `hload_030`, `hload_031`, `hload_034`, `hload_035`, `hload_038`, `hload_039`, `hload_042`, `hload_043`, `hload_046`, `hload_047`, `hload_050`, `hload_078`, `hload_081`, `hload_084`, `hload_087`, `hload_090`, `hload_093`, `hload_096`, `hload_099`, `vsec_022`, `vsec_023`, `vsec_026`, `vsec_027`, `vsec_030`, `vsec_031`, `vsec_034`, `vsec_035`, `vsec_038`, `vsec_039`, `emerg_001`, `emerg_002`, `emerg_004`, `emerg_005`, `emerg_006`, `emerg_008`, `emerg_009`, `emerg_010`, `emerg_012`, `emerg_013`, `emerg_014`, `emerg_016`, `emerg_017`, `emerg_018`, `emerg_020`, `emerg_021`, `emerg_022`, `emerg_024`, `emerg_025`, `emerg_026`, `emerg_028`, `emerg_029`, `emerg_030`, `emerg_032`, `emerg_033`, `emerg_034`, `emerg_035`, `emerg_036`, `emerg_037`, `emerg_038`, `emerg_039`, `emerg_040`, `emerg_041`, `emerg_042`, `emerg_043`, `emerg_044`, `emerg_045`, `emerg_046`, `emerg_047`, `emerg_048`, `emerg_049`, `emerg_050`, `emerg_051`, `emerg_052`, `emerg_053`, `emerg_054`, `emerg_055`, `emerg_056`, `emerg_057`, `emerg_058`, `emerg_059`, `emerg_060`, `emerg_061`, `emerg_062`, `emerg_063`, `emerg_064`, `emerg_065`, `emerg_066`, `emerg_067`, `erob_001`, `erob_002`, `erob_004`, `erob_005`, `erob_006`, `erob_008`, `erob_009`, `erob_010`, `erob_012`, `erob_013`, `erob_014`, `erob_016`, `erob_017`, `erob_018`, `erob_020`, `erob_021`, `erob_022`, `erob_024`, `erob_025`, `erob_026`, `erob_028`, `erob_029`, `erob_030`, `erob_032`, `erob_033`, `erob_034`, `erob_035`, `erob_036`, `erob_037`, `erob_038`, `erob_039`, `erob_040`, `erob_041`, `erob_042`, `erob_043`, `erob_044`, `erob_045`, `erob_046`, `erob_047`, `erob_048`, `erob_049`, `erob_050`, `erob_051`, `erob_052`, `erob_053`, `erob_054`, `erob_055`, `erob_056`, `erob_057`, `erob_058`, `erob_059`, `erob_060`, `erob_061`, `erob_062`, `erob_063`, `erob_064`, `erob_065`, `erob_066`, `erob_067`, `hload_001`, `hload_004`, `hload_005`, `hload_008`, `hload_009`, `hload_012`, `hload_013`, `hload_016`, `hload_017`, `hload_020`, `hload_021`, `hload_024`, `hload_025`, `hload_028`, `hload_029`, `hload_032`, `hload_033`, `hload_036`, `hload_037`, `hload_040`, `hload_041`, `hload_044`, `hload_045`, `hload_048`, `hload_049`, `hload_051`, `hload_052`, `hload_053`, `hload_054`, `hload_055`, `hload_056`, `hload_057`, `hload_058`, `hload_059`, `hload_060`, `hload_061`, `hload_062`, `hload_063`, `hload_064`, `hload_065`, `hload_066`, `hload_067`, `hload_068`, `hload_069`, `hload_070`, `hload_071`, `hload_072`, `hload_073`, `hload_074`, `hload_075`, `hload_076`, `hload_077`, `hload_079`, `hload_080`, `hload_082`, `hload_083`, `hload_085`, `hload_086`, `hload_088`, `hload_089`, `hload_091`, `hload_092`, `hload_094`, `hload_095`, `hload_097`, `hload_098`, `hload_100`, `pdef_001`, `pdef_002`, `pdef_003`, `pdef_004`, `pdef_005`, `pdef_006`, `pdef_007`, `pdef_008`, `pdef_009`, `pdef_010`, `pdef_011`, `pdef_012`, `pdef_013`, `pdef_014`, `pdef_015`, `pdef_016`, `pdef_017`, `pdef_018`, `pdef_019`, `pdef_020`, `pdef_021`, `pdef_022`, `pdef_023`, `pdef_024`, `pdef_025`, `pdef_026`, `pdef_027`, `pdef_028`, `pdef_030`, `pdef_031`, `pdef_032`, `pdef_034`, `pdef_035`, `pdef_036`, `pdef_038`, `pdef_039`, `pdef_040`, `pdef_042`, `pdef_043`, `pdef_044`, `pdef_046`, `pdef_047`, `pdef_048`, `pdef_050`, `pdef_051`, `pdef_052`, `pdef_053`, `pdef_054`, `pdef_055`, `pdef_056`, `pdef_057`, `pdef_058`, `pdef_059`, `pdef_060`, `pdef_061`, `pdef_062`, `pdef_063`, `pdef_064`, `pdef_065`, `pdef_066`, `pdef_067`, `pdef_068`, `pdef_069`, `pdef_070`, `pdef_071`, `pdef_072`, `pdef_073`, `pdef_074`, `pdef_075`, `pdef_076`, `pdef_077`, `pdef_078`, `pdef_079`, `pdef_080`, `pdef_081`, `pdef_082`, `pdef_083`, `pdef_084`, `pdef_085`, `pdef_086`, `pdef_087`, `pdef_088`, `pdef_089`, `pdef_090`, `pdef_091`, `pdef_092`, `pdef_093`, `pdef_094`, `pdef_095`, `pdef_096`, `pdef_097`, `pdef_098`, `pdef_099`, `pdef_100`, `vsec_001`, `vsec_002`, `vsec_003`, `vsec_004`, `vsec_005`, `vsec_006`, `vsec_007`, `vsec_008`, `vsec_009`, `vsec_010`, `vsec_011`, `vsec_012`, `vsec_013`, `vsec_014`, `vsec_015`, `vsec_016`, `vsec_017`, `vsec_018`, `vsec_019`, `vsec_020`, `vsec_021`, `vsec_024`, `vsec_025`, `vsec_028`, `vsec_029`, `vsec_032`, `vsec_033`, `vsec_036`, `vsec_037`, `vsec_040`, `vsec_041`, `vsec_042`, `vsec_043`, `vsec_044`, `vsec_045`, `vsec_046`, `vsec_047`, `vsec_048`, `vsec_049`, `vsec_050`, `vsec_051`, `vsec_052`, `vsec_053`, `vsec_054`, `vsec_055`, `vsec_056`, `vsec_057`, `vsec_058`, `vsec_059`, `vsec_060`, `vsec_061`, `vsec_062`, `vsec_063`, `vsec_064`, `vsec_065`, `vsec_066`, `vsec_067`, `vsec_068`, `vsec_069`, `vsec_070`, `vsec_071`, `vsec_072`, `vsec_073`, `vsec_074`, `vsec_075`, `vsec_076`, `vsec_077`, `vsec_078`, `vsec_079`, `vsec_080`

### quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)

共 **400** 条：`emerg_003`, `emerg_007`, `emerg_011`, `emerg_015`, `emerg_019`, `emerg_023`, `emerg_027`, `emerg_031`, `hload_002`, `hload_003`, `hload_006`, `hload_007`, `hload_010`, `hload_011`, `hload_014`, `hload_015`, `hload_018`, `hload_019`, `hload_022`, `hload_023`, `hload_026`, `hload_027`, `hload_030`, `hload_031`, `hload_034`, `hload_035`, `hload_038`, `hload_039`, `hload_042`, `hload_043`, `hload_046`, `hload_047`, `hload_050`, `hload_078`, `hload_081`, `hload_084`, `hload_087`, `hload_090`, `hload_093`, `hload_096`, `hload_099`, `vsec_022`, `vsec_023`, `vsec_026`, `vsec_027`, `vsec_030`, `vsec_031`, `vsec_034`, `vsec_035`, `vsec_038`, `vsec_039`, `emerg_001`, `emerg_002`, `emerg_004`, `emerg_005`, `emerg_006`, `emerg_008`, `emerg_009`, `emerg_010`, `emerg_012`, `emerg_013`, `emerg_014`, `emerg_016`, `emerg_017`, `emerg_018`, `emerg_020`, `emerg_021`, `emerg_022`, `emerg_024`, `emerg_025`, `emerg_026`, `emerg_028`, `emerg_029`, `emerg_030`, `emerg_032`, `emerg_033`, `emerg_034`, `emerg_035`, `emerg_036`, `emerg_037`, `emerg_038`, `emerg_039`, `emerg_040`, `emerg_041`, `emerg_042`, `emerg_043`, `emerg_044`, `emerg_045`, `emerg_046`, `emerg_047`, `emerg_048`, `emerg_049`, `emerg_050`, `emerg_051`, `emerg_052`, `emerg_053`, `emerg_054`, `emerg_055`, `emerg_056`, `emerg_057`, `emerg_058`, `emerg_059`, `emerg_060`, `emerg_061`, `emerg_062`, `emerg_063`, `emerg_064`, `emerg_065`, `emerg_066`, `emerg_067`, `erob_001`, `erob_002`, `erob_004`, `erob_005`, `erob_006`, `erob_008`, `erob_009`, `erob_010`, `erob_012`, `erob_013`, `erob_014`, `erob_016`, `erob_017`, `erob_018`, `erob_020`, `erob_021`, `erob_022`, `erob_024`, `erob_025`, `erob_026`, `erob_028`, `erob_029`, `erob_030`, `erob_032`, `erob_033`, `erob_034`, `erob_035`, `erob_036`, `erob_037`, `erob_038`, `erob_039`, `erob_040`, `erob_041`, `erob_042`, `erob_043`, `erob_044`, `erob_045`, `erob_046`, `erob_047`, `erob_048`, `erob_049`, `erob_050`, `erob_051`, `erob_052`, `erob_053`, `erob_054`, `erob_055`, `erob_056`, `erob_057`, `erob_058`, `erob_059`, `erob_060`, `erob_061`, `erob_062`, `erob_063`, `erob_064`, `erob_065`, `erob_066`, `erob_067`, `hload_001`, `hload_004`, `hload_005`, `hload_008`, `hload_009`, `hload_012`, `hload_013`, `hload_016`, `hload_017`, `hload_020`, `hload_021`, `hload_024`, `hload_025`, `hload_028`, `hload_029`, `hload_032`, `hload_033`, `hload_036`, `hload_037`, `hload_040`, `hload_041`, `hload_044`, `hload_045`, `hload_048`, `hload_049`, `hload_051`, `hload_052`, `hload_053`, `hload_054`, `hload_055`, `hload_056`, `hload_057`, `hload_058`, `hload_059`, `hload_060`, `hload_061`, `hload_062`, `hload_063`, `hload_064`, `hload_065`, `hload_066`, `hload_067`, `hload_068`, `hload_069`, `hload_070`, `hload_071`, `hload_072`, `hload_073`, `hload_074`, `hload_075`, `hload_076`, `hload_077`, `hload_079`, `hload_080`, `hload_082`, `hload_083`, `hload_085`, `hload_086`, `hload_088`, `hload_089`, `hload_091`, `hload_092`, `hload_094`, `hload_095`, `hload_097`, `hload_098`, `hload_100`, `pdef_001`, `pdef_002`, `pdef_003`, `pdef_004`, `pdef_005`, `pdef_006`, `pdef_007`, `pdef_008`, `pdef_009`, `pdef_010`, `pdef_011`, `pdef_012`, `pdef_013`, `pdef_014`, `pdef_015`, `pdef_016`, `pdef_017`, `pdef_018`, `pdef_019`, `pdef_020`, `pdef_021`, `pdef_022`, `pdef_023`, `pdef_024`, `pdef_025`, `pdef_026`, `pdef_027`, `pdef_028`, `pdef_030`, `pdef_031`, `pdef_032`, `pdef_034`, `pdef_035`, `pdef_036`, `pdef_038`, `pdef_039`, `pdef_040`, `pdef_042`, `pdef_043`, `pdef_044`, `pdef_046`, `pdef_047`, `pdef_048`, `pdef_050`, `pdef_051`, `pdef_052`, `pdef_053`, `pdef_054`, `pdef_055`, `pdef_056`, `pdef_057`, `pdef_058`, `pdef_059`, `pdef_060`, `pdef_061`, `pdef_062`, `pdef_063`, `pdef_064`, `pdef_065`, `pdef_066`, `pdef_067`, `pdef_068`, `pdef_069`, `pdef_070`, `pdef_071`, `pdef_072`, `pdef_073`, `pdef_074`, `pdef_075`, `pdef_076`, `pdef_077`, `pdef_078`, `pdef_079`, `pdef_080`, `pdef_081`, `pdef_082`, `pdef_083`, `pdef_084`, `pdef_085`, `pdef_086`, `pdef_087`, `pdef_088`, `pdef_089`, `pdef_090`, `pdef_091`, `pdef_092`, `pdef_093`, `pdef_094`, `pdef_095`, `pdef_096`, `pdef_097`, `pdef_098`, `pdef_099`, `pdef_100`, `vsec_001`, `vsec_002`, `vsec_003`, `vsec_004`, `vsec_005`, `vsec_006`, `vsec_007`, `vsec_008`, `vsec_009`, `vsec_010`, `vsec_011`, `vsec_012`, `vsec_013`, `vsec_014`, `vsec_015`, `vsec_016`, `vsec_017`, `vsec_018`, `vsec_019`, `vsec_020`, `vsec_021`, `vsec_024`, `vsec_025`, `vsec_028`, `vsec_029`, `vsec_032`, `vsec_033`, `vsec_036`, `vsec_037`, `vsec_040`, `vsec_041`, `vsec_042`, `vsec_043`, `vsec_044`, `vsec_045`, `vsec_046`, `vsec_047`, `vsec_048`, `vsec_049`, `vsec_050`, `vsec_051`, `vsec_052`, `vsec_053`, `vsec_054`, `vsec_055`, `vsec_056`, `vsec_057`, `vsec_058`, `vsec_059`, `vsec_060`, `vsec_061`, `vsec_062`, `vsec_063`, `vsec_064`, `vsec_065`, `vsec_066`, `vsec_067`, `vsec_068`, `vsec_069`, `vsec_070`, `vsec_071`, `vsec_072`, `vsec_073`, `vsec_074`, `vsec_075`, `vsec_076`, `vsec_077`, `vsec_078`, `vsec_079`, `vsec_080`

### verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative

共 **201** 条：`emerg_003`, `emerg_007`, `emerg_011`, `emerg_015`, `emerg_019`, `emerg_023`, `emerg_027`, `emerg_031`, `hload_026`, `hload_027`, `hload_030`, `hload_031`, `hload_034`, `hload_035`, `hload_038`, `hload_039`, `hload_042`, `hload_043`, `hload_046`, `hload_047`, `hload_050`, `vsec_022`, `vsec_023`, `vsec_026`, `vsec_027`, `vsec_030`, `vsec_031`, `vsec_034`, `vsec_035`, `vsec_038`, `vsec_039`, `emerg_001`, `emerg_002`, `emerg_004`, `emerg_005`, `emerg_006`, `emerg_008`, `emerg_009`, `emerg_010`, `emerg_012`, `emerg_013`, `emerg_014`, `emerg_016`, `emerg_017`, `emerg_018`, `emerg_020`, `emerg_021`, `emerg_022`, `emerg_024`, `emerg_025`, `emerg_026`, `emerg_028`, `emerg_029`, `emerg_030`, `emerg_032`, `emerg_033`, `emerg_034`, `emerg_035`, `emerg_036`, `emerg_037`, `emerg_038`, `emerg_039`, `emerg_040`, `emerg_041`, `emerg_042`, `emerg_043`, `emerg_044`, `emerg_045`, `emerg_046`, `emerg_047`, `emerg_048`, `emerg_049`, `emerg_050`, `emerg_051`, `emerg_052`, `emerg_053`, `emerg_054`, `emerg_055`, `emerg_056`, `emerg_057`, `emerg_058`, `emerg_059`, `emerg_060`, `emerg_061`, `emerg_062`, `emerg_063`, `emerg_064`, `emerg_065`, `emerg_066`, `emerg_067`, `hload_028`, `hload_029`, `hload_032`, `hload_033`, `hload_036`, `hload_037`, `hload_040`, `hload_041`, `hload_044`, `hload_045`, `hload_048`, `hload_049`, `hload_051`, `hload_052`, `hload_053`, `hload_054`, `hload_055`, `hload_056`, `hload_057`, `hload_058`, `hload_059`, `hload_060`, `hload_061`, `hload_062`, `hload_063`, `hload_064`, `hload_065`, `hload_066`, `hload_067`, `hload_068`, `hload_069`, `hload_070`, `hload_071`, `hload_072`, `hload_073`, `hload_074`, `hload_075`, `pdef_026`, `pdef_027`, `pdef_028`, `pdef_030`, `pdef_031`, `pdef_032`, `pdef_034`, `pdef_035`, `pdef_036`, `pdef_038`, `pdef_039`, `pdef_040`, `pdef_042`, `pdef_043`, `pdef_044`, `pdef_046`, `pdef_047`, `pdef_048`, `pdef_050`, `pdef_051`, `pdef_052`, `pdef_053`, `pdef_054`, `pdef_055`, `pdef_056`, `pdef_057`, `pdef_058`, `pdef_059`, `pdef_060`, `pdef_061`, `pdef_062`, `pdef_063`, `pdef_064`, `pdef_065`, `pdef_066`, `pdef_067`, `pdef_068`, `pdef_069`, `pdef_070`, `pdef_071`, `pdef_072`, `pdef_073`, `pdef_074`, `pdef_075`, `vsec_021`, `vsec_024`, `vsec_025`, `vsec_028`, `vsec_029`, `vsec_032`, `vsec_033`, `vsec_036`, `vsec_037`, `vsec_040`, `vsec_041`, `vsec_042`, `vsec_043`, `vsec_044`, `vsec_045`, `vsec_046`, `vsec_047`, `vsec_048`, `vsec_049`, `vsec_050`, `vsec_051`, `vsec_052`, `vsec_053`, `vsec_054`, `vsec_055`, `vsec_056`, `vsec_057`, `vsec_058`, `vsec_059`, `vsec_060`

### pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec

共 **103** 条：`emerg_035`, `emerg_036`, `emerg_037`, `emerg_038`, `emerg_039`, `emerg_040`, `emerg_041`, `emerg_042`, `emerg_043`, `emerg_044`, `emerg_045`, `emerg_046`, `emerg_047`, `emerg_048`, `emerg_049`, `emerg_050`, `emerg_051`, `emerg_052`, `emerg_053`, `emerg_054`, `emerg_055`, `emerg_056`, `emerg_057`, `emerg_058`, `emerg_059`, `emerg_060`, `emerg_061`, `emerg_062`, `emerg_063`, `emerg_064`, `emerg_065`, `emerg_066`, `emerg_067`, `hload_051`, `hload_052`, `hload_053`, `hload_054`, `hload_055`, `hload_056`, `hload_057`, `hload_058`, `hload_059`, `hload_060`, `hload_061`, `hload_062`, `hload_063`, `hload_064`, `hload_065`, `hload_066`, `hload_067`, `hload_068`, `hload_069`, `hload_070`, `hload_071`, `hload_072`, `hload_073`, `hload_074`, `hload_075`, `pdef_051`, `pdef_052`, `pdef_053`, `pdef_054`, `pdef_055`, `pdef_056`, `pdef_057`, `pdef_058`, `pdef_059`, `pdef_060`, `pdef_061`, `pdef_062`, `pdef_063`, `pdef_064`, `pdef_065`, `pdef_066`, `pdef_067`, `pdef_068`, `pdef_069`, `pdef_070`, `pdef_071`, `pdef_072`, `pdef_073`, `pdef_074`, `pdef_075`, `vsec_041`, `vsec_042`, `vsec_043`, `vsec_044`, `vsec_045`, `vsec_046`, `vsec_047`, `vsec_048`, `vsec_049`, `vsec_050`, `vsec_051`, `vsec_052`, `vsec_053`, `vsec_054`, `vsec_055`, `vsec_056`, `vsec_057`, `vsec_058`, `vsec_059`, `vsec_060`

### reference subject names crane equipment; camera verb may be confused with subject identity

共 **51** 条：`emerg_003`, `emerg_007`, `emerg_011`, `emerg_015`, `emerg_019`, `emerg_023`, `emerg_027`, `emerg_031`, `hload_002`, `hload_003`, `hload_006`, `hload_007`, `hload_010`, `hload_011`, `hload_014`, `hload_015`, `hload_018`, `hload_019`, `hload_022`, `hload_023`, `hload_026`, `hload_027`, `hload_030`, `hload_031`, `hload_034`, `hload_035`, `hload_038`, `hload_039`, `hload_042`, `hload_043`, `hload_046`, `hload_047`, `hload_050`, `hload_078`, `hload_081`, `hload_084`, `hload_087`, `hload_090`, `hload_093`, `hload_096`, `hload_099`, `vsec_022`, `vsec_023`, `vsec_026`, `vsec_027`, `vsec_030`, `vsec_031`, `vsec_034`, `vsec_035`, `vsec_038`, `vsec_039`


## 逐条详情

### `emerg_003` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_007` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_011` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_015` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_019` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_023` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_027` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_031` — high

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_002` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_003` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_006` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_007` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_010` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_011` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_014` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_015` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_018` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_019` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_022` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_023` — high

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `mobile crane telescoping`
- image_path: `dataset/images/construction/mobile_crane_telescoping.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_026` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_027` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_030` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_031` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_034` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_035` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_038` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_039` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_042` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_043` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_046` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_047` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing`
- image_path: `dataset/images/construction/tower_crane_luffing.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_050` — high

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_078` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_081` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_084` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_087` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_090` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_093` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_096` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_099` — high

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `container terminal quay crane`
- image_path: `dataset/images/maritime/container_terminal_quay_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_022` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_023` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_026` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_027` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_030` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_031` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_034` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_035` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_038` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `tower crane luffing jib`
- image_path: `dataset/images/construction/tower_crane_luffing_jib.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_039` — high

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `lattice boom crawler crane`
- image_path: `dataset/images/construction/lattice_boom_crawler_crane.jpg`
- 可能问题：
  - reference subject names crane equipment; camera verb may be confused with subject identity
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_001` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_002` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_004` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_005` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_006` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_008` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_009` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_010` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_012` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_013` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_014` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_016` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_017` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_018` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_020` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_021` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_022` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_024` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_025` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_026` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_028` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_029` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_030` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_032` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_033` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `high voltage transformer yard`
- image_path: `dataset/images/energy_power/high_voltage_transformer_yard.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_034` — medium

- domain: `extreme_emergency`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `wind turbine`
- image_path: `dataset/images/energy_renewable/wind_turbine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `emerg_035` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_036` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_037` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_038` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_039` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_040` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_041` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_042` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_043` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_044` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_045` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_046` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_047` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_048` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_049` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_050` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_051` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_052` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_053` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_054` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_055` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_056` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_057` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_058` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_059` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_060` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_061` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_062` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_063` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_064` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_065` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `offshore oil platform`
- image_path: `dataset/images/oil_gas/offshore_oil_platform.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_066` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `distillation column array`
- image_path: `dataset/images/chemical/distillation_column_array.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `emerg_067` — medium

- domain: `extreme_emergency`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `erob_001` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_002` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_004` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_005` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_006` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_008` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_009` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_010` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_012` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_013` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_014` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_016` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_017` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_018` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_020` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_021` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_022` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_024` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_025` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_026` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_028` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_029` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_030` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_032` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `surgical robot instrument arm`
- image_path: `dataset/images/robotics/surgical_robot_instrument_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_033` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial robot arm`
- image_path: `dataset/images/robotics/industrial_robot_arm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_034` — medium

- domain: `embodied_robotics`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `collaborative robot`
- image_path: `dataset/images/robotics/collaborative_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `erob_035` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_036` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_037` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_038` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_039` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_040` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_041` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_042` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_043` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_044` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_045` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_046` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_047` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_048` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_049` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_050` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_051` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_052` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_053` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_054` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_055` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_056` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_057` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_058` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_059` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_060` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_061` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_062` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_063` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_064` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic pipe crawler`
- image_path: `dataset/images/robotics/robotic_pipe_crawler.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_065` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `snake robot inspection unit`
- image_path: `dataset/images/robotics/snake_robot_inspection_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_066` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `agv fleet navigation unit`
- image_path: `dataset/images/robotics/agv_fleet_navigation_unit.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `erob_067` — medium

- domain: `embodied_robotics`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `autonomous mobile robot`
- image_path: `dataset/images/robotics/autonomous_mobile_robot.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_001` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_004` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_005` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_008` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_009` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_012` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_013` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_016` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_017` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_020` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_021` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_024` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `hydraulic shovel loading`
- image_path: `dataset/images/mining/hydraulic_shovel_loading.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_025` — medium

- domain: `heavy_load_construction`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `excavator`
- image_path: `dataset/images/construction/excavator.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `hload_028` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_029` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_032` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_033` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_036` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_037` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_040` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_041` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_044` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_045` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_048` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `cable laying ship drum`
- image_path: `dataset/images/maritime/cable_laying_ship_drum.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_049` — medium

- domain: `heavy_load_construction`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `mine hoist headframe`
- image_path: `dataset/images/mining/mine_hoist_headframe.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `hload_051` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_052` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_053` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_054` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_055` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_056` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_057` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_058` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_059` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_060` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_061` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_062` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_063` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_064` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_065` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_066` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_067` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_068` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_069` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_070` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_071` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_072` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `tunnel boring machine`
- image_path: `dataset/images/construction/tunnel_boring_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_073` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_074` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `thickener tank farm`
- image_path: `dataset/images/mining/thickener_tank_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_075` — medium

- domain: `heavy_load_construction`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `trenchless pipe jacking machine`
- image_path: `dataset/images/construction/trenchless_pipe_jacking_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `hload_076` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_077` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_079` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_080` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_082` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_083` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_085` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_086` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_088` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_089` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_091` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_092` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_094` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_095` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_097` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_098` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `precast yard stacking gantry`
- image_path: `dataset/images/construction/precast_yard_stacking_gantry.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `hload_100` — medium

- domain: `heavy_load_construction`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `cable stayed bridge deck segment`
- image_path: `dataset/images/construction/cable_stayed_bridge_deck_segment.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_001` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_002` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_003` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_004` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_005` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_006` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_007` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_008` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_009` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_010` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_011` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_012` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_013` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_014` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_015` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_016` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_017` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_018` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_019` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_020` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_021` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_022` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `five axis machining center`
- image_path: `dataset/images/manufacturing/five_axis_machining_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_023` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_024` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_025` — medium

- domain: `precision_defect_gen`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `pdef_026` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_027` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_028` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_030` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_031` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_032` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_034` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_035` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_036` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_038` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_039` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_040` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_042` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_043` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_044` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_046` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_047` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `micro 009`
- image_path: `dataset/images/electronics/micro_009.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_048` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `gear hobbing machine`
- image_path: `dataset/images/manufacturing/gear_hobbing_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_050` — medium

- domain: `precision_defect_gen`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `pcb circuit board`
- image_path: `dataset/images/electronics/pcb_circuit_board.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `pdef_051` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_052` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_053` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_054` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_055` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_056` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_057` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_058` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_059` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_060` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_061` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_062` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_063` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_064` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_065` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_066` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_067` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_068` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_069` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_070` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_071` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_072` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `industrial washing line`
- image_path: `dataset/images/manufacturing/industrial_washing_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_073` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `centrifuge battery`
- image_path: `dataset/images/chemical/centrifuge_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_074` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `automated grinding cell`
- image_path: `dataset/images/manufacturing/automated_grinding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_075` — medium

- domain: `precision_defect_gen`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `cnc machine`
- image_path: `dataset/images/manufacturing/cnc_machine.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `pdef_076` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_077` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_078` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_079` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_080` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_081` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_082` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_083` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_084` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_085` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_086` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_087` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_088` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_089` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_090` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_091` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_092` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_093` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_094` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_095` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_096` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_097` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_098` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_099` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `gas turbine compressor section`
- image_path: `dataset/images/oil_gas/gas_turbine_compressor_section.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `pdef_100` — medium

- domain: `precision_defect_gen`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `heat exchanger bundle`
- image_path: `dataset/images/chemical/heat_exchanger_bundle.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_001` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `veh 014`
- image_path: `dataset/images/construction/veh_014.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_002` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `heavy haul truck`
- image_path: `dataset/images/mining/heavy_haul_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_003` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `road train coupling system`
- image_path: `dataset/images/construction/road_train_coupling_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_004` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `articulated dump truck`
- image_path: `dataset/images/mining/articulated_dump_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_005` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `veh 014`
- image_path: `dataset/images/construction/veh_014.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_006` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `heavy haul truck`
- image_path: `dataset/images/mining/heavy_haul_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_007` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `road train coupling system`
- image_path: `dataset/images/construction/road_train_coupling_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_008` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `articulated dump truck`
- image_path: `dataset/images/mining/articulated_dump_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_009` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `veh 014`
- image_path: `dataset/images/construction/veh_014.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_010` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `heavy haul truck`
- image_path: `dataset/images/mining/heavy_haul_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_011` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `road train coupling system`
- image_path: `dataset/images/construction/road_train_coupling_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_012` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `articulated dump truck`
- image_path: `dataset/images/mining/articulated_dump_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_013` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `veh 014`
- image_path: `dataset/images/construction/veh_014.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_014` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `heavy haul truck`
- image_path: `dataset/images/mining/heavy_haul_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_015` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `road train coupling system`
- image_path: `dataset/images/construction/road_train_coupling_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_016` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `articulated dump truck`
- image_path: `dataset/images/mining/articulated_dump_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_017` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `veh 014`
- image_path: `dataset/images/construction/veh_014.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_018` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `heavy haul truck`
- image_path: `dataset/images/mining/heavy_haul_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_019` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `road train coupling system`
- image_path: `dataset/images/construction/road_train_coupling_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_020` — medium

- domain: `visual_security`
- task_category: `rigid_body_kinematics_and_coupling`
- motion_type: `orbit`
- viewpoint_motion_target: `45.0`
- reference_subject: `articulated dump truck`
- image_path: `dataset/images/mining/articulated_dump_truck.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 45.0
```

### `vsec_021` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `formwork climbing system`
- image_path: `dataset/images/construction/formwork_climbing_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_024` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `aerial work platform boom`
- image_path: `dataset/images/construction/aerial_work_platform_boom.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_025` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `formwork climbing system`
- image_path: `dataset/images/construction/formwork_climbing_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_028` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `aerial work platform boom`
- image_path: `dataset/images/construction/aerial_work_platform_boom.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_029` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `formwork climbing system`
- image_path: `dataset/images/construction/formwork_climbing_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_032` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `aerial work platform boom`
- image_path: `dataset/images/construction/aerial_work_platform_boom.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_033` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `formwork climbing system`
- image_path: `dataset/images/construction/formwork_climbing_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_036` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `aerial work platform boom`
- image_path: `dataset/images/construction/aerial_work_platform_boom.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_037` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `formwork climbing system`
- image_path: `dataset/images/construction/formwork_climbing_system.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_040` — medium

- domain: `visual_security`
- task_category: `topology_mutation_and_failure`
- motion_type: `dolly`
- viewpoint_motion_target: `1.5`
- reference_subject: `aerial work platform boom`
- image_path: `dataset/images/construction/aerial_work_platform_boom.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
- motion 段落：
```text
perform a controlled dolly-in toward the local defect or failure region; target motion value 1.5
```

### `vsec_041` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_042` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_043` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `pressure vessel farm`
- image_path: `dataset/images/chemical/pressure_vessel_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_044` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `solvent extraction battery`
- image_path: `dataset/images/chemical/solvent_extraction_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_045` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_046` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_047` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `pressure vessel farm`
- image_path: `dataset/images/chemical/pressure_vessel_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_048` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `solvent extraction battery`
- image_path: `dataset/images/chemical/solvent_extraction_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_049` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_050` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_051` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `pressure vessel farm`
- image_path: `dataset/images/chemical/pressure_vessel_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_052` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `solvent extraction battery`
- image_path: `dataset/images/chemical/solvent_extraction_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_053` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_054` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_055` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `pressure vessel farm`
- image_path: `dataset/images/chemical/pressure_vessel_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_056` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `solvent extraction battery`
- image_path: `dataset/images/chemical/solvent_extraction_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_057` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `piping manifold`
- image_path: `dataset/images/chemical/piping_manifold.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_058` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `chemical storage tanks`
- image_path: `dataset/images/chemical/chemical_storage_tanks.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_059` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `pressure vessel farm`
- image_path: `dataset/images/chemical/pressure_vessel_farm.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_060` — medium

- domain: `visual_security`
- task_category: `fluid_dynamics_and_thermodynamics`
- motion_type: `pan`
- viewpoint_motion_target: `45.0`
- reference_subject: `solvent extraction battery`
- image_path: `dataset/images/chemical/solvent_extraction_battery.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
  - verb buried in long wrapper (`perform a controlled ...`) rather than direct imperative
  - pan tied to fluid evolution wording; camera path depends on leak motion, not a clean pan spec
- motion 段落：
```text
perform a controlled lateral pan that follows the evolving leak, spray, smoke, flame, or surge; target motion value 45.0
```

### `vsec_061` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `assembly line`
- image_path: `dataset/images/manufacturing/assembly_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_062` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `server rack row in data center`
- image_path: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_063` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `concrete batching plant`
- image_path: `dataset/images/construction/concrete_batching_plant.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_064` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic welding cell`
- image_path: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_065` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `assembly line`
- image_path: `dataset/images/manufacturing/assembly_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_066` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `server rack row in data center`
- image_path: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_067` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `concrete batching plant`
- image_path: `dataset/images/construction/concrete_batching_plant.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_068` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic welding cell`
- image_path: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_069` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `assembly line`
- image_path: `dataset/images/manufacturing/assembly_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_070` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `server rack row in data center`
- image_path: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_071` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `concrete batching plant`
- image_path: `dataset/images/construction/concrete_batching_plant.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_072` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic welding cell`
- image_path: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_073` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `assembly line`
- image_path: `dataset/images/manufacturing/assembly_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_074` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `server rack row in data center`
- image_path: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_075` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `concrete batching plant`
- image_path: `dataset/images/construction/concrete_batching_plant.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_076` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic welding cell`
- image_path: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_077` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `assembly line`
- image_path: `dataset/images/manufacturing/assembly_line.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_078` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `server rack row in data center`
- image_path: `dataset/images/electronics/server_rack_row_in_data_center.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_079` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `concrete batching plant`
- image_path: `dataset/images/construction/concrete_batching_plant.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

### `vsec_080` — medium

- domain: `visual_security`
- task_category: `spatial_exploration_and_viewpoint`
- motion_type: `orbit`
- viewpoint_motion_target: `75.0`
- reference_subject: `robotic welding cell`
- image_path: `dataset/images/manufacturing/robotic_welding_cell.jpg`
- 可能问题：
  - quantified target only as `target motion value` without °/deg/x (e.g. 45°, 90°, 2x)
  - motion clause lacks structural visibility (which parts stay in view)
- motion 段落：
```text
perform a smooth constant-radius orbit around the subject; target motion value 75.0
```

## 备注

本清单为启发式人工复核清单，非自动判定不合格。
`static` 任务使用固定机位描述，未纳入 orbit/pan/dolly/crane 动词缺失类问题。

## 补充：结构可见性复检（文件夹 `5/`）

- 复检时间（UTC）：2026-05-19T10:32:13.085085+00:00
- 检查字段：`prompt`（重点为 **Motion requirement** 段落是否写明取景时应可见的部件/结构）
- 结论：**486 / 486** 条样本在 motion 段落中**缺少**明确的结构可见性描述（仅「around the subject」「local defect region」或仅靠 `Reference subject` 点名设备）。
- 明细与 JSON 备份见：`../5/PROMPT_STRUCTURE_VISIBILITY_AUDIT.md`、`../5/prompt_structure_visibility_audit.json`

说明：全库 `prompt` 的 Geometric integrity 等轴段常出现 “joints / members” 等**评测约束用语**，不计入「运镜时什么部件应在画面中」的结构描述。

