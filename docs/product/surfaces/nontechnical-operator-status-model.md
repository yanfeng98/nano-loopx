# 非技术 Operator 状态模型


本说明为正在运营长程 agent goal 但不想检查 prompt、日志、CLI 输出或原始轨迹的人定义首屏状态模型。

该模型刻意面向产品。它把 LoopX 状态翻译成通俗语言卡片：

- 自上次检查以来发生了什么变化；
- agent 现在在做什么；
- 进展在哪里被阻塞；
- agent 接下来计划什么；
- agent 需要用户提供什么；
- 用户反馈如何改变控制面。

同一模型应适用于工程、benchmark、研究与创作者-operator 案例。文案可以随领域变化，但控制面对象保持相同：goal、gate、todo、evidence、safe side path、run 历史、quota 与 feedback。

第一个真实目标用户是 Loop Agents 的 maintainer/operator。那个人不只问"agent 做了什么？"而是问：

- 哪些外部信号值得关注；
- 哪些信号应成为高价值锚点；
- 哪条 agent 泳道拥有下一步；
- agent 是变得更有用还是仅仅更忙；
- 哪里的人类判断应当改变 loop。

## 采用模式

Status surface 应支持两种采用模式。

### 只读评审模式

只读模式下，用户可以连接既有 agent 工作，而不采用 LoopX 控制 loop。Surface 摄取公开或经同意的 artifacts，如 issues、pull requests、文档、run 摘要、紧凑日志或手动录入的反馈。然后显示可评审摘要并捕获人类评分。

该模式不应改动 agent 的计划。其产品价值是度量：maintainer 可以看到 agent 是否创造了有用工作、是否尊重边界、是否负责任地消耗注意力，以及是否随时间改进。

### LoopX 写回模式

写回模式下，同一份反馈变成控制面输入。评分与评论可以变成 gates、todo 变更、选中锚点、reward 说明、scope 纠正或下一个改进目标。重要契约是：显示 surface 不悄悄把品味或模糊反馈变成硬策略。它必须显示将要写回什么以及为什么。

这个两步采用路径让产品容易尝试，同时保留更大的 LoopX 承诺：先评审，再受控改进。

## Agent 工作 Feed

默认交互应像评审一叠 agent 工作卡，而不是操作后端控制台。用户应当可以快速"浏览"近期输出并给出低摩擦反馈，同时保持每张卡片可审计。

工作卡表示一个被评审的输出，而不是原始 todo：

- `Output`：agent 产出了什么。
- `Why now`（为什么现在）：为什么这值得关注而不是留在历史里。
- `Evidence`（证据）：artifact、验证、来源边界或 blocker。
- `Cost`（成本）：可得时的 token/quota 成本与用户注意力成本。
- `Next proposal`（下一提案）：继续、停止、验证、晋升或询问。
- `Feedback`（反馈）：写入评审状态的结构化按钮。

Feed 应优先管理价值：

- 未解决的人类 gates；
- 高价值但不确定的输出；
- 昂贵的重复工作模式；
- 晋升前的 evidence 缺口；
- 可能成为锚点、showcase 或 public-safe 示例的卡片。

Feed 必须保持可检查。卡片在首屏可以轻量，但用户应能打开其背后的 evidence、PR、run 摘要、边界说明或评审历史。否则 surface 会变得漂亮但不可信。

## 设计原则

1. **从用户意义开始，而不是 runtime 内部。** 首屏应说"等待你的发布决策"，然后才说 `operator_gate`。
2. **把阻塞与进行中的工作分开。** 一个 user gate 可以阻塞一条路线，而安全侧路工作继续。Surface 应同时展示两个事实。
3. **让 evidence 可检查但不原始。** 显示紧凑 evidence、验证与来源边界；把轨迹、凭据、私有笔记、原始 benchmark 日志与私有创作资料挡在卡片外。
4. **把反馈当作结构化转变。** 用户反馈应变成 gate 决策、偏好提示、todo 变更或产品改进说明，而不是无追踪的聊天记忆。
5. **评审表现，而不只是状态。** Loop Agent 应显示它在哪里创造价值、在哪里失分、什么反馈改变过，以及它接下来应当改进什么。
6. **让反馈廉价但结构化。** 用户应能在不先读长 run 报告的情况下关闭、批准、纠正、晋升或 gate 一张工作卡。
7. **青睐一个下一动作。** 首屏可以链接到待办，但它应命名下一个将要发生的具体事情，或需要人类回答的确切问题。

