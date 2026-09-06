---
name: loopx-benchmark
description: Use when a LoopX-managed goal runs, tracks, scores, or analyzes a benchmark experiment through benchmark-toolkit, including experiment-board rows, solver arms, integrity qualification, matched comparisons, or case insights. Do not use for casual benchmark discussion, ordinary software microbenchmarks, or eval mentions without LoopX experiment state.
---

# LoopX Benchmark 工作流


对 LoopX 管理的 benchmark 实验使用本技能。内置的
`benchmark-toolkit` capability 拥有 provider-neutral 实验状态与完整性边界。
本打包技能是它的任务触发版 Agent playbook。

该 capability 无需按 Goal 启用开关即可目录就绪。安装本技能不授予 runner、
shell、network、credential、private-evidence 或 Goal 变更权限。尊重所选 todo
的必需 capability、任何外部 provider 绑定、宿主权限与用户 gate。

## Capability 界面

- `loopx capability show benchmark-toolkit --format json` — 目录条目，含使用
  提示、角色边界与运行后 case-insight 模板。
- `loopx benchmark --help` — 子命令（experiment-board-show、
  experiment-board-upsert、source-revision-fence、integrity-qualification、
  classify-artifacts）。

## 通过公开安全契约共享研究

当另一个 benchmark 开发者需要可移植的研究数据时，使用该 capability 的
typed study 流程，而不是共享 runner 特定 ledger 或原始证据：

1. 用 `benchmark study-validate` 验证 `benchmark_study_manifest_v0`。
2. 用 `benchmark upload-envelope` 包装一个允许清单中的 manifest、
   experiment-board 行、脱敏 insight 或运行时观察。
3. 先不带 `--execute` 运行 `benchmark upload-local`，然后对调用方选择的
   本地 JSONL 存储显式执行。
4. 用 `benchmark upload-readback` 验证 record/digest/revision 绑定。
5. 用 `benchmark study-dashboard` 推导 campaign/arm/case/run 包；
   仅当研究预先注册了该设计时才传递紧凑的四臂契约。

对 `case_insight_projection`，先用 `insight.status=complete` 上传同一运行
的活跃终态 experiment-board 行。case、run 与 outcome 必须匹配；run 行仍是
arm、score、countability、integrity 与 treatment-fidelity 的唯一权威。构建
envelope 前，把私有运行后证据压缩为有界散文与公开安全句柄或摘要。

本地 provider 是无网络模拟。它不授予远端上传、发布、凭据、保留或 benchmark
提交权限。Adapter 保留其原始指标名称，并在构建 envelope 前压缩私有运行后
证据。

## 选择运行通道

- **检查或解释：**使用 `capability show` 与 `benchmark --help`；保持只读。
  不要仅因用户问 toolkit 做什么就创建 experiment-board 行。
- **计划、选择或启动运行：**遵循下方的实验序列。第一步是读板；启动仍需
  经授权的 runner 与被认可的源。
- **监控活跃 campaign：**读板与运行时所属投影；仅在材料性运行迁移时更新。
  不要从计时器滴答制造进展。
- **分析终态运行：**等待 solving 终态且评分完成后，才读取隐藏 evaluator
  证据或编写 case insight。

对通用库 microbenchmark 或没有 LoopX Goal/板的 eval，使用任务常规工具，
而不是强加此工作流。

## 实验序列

1. **启动或选择 case 前先读实验板。**
   ```bash
   loopx benchmark experiment-board-show --goal-id <GOAL_ID> --format json
   ```
   选择下一 arm 前检查 baseline、treatment、explore、countability、effort
   与 insight 行。

2. **在每次新运行接纳前认定源修订。**
   ```bash
   loopx benchmark source-revision-fence \
     --source-checkout <clean-source> \
     --expected-revision <PIN> \
     --observed-reference-revision <OBSERVED_HEAD> \
     --require-admitted --format json
   ```
   除非干净的固定源与观察到的参考 head 匹配，否则该 fence 失败关闭。

3. **运行时先预览，再预注册或标记运行行。**
   ```bash
   loopx benchmark experiment-board-upsert --goal-id <GOAL_ID> \
     --row-json <running-row.json> --format json
   loopx benchmark experiment-board-upsert --goal-id <GOAL_ID> \
     --row-json <running-row.json> --execute --format json
   ```
   运行行使用 `status=running`、空的 `metrics` 与
   `countability={integrity_qualified:false, official_result_present:false,
   score_countable:false}`。每次迁移保持同一稳定 `run_id`。

