# openviking_session_memory_adapter_v0
> [English](openviking-session-memory-adapter-v0.md)

`openviking_session_memory_adapter_v0` 是 [session_runtime_loopx_projection_v0](session-runtime-loopx-projection-v0.md) 面向 OpenViking 式 issue-fix 工作流的公开安全特化。它预览 LoopX 如何在不把原始轨迹、issue 评论或工具输出复制进 LoopX 状态的情况下，把紧凑的每 goal、每 issue 会话状态连接到记忆检索决策。

这是只读适配器契约。它不执行实时 OpenViking 检索、不写记忆、不读取 issue/评论正文、不发布评论、不创建 PR、不修改运行时状态。

## 边界

事实来源仍保持拆分：

- 会话运行时拥有原始 transcript、工具调用、工具输出、轨迹、host 认证与原始执行日志；
- issue 跟踪器拥有 issue 正文、评论正文、timeline 与 provider 载荷；
- 记忆系统拥有 embeddings、原始记忆记录、检索查询与 writeback 交易；
- LoopX 拥有紧凑 goal 状态、todos、gates、quota、run 历史与公开安全投影记录。

适配器可以保留紧凑关联键，如 goal id、issue ref、session id、memory ref id、run id 与 todo id。它不得复制原始正文、原始轨迹行、prompt 文本、工具输出文本、凭据、私有 URL 或本地文件系统路径。

## 形状

```json
{
  "schema_version": "openviking_session_memory_adapter_v0",
  "mode": "read_only_projection",
  "specializes": "session_runtime_loopx_projection_v0",
  "goal_id": "loopx-meta",
  "issue_projection": {},
  "session_projection": {},
  "memory_projection": {},
  "retrieval_gates": [],
  "status_projection": {},
  "evidence_projection": {},
  "future_gates": [],
  "truth_contract": {
    "source_of_truth": [
      "loopx_goal_state",
      "session_runtime_projection",
      "public_issue_metadata",
      "memory_system_refs"
    ],
    "adapter_is_writable": false,
    "live_retrieval_allowed": false,
    "memory_writeback_allowed": false,
    "issue_body_read_allowed": false,
    "comment_body_read_allowed": false,
    "tool_output_ingest_allowed": false
  }
}
```

## Issue 投影

`issue_projection` 限于路由元数据：

- `provider`：紧凑 provider 标签，如 `github`；
- `repo`：安全时的公开仓库 slug；
- `issue_number`：数字 issue 或 PR id；
- `issue_ref_id`：紧凑公开安全关联键；
- `title_summary`：适配器或操作员编写的可选简短摘要；
- `issue_body_copied`：公开 fixture 中始终 false；
- `comment_bodies_copied`：公开 fixture 中始终 false；
- `provider_payload_copied`：公开 fixture 中始终 false。

若真实修复需要正文或评论文本，把它表示为关卡。不要把文本复制进本投影。

## 会话投影

`session_projection` 把 issue 映射到紧凑运行时状态：

- `runtime_id`；
- `session_refs[]`：公开安全 session id 或脱敏句柄；
- `latest_event_ref`；
- `linked_todo_ids[]`；
- `outcome_refs[]`；
- `raw_trajectory_copied`：false；
- `raw_transcripts_copied`：false；
- `raw_tool_outputs_copied`：false。

投影可以说会话被阻塞、已验证或过期。它不得包含原始 prompt、源 diff、工具输出、trace URL 或终端日志。

## 记忆投影

`memory_projection` 是记忆路由的预览，不是记忆转储：

- `namespace`：紧凑记忆命名空间；
- `retrieval_mode`：`preview_only`、`disabled` 或 `future_gated`；
- `live_retrieval_performed`：v0 公开 fixture 中为 false；
- `writeback_performed`：v0 公开 fixture 中为 false；
- `query_summary`：为何检索会有用的公开安全摘要；
- `top_k_preview`：请求的预览计数，不是实时检索结果；
- `candidate_refs[]`：记忆引用行。

每个候选引用可包括：

- `memory_ref_id`；
- `source_kind`：`prior_issue`、`session_outcome`、`operator_note`、`validation_summary` 或 `unknown`；
- `score_bucket`：`high`、`medium`、`low` 或 `unknown`；
- `summary`：紧凑公开安全笔记；
- `raw_memory_copied`：false。

适配器不得暴露 embeddings、向量内容、原始记忆正文、私有 issue 文本、prompt 摘录或工具输出。

## 检索关卡

`retrieval_gates[]` 描述真实检索或 writeback 前必须批准什么：

- `capability`：`live_openviking_retrieval`、`memory_writeback`、`issue_body_read`、`comment_body_read` 或 `raw_tool_output_ingest`；
- `state`：`future_gated`、`blocked_without_authority` 或 `approved`；
- `required_authority`：紧凑权限标签；
- `blocks`：在该关卡批准前仍保持禁用的内容。

在 v0 中，即使公开 fixture 有候选引用，实时 OpenViking 检索与记忆 writeback 仍保持未来关卡。这使 fixture 可复现，并避免意外依赖私有本地记忆存储。

## 状态与证据投影

`status_projection` 遵循 session-runtime 首屏契约：

- `waiting_on`；
- `next_action`；
- `user_action_required`；
- `agent_can_continue`；
- `first_agent_todo`；
- `gate_state`；
- `quota_state`；
- `memory_state`：`preview_only`、`future_gated`、`blocked` 或 `disabled`。

`evidence_projection` 只包含紧凑引用：

- `source_refs`：goal、issue、session、memory、todo 与 run id；
- `validation_refs`：smoke、检查、CI 或评审证明 id；
- `raw_trajectories_copied`、`comment_bodies_copied`、`raw_tool_outputs_copied`、`credentials_copied`、`private_paths_copied`：公开 fixture 中全部 false；
- `public_safe_summary`。

## 未来关卡

以下能力在 v0 中保持未来关卡：

- `live_openviking_retrieval`；
- `memory_writeback`；
- `issue_body_read`；
- `comment_body_read`；
- `raw_tool_output_ingest`；
- `external_issue_comment_or_pr_publish`。

任何未来实现必须添加一个带显式权限、dry-run 预览、审计 id、公开/私有边界检查与失败行为的独立实时适配器契约，这些关卡才可移到 `approved`。

## 验收检查

一个公开 fixture 或实现在以下条件下可接受：

1. `schema_version` 恰好是 `openviking_session_memory_adapter_v0`；
2. `mode` 恰好是 `read_only_projection`；
3. `specializes` 恰好是 `session_runtime_loopx_projection_v0`；
4. issue 投影把 issue 正文、评论正文与 provider 载荷排除在 fixture 之外；
5. session 投影把原始轨迹、transcript 与工具输出排除在 fixture 之外；
6. memory 投影仅预览或未来关卡，未执行实时检索或 writeback；
7. 候选引用包含紧凑 id、分数桶、来源种类与摘要，但不含原始记忆正文；
8. 检索关卡包括实时检索、记忆 writeback、issue 正文读取、评论正文读取与原始工具输出摄取；
9. 状态投影可在无私有证据的情况下渲染首屏；并且
10. 公开 fixture 不包含原始轨迹、评论正文、工具输出、凭据、私有链接、本地路径或内部项目名。
