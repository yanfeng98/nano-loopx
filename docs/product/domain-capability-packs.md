# 领域能力包


状态:设计目标。

原则:LoopX 默认是一个通用控制面。它应在尝试做出领域判断之前,先保证 state、evidence、边界、交接与校验路由。领域包可以让 LoopX 更聪明,但它们必须对能力与权限保持显式。

## 为什么存在

长程项目常常开始看起来有领域特定性。一个 ML 实验 agent、一个基准 agent、一个部署 agent 和一个文档 agent 都需要持久 state 与紧凑 evidence,但只有其中一部分应该了解主要指标、数据集窗口、训练任务或提升决策。

因此默认控制面应做两件事:

- 认识到领域包可能有帮助;
- 在注册表或 owner 记录该权限之前,停止启用领域特定的自主性。

这避免了"跟踪我的 goal"悄然升级为"解释并启动领域工作"。它也保持 LoopX 对普通工程 todo 有用,这类 todo 没有实验板、主要指标、护栏或生产任务句柄。

## 一个控制面之上的领域车道

Agent 原生 Kanban 隐喻提供了一个实用的放置规则:

| 界面 | Owner | 示例 |
| --- | --- | --- |
| 通用卡片生命周期 | LoopX Kernel | 认领、gate、monitor、延迟、完成、取代、配额、恢复 |
| 领域车道与阶段 | 能力包 | Issue Fix 评审阶段或实验评估阶段 |
| 外部事实与效果 | Provider | 检查状态、评审状态、指标结果、任务回读 |
| 可见的看板列 | Projection | 可运行、等待、监控中、评审、完成 |

领域车道是对领域 state 加已接受 Kernel state 的读模型。它可以解释某个 issue 已从补丁阶段移到 CI 评审,或某个假设已从执行移到 holdout 评估。它不拥有底层的 todo、认领、gate、配额或调度。

这样保持两类变更分离:

- 新增领域阶段通常改变包的领域 State schema、转换提议与投影;
- 新增跨领域生命周期规则只在规则具有 provider-neutral 契约且在一个包之外有真实调用方时才改变 Kernel。

不要仅仅为了绘制一个有用的看板,就把 `ci_review`、`holdout` 或 `promotion_candidate` 加入通用 Kernel 状态枚举。包应派生这些标签,然后通过现有类型化转换边界提交任何有后果的认领、gate、monitor、后继或收尾。

## 契约形态

`domain_pack_contract_v0` 是注册表持有的 goal 边界扩展:

```yaml
domain_packs:
  ml_experiment:
    enabled: false
    autonomy: suggest_only
    allowed_actions:
      - observe_external_jobs
      - ingest_metrics
      - classify_results
      - propose_replan
    capability_requirements:
      - external_evidence_poll
    primary_metric_authority: explicit_board_only
    auto_launch_requires: board_selected_and_verified
```

允许的 `autonomy` 值:

| 值 | 含义 |
| --- | --- |
| `suggest_only` | 检测信号并建议启用某个包。不要写入领域结论。 |
| `advisory` | 写入紧凑结果、假设与重规划提议。不要启动、停止、重启或同步生产代码。 |
| `delivery` | 仅在 goal 边界、配额护栏、能力 gate 与校验/写回生命周期内执行授权的领域动作。 |

默认行为:

- `enabled=false`:状态可以说"这个 goal 看起来像 ML 实验;如果确实如此,请启用 ml_experiment 包。"
- `autonomy=suggest_only`:包可以解释它为何有帮助,但不写入实验结果或重规划决策。
- `autonomy=advisory`:包可以写入紧凑 evidence、结构化结果摘要与提议的重规划,但仍不能启动任务。
- `autonomy=delivery`:启动/停止/重启/同步动作需要显式 goal 边界授权、新鲜配额、已选择并验证的看板权威、预检校验与紧凑写回。

首次启用应是可见的注册表或 owner 决策。后续 Turn 只能在该记录的 goal 边界内自主使用已启用的包。

## 通用能力

这些能力不是 ML 专属,应在默认 LoopX 控制面中可用。

