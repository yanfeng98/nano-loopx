# Codex App 控制面 Hook 缓存

> [English](codex-app-control-plane-hook-cache.md)

状态：实验性设计说明，默认关闭。

本说明定义一个可能的 Codex App host hook 的边界：向 heartbeat worker 暴露紧凑的 LoopX 控制面快照。目的是一方面减少长程 Codex App heartbeat 中反复的 token 密集型 status/quota 检查，另一方面不削弱 LoopX 的事实源、gate、隐私或写回规则。

该功能必须保持默认禁用。只有在本文中的 evidence gate 通过之后，它才能成为用户可见选项。只有另行记录一次采用决策（含 rollout evidence 与回退行为）之后，它才能成为默认路径。

## 问题

如今，可信的 Codex App heartbeat 通常运行：

```bash
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" \
  quota should-run --goal-id <goal-id> --agent-id <agent-id>
```

该命令是正确的 authority 边界，但完整 JSON 载荷可能很大。Worker 往往只需要一小份路由摘要：

- 是否需要用户动作；
- 当前 agent 是否必须尝试工作；
- 选中的 todo id 与紧凑动作文本；
- scheduler 动作与 reset/backoff 提示；
- workspace guard 与 capability gate 决策；
- 提示过期或不完整时的下一个冷路径命令。

产品问题是：Codex App 能否把这份紧凑路由摘要作为本地 host hint 提供，让 heartbeat prompt 不再反复吸收整个控制面载荷。

## 非目标

Hook 缓存不得：

- 用自身替换 LoopX registry、活跃状态、run 历史或 quota 记账作为事实源；
- 绕过 `quota should-run`、user/controller gates、workspace guard、capability gates、public/private 边界扫描或 spend-after-validation 规则；
- 为所有用户或所有 goal 启用自身；
- 存储原始活跃状态正文、聊天 transcript、私有资料、本地绝对路径、凭据或完整 run-history 记录；
- 把过期或缺失的提示变成运行的许可。

## 实验契约

实验载荷是 `codex_app_control_plane_snapshot_v0`：

```yaml
schema_version: codex_app_control_plane_snapshot_v0
enabled_by_default: false
mode: advisory_hint
goal_id: example-goal
agent_id: codex-evidence-peer
generated_at: "2026-01-01T00:00:00Z"
source_fingerprint:
  registry_goal_updated_at: "2026-01-01T00:00:00Z"
  active_state_sha256_16: "publicsafehash"
  runtime_index_mtime: "2026-01-01T00:00:00Z"
summary:
  should_run: true
  effective_action: normal_run
  user_action_required: false
  agent_must_attempt: true
  selected_todo_id: todo_publicsafe
  compact_action: "Run one bounded validated batch."
  scheduler_action: run_now
fallback:
  cold_path: quota_should_run
  command: loopx --format json quota should-run --goal-id example-goal --agent-id codex-evidence-peer
  required_when: stale_missing_mismatch_or_delivery_write
privacy:
  contains_raw_state: false
  contains_raw_history: false
  contains_private_paths: false
```

该载荷是 host-runtime 提示。LoopX 保持权威。Worker 可以用提示决定是否去取冷路径，但任何文件编辑、外部动作、PR 发布或 quota spend 仍需要正常 LoopX guard，除非后续一个显式启用的实验证明该紧凑快照是那个 guard 的新鲜、奇偶校验投影。

## 新鲜度与失效

仅当所有身份键匹配时提示才新鲜：

- `goal_id`；
- `agent_id`；
- 选中的 todo id 或有效动作；
- scheduler 动作；
- 活跃状态指纹；
- registry goal 更新指纹；
- runtime index 指纹。

以下情况立即失效：

- 用户反馈到达；
- todo 被添加、认领、完成、推迟、取代或重新指派；
- gate 被解决或引入；
- scheduler 动作变化；
- workspace guard 或 capability gate 变化；
- run 历史收到实质转变；
- 应用无法证明快照来自同一本地 registry 路径。

缺失、过期或不匹配的提示回退到 CLI。回退是成功，不是错误。

## 激活级别

| 级别 | 名称 | 允许行为 | 默认 |
| --- | --- | --- | --- |
| 0 | `disabled` | 无 hook/缓存。Heartbeat 像今天一样调用 CLI。 | 是 |
| 1 | `advisory_hint_lab` | 应用可以显示或注入紧凑提示，但 worker 在交付工作前仍运行 CLI。 | 否 |
| 2 | `quiet_wait_cache_lab` | 应用可以用新鲜、奇偶校验的提示满足 quiet wait/no-op 路由；run-now 交付仍使用 CLI。 | 否 |
| 3 | `guard_projection_lab` | 应用可以在奇偶校验 evidence 之后仅为显式 opt-in 的 goal 投影紧凑 guard 用于 run-now 路由。 | 否 |
| 4 | `default_candidate` | 默认候选，在 evidence gate 与 rollout 决策通过前被阻塞。 | 否 |

启用必须显式、本地、可逆，例如未来的 registry 或应用设置：

```yaml
codex_app_control_plane_hook_cache:
  enabled: true
  level: advisory_hint_lab
  owner_decision_id: todo_publicsafe
```

LoopX 不应从 Codex App、heartbeat 或大载荷的存在推断启用。

## Evidence Gates

在级别 2 及以上之前：

1. **奇偶校验：** 至少 100 个采样 heartbeat 决策将 hook 快照与新鲜 `quota should-run` 输出对比，做到零误判运行、零误判 quiet-skip 决策。
2. **过期性：** 夹具与实时测试覆盖用户反馈、todo 变更、gate 变化、scheduler reset、workspace guard 变化与 run-history 实质转变。
3. **隐私：** public/private 扫描证明快照不包含原始活跃状态正文、聊天 transcript、本地路径、凭据、私有链接或原始 run-history 记录。
4. **回退：** 每个缺失、过期、畸形或不匹配的提示都触发正常 CLI 路径，并且回退决策本身不 spend quota。
5. **成本：** 测得的 prompt-token 与延迟节省足够实质，才值得额外 host-runtime 复杂度。
6. **Operator 评审：** owner 或 maintainer 记录 rollout 决策，命名启用的级别、回滚路径与监控指标。

在默认候选之前：

- evidence 必须包含多个 goal、至少一个 peer 任务 workspace guard、至少一个 user-gated goal、至少一个 monitor-only 等待，以及至少一个活跃 run-now goal；
- 默认必须在不迁移项目状态的情况下可逆；
- 纯 CLI 路径必须保持文档化并有测试。

## 回退 CLI 路径

回退保持：

```bash
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" \
  quota should-run --goal-id <goal-id> --agent-id <agent-id>
```

Worker 可以用 `jq` 或未来的 LoopX 命令请求紧凑本地摘要，但回退必须保留相同的 `interaction_contract`、`scheduler_hint`、`workspace_guard`、`goal_boundary` 与 todo 投影语义。

## 建议的第一个实验

只从级别 1 开始：

1. 在默认 heartbeat 路径之外添加一个 host 提供的紧凑快照夹具。
2. 在一个冒烟测试与一次手动 heartbeat canary 中把它与新鲜 CLI guard 对比。
3. 记录 token/延迟节省与每个不匹配。
4. 把全部交付、写回、发布与 quota spend 决策留在既有 CLI guard 上。

这给 LoopX 一条可度量的产品路径，同时不悄悄改变既有 Codex App heartbeat 的行为。
