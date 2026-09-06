# Status 数据契约

> [English](status-data-contract.md)

`loopx --format json status` 是给 Agent、heartbeat 作业、dashboard 与本地 UI
实验的稳定首屏数据契约。

该命令是导出：它读取 registry、紧凑 run 索引与公共/私有契约检查，
然后发出一个 JSON 对象。它不检查紧凑索引字段之外的私有 run payload，也不改动文件。
导出是 Agent 面向的机器状态。Dashboard 应消费该契约并翻译成人类 operator 视图，
而不是把原始 CLI 字段当作产品文案。
特别是，首屏 dashboard 应在把原始机器字段（如 `single_surface`、`focus_wait`、
`quota_slot_spent` 或并发片段）作为主要文案前，把它们翻译成 operator 语言。
机器令牌可以保留在下钻视图、日志或需要精确可调试性的 packet 中。

当命令在项目本地 `.loopx/registry.json` 外运行时，CLI 在存在时回退到
`~/.codex/loopx/registry.global.json` 的共享本地全局 registry。
该 registry 由 `connect` 与 `refresh-state` 自动维护，因此每个项目 Agent
可以更新自己的本地状态，而 dashboard 仍看到多项目视图。

对本地 dashboard，同一 JSON 形状可以经 loopback HTTP 提供：

```bash
loopx serve-status --global-registry --port 8766 --limit 80
```

该示例中的默认端点是 `http://127.0.0.1:8766/status.json`。
`--global-registry` 是 canonical 多项目 dashboard 模式：即使从项目 checkout
内启动，它也提供共享全局 registry，避免项目本地 registry 范围警告。
对项目本地调试，省略 `--global-registry` 或显式传项目 registry。服务器用于本地
dashboard 开发，并包含 CORS 头，因此另一个 localhost 端口上的 Vite App 可以获取它。
一次性 `loopx demo` 路径刻意在 `127.0.0.1:8765` 使用项目本地服务器；
它不把临时 demo 同步进共享全局 registry。

每个项目支撑的 `attention_queue.items[]` 行可以包含只读 `goal_channel_projection`
对象，`schema_version=goal_channel_projection_v0`。这是同一 status 条目的
dashboard/frontstage 投影：当前决策框架、用户与 Agent todos、quota、软声明、
紧凑 run 事件、来源警告与显式真相契约。它不是写 API。Dashboard 可以把它渲染为
通道卡片或时间线，但项目真相仍来自 registry、active state、quota guard 与
仅追加 run history。

行还可以包含可选 `task_graph_projection` 对象，
`schema_version=task_graph_projection_v0`。默认 `status` 热路径省略该图以保留
dashboard 接口预算；需要图的调用方可以用
`loopx --format json status --include-task-graph` 请求，或使用完整 review packet。
这是现有 todos、gates、leases、run ids 与事件 ledger 状态的紧凑图视图。
它只读，且只用于显示在平面 todo 列表中难扫描的依赖、验证、修复、审计、延续与
handoff 关系。它不得引入第二个 scheduler、图写 API、隐藏租约存储或替代任务真相。
协议定义在
[`docs/reference/protocols/task-graph-projection-v0.md`](reference/protocols/task-graph-projection-v0.md)；
消费方应在缺失时忽略该字段。

行还可以包含可选 `openviking_session_memory_adapter` 对象，
`schema_version=openviking_session_memory_adapter_v0`。这是给 OpenViking 风格
issue memory 的 public-safe 会话运行时特化：紧凑 issue refs、session refs、
memory refs、检索 gate、status 投影与证据投影。它只读，不得执行 live OpenViking
检索、写 memory、读 issue/comment 正文、摄入原始工具输出或轨迹，
或发布外部 issue comments/PRs。协议定义在
[`docs/reference/protocols/openviking-session-memory-adapter-v0.md`](reference/protocols/openviking-session-memory-adapter-v0.md)；
消费方应在缺失时忽略该字段。

行还可以包含可选 `local_agent_launch_plan` 对象，
`schema_version=local_agent_launch_plan_v1`。这是对已配置 Agent、角色分配、
非可执行启动预览行、status 投影、证据投影与未来 gate 的 dry-run 预览。
它只读，不得启动本地 worker、调用外部 Agent 服务、暴露 shell 命令、写 LoopX
状态或授予 host 权威。协议定义在
[`docs/reference/protocols/local-agent-launch-plan-v1.md`](reference/protocols/local-agent-launch-plan-v1.md)；
消费方应在缺失时忽略该字段。

Loopback status 导出包含 `status_contract.schema_version`。Dashboard 用该小协议
标记检测 checkout 推进后 `127.0.0.1:8766` 是否仍由更旧 daemon 或发布快照提供。
如果字段缺失或低于 dashboard 期望版本，产品 UI 应警告 operator
并指向安全重载路径：`scripts/macos-dashboard-launchagent.sh restart`。

同一本地 server 为 dashboard 奖励验证暴露 `POST /reward/dry-run`。
它接受所选 `goal_id`、`run_generated_at`、紧凑奖励字段与 public-safe 摘要文本，
然后返回 `appended=false` 的紧凑验证结果。它还返回与 CLI 相同的协调字段：
`active_state_summary` 与 `project_agent_visibility`。它不改 run 索引，
也不返回私有产物路径。

当 status 经 loopback HTTP 提供时，`/status.json` 还包含可选 `local_dashboard_api`
能力块。CLI status 导出可以省略它，因为它们是纯只读快照。该块是 dashboard 的
本地写便利能力机器契约：

```json
{
  "local_dashboard_api": {
    "source": "serve-status",
    "reward_dry_run_url": "/reward/dry-run",
    "reward_append_url": null,
    "reward_write_enabled": false,
    "configure_goal_dry_run_url": "/control-plane/configure-goal/dry-run",
    "configure_goal_apply_url": null,
    "control_plane_write_enabled": false
  }
}
```

已弃用的 dashboard 诊断路由在
`/deprecated/frontstage/ops?statusUrl=<relative-or-loopback>` 使用 TanStack
Query 支撑的本地 status 读取器。旧 `/frontstage?mode=ops` 形式重定向到该命名空间。
Showcase 模式仍忽略 `statusUrl`；只有显式的已弃用诊断路由可以获取 status 流。
查询层在信任 loopback 流前验证 `status_contract.schema_version`。如果流低于
dashboard 期望 schema 版本，路由用 `status_contract.reload_hint` 显示过期
daemon 修复文案，而不是静默渲染旧协议。

同一 frontstage 查询层把 `local_dashboard_api` 投影为能力，而不是浏览器权威。
它可以显示宣传了 reward dry-run 或控制面 dry-run URL，但除非流是相对或
loopback、匹配 URL 存在且对应 `*_write_enabled` 标志为 true，
写便利能力保持禁用。Frontstage 默认必须保持只读；任何未来写 UI 仍必须使用
预览锁定的本地 API，并把 CLI/事件 ledger 状态保持为真相源。

控制面设置写路径遵循与奖励追加相同的 opt-in 规则。默认 `serve-status`
通过 `POST /control-plane/configure-goal/dry-run` 验证 dashboard 设置草稿，
但不暴露 apply 能力。用 `--enable-control-plane-write-api` 启动 loopback server
暴露 `POST /control-plane/configure-goal/apply`；Dashboard 应只在
`local_dashboard_api.control_plane_write_enabled=true` 且 apply URL 存在时启用
Apply。Apply 请求必须复用 dry-run 响应中的新鲜 `preview_id`。

控制面设置草稿可以用 `multi_subagent_feature="enabled"` opt in 有界子 Agent
编排，或 `"off"` 保持默认单 Agent 模式。这是 registry `spawn_policy` 的产品
包装；dashboard 面应优先它，而不是暴露原始 `orchestration_mode` 加
`spawn_allowed` 开光。

## 命令

```bash
loopx --format json status > goal-status.json
```

默认 `status` 扫描 LoopX 安装根的公共/私有契约健康。
只有当你刻意想要 status 导出检查某个特定 public-safe 项目面时，
才使用窄扫描路径：

```bash
loopx --format json status \
  --scan-path README.md \
  --scan-path docs/ \
  --scan-path examples/
```

对计算分配，`loopx quota status` 与 `loopx quota plan` 从该同一 status payload
派生 Agent 面向分组。`loopx --registry "$HOME/.codex/loopx/registry.global.json"
quota should-run --goal-id <goal-id>` 从该分组为项目 heartbeat 派生每目标自动化
guard。这些是只读视图，不是独立真相源。脚本应把 quota-plan JSON 中的
`summary.next_automatic_turn` 当作建议，并仍尊重显示的健康、operator 与证据 gate。
每目标 guard 还发出 `heartbeat_recommendation`，一个针对首次只读映射运行与
安静映射 no-op 等通用生命周期情形的紧凑执行者提示。项目特定策略仍应来自 registry、
active state、adapter 输出或边界规则，而不是临时的 scheduler 提示分支。
Registry 条目还可以声明紧凑 `control_plane` 设置。这些设置是每目标策略，
不是全局提示文本。默认 `control_plane.self_repair.enabled=false`；
只有 registry 启用的目标能变健康或等待投影停滞为 `quota should-run` 自修复
机器契约。
当所选 attention 条目由 project asset 支撑时，每目标 guard 还携带紧凑
`handoff_readiness`，带 `handoff_status` 与 `post_handoff_run_seen`。
Heartbeat 作业因此能说出所选目标仍在等待目标 run，还是已见过 post-handoff 工作，
而无需解析完整 status payload。
对 replan，guard 携带 host 构建的 `replan_context_v0` 与紧凑
`replan_action_packet_v0`。上下文从 Agent 作用域证据历史投影有界覆盖 ledger、
未覆盖边界与 delivery 收据。执行模型因此从已交付上下文选择方向；
它不必发现并执行证据日志命令作为协议预检。
`loopx evidence-log --goal-id <goal-id> --agent-id <agent-id> --thin`
仍是冷路径诊断年表，其读收据对可观测性有用，但读或遗留 ACK 不能关闭 replan
义务。关闭需要针对当前义务接受的 typed 语义 delta：新面、假设、探针族、
有状态根基的可运行 successor、新鲜证据链接的 vision 路径、具体新 blocker 或
覆盖支撑的终态结果。可运行 successor 由一次携带确切 `replan_obligation_id` 的
`todo add` 记录；Todo 写是收据并返回细粒度 turn 边界，因此不需要第二个 ACK
命令。同一 goal-frontier reducer 被 quota 与 `refresh-state` 使用，
所以 vision/边界派生义务不能被维护分类或旧义务的 ACK 绕过。

对 turn 作用域可执行结算，`interaction_contract.cli_channel.replan_settlement_contract`
把该语义义务与该 Turn 的因果结算身份分开。它恰投影一个 `settlement_binding`。
当 quota 收据已拥有所选 Todo，refresh 与 spend 只使用 `--todo-id`；
replan 义务保持为由该 Todo 绑定 writeback 清偿的语义目标，
且不得作为第二个结算标志添加。无 Todo replan 则直接用
`--replan-obligation-id` 绑定义务。两条路径保留相同 typed 语义 delta 验证与
有序 refresh-then-spend 链。无 turn 身份的读保持紧凑，不投影可执行结算契约或
spend 动作。

同一 guard 可以包含 `work_lane_contract`。Schema `work_lane_contract_v1`
是 guard 一等 `interaction_contract` 下 monitor 与推进路由的兼容下钻。
它区分 `lane=continuous_monitor` 与 `lane=advancement_task`，携带下一 lane，
并暴露一个 `obligation` 字符串，如 `advance_unless_material_monitor_transition`。
Agent todo 条目可以包含 `task_class=advancement_task` 或
`task_class=continuous_monitor`，加可选 `action_kind`，如 `run_eval`、`validate`、
`rebuild`、`writeback`、`monitor` 或 `poll`。显式 `task_class` 对 todo 条目本身
权威；`task_class` 缺失时识别出的通用 `action_kind` 可以推断 lane；
遗留 todo 文本只是兼容 fallback。所选目标的 `next_action`/`recommended_action`
在点名可执行链（如收集重复、重建标签、重跑 scorer 或验证 eval gate）时，
仍可以把否则 monitor-only 的 todo 集提升回 `lane=advancement_task`。
隐藏开放 todos 当作推进工作而非 monitor-only 工作，因此截断的 top-N todo 投影
不能意外静默可执行积压。
对带开放 Agent todos 的依赖观察投影，guard 只在至少一个开放 todo 是推进类工作时
设置 `next_lane=advancement_task`、`must_attempt_work=true` 与
`reason_codes=["dependency_observation", "open_agent_todo"]`。
如果所有可见开放 todos 都是 monitor 类且没有隐藏开放 todo，guard 设置
`obligation=quiet_until_material_monitor_transition` 与 `must_attempt_work=false`。
一个窄例外防止长自主项目在完成最后一个可见 delivery todo 后停滞：当前
`next_action`/`recommended_action` 显式指向推进类可执行链时，
monitor-only todos 被提升为 `lane=advancement_task`，
`obligation=materialize_advancement_todo_or_blocker`。该义务要求 worker
创建具体推进 todo 或写 blocker，而不是安静等待 monitor。Heartbeat 推荐可以说
`follow_work_lane_contract` 或 `monitor_quiet_until_material_transition`，
但不应复述 lane 语义；未变化 monitor 轮询保持
`should_run=false` 与 `effective_action=monitor_quiet_skip` 的安静无 spend 检查，
而实质依赖状态转移在改变所选目标决策时可以写回一次。
当最终 Agent 作用域投影选择 `effective_action=agent_scope_wait` 等非执行等待时，
暴露的 `work_lane_contract` 也必须是不可执行的（`must_attempt_work=false`），
即使目标级下一动作否则会派生推进义务。原始目标级 lane 可以保持紧凑延迟诊断
上下文，但执行者不得把它当作竞争义务。
`handoff_readiness.handoff_interface_budget` 声明最小项目 Agent handoff 的机器可读
预算：`mode=project_agent_handoff`、`max_lines=16` 与 `max_chars=1800`。
`loopx review-packet --handoff-only --format json` 返回同一契约加实时
`line_count`、`char_count` 与 `within_budget`，使短 heartbeat 无需在提示文本携带
该规则即可拒绝 handoff 膨胀。
对 spend 记账，status 从当前 quota 窗口内的紧凑 `quota_slot_spent` 运行时事件
派生 `spent_slots`。Registry 保持为计算份额与窗口大小的策略源，而非 spend ledger。
`quota_slot_spent` 是 status 中性记账：它必须在 run history 中保持可审计，
但 status 与 attention queue 应使用最新非记账 run 作为当前工作状态。
更一般地，status 应暴露仅追加事件 ledger 上的投影，而不是充当 ledger 本身。
工作分类、人类奖励 overlay、operator-gate 恢复契约、quota spend 行、证据轮询、
blocker 写回与产物验证应保持为事件可审计；dashboard 与 heartbeat 提示消费这些
事件的紧凑投影做当前状态决策。
按 lane 说，`next_automatic_turn` 只能点名第一个合格目标；operator-gated、
focus-waiting、waiting、throttled、paused 与 health-blocked 目标必须留在合格
lane 外，即使它们有高 `quota.compute`。

## 顶层形状

