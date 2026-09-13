# FORGE-Bench 全代码说明与运行机制

本文覆盖仓库中的 Python 代码文件。先讲主链，再逐文件说明；`__init__.py` 只负责把目录声明为可导入包，不承担业务计算。

## 一、项目怎样运作

数据流是：`dataset/annotations` 定义任务与参考图 → 各生成脚本按同一 500 个 task ID 产出模型视频 → `eval/run_eval.py` 做预检、抽帧、算子取证和多模态 Judge → `scoring/per_sample.py` 对单样本六轴门控 → `scoring/aggregate.py` 计算模型均值、置信区间和诊断 → `scoring/report.py`、`leaderboard.py` 和论文复现脚本生成发布材料。

正式排名只认六轴门控后算术平均。任务类别权重、旧 0.8/0.2 分数、视觉质量、推理一致率和各种风险分都是诊断项。运行缺视频、缺轴或 Judge 输出不可解析时不可发布。

## 二、数据与总入口

- `dataset/validate.py`：验证标注 JSON 的字段、ID 唯一性、文件引用、类别和数值范围，是改任务后首先运行的数据质量闸门。
- `eval/run_eval.py`：正式评测编排器。解析命令行，定位任务视频，调用预检与视频协议，运行 Judge/算子，组织逐样本记录，再交给 scoring 聚合并落盘。
- `eval/preflight.py`：在昂贵推理之前核对依赖、视频、样本、Judge 配置和输出目录，尽早把整批不可运行的问题暴露出来。
- `eval/video_protocol.py`：统一视频解码、原生帧信息、确定性 2-fps Judge 采样、首尾帧覆盖和接触表构造，保证不同模型接受同一观察协议。
- `eval/metadata.py`：收集运行环境、版本、模型标识、输入摘要等可复现元数据。
- `eval/llm_judge.py`：Judge 抽象与通用请求/解析逻辑，要求结构化六轴评分、理由、失败模式、置信度和证据帧。
- `eval/llm_judge_openai.py`：OpenAI 兼容接口实现，负责消息格式、图像输入、重试和响应规范化。
- `local_video_judge.py`：本地或远端部署 Judge 的独立入口，供主评测器以兼容方式调用。

## 三、轴定义、应用层与证据编排

- `eval/axis_registry.py`：六轴规范名称、别名、技术轴集合、旧任务类别诊断权重和轴解释的中心注册表；避免各脚本自行发明字段名。
- `eval/application_taxonomy.py`：定义检查、维护、安全训练等应用类型及其判定语义。
- `eval/operator_plan.py`：根据任务类别、运动和约束选择应运行的 CV 算子，并描述预期信号。
- `eval/operator_evidence.py`：执行/汇总局部保持、时间断裂、刚体跟踪等证据，输出 validity、confidence、风险标签和是否可用于封顶。
- `eval/reasoning_alignment.py`：用标注的隐含规则问题计算推理一致率；它解释 Judge 是否理解约束，不进入主榜。
- `eval/visual_quality.py`：测量清晰度、曝光、压缩和画面可读性等中间帧技术质量，只作诊断。
- `eval/weakness_targets.py`：把失败模式映射到预先定义的能力弱点，供统计和定向改进。
- `eval/domain_alignment/eval.py`：检查输出内容与任务领域/语义是否相符；`domain_alignment/__init__.py` 提供包入口。

## 四、视觉与物理算子

