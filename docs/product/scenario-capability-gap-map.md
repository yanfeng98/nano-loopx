# 场景能力差距图


状态:产品引导笔记。

本笔记比较三个场景族所需的底层 LoopX 能力:

- 仓库 issue-fix Loop,包括 OpenViking/Viking 风格的 issue 分诊与补丁交付;
- 创作者或自媒体运营 Loop;
- 仓库中已存在的其他场景信号,如基准 runner、ML 实验建议与 host 集成。

它刻意不是把这些领域烘焙进核心运行时的计划。核心应保持 goal state、todo、gate、evidence、配额、校验与交接通用。场景特定行为应在注册表或 owner 记录边界后,作为显式适配器或领域包到来。

## 共同基质

三个场景族在领域逻辑有用之前,都需要相同的控制面基质:

| 能力 | 为何重要 |
| --- | --- |
| `connector_observation_v0` | 从外部源拉取紧凑事实,而不把原始/私有材料复制进 LoopX state。 |
| `source_status_v0` | 把每个事实标记为公开、私有、合成、未发布、需评审或禁止用于公开界面。 |
| `artifact_handle_v0` | 把 issue、PR、CI 运行、草稿、文章、基准任务或指标板追踪为带允许轮询动作的可观察句柄。 |
| `todo_lifecycle_v0` | 把场景转化为具体的用户与 agent todo,含 `todo_id`、owner、校验与后继工作。 |
| `capability_gate_v0` | 说明 agent 执行 todo 前需要哪些工具或领域包。 |
| `validation_surface_map_v0` | 要求每一步命名如何检查成功:测试、CI、评审、来源归因、打分或阻碍写回。 |
| `handoff_packet_v0` | 为人类或另一个合格对等方打包当前状态、evidence、风险与下一个安全动作。 |
| `feedback_writeback_v0` | 把用户奖励、纠正、风格反馈或评审评论转化为持久 state,而非仅聊天记忆。 |
| `publish_boundary_v0` | 在显式 gate 允许前,停止公开发布、平台发布、排行榜提交或生产动作。 |

当前 LoopX 架构已有该基质的碎片:注册表条目、active goal state、todo 生命周期、配额、状态、评审包、公开/私有扫描与 host 集成契约。差距在于 connector、source 状态、校验映射与反馈写回对这些场景来说尚未成为足够头等能力。

## 增量 State 界面

LoopX 不应为每个高频场景创建一个产品孤岛。更好的形态是增量 state 界面:一个叠加在通用 goal/todo/gate/evidence 模型之上的小型面向领域投影。

当场景有重复的用户语言与重复决策,但尚不足以说明需要自定义前端或自主领域包时,增量 state 界面有用。它应包括:

- 一个紧凑外部句柄,如 issue、帖子、草稿、实验、CI 运行或指标板;
- 来源状态与新鲜度;
- 用户或 owner 路由目标;
- 允许的下一步动作与停止条件;
- 校验界面;
- 提升目标:正常 LoopX 用户 todo、agent todo、gate、锚点或评审事件。

MVP UI 可以是 host 已有的任何东西:GitHub 标签、issue 评论、Lark 消息、CLI 评审包或静态 dashboard 卡片。自定义前端只有在 state 界面证明该场景值得保留之后才值得。

## 仓库 Issue-Fix Loop

Issue-fix Loop 把报告的问题转化为经评审的补丁或阻碍。高价值路径不只是"agent 写代码";它是受控接收、复现、补丁选择、校验、评审与安全发布。

| 阶段 | LoopX 对象 | 需要的能力增量 |
| --- | --- | --- |
| Issue 接收 | artifact handle + source status | 表示 issue URL/id、报告者上下文、公开/私有边界、新鲜度,以及原始 issue 文本是否可读或可引用。 |
| 分诊 | agent todo + validation map | 分类为 bug、文档缺口、功能请求、不稳定测试、依赖断裂或复现不足;命名首个安全校验。 |
| 复现计划 | result event + blocker lane | 记录精确的可复现状态,而不存储原始日志或私有痕迹。 |
| 补丁规划 | handoff packet | 把候选界面与原始 diff 分开;保持补丁归属与写入范围可见。 |
| 实现 | claimed todo + worktree guard | 为写仓库的对等方要求任务/仓库工作区隔离、不相交写入范围与评审前本地校验。 |
| 校验 | validation surface map | 在标记进展前把测试、lint、CI、fixture smoke 或人工复现与 todo 绑定。 |
| 独立评审 | successor handoff todo | 在普通独立交接上使用 `action_kind=review`;仅当作者不得回收时才添加执行者排除。 |
| 发布 | publish boundary | 区分本地 commit/PR 与包发布、生产部署或外部提交。 |
| 反馈 | feedback writeback | 把评审评论、失败 CI 或维护者纠正转化为后继 todo 与 evidence 更新。 |

