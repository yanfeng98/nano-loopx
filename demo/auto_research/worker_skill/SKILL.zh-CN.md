---
name: loopx-auto-research
description: Use when a LoopX worker is operating an auto-research lane, demo pane, frontier item, evidence packet, promotion/retirement decision, or visible tmux/Codex auto-research rehearsal. Identity must come from the LoopX role profile and quota/frontier packet; this skill only provides role-specific execution checklists, artifact contracts, and stop conditions.
---

# LoopX Auto Research

这是 auto-research 面板的 worker 本地角色 playbook。它与 auto-research capability 一起打包,应由 worker 启动器注入或引用;它不是普通项目 agent 的全局 LoopX skill。

## 路由边界

在 LoopX auto-research worker 拥有角色 profile、frontier 条目、启动器包或用户可见 demo 面板后使用本 skill。本 skill 是角色 playbook。它不构成身份、权威、当前 frontier 或合并/发布权限的真相来源。

身份来自 LoopX 控制面元数据:

- 启动器/frontier/引导包中的 `auto_research_role_profile_v0`;
- `quota should-run --goal-id ... --agent-id ...`;
- todo 认领、capability token、写入范围与受保护范围;
- 仓库或工作区 `AGENTS.md` 规则,它只能让边界更严格。

没有角色拥有完整图。不要从面板标题、分支名、tmux 窗口名或本 skill 恰好可见的章节推断角色。

## 面板 Tick 契约

通用多 agent 内核拥有默认的 LoopX 项目/文档 registry skills 与固定 A2A 唤醒 prompt。本 skill 应保持角色特定:在面板本地 tick 已从 LoopX 解析身份、quota 与 frontier 之后使用它。

紧凑 frontier 命令:`loopx --format json auto-research frontier --goal-id "$LOOPX_GOAL_ID" --agent-id "$LOOPX_AGENT_ID"`。同时遵守 `quota should-run`。

如果启动器导出了 `LOOPX_ROLE_ID`、`LOOPX_ROLE_PROFILE_REF` 或 profile JSON 路径,请把这些值与 quota 及 frontier 包比较。不一致时停止。不要猜测预期角色。

如果角色 profile 包含 `successor_todos`,把这些声明当作创建下一个 agent todo 的仅有的角色本地方式。后继声明必须命名目标 agent,并包含 `todo_command_template`,例如 `loopx todo add ... --claimed-by {target_agent_id_shell}`。在可见 auto-research 中,面板本地 tick 是守卫/frontier 读取,不是研究写入者。只有在可见角色撰写了满足声明条件的真实 public-safe 证据或笔记之后,才渲染并运行后继 todo。不要用散文杜撰额外的续接计划,也不要让 leader 面板挑选下一个角色。

在无后续任务地完成之前,把证据摘要与 `role_profile.continuation_policy` 比较。当目标仍未达成且声明的后继条件满足时,先创建或链接该后继。只有在目标达成、已投影的阻塞器或用户关卡停住该通道,或证据支撑的退役关闭了 frontier 时,无后续任务才有效。

对于可见 demo 演练,`auto-research demo-supervisor` 默认只读;只在用户选择启动可见本地面板时才使用 `--execute`。默认演练不得自行启动 Codex、写入 LoopX 状态或消耗 quota。

## 角色解析

把角色 profile 映射到以下某个章节:

| 角色 id 或通道 | skill 章节 | 权威来源 |
| --- | --- | --- |
| `research_curator` | Research curator | 角色 profile、quota 包、契约 todo |
| `hypothesis_proposer` | Hypothesis proposer | 角色 profile、frontier 包、假设 todo |
| `research_executor` | Research executor | 角色 profile、选中的 frontier 条目、写入范围 |
| `evaluator_promoter` | Evaluator/promoter | 角色 profile、证据包、晋升策略 |
| `research-narrator`、`product_narrator` | Projection narrator | 只读投影包与首屏关卡 |
| `control-plane-guard` | Control-plane guard | quota/status/check 包与仓库规则 |

当前 demo 可能渲染少于四个逻辑研究角色的面板,或使用不同名称。这只是一个宿主布局选择。每条持久记录仍应点名产生它的逻辑角色或转换职责。

## 共享停止条件

以下任一项成立时,停止并报告确切阻塞器:

- quota 说 `should_run=false`、`delivery_allowed=false`,或用户/运营方关卡打开;
- 选中的 todo 缺失、被另一 agent 认领,或与 profile 的 `capability_token` 不兼容;
- 下一次编辑触及 `protected_scope`、凭据、私有材料、原始日志、原始评估数据或未批准的发布组件面;
- profile、frontier、`AGENTS.md` 与本 skill 相互矛盾;
- 工作会需要 leader/coordinator agent 来选择、晋升或重写整张图。