```json
{
  "ok": true,
  "registry": ".loopx/registry.json",
  "runtime_root": "./runtime",
  "goal_count": 3,
  "run_count": 2,
  "goal_filter": null,
  "status_contract": {
    "schema_version": 2,
    "minimum_dashboard_schema_version": 2,
    "producer": "loopx status",
    "reload_hint": "scripts/macos-dashboard-launchagent.sh restart"
  },
  "contract": {
    "ok": true,
    "summary": {
      "errors": 0,
      "warnings": 0,
      "checks": 4
    },
    "errors": [],
    "warnings": [],
    "checks": [
      "registry goals checked: 3",
      "runtime indexes checked: 3",
      "run-history goals=3 runs=2",
      "public boundary scan clean: 12 files"
    ]
  },
  "global_registry": {
    "available": true,
    "ok": true,
    "registry": "~/.codex/loopx/registry.global.json",
    "current_registry": ".loopx/registry.json",
    "current_registry_is_global": false,
    "global_goal_count": 4,
    "current_goal_count": 3,
    "source_registry_count": 2,
    "summary": {
      "high": 0,
      "action": 0,
      "info": 1,
      "checks": 2,
      "findings": 1
    },
    "findings": [],
    "checks": []
  },
  "attention_queue": {
    "available": true,
    "item_count": 2,
    "needs_user_or_controller": 1,
    "needs_controller": 0,
    "needs_codex": 1,
    "watching_external_evidence": 0,
    "watching_monitor": 0,
    "autonomous_backlog_candidates": {
      "source": "attention_queue.agent_todos",
      "open_count": 1,
      "task_class": "advancement_task",
      "items": [
        {
          "goal_id": "loopx-meta",
          "quota_state": "eligible",
          "priority": "P1",
          "todo_index": 1,
          "task_class": "advancement_task",
          "text": "Add an autonomous backlog candidate surface for eligible goals.",
          "source": "agent_todos"
        }
      ]
    },
    "items": []
  },
  "run_history": {
    "available": true,
    "goal_count": 3,
    "run_count": 2,
    "goals": [],
    "recent_runs": []
  },
  "event_ledger_summary": {
    "available": true,
    "source": "run_history",
    "sample_run_count": 2,
    "proxy_note": "append-only run-history projection; compact event-class counts only",
    "event_classes": ["accounting", "decision", "evidence", "state", "work"],
    "totals": {
      "events_24h": 2,
      "events_7d": 2,
      "by_class_24h": {
        "accounting": 1,
        "decision": 0,
        "evidence": 0,
        "state": 1,
        "work": 0
      },
      "by_class_7d": {
        "accounting": 1,
        "decision": 0,
        "evidence": 0,
        "state": 1,
        "work": 0
      }
    },
    "goals": []
  },
  "promotion_readiness_summary": {
    "available": true,
    "source": "runtime_release_ledger",
    "evidence_scope": "runtime_release",
    "goal_id": null,
    "dashboard_readiness": "passed",
    "generated_at": "2026-06-01T00:08:00+00:00",
    "classification": "canary_promotion_readiness_smoke_group",
    "delivery_batch_scale": "multi_surface",
    "delivery_outcome": "primary_goal_outcome",
    "json_exists": true,
    "markdown_exists": true,
    "freshness_window_hours": 24,
    "freshness_status": "fresh",
    "is_fresh": true,
    "requires_readiness_run": false,
    "age_seconds": 120,
    "age_hours": 0.03,
    "sample_run_count": 1,
    "proxy_note": "canary promotion-readiness projection from the runtime release ledger with legacy goal-history fallback; exact evidence stays in append-only artifacts"
  },
  "promotion_gate": {
    "ok": true,
    "gate": "promotion_readiness",
    "gate_state": "ready",
    "can_promote": true,
    "should_warn": false,
    "non_blocking": true,
    "recommended_action": "promotion readiness is fresh",
    "readiness": {
      "freshness_status": "fresh",
      "requires_readiness_run": false
    }
  },
  "decision_freshness_summary": {
    "available": true,
    "source": "run_history",
    "sample_run_count": 2,
    "window_days": 7,
    "proxy_note": "checkpointed decision freshness projection; rebase old decisions at the decision point before reuse",
    "summary": {
      "decision_count": 1,
      "stale_count": 0,
      "rebase_required_count": 1,
      "fresh_count": 0
    },
    "items": [
      {
        "goal_id": "loopx-meta",
        "decision_kind": "operator_gate",
        "decision_at": "2026-06-01T00:05:00+00:00",
        "classification": "operator_gate_approved",
        "age_days": 0.2,
        "stale_by_age": false,
        "newer_event_count_7d": 1,
        "newer_event_classes_7d": {
          "accounting": 1,
          "decision": 0,
          "evidence": 0,
          "state": 0,
          "work": 0
        },
        "freshness_state": "rebase_required",
        "requires_decision_point_rebase": true,
        "reason": "newer sampled events exist after decision; rebase at decision point"
      }
    ]
  },
  "usage_summary": {
    "available": true,
    "source": "run_history",
    "sample_run_count": 2,
    "proxy_note": "run-history proxy; carries aggregate token/cost/duration, excludes raw thread logs",
    "totals": {
      "runs_24h": 2,
      "runs_7d": 2,
      "quota_spend_slots_24h": 1,
      "quota_spend_slots_7d": 1,
      "automation_run_count_24h": 1,
      "automation_run_count_7d": 1,
      "progress_signal_run_count_24h": 1,
      "progress_signal_run_count_7d": 1
    },
    "goals": []
  }
}
```

默认 `loopx status` 是多目标 dashboard/控制面视图。`loopx status --goal-id <goal-id>`
保留 `global_registry` 等全局健康字段，而其 `contract` 投影只包含全局错误
加归所选目标所有的错误。它还把 `attention_queue`、`run_history`、
`event_ledger_summary`、`usage_summary` 与 `todo_index` 等 goal 作用域区块聚焦到
请求目标。Agent 需要单目标更丰富推理 packet 时用
`loopx diagnose --goal-id <goal-id>`。

消费方应把未知字段当作附加的。首屏 UI 的必需字段是 `ok`、`contract` 与
`attention_queue`。`status_contract`、`event_ledger_summary`、
`promotion_readiness_summary`、`promotion_gate`、`decision_freshness_summary`
与 `usage_summary` 是可选的，应视为紧凑协议或 run-history 投影，
而不是 ledger 本身、权威计费遥测或发布操作源。`usage_summary` 在 run 报告 typed
`run_usage_v0` 使用行时携带聚合 token/成本/时长，但它仍是 run-history 代理，
不是计费记录。畸形、负或非有限 usage 在摄入/读取时 fail closed，
而不是显示为零。缺失 `status_contract` 表示更旧 status producer；
loopback dashboard 应把它作为 daemon 新鲜度警告显示，
而不是静默隐藏较新面板。

## 接口预算 Cadence

当 run-history 记录包含 `interface_budget_cadence` 时，`loopx status`
在 `attention_queue.items[].project_asset.interface_budget_cadence` 投影其紧凑副本。
对所选目标，`quota should-run` 还在顶层镜像同一对象为
`interface_budget_cadence`。

该字段是 heartbeat worker 的约束信号，不是 dashboard 功能请求。
它记录最新干净热路径预算检查、观察到的最紧余量，与下次检查到期时间。
新鲜干净检查只有在最紧指标仍有正余量时才能支持接口预算 guard 的安静跳过；
过期、超预算或零余量检查应提示运行 `python3
examples/control_plane/hot-path-interface-budget-smoke.py` 或等效显式漂移检查。

稳定字段：

- `checked_at`
- `freshness_hours`
- `next_check_due_at`
- `overdue`
- `within_budget`
- `surface_count`
- `minimum_headroom_ratio`
- `tightest_surface`
- `tightest_metric`
- `headroom_remaining`
- `recommendation`

## 晋升 Gate JSON

`loopx promotion-gate --format json` 是本地发布晋升的紧凑机器可读 gate。
它读取与 `doctor`、`status` 与 `install-local.sh` 相同的仅追加就绪事件，
然后返回小操作结果，脚本可以断言而无需解析安装器 stderr。

该命令只读且非阻塞。`can_promote=false` 表示安装器应在晋升前警告，
而不是 CLI 拒绝安装。警告保持人类面向护栏；自动化应使用 `gate_state`、
`can_promote`、`should_warn` 与 `readiness.freshness_status` 作为稳定字段。
`loopx status --format json` 在 `promotion_gate` 下嵌入同一紧凑结果，
因此 dashboard 面板、安装器 smoke 与 CLI gate 检查消费一个状态契约，
而不单独重新派生发布就绪状态。

发布检查通过后，canary 使用显式写边界：

```bash
loopx promotion-readiness record \
  --dashboard-readiness passed \
  --execute
```

不带 `--execute`，该命令只预览运行时级追加。Canary 只在显式 dashboard 省略时
提供 `skipped`；存在 dashboard 来源时依赖失败不得记录为 `passed`。

新鲜形状：

```json
{
  "ok": true,
  "registry": ".loopx/registry.json",
  "runtime_root": "~/.codex/loopx",
  "gate": "promotion_readiness",
  "gate_state": "ready",
  "can_promote": true,
  "should_warn": false,
  "non_blocking": true,
  "recommended_action": "promotion readiness is fresh",
  "readiness": {
    "available": true,
    "source": "runtime_release_ledger",
    "evidence_scope": "runtime_release",
    "goal_id": null,
    "dashboard_readiness": "passed",
    "classification": "canary_promotion_readiness_smoke_group",
    "freshness_status": "fresh",
    "requires_readiness_run": false,
    "freshness_window_hours": 24,
    "json_exists": true,
    "markdown_exists": true
  }
}
```

缺失或过期形状：

```json
{
  "ok": true,
  "gate": "promotion_readiness",
  "gate_state": "warning",
  "can_promote": false,
  "should_warn": true,
  "non_blocking": true,
  "recommended_action": "python3 examples/canary/canary-promotion-readiness-smoke.py",
  "warning_message": "promotion-readiness evidence is stale; ...",
  "readiness": {
    "freshness_status": "stale",
    "requires_readiness_run": true
  }
}
```

`warning_message` 刻意人类面向且可能变化。它存在让
`scripts/install-local.sh` 保留 operator 警告，但自动化应优先上面的结构化字段。

## 全局 Registry 健康

`global_registry` 是本地多项目健康面。即使当前命令指向项目本地 registry，
它也检查共享 `registry.global.json`，使 dashboard 用户能在 registry 范围问题
变成幽灵项目之前看到它们。

健康发现紧凑且仅本地。它们可以在开发机导出中包含本地文件系统路径，
所以在机器外不要发布原始本地 status JSON。

Registry 边界应用以下检查：

```bash
loopx registry-boundary --path <registry.json> --require-gitignored
```

共享 `registry.global.json` 分类为 `shared_local_registry` 且不得 push。
项目 `.loopx/registry.json` 文件是 `project_local_private_registry`。
生成的 public-safe registry 投影默认仍是运行时产物：它们对评审或 handoff 有用，
但除非文件是 `examples/` 下显式编写的示例 fixture，
`github_push_allowed=false`。Dashboard/status JSON 因此应把 registry 数据当作
本地控制面视图，而不是仓库产物。

发现形状：

```json
{
  "kind": "stale_source_registry",
  "severity": "action",
  "goal_id": "project-main-control",
  "message": "`project-main-control` source registry changed after its last global sync",
  "recommended_action": "run `loopx sync-global --goal-id project-main-control` from the source project",
  "path": "/path/to/project/.loopx/registry.json"
}
```

当前发现种类：

- `duplicate_goal_id`：全局 registry 对同一目标 id 包含多个条目；
  这是高严重度，因为路由有歧义。
- `source_registry_missing`：全局条目指向一个不再存在的来源 registry。
- `stale_source_registry`：来源 registry 在最后记录的 `synced_at` 后变化，
  因此全局条目可能过期。
- `state_file_missing`：目标声明的 active state 文件不再存在。
- `state_file_not_declared`：全局条目没有持久 active state 文件。
- `current_registry_scope_excludes_global_goals`：信息性提醒——项目本地 registry
  视图排除了共享全局 registry 中存在的目标。

高与 action 发现也被提升进 `attention_queue.items`，`source=global_registry`；
信息性范围发现留在全局 registry 面板，使本地项目视图不嘈杂。来源 registry
出处发现（`source_registry_missing` / `stale_source_registry`）在存在时被塌缩进
同一 `goal_id` 的 live quota-backed 队列条目，位于
`global_registry_shadow_findings`，因此过期来源影子不会成为第二个 quota 健康
blocker，同时该事实在 `global_registry.findings` 中保持可见。

## 契约健康

`contract.ok=false` 表示 UI 在鼓励更多 adapter 工作前应显示阻塞健康状态。

摘要计数器刻意小：

- `errors`：应阻塞进度的边界或 registry 问题。
- `warnings`：值得在次级健康面板显示的非阻塞问题。
- `checks`：成功观察，对审计轨迹有用。

`error_diagnostics` 是错误归属的真相源。每行有稳定 `code`、人类可读 `message`，
以及 `scope=global` 或带 `goal_id` 的 `scope=goal`；已知子集共享的发现可以用
`scope=goals` 加 `goal_ids`。Registry 解析失败、歧义目标身份、registry 边界违规与
公共边界违规是全局的。Goal 条目、active-state 与 todo 契约失败归产生它们的
目标或已知目标集所有。

`errors`、`global_errors` 与 `goal_errors` 是从那些结构化诊断派生的兼容投影；
消费方不得从消息前缀推断归属。`warnings` 与 `checks` 保持短字符串。
Checks 应足够具体支持 operator 决策，而不暴露本地路径或私有证据。
项目在本地机器外暴露该导出前，它们必须 public-safe。

## Attention Queue

Attention queue 按 LoopX status 逻辑排序。UI 应把它渲染为主要工作列表。

计数器：

- `item_count`：所有可见队列条目。
- `needs_user_or_controller`：等待人类用户或目标 controller 的条目。
- `needs_controller`：等待目标 controller 或 adapter 连接的子集。
- `needs_codex`：准备好接受 Codex 动作的条目。
- `watching_external_evidence`：应监控但直到外部证据变化才行动的条目。
- `watching_monitor`：保持可见而不暗示立即 Codex 工作的 monitor-only 条目。

条目形状：

```json
{
  "goal_id": "complex-project-main-control",
  "status": "ready_for_controller_opt_in",
  "lifecycle_phase": "controller_gated",
  "lifecycle_flags": [
    "controller_gated",
    "adapter_inspected"
  ],
  "waiting_on": "user_or_controller",
  "severity": "action",
  "recommended_action": "先在 LoopX 完成 operator 判断；同意后项目 Agent 只执行 read-only map dry-run",
  "project_asset": {
    "owner": "user_or_controller",
    "gate": "operator_question",
    "next_action": "先在 LoopX 完成 operator 判断；同意后项目 Agent 只执行 read-only map dry-run",
    "stop_condition": "record aligned eval evidence and one human reward event",
    "user_todos": {
      "open": 1,
      "done": 2,
      "total": 3,
      "next": "Record the owner/SOP conclusion in the review worksheet."
    },
    "agent_todos": {
      "open": 1,
      "done": 0,
      "total": 1,
      "next": "Run the read-only validation map after approval."
    },
    "quota": {
      "compute": 0.5,
      "state": "operator_gate",
      "spent_slots": 0,
      "allowed_slots": 720,
      "reason": "operator gate blocks gated delivery"
    },
    "latest_validation": {
      "generated_at": "2026-06-02T12:00:00+00:00",
      "classification": "ready_for_controller_opt_in",
      "summary": "read-only map available; write-control not approved"
    }
  },
  "handoff_readiness": {
    "ready": false,
    "codex_ready": false,
    "source": "project_asset",
    "quota_state": "operator_gate",
    "handoff_status": "not_ready",
    "post_handoff_run_seen": false,
    "checks": {
      "project_asset_backed": true,
      "same_source_should_run": true,
      "codex_ready": false,
      "handoff_has_next_action": true,
      "handoff_has_stop_condition": true,
      "handoff_sanitized_surface": true
    },
    "next_probe": "loopx review-packet --goal-id complex-project-main-control --handoff-only"
  },
  "operator_question": "是否同意 `complex-project-main-control` 先执行 read-only map opt-in？",
  "agent_command": "loopx read-only-map --goal-id complex-project-main-control --dry-run",
  "quota": {
    "compute": 0.5,
    "window_hours": 24,
    "slot_minutes": 1,
    "allowed_slots": 720,
    "spent_slots": 0,
    "state": "operator_gate",
    "reason": "planned goal needs operator opt-in before spending agent turns"
  },
  "source": "latest_run",
  "controller_stage": "ready_for_read_only_not_decision",
  "missing_gates": [
    "human_reward_capture",
    "aligned_eval_decision_evidence"
  ],
  "next_handoff_condition": "record aligned eval evidence and one human reward event"
}
```