## 卡片集

### 工作 Feed

用途：让用户快速评审近期 agent 输出，并把模糊判断变成结构化反馈。

建议字段：

- `Card type`（卡片类型）：progress、blocker、proposal、evidence、anchor 候选、showcase 候选或边界警告。
- `Summary`（摘要）：一两句话说明 agent 产出了什么。
- `Proof`（证明）：紧凑 evidence 与验证状态。
- `Cost`（成本）：已知时含 token/quota 成本、耗时与注意力成本。
- `Suggested action`（建议动作）：继续、验证、晋升、推迟、停止或询问。
- `Feedback actions`（反馈动作）：有用、没用、方向错误、evidence 缺失、晋升为锚点、私有/有风险。

Feed 是主要评审 surface。其他卡片可以作为卡片详情或过滤器出现，但首屏应帮助用户快速清掉最高价值的评审条目。

### Goal Snapshot

用途：提醒用户长程 goal 是什么，以及当前工作为何重要。

建议字段：

- `Goal`（目标）：来自 registry 或活跃状态的一句话。
- `Mode`（模式）：delivery、safe side path、规划提案、等待用户或暂停。
- `Owner`（所有者）：注册 peer 或用户。
- `Freshness`（新鲜度）：最新有意义更新时间与状态是否新鲜。

通俗语言示例：

- "让 benchmark 评估泳道前进，同时一个 user gate 等待。"
- "只用合成数据准备一个 creator-operator showcase。"
- "等待你的决策再发布；安全的文档工作仍在推进。"

### 自上次检查后

用途：在用户不得不读历史之前回答"发生了什么变化？"

建议字段：

- `Latest outcome`（最新结果）：已交付、部分进展、记录 blocker、no-op 或规划提案。
- `Evidence`（证据）：紧凑验证或 artifact 摘要。
- `Confidence`（置信度）：高、中、低或阻塞。
- `Boundary`（边界）：public-safe、私有、需要批准或仅限内部。

该卡片绝不应从 surface 性变更声称结果进展。如果 Turn 只准备了契约或文档，就直说，并指向下一个承载结果的步骤。

### 信号收件箱

用途：显示哪些外部信号进入了 loop，以及是否有任何值得变成工作的。

建议字段：

- `Signal`（信号）：issue、PR、评审评论、失败的检查、聊天反馈、文档变更、benchmark 结果或用户说明。
- `Source`（来源）：公开 artifact、私有来源、连接器或手动录入。
- `Fit`（契合度）：忽略、监控、候选锚点、询问 owner 或创建 todo。
- `Boundary`（边界）：public-safe、私有、需要 owner 评审或不可用。

该卡片默认安静。它应避免把每个信号变成工作。Maintainer 应看到少数可能改变优先级的信号。

### 锚点选择

用途：识别值得推动的少数高价值锚点。

建议字段：

- `Anchor`（锚点）：公开 issue、PR、失败的检查、过期的评审、用户请求、showcase 候选或内部管理问题。
- `Why this matters`（为何重要）：可信痛点、重复工作流、公开 evidence 或战略价值。
- `Allowed action`（允许动作）：观察、路由 owner、诊断、开 PR、写提案或询问人类。
- `Owner split`（所有者划分）：LoopX maintainer、collaborator、仓库 maintainer 或 adapter。
- `Exit`（出口）：已接受、已拒绝、已合并、被阻塞、不安全或 showcase 候选。