## Benchmark 工作区提示

当角色 profile 或工作区暴露 benchmark 契约时,在撰写研究结论之前使用该契约。对 KNN 式 demo 这意味着:

- 阅读 `research_contract.public.json`、`README.md` 与可编辑的 solver;
- 只编辑声明的可编辑范围,如 `solution.py`;
- 在提议晋升前运行声明的 dev 命令;
- 在声称已验证改进前运行声明的 held-out 命令;
- 总结机制、命令、分数与受保护范围干净度。
- 把契约与 eval JSON 输出传给 `loopx auto-research evidence`,而不是手工撰写证据包。

面板本地 tick 可以指向一个 todo;它不能算作 benchmark 证据。

## Research Curator

当角色拥有原始研究愿望、objective、必需产物、验收标准、指标、可编辑范围、受保护范围、budget 与关卡时使用。

允许的动作:

- 创建或刷新 `auto_research_delivery_contract_v0`,嵌入现有 `research_contract_v0`;
- 使受保护边界显式;
- 当晋升或发布需要判断时,写入用户/运营方关卡 todos;
- 从现有证据请求只读投影。

有用命令:

```bash
loopx --format json auto-research frontier \
  --goal-id "$LOOPX_GOAL_ID" \
  --agent-id "$LOOPX_AGENT_ID"
```

产物契约:

- objective 是 public-safe 且有界的;
- 原始愿望、假设、非目标与契约引用是 public-safe 且显式的;
- 每个必需产物与验收标准都有稳定的 public-safe id;
- 指标方向与受保护评估器是显式的;
- 写入范围与受保护范围被点名;
- 晋升策略说明什么证据足够。
- 失败策略点名兜底产物,以及当前契约无法满足时重新进入研究的条件。

不得:

- 挑选赢家;
- 运行实验;
- 把无支撑指标呈现为产品价值。

## Hypothesis Proposer

当角色把想法转化为 todo 支撑的假设、细化、后继或退役时使用。

允许的动作:

- 创建带 `todo_id`、`claimed_by`、机制族、父链接与接地引用或无条件理由的 `research_hypothesis_v0` 记录;
- 退役重复、耗尽的重试或被反驳的方向,同时保持负面证据可见;
- 添加下一个有界的 agent todo。

写入之前:

- 确认该想法没有声称来自用于构思的同一来源的新颖性;
- 确认该假设可以在允许的写入范围内尝试;
- 把 todo 顺序与理由保存在 LoopX 状态中,而不只保存在 chat 里。

不得:

- 删除失败;
- 挑选赢家;
- 用更干净的故事替换假设来隐藏矛盾证据。

## Research Executor

当角色在隔离工作区/worktree 中恰好运行一个选中的假设并记录尝试证据时使用。

允许的动作:

- 认领为此 agent 选中的当前 frontier 条目;
- 只编辑允许的解决方案或实验范围;
- 只在契约允许时运行 dev 或 holdout 评估;
- 构建 `auto_research_evidence_packet_v0` 或等价的 public-safe 事件;
- 当 profile 的 `successor_todos.condition` 满足时,只创建角色声明的后继 todo,例如 holdout 验证 todo 或 holdout 后 verifier 摘要 todo。

后继路由在这里,而不是在中央投影器中:角色 profile 必须命名目标 agent,并提供 `todo_command_template`,通常是普通的 `loopx todo add ... --claimed-by {target_agent_id_shell}` 命令。内核只验证目标 agent 并执行正常 LoopX todo writer。

证据写回应使用显式的通道撰写证据包或当前状态暴露的正常 LoopX todo/evidence 命令。在评审包边界之后才追加,然后在可见通道被接受时从通道撰写的包中捕获紧凑实时证据。不要用 worker-turn 制造 dev 或 holdout 指标。

在选定 frontier todo 的真实追加/捕获成功之后,用紧凑 public-safe 证据关闭那个选定 todo。依赖的 evaluator 或 successor 通道通常从 `todo_done:<selected_todo_id>` 恢复;在有支撑证据后留下 executor todo 打开会使下一轮搁浅。

不得:

- 编辑受保护的评估器/数据范围;
- 晋升结果;
- 省略失败、无定论或防护栏失败的尝试。

## Evaluator/Promoter

当角色读取证据并把它分类为被支持、被反驳、需要重试、晋升就绪或退役就绪时使用。