条目字段：

- `goal_id`：来自 registry 或运行时的稳定目标标识符。
- `status`：adapter 分类或派生状态。
- `lifecycle_phase`：用于首屏可视化的派生 state 交互阶段。
- `lifecycle_flags`：适用于最新状态的所有紧凑阶段。
- `waiting_on`：`user_or_controller`、`controller`、`codex`、`external_evidence`
  或 `monitor_signal`。
- `severity`：`high`、`action` 或 `watch`。
- `recommended_action`：恰好一个下一动作。
- `project_asset`：从同一条目派生的紧凑控制面投影。它必须携带 `owner`、`gate`、
  `support_mode`、`next_action` 与 `stop_condition`，并可以包含紧凑 `user_todos`、
  `agent_todos`、`quota` 与 `latest_validation` 摘要。Registry 支撑的项目资产还包含
  `execution_profile`（`loopx connect` 创建的项目级 delivery floor）与
  `orchestration`（registry `spawn_policy` 的紧凑投影，带 `mode`、`spawn_allowed`、
  `max_children` 与可选 `allowed_domains`）。它们还可以包含 `control_plane`
  （self-repair 等设置的紧凑每目标策略投影）与 `stale_latest_run_warning`
  （当前 active-state 文件看起来比最新 run 捕获的状态投影更新或不同）。
  该警告是修复提示，不是 scheduler gate：消费方应在信任 latest-run 派生路由前
  运行 `refresh-state`，而 quota 资格仍来自 quota guard。当编排模式是
  `multi_subagent` 时，项目资产还可以包含 `subagent_activity`，从 run history
  派生的紧凑子 run 投影。它记录子 run id、角色、状态、父链接、public-safe 作用域
  摘要与 quota-spend 计数，仅供观察；它不是锁服务或写仲裁器。
  这是 Agents 与 dashboard 的首屏项目资产面；它让消费方避免从分散字段重建
  owner、gate、support mode、下一动作、停止条件、todo 计数、计算状态与最新验证。
  它还让 delivery-floor 与编排策略贴近项目资产，而不强迫 Agent 从历史推断。
  `support_mode` 是紧凑产品模式标签：`read_only_observer`、`decision_support`、
  `reward_capture` 或 `selective_assist`。它描述当前 operator/Agent 关系；
  不是权限位，也不覆盖 `gate`、`quota` 或 `agent_command`。当已批准的
  `agent_command` 存在且 public-safe 时，`project_asset.next_safe_command`
  可以重复该命令，使首屏 dashboard 与 handoff packet 无需扫描顶层队列字段
  即可显示下一个可执行本地步骤。
  建议性 dreaming 输出可以包含 `dreaming_proposal` 与 `dreaming_lane_badge`。
  proposal 携带紧凑理由与晋升要求；badge 只为 UI/heartbeat 消费方携带路由事实：
  `lane=dreaming`、`advisory=true`、`interrupts_delivery=false`、
  `review_required=true`、`execution_allowed=false`、
  `delivery_spend_allowed=false` 与 `promoted_to_delivery=false`。
  消费方应把 badge 渲染为单独 Dreaming lane 或次级徽章，
  且不得把它当作 delivery 授权。
  Markdown 渲染器应在可用时把第一个未完成的用户与 Agent todo 包含在这里，
  使热路径读者无需扫描详细 todo 区块。更丰富的顶层 `user_todos`、`agent_todos`
  与 `quota` 字段保持供详细视图。
- `goal_boundary.peer_task_coordination`：可选 quota-only 协调权威。
  它只在 registry 显式选择 `coordinator_agent_id` 时出现。已注册 peers
  否则独立；子 spawn 策略不暗示已注册 peer 协调权威。被阻塞的显式 bundle
  不取代协调者自己的可运行 Todo；无本地 fallback 时它投影
  `interaction_contract.mode=peer_coordination_blocked`，
  使 scheduler 直到实质协调输入变化才停止。
- 当前路由权威：消费方应从 `attention_queue.items` 及其 `project_asset` 选择
  当前 owner、gate、等待方与下一动作。`run_history.latest_runs` 是证据与下钻面；
  它可能受 status 命令上限或过滤器限制，所以消费方不得用它作为判断 gate
  仍待决或已批准的单独来源。
- `handoff_readiness`：可选项目资产一致性与 follow-through 摘要。`ready=true`
  表示当前队列条目在同一来源、quota、next-action、stop-condition 与公共安全检查下
  可被 Codex 运行。`handoff_status=ready_waiting_for_run` 表示 handoff 就绪或
  已批准，但紧凑历史窗口内没有出现后续非记账 run。
  `handoff_status=post_handoff_run_seen` 表示存在较新非中性 run；
  `post_handoff_latest_run` 按时间戳与分类识别该最新已见 run，
  而 `delivery_batch_scale` 标记观察到的 delivery 是 test-only、single-surface、
  multi-surface、implementation 形状还是未知。Delivery scale 与 outcome 只来自
  显式 typed 字段。分类名、健康文本、推荐与证据对象的存在性绝不建立 delivery
  语义。`delivery_turn_kind` 来自显式 kind、显式 outcome 或被现有结算谓词接受的
  作用域 typed blocker 观察。`outcome_gap` 单独不证明 blocker writeback。
  `post_handoff_recent_runs` 是最近 post-handoff 工作 run 的紧凑最新优先切片。
  `post_handoff_small_scale_streak` 只计开头显式 `test_only` / `single_surface`
  scale；unknown 打断连续段。显式 `delivery_outcome` 值是 `outcome_progress`、
  `surface_only`、`outcome_gap` 与 `primary_goal_outcome`。缺失或无效历史语义保持
  unknown。无 floor 配置时缺失 outcome 保留内部 `not_configured` 哨兵，
  并从紧凑 run 省略。遗留 outcome-marker/hint 列表保留 floor 配置兼容性，
  但其词不再分类 run。配置该 floor 后，`post_handoff_outcome_gap_streak`
  只计连续显式 `surface_only` / `outcome_gap` outcome；unknown 打断连续段。
  Follow-through 义务需要 typed 字段，从不叙事推断。新 delivery 声明使用现有
  writer 枚举字段；不带 delivery 声明的 state-only refresh 保持合法。这刻意改变
  以前从旧未类型标签推断的决策，而不重写 run history。`quota_slot_spent` 事件
  不算 post-handoff 工作。
- `operator_question`：可选的、要在 LoopX operator 视图显示的人类面向 gate。
  这是用户/controller 判断的 canonical 位置。
- `agent_command`：operator gate 获批后目标项目 Agent 的可选命令或指令。
  Dashboard 消费方不应单独把它当作批准。
- `quota`：可选紧凑计算配额状态。它应摘要计算份额（`1.0`、`0.5`、`0.3` 或 `0`）、
  资格、近期 spend 与 public-safe 理由，而不暴露私有证据。见
  [quota-allocation.md](quota-allocation.md)。
- `control_plane`：该目标的可选紧凑 registry 策略。当前设置包括
  `self_repair.enabled`、`self_repair.allow_health_blocker_repair` 与
  `self_repair.allow_waiting_projection_repair`。缺失设置表示默认关闭，
  因此普通目标保持在现有 skip/wait lane。
- `user_todos`：从 active state 的 `## User Todo ...` /
  `## Owner Review Reading Queue` 区块解析的可选复选框摘要。Dashboard 消费方应把
  第一个未完成条目渲染为人类面向下一步，同时把 `recommended_action` 保持为路由
  上下文。紧凑 `project_asset.user_todos` 投影保留遗留 `next` / `next_index`
  字段，还可以包含至多三个未完成 `items` 供需要超过第一个开放 todo 的薄 worker。
- `agent_todos`：从 `## Agent Todo`、`## Codex Todo` 或 `## Project Agent Todo`
  解析的可选复选框摘要。Agent 面向消费方可以在 gate 与 quota 允许执行后用它选择
  实现工作；它不是用户批准信号。Status、quota 与 review-packet 投影应保留至多
  三个未完成 agent todo 条目，使短 heartbeat 不把"第一个可见条目"与整个积压混淆。
  Todo 摘要还暴露推进类工作的 `first_executable_items` 与持续 monitor 工作的
  `monitor_open_items`；可执行条目是主动作面，而 monitor 条目是补充上下文，
  除非记录实质转移或 blocker，否则不应消耗所选目标的推进槽位。
- `issue_meta_surface`：从 active-state `## Issue Meta Surface` 区块解析并镜像到
  `project_asset.issue_meta_surface` 的可选 public-safe issue/PR 锚点投影。
  Schema `issue_meta_surface_v0` 携带有界紧凑 `issue_meta_surface_item_v0` 行列表，
  带 `repo_handle`、`issue_handle`、GitHub 风格 `labels`、`owner_route`、
  `related_code_hint`、`validation_surface`、`promotion_target`、`status` 与
  `freshness`。它是 issue/PR 求解器锚点的场景状态面，
  不是读私有来源、发布评论或打开 PR 的命令。
- `capability_gate`：从声明显式 `required_capabilities` 的可见可执行 agent todos
  派生的可选每目标 quota 投影。当 `action=run` 时，gate 投影
  `runnable_candidates` 与 `blocked_candidates`；`decision_owner=agent`
  表示 Agent 在 steering audit 期间从可运行集选择实际 todo。Gate 不得把
  `recommended_action` 重写为单一所选 todo。`required_capabilities`
  表示直接执行该 todo 的前置条件，而不是 todo 试图构建的能力。Todo 可以单独声明
  它开发、修复、物化或 parity 检查的能力的 `target_capabilities`。
  目标能力不是硬 gate。如果目标 bridge（如 `benchmark_runner`）缺失，
  候选仍可出现在 `runnable_candidates`，带 `capability_repair_mode=true`、
  `capability_action=repair_bridge` 与候选上 `missing_target_capabilities`。
  当没有可见可执行候选可运行，gate 拥有决策并返回 `repair_bridge`、`ask_owner`
  或 `skip`，带具体缺失能力细节。
- `project_asset.todo_projection_gap`：status 无法为已连接项目投影 `user_todos`
  与/或 `agent_todos` 时发出的可选显式缺口对象。这表示"首屏 todo 状态未知"，
  不是"零 todos"。消费方应在把项目资产视为首屏完整前表露缺失角色，
  并请求可解析的 active-state todo 区块或状态文件修复。
- Todo 摘要使用 `schema_version=todo_summary_v0`；解析的 todo 条目使用
  `schema_version=todo_item_v0`。来源 active state 可以保持普通 Markdown 复选框，
  但 status/quota/dashboard 消费方应在存在时优先结构化条目字段：`todo_id`、
  `role`、`status`、`priority`、`title`、`archive_state`、`source_section`、
  `index`、`text`、`task_class`、`action_kind`、`note`、`evidence`、`reason`、
  `completed_at`、`updated_at`、`superseded_by` 与 `claimed_by`。Todo 摘要还可以暴露
  `claimed_open_count` 与 `unclaimed_open_count`，使 dashboard 与 heartbeat 调度器
  显示软归属而不推断锁。`claimed_by` 是通过 todo CLI 写入的可见性提示，
  不是租约或权限授予；claim id 必须在目标的 coordination 契约上注册，
  且 Agent 仍必须遵守 quota、gate、写作用域检查与其自动化/handoff 作用域。
  `todo_id` 由 todo CLI 写入时一等；无元数据的遗留 Markdown 仍从当前条目文本
  与区块获得解析器派生兼容 id，第一个生命周期命令把该 id 物化回元数据。
  第一个开放条目仍可通过 `first_open_items` 供更旧 heartbeat。Frontstage 消费方
  不应把该 top-N scheduler 视图当作整个积压。Todo 摘要还可以投影可见性 lane：
  按优先级排序的未声明候选 `unclaimed_priority_open_items`、
  可能在 top-N 外的已声明工作 `claimed_open_items`、已声明可执行 delivery 工作
  `claimed_advancement_open_items` 与已声明持续 monitor 工作
  `claimed_monitor_open_items`。Agent 感知 quota/status 投影可以进一步包含
  `current_agent_claimed_open_items`、`current_agent_claimed_advancement_items`、
  `current_agent_claimed_monitor_items` 与 `claimed_by_others_items`。
  Scheduler 仍可以从更窄可执行候选集选择；dashboard/frontstage 用这些 lane 保持
  归属可见。可见性 lane 可以宽于 scheduler lane，但保持有界；默认 Agent 面上限
  是每 lane 16 条。消费方应用对应计数指示当前 payload 中扩展的已声明工作
  多于显示，而更丰富 frontstage 视图应使用未来分页/过滤投影，
  而不是强迫更大 heartbeat payload。
  Canonical todo 下钻契约是 `docs/reference/protocols/todo-detail-cold-path-v0.md`：
  热路径摘要可以只为单个选定条目携带紧凑 `todo_detail_ref_v0` 指针，
  而完整笔记、证据摘要、相关生命周期引用与页令牌留在 `todo_detail_cold_path_v0`
  冷路径响应。Status、quota、heartbeat 与 handoff payload 不得为让隐藏积压可见
  而内联完整 todo 细节。
  当已声明 lane 超过上限时，生产者应避免原始 top-N 截断。按优先级与来源位置排序，
  按 `claimed_by` 分组，取每 claimant 公平切片，然后用排序余量填补剩余槽位。
  Agent 作用域投影随后应把聚焦排序为当前 Agent 已声明条目、未声明条目与较低权重
  其他 Agent 已声明条目。其他 Agent 声明是可见性上下文与最后候选；
  它们不是硬锁，但也不应胜过当前 Agent 自己的已声明工作或未声明工作。
  延迟 todos 在排序开放 todo lane 后，经 `deferred_items` 与（满足机器可读恢复
  条件时）`deferred_resume_candidates` 投影。这是 gate-resume lane，
  不是无候选证据也不是可执行积压。默认延迟可见性上限是 8 条。解析的延迟条目
  可以包含 `resume_when`、`resume_condition` 与 `resume_ready`；消费方在生命周期
  命令重新打开或替代该 todo 前不得把它们并入 `first_open_items` 或可执行积压。
  Agent 作用域 quota 可以把就绪候选进一步分成
  `current_agent_deferred_resume_candidates`、`unclaimed_deferred_resume_candidates`
  与 `other_agent_deferred_resume_candidates`，其中只有前两个能在允许 Agent 作用域
  无候选等待前唤醒当前 peer。
  开放 todos 也可以携带 `resume_when`；status 应附 `resume_condition` /
  `resume_ready`，但把条目留在可执行积压外直到 `resume_ready=true`。
  `monitor_changed:<todo_id>` 条件还携带 `resume_monitor_generation`，
  而目标 monitor 携带单调 `material_change_generation`；就绪要求后者严格更大。
  这让 Agent 看到尚未解锁的 successors，而不会误选为当前工作或在未变化/重放
  monitor 结果上唤醒。
  未来可选字段如 `created_at`、租约 TTL、依赖或证据链接应扩展该条目形状，
  而不是发明另一个 todo 面。
