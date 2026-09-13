# FORGE-Bench 正式评分方法（v4.1）

本文件定义唯一可用于主榜排序的分数。旧版 `0.8 × technical + 0.2 × application`、连续可靠度倍率和 `b=15` 仿射变换全部退役，只能作为显式标记的历史诊断量，不能用于排名。

## 1. 六个正式评分轴

对样本 $i$，Judge 分别给出六个 $[0,100]$ 分数：

1. $L_i$：工业逻辑与事实对齐——工业因果、事实、安全规则是否正确。
2. $G_i$：几何完整性——形状、部件、连接关系和拓扑是否稳定。
3. $P_i$：物理合理性——运动、碰撞、流体、受力和材料变化是否合理。
4. $T_i$：时间一致性——身份、状态和演化是否连续，是否跳变、重置或断裂。
5. $R_i$：参考与运动忠实度——是否保留参考图，同时正确执行指定运动。
6. $U_i$：应用有用性——结果对声明的检查、培训、设计或安全用途是否有用。

六轴在主榜中等权。任务类别权重仅保留作技术诊断，不进入正式总分。

## 2. 事件覆盖门控

设 $C_i\in[0,100]$ 为可观察必需事件覆盖率。它不是第七轴，而是六轴共同上限：

$$x^{(0)}_{ik}=\min(x_{ik},C_i),\quad x_{ik}\in\{L_i,G_i,P_i,T_i,R_i,U_i\}.$$

必需事件只完成 35%，六轴都不能高于 35；事件完全未发生时六轴均封顶为 0。没有有效覆盖观测时不凭空生成覆盖率，也不执行此项封顶。

## 3. 算子证据资格

CV 算子必须同时满足：名称在白名单；`used_for_axis_cap=true`；`validity` 为 `valid`（缺省兼容值也接受）；`confidence >= 0.70`。否则只作诊断。

布尔开关只接受 JSON 的 `true`，不接受字符串 `"true"`、`"false"` 或数字 `1`。置信度必须是 `[0,1]` 内有限数值，变化面积比例同样必须在 `[0,1]` 内。正式算子规则由 `scoring.policy.operator_caps` 统一执行，单样本与聚合入口不得各自定义规则。

白名单仅有 `local_region_lock`、`temporal_break`、`rigid_joint_tracking`。每项证据只对指定轴封顶一次；多个上限取最小值，所以执行顺序不影响结果。

## 4. 正式算子封顶

- 全局重生成：`local_region_lock.risk == global_regeneration` 时，$R_i\le35$、$T_i\le45$。
- 大面积非局部变化：合格算子确认变化面积超过 25% 且未进入全局重生成时，$R_i\le50$。
- 突然时间跳变：`temporal_break.abrupt_transition=true` 时，$T_i\le35$。
- 后段突然断裂：同时 `late_break=true` 时，采用更严格的 $T_i\le25$。
- 刚体漂移：`rigid_joint_tracking.risk == rigid_drift` 时，$G_i\le45$。

25% 是“大面积非局部变化”的面积起点；35% 是全局重生成判定使用的更高面积边界。面积是显著变化有效区域占画面（或算子规定区域）的比例，不是“像素值变化 25%”。触发还须满足空间分布、置信度、有效性和白名单条件。

## 5. 唯一正式公式

记应用全部合格上限后的六轴为 $L_i',G_i',P_i',T_i',R_i',U_i'$：

$$S_i=\frac{L_i'+G_i'+P_i'+T_i'+R_i'+U_i'}{6}.$$

模型分为有效完整样本的简单平均：

$$S_{model}=\frac1N\sum_{i=1}^{N}S_i.$$

置信区间按场景 ID 做 cluster bootstrap（默认 1000 次，随机种子 1729）。请求集合只要存在缺失视频、缺轴或不可解析 Judge 输出，运行即不可发布；不得静默只发布完整子集。

## 6. 非排名诊断量

- `technical_score`：五个技术轴的任务类别加权诊断分。
- `linear_ranking_score`：旧版 0.8/0.2 分数，仅供历史对照。
- `constraint_adjusted_score`：兼容字段，v4 中等于 `ranking_score`。
- `motion_gated_score`、`operator_risk_adjusted_score`、`legacy_penalty_adjusted_score`：旧实验或诊断输出。
- reasoning alignment、visual quality、pass rate、task realization：解释性统计，不是第二个排行榜。

规范配置位于 `scoring/forge_v4_config.json`；可执行实现位于 `scoring/per_sample.py` 与 `scoring/aggregate.py`。文档与实现若冲突，应停止发布并修复版本。

## 7. 输入校验与历史缓存迁移

六轴分数和已提供的事件覆盖率必须是 `[0,100]` 内的有限 JSON 数值。布尔值、字符串、NaN、无穷大和越界值不转换、不截断；缺轴或输入无效时，该样本不可用于正式排名，整个请求集合不可发布。

v4.1 的版本号与配置 SHA-256 必须同时匹配。旧缓存使用 `python -m scripts.reaggregate_cached_results <结果目录>` 迁移：从 `raw_axis_scores` 和原始应用 Judge 分数重建六轴，再执行当前封顶规则，更新逐样本结果、聚合与报告。原始逐样本文件保存在 `per_sample.before_v4_migration.json`。缺少原始六轴证据时记录 `scoring_migration_error`，必须重新评审，不能沿用已变换的旧轴分数。

确定性重算不验证视频是否更新，也不重新生成 Judge 证据。视频、参考图或任务发生变更后，仍须按当前评测协议重新评审；旧视频证据不能因重算而成为当前视频的有效成绩。

历史诊断字段保留兼容用途；当前主榜唯一字段为 `ranking_score`。交付包中的源码、规范配置及校验清单必须与当前仓库一致。

分片合并必须按请求任务清单对齐；缺失任务保留为 `missing_shard_result`，禁止静默缩小评测集合。重复任务 ID 的清单直接拒绝。缓存迁移保留已记录的输入错误，必须重新评审才能消除。