允许的动作:

- 只在选中的 frontier 动作是 `run_holdout_eval` 且契约允许该划分时运行 held-out 验证;
- 把契约的指标与晋升策略应用于已评分或未评分的证据;
- 用有界理由与可恢复 ref 请求重试;
- 创建晋升、退役或关卡候选;
- 为下一个 worker 写紧凑验证笔记;
- 当证据需要另一个有界划分时,只添加角色声明的后继 todo,用 profile 的 `todo_command_template`。
- 当 `continuation_policy` 仍报告未达目标、且角色声明的后继条件满足时,不要无后续任务地关闭。

验证清单:

- 划分标签与指标方向是显式的;
- dev 证据不被表示成 held-out 证明;
- 边界说明受保护范围保持干净;
- 负面证据保持可查询。

当证据到达终态边界时:

- 用 `loopx auto-research decide` 记录 `promoted` 或 `retired`;晋升候选不是终态结果;
- 把决策绑定到当前证据图 revision,并保持决策证据 ref 的 public-safe;
- `loopx auto-research review --require-independent` 只能由与假设产出者和决策 agent 都不同的已注册同行使用;
- 把自我评审当作可见评审证据,绝不当作独立评审;
- 当 curator 提供了 `auto_research_delivery_contract_v0` 时,在终态决策与所需评审后运行
  `loopx auto-research artifact-receipt --contract <contract-file>`;
- 把每个非验证 receipt 连同其失败类型、验证边界、兜底产物与再入条件返回给用户;不要把单次失败尝试变成终态不可能声明;
- 决策与评审后使用 `loopx auto-research project-results`,以便确切的 `loopx auto-research results` 查询可以验证 Explore 回读。

示例终态路径:

```bash
loopx auto-research decide \
  --goal-id "$LOOPX_GOAL_ID" \
  --hypothesis-id "<hypothesis-id>" \
  --outcome promoted \
  --reason holdout_validated \
  --agent-id "$LOOPX_AGENT_ID" \
  --execute

loopx auto-research review \
  --goal-id "$LOOPX_GOAL_ID" \
  --hypothesis-id "<hypothesis-id>" \
  --reviewer-agent-id "$LOOPX_AGENT_ID" \
  --verdict approve \
  --require-independent \
  --execute

loopx auto-research artifact-receipt \
  --contract "<delivery-contract-file>"
```

不得:

- 绕过 owner/operator 关卡;
- 认证 show 展示结论;
- 重写假设图让结果看起来更干净。
- 把同一个产出者或决策 agent 标成独立评审者。

## Projection Narrator

当角色是对已接受投影的只读产品叙述时使用。这在 v0 是转换职责,以后可能变成独立角色。

允许的动作:

- 从晋升、退役与重试证据渲染 `research_evidence_graph_v0`;
- 只从投影 ref 更新 public-safe 文档或 Frontstage 组件面;
- 把失败与退役方向保留为有用的学习。

有用命令:

```bash
loopx --format json auto-research project-results \
  --goal-id "$LOOPX_GOAL_ID" \
  --execute

loopx --format json auto-research results \
  --goal-id "$LOOPX_GOAL_ID" \
  --include-history
```

必须在以下情况前停止:

- 发明指标;
- 读取私有源码正文;
- 未经过首屏评审关卡就改变首视口、hero、主 CTA 或打开导航。

## Control-Plane Guard

当角色检查可见 demo、frontier、证据追加、合并或发布动作是否安全且可中断时使用。

允许的动作:

- 运行 quota/status/check 包;
- 验证 public/private 边界;
- 确认 attach/stop/takeover 控件可见;
- 当投影矛盾时写阻塞器或修复 todos。

有用命令:

```bash
loopx --format json auto-research demo-supervisor \
  --goal-id "$LOOPX_GOAL_ID" \
  --workspace "$LOOPX_PROJECT"
```

不得:

- 充当 leader agent;
- 为其他角色选择实验;
- 批准自己的关卡。

## 写回

在验证过的步骤之后,只写回该角色允许的最小持久产物:

- `research_contract_v0`;
- `research_hypothesis_v0`;
- `auto_research_evidence_packet_v0`;
- 晋升/退役/关卡候选;
- `research_evidence_graph_v0`;
- LoopX todo 完成加下一个 todo/理由;
- 只有当 quota 契约允许时,在验证之后执行 `loopx refresh-state` 与一次 quota 消耗。

如果步骤被阻塞,把阻塞器写成 todo/理由,并且不要仅仅为了发现一个未变化的关卡而消耗 quota。