对开源 issue / PR 试点而言，该卡片是增长与控制之间的桥。LoopX 不需要实现每个 solver；它需要选好锚点并保持 evidence 可评审。

### 当前工作

用途：显示活跃 agent 现在实际在做什么。

建议字段：

- `Todo`：选中的 todo 标题，缩短。
- `Claim`：已认领 agent 与角色。
- `Scope`（范围）：人类可读的泳道，如 benchmark、产品化文档、runtime 契约或 showcase。
- `Stop condition`（停止条件）：让 agent 停下来询问的条件。

对写仓库任务，该卡片还应显示选中的 workspace 策略、仓库策略是否允许自合入，以及是否存在显式 peer 评审交接。

### Blocker 或 Gate

用途：让人为决策可见，同时不暗示 agent 无能为力。

建议字段：

- `Question`（问题）：确切的用户或 controller 决策。
- `Blocked route`（被阻塞路线）：必须等待的工作。
- `Safe side path`（安全侧路）：独立工作是否可以继续。
- `Repeat policy`（重复策略）：是否应提醒用户直到解决。

通俗语言文案应把"被 gate 的路线在等待"与"整个 goal 停止"分开。例如：

```text
在发布案例稿之前需要你的决策。
安全侧路：继续打磨公开文档与合成 demo。
```

### 下一个 Agent 动作

用途：回答"如果我什么都不做，会发生什么？"

建议字段：

- `Next action`（下一动作）：来自 quota/status 的一个有界动作。
- `Validation`（验证）：工作后期望的 smoke、检查、评审或 artifact。
- `Quota`：足以说是否允许再一次自动 Turn。
- `Fallback`（回退）：验证失败或出现 blocker 时会发生什么。

对非技术用户，quota 默认不应显示为原始内部计数器。使用通俗文案，如"允许再一次自动 Turn"或"等待下一次调度检查"。

### 我需要你做什么

用途：把用户注意力转成简短、具体的动作。

建议字段：

- `Decision`（决策）：批准、拒绝、推迟、选择选项、提供缺失上下文或无动作。
- `Why now`（为何现在）：答案解锁了什么。
- `Safe default`（安全默认值）：用户不回答时什么将继续。
- `Deadline`（截止）：只有项目有真实截止时才显示。

如果没有打开的 user todo，该卡片应显示"无需动作"并视觉安静。它不应为了保持 UI 忙碌而杜撰问题。

### 反馈捕获

用途：让用户不直接编辑控制面就能转向。

反馈选项应映射到结构化写回：

| 用户输入 | 控制面效果 |
| --- | --- |
| "批准这条路线。" | 带 scope 与 evidence 引用的 gate 决策。 |
| "不要再这样做。" | 偏好提示加可能 todo 变更。 |
| "这个有用。" | 带紧凑理由的 run 绑定 reward。 |
| "摘要不清楚。" | 产品改进说明或 status 文案 todo。 |
| "转向另一条泳道。" | Replan 提案或优先级/todo 更新。 |
| "这包含私有资料。" | 边界纠正与停止/升级。 |

Surface 应避免把推断的品味变成硬策略。显式反馈可以塑形 replanning，但私有聊天不应变成公开 evidence，软偏好应保持与安全、权限或合规 gates 可区分。

### 表现评审

用途：帮助 maintainer 判断 Loop Agent 是否在改进。

建议字段：

- `Value`（价值）：创造了什么有用 artifact 或决策。
- `Quality`（质量）：已接受、已纠正、已拒绝、被阻塞或需要评审。
- `Control`（控制）：gates、scope 与边界是否被尊重。
- `Cost`（成本）：相对于价值消耗的 quota 或注意力。
- `Learning`（学习）：下次应改变什么。

这是模糊人类反馈变成持久物的主要方式，而不假装它是 benchmark 分数。评审可以保持轻量，但它必须绑定 evidence 与下一个改进目标。

### 项目级 Reward

单任务 benchmark 可以度量 agent 是否解决了一个任务。它们不能完整度量一个长程 agent 是否在复杂项目上创造了有用价值。因此管理 surface 应暴露项目级 reward 模型：