对于 OpenViking/Viking 风格的 issue-fix 案例,首个有用适配器应是读为主的:

1. 把公开 issue 与仓库元数据摄取为紧凑句柄;
2. 把 issue-fix 阶段投影为 LoopX todo;
3. 读取源文件或生成补丁前要求执行 gate;
4. 写出脱敏的校验与评审交接包;
5. 在发布、部署或受保护分支动作前停止。

这类似现有 AgentIssue-Bench 包,但应面向产品而非基准。基准路由证明源与补丁边界;产品路由必须添加面向维护者的状态、评审交接与安全延续语义。

### Issue Meta 界面 MVP

上层应把 issue 记录为管理信号,然后才成为 agent 工作。这让 v0 产品保持简单:GitHub 标签与评论可以是可见 UI,而 LoopX 拥有紧凑 state 投影。

`issue_meta_surface_v0` 应是轻量记录:

| 字段 | 含义 |
| --- | --- |
| `issue_handle` | 公开安全的仓库加 issue 或 PR 标识,而非原始正文文本。 |
| `source_status` | 公开/私有/合成/需评审标签与新鲜度。 |
| `label_set` | 用作 MVP 显示与路由层的 GitHub 标签或 host 标签。 |
| `related_code_hint` | 可选紧凑路径/模块/包提示;绝不是原始 diff 或私有路径。 |
| `owner_route` | 应看到该 issue 的维护者、频道或显式选择的已注册对等方。 |
| `allowed_action` | 观察、询问 owner、复现、起草计划、准备补丁或交接。 |
| `validation_surface` | 测试、CI、复现器、维护者确认或阻碍 evidence。 |
| `promotion_target` | Agent todo、用户 todo、评审事件、锚点候选或归档。 |

该界面不应要求前端。首个有用实现可以是读取所选 GitHub 标签、创建紧凑 issue-meta 记录,并仅在显式路由决策后才写入正常 LoopX todo 的 CLI 或 host 适配器。后续前端可以按标签或状态渲染相同记录。

P0 issue-meta 验收:

- 一个 issue 可以不复制原始 issue 正文或原始 diff 表示;
- 相关代码提示可以存储为紧凑、可评审的提示;
- 路由足够显式,避免"有人应该找到 owner";
- 选中的 issue 可以提升为带校验与停止条件的具体 agent todo;
- 未选中的 issue 保持为信号,而非积压杂乱。

### Issue-Fix 差距

P0 差距:

- `issue_intake_packet_v0`:紧凑 issue 句柄、来源状态、仓库锚点、权限边界与首个校验界面。
- `repro_validation_map_v0`:结构化复现状态、测试目标、受阻原因与下一个所需 evidence。
- `patch_handoff_packet_v0`:候选变更范围、已完成校验、残余风险与交接 owner 条件。

P1 差距:

- 超出软 `claimed_by` 与独立 opt-in `task-lease` CLI 的 host 集成 worktree 租约执行;
- 通过薄 host 适配器或 MCP 门面为 GitHub 风格 issue/PR/CI 界面提供 connector 支持;
- 用非 CLI 行话解释"可打补丁"、"等待复现"、"等待评审"与"有可用安全旁线工作"的 frontstage 卡片。

非目标:

- 暂时不要创建独立的核心 LoopX issue 对象;
- 不要在公开文档或紧凑状态中存储原始 issue 正文、原始 diff、测试正文、日志或私有仓库内容;
- 不要在没有现有边界 gate 的情况下 autopush、部署或发布。

