---
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
product_contract_source: ce-plan-bootstrap
---

# 修复 Codex App Thread Agent 身份复用

> [English](issue-2785-thread-agent-identity.md)

## 目标

让同一个稳定 Host thread 中重复的 Codex App `/loopx` 调用复用该 thread 已经选定的
Agent identity。一个任务、worktree 或新的 Todo 本身不得创建新的 peer。

## 决策

- 绑定键是 `(host_surface, goal_id, thread_id)`，映射到一个已经注册的 `agent_id`。
- 当没有显式 `--thread-id` 时，Codex App 的 `start-goal` 使用其环境中的
  `CODEX_THREAD_ID`。其他 Host 可以传入不透明 thread ID。
- 身份解析优先使用已验证的 thread 绑定。来自当前 Host task 活跃交互契约的确切 Agent 是
  一个有效的初始选择，并且必须在 Todo writeback 之前绑定。
- 一个稳定的未绑定 thread 是一个新的 Host session，默认采用全新注册。registry 顺序与
  单一注册 lane 不是 takeover 的身份证据。
- 缺失的 thread ID 或冲突的绑定失败关闭（fail closed）。当 Host 无法提供稳定 ID 时，
  `--new-peer` 携带显式的全新 session 意图；任务文本、新 Todo 或 worktree 绝不含该意图。
- 绑定是一次显式的、幂等的变更。source/global registry 同步与绑定 readback 必须在继续
  规划或 Todo writeback 之前成功。

## 边界

范围内：

- 有界的不透明 thread-ID 校验与 project/global registry 持久化；
- guided `start-goal` 身份解析与命令传播；
- 生成的 `/loopx` 与 project-skill 指南；
- 单元、CLI 与合成 public-smoke 覆盖。

范围外：

- Codex App 的 Host 变更或合成 thread ID；
- 从对话文本或 registry 顺序进行身份推断；
- 跨 runtime 的身份转移、过期或绑定管理 UI；
- 原始 transcript、凭证、路径或私有 host 元数据。

## 必需事务

对于未绑定的 Codex App thread：

1. 检查已连接的 goal 与已注册 lanes；
2. 默认采用全新注册，或仅在显式 takeover 时选择现有 lane；
3. 选中后注册全新身份，然后执行 `bind-agent-thread --execute`；
4. 要求 `ok=true`、`global_sync.ok=true` 与 `registration_readback.verified=true`；
5. 只有在此之后才规划并写入 Todo 状态、refresh、激活并运行 quota。

后续相同绑定的调用会在 `start-goal`、heartbeat、quota、refresh-state 与 Todo 命令中直接复用
已绑定的 Agent。它们不重复绑定变更。

## 验证

聚焦验证必须覆盖：

- 非法、缺失、幂等与冲突的绑定；
- 环境 Codex App thread-ID 解析；
- 在 Todo writeback 之前的绑定/readback 有序步骤；
- 真实首次调用绑定，随后一次不带 `--agent-id` 的第二次调用；
- 一个稳定未绑定 thread 默认采用全新注册，同时保留显式的现有 lane takeover；
- 除非 `--agent-id` 或 `--new-peer` 显式给出，缺失的 thread ID 保持 fail closed；
- 生成的 Skill 文本复用活跃 task 身份，绝不让 worktree、Todo 或带参数调用成为新 peer；
- public smoke 的独立与官方 runner 执行。

最低命令：

```bash
pytest -q \
  tests/test_thread_agent_binding.py \
  tests/control_plane/test_start_goal_compact_projection.py \
  tests/test_slash_command_install.py
python3 examples/codex-app-thread-agent-identity-smoke.py
python3 examples/run-smokes.py --suite full-public \
  --script examples/codex-app-thread-agent-identity-smoke.py --json
git diff --check
```

## 完成定义

- 一个 Codex App task 中重复的 `/loopx` 调用复用同一个稳定 Agent lane。
- 首次显式 lane 选择在写入任何 Todo 之前已 durable 绑定并 readback。
- 缺失的 thread ID 与冲突的绑定在没有意外 peer 创建的情况下保持 fail closed。
- 全新 peer 注册是显式的、已验证的，并可单独归因。
- CLI、packet、Skill、协议与测试表达同一条身份规则。