| 能力 | 默认角色 |
| --- | --- |
| `observable_artifact_handle_v0` | 用可观察句柄、允许的轮询命令、产物引用、终结标记与读取边界描述外部任务、CI 运行、基准尝试、评估、部署或其他长任务。 |
| `validation_surface_map_v0` | 要求每个可执行 todo 命名其校验方式:代码测试、文档扫描、外部 evidence、评审包或阻碍写回。 |
| `result_event_v0` | 在不假设领域指标 schema 的前提下记录终结状态、evidence 指针、校验状态、结果分类与下一步动作。 |
| `reward_style_hint_preview` | 从紧凑 reward/todo evidence 提供只读候选排序提示。提示可以解释排序,但不能覆盖用户 gate、认领、范围、能力、工作区护栏或 goal 边界。 |
| `handoff_packet_v0` | 为人类或另一 agent 打包目标、当前状态、校验、风险、下一步动作与停止条件。领域包可以添加字段,但交接本身是通用的。 |
| `status_frontstage_plain_language_projection` | 用普通语言解释发生了什么、什么被阻碍、接下来会发生什么以及需要什么用户动作。领域包可以添加专门卡片。 |

这些应保持对任何项目类型安全。项目特定适配器决定它可暴露哪些句柄、引用与校验,但协议形态是通用的。

## ML 实验包

ML 实验包是一个领域能力包。它应保持默认关闭,因为它带有普通工程工作可能不共享的假设。

包控制的能力:

| 能力 | 为何是领域特定的 |
| --- | --- |
| `ml_experiment_result_v0` | 使用主要指标、基线增量、护栏指标、决策窗口、对齐评估与仅训练护栏概念。 |
| `dataset_window_contract_v0` | 建模日期/小时覆盖、匹配窗口、缺失小时处理、公平性标签与样本可比性。 |
| `hypothesis_ledger_v0` | 追踪机制族、路由、正负 evidence、近邻排除、退休规则与可移植性。 |
| `experiment_replan_v0` | 选择下一批实验、探索/利用分配、配额使用、提升与退休提议。 |
| `external_training_job_adapter` | 轮询外部训练或评估任务、摄取指标、检查工作区标记、终结标记与血缘。 |
| `auto_launch_experiment` | 启动/停止/重启/同步动作是交付权威,不是通用控制面行为。 |
| `dreaming_experiment_proposal_v1` | 从实验历史生成候选机制、研究方向与归档建议;有用,但在评审前仅作参考。 |

包绝不应仅因为 todo 中的文本看起来眼熟,就推断某个指标板、数据集路径、训练系统或启动命令已获授权。权威来自注册表、goal 边界与紧凑的 owner 决策。

### 快速试用

算法实验用户可以在不启用交付权威的情况下试用 advisory 形态:

```bash
loopx ml-experiment preview --format json \
  --experiment-id exp_preview_v1 \
  --primary-metric offline_auc \
  --baseline-value 0.421 \
  --candidate-value 0.437 \
  --guardrail-status clean \
  --train-window train_2026w24 \
  --eval-window eval_2026w25 \
  --hypothesis-id h_route_mix_v1 \
  --mechanism-family "candidate retrieval mix" \
  --route route_mix \
  --positive-evidence offline_eval_delta_positive \
  --next-candidate holdout_eval
```

预览不写入任何 state,也不启动任何东西。它返回紧凑的公开安全 `ml_experiment_result_v0`、`dataset_window_contract_v0`、
`hypothesis_ledger_v0` 与 `experiment_replan_v0` 部分,且
`launch_actions_enabled=false` 与 `production_actions_enabled=false`。
使用产物别名,而不是原始日志、私有路径、内部链接或携带凭据的指标转储。

### Volc/MLP 任务包

对于外部训练/评估系统,LoopX 还可以渲染紧凑的
`volc_mlp_task_packet_v0` 事实包。这是观察与交接格式,不是启动器。它捕获任务身份、任务状态、train/eval 窗口、代码/模型血缘、指标产物别名与允许的轮询契约。它刻意不存储原始命令行、环境转储、凭据、生产路径、工作区路径或私有日志。如果调用方把原始路径或 URL 作为工作区或指标引用传入,LoopX 会发出不可逆的 `redacted:<digest>` 句柄代替。

