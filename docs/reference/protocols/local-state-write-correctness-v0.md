# 本地状态写入正确性 v0

状态：LoopX 本地状态写入的公开安全协议草稿。

LoopX 仍把 Markdown active state 保持为人与 agent 工作界面。本契约定义任何改变该本地状态或派生本地控制面工件的写入的正确性信封。它不是新存储后端。它是通用包形状，使未来实现可以增加更强锁、幂等重试、乐观修订检查与 lease 投影，而无需分别改每个写者。

## 范围

本协议适用于本地 LoopX 写入，例如：

- active-state todo 添加、更新、完成、接替与归档操作；
- 更新路由、进度或下一动作的 `refresh-state` 写入；
- 后来投影进 active state 的 event-store 追加操作；
- 记录紧凑本地证据的评审包或 dashboard writeback。

它不授予读取私有物料、外部发布、运行生产动作、绕过人类关卡或修改远程服务的权限。那些仍是独立边界决策。

## 正确性模型

每个本地写入应可描述为一个 `write_intent`：

| 字段 | 含义 |
| --- | --- |
| `write_id` | 本次请求逻辑写入的稳定 id。 |
| `goal_id` | Goal 边界。写者不得锁定或修订无关 goal。 |
| `writer_id` | 发起写入的已注册 agent、CLI 命令或适配器。 |
| `write_class` | 紧凑操作家族，如 `todo_update`、`refresh_state` 或 `event_append`。 |
| `target_refs` | Goal 局部引用，如 `todo_id`、`run_id` 或 `state_file`。 |
| `idempotency_key` | 确定性重试键。重放同一键不得重复逻辑效果。 |
| `expected_revision` | 写入前读取的可选乐观修订/CAS token。 |
| `lease_ref` | 解释写者为何可以继续的可选每 todo 或每 goal lease。 |

锁边界默认按 goal。当写入只触及一个 todo，且写者能证明不受节排序、归档压缩或共享摘要更新影响时，允许更窄的每 todo 锁。

## 必需相位

1. `prepare`：解析 `goal_id`、target refs、当前修订与边界策略。此处不发生写入。
2. `preview`：产出紧凑补丁摘要与安全结果。
3. `apply`：获取锁、重读修订，不匹配则拒绝或合并，然后原子写入。
4. `record`：发出带 applied/skipped/rejected/failed 状态的紧凑证据。
5. `project`：在 status/review 包中暴露最新修订、锁边界与相关 lease 状态，而不复制原始私有状态。

## 冲突语义

- 同一 `idempotency_key` 且意图效果相同：返回 `skipped_duplicate` 或 `already_applied`。
- 锁持有期间同一目标但不同幂等键：等待或返回 `lock_busy`。
- `expected_revision` 不匹配：失效关闭为 `revision_conflict`，除非写者可以从新修订重算非重叠补丁。
- Lease 过期或被不同写者持有：失效关闭为 `lease_conflict`；不静默清除另一个 agent 的 claim。
- 载荷不安全：以 `boundary_rejected` 拒绝且不写本地状态。
- 无变更的 dry-run 预览：返回 `preview_only`，并包含真实 apply 所需的同一 write intent、锁边界、修订与预期写 scope。

## 示例包