- Agent 作用域 quota payload 可以包含 `agent_todo_summary.claim_scope`，
  `schema_version=agent_claim_scope_v0`。Quota guard 应先选当前 Agent 声明的 todos，
  再选未声明 todos，然后暴露其他 Agent 声明的 todos 为较低权重候选。兼容 payload
  仍可包含 `blocked_claimed_items`，但新消费者应优先 `other_agent_claimed_items`
  与 `other_agent_claimed_open_count`。这是 claim 感知路由，不是硬租约：
  每个 peer 可以检查目标级积压，而声明、任务策略、能力与边界决定它可以执行什么。
  即使 active state 全局 `Next Action` 点名另一个 peer 的 lane，当前 Agent 声明的
  todo 仍可被选中；那不是状态投影不匹配。
- Agent 作用域 quota payload 还暴露版本化 `task_scope` 枚举
  `goal_all_read_claimed_run_global_read_v0`。它表示 peer 可以读取当前目标的所有
  普通 todo、可以考虑自己的声明或合格未声明候选、执行前必须声明，
  且只能执行其声明的合格 todo。其他 Agent 声明仅诊断。跨目标读保持目标本地路由外，
  需要显式只读 global-manager 清单（如 `loopx global-summary`）；
  它们从不授予跨目标执行。现有 goal、agent 与冷路径命令字段提供绑定参数，
  而不复制它们。TurnEnvelope 保留该紧凑枚举，使模型看到与完整 quota 决策相同的
  边界。
- `dependency_blockers`：来自其他当前 attention-queue 目标的未完成用户 todos 的
  可选紧凑摘要。这让 dashboard 与 heartbeat 调度器把兄弟/项目依赖 gate 与当前目标
  自己的 `user_todos` 分开显示；它只是可见性上下文，不得单独改变当前目标的 quota
  或 owner 决策。
- 本地 active-state 文件路径被刻意从队列条目省略。它们是有用调试/来源元数据，
  但 public-safe status 队列应用 `goal_id`、项目资产状态与紧凑 todos 识别工作，
  而不是暴露机器特定路径。
- `source`：`contract`、`registry`、`run_history` 或 `latest_run`。
- `controller_stage`：来自最新 run 的可选紧凑 controller 就绪分类。
- `missing_gates`：可选的 public-safe gate id，说明目标为何还不能推进到下一
  controller 阶段。
- `next_handoff_condition`：推进 controller handoff 的可选 public-safe 条件。

`status=unregistered_runtime_goal` 在运行时拥有一个不在 registry 中的可执行目标时
发出。Dashboard 消费方应把它显示为 controller 工作：目标活跃则注册它，
目标陈旧则归档运行时记录。Watch-only 遗留记录保持 run history 可见而不进队列。

`status=state_refreshed` 在最新紧凑 run 来自 `loopx refresh-state` 时对注册目标
发出。Dashboard 消费方应把它显示为 Codex-ready 工作：controller 状态已变，
下一个 Agent turn 应在继续前检查刷新后的 active state。
如果刷新命令未带 `--recommended-action` 运行，紧凑 `recommended_action` 应是
刷新 active state `## Next Action` 的第一个本地控制面条目，包括换行续行；
只有该持久区块缺失时才回退到第一个开放 Agent Todo，最后到通用刷新通知。该字段
可以携带稳定本地路由引用，如 todo id、分支名、agent id、PR refs 或私有材料指针，
因为它服务单 operator 的本地 loop。它不得携带凭据、认证头或内联秘密。
公共/导出槽负责在渲染可分享面前脱敏或省略本地/私有引用。记录包含
`recommended_action_source`（`explicit_arg`、`active_state_next_action`、
`agent_todo_fallback` 或 `default_refresh_action`），使消费方区分 run 指导、
持久状态投影与最后手段兼容 fallback。
`--recommended-action` 描述追加的 run 记录；它不重写 active state 的持久
`## Next Action`。在多 Agent 目标中刻意改变该持久路线时，注册 peer 必须运行
`refresh-state --agent-id <registered-peer> --progress-scope goal --next-action
<local control-plane action>`。Status 投影可以暴露
`active_state_next_action` 与 `latest_run_recommended_action` 两者；
当它们不同时，`next_action_projection_warning` 标记漂移，
而不是静默选一个作为唯一真相。可执行分发应使用
`agent_lane_next_action` / todo 投影，而不是把共享 `## Next Action` 当作每 Agent
工作条目。

在多 Agent 目标中，`refresh-state` 需要显式 `--agent-id`；文本或 todo 标题推断
不是有效身份来源。当 refresh 以 `--agent-id` 作用域且无 `--progress-scope` 时，
run 记录 `progress_scope=agent_lane`。这是 lane 笔记，不是项目级 status 转移：
status/quota 继续为目标级 `status` 与 `recommended_action` 选择最新非 Agent lane
run，同时把 lane 笔记作为 attention 条目与项目资产上的
`agent_lane_recommendation` 暴露。多 Agent 目标中的目标级 refresh 必须使用
注册 peer 且带 `--progress-scope goal`。Agent lane 作用域用于不应替代持久目标
路线的 peer 本地推荐。

如果 peer self-merged 切片实质推进公共产品或用例路径，该 peer 或另一个注册 peer
还应写匹配 `delivery_outcome=outcome_progress` 的项目级 refresh（或跳过额外的项目级
同步）。后来的 `surface_only` 项目级同步会成为最新非 Agent lane run，
所以 quota 可能正确要求 follow-through，即使 peer lane 笔记记录了真实进度。

对注册的 `connected`、`connected-read-only` 与 `pre-tick-runnable` adapter，
不是 blocker、gate 或 watch 分类的自定义紧凑进度分类也保持 Codex-ready。
这让 controller 在 quota 记账前记录验证进度 run，而不必仅为使
`quota spend-slot` 合格而强制额外 state-only refresh。

### 自主积压候选

`attention_queue.autonomous_backlog_candidates` 是来自当前队列条目中
`waiting_on=codex` 且目标 quota 为 `eligible` 的未完成 `advancement_task`
Agent todos 的可选紧凑列表。Monitor 类 todos 被刻意排除在该积压外，
使依赖/就绪观察不能挤掉实现、规划或 blocker 写回候选。
`attention_queue.autonomous_monitor_candidates` 可以单独从
`waiting_on=codex` 或 `waiting_on=monitor_signal` 队列条目暴露紧凑
`continuous_monitor` todos，使 heartbeat 调度器仍看到当前 watch 面，
而不把它们当作主要推进工作。两个候选面都在 Agent 用 todo CLI 注册时保留
`action_kind`。

两个列表只是候选面：消费方在花一个 turn 前仍必须遵守所选目标的 quota、
`goal_boundary`、owner/gate、公共/私有边界与验证/writeback 规则。

`quota should-run` 在所选目标有 registry `spawn_policy` 或项目资产编排状态时包含
`goal_boundary.orchestration`。消费方用该边界决定下一个有界 turn 应保持默认单
worker 模式，还是可以在声明上限下启动子 worker。

Registry 条目可以用可选 public-safe 字段覆盖首屏关注：`waiting_on`、
`attention_status`、`recommended_action`、`operator_question` 与
`next_handoff_condition`。Status 在分类最新 run 前尊重它，因此带新鲜
`state_refreshed` 记录的目标在 active state 说人类或目标 controller 决策是真实
下一 gate 时仍可保持 `waiting_on=user_or_controller`。这用于状态真相纠正，
不是授予项目 Agent 执行。全局 registry 同步在不同后续来源为同一目标省略这些
字段时保留现有 attention 覆盖，因此 controller 编写的 gate 不会在普通项目同步期间
意外丢失。当同一来源 registry 再次同步且省略这些字段，该来源被视为权威，
过期覆盖被清除。同步 registry 条目也可以设置 `clear_attention_override=true`
显式清除覆盖。

Todo 提取独立于 attention 覆盖。目标可以因为 registry 说
`waiting_on=user_or_controller` 而留在 operator lane，同时 active state 暴露更具体
用户清单。这是复杂项目评审的优选形状：让 `recommended_action` 短到足以路由队列，
并把有序用户工作放在 dashboard 可以摘要的复选框区块。该路由文本属于用户的本地控制面：
它可以包含私有项目引用，但不得包含 AK/SK 值、令牌、认证头、密码或内联凭据。

对注册的计划高复杂度目标，兼容 `*_read_only_map_v0` adapter 且无 run 时，
status 保持队列条目 `waiting_on=user_or_controller`，为 Goal Harness operator 视图
发出 `operator_question`，并把 dry-run 预览放入 `agent_command`。预览应报告
`opt_in_required=true` 且不追加任何内容；dashboard 消费方不得把该命令当作
controller opt-in 或持久映射 run。人类可读 Markdown status 视图还可以在
`agent_command` 前渲染 `operator_gate_dry_run` helper；该 helper 是用户拥有的
gate 记录预览，不是 JSON 契约字段或项目 Agent 命令。
执行者面向 guard 比 status 显示更严格：`quota should-run` 必须保持这些计划条目为
`should_run=false`、`state=operator_gate`，且在批准的 operator-gate run 使目标合格前
不得包含 `agent_command`。这防止预览命令变成自动项目 Agent handoff。
当 quota payload 包含 `agent_todo_summary` 时，目标项目 Agent 可以用它作为自己
下一动作的安全后续清单，而不是重读聊天历史。当 quota payload 包含
`safe_bypass_allowed=true`，该权限只覆盖从 active state 优先级栈的独立只读
steering 或分析；它仍不得执行被 gate 的预览命令、adapter 工作、write-control 或
生产动作。当 payload 还包含 `gate_prompt`、`operator_question`、
`user_todo_summary` 或 `agent_todo_summary`，执行者应在可见线程用 `NOTIFY`
问具体 gate，除非同一未决 gate 最近已被问过；guard 不得把用户决策塌缩成静默跳过。
当目标有 `coordination.registered_agents`，身份感知 heartbeat 提示应调用
`quota should-run --agent-id <registered-agent>`。如果旧已安装提示省略该标志，
quota payload 应包含 `decision=automation_prompt_upgrade`、
`effective_action=automation_prompt_upgrade_required`、
`automation_prompt_upgrade.required=true`、`blocks_should_run=true` 与示例
`heartbeat-prompt --agent-id ... --agent-scope ...` 命令。执行者应把它当作提示升级
动作，而不是 delivery 权限、quiet no-op 或新 operator gate。`should_run`、
`normal_delivery_allowed` 与 `interaction_contract.agent_channel.delivery_allowed`
必须保持 `false`，直到自动化以注册 `--agent-id` 重跑 `quota should-run`。
当 v0.1 层级字段仍存在，同一对象还携带稳定 `migration_id`、
`host_update_idempotency_key` 与 `completion_command`。Host 可以用同一 id 重试
重新生成与自动化更新；registry 切换只在 host 更新成功且完成命令确认确切 id 后发生。
完成移除层级字段，记录 `coordination.completed_migrations.peer_agent_runtime_v1`，
并用已完成 id 重复时是幂等 no-op。一旦该标记存在，`quota should-run` 绝不投影该
registry 迁移。这是直到确认的稳定、可重试迁移，不是循环通知，
也不是用不同键多次更新自动化的权限。
所选身份是 turn envelope 的一部分。解释或记账同一 turn 的后续生命周期命令，
包括作用域 `refresh-state` 与 `quota spend-slot`，在子命令支持时应保留相同
`--agent-id`。掉身份的 spend 预览可以对无作用域自动化正确显示
`automation_prompt_upgrade_required`，但那是作用域 turn 的记账/投影不匹配，
不是早期 peer guard 无效的证据。
可问责 `refresh-state` 通常把当前 checkout 记录为 `delivery_workspace`。
当实现与验证在独立 worktree 发生，但 registry/状态投影必须从另一 checkout 运行时，
传 `--delivery-workspace-path <delivery-worktree>`。LoopX 对照 peer 隔离策略验证
引用的 checkout，并只持久其无凭据仓库身份与工作区类别，永不包括本地路径。
显式 canonical checkout 对 peer delivery 被拒绝，因此该因果覆盖不能把非隔离
工作变成可问责 delivery。
对注册 Agent 作用域 turn，`quota should-run --agent-id` 可以包含
`agent_lane_next_action.schema_version=agent_lane_next_action_v0`。这是当前 Agent
所选推进切片的只读派生指针，先选自可运行能力候选，然后从 Agent 作用域可执行
todo 摘要。即使 active state 全局 `Next Action` 仍由另一路线拥有，
它也可以指向当前 Agent 声明的 todo；因此该字段必须携带
`preserves_goal_next_action=true`，且不得当作项目级 status 覆盖。
`status --agent-id` 可以复用同一 quota 派生对象作为条目/项目资产观察数据；
消费方必须把它渲染为 Agent lane 指针，而不是 `recommended_action` 替代品。
人类 Markdown 应把该指针标为当前 Agent 的 todo，并把并排显示的全局 Agent todo 行
标为目标级，使 `--agent-id` 不被误认为替代目标级队列的过滤器。
当多个已准入推进 todo 保持可运行，同一 guard 还包含
`action_portfolio.schema_version=quota_action_portfolio_v2`。`primary`
是有序推荐，而 `suggested_actions` 是单一 canonical 有界便利视图：它携带推荐加
至多两个有序、Agent 作用域、能力就绪替代，并标记它们为 `recommended` 或
`alternative`。Portfolio 不在第二 fallback 视图下复制那些候选。
`selection_policy.candidate_scope=current_authoritative_eligible_todos`
把合法选择边界与显示建议分开；`suggestions_exhaustive=false`
让该区别机器可读。`selection_policy.decision_owner=agent` 与
`recommendation_role=default_not_binding` 使该边界的优先级排序建议性，
而不是静默绑定第一个 Todo。

版本 2 为每个 `suggested_actions[]` 条目添加可选 `continuation_hint` 字段，
使 Agent 无需把紧凑 packet 接回完整 Todo 摘要即可看到候选的下一个执行边界。
所有 v1 选择、排序、身份与权限语义保持不变。默认生产者现在只发出 v2；
`quota should-run`、紧凑 CLI 输出、TurnEnvelope 与无模型 `loopx turn` controller
都携带或消费该版本。紧凑 CLI 投影单独报告
`suggested_action_details.schema_version=quota_cli_action_portfolio_compaction_v1`
并内联 `todo_id`、`selection_role`、`priority`、`action_kind`、`text` 与
`continuation_hint`。精确匹配 schema 版本的 host 必须在消费新默认前升级其 portfolio
解码器。没有 v1 双发或降级协商；未知版本必须 fail closed，
而不是静默把推荐当作 delivery 权威。已忽略未知附加条目字段的消费方仍需要接受
显式 v2 版本。

第一次 quota 响应设置 `selection_required=true`，并暴露一个 typed
`selection_command.command_args_template`，带 `{todo_id}` 占位符加共享绑定
`route_prefix` 与权威开放 Agent 队列的紧凑 `candidate_discovery_args`。
其 heartbeat 收据没有结算身份，所以直接 delivery 与 spend fail closed。
模板刻意独立于有界建议：Agent 可以发现并请求任何当前投影的、Agent 作用域、
能力就绪 Todo。该请求是待决选择，不是已提交的收据身份。Quota 首先重跑当前 lane
仲裁与资格；新到期的高优先级 monitor、阻塞用户 gate 或其他抢占会推迟请求，
并让收据保持无身份。合格请求不必出现在有界建议中。只有升级后的响应恢复 delivery
及其结算计划。如果只有一个已准入动作，不添加 portfolio 选择阶段。