```text
reward = f(quantity, quality, token cost, user attention cost)
```

字段有不同来源：

- `Quantity`（数量）：完成的任务、已接受锚点、已合并 PR、已解决 blockers 或其他可计数输出。
- `Quality`（质量）：人类评审、maintainer 评分、接受/拒绝结果、纠正率与 evidence 质量。
- `Token cost`（token 成本）：run 与 quota 记账。
- `User attention cost`（用户注意力成本）：user gates、评审请求、澄清 Turn、批准步骤与手动干预。

这里正是智能显示 surface 超越 dashboard 的地方：它补上缺失的质量信号。用户可以先用只读模式连接既有 agent 工作、评分工作，并看到 agent 是否在创造价值。LoopX 写回启用后，同一分数可以调整 gates、todos、锚点、reward 说明与下一个改进目标。

## 状态映射

首屏应在添加新 UI 状态之前由既有 LoopX 投影生成。

| 产品卡片 | 来源字段 |
| --- | --- |
| Goal Snapshot | registry goal、活跃状态目标、最新 status 分类 |
| 自上次检查后 | run 历史、refresh-state 交付结果、验证 evidence |
| 信号收件箱 | 连接器事件、用户反馈、issue/PR 元数据、文档变更 |
| 锚点选择 | 规划队列提案、晋升 todos、未来锚点 packets |
| 当前工作 | agent todos、`claimed_by`、建议性 `agent_profile_v1`、显式提供时的可选硬 leases |
| Blocker 或 Gate | user todos、operator gate、interaction contract、goal boundary |
| 下一个 Agent 动作 | quota 决策、推荐动作、下一动作、停止条件 |
| 我需要你做什么 | user todo 摘要与具体 operator 问题 |
| 反馈捕获 | reward 覆盖层、gate 命令、todo 更新、未来 feedback signal |
| 表现评审 | run evidence、reward 覆盖层、结果分类、成本摘要 |

缺失字段应优雅降级。当没有显式硬 lease 行时，把 `claimed_by` 显示为软所有权，避免声称排他执行。没有 `agent_profile_v1` 时，显示注册 peer id 与当前 claims；不从身份名推断排名或 authority。

## 创作者-Operator 示例

对一个非技术创作者-operator 案例，卡片可以这样读：

```text
Goal Snapshot
为一位创作者-operator 保持每周内容研究 loop 前进。

自上次检查后
Agent 发现了三个合成趋势簇，并拟定了两个角度选项。
Evidence 只是演示数据；不包含真实平台抓取。

当前工作
选中的 peer 正在构建 public-safe showcase 故事板。

Blocker 或 Gate
在用户批准语气与来源策略之前，发布保持阻塞。
安全侧路：打磨合成 demo 文案与反馈流程。

下一个 Agent 动作
生成假数据故事板，并验证其中不含私有资料或自动发布声明。

我需要你做什么
现在无需动作。
```

这就是产品应追求的可读性水平：用户无需读 agent 日志就能看到工作、边界、gate 与安全延续。

## 验收标准

该模型的第一个实现在以下情况就绪：

- 一个 public-safe status mock 可以从合成或既有紧凑 LoopX 投影渲染所有卡片；
- 打开的 user todos 显示为具体问题，而不是泛化"owner gate"文案；
- 信号收件箱与锚点选择可以在不要求定制 issue-fix UI 的情况下表示至少一个 public-safe issue/PR 试点；
- 无打开 user todo 状态安静渲染，没有虚假紧迫感；
- peer 所有权与显式评审交接可见，且不覆盖 quota 或 gate 决策；
- 反馈按钮映射到显式控制面效果；
- 表现评审说明保持 evidence 支撑，并区分价值、质量、控制、成本与学习；
- 私有 evidence、原始轨迹、凭据与内部链接不得出现在公开卡片载荷中。

该模型应成为当前 CLI/status 契约与未来前端或 Lark 首接触 surface 之间的桥。