```json
{
  "schema_version": "local_state_write_correctness_v0",
  "write_intent": {
    "write_id": "write_todo_123_complete_001",
    "goal_id": "loopx-meta",
    "writer_id": "codex-product-capability",
    "write_class": "todo_update",
    "target_refs": {
      "todo_id": "todo_123",
      "state_file_ref": "registry.goal.state_file"
    },
    "idempotency_key": "loopx-meta:todo_123:complete:write_todo_123_complete_001",
    "expected_revision": {
      "kind": "active_state_revision",
      "value": "sha256:before-write"
    },
    "lease_ref": {
      "kind": "todo_claim",
      "goal_id": "loopx-meta",
      "todo_id": "todo_123",
      "claimed_by": "codex-product-capability",
      "lease_id": "lease_todo_123_codex_product_capability"
    }
  },
  "lock_boundary": {
    "kind": "per_goal",
    "lock_key": "goal:loopx-meta",
    "narrower_lock_allowed": "per_todo_when_patch_is_single_todo_and_order_independent"
  },
  "preview": {
    "mode": "dry_run",
    "patch_summary": "mark todo_123 done and attach compact evidence",
    "non_destructive": true,
    "expected_write_scopes": [
      "active_state"
    ]
  },
  "apply_result": {
    "status": "applied",
    "applied_revision": {
      "kind": "active_state_revision",
      "value": "sha256:after-write"
    },
    "duplicate_of": null,
    "conflict": null
  },
  "projection": {
    "status_surface": "todo_123 done",
    "lease_projection": {
      "todo_id": "todo_123",
      "claimed_by": "codex-product-capability",
      "lease_state": "released_after_done"
    },
    "public_boundary": {
      "raw_logs_copied": false,
      "private_paths_copied": false,
      "credentials_copied": false,
      "production_action_authorized": false
    }
  }
}
```

## 验收检查

一个本地状态写者在本协议下兼容，当：

1. 它能在变更前产生或内部推导 `write_intent`；
2. 同一 `idempotency_key` 的重试不能重复 todos、证据或事件；
3. 锁 scope 至多为按 goal，除非操作被证明为单 todo 且顺序无关；
4. 乐观修订不匹配失效关闭，或从新鲜状态重算；
5. lease 投影绝不使一个 agent 静默窃取另一个 agent 的 claim；
6. 公开 status/review 包在不含原始本地文件、私有路径、凭据、原始日志或原始 transcript 的情况下暴露紧凑修订与 lease 状态；
7. 每个破坏性或外部效果仍保持在单独的显式关卡之后。

## 运行时提升关卡

当前实现目标是预览优先。一个改变真实写入行为的后续补丁，必须携带一个小提升关卡，才能对规范写入路径强制硬幂等、修订检查或 lease 冲突。阶段关卡是公开安全 fixture 契约，不是权限授予。

```json
{
  "schema_version": "local_state_write_correctness_rollout_gate_v0",
  "writer_id": "loopx.todo",
  "write_class": "todo_update",
  "current_mode": "dry_run_preview",
  "promotion_target": "shadow_validate",
  "allowed_to_change_write_behavior": false,
  "required_evidence": {
    "dry_run_packet_smoke": "examples/control_plane/todo-write-correctness-smoke.py",
    "idempotency_key_stability": "same logical input produces the same idempotency_key",
    "expected_revision_fixture": "expected_revision is computed from the active state before mutation",
    "revision_conflict_fixture": "stale expected_revision returns revision_conflict before mutation",
    "lease_projection_fixture": "foreign or expired lease returns lease_conflict before mutation",
    "public_boundary_scan": "loopx check --scan-path <changed-public-paths>"
  },
  "exit_criteria": [
    "dry-run JSON and markdown projections stay stable",
    "duplicate retries cannot duplicate todos, evidence, events, or refresh runs",
    "revision and lease conflicts are observable without copying raw state",
    "status and review packets expose only compact public-safe write refs"
  ]
}
```

`allowed_to_change_write_behavior=false` 意为补丁可以增加 fixture、投影或影子验证脚手架，但不得拒绝或改写先前已接受的真实写入。后续强制补丁只有在对应写者具有所需冲突 fixture 且其回滚行为已文档化时才能翻转该字段。这使推出保持小：先在单个写者上证明契约，再在单独验证步骤中收紧行为。

## 推出说明

首个实现步骤应是非破坏性的：添加协议文档与 fixture smokes，然后适配一个既有写者在 dry-run 中发出或验证紧凑形状。只有在一致性证明之后，LoopX 才应以硬幂等键、乐观修订/CAS 或按 goal 锁元数据收紧运行时写入路径。