- `eval/geometric_integrity/kinematic.py`：用光流/轨迹检查机械部件运动是否稳定、是否出现不合理形变。
- `eval/geometric_integrity/lattice.py`：检测规则网格或重复结构的完整性、间距和缺损。
- `eval/geometric_integrity/lattice_fourier.py`：用频域周期峰补充网格检测，适合密集重复纹理。
- `eval/geometric_integrity/rotary.py`：分析旋转部件中心、半径和旋转连续性。
- `eval/geometric_integrity/surface.py`：检查表面结构和视角变化下的稳定性，区分透视变化与真实破坏。
- `eval/geometric_integrity/symmetry_mech.py`：测量机械对象双侧/旋转对称保持情况。
- `eval/geometric_integrity/track_chain.py`：跟踪履带、链条等连续结构的部件数量与连接稳定性。
- `eval/industrial_constraints/count_invariant.py`：核对任务要求保持不变的部件数量。
- `eval/industrial_constraints/kinematic_coupling.py`：判断关节、连杆或成对部件是否保持正确耦合运动。
- `eval/industrial_constraints/periodic_structure.py`：检查叶片、齿、孔阵列等周期结构是否增删、错位。
- `eval/industrial_constraints/topology_merge_detector.py`：发现本应分离的物体/部件是否错误融合。
- `eval/physical_plausibility/eval.py`：汇总运动学、流体、碰撞和材料变化证据，给出物理合理性诊断。
- `eval/temporal_coherence/eval.py`：测量跨帧突变、闪烁、身份漂移和后段断裂。
- `eval/viewpoint_motion_fidelity/eval.py`：估计相机静止、平移、环绕等运动是否执行及幅度是否合理。
- `eval/visual_fidelity/eval.py`：比较参考图与视频的主体、外观和场景保持程度。
- `eval/calibration/difficulty_report.py`：按任务难度切片报告表现，检查分数是否随难度合理变化。
- 各上述目录中的 `__init__.py`：包初始化与公开导入，不实现独立评分规则。

## 五、正式评分与报告

- `scoring/policy.py`：加载并强校验 v4 JSON，确保六轴顺序、等权聚合、全轴覆盖率封顶和算子配置没有被悄悄改坏。
- `scoring/per_sample.py`：单样本评分核心；规范化六轴、应用事件覆盖和合格算子封顶，并计算单样本主榜分。
- `scoring/aggregate.py`：跨样本核心；只对六轴完整有效记录计算主榜均值和 cluster-bootstrap CI，同时输出旧指标但明确标成诊断。
- `scoring/compare.py`：比较两个模型或两次运行的轴分与总体差异。
- `scoring/leaderboard.py`：读取聚合结果生成排行榜数据和展示格式。
- `scoring/report.py`：生成完整评测报告、分类切片、失败原因和可审计字段。
- `scoring/discriminative_power.py`：分析轴/题目的区分能力，防止大量题目对模型没有辨别度。
- `scoring/failure_heatmap.py`：把模型、任务类别和失败模式整理成热图。
- `scoring/weakness_targets.py`：聚合弱点标签并输出模型能力短板。
- `scoring/__init__.py`：评分包入口。

## 六、数据设计、参考图与标注维护脚本

- `add_practical_scene_families.py`：加入更贴近实际用途的场景族。
- `add_reasoning_alignment_fields.py`：给样本补隐含规则问答字段。
- `add_samples_for_unreferenced_images.py`：为尚未被任务引用的图片创建候选样本。
- `add_*rejected_task_replacements.py` / `apply_*rejected_task_replacements.py`：分批应用人工否决任务的替换方案；不同文件对应不同审查批次，保留批次可追溯性。
- `apply_new_reference_images.py`：把确认的新参考图、描述和动作同步进标注。
- `apply_prompt_review_460.py`：应用 460 条 prompt 人审修订。
- `apply_user_deleted_review_replacements.py`：补回因人工删除而需要替换的任务。
- `apply_vsec_surveillance_replacements.py`：更新视觉安防子集的替换任务。
- `enrich_application_layer.py`：补齐应用目标、价值和误导性失败模式。
- `complete_weakness_targets.py` / `weakness_targets.py`：补齐和维护任务弱点标签。
- `refresh_samples_from_blueprint.py`：从蓝图字段重新同步正式样本。
- `rebuild_generation_prompts.py`：由规范字段重建生成 prompt，减少手工漂移。
- `repair_review_suggestions.py`：把人审建议修复为合法标注变更。
- `renumber_images_update_samples_and_prompts.py`：重编号图片并原子更新样本和 prompt 引用。
- `repoint_duplicate_image_references.py`：让重复引用指向规范图片。
- `reuse_compatible_reference_images.py`：在语义兼容时复用已有参考图。
- `rollback_imported_candidate_samples.py`：回滚特定候选导入批次，而非删除整套数据。
- `_shorten_feishu_prompts.py`：为飞书展示缩短过长 prompt，不改变正式生成语义。

## 七、图片搜集、筛选与导入脚本

