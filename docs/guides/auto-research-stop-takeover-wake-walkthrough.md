# Auto Research 停止、接管与状态感知唤醒


面向贡献者的、已交付 Auto Research 控制转移走查。复用现有单命令路径。不要添加
第二个 launcher，也不要在未经 maintainer 预览的情况下修改 README 首屏。

运行时控制转移在
[#2786](https://github.com/huangruiteng/loopx/pull/2786) 交付（相关
[#2783](https://github.com/huangruiteng/loopx/issues/2783)）。本指南是 GH-C43 的
操作者侧证明路径。

规范命令路径：
[Auto-research 命令路径](../../demo/auto_research/README.md)。

## 本走查覆盖什么

| 转移 | 操作者信号 | 结果 |
| --- | --- | --- |
| 外部停止 | 放置 `workspace/.loopx-auto-research-stop` | Worker-loop 在下一轮之前以 `stop_reason = operator_stop_requested` 退出 |
| 操作者接管 | `auto-research start … --execute --attach` | 附加到可见 tmux 会话；跳过默认后台唤醒，让操作者先行动 |
| 状态感知唤醒 | `--wake-visible-after-launch` 配合 `--no-attach` | 只有带选中可运行 todo 且 `quota.should_run` 的 lane 收到固定 A2A 唤醒 |
| Quota 暂停 | 实时 `quota.ok && !quota.should_run` | Worker turn 返回 `mode = paused_by_quota`；Loop 报告 `stop_reason = quota_paused` |

单个 `worker-turn` 调用不受停止标记拦截。这样在多轮 Loop 暂停时仍保留手动推进
lane 的能力。

## 边界

- 坚持使用交付的 `loopx auto-research start` / `worker-loop` / `worker-turn`
  命令。不要发明并行 demo launcher。
- 只使用合成或脱敏的公开安全证据。不携带凭证、原始 Codex 记录、私有路径或
  在线模型主张。
- `--attach` 与 `--wake-visible-after-launch` 按设计互斥：选择操作者接管或
  后台唤醒，不要两者兼得。
- 停止 worker-loop 不等于杀死 tmux 会话。移除停止标记即可恢复 Loop；仅当
  可见彩排本身应当结束时才使用 `tmux kill-session`。

## 1. 从现有命令路径出发

先导出一个显式 goal 与工作区身份，并在之后的每条命令中复用。没有
`--goal-id` 时，`start` 会创建一个带时间戳的新 goal，下面的停止/恢复命令
将无法指向它：

```bash
export GOAL_ID="loopx-auto-research-demo"
export WORKSPACE="$HOME/loopx-auto-research-demo"

export LOOPX_REGISTRY="$HOME/.codex/loopx/registry.global.json"
export LOOPX_RUNTIME_ROOT="$HOME/.codex/loopx"

loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --goal-id "$GOAL_ID" \
  --workspace "$WORKSPACE" \
  --create-workspace

loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --goal-id "$GOAL_ID" \
  --workspace "$WORKSPACE" \
  --create-workspace \
  --execute \
  --replace-existing
```

对于记录唤醒证据、但不附加的 JSON 自动化：

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research start \
  "How should we evaluate autonomous research agents?" \
  --goal-id "$GOAL_ID" \
  --workspace "$WORKSPACE" \
  --create-workspace \
  --execute \
  --no-attach \
  --wake-visible-after-launch
```

## 2. 停止 Worker Loop 而不破坏状态

当多轮 worker-loop 正对 `$WORKSPACE` 研究工作区运行时，把停止标记放在那里。
`worker-loop` 从其自身工作目录读取标记，因此请从 `$WORKSPACE` 运行：

```bash
touch "$WORKSPACE/.loopx-auto-research-stop"
```

下一轮检查以如下内容退出：

```json
{
  "ok": true,
  "stop_reason": "operator_stop_requested",
  "turn_count": 0
}
```

当标记在第 1 轮之前存在时如此；若标记出现在轮次之间，则保留先前轮次。标记在
每轮顶部检查，而不只是进程入口。

通过移除标记并调用 `worker-loop` 从同一工作区、同一 goal 恢复：

```bash
rm -f "$WORKSPACE/.loopx-auto-research-stop"

cd "$WORKSPACE"

loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  --format json auto-research worker-loop \
  --goal-id "$GOAL_ID" \
  --agent-id research-curator \
  --agent-id hypothesis-proposer \
  --agent-id research-executor \
  --agent-id evaluator-promoter \
  --max-rounds 2 \
  --execute \
  --complete-selected-todo
```

`operator_stop_requested` 与 `quota_paused`、`no_executed_turns`、
`no_runnable_frontier` 和 `max_rounds` 不同。

## 3. 接管可见 Lane

立即的操作者接管使用同一个 start 命令配合 `--attach`，指向同一显式 goal 与
工作区。这会跳过默认的可见角色唤醒，让操作者先进入 tmux 会话：

```bash
loopx --registry "$LOOPX_REGISTRY" \
  --runtime-root "$LOOPX_RUNTIME_ROOT" \
  auto-research start "How should we evaluate autonomous research agents?" \
  --goal-id "$GOAL_ID" \
  --workspace "$WORKSPACE" \
  --create-workspace \
  --execute \
  --attach
```

在会话内，中断某个 pane，运行单个 lane 的 worker-turn 或手动推进 todo，然后
继续。之后无需重新启动即可附加：

```bash
tmux attach -t loopx-auto-research
```

只停止可见彩排（而非 LoopX goal 状态）用：

```bash
tmux kill-session -t loopx-auto-research
```

## 4. 状态感知唤醒过滤器

当启动后请求唤醒时，Auto Research 通过
`load_auto_research_worker_frontier()` 加载每个 lane 的 frontier，并跳过不应该
收到固定 A2A prompt 的 lane：

| 跳过原因 | 含义 |
| --- | --- |
| `quiet_completion_allowed` | Goal 已允许安静完成 |
| `no_selected_todo` | Frontier 没有选中的可运行 todo |
| `quota_should_run_false` | 调度器拦截了该 lane |
| `no_agent_mapping` | 已启动 lane 没有 agent id 映射 |
| `frontier_load_failed` | Frontier 加载失败；receipt 使用 `error_code`，绝不使用原始异常字符串 |

如果每个 lane 都被过滤，唤醒 receipt 是一个公开安全的 no-op：

```json
{
  "ok": true,
  "schema_version": "multi_agent_pane_a2a_wakeup_v0",
  "mode": "no_op_all_filtered",
  "target_lanes": [],
  "prompt_delivery": "skipped_no_ready_lanes",
  "wakeup_model": "state_aware_filter_no_ready_lanes"
}
```

空的就绪集合绝不能以 `[]` 调用底层唤醒 helper，因为遗留唤醒语义把空列表解释为
“所有 lane”。

被过滤的 lane 出现在 `state_aware_filter` 下以便审计。广播器仍然不选择 todo，
也不写入 LoopX 研究真值。

## 5. Quota 暂停对操作者停止

当某一 Turn 看到 `quota.ok` 且 `quota.should_run == false` 时，它在执行之前返回
`mode = paused_by_quota`。如果一轮中每个 Turn 都这样暂停，worker-loop 以
`stop_reason = quota_paused` 停止。

不要将资源压力当作操作者意图：

- `quota_paused` —— 调度器说不要花费；
- `operator_stop_requested` —— 操作者放置了停止标记。

## 可复现验证

无需在线模型。运行固定每个转移的合成 smoke，然后是可选周期 smoke：

```bash
python3 examples/auto-research-stop-marker-smoke.py
python3 examples/auto-research-state-aware-wake-smoke.py
python3 examples/auto-research-quota-pause-smoke.py
python3 examples/auto-research-stop-takeover-walkthrough-smoke.py
python3 examples/auto-research-demo-e2e-worker-loop-smoke.py
python3 examples/auto-research-visible-worker-hook-smoke.py
python3 examples/showcase-catalog-smoke.py
loopx check --scan-path docs/showcases --scan-path docs/guides
```

## 证据边界

本走查用合成夹具记录已交付的公开契约。它不声称某研究发现已可投产，不记录原始
日志或凭证，也不把 Auto Research 当作第二个核心调度器晋升。晋升仍需要 rollout
支撑的证据以及常规 LoopX gate 或写回规则。