4. **预览并 upsert 终态 score、countability、effort 与 insight。**
   先运行完整性资格认定。自动的受限访问匹配是可计数的嫌疑，不是作弊裁决。
   solver 与评分终态后，检查真实 solver 轨迹、工具结果与最终工作区。
   只有在该评审后，才传递紧凑的
   `benchmark_restricted_access_adjudication_v0`；仅当受限材料确实被披露且
   因果进入 solving 或验证决策时才确认作弊。

   ```bash
   loopx benchmark experiment-board-upsert --goal-id <GOAL_ID> \
     --row-json <terminal-row.json> --execute --format json
   ```
   终态行设置 `status=completed`，填入 `metrics`（主指标加 guardrail），
   并更新 `countability`。仅当 `integrity_qualified=true` 且
   `official_result_present=true` 时，才标记 `score_countable=true`。运行后
   分析完成后填入 `effort` 并将 `insight.status` 设为 `complete`。

   对非 baseline arm，另外单独压缩审阅过的机制事实：
   ```bash
   loopx benchmark treatment-continuation-receipt \
     --observation-json <compact-post-run-observation.json> --format json
   ```
   该 receipt 区分合格启动与启动后语义控制持续。它仅供分析，不得改变
   score countability、integrity 资格认定、treatment fidelity 或匹配对资格。

5. **选择下一 arm 前读取匹配比较。**
   ```bash
   loopx benchmark experiment-board-show --goal-id <GOAL_ID> --format json
   ```
   只从 `matched_pair_countable` 比较中主张配对结果。把纯诊断 Explore 行
   保留在单独证据通道。

## 运行行契约

- `benchmark_id`、`study_id`、`case_id`、`run_id`、`arm_id`、`arm_role`、
  `attempt`、`status`、`observed_at`、`model_id`、`protocol_id`、
  `comparison_protocol_id`、`claim_scope`、`primary_metric`、
  `guardrail_metrics`、`metrics`、`countability`、`treatment_fidelity`、
  `effort`、`insight` 是规范行字段（`schema_version` =
  `benchmark_experiment_board_row_v0`）。
- Baseline 行必须使用 `treatment_fidelity=not_applicable`，且不能命名
  `comparison_anchor_run_id`。非 baseline 行必须命名 `comparison_anchor_run_id`。
- Metrics 是 `{"name": {"value": <number>, "unit": <str>,
  "higher_is_better": <bool>}}`；最多 16 项。`primary_metric` 不得同时是
  guardrail 指标。
- `score_countable` 需要 `status=completed`、`integrity_qualified=true` 与
  `official_result_present=true`。`score=0` 是有效的已完成结果。

## 源、完整性与产物边界

- `source-revision-fence` 只读且由调用方观察：它不执行 fetch、install 或
  launch。它只阻止新的接纳。
- `integrity-qualification` 把私有轨迹与 runner 隔离证据压缩为紧凑公开安全
  receipt（哈希、计数、原因码）。
- 对受限源访问或宿主边界逃逸探针的扫描命中，会把 `restricted_access_review`
  设为 `suspected`，同时保持运行可计入分数。对运行后 agent 决策使用
  `--restricted-access-adjudication-json`；只有确认披露加因果使用才取消
  分数资格。
- `classify-artifacts` 在不读取产物的前提下分类 benchmark 产物路径；在读取
  或发布任何候选产物前使用它。
- Solving 阶段，solver 通道不得读取隐藏测试、verifier 源、标准答案或官方
  反馈。运行后分析者只能在 solver 终态且评分完成后读取完整私有证据。
- `capability bind` 为 Goal 选择外部 provider 实现；它不是该内置 capability
  的激活机制。Todo `required_capability` 字段保持为运行时前置条件，而非产品
  capability 开关。

## Campaign 监控与运行后洞察

- 当 campaign 启动且调用方授权持续监控时，添加一个 `continuous_monitor` todo。
  在材料性 scored-case 迁移时刷新聚合 score/coverage 并写入
  `benchmark_case_insight_v0`，在 campaign 保持活跃期间进行有界周期性评审。
- 把该 monitor 视为观察通道，而非可执行交付。当材料性 poll 发现有界仓库、
  runner-repair 或实验工作时，用 `quota monitor-poll --material-change
  --next-agent-todo` 并带显式 `--next-action-kind`、repository 与必需
  capability，以创建独立可运行的 `advancement_task`。无变化的 poll 不产生
  继任者，也不消耗交付 quota。
- 如果主 campaign advancement Todo 在等待某个 monitor 迁移，保持其为 `open`，
  并把 `resume_when=monitor_changed:<monitor-todo-id>` 与已创建的独立可运行
  继任者配对。不要将等待标记为 `blocked`，也不要将 monitor 本身视为交付
  工作。
- 只报告公开安全结论（可计数的 baseline、可计数的 treatment、匹配对、按 arm
  的聚合主指标、改善/持平/回退配对计数）。永远不要把原始私有证据复制到用户
  更新中。
- solver 停止且评分完成后，读取任务、真实轨迹、最终工作区、隐藏测试、verifier
  与失败/评分细节；写一个 `benchmark_case_insight_v0` 解释决定性证据、结果
  为何发生以及 LoopX 下一步应测试什么。
- 对 treatment arm，记录合格启动是否跟随语义 Todo 迁移、技术重规划或控制
  收尾。仅当完整授权的运行后评审未观察到此类迁移时才使用 `startup_only`；
  否则其缺省为 `unknown`。保持终态结算独立。
- 无材料性变化时不要发送重复的用户更新。