- `find_reference_images.py` / `find_scene_images.py`：按任务查询并下载参考图候选。
- `download_commons_candidates.py` / `download_commons_category_scene_candidates.py`：从 Wikimedia Commons 获取可追溯候选。
- `expand_scene_image_library.py` / `run_parallel_scene_expansion.py`：扩充场景图库并行任务。
- `fast_multisource_image_backfill.py` / `targeted_candidate_backfill_v2.py` / `search_quality_backfill_candidates.py`：针对缺口从多源快速补图并进行质量过滤。
- `build_candidate_backfill_plan.py` / `build_dataset_backfill_plan.py` / `build_image_deficit_plan.py` / `make_image_sourcing_plan.py`：计算图片缺口并生成采购/搜索计划。
- `build_image_search_prompts.py`：把场景需求改写为检索词。
- `build_doubao_privacy_safe_images.py`：构建隐私安全的图像生成/替换集合。
- `curate_image_candidates.py` / `curate_scene_candidate_pool.py`：按语义、构图和图像统计筛选候选。
- `clean_image_candidates_strict.py` / `clean_image_task_alignment.py`：执行严格质量清洗与图文对齐检查。
- `flatten_screen_image_candidates.py` / `organize_candidate_images_flat.py`：整理候选目录，方便人工平铺浏览。
- `import_candidates.py` / `import_approved_image_candidates.py` / `import_scene_expansion_candidates.py` / `import_screened_image_candidates.py` / `import_imagesforloss.py`：分别导入通用、批准、场景扩展、已筛选和特定来源图片，并维护来源记录。
- `promote_backfill_candidates.py`：把通过审核的补图候选提升为正式资产。
- `prune_scene_images_to_target.py` / `optimize_image_library.py`：按覆盖、质量和重复度把图库压到目标规模。
- `normalize_scene_images_and_prompts.py` / `standardize_selected_images_and_report.py`：统一图片格式、尺寸、命名和关联 prompt，并输出变更报告。
- `materialize_video_generation_500_images.py`：生成 500 任务可直接使用的参考图目录。
- `dedupe_video_500_image_paths.py`：消除 500 任务清单中的重复路径。
- `list_unused_quality_images.py` / `list_unused_scene_images.py`：列出未使用优质图和场景图，供人工再分配。
- `audit_image_library_duplicates.py` / `audit_import_batch_duplicates.py`：用哈希/感知特征检查图库和导入批次重复。
- `audit_imported_image_semantics.py` / `audit_replacement_candidates.py`：检查新图是否真的符合任务语义和替换条件。

## 八、视频生成、下载与整理脚本

- `export_prompts.py`：导出模型调用所需 prompt 表。
- `export_video_gen_package.py`：打包生成端所需标注、参考图和清单。
- `build_scene_seed_samples.py`：构造生成试跑的场景种子样本。
- `build_stratified_video_manifest.py`：按类别/难度分层生成视频清单。
- `build_orbit_generation_manifest.py`：生成环绕镜头专项清单。
- `build_missing_camera_motion_manifest.py`：找出相机运动缺失的视频供重生成。
- `build_bad_video_manifest.py`：汇总损坏或人工判坏视频。
- `build_final_regeneration_package.py`：生成最终重跑输入包。
- `run_seedance2_500.py` / `run_veo31_fast_500.py` / `run_wan30_500.py`：调用对应模型批量生成 500 任务。
- `run_minimax_video_batch.py` / `resume_minimax_video_downloads.py`：提交 MiniMax 批次并断点续传结果。
- `build_wan21_eval_shards.py` / `merge_wan22_batches.py`：为 WAN 系列拆分评测分片并合并生成批次。
- `organize_dataset_videos.py`：把下载结果按模型和 task ID 放入规范目录。
- `trim_video_sets_to_5s.py`：统一视频时长到协议要求。
- `audit_mp4_integrity.py` / `final_validate_all_videos.py` / `validate_organized_videos.py` / `validate_wan21_complete.py`：逐层检查 MP4 可解码性、数量、ID 集合、时长与完整性。

## 九、正式评测、Judge 与人工校准脚本

