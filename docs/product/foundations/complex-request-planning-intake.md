# 复杂请求规划接收


本笔记为大型用户请求定义一个可摄入的有界模式。它通过把策略密集的对话转化为小型的、类型化的 LoopX 计划,让 agents 可以检查、认领与验证,从而防止它变成不可见的聊天历史。

该模式刻意保守。它不是交付捷径、领域专家或权限授予。它是一个规划接收器,在保留权威、范围与公开/私有边界的同时,把混乱上下文转化为控制面对象。

## 何时使用

当用户输入混合了以下多个信号时,使用 `complex_request_intake_v0`:

- 一次 Turn 中的产品策略、路线图、合作伙伴想法、基准方向或发布规划;
- 多个可能的工作车道且归属不清;
- 引用现有权威文档、active state 或先前决策;
- 要求"先想清楚整个计划"再实现;
- 心跳只在聊天中发现重要策略,而非 LoopX state。

不要把它用于窄 bug 修复、单次文档编辑、直接 PR 合并或清晰的单步用户 gate。

## 产品角色

复杂接收位于智能管理界面与正常 LoopX 执行之间:

```text
large user signal
  -> complex_request_intake_v0
  -> small typed todo batch
  -> normal quota / claim / execution / evidence writeback
```

接收给管理界面一些稳定的东西来展示:主题、候选锚点、归属决策与接下来几片证明。正常 LoopX 对象仍是交付的真相源。
对于 Lark Kanban 等外部追踪器,这是任务生成路径:追踪器显示状态与认领,而接收创建稍后同步回追踪器的类型化 todo 批次。

## 接收步骤

1. **先读权威。** 在发明工作之前,检查注册表声明的 active state、status/quota 输出、已注册文档、当前 todo,以及任何显式命名的公开设计笔记。
2. **综合主题。** 把请求归约为几个主题,如产品证明、接入、基准 evidence、管理界面、合作伙伴锚点或仓库安全。
3. **创建小型 todo 批次。** 只添加最小可行集的有类型 todo,通常三到七个。每个 todo 应有优先级、角色、`task_class`、`action_kind`、验收 evidence 与停止条件。
4. **窄认领。** 当前 agent 只能认领匹配其建议配置与当前范围的项目。其他对等方的工作留在其认领者;当任务策略要求不同对等方时,使用显式认领转移或普通独立交接。
5. **把私有思考留在本地。** 如果需要原始策略、名称、截图或敏感上下文,写一个本地/私有管理笔记,并在公开文档或 active state 中只引用安全摘要。
6. **刷新下一步动作。** 写回后刷新 LoopX state,使配额、状态与管理界面能看到所选的下一片证明。

## 输出契约

接收结果应足够紧凑,可在状态卡片中评审:

```yaml
complex_request_intake_v0:
  source_refs:
    - active_state
    - registered_docs
    - user_message_summary
  theme_summary:
    - name: management_surface
      intent: make long-running agent work reviewable
    - name: proof_anchor
      intent: select high-value public evidence before broad execution
  todo_batch:
    - todo_id: todo_example
      priority: P1
      role: agent
      task_class: advancement_task
      action_kind: public_contract_design
      acceptance: "Public doc linked from product index and passes boundary scan."
      stop_condition: "Stop before runtime write paths or private material."
  claim_decisions:
    - todo_id: todo_example
      claimed_by: codex-side-bypass
      reason: "Matches productization/docs lane."
  private_note_ref: "local-only, optional"
  writeback:
    status: planned
    recommended_action: "Work the first claimed proof slice."
```

具体 schema 可以演进,但上述字段捕获了最小可评审形态:上下文来自哪里、它意味着什么、创建了哪些 todo、谁可以处理它们,以及什么 evidence 将证明进展。

## 边界

- 接收不执行计划。它只准备有界工作。
- 接收不覆盖用户 gate、仓库安全规则、worktree 策略、配额或认领所有权。
- LoopX 核心不应做脆弱的自然语言范围过滤。Agents 使用其已知范围,并把结果编码为显式 todo 元数据。
- 完成的非平凡 todo 不需要强制后继。它需要一个真实存在时的清晰下一个 todo,或一个简短的不跟进理由。
- 仅 monitor 的 Loop 不应永远运行而不产生 evidence、阻碍、规划接收或安静空操作理由。
- 私有上下文可以告知本地规划,但公开文档与已提交 state 必须只包含安全摘要。

## 管理界面含义

管理界面应把复杂接收渲染为头等评审卡片:

- 从请求提取的主题;
- 带优先级、角色与认领状态的提议 todo 批次;
- 当前 agent 认领决策对比带评审动作的普通对等方交接;
- 第一片证明的预期 evidence;
- 任何未决用户 gate;
- 仅本地管理笔记的链接,而不暴露其内容。

这让维护者可以在 agents 花费多个 Turn 前评审计划。它还支持"刷过工作"的交互:接受一片、拒绝一个范围外项、请求 evidence,或把一个主题提升为锚点。

## 验收标准

当以下条件满足时,一次好的接收是成功的:

- 大型请求不再只在聊天中;
- 结果 todo 通过 LoopX status/quota 投影可见;
- 当前 agent 只认领当前范围的工作;
- 主要或用户决策具体,而非藏在泛化 owner gate 后;
- 公开产物通过私有边界扫描;
- 下一个心跳有具体证明片或安静空操作理由。

目标是让复杂策略可管理,而不把 LoopX 变成一个自由形式的规划巨石。