当所选工作有意义的 typed 谱系、等待、兄弟或目标接受上下文时，同一默认 guard
还可以包含 `planning_horizon.schema_version=quota_planning_horizon_v0`。
它是有界只读投影：至多 5 个 Todo 条目、8 个 typed 关系、2 个接受缺口与
3 个 attention id。`source_context_todo_count` 覆盖开放加延迟来源 Todos；
省略与文本截断计数器让不完整切片显式。`successor` 保持 `lineage_only`，
而 `resumes_when` 与 `unblocks` 保留现有 typed 生命周期语义。Horizon 不让
另一个 Todo 可执行，也不改变所选 Todo。消费方必须用现有显式选择重入选另一个
可运行动作，并在把不完整 horizon 当作穷举前遵循 `detail_refs`。

`action_portfolio`、`planning_horizon` 与显式 Agent Todo 细节透镜都派生自一个
`todo_planning_inventory_v0`。`planning_state` 与 `claim_state` 正交：
可运行未声明工作携带 `claim_required_before_work=true`，而其他 Agent 声明的工作
不被静默变为可执行。`quota should-run --include-detail agent-todos`
暴露更大的有界 `todo_planning_inventory_detail_v0` 投影；
`item_detail_ref=$.agent_todo_summary` 避免复制完整 Todo payload。
其完整性计数器对省略保持权威。需要完整开放来源的消费方遵循
`detail_refs.full_todo_list`，而不是假设任一有界投影穷举。

正确 typed 的未来工作被提前处理。有有效未来 `next_due_at` 的更高优先级
`continuous_monitor` 不可执行；quota 选择下一个就绪推进 todo，
并把未来 monitor 记录在 `action_portfolio.unavailable_higher_priority` 下，
`availability_reason=scheduled_for_future`。把这类工作标为 `advancement_task` 的
遗留状态不能从"Monday"或"after the window opens"等短语重新分类；显式
`task_class` 保持权威。Portfolio 仍为该兼容情形暴露有界替代，
使 Agent 无需重放整个冷诊断 packet 即可绑定另一个就绪动作。
同一作用域 guard 可以包含 `goal_route_hint.schema_version=goal_route_hint_v0`。
这是对当前 `agent_lane_next_action`、`agent_scope_frontier` 与紧凑每 Agent todo
lane 的目标级读路径综合。它携带 `preserves_goal_next_action=true` 与
`goal_next_action_mutation=none`，使 host 能解释 lane 决策，
而不改动共享 `## Next Action`，也不把其他 Agent 的队列塌缩进当前 Agent 路线。
在候选来源内，选择先按当前 Agent 声明排序，然后 `capability_repair_mode=true`，
然后优先级/索引。因此修复模式条目在更旧普通可运行 P0 todo 更早出现在 active state
时，仍保持为建议的 Agent lane 切片；否则一个旨在构建缺失能力的 todo 可以被依赖
该能力可靠的工作饿死。
对任何注册 peer，所选任务写仓库状态时 `quota should-run` 还强制工作区边界。
如果 guard 从非 git 目录、无关 git worktree 或不满任务/仓库隔离策略的 checkout
运行，payload 应包含 `workspace_guard.schema_version=agent_workspace_guard_v1`、
`workspace_guard.action=move_to_independent_worktree`、
`workspace_repair_allowed=true`、`normal_delivery_allowed=false` 与
`effective_action=agent_workspace_repair`。交互契约应使用 `mode=agent_workspace_repair`，
要求 peer 创建或切换到独立 worktree/分支，并在仓库编辑前用相同 `--agent-id`
重跑 `quota should-run`。该预检不花 quota；`quota spend-slot` 应在 guard 从独立
worktree 重跑前 fail closed。
Workspace 与边界 guard 必须绑定到 due-monitor、能力 fallback 与作用域 gate 路由后的
最终 work-lane `selected_todo`。它们不得从不相关的第一个可执行积压条目继承仓库或
写作用域语义；特别是所选只读持续 monitor 保持 monitor 工作，即使独立仓库修复也可
运行。
如果所选 todo 声明 `task_repository`，guard 还应投影该无凭据身份为
`workspace_guard.repository_source=selected_todo.task_repository`；否则
`repository_source=goal.repo`。匹配的仓库身份是必要不充分条件：当前 checkout
仍必须是链接 worktree，而不是该仓库的 canonical checkout。`task_repository`
不是写作用域或权限授予。
Dashboard 与 Review Packet 消费方应把 `workspace_guard` 投影为 Agent 通道工作区
修复，而不是 operator 或用户 gate。首屏可以渲染当前工作区类别、所需工作区类别、
修复动作与普通 delivery 是否允许。它不应要求用户批准移动、把所选 todo 标记为用户
阻塞，或隐藏开放同作用域工作。如果 peer 也在看另一个 peer 声明的 todo，
packet 应分别解释两个边界：工作区 guard 要求移到独立 worktree，
而声明边界要求选择作用域内当前 Agent 或未声明 todo、转移声明或创建显式 successor。
当 payload 包含 `notify_user_on_open_todo=true`，开放的 `user_todo_summary`
是当前 blocker-push 面，即使没有 operator gate。这用于 `focus_wait`、`waiting`
与 `external_evidence` lane，简短 user/owner 回答可以解锁进度或停止重复无意义轮询。
执行者应列出至多三个开放 todos，包含 `open_todo_notify_reason`，
跳过实现工作，并为该 blocker-push turn 跳过 quota spend。当 payload 还包含
`open_todo_notification_policy=repeat_until_resolved`，执行者应重复通知直到 todo
完成、延迟或被替换。`notification_suppressed=true` 的 `user_gate_notification_cooldown_v0`
packet 是窄例外：gate 与开放计数保持可见，而 `interaction_contract.user_channel`
变为 `action_required=false`、`notify=DONT_NOTIFY`，直到有界提醒窗口或实质
gate/host 变化。其他 blocker-push 情形在相同 blocker 最近被表露时仍可去重。

抑制决策还从最终用户通道移除 `actions` 与 `non_blocking`，
因此遗留 `user_action` 不能把同一契约重新提升为 `NOTIFY`。Provider sink
必须按 gate 身份加实质状态世代去重 delivery，只在显式到期的提醒窗口加额外提醒
世代；展示文本不是 delivery 身份。
合格 monitor-only 无转移轮询把开放用户 todos 保持在 `user_todo_summary`，
但不得强制重复通知或设置 `requires_user_action=true`；它们应表露为安静
`monitor_quiet_skip`，而不是可执行 run。
当 payload 包含 `external_evidence_observation`，目标等待仍需要只读观察契约的外部
monitor。这不是提示特定建议：`quota should-run` 还应设置
`effective_action=external_evidence_observe` 与
`execution_obligation.kind=external_evidence_observation_required`。执行者必须
检查具体可观察 handle 或紧凑 writeback 面，如线程 id、自动化 id、作业 id、
锁/结果标记或结果路径。如果无 handle，正确动作是紧凑 blocker 或启动就绪
writeback，不是 quiet no-op 也不是 benchmark 执行。
当 payload 包含 `heartbeat_recommendation`，执行者应在发明本地自动化行为前遵循
该通用生命周期提示：`run_first_read_only_map` 在花一次前运行并保存一次真实只读
映射，而 `mapped_noop_if_unchanged` 在无新指令、证据、todo、过期来源或安全 handoff
时返回 quiet no-op，不再 dry-run 或 quota spend。
当 payload 包含 `stale_latest_run_warning`，当前 active-state 投影已超前于最新
run-history 快照。执行者应在依赖 latest-run status、review packet 或 handoff 字段前
用新鲜状态刷新修复控制面投影，但该警告单独不授权生产动作，也不覆盖 `should_run`。
当 payload 包含 `backlog_hygiene_warning`，active state 在
`Next Action` 或 `Operating Lessons` 中有多个 public-safe 持久后续条目，
而活跃 `Agent Todo` 清单无开放条目。执行者应在 heartbeat 调度依赖那些叙事区块前
把持久后续工作镜像进具体 Agent Todo 复选框。该警告只是清单卫生信号：
它不改变 quota 资格、不授予写或生产权限，也不在
`execution_obligation.must_attempt_work=true` 时使 quiet no-op 合法。
当 payload 包含 `completed_todo_archive_warning`，活跃 `Agent Todo` 清单积累了
太多已完成条目，使 dashboard/status 面无法保持当前开放工作可见。执行者应把更旧
已完成条目移入专用 `Completed Work Archive` 区块，并只在活跃 `Agent Todo` 下保持
当前开放工作加少量近期完成尾部。警告的 `archive_command_template` 把投影的
`default_archive_keep_count` 包含为 `--max-active-done`，使可复制命令与警告的
近期完成尾契约保持对齐。归档区块被活跃 todo 解析刻意忽略。
该警告只是清单卫生信号：它不改变 quota 资格、不授予写或生产权限，
也不替代开放用户/Agent todo blocker。它也不把开放 todo 标记完成；
执行者应用 `loopx todo complete`、`todo update` 或 `todo supersede` 做按 `todo_id`
的结构化生命周期转移。
当 payload 包含 `autonomous_replan_obligation`，active state 的当前 `Next Action`
或 `Operating Lessons`，或近期公共 run history，携带 public-safe 证据表明 controller
可能卡在周期评审阈值、无进展连续段、重复动作循环、阶段转移、积压不匹配、
证据矛盾或两次重复公共 monitor/无进展 run 记录。历史进度条目与已完成 todos
被刻意排除在 active-state 触发源外。执行者应把该对象当作机器可读规划契约，
而不是提示建议：检查 `triggers`，把紧凑 `todo_actions` 应用为 split/add/retire
指导，写所选 todo/vision/blocker delta，并停在 `stop_condition`。验证保持正常
delivery 证据或 PR 评审路径的一部分，不是投影给运行时 Agent 的命令。默认停滞阈值
是 2 个连续停滞 turn 或公共 run 记录。`quota_monitor_poll` 记录对最新 dashboard
状态是 status 中性，但它对该特定 replan 检测器仍是公共停滞 run 证据。对合格目标，
`heartbeat_recommendation.recommended_mode` 可以变为
`autonomous_replan_required`，`execution_obligation.kind` 可以变为
`autonomous_replan_required` 且 `must_attempt_work=true`，
即使开放用户 todos 保持可见，只要所选切片留在私有、破坏性、生产或仅 owner 权威外
并遵守 `stop_condition`。开放 typed `user_action` 即使无当前可运行 Agent todo仍
保持非阻塞通知；它不得强制 `waiting_on=controller`。当两次有界停滞留下空 Agent
边界，义务要求一个 typed 语义结局。当有界边界已拥有具体 typed 目标时，
交互契约投影带 `--replan-obligation-id <exact-id>`、`--action-kind` 与稳定
`--target-key` 或 Explore 节点引用的声明 `todo add`。该一次变更原子记录可运行
successor 及其因果义务；它返回 `host_action=end_current_heartbeat`，
successor 在下一次 heartbeat 运行。通用规划指令从不被编译成 Todo。
当无已知可执行目标时，packet 反而要求 typed 语义或覆盖支撑的终态 writeback。
不需要第二个修复 ACK 写。用户提醒在该 replan 路径全程保持可见。
这是让 monitor-only 工作不消耗主要可执行积压，而不是绕过真实 gate。

`quota should-run` 与 `status --agent-id` 还可以暴露
`goal_frontier_projection.schema_version=goal_frontier_projection_v0`。
该投影归 `loopx.control_plane.goals.goal_frontier` 所有：它是紧凑每目标进度/边界
视图，不是另一个 quota 子状态。当它包含 `autonomous_replan_decision`，
该决策在 lane 本地 `monitor_quiet_skip`、`agent_scope_wait` 或
`agent_scope_exhausted` 投影前做出，使那些本地无候选状态不能掩盖必需的
有界 replan。
payload 包含 `interaction_contract.schema_version = loopx_interaction_contract_v0`，
它是所选目标的主要用户/Agent/CLI 协议。它把当前 turn 分组为稳定 `mode`，
如 `bounded_delivery`、`user_gate`、`user_todo_blocker_push`、
`external_evidence_observation`、`monitor_quiet_skip`、`autonomous_replan`、
`outcome_floor_recovery`、`mapped_noop_if_unchanged` 或 `quota_throttled`。
其 `user_channel` 说明是否打断用户及原因；`agent_channel` 说明 Codex 是否必须
尝试工作、delivery 是否允许、quiet no-op 是否允许，以及主动作；`cli_channel`
说明哪些 CLI 转移与 spend 策略适用。执行者应先读 `interaction_contract`，
把 `interaction_contract.agent_channel.primary_action` 作为当前 turn 唯一可执行
动作入口。可选 `agent_channel.resolution_trace.summary` 是诊断：
它紧凑记录 `primary_action` 匹配的源信号及是否检测到漂移。现有
`state_action_projection_warning` / `next_action_projection_warning` 字段携带任何
writeback 评审指导。Trace 不是独立 next-action 权威，也不暗示自动 active-state
writeback。`execution_obligation`、`heartbeat_recommendation`、
`work_lane_contract`、`external_evidence_observation`、`goal_boundary` 与
`protocol_action_packet` 保持该契约下的兼容与下钻字段，不是竞争真相源。

