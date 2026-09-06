# local_agent_launch_plan_v1

`local_agent_launch_plan_v1` 是一个公开安全的 dry-run 契约，用于预览 LoopX 如何在任何 host 启动 worker、daemon、server 或外部进程之前，把本地对等 agent 分配给当前 todo。

它只回答一个狭窄问题：「给定已注册对等方、配额、todo claim、任务策略与当前关卡，操作员应看到怎样的启动预览？」它不是启动器、scheduler、任务 lease 存储或权限授予。

## 边界

事实来源仍为：

- registry 的 `coordination.agent_model=peer_v1` 与 `registered_agents`；
- `quota should-run` 及其 `interaction_contract`；
- todo 投影、claims/leases、capabilities、gates 与 run 历史；
- 任务/仓库工作区与评审策略。

计划为 `mode=dry_run`。它不得启动进程、分配 shell、打开 daemon 连接、调用远程 agent 服务、认领 todo 或写入 LoopX 状态。

## 形状

```json
{
  "schema_version": "local_agent_launch_plan_v1",
  "mode": "dry_run",
  "goal_id": "loopx-meta",
  "agent_model": "peer_v1",
  "generated_at": "2026-07-10T04:00:00Z",
  "configured_agents": [],
  "task_assignments": [],
  "launch_preview": [],
  "status_projection": {},
  "evidence_projection": {},
  "future_gates": [],
  "truth_contract": {
    "source_of_truth": [
      "registry",
      "quota_should_run",
      "todo_projection",
      "run_history"
    ],
    "plan_is_authoritative": false,
    "plan_is_executable": false,
    "write_api": false,
    "launch_command_allowed": false,
    "recompute_rule": "Recompute before each preview."
  }
}
```

没有 goal 级 leader id。host 可以显示为某任务包选中的对等方，但该协调者是确定性的且临时的；它不会获得对其他身份的持久化权限。

## 已配置 Agent

`configured_agents[]` 是身份与能力检查后的发现对等方列表。每项包括：

- `agent_id`；
- `agent_model=peer_v1`；
- 可选咨询性 `profile_role` 与 `scope_summary`；
- `source`，通常为 `registry.coordination.registered_agents`；
- `can_receive_work` 与紧凑的 `blocked_by` 原因。

不要把原始自动化 prompt、私有聊天历史、本地路径或 connector 载荷复制进预览。

## 任务分配

`task_assignments[]` 为显示目的把当前 todo 映射到对等方。必需字段：

- `agent_id` 与 `todo_id`；
- `assignment_kind`：`claimed`、`unclaimed_candidate`、`monitor_only` 或 `blocked`；
- `responsibility`：一句紧凑公开安全的话；
- `claim_policy`：该 todo 必须如何认领或转移；
- 可选 `action_kind`、`excluded_agents` 与 `unblocks_todo_id`，用于任务语义、执行者分离与依赖血统。

分配是咨询性的预览行。真实认领或转移仍使用 todo 生命周期。profile 不能提供隐式评审者。

## 启动预览

每个预览描述 host 在启动前会显示什么，并保持不可执行：

```json
{
  "preview_id": "preview_peer_delivery",
  "agent_id": "codex-product",
  "todo_id": "todo_public_slice",
  "next_step_label": "Build the public dry-run fixture slice.",
  "workspace_policy": "selected_task_requires_isolation",
  "host_execution": {
    "will_start_process": false,
    "tool_call_allowed": false,
    "shell_command": null,
    "daemon_required": false,
    "external_service_call": false
  }
}
```

预览可以指名 todo 与任务工作区策略，但不得包含可运行命令、进程 id、凭据、认证 token、私有路径或远程 URL。真实启动支持需要单独的 host 执行契约。

## 状态与证据投影

`status_projection` 包括 `waiting_on`、`next_action`、`user_action_required`、`agent_can_continue`、`first_agent_todo`、`gate_state`、`quota_state` 与 `launch_state`。

`evidence_projection` 携带紧凑来源与验证引用，以及针对原始日志、transcript、凭据与私有路径的显式 false 标记。证据引用是关联键，不是内嵌载荷。

## 未来关卡

以下仍保持未来关卡：

- `server_daemon_launch`；
- `external_agent_execution`；
- `credentialed_host_actions`；
- `state_write_from_preview`。

每个关卡标明 `future_gated` 或 `blocked_without_authority`，以及它可以启用前所需契约。

## 验收检查

一个 fixture 或实现在以下条件下可接受：

1. `schema_version=local_agent_launch_plan_v1`、`agent_model=peer_v1` 且 `mode=dry_run`；
2. 已配置 agent 是唯一对等方且无 leader/parent 角色；
3. 每个任务分配都引用一个已配置对等方与既有 todo；
4. 评审保持 `action_kind=review`；任何执行者排除都是显式的；
5. 每个预览保持所有 host 执行布尔值为 false 且命令为 null；
6. 状态与证据投影保持紧凑且公开安全；
7. 所有真实启动、凭据与预览写入能力都保持受限。