## 创作者与自媒体运营 Loop

创作者运营路径已有公开安全的案例规范与反馈契约。其瓶颈较少在于补丁正确性,更多在于来源归因、用户品味、无自动发布 gate 与有用的起草队列。

| 阶段 | LoopX 对象 | 需要的能力增量 |
| --- | --- | --- |
| Connector 摄取 | connector observation + source status | 区分公开平台摘要、私有聊天/材料、合成演示数据与需评审来源。 |
| 信息与热点排序 | reward-style hint + validation map | 按相关性与 evidence 质量排序候选,而不声称趋势或性能提升。 |
| 洞察提取 | result event | 保留来源归因,以及该项目值得据此创作的原因。 |
| 草稿创建 | agent todo + draft queue | 分开大纲、草稿、重写、来源映射与发布 gate 状态。 |
| 打分与反馈 | feedback writeback | 把"有用"、"不是我风格"、"太营销"或"不要用这个来源"转化为持久偏好、todo 或边界纠正。 |
| 重写 Loop | successor todo | 保持修订工作可执行,同时发布仍受 gate 约束。 |
| 发布决策 | user gate | 无自动发布;外部发布前需要显式的语气/来源/策略批准。 |

浏览器路由公共信息源或本地聊天 connector 处理私有微信式历史等 connector 示例应保持适配器所有。LoopX 只存储紧凑来源标签、evidence 摘要、gate、反馈与下一步动作。

### Content-Ops State 界面 MVP

创作者路径需要 state 界面先于发布器。该界面应让工作队列有用,同时保持发布受 gate 约束且来源边界可见。

`content_ops_surface_v0` 应包括这些记录:

| 记录 | 用途 |
| --- | --- |
| `source_item_v0` | 来自平台、聊天、文档或合成演示源的紧凑观察,含来源状态、新鲜度、条款说明与允许的引用/使用策略。 |
| `angle_candidate_v0` | 该来源可能对该创作者重要的原因:受众、主题、新颖性、用户偏好契合度、evidence 质量,以及忽略时的拒绝原因。 |
| `draft_item_v0` | 大纲/草稿/重写/来源映射状态,链接到来源项与显式用户偏好提示。 |
| `feedback_signal_v0` | 有用/没用、风格纠正、来源拒绝、发布批准/否决或偏好笔记。 |
| `publish_gate_v0` | 外部发布的人工批准记录;不因草稿存在而自动发布。 |
| `material_memory_v0` | 带归因、被拒角度与复用边界的持久来源安全资料库条目。 |

首个公开安全实现现在由
`loopx/capabilities/content_ops/surface.py`、`docs/reference/protocols/content-ops-surface-v0.md`
与 `examples/content-ops-surface-fixture-smoke.py` 锚定。这让 MVP 保持为 state 界面契约:来源/草稿/反馈/gate 事实可以提升为正常 LoopX todo,但投影本身是只读的,没有发布权威。

state 流应刻意保持平淡:

```text
connector observation
  -> source_item_v0
  -> angle_candidate_v0
  -> user/agent todo for draft or rejection
  -> draft_item_v0
  -> feedback_signal_v0
  -> rewrite todo or publish_gate_v0
  -> optional material_memory_v0
```

它在三方面区别于普通内容流水线:

- 工作单元不是"多发帖子";而是"选择、证明、草拟、评审并学习";
- 成功信号是被接受的信号或被接受的草稿质量,而非原始文章数;
- 反馈改变持久偏好与来源边界,而不只是改进当前草稿。

P0 content-ops 验收:

- 每个项目在成为草稿前都有来源状态与新鲜度;
- 草稿携带来源映射与发布 gate;
- 用户反馈写入以下其一:偏好提示、来源边界纠正、重写 todo 或发布决策;
- 运维者可以看到"等待来源评审"、"可起草"、"等待反馈"、"可进入发布决策"与"有可用安全旁线工作";
- 没有 connector、浏览器或聊天适配器把原始私有材料写入公开 LoopX state。
- 在 connector 或前端将该界面视为稳定之前,公开 fixture 与投影 smoke 通过。

### Creator-Ops 差距

P0 差距:

- `source_status_v0` 作为洞察、草稿与资料库条目的可复用字段;
- 把风格反馈、奖励、todo 更新与边界纠正映射为显式 state 的 `feedback_writeback_v0`;
- 在首屏运维者模型中渲染的无自动发布 gate。

P1 差距:

- connector 新鲜度与使用条款元数据;
- 带归因、被拒角度与来源状态的资料库 schema;
- 面向前端与评审包的草稿队列投影。

## 其他仓库场景信号

仓库已记录了一些应指导通用基质的场景类别:

| 场景信号 | 现有界面 | 能力教训 |
| --- | --- | --- |
| 长程基准 | `benchmark/` 与基准研究 RFC | 保持基准原生执行在 LoopX 核心之外,同时复用狭窄的工具包边界。 |
| ML 实验建议 | `docs/product/domain-capability-packs.md` | 领域包应默认关闭,并对自主性、主要指标与启动权威显式。 |
| Host 集成 | `docs/reference/protocols/host-integration-surface-v0.md` | Hooks、MCP 与 loopback API 必须保持为 CLI 等价生命周期读写之上的薄门面。 |
| 非技术运维者 UI | `docs/product/surfaces/nontechnical-operator-status-model.md` | 首屏文案需要普通语言的 state、阻碍、用户动作、校验与反馈路径。 |
| 创作者运营 showcase | `docs/showcases/cases/0620-creator-operator-case-spec.md` | 公开演示需要合成数据、来源状态规则与可见反馈效果。 |

这些不应成为独立控制面。它们应施压同一组 LoopX 原语,直到原语足够强以支持多个领域。

### 仓库场景清单

README 与产品文档已经命名了比前两个示例更多的场景压力。有用的产品动作是排序每个场景需要的基质,而不是每个场景启动一个适配器。

| 排名 | 场景信号 | 仓库中的 evidence | 首建底层增量 |
| --- | --- | --- | --- |
| P0 | 维护者管理与多 agent 车道 | `docs/product/surfaces/intelligent-management-surface.md`、`docs/product/surfaces/nontechnical-operator-status-model.md` | `signal_v0`、`anchor_v0`、`management_projection_v0` 与车道级 `performance_review_v0`,以便维护者在更多自动化被信任前评审价值、质量、成本与注意力。 |
| P0 | 仓库 issue-fix 与 PR 驱动增长 | `docs/product/surfaces/intelligent-management-surface.md`、`docs/project-agent-todo-contract.md` | `issue_meta_surface_v0`、`issue_intake_packet_v0` 与 `patch_handoff_packet_v0`,以便 issue 信号保持可见而不成为原始积压或不安全补丁权威。 |
| P0 | 创作者与自媒体运营 | `README.md`、`README.md`、`docs/product/vision.md` | `content_ops_surface_v0`、来源感知的草稿队列与持久 `feedback_signal_v0`,以便来源边界、品味反馈与无自动发布 gate 跨 Turn 存活。 |
| P0 | 基准研究工作流 | `benchmark/`、基准研究 RFC | 匹配臂、原生 runner/verifier 归属、紧凑凭据与工具包边界检查,而不内置 LoopX runner。 |
| P1 | Codex CLI TUI 接入与延续 | `README.md`、`docs/product/runtimes/codex-cli/codex-cli-tui-loop.md`、`docs/product/runtimes/codex-cli/codex-cli-automation-driver.md` | `host_session_handle_v0`、可见会话证明、空闲/回退状态与提示升级检测,使单消息引导与同 TUI 延续清晰可恢复。 |
| P1 | ML 实验建议 | `docs/product/domain-capability-packs.md`、`docs/product/roadmaps/experiment-controller-milestone.md` | `domain_pack_detection_v0`、`domain_pack_contract_v0` 与建议性 `ml_experiment_result_v0`,以便识别实验形态的 goal 而不悄然启用启动或路由决策。 |
| P1 | Host 集成与本地 dashboard API | `docs/reference/protocols/host-integration-surface-v0.md`、`docs/integration.md` | `host_integration_surface_v0` 加 CLI 等价 dry-run/写回契约,使浏览器、MCP 与 loopback 界面保持门面而非新权威。 |
| P1 | 研究与材料注册表 Loop | `docs/operations/authority-source-registration.md`、`docs/research/` | `authority_source_v0`、紧凑来源契约与新鲜度检查,使持久材料在不复制来源正文或私有链接的情况下指导路由。 |
| P2 | 公开 frontstage/showcase 采用 | `docs/product/surfaces/frontstage-two-surface-strategy.md`、`docs/showcases/README.md` | `showcase_case_v0` 与公开安全合成 fixture,使演示在不泄漏实时控制 state 或把 showcase UI 变成控制权威的情况下解释 LoopX。 |
| P2 | Office 运营与合作伙伴 connector | `docs/product/surfaces/intelligent-management-surface.md` | 通用 `connector_observation_v0`、`signal_v0` 与评审流卡片,使合作伙伴工具在 LoopX 拥有任何领域执行器之前发送紧凑工作信号。 |