同一 payload 包含 `scheduler_hint.schema_version=scheduler_hint_v0`。
这是 host 运行时的调度契约，不是 delivery 权限：Codex App 可以为长等待退避其
自动化 cadence，而 Codex CLI TUI 与 Claude Code loop 可以在重复未变化轮询后运行
一次最终 quota/replan 检查，然后只在 guard 仍未变化时退出/停止。Cadence 变更、
最终检查与 loop 自停从不花 quota。Host scheduler 把
`recommended_interval_minutes` 应用为下一个目标间隔，并把后续未变间隔乘以
`unchanged_poll_backoff_multiplier` 直到 `max_interval_minutes`；
`example_progression_minutes` 暴露紧凑人类可读序列。Hint 还包含紧凑
`reset_policy`：host 在轮询间比较 `reset_token`，并在该 token 变化、
或用户回复、新/重分配 todo、已解决 gate 或实质转移使目标再次可执行时清除
未变化/退避连续段。Token 由 scheduler 动作加身份/profile 输入派生，
而热路径只携带动作字段加短 `identity_signature`；profile 签名、reset 条件摘要与
完整 stateful-backoff 策略在调用方请求
`loopx quota should-run --include-detail scheduler` 时从
`scheduler_hint.cold_path_detail` 可用。Reset 在未变化退避恢复前把 Codex
App/本地 cadence 回到当前 profile 初始间隔，且不花 quota。
Codex App heartbeat 只在 `codex_app.stateful_backoff.apply_needed=true` 且
`codex_app.recommended_rrule` 存在时使用 `automation_update`。如果该更新成功，
Agent 必须运行 `codex_app.ack_hint.cli_args`；当前 payload 用
`quota scheduler-ack-current`，让 LoopX 重读最新 hint，然后在运行时根下持久化
`reset_token`、`identity_signature`、`progression_index` 与
`last_applied_rrule`。同一身份重复时，LoopX 在已应用间隔流逝后推进 progression，
直到最大间隔。即时 post-ACK 读回保持在被确认 RRULE 上，使重复调和收敛而非振荡。
当 reset token 变化时，下一个投影 RRULE 回到 `reset_policy.codex_app_initial_rrule`。
如果当前期望 RRULE 已应用，`recommended_rrule` 被省略且应跳过 host 更新。
当该匹配读回仍需要 reset-token/identity 绑定时，`ack_needed=true`；
直接运行绑定 ack。否则无需 scheduler 动作。
对 CLI payload，`ack_hint.cli_args` 以源 `should-run` 调用使用的 registry 与有效
runtime-root 绑定开始。消费方必须保留该前缀，使 ACK 不能在项目与共享 registry
间拆分 scheduler 状态。`scheduler-ack` 只记录已应用的 host cadence；
下一个 RRULE（如果有）由未来 `quota should-run` 投影，而不是 ack 响应。
payload 还包含 `execution_obligation`，这是旧 worker 决定 quiet no-op 是否允许的
兼容入口。`heartbeat_recommendation.notify` 只是用户面向通知策略。它不得被解释为
执行 gate。`heartbeat_recommendation.agent_must_attempt` 把
`execution_obligation.must_attempt_work` 镜像为单字段快捷方式，
使薄 heartbeat 提示可以基于一个布尔而非解析 notify 语义来挂起工作义务。如果
`autonomous_replan_required`，`heartbeat_recommendation.notify` 是 `NOTIFY`：
replan turn 是机器执行契约，不得投影为 `DONT_NOTIFY`（Agent 可能误读为 quiet
no-op 权限）。如果 `execution_obligation.kind=external_evidence_observation_required`，
普通 delivery 仍阻塞，但 worker 在可以停止前必须执行一次只读观察或写紧凑
缺失 handle blocker。如果 `execution_obligation.must_attempt_work=true`，
worker 应在 `work_lane_contract` 存在时于其下选择一个有界片段，否则在
`effective_action` / `goal_boundary` 下选择，验证它、写持久状态/事件，
并在 delivery 后花一次，即使 `notify=DONT_NOTIFY`。Quiet no-op 需要
`execution_obligation.must_attempt_work=false` 且无
`notify_user_on_open_todo=true` 等 blocker-push 通知；两者都存在时，
通知用户且不 spend。验证 `mapped_noop_if_unchanged` 保持 quiet no-op 情形。
guard 还发出 `protocol_action_packet.schema_version = protocol_action_packet_v0`，
一个给执行者与未来 LLM-router 实验的紧凑仅规则 packet。它把同一 quota guard
蒸馏为单个主 actor、用户/Agent 动作要求、quiet-noop 允许、执行 lane，
在单一 `summary` 字符串内加短 `llm=no_api` 标记，使热路径留在接口预算内。
详细 spend 策略留在 `heartbeat_recommendation.spend_policy`。该 packet 不是新权威
源，也不授权模型/API 使用；它是可选 Codex/LLM 摘要器必须在 payload 缩小与
用户/Agent 动作清晰度上胜出的确定性基线。当开放 todo 使用常见
`[P*] short title: details` 形状时，packet 用短标题作为动作标签，
使长进度笔记不再进入热路径。
如果开放用户 todos 与可执行 Agent 工作共存，packet 保持主 actor 为 `agent`，
但加 `user_action_pending=true` 加紧凑 `user_action` 标签。这保留 owner 可见
blocker，而不把那个 owner todo 误标为 `agent_action`。
当 registry 启用目标有 `control_plane.self_repair.enabled=true`，
`quota should-run` 可以返回 `decision=self_repair`、`self_repair_allowed=true`、
`stall_self_repair` 与 `effective_action`，如 `control_plane_health_repair` 或
`control_plane_projection_repair`。这是短 heartbeat 的机器可读停滞修复契约：
修复控制面投影或写回具体 blocker、验证、记录持久事件，然后花一次。
没有该 registry 策略的目标默认不得获得该 lane。
当 payload 包含 `decision_freshness_warning`，目标仍可合格，但该目标采样的
reward/gate 状态过期或其后有更新事件。执行者在决策点重读当前 registry、
ACTIVE_GOAL_STATE、quota、策略与 run status 前不得把旧决策当作权威复用。
该警告是决策复用护栏，不是仓库回卷，也不是 `should_run` 的替代。
如果 payload 的 `handoff_readiness.post_handoff_outcome_gap_streak` 达到
`project_asset.execution_profile.outcome_floor.surface_streak_threshold`，
`quota should-run` 在 floor 声明具体 `must_advance` 目标时还应强制 handoff 契约，
返回 `should_run=true`、`state=focus_wait`、
`blocked_action_scope=delivery_outcome_floor`、`safe_bypass_allowed=true`、
`safe_bypass_kind=outcome_floor_recovery`、`recovery_delivery_allowed=true`、
`effective_action=outcome_floor_recovery`、`decision=safe_bypass_recovery` 与
`heartbeat_recommendation.recommended_mode=outcome_floor_recovery`。
该形状中 `should_run` 表示存在 Codex 可执行 turn，而 `normal_delivery_allowed=false`
说明普通 delivery 被阻塞。执行者应把 `effective_action=outcome_floor_recovery`
当作恢复权限，只在验证 ranker/cross-domain 证据或具体 blocker writeback 后 spend，
并避免继续 surface-only loop 或被动等待。
Status 导出应对 `attention_queue.items[]` 与 `project_asset.quota` 应用同一 quota
guard，同时保留 `handoff_readiness` run 证据：`codex_ready` 可以变 false，
但 `post_handoff_latest_run`、`post_handoff_recent_runs` 与
`post_handoff_outcome_gap_streak` 应保持 dashboard 与 handoff packet 可见。

Review Packet 真相源规则：

- dashboard/operator 视图拥有人类决策；
- 复制的 Review Packet 是从该决策面到本地 operator 预览与目标项目 Agent 指令的
  桥；
- `loopx review-packet --goal-id <goal-id>` 可以从 status 契约为 CLI 面向 Agent
  生成同一 packet，但它仍是只读打包命令；
- 当 status 包含需要 rebase 的同目标 `decision_freshness_summary` 条目时，
  完整 Review Packet 应在 operator 批准或转发工作前渲染紧凑人类可见新鲜度警告；
  该警告留在最小化 handoff-only 文本外，使项目 Agent 仍收到小当前指令；
- `loopx review-packet --goal-id <goal-id> --handoff-only` 是给已选或已批准
  目标 Agent 转发的复制最小形式：它在 Markdown 输出只打印
  `project_agent_handoff` 文本，而 JSON 输出返回最小化 handoff payload 而非完整
  operator packet。为保持热路径紧凑，handoff-only JSON 不暴露单独
  `handoff_followthrough_summary` 散文字段；该散文在完整 Review Packet 与嵌入
  handoff 文本中仍可用；
- 项目 Agent handoff 命令在进入 `project_agent_command`、
  `project_agent_handoff` 或 `handoff_text` 前脱敏本地绝对 registry/runtime 路径；
- 项目 Agent handoff 文本是接口预算的热路径产物：它应保持在 16 行与 1800 字符内，
  至多包含一个命令块，并只携带目标 goal guard、最小上下文规则、来源标签、
  可选的紧凑 post-handoff delivery scale、可选 delivery 契约、转发/执行边界、
  命令与停止条件；
- `handoff_delivery_contract` 是从当前 `handoff_readiness` 加
  `project_asset.execution_profile` 派生的可选结构化指导，不是目标特定 hack。
  当重复小规模 follow-through 达到 profile 的
  `degradation_policy.small_scale_streak_threshold`，packet 可以设置
  `mode=expand_after_repeated_small_delivery`，要求目标 Agent 以 profile
  `minimum_scale` 运行一个连贯批量，带声明的 `must_include` 面，
  或不花 quota 报告 blocker。当 implementation 形状 run 仍只是
  forecast/runbook/queue/field 传播且
  `post_handoff_outcome_gap_streak` 达到 profile 的
  `outcome_floor.surface_streak_threshold`，packet 可以改设置
  `mode=expand_after_surface_progress_loop` 并要求下次 delivery 推进声明的
  outcome floor，或不 spend 报告 blocker；
- handoff-only 输出不得携带完整 Review Packet、人类决策区块、本地 operator-gate
  预览、operator 决策 payload 字段、原始 `run_history` 或 `latest_runs` 冷路径证据；
- 本地 `operator_gate_dry_run` 预览属于用户或 controller，不是目标项目 Agent；
- 项目 Agent 命令是 controller gate 的批准后 dry-run 路径，或已连接 delivery
  Codex 目标的 quota guard。已连接 delivery handoff 可以在 `should_run=true` 后
  授权有界写作用域 delivery；它们仍必须为未批准作用域、生产动作、破坏性 git、
  私有材料或 surface-only loop 停下。

对 controller opt-in packet，operator 问题必须出现在任何本地 gate 预览前，
而本地 gate 预览必须出现在任何项目 Agent 命令前。Dashboard、脚本或 Agent
不得从复制的 packet、评审 URL、所选 `goal_id` 或 `agent_command` 的存在推断
批准、奖励、write-control 或真实 map run。

Review Packet 的项目 Agent 区块应短且可操作：在显示任何命令前点名当前上下文
来源、转发条件、执行边界与停止条件。上下文来源规则保持 Agent handoff 不膨胀：
packet 只携带最小当前指令；目标 Agent 需要更多上下文时，它读取当前 active state、
status、history 与命令输出，而不是从旧聊天或旧 packet 重建真相。对 controller
opt-in，那意味着区块只在显式人类/controller 同意后转发，Agent 只运行只读或
dry-run 项目路径，并在需要真实批准、write-control、run-history 追加、生产动作或
命令失败时停止。这让目标 Agent 容易遵循 packet，同时保留 dashboard 作为人类决策面
与档案证据轨迹作为冷路径。

对 focus-wait packet，Review Packet 应把第一个开放 owner/user todo 表露为解锁
条件，而不是普通 delivery 工作。人类区块应说明项目为何安静、谁可以解锁它、
delivery 恢复前需要哪些证据。项目 Agent 区块不得呈现安全本地 delivery 路径；
它应只指向 status 或 history 检查，并告诉目标 Agent 保持 `focus_wait`，
直到新 owner 证据、干净基线或外部 eval 改变状态。
Dashboard 动作 packet 与首屏卡片应遵循同一规则：把条目标为 `Focus wait` /
owner blocker，把第一个开放 owner/user todo 显示为解锁条件，
并让复制便利只是 status/history，而不是已批准 handoff 或只读映射 delivery 路径。

`status=read_only_project_map` 在最新紧凑 run 来自 `loopx read-only-map` 时发出。
Dashboard 消费方应把它显示为带映射特定徽章或下钻的 Codex-ready 工作：项目已连接
且有只读映射 run，但下一个有用动作仍需要 controller 或 Agent 使用该映射。
紧凑 run 记录可以包含 public-safe `project_map` 对象：

```json
{
  "adapter_kind": "read_only_project_map_v0",
  "adapter_status": "connected-read-only",
  "authority_source_count": 1,
  "authority_registry_declared": true,
  "authority_registry_path_exists": true,
  "authority_registry_default_entry_count": 2,
  "authority_registry_default_entries_present": 2,
  "topic_authority_count": 8,
  "authority_registry_conflict_risk": "low",
  "guard_count": 3,
  "sections_found": 4,
  "sections_checked": 7,
  "project_registry_exists": true,
  "goal_state_dir_exists": true,
  "active_state_file_exists": true,
  "files_present": 4,
  "files_checked": 9,
  "residual_risk_count": 1
}
```

完整 run payload 还可以包含 `residual_risks`，紧凑 public-safe 列表，
如 `planned_adapter_requires_controller_opt_in` 或
`project_local_goal_state_not_detected`。如果声明了可选权威注册表，缺失 registry
文件、缺失默认条目、过期来源或中/高冲突风险以稳定 `authority_registry_*` 标签
报告。项目 Agent 应直接转达该列表，而不是发明自由形式风险摘要。

对同仓库多目标项目，`project_registry_exists`、`goal_state_dir_exists` 与
`active_state_file_exists` 是 goal 作用域健康信号。项目可以同仓库既有
`main-control` 也有 `side-bypass`，但每个所选 `goal_id` 应有自己的
`.codex/goals/<goal-id>/` 目录。如果该目录缺失，映射报告
`project_goal_state_dir_not_detected:<goal-id>` 与遗留
`project_local_goal_state_not_detected` 风险，即使同仓库另一目标健康。

CLI 清理路径是 `loopx archive-runtime --goal-id <goal-id>`。它默认 dry-run，
要求 `--execute` 才把运行时目录移到 `<runtime-root>/archived-goals/` 下。

## Run History

`run_history` 是给 dashboard 的紧凑、public-safe 下钻面。它镜像紧凑 run 索引，
但剥离本地产物路径。UI 应以 `json_exists` 与 `markdown_exists` 显示产物可用性，
而不是直接链接本地文件。

在 `status`、`quota should-run` 与 `history` 读路径上，相对 `common_runtime_root`
值、相对 `--runtime-root` 覆盖与相对 run-index 产物路径按拥有所选 registry 的
项目根解析，而不是调用者当前工作目录。这让那些读面从独立 worktree 调用时保持稳定。

Goal 形状：

```json
{
  "id": "complex-project-main-control",
  "domain": "complex-project-control",
  "status": "active-read-only",
  "lifecycle_phase": "controller_gated",
  "lifecycle_flags": [
    "controller_gated",
    "adapter_inspected"
  ],
  "registry_member": true,
  "legacy_runtime_goal": false,
  "adapter_kind": "complex_project_read_only_map_v0",
  "adapter_status": "connected-read-only",
  "authority_registry": {
    "declared": true,
    "path": "docs/meta/DOC_REGISTRY.yaml",
    "path_exists": true,
    "default_entry_count": 3,
    "default_entries_checked": 3,
    "default_entries_present": 3,
    "topic_authority_count": 8,
    "project_material_count": 6,
    "project_material_repository_count": 2,
    "project_material_owner_review_required_count": 1,
    "project_material_stale_count": 1,
    "project_material_current_authority_count": 1,
    "deprecated_source_count": 0,
    "conflict_risk": "low"
  },
  "quota": {
    "compute": 0.5,
    "window_hours": 24,
    "slot_minutes": 1,
    "allowed_slots": 720,
    "spent_slots": 0,
    "state": "operator_gate",
    "reason": "operator gate blocks gated delivery; safe non-gated steering may continue",
    "blocked_action_scope": "gated_delivery",
    "safe_bypass_allowed": true
  },
  "index_exists": true,
  "raw_index_records": 2,
  "unique_runs": 2,
  "subagent_activity": {
    "source": "run_history",
    "parent_goal_id": "complex-project-main-control",
    "child_count": 2,
    "visible_child_count": 2,
    "completed_count": 1,
    "active_count": 1,
    "quota_spend_slots": 2,
    "items": [
      {
        "run_id": "docs-map-001",
        "goal_id": "docs-map-subagent",
        "parent_run_id": "controller-run-001",
        "spawned_by_goal_id": "complex-project-main-control",
        "agent_role": "explorer",
        "state": "completed",
        "work_scope": [
          "docs/**"
        ],
        "touched_paths": [],
        "touched_path_count": 0,
        "handoff_summary": "Mapped task clusters without editing files.",
        "quota_spend_slots": 1
      }
    ],
    "proxy_note": "compact child-run projection only; parent controller remains the authority for locks, writes, and merge decisions"
  },
  "latest_runs": []
}
```

Goal 上的 `authority_registry` 来自 registry，即使最新 run 是 operator gate 或
reward overlay 而非新鲜项目映射也保持可见。Dashboard 消费方应在请求 operator
决策前把它翻译成一行人类面向文本，如"default entries 3/3, topic 8, materials 6,
owner review 1, risk low"。材料细节留在项目本地：公共 status 暴露材料角色、
仓库链接、owner 评审缺口、过期来源与当前权威的紧凑计数，而不是 URL、仓库根、
产品配置或原始评审笔记。Markdown status 渲染器应在 attention 队列条目上以
`authority_material` 行暴露同一紧凑上下文，使 Agent 面向 handoff 看到新鲜度与
owner 评审压力，而无需内部材料链接或来源文本。

Goal 上的 `quota` 来自 registry，未声明时默认 `compute=1.0`。在 v0.1 中，
status 从硬 gate 与 attention 归属只派生紧凑产品状态：`eligible`、`focus_wait`、
`throttled`、`waiting`、`operator_gate`、`paused` 或 `blocked_health`。
它不是权限信号，不替代人类奖励、operator gate、写批准或生产动作授权。

