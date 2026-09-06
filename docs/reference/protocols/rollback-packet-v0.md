# rollback_packet_v0

`rollback_packet_v0` 是长程 LoopX 工作的公开安全补偿协议。它描述投递步骤造成风险之后必须撤销、修复前进、清理或监控的内容。它是计划与证据包，不是执行许可。

LoopX 中的回滚比 `git revert` 更广。长程任务可能需要补偿仓库提交、本地状态投影、外部资源、开放 PR、缓存公开界面、todo 所有权或用户关卡。包使这些关系显式，使 agent 不抹除历史、不重复同一不安全动作，也不让操作员猜测仍暴露什么。

## 产品契约

包存在的目的是回答五个问题：

1. 哪些可见或持久化状态受影响？
2. 是哪个 todo、rollout 事件、commit、PR 或外部资源导致的？
3. 下一安全动作是 revert、fix-forward 补丁、状态修正、支持请求、外部清理还是 monitor？
4. 谁必须批准受保护或破坏性步骤？
5. 哪些验证与公开/私有边界检查证明补偿已完成？

## 形状

```json
{
  "schema_version": "rollback_packet_v0",
  "packet_id": "rollback_public_boundary_example_v0",
  "goal_id": "public-long-horizon-loop",
  "created_at": "2026-06-24T01:20:00+08:00",
  "trigger": {
    "kind": "public_boundary_leak",
    "summary": "A public PR surface exposed context that should remain local.",
    "todo_ids": ["todo_public_boundary_repair"],
    "source_event_ids": ["evt_lh_005_minimal_fixture_validated"]
  },
  "scope": {
    "repository_refs": {
      "commit_refs": ["abcdef1"],
      "pr_refs": ["huangruiteng/loopx#617"]
    },
    "todo_ids": ["todo_public_boundary_repair"],
    "external_resource_refs": ["github_support_request"],
    "user_visible_surfaces": ["pull_request", "cached_view"],
    "local_state_refs": []
  },
  "decision": {
    "owner": "maintainer",
    "required": true,
    "reason": "History rewrite and external cached-view removal require explicit owner action.",
    "default_safe_action": "pause_and_monitor"
  },
  "plan": [
    {
      "step_id": "clean_main_history",
      "kind": "history_rewrite",
      "action": "replace public branch history with a clean equivalent commit set",
      "requires_gate": true,
      "destructive": true,
      "automatable_by_agent": false
    },
    {
      "step_id": "submit_support_request",
      "kind": "support_request",
      "action": "ask provider support to remove read-only PR refs and cached views",
      "requires_gate": true,
      "destructive": false,
      "automatable_by_agent": false
    },
    {
      "step_id": "verify_public_boundary",
      "kind": "validation",
      "action": "scan normal heads and changed public paths for private markers",
      "requires_gate": false,
      "destructive": false,
      "automatable_by_agent": true
    }
  ],
  "todo_compensation": {
    "complete_todo_ids": ["todo_submit_support_request"],
    "add_todos": [
      {
        "role": "agent",
        "task_class": "continuous_monitor",
        "title": "Verify provider-side cached view removal after support response."
      }
    ],
    "supersede_todo_ids": []
  },
  "validation": {
    "commands": [
      "git diff --check",
      "loopx check --scan-path <public-safe-path>",
      "git ls-remote --heads origin"
    ],
    "public_boundary_scan_required": true,
    "success_criteria": [
      "normal public heads no longer contain the affected public markers",
      "provider-owned cached views or read-only refs are removed or tracked by an open external gate",
      "successor monitor todo exists when external cleanup is pending"
    ]
  },
  "boundary": {
    "raw_task_text_recorded": false,
    "raw_logs_recorded": false,
    "raw_trajectory_recorded": false,
    "raw_session_transcript_recorded": false,
    "credential_values_recorded": false,
    "absolute_paths_recorded": false
  }
}
```

## 种类

允许的触发种类：

- `validation_regression`；
- `public_boundary_leak`；
- `operator_request`；
- `external_setup_partial_failure`；
- `wrong_owner_or_lane`；
- `bad_state_projection`；
- `release_or_publish_mistake`。

允许的计划步骤种类：

- `git_revert`：创建正常 revert 提交；
- `fix_forward`：保留历史并添加修正补丁；
- `history_rewrite`：重写公开分支历史；始终受保护；
- `state_compensation`：修正 LoopX active state、todo 元数据或 rollout 事件投影；
- `external_cleanup`：清理外部资源；
- `support_request`：请 provider 移除只读或缓存界面；
- `todo_supersede`：用 successor 工作替换过期 todos；
- `validation`：证明补偿状态。

## 提交与 Todo 关联

提交到 todo 的关联是最小有用回滚锚点。公开 PR 或提交应可追溯至：

- 一个或多个 `todo_id` 值；
- 可用时的一个或多个 rollout 事件 id；
- 验证命令或公开安全证据引用；
- 完成后的 successor todos 或 no-follow-up 理由。

该关联不要求每条提交消息编码全部细节。它要求足够持久化状态，使后续 agent 能回答「此提交补偿、接替或验证哪个 todo？」而无需读取私有聊天历史。

关联缺失时，用 rollback 包在触碰历史之前创建缺失的补偿 todos。

## 安全规则

- rollback 包不授权破坏性 git 命令、force push、生产动作、provider 支持请求、外部删除或公开评论。
- `history_rewrite` 需要显式用户或 maintainer 批准以及备份或等价恢复点。
- Provider 自有的只读引用、缓存视图或搜索索引是外部清理。若普通仓库命令无法移除它们，包必须保持用户/支持关卡或 monitor todo 开放。
- 外部资源设置应优先保存部分成功，而非删除。若可用板、base、环境或工件已创建，先保存最小可用本地配置，然后把可选富化失败视为警告或后续工作。
- 当 fix-forward 能避免受保护历史操作并完全移除用户可见风险时，优先使用它。
- 公开 fixture 与包不得包含原始日志、原始 transcript、凭据、本地绝对路径或私有源正文。

## 验收检查

一个有效包或实现必须证明：

- `schema_version` 恰好是 `rollback_packet_v0`；
- 每个计划步骤有 `step_id`、`kind`、`action`、`requires_gate`、`destructive` 与 `automatable_by_agent`；
- 破坏性或 provider 自有动作需要关卡；
- 包关联至少一个 todo、rollout 事件、commit/PR 引用或外部资源引用；
- 回滚步骤后仍有工作时 todo 补偿显式；
- 验证命令是公开安全标签，而非原始日志；
- 边界标志存在且为 false。

持久化 smoke 是：

```bash
python3 examples/protocol/rollback-packet-protocol-smoke.py
```
