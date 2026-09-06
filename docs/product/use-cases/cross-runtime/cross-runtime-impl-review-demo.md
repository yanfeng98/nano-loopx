# 跨 Runtime 实现/评审演示


本说明为"Claude Code 实现，Codex 评审"这一模式定义一个 LoopX 原生 demo 路径，同时不让任一 runtime 成为事实源。

可比的产品形态是双 agent 编码 loop，但 LoopX 应展示不同的强项：跨 agent surface 的持久状态、gates、evidence、quota 与 handoff。Demo 应让角色拆分可见，同时保留 LoopX 的控制面边界。

## Demo 声明

LoopX 可以跨不同 agent runtime 协调实现/评审 loop：

- Claude Code 拥有一个实现 todo 并写出有边界 patch。
- Codex 拥有一个评审 todo 并产出结构化评审判定。
- 一个 verifier 命令或 smoke 结果被记录为紧凑 evidence。
- LoopX 拥有 todo claims、gates、evidence、quota 与下一个 handoff。

Demo 不得声称 LoopX 本身是通用执行器。Runtime 启动仍属宿主 surface：Claude Code `/loop`、Codex App heartbeat、Codex CLI TUI goal 模式或显式 shell 桥。

## 当前 Public-Safe 流程

```text
用户需求
   │
   ▼
/loopx <implementation goal>
   │
   ▼
LoopX 写两个 role-scoped todos
   │
   ├─ claude-code-impl 认领 implementation
   │     └─ patch 摘要 + 变更文件 + 验证尝试
   │
   └─ codex-review 认领 review
         └─ PASS/BLOCK 判定 + 发现 + 所需 verifier
   │
   ▼
review-packet + quota should-run 决定下一个 handoff
```

最小命令 surface：

```bash
loopx demo impl-review --preset claude-codex --dry-run

loopx todo add --goal-id <goal> --role agent \
  --text "[P0] Implement <bounded requirement>." \
  --claimed-by claude-code-impl

loopx todo add --goal-id <goal> --role agent \
  --text "[P0] Review the implementation patch and verifier result." \
  --claimed-by codex-review

loopx --format json quota should-run --goal-id <goal> --agent-id claude-code-impl
loopx todo claim --goal-id <goal> --todo-id <todo_id> --claimed-by claude-code-impl
loopx review-packet --goal-id <goal>
loopx --format json quota should-run --goal-id <goal> --agent-id codex-review
```

对 Claude Code，可见 runtime 入口保持：

```text
/loopx <implementation goal>
/loop
```

对 Codex，可见评审入口保持为既有 Codex surface 之一：

```text
/loopx Review <implementation evidence>
```

或一个 `quota should-run --agent-id codex-review` 选中评审 todo 的 Codex App heartbeat。

## 状态形态

```yaml
cross_runtime_impl_review_demo_packet_v0:
  goal_id: "public demo goal"
  requirement: "bounded user-visible change"
  roles:
    implementer:
      agent_id: "claude-code-impl"
      runtime: "claude_code"
      owns:
        - patch proposal
        - implementation evidence summary
        - first verifier attempt
      must_not:
        - approve its own review gate
        - publish or merge without owner approval
    reviewer:
      agent_id: "codex-review"
      runtime: "codex"
      owns:
        - review verdict
        - blocker list
        - verifier recommendation
      must_not:
        - rewrite the implementation unless explicitly handed a fix todo
        - treat style preferences as blocking defects
  loopx_control_plane:
    owns:
      - todo claims
      - quota decisions
      - human gates
      - compact evidence
      - review packet
      - next handoff
  verifier:
    command: "project-specific smoke or test command"
    required_before_done: true
  stop_conditions:
    - user gate required
    - source or write boundary unclear
    - verifier missing or inconclusive
    - reviewer BLOCK verdict with no bounded fix todo
```

## 评审判定契约

评审者输出应足够紧凑，供 `review-packet` 与 dashboards 使用：

| 字段 | 含义 |
| --- | --- |
| `verdict` | `PASS`、`BLOCK` 或 `INCONCLUSIVE`。 |
| `blockers` | 仅客观缺陷：失败测试、损坏行为、未满足需求、不安全边界。 |
| `suggestions` | 非阻塞的风格、命名或后续说明。 |
| `verifier` | 已运行、推荐或缺失的命令或 smoke。 |
| `handoff` | 下一个 todo owner：implementer 修复、reviewer 接受、user gate 或归档。 |

这使 demo 不至于变成两个模型之间的争吵。`BLOCK` 判定创建或保留实现 todo；`PASS` 判定在完成前仍要求 verifier evidence。

## 产品化路径

1. **仅文档/demo。** README 与本说明描述角色契约、命令与边界。
2. **夹具彩排。** 公开 smoke 不运行任一 runtime 就检查 implementer evidence、reviewer 判定、verifier 结果与下一个 handoff。
3. **Host adapter packet。** `loopx demo impl-review --preset claude-codex --dry-run` 渲染 `cross_runtime_impl_review_demo_packet_v0`；它不写状态、不启动 runtime，只渲染规划的 todos、gates、命令与 evidence 边界。
4. **Opt-in 执行。** 只在 packet 稳定后，通过其原生可见 surface 启动 Claude Code 或 Codex，并记录紧凑 evidence。

v0 demo 应止步于文档加夹具验证。这足以展示 LoopX 相较单 runtime loop 的优势：角色拆分跨工具幸存，但人类 gates 与 evidence 保持集中。

## 边界

允许的公开 evidence：

- public-safe 需求摘要；
- todo id 与 agent id；
- 变更文件摘要；
- verifier 命令与 pass/fail/inconclusive 标签；
- 评审判定与 blocker 标题；
- review-packet 或 dashboard 链接。

禁止的 evidence：

- 原始 Claude 或 Codex transcripts；
- 私有 prompt、凭据、本地秘密或私有文档链接；
- 原始 benchmark 任务文本、轨迹、日志或 verifier 尾部；
- 未发布 maintainer 消息；
- 未经 owner gate 的权限变更、合并、发布或外部评论。

这让 demo 兼容 LoopX 的 public/private 边界与既有 Claude Code opt-in adapter。