Run 形状：

```json
{
  "generated_at": "2026-05-31T21:15:00+00:00",
  "goal_id": "complex-project-main-control",
  "classification": "ready_for_controller_opt_in",
  "lifecycle_phase": "controller_gated",
  "lifecycle_flags": [
    "controller_gated",
    "adapter_inspected"
  ],
  "recommended_action": "ask the target controller to opt into a read-only map before any mutation",
  "health_check": "8/8",
  "run_id": "controller-run-001",
  "subagents": [
    {
      "run_id": "docs-map-001",
      "goal_id": "docs-map-subagent",
      "parent_run_id": "controller-run-001",
      "spawned_by_goal_id": "complex-project-main-control",
      "agent_role": "explorer",
      "state": "completed",
      "work_scope": [
        "docs/**"
      ],
      "touched_path_count": 0,
      "handoff_summary": "Mapped task clusters without editing files.",
      "quota_spend_slots": 1
    }
  ],
  "subagent_count": 1,
  "controller_readiness": {
    "classification": "ready_for_read_only_not_decision",
    "read_only_observer_ready": true,
    "decision_advisor_ready": false,
    "write_controller_ready": false,
    "missing_gates": [
      "human_reward_capture",
      "aligned_eval_decision_evidence"
    ],
    "review_judgment": "safe to connect read-only observation, but not decision advice",
    "next_handoff_condition": "record aligned eval evidence and one human reward event",
    "gates": [
      {
        "id": "durable_goal_context",
        "ok": true,
        "review": "goal state and run history are available"
      },
      {
        "id": "human_reward_capture",
        "ok": false,
        "review": "no operator reward has been recorded yet"
      }
    ]
  },
  "human_reward": {
    "recorded_at": "2026-06-01T00:05:00+00:00",
    "decision": "continue_route",
    "reward": "positive",
    "reason_summary": "operator accepted the route because the comparable metric improved and validation was aligned",
    "follow_up": "promote the route to a longer-window check"
  },
  "json_exists": true,
  "markdown_exists": true
}
```

`active_task_count`、`active_priorities` 与 `cache_check` 等可选紧凑字段可以在
adapter 记录时出现。实验 controller adapter 还可以包含紧凑 `controller_readiness`
与 `human_reward` 摘要。

`lifecycle_phase` 由 status 层派生，使 dashboard 把状态交互阶段与 adapter 特定
分类分开：

- `connected`：目标注册了已连接 adapter 但无 run。
- `mapped`：最新 run 是通用 `read_only_project_map`。
- `refreshed`：最新 run 是状态-only `state_refreshed` 更新。
- `adapter_inspected`：项目 adapter 产生了紧凑 run。
- `reward_judged`：人类奖励 overlay 附着到 run。
- `operator_approved`：operator gate 获批，已批准的 `agent_command` 可以交给目标
  项目 Agent。
- `operator_gated`：operator gate 被拒绝或延迟，目标保持 gate。
- `controller_gated`：存在 controller 就绪证据，但目标仍缺人类奖励或可比较证据
  等 gate。
- `controller_ready`：存在 decision-advisor 或 write-controller 就绪。
- `planned`、`registered` 与 `run_recorded`：尚未连接或无分类 run 目标的 fallback
  阶段。

`lifecycle_flags` 可以包含多个阶段。例如 run 可以同时是 `adapter_inspected` 与
`reward_judged`、`adapter_inspected` 与 `operator_approved`，或 `adapter_inspected`
与 `controller_gated`。UI 应先显示主阶段，并把 flags 用作次级徽章。
当 Codex 拥有的目标携带 `lifecycle_phase=focus_wait` 或 `continuation_boundary`
标志，quota 应表露 `state=focus_wait` 而非 `eligible`。这让计算配额与 delivery
focus 分开：目标可以保持健康可见，而自动 turn 等待新证据、owner 输入、外部 eval
或干净基线。
Quota 也可以在 post-handoff delivery 反复错过声明 outcome floor 时使用
`state=focus_wait`。那时 `blocked_action_scope` 应识别
`delivery_outcome_floor`，目标 Agent 应带着 outcome 规模证据返回，
或在不再花一个槽位的情况下报告 blocker。当 floor 声明 `must_advance`，
quota payload 应用 `normal_delivery_allowed=false`、`recovery_delivery_allowed=true`、
`should_run=true` 与 `effective_action=outcome_floor_recovery`
把普通 delivery 与恢复 delivery 分开，使 dashboard 与 heartbeat 消费方不把恢复
lane 误认为安静跳过。

对 `controller_readiness`，status 导出只保留 controller-stage 布尔、缺失 gate 名、
operator 面向评审文本、下一 handoff 条件与带 `id`、`ok` 与 `review` 的紧凑 gate
行。对 `human_reward`，status 导出只保留 `recorded_at`、`decision`、`reward`、
`reason_summary` 与 `follow_up`。对 `operator_gate`，status 导出只保留
`recorded_at`、`gate`、`decision`、`operator_question`、`reason_summary`、
`follow_up` 与 `agent_command`。Operator-gate run 还可以包含紧凑
`operator_gate_resume_contract`，带 `version=operator_gate_resume_contract_v0`、
`gate_id`、`created_state_ref`、`latest_state_ref`、`operator_decision`、
新鲜度/前置条件检查、rebase 结果、结果动作与 resume 后验证文本。
该契约是公共 checkpointed-decision 面。其 rebase 只作用域到批准/恢复决策点；
它不是仓库/worktree 回滚、恢复或时移机制。更丰富证据属于私有 run payload。

Operator gate 决策回答"项目 Agent 可以跨这个 gate 吗？"，并与奖励信号分开。
用于 read-only map opt-in 等批准：

```bash
loopx operator-gate \
  --goal-id complex-project-main-control \
  --decision approve \
  --reason-summary "同意先执行 read-only map opt-in"
```

Dry-run 形式不追加任何内容。真实追加写 `operator_gate_approved`、
`operator_gate_rejected` 或 `operator_gate_deferred` 紧凑 run。已批准 gate
作为带已批准 `agent_command` 的 Codex-ready 表露；拒绝/延迟 gate 留在
用户/controller lane，带记录理由。已批准命令不是旧 checkpoint 的时移重放：
在批准/恢复决策点，目标 turn 必须重读当前 registry、`ACTIVE_GOAL_STATE`、
quota、repo dirty/ref 快照、策略与 run status。该检查决定批准动作现在是否仍有效；
它不得把整个仓库状态带回旧 gate。Quota spend、eval/实验启动、生产写或外部消息
属于新鲜批准的恢复之后。

Operator 可以用 CLI 追加 `human_reward`：

```bash
loopx reward \
  --goal-id example-experiment-goal \
  --decision continue_route \
  --reward positive \
  --reason-summary "comparable validation improved and the route is worth extending"
```

命令向目标的 `index.jsonl` 追加紧凑 overlay 行。历史加载合并具有相同 run key 的
后续行，因此可以添加反馈而不重写原始 run JSON 或 Markdown payload。

当 operator 反馈是路线、优先级、benchmark 协议、安全或运维规则纠正时，
overlay 也可以包含紧凑教训：

```bash
loopx reward \
  --goal-id example-experiment-goal \
  --decision route_correction \
  --reward mixed \
  --reason-summary "run the driver repair before expanding cases" \
  --lesson-kind route \
  --lesson-summary "Do not expand cases before driver repair is validated" \
  --lesson-avoid "expand cases before driver repair" \
  --lesson-prefer "validate driver repair first"
```

`human_reward.lesson` 是警告/rebase 信号，不是 write-control。Status 导出紧凑
教训，而 `quota should-run` 在当前 `recommended_action` 与近期教训的 `avoid`
短语重叠时发出 `reward_lesson_projection_warning`。Agent 随后应在继续前更新
受影响的 todo 或 Next Action。

Dry-run 与追加响应都包含：

```json
{
  "active_state_summary": "dry-run：将记录目标 `example-experiment-goal` ...",
  "project_agent_visibility": {
    "source_of_truth": "run_bound_human_reward_overlay",
    "history_command": "loopx history --goal-id example-experiment-goal --limit 3",
    "active_state_role": "summary_only",
    "review_packet_role": "optional_handoff_only"
  }
}
```

Agent 应把 `history_command` 当作标准可见性路径。Active state 可以为上下文重复
摘要与下一动作，但它不是持久奖励存储。

当 `loopx status` 渲染 Markdown 时，带 `human_reward` 的最新 run 应在
`Run History` 下展开紧凑奖励字段，并重复同一项目 Agent 历史查找。
这让 dashboard 保持 operator 面，同时使 CLI status 对只需要注意到并检查已记录
奖励的项目 Agent 足够。

Markdown 响应还应在顶部附近显示短 `Write Effect` 区块，使 operator 看到所选 run、
overlay 是实际追加还是只预览、active-state writeback 是否会发生，以及唯一项目
Agent 历史查找。

当 operator 显式要求时，CLI 也可以预览或执行 active-state 摘要写：

```bash
loopx reward \
  --goal-id example-experiment-goal \
  --decision continue_route \
  --reward positive \
  --reason-summary "comparable validation improved and the route is worth extending" \
  --write-active-state-summary
```

该响应包含 `active_state_update`，例如：

```json
{
  "active_state_update": {
    "requested": true,
    "section": "Progress Ledger",
    "would_write": false,
    "written": true,
    "already_present": false
  }
}
```

Loopback dashboard 写路径是 opt-in。默认 `serve-status` 只暴露
`POST /reward/dry-run`；在 loopback host 上以 `--enable-reward-write-api` 启动时，
它还暴露 `POST /reward/append`。Append 请求必须复用 dry-run 响应返回的
`preview_id`，因此变化的 payload、变化的所选 run 或变化的原始 index 计数迫使
operator 再次预览。紧凑浏览器响应不暴露索引路径、状态文件路径或原始私有证据。

## 事件 Ledger 摘要

`event_ledger_summary` 是紧凑 run 索引上的可选 dashboard 友好投影。
它让持久执行契约可见，而无须 dashboard 或 heartbeat 提示读取完整 run history。

摘要把采样 run 记录分类为：

- `accounting`：`quota_slot_spent` 等 quota 与 spend 行；
- `decision`：operator gate、恢复契约、延迟、批准与 `human_reward` overlays；
- `evidence`：eval、metric、CI、deploy、artifact、blocker、失败/done 或只读
  证据轮询观察；
- `state`：状态刷新与其他紧凑状态投影行；
- `work`：其余有界 delivery 或实现进度行。

摘要报告 24h/7d 总数与每目标按事件类别的计数。它不得替代仅追加 run、奖励、
quota、验证、产物、blocker 或证据事件。每个每目标行还可以包含
`latest_event_class` 与 `latest_event_at`，它们是 dashboard 的紧凑路由提示，
不是最新 run 记录的替代。

## 晋升就绪摘要

`promotion_readiness_summary` 是运行时发布 ledger 上的可选发布控制投影，
只在运行时 ledger 没有有效就绪事件时保留遗留 Goal run-history 事件作为读兼容
fallback。它找到最新 `canary_promotion_readiness_smoke_group` 事件，
报告在把 live checkout 晋升为默认本地发布快照前该证据是否足够新鲜可信。
新证据是运行时作用域的，因为发布就绪被使用该本地安装的每个 Goal 共享；
它不需要也不改动项目 Goal。

摘要报告：

- `freshness_status`：`fresh`、`stale`、`missing` 或 `unknown`。
- `freshness_window_hours`：新鲜度窗口，当前为 24 小时。
- `is_fresh` 与 `requires_readiness_run`：给安装器、dashboard 与 heartbeat 作业的
  紧凑 guard。
- `age_seconds` / `age_hours`：事件时间戳可解析时的证据年龄。
- `json_exists` / `markdown_exists`：最新证据产物是否仍存在。
- `dashboard_readiness`：运行时级证据的 `passed` 或 `skipped`，
  刻意省略与成功检查永不无区别。

该投影不晋升任何东西，也不替代 LoopX 运行时根下的仅追加发布产物。
`scripts/install-local.sh` 消费同一就绪事实只打印非阻塞警告；operator 仍应运行
`loopx doctor` 或 canary-promotion readiness smoke 获取确切本地发布证据。

## 决策新鲜度摘要

`decision_freshness_summary` 是采样 run history 上的可选 checkpointed-decision
投影。它存在是因为聊天线程不是长时控制决策的真相源：持久源是仅追加 run history
与事件 ledger。Codex 线程可能记住旧批准或奖励，但在花配额、启动工作或改动外部状态
前，它必须对照最新 registry、active state、quota、策略与 run-status 事实重新基准
那个决策点。

摘要把紧凑 `human_reward`、`operator_gate`、operator-gate 恢复契约与
reward/gate 类分类当作 checkpointed decisions。对每个采样决策它报告：

- `freshness_state`：`fresh`、`rebase_required` 或 `stale_rebase_required`。
- `stale_by_age`：决策是否早于新鲜度窗口。
- `newer_event_count_7d` 与 `newer_event_classes_7d`：七天窗口内同目标的
  更新采样事件。
- `requires_decision_point_rebase`：worker 在复用旧决策前是否应刷新当前控制面状态。

这是决策点 re-base helper，不是仓库重置或时移机制。更新事件意味着 worker 应在
当前状态重新解释旧奖励或 gate；它们不把项目滚回旧聊天上下文。如果
`status --limit` 省略更旧 run，摘要可能漏掉过期决策，因此消费方应把它当作
操作警告面，并在需要时下钻项目历史做确切重放。
`quota should-run` 在采样决策具有 `requires_decision_point_rebase=true` 时，
为所选目标将该投影消费为 `decision_freshness_warning`。该警告刻意附加：
它不翻转 `should_run`，但告诉 worker 它计划复用的任何旧奖励或 gate 必须先重新
绑定到当前控制面状态。Dashboard 项目/细节与分享面应在批准或转发前把非空同目标条目
渲染为紧凑中文 operator 警告，明确说明 decision-point rebase 意为重读当前控制面
状态，而不是把仓库或项目滚回旧聊天上下文。

`quota should-run` 还把 `promotion_readiness_summary` 在采样 canary
promotion-readiness 证据缺失、过期或未知时消费为 `promotion_readiness_warning`。
该警告是发布就绪 guard 面，不是调度决策：它不翻转 `should_run`，
但让 heartbeat worker 报告在新鲜 canary promotion-readiness 证据写入共享运行时
发布 ledger 前不应晋升发布快照。这使发布就绪留在可查询控制面状态，
而不是依赖 dashboard 散文、`doctor` 输出或聊天线程。警告消息点名写回命令
`python3 examples/canary/canary-promotion-readiness-smoke.py`。带
`--no-write-evidence` 的 run 验证 canary 而不刷新该持久投影，无法清除警告。

## Usage 摘要

`usage_summary` 是同一紧凑 run history 派生的可选 dashboard 友好代理。
当 run 携带 typed `run_usage_v0` usage 行，摘要聚合目标的输入/输出 token 计数，
以及测得时的 cache tokens、估计成本与墙钟时长；未报告的 run 不贡献任何内容。
它仍是代理，不是计费遥测：它仍排除原始线程日志、本地项目路径、私有产物内容，
或任何需要读取 Codex 会话转录的内容。只捕获聚合数字 usage。没有第二个 usage
ledger——run history 加该 typed 行是单一真相源。

Host 与 writer 通过
`loopx.control_plane.quota.usage_collector.ingest_usage_into_run_record` 摄入
usage，接入 `write_reserved_run_artifacts` 与 `refresh-state` run 写路径。
第一个随附测量源是 Codex CLI 会话上线：`loopx refresh-state --usage-codex-session
<rollout.jsonl>` 只读取最新聚合 `token_count` 总计、模型 id、会话 id 与事件时间戳
——从不是提示、补全或工具输出。会话必须显式绑定；没有自动会话发现，
因为猜测并发会话冒把一个会话的 spend 归到另一个 run。自行测量 usage 的 host
可以改传一个完成的每 run 测量，用 `--usage-json`。不带任一标志，usage 保持 unknown。