```bash
loopx ml-experiment volc-task-packet --format json \
  --task-id task-candidate-0 \
  --task-name external_slice_cross_screen \
  --state Running \
  --priority 4 \
  --retried-times 0 \
  --train-window 20251002-20260501 \
  --eval-window 20260501-20260508 \
  --code-ref codex/example-feature-cross@abc1234 \
  --model-name candidate_model_abc1234 \
  --mechanism-family explicit_context_item_crosses \
  --source-task-id task-baseline-0 \
  --metric-ref metrics/eval-summary.json \
  --primary-metric target_slice_auc \
  --guardrail-metric overall_auc
```

该包保持 `launch_actions_enabled=false` 与
`production_actions_enabled=false`。项目特定适配器可以把它用作持久紧凑 evidence,但实际的创建/停止/重启/同步动作仍需要显式交付权威、配额、预检校验与写回。

当任务达到实质性 evidence 时,agent 可以渲染一行
`volc_mlp_result_ledger_v0`。这是任务包之上的基准台账层:它记录同窗口指标增量、护栏状态、以训练指标为护栏的策略、失败归因标签与紧凑的提升/不提升路由。它对长程模型迭代很有用,因为它阻止 agent 在不提升结果后反复重试薄弱的近邻实验,同时保留足够的公开安全 evidence 用于重规划。

```bash
loopx ml-experiment volc-result-ledger --format json \
  --experiment-id external_slice_screen \
  --task-id task-candidate-1 \
  --task-name external_slice_cross_screen \
  --state Completed \
  --train-window 20251002-20260501 \
  --eval-window 20260501-20260508 \
  --code-ref codex/example-feature-cross@abc1234 \
  --model-name candidate_model_abc1234 \
  --mechanism-family explicit_context_item_crosses \
  --primary-metric target_slice_auc \
  --baseline-value 0.731 \
  --candidate-value 0.742 \
  --guardrail-status clean \
  --guardrail-metric guardrail_slice_a_auc \
  --guardrail-metric guardrail_slice_b_auc \
  --positive-evidence same_window_target_slice_auc_up
```

对于启动/评估失败的尝试,省略指标值,改为传递紧凑失败标签:

```bash
loopx ml-experiment volc-result-ledger --format markdown \
  --experiment-id external_slice_screen \
  --task-id task-candidate-0 \
  --task-name external_slice_cross_screen \
  --state Failed \
  --train-window 20251002-20260501 \
  --eval-window 20260501-20260508 \
  --code-ref codex/example-feature-cross@abc1234 \
  --model-name candidate_model_abc1234 \
  --mechanism-family explicit_context_item_crosses \
  --primary-metric target_slice_auc \
  --failure-label stale_model_py_root \
  --failure-label missing_restore_checkpoint \
  --negative-evidence failed_before_eval_metrics
```

结果台账仍保持 `launch_actions_enabled=false` 与
`production_actions_enabled=false`;它是可移植的事实/决策行,不是带创建/停止/重启权威的 Volc connector。

## 检测

`domain_pack_detection_v0` 是仅建议探测器。它可以检查公开安全的 goal 元数据与紧凑 state 中的信号,例如:

- 实验板或评估产物引用;
- 主要指标或护栏标签;
- 外部任务 evidence 句柄;
- 反复出现的指标/分类/结果 todo;
- 显式要求实验 advisory 或交付的 owner 语言。

探测器返回建议,而非权限:

```json
{
  "schema_version": "domain_pack_detection_v0",
  "suggested_pack": "ml_experiment",
  "confidence": "medium",
  "reason_codes": ["primary_metric_label", "external_job_handle"],
  "allowed_next_action": "suggest_enablement",
  "requires_owner_or_registry_decision": true
}
```

如果包被禁用,agent 可以建议启用它,并可以继续通用控制面工作。它不得写入实验结论、标记赢家、启动任务,或把领域提示当作 gate 绕过。

## 结果流

当 ML 实验包以 advisory 模式启用时,通用结果事件仍包裹领域结果:

```yaml
result_event_v0:
  terminal_state: done
  evidence_pointer: compact_metrics_artifact
  validation_status: validated
  outcome_classification: outcome_progress
  next_action: propose_replan
  domain_extension:
    kind: ml_experiment_result_v0
    primary_metric_status: improved
    guardrail_status: clean
    decision_status: candidate_not_winner_yet
```

通用字段保持状态、配额、评审包与前场界面稳定。领域扩展只在包启用后添加有用的解释。

## State 放置