- `run_full_formal_4gpu.py`：四 GPU 正式评测总调度和故障恢复。
- `retry_formal_incomplete.py`：只重跑正式结果中缺失/失败的样本。
- `build_formal_judge_retry_manifest.py`：把不可解析 Judge 输出转换为精确重试清单。
- `combine_eval_shards.py`：合并并校验并行评测分片。
- `reaggregate_cached_results.py`：Judge 原始结果不变时，用新评分代码重新聚合。
- `eval_hailuo_qwen_omni.py`：海螺视频的 Qwen-Omni 专项旧评测器；其旧加权总分仅可作历史诊断。
- `analyze_judge_robustness.py`：测 Judge 对提示、顺序或采样扰动的稳健性。
- `build_pairwise_judge_calibration_manifest.py` / `evaluate_pairwise_judges.py`：制作成对盲评材料并比较候选 Judge 与人类偏好。
- `build_human_judge_alignment_pack.py`：生成匿名、随机化的人类复核包和录入模板。
- `build_prompt_alignment_review_460.py`：制作 460 条图像-prompt 对齐人审任务。
- `make_angle_probe_contact_sheet.py` / `make_flat_review_contact_sheets.py` / `make_scene_contact_sheets.py`：生成角度、平铺或场景接触表，供人工快速浏览。
- `serve_mobile_review.py`：启动移动端友好的本地审核页面。
- `build_local_video_judge_report.py`：汇总本地 Judge 运行状态与结果。
- `audit_generation_prompts.py` / `audit_prompt_motion_verbs.py`：检查 prompt 完整性和运动动词是否与标注一致。
- `audit_operator_usage.py`：统计哪些算子运行、失效或参与封顶，防止静默缺证据。

## 十、分析、发布与论文脚本

- `analyze_gate_sensitivity.py`：旧门控参数敏感性实验；不得把结果当 v4 主榜。
- `classify_generation_content_difficulty.py`：按内容、运动和约束压力划分生成难度。
- `summarize_low_score_reasons.py`：聚合低分理由和常见失败模式。
- `build_video_evaluation_report.py`：把逐样本输出整理成面向阅读的评测报告；应调用正式 v4 排名语义。
- `build_feishu_doc.py`：生成飞书版项目说明和表格。
- `build_hf_video_scoring_package.py`：生成不压缩的 HF 路径、500 参考图、评分源码、文档、论文和校验和文件夹。
- `reproduce_paper_tables.py`：从正式结果重建论文表格，避免手工抄数。
- `final_validate_all_videos.py`：发布前最后核验所有模型视频矩阵。

## 十一、测试文件

- `test_pipeline_smoke.py`：覆盖评测到聚合的主链和大量边界行为。
- `test_scoring_policy.py`：锁定 v4 六轴、直接封顶和等权公式。
- `test_scoring_hardening.py`：验证异常值、缺字段、旧字段不会污染主榜。
- `test_scoring_validity_details.py`：验证缺轴、解析恢复和不可发布原因记录。
- `test_failure_diagnostics.py`：验证失败模式汇总。
- `test_video_protocol.py`：验证抽帧、首尾覆盖、时长与索引。
- `test_run_eval_video_resolution.py`：验证任务到实际视频路径的解析。
- `test_generation_prompt.py`：验证生成 prompt 与规范字段一致。
- `test_image_backfill_safety.py`：验证补图流程不会误覆盖正式资产。
- `test_pairwise_judge_calibration.py`：验证盲评配对、随机化和统计。
- `test_formal_judge_retry_manifest.py` / `test_retry_formal_incomplete.py`：验证失败重试只覆盖目标样本。
- `test_full_formal_supervisor.py`：验证多 GPU 调度、恢复和完成判定。
- `test_local_video_judge_report.py`：验证本地 Judge 报告。
- `test_paper_release_tools.py`：验证论文复现、完整样本政策和发布字段。
- `test_qwen_omni_eval.py`：验证专项 Qwen-Omni 解析与诊断计算。
- `test_weakness_targets.py`：验证弱点映射与覆盖。
- `tests/__init__.py`：测试包初始化。

## 十二、改动时应遵守的边界

改数据先跑 `dataset/validate.py`；改视频协议跑 `test_video_protocol.py`；改 Judge/解析跑主链和 validity 测试；改评分必须同步 JSON、`policy.py`、`per_sample.py`、`aggregate.py`、本评分方法、README、论文和发布脚本。任何脚本若仍输出旧 0.8/0.2 数值，字段名必须明确包含 `legacy` 或 `diagnostic`，且不得写入 `ranking_score`。