累计 host 快照在该 producer 边界转换为非负 delta，而 run 索引追加是单一提交点：
每个会话的 delta 基从其自己已记账行重建（每会话 id 的 telescoping absolute + delta
和），而不是从第二状态文件，因此崩溃或重试永远不会把基留在 ledger 之后。
基线按会话，每个观察绑定 `usage.source_snapshot_id`，所以交错会话永不互相重新
基准：返回的会话只记账自己的增量，而不是重记账其完整累计总计。基读取与行追加在
每目标 usage 记账锁下进行，因此并发刷新不能从过期基资助两个 delta。
用相同快照身份重放相同观察是幂等零 delta；同一身份携带任何不同计数器或绑定标签
则 fail closed，而不是静默清零真实 usage。新会话以新鲜绝对观察开始，
而不是错误的重置错误。缺失可选测量保持省略（unknown），而不是零填充。
畸形、负、非有限（`NaN`/`Infinity`，在 typed builder、严格 JSON `--usage-json`
边界与禁止非标准 JSON 常量的持久序列化处被拒）、重置或乱序观察以 typed
`UsageRowError` fail closed；它们永不 clamp 或静默丢弃，失败的 usage 观察阻塞
整个 refresh 追加。Rollout 解析只容忍撕裂的最后一行（并发写噪声）；
其后带有效事件的畸形行 fail closed，而不是记账过期累计快照。
Quota/attempt 记账行不被重新解释为 token 或美元 usage。

Typed 紧凑 usage 行当前报告：

- `schema_version`：必须是 `run_usage_v0`
- `measurement_kind`：`absolute` 或 `delta`
- `source_snapshot_id`：稳定 host/runtime 快照身份，供幂等重放
- `input_tokens` / `output_tokens`：必需非负整数
- `cache_tokens` / `cost_usd` / `duration_ms`：可选；未测量时省略
- `provider` / `model`：public-safe 运行时标签

摘要当前报告：

- `runs_24h` / `runs_7d`：当前 status 样本中的观察紧凑 run 记录。
- `quota_spend_slots_24h` / `quota_spend_slots_7d`：该样本中来自
  `quota_slot_spent` 事件的槽位。
- `automation_run_count_24h` / `automation_run_count_7d`：紧凑
  `quota_event.source` 为 `heartbeat`、`automation` 或 `cron` 的 quota spend 事件。
  如果紧凑 run 索引不保留来源，`quota_slot_spent` 计为自动化/spend 代理，
  而不是丢弃。
- `progress_signal_run_count_24h` / `progress_signal_run_count_7d`：看起来像真实项目
  或 adapter 进度而非记账/簿记的紧凑 run 记录。该代理排除 `quota_slot_spent` 与
  `state_refreshed`，使 dashboard 发现一直花费或刷新状态而没有新 delivery、验证、
  映射、blocker 或 gate 信号的自动化 loop。
- `input_tokens_24h` / `input_tokens_7d`、`output_tokens_24h` /
  `output_tokens_7d`、`cache_tokens_24h` / `cache_tokens_7d`：报告 typed
  `run_usage_v0` 块 run 的聚合 token 计数。窗口（或可选指标）无测量样本时省略
  指标字段；24h 字段可以缺失而对应 7d 字段保持存在。
- `cost_usd_24h` / `cost_usd_7d`：测得时由报告运行时计算的聚合估计成本（美元），
  四舍五入到六位小数。
- `duration_ms_24h` / `duration_ms_7d`：测得时的聚合墙钟毫秒。
- `project_share_24h`：观察 24h run 的每目标份额，保留三位小数。

因为 `status --limit` 可以限制近期 run 样本，消费方应显示 `sample_run_count`，
并把这些值当作发现忙碌项目线的操作信号，而不是精确历史记账。
Markdown status 渲染器包含相同总计加顶部采样目标，使 heartbeat operator
无需打开完整 JSON payload 即可注意到低进度 loop。

## 显示模型

一个有用的首个 UI 可以只从该导出构建：

- 头部：operator 动作与所选动作分享应在辅助源控制、指标与原始下钻之上，
  因为 dashboard 是用户决策面，而不是 Agent CLI 镜像。
- 指标：`ok`、`goal_count`、`run_count` 与契约摘要。
- Canonical 首页：默认 dashboard 路由应在可用时渲染共享全局 status 源上的
  中文优先控制面首页。它应强调项目卡片、每个项目顶部的四个 todos 及逐条目状态、
  真实用户 todos、Agent 优先级 todos、quota/guard 状态与最新证据，然后才是原始
  下钻。这是 status 导出上的浏览器呈现，不是新 status 源。
- 详细 ops 视图：`?view=ops` 可以渲染更旧调试工作台，带原始队列过滤器、
  所选目标细节、奖励草稿与 run-history 面板。遗留 `view=share` 值可以保持
  canonical 首页的兼容别名，但非 ops 视图不应被当作独立持久模式。
- Usage 快照：观察 24h/7d run、quota spend 槽位、自动化 run 计数、
  进度信号 run 计数与按当前样本份额最忙目标的可选 `usage_summary` 代理指标。
- 晋升就绪 ops 面板：可选 `promotion_readiness_summary` 状态，在发布快照晋升前
  显示最新 canary promotion-readiness 证据是 fresh、stale、missing 还是 unknown。
- 晋升 gate ops 面板：可选 `promotion_gate` 状态，显示从同一就绪事件派生的紧凑
  `can_promote` / `should_warn` 发布晋升决策；dashboard 代码应显示它，
  而不是重算它。
- 决策新鲜度 ops 面板：可选 `decision_freshness_summary` 指标，用于全局决策数、
  过期数、需重新基准数、新鲜数与顶部受影响目标。该面板是旧奖励/gate 复用的路由
  警告；确切重放与事件顺序仍在仅追加 run history。
- 计算配额摘要：合格接受下一个 Agent turn 的目标、focus-waiting、throttled、
  waiting、paused 与 operator-gated 目标在 quota 字段存在时应在首屏可见。
  自动化 cadence 应被视为执行细节，而不是唯一优先级信号。
- 用户动作摘要：首屏卡片应从同一所选 operator 决策与奖励默认逻辑派生，
  在原始 goal 细节前分组奖励 gate、controller opt-in、证据关注、Codex handoff
  与阻塞健康条目。卡片可以显示匹配的安全 CLI 路径标签或命令加奖励草稿
  decision/reward 提示，但那些是 Agent 面向 status 导出上的便利能力，
  不是浏览器侧写。Dashboard 可以从这些卡片派生本地 action-kind 过滤器，
  如 reward、controller、Codex、evidence 与 health，而无需新 status 字段。
  把该焦点持久化到 URL 搜索参数是 dashboard UI 状态；它不改变 status 契约或
  持久目标真相。
- 所选目标细节：dashboard 可以把所选 `goal_id` 持久化到 URL 搜索状态，
  使评审链接可以重开同一 run-history 细节。该所选目标状态不是 status 导出的一部分，
  不得当作批准、奖励或 controller 信号。
- 评审链接：dashboard 可以复制包含本地 `actionKind`、所选 `goalId`、来源
  `statusUrl`、`lane`、`severity` 与可选 `view=ops` 搜索状态的浏览器 URL。
  该链接是该导出上的用户评审便利能力；它不得向 status 契约加字段，
  也不得改动目标运行时状态。
- Review Packet：dashboard 应为所选动作卡片暴露单一 canonical 复制便利能力，
  而不是单独的链接、回复、handoff 与 Agent 提示按钮。packet 可以包含评审链接、
  中文同意/不同意/理由/下一步提示、项目 Agent 指令、安全本地路径、奖励/默认提示与
  本地 dry-run 预览。对奖励动作，项目 Agent 区块应指向 run history 查找，
  而不是要求目标项目 Agent 代用户追加或 dry-run 用户奖励。对 controller opt-in
  动作，packet 必须保持该顺序：人类问题、用户/controller 拥有的本地 gate dry-run
  预览，然后项目 Agent dry-run 指令。dashboard/operator 视图拥有人类决策；
  项目 Agent 命令只是批准后 dry-run 执行路径。对携带 `agent_command` 的已批准
  Codex 动作，复制便利能力应切换到 handoff-only 内容：无人类 gate 包装，
  只有目标 goal guard、转发条件、执行边界、停止条件与命令。
  它仍是浏览器 UI 状态，不得解析为持久奖励、批准、controller opt-in 或
  write-control。
- Goal 目录：所有 `run_history.goals`，按 `domain` 心智分组，并在目标需要动作时
  用匹配 attention 条目与生命周期阶段徽章丰富。
- 用户评审映射：connected、mapped、refreshed、adapter-inspected、reward-judged
  与 controller-ready 目标计数，写为 operator 面向状态而非原始 adapter 状态。
  有 controller 证据但缺 gate 的目标应显示为 controller-gated，不是 controller-ready。
- 主队列：`attention_queue.items`。
- 首屏动作卡片：当队列条目携带 `operator_question`，把它显示为主要 operator 提示，
  优先于 `recommended_action`。`recommended_action` 保持上下文；
  `agent_command` 只在 operator 问题被回答后显示为安全目标 Agent 命令。
  当 Codex 拥有的队列条目有 `quota.state=focus_wait`，即使 `waiting_on=codex`
  也把它显示为 focus-wait owner blocker：卡片应说明它为何安静、谁或什么可以解锁它、
  需要哪些证据、复制 packet 仅用于 status/history 检查。
- 队列 gate 提示：直接在队列行显示 `controller_stage`、`missing_gates` 与
  `next_handoff_condition`，使 operator 无需打开完整 run payload 即可看到
  被关注目标为何未就绪。
- 用户 lane：`waiting_on=user_or_controller` 或 `controller` 条目。
- Codex lane：`waiting_on=codex` 条目。
- Watch lane：`waiting_on=external_evidence` 或 `waiting_on=monitor_signal` 条目。
- Dreaming lane/badge：带 `project_asset.dreaming_lane_badge.schema_version=
  dreaming_lane_badge_v0` 的条目。这些条目是建议性评审面；delivery lane 继续遵循
  quota 与当前 owner/gate 路由。
- 健康面板：契约 `errors`、`warnings` 与 `checks`。
- Run 细节面板：来自 attention queue 的所选目标、紧凑分类、权威覆盖、
  controller 就绪、健康检查、奖励信号与产物可用性。
- 奖励 CLI 草稿：所选目标加最新紧凑 run 时间戳应足以生成本地
  `loopx reward --dry-run` 命令。草稿字段应从所选 operator 决策与缺失 gate 默认，
  同时在验证前保持可编辑。Dashboard 只在实时 loopback status server 显式暴露
  奖励写 API 时追加反馈。
- 奖励 dry-run 检查：当 dashboard 从 loopback status server 加载时，
  它可以通过 `POST /reward/dry-run` 验证同一草稿并显示紧凑结果，
  包括中文 active-state 摘要与项目 Agent history 命令。响应包含 `preview_id`。
- 奖励追加：当同一 loopback server 以 `--enable-reward-write-api` 启动时，
  dashboard 可以把确切预览发送到 `POST /reward/append`。成功追加写一个 run 绑定
  `human_reward` overlay、刷新 status，并使下一个项目 Agent 自动化能通过
  `loopx status` 或 `loopx history` 看到反馈。
- 奖励真相源：持久用户奖励属于通过 `loopx reward` 追加的 run 绑定
  `human_reward` overlay。Active goal state 可以摘要记录了这样的奖励，
  Review Packet 可以通过返回的历史查找转发给另一个项目 Agent 做即时协调，
  但二者都不替代多 Agent 奖励信号的紧凑 run overlay。
- Operator 决策：所选目标细节应把 `waiting_on`、`severity`、`lifecycle_phase`、
  `missing_gates` 与 `recommended_action` 翻译为人类立场，如评审/授权、
  让 Codex 继续、等待证据或先修健康。原始分类保持下钻细节。
- 安全 CLI 路径：所选目标细节还应显示该立场的下一个安全本地命令类别：
  status/history 检查、read-only-map 或 refresh-state dry-run，
  或通过 Reward CLI Draft 的 reward dry-run。这是 dashboard 到 Agent 的桥；
  它不得暗示浏览器侧批准、奖励追加或写 controller 执行。

浏览器侧奖励追加在默认 status server 行为之外。如果本地 server 启用它，
必须遵循 [dashboard-reward-write-boundary.md](reference/contracts/dashboard-reward-write-boundary.md)
中的显式 opt-in 边界。

建议徽章映射：

- `severity=high`：阻塞。
- `severity=action`：需要决策或有界工作片段。
- `severity=watch`：无立即动作；等待证据或实质 monitor 转移。

## 静态 Dashboard 演示

仓库包含一个零依赖渲染器，把任何 status JSON 导出变成静态 HTML dashboard：

```bash
loopx --format json status > /tmp/goal-status.json
python3 examples/render-status-dashboard.py /tmp/goal-status.json /tmp/goal-status.html
```

生成页把队列条目分组进用户/controller、Codex-ready 与外部证据 lane。
它是本地检查与 UI 原型的小演示；不是产品 dashboard。

官方 dashboard 方向是 React/Vite 控制面 App，可以用 typed 路由、过滤器、表格、
图表与下钻页渲染同一 JSON 契约。见
[dashboard-frontend-selection.md](product/roadmaps/dashboard-frontend-selection.md)。

## Adapter 责任

Adapter 应写包含以下内容的紧凑 run 索引记录：

- `generated_at`
- `goal_id`
- `classification`
- `recommended_action`
- `json_path`
- `markdown_path`

项目 adapter 可以添加 `health_check`、`active_task_count`、`active_priorities`
或紧凑 `human_reward` 摘要等紧凑 public-safe 字段。原始日志、提示、私有指标、
工作区路径与内部文档链接属于私有 run payload，不属紧凑索引记录。

Benchmark status 快照可以包含 `runs[].observable_handle_policy`，
`schema_version=benchmark_observable_handle_policy_v0`。这是一次性 benchmark
scheduler 的附加 public-safe 生命周期投影。消费方可以用它决定 run 应继续轮询、
卸载/禁用本地 `launchd` 标签，或在任何重跑前写精确缺失 handle blocker。
它必须只从紧凑产物、pid 存活性与 run 标签派生；不得暴露原始日志、任务文本、
轨迹、scheduler payload 或本地路径。快照还可以包含
`runs[].process_polling.schema_version=benchmark_process_polling_v0` 使轮询边界
显式。该对象记录轮询只使用私有 pid 文件与紧凑产物；它必须保持
`process_table_read=false`、`cmdline_read=false`、`argv_read=false` 与
`raw_process_payload_recorded=false`，因此嵌入 worker argv 的 benchmark 任务提示
不能泄漏进 status、上线日志、聊天摘要或控制面投影。

## 边界

只有 registry id、adapter 分类与推荐动作脱敏后，JSON 导出才安全喂给本地
dashboard。公开分享导出前，验证它不含：

- 本地绝对用户路径，
- 私有文档链接，
- 凭据，
- 原始生产日志，
- 内部任务 id，
- 私有指标值。

`examples/` 下的公共示例已脱敏，可用于演示。

## 兼容规则

- 允许附加字段。
- 现有字段含义应在小版本间保持稳定。
- 消费方应忽略未知字段。
- 消费方应把缺失的 `attention_queue.items` 当作空队列处理。
- 消费方应把缺失的 `run_history` 当作不可用处理。
- 消费方应把 `contract.ok=false` 当作比空 attention queue 更强的信号。