排名说明哪个基质应首先成为可复用:

1. **P0:信号到锚点流水线。** 管理界面、issue Loop 与创作者 Loop 都需要带来源状态、新鲜度、建议效果与显式提升到 todo、gate、评审事件或锚点的 `signal_v0`。
2. **P0:紧凑产物句柄与校验界面。** Issue 复现、基准运行、Codex 会话、实验任务与内容草稿都需要带允许轮询/读取动作、校验状态与无原始材料 evidence 规则的可观察句柄。
3. **P0:反馈写回作为类型化 state。** 评审流评分、用户风格反馈、维护者纠正与基准路由判断必须成为 `feedback_signal_v0`、reward 叠加、todo 更新、边界纠正或绩效评审笔记。
4. **P1:无权限升级的领域包检测。** ML 实验、办公运营、issue solver 与内容 connector 可以被检测为场景形态,但只有注册表或 owner 边界记录才能启用建议或交付自主性。
5. **P1:host 门面纪律。** 浏览器、MCP、dashboard、Codex CLI、基准 host 与 connector 界面应暴露与 CLI 相同的 dry-run、校验、写回与停止条件生命周期。
6. **P2:场景特定前端与适配器。** 只有在紧凑 state 界面在普通 LoopX 状态与评审包中被证明有用后,才构建自定义卡片、发布器队列、实验面板或 issue dashboard。

## 优先级栈

P0:让 issue-fix Loop 产品原生。

1. 定义 `issue_intake_packet_v0`、`repro_validation_map_v0` 与 `patch_handoff_packet_v0`。
2. 把 `issue_meta_surface_v0` 定义为 GitHub 标签、owner 路由、相关代码提示与 todo 提升之上的管理层。
3. 添加仅使用紧凑公开元数据的公开安全 issue-fix fixture。
4. 在不读取原始源文件或生成补丁的情况下,把 issue-fix fixture 投影为 todo 与评审交接。

P0:让 creator-ops 反馈持久。

5. 在来源项、角度候选、草稿、反馈信号、发布 gate 与材料记忆之上定义 `content_ops_surface_v0`,附公开安全 fixture/投影辅助函数与 smoke。
6. 把 `source_status_v0` 与 `feedback_writeback_v0` 提升为可复用产品契约。
7. 在状态与前端演示数据中保持无自动发布 gate 可见。

P1:扫描并排序剩余场景信号。

8. 完成跨维护者管理、issue-fix、创作者运营、基准、Codex CLI、ML 实验、host 集成、研究材料、frontstage 与合作伙伴 connector 的首次仓库场景清单。
9. 从该扫描提升可复用 P0 基质:信号到锚点、产物句柄/校验与反馈写回契约。
10. 在注册表边界显式启用之前,避免添加领域包。

## 验收标准

当场景能力图让维护者能回答以下问题时,它就是有用的:

- 哪些外部事实是紧凑句柄,哪些是原始材料;
- 哪个工作项可由 agent 执行,哪个是用户 gate;
- 什么校验能证明进展;
- 任务策略在哪里要求在延续前进行显式对等方评审;
- 在 gate 等待期间什么可以安全继续;
- 什么绝不能发布或作为公开 evidence 对待。

当这些答案在 LoopX state 中可见时,场景就准备好接受薄适配器或演示。当它们只在散文或聊天中时,下一个产品步骤是先添加缺失的控制面能力。