ML 实验 state 应存储在三层中,而不是直接追加进核心 active state。

| 层 | 默认位置 | 拥有 | 不拥有 |
| --- | --- | --- | --- |
| 核心 LoopX state | 注册表、`ACTIVE_GOAL_STATE.md`、todo、运行历史、上线事件 | 当前下一步动作、gate、认领、紧凑 evidence 摘要、配额/花费生命周期 | 逐任务指标历史、原始外部任务详情、实验板规模台账 |
| 领域 state | `.loopx/domain-state/<goal-id>/<domain-pack>/...` | 任务/结果行、数据集窗口契约、同窗口比较、护栏摘要、提升/退休决策 | 凭据、原始日志、原始启动命令、大型指标转储 |
| 原始/私有产物 | 项目本地被忽略的适配器存储,如 `.local/` 或私有 connector 缓存 | 原始日志、命令快照、工作区路径、调试包、大型指标产物 | 状态真相、todo 所有权、配额权威 |

领域 state 层是项目本地且 gitignored 的,因此它可以包含不应公开的运维者私有任务 id 与紧凑指标事实。它仍是供 agent 使用的读模型,而不是原始 evidence 桶。保持紧凑可防止状态、重规划与交接提示继承嘈杂或敏感的运营痕迹,同时避免把 ML 特定 state 塞进通用控制面的相反问题。

当调用方传递 `--goal-id` 时,CLI 写入该层:

```bash
loopx ml-experiment volc-result-ledger \
  --goal-id example-goal \
  --experiment-id external_slice_screen \
  --task-id task-candidate-1 \
  --task-name external_slice_cross_screen \
  --state Completed \
  --train-window 20251002-20260501 \
  --eval-window 20260501-20260508 \
  --code-ref codex/example-feature-cross@abc1234 \
  --model-name candidate_model_abc1234
```

默认目标是
`.loopx/domain-state/example-goal/ml_experiment/ledger.jsonl`。调用方可以为迁移或测试传递 `--ledger-path`,但常规项目使用应优选 goal 边界的默认路径。

代码应遵循同样的拆分:

| 代码区 | 拥有 |
| --- | --- |
| `loopx/domain_state.py` | 跨包路径约定、本地锁、原子 JSONL upsert 与小型存储原语 |
| `loopx/domain_packs/<pack>.py` | 包特定 schema、指标解释、渲染器与台账键选择 |
| 遗留顶层模块如 `loopx/ml_experiment.py` | 仅当旧导入已存在时才做兼容再导出 |

## 路线图

P0:拆分边界。

1. 设计与校验 `domain_pack_contract_v0`:`enabled`、`autonomy`、
   `allowed_actions`、`capability_requirements` 与边界语义。
2. 把 `domain_pack_detection_v0` 实现为仅建议。它可以识别实验形态的 goal,但不能自我启用。
3. 把 `observable_artifact_handle_v0` 提升为长程工作的默认通用能力。

P1:添加 ML 实验 advisory 模式。

4. 基于紧凑指标/评估产物定义 `ml_experiment_result_v0`。
5. 定义 `dataset_window_contract_v0`:日期/小时覆盖、交集、公平性标签与结论资格。
6. 定义 `hypothesis_ledger_v0`:机制族、正负 evidence、近邻排除与提升/退休条件。
7. 添加不启动任务也能提议候选与校验需求的 `experiment_replan_preview`。

P2:添加受控交付。

8. 在显式注册表边界、看板选择、预检校验、配额、能力 gate 与写回之后实现 `ml_experiment` 交付模式。
9. 添加 `ml_experiment_frontstage` 卡片,解释当前最佳路由、它为何是/不是赢家、什么 evidence 待定,以及什么用户反馈会改变计划。
10. 添加用于 advisory 候选生成与归档建议的 `experiment_dreaming_lane`。提升为可执行 agent todo 需要运维者评审。

## 非目标

- 不要在默认控制面中内嵌 ML 实验假设。
- 不要仅凭检测就自动启动或停止外部任务。
- 不要从任意文本推断主要指标权威。
- 不要在公开文档或通用状态投影中存储原始指标转储、私有任务日志、凭据、本地路径或生产产物。
- 不要让 reward 风格或重规划提示覆盖 gate、认领、范围、能力、工作区护栏或 goal 边界。
