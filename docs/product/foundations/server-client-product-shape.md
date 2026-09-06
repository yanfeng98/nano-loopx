# Server-Client 产品形态


本笔记描述 LoopX 的中期产品形态。它不是网络服务的实现规范。目的是把产品角色命名得足够清晰,让未来的 CLI、dashboard、Lark、MCP 与 server 工作共享一个思维模型。

LoopX 是 agent Loop 周围的控制面:

- server 拥有持久的 goal state、事件历史与受治理的规划车道;
- client 充当用户的意图代理;
- 执行器 Loop 做有界工作并写回 evidence。

## 产品角色

### Server

LoopX server 是持久的控制面 owner。首先应把它看作数据库支撑的 state 系统,而不是 agent 智能所在处。在 local-first 模式下,这可能仍由文件加 CLI 命令实现。但在产品形态中,server 是长程事实变得连贯的地方:

- 稳定的 goal 身份、当前信念、todo state、gate state 与运行历史;
- 已注册的 agent 身份、角色、范围、worktree 策略与评审交接默认;
- 面向维护者的信号收件箱、所选锚点与绩效评审摘要;
- 逐 todo 软认领与可选硬租约 state;
- 配额、花费、幂等与并发策略;
- 紧凑的公开/私有边界摘要;
- 面向客户端的紧凑思维模型与管理投影;
- 调度的规划、dreaming 与重规划队列;
- 面向维护者绩效评审的评审与反馈汇总;
- 从建议车道提升提议到普通用户或 agent todo。

该存储周围的后端层应薄而严格:类型化读取、幂等写入、冲突检查、紧凑投影、调度器决策与公开/私有边界执行。它更接近控制面数据库加投影 API,而不是拥有领域行为的传统应用服务器。

server 应保持保守。规划车道可以排序候选 todo、呈现重构警告或提议 evidence 探针,但直到通过正常 gate、配额与边界路径提升前,它们不执行受保护工作、不读取私有材料、不花费交付配额。

对于维护者优先的产品界面,server 应把外部信号视为候选工作。GitHub issue、pull request、失败检查、Lark 反馈或文档变更可以进入信号收件箱;只有所选高价值锚点成为 todo、owner 路由请求或 showcase 候选。这防止"总是在运行"变成"总是忙"。

### 交付与规划队列

server 路线图应把两个队列族分开,同时保持在同一个持久 state 系统中:

- **交付队列**:执行器可以在 `quota should-run`、认领或租约检查、worktree 策略、能力检查与 goal 边界检查后处理的提升用户或 agent todo。
- **规划队列**:dreaming、周期重规划、记忆整合与重构警告提议,它们可以检查紧凑运行历史并排序候选工作,但提升前保持建议性。

两个队列应共享平淡的控制面基质:逐 goal 锁、逐 todo 或逐提议身份、幂等键、仅追加事件、公开/私有边界摘要与紧凑状态投影。它们不应共享交付权限。规划提议可以说"这个 todo 应上移"、"这个陈旧车道需要拆分"或"这个阻碍应被询问";它不能悄然变更 active 真相、认领交付工作、读取 gate 材料或花费交付配额。

提升是关键转换:

```text
planning proposal
  -> operator/controller decision or policy-approved controller action
  -> normal user/agent todo or gate
  -> quota / lease / boundary checked delivery turn
```

这让 server 端 dreaming 与周期重规划有用,而不把 server 变成隐藏自主 agent。Server 拥有持久调度事实与提议记录;client 与执行器仍执行可见的人机协同转换与有界交付工作。

### 管理投影与摘要

Loop Agent 管理在普通状态之上增加第二个投影需求。Server 应保持内核 state 显式,但向客户端暴露压缩读模型:

- **思维模型投影**:把 goal state、gate、todo、认领、范围、evidence、运行历史、配额与交接映射为五个用户概念:Goal、下一步、需要你的判断、Evidence、可以继续。
- **绩效评审投影**:把一个车道或锚点汇总为数量、质量、token 成本、用户注意力成本、最新 evidence 与下一个预期。
- **评审流投影**:把近期输出、gate、阻碍与信号转化为用户可以标记有用、没用、需要 evidence、范围外或太贵的卡片。

这些投影首先应从记录的 state 确定性得出。模型支撑的摘要器可以帮助产生更友好的措辞、聚类重复信号或起草评审摘要,但出于控制目的它必须默认关闭。它的输出建议性,直到通过类型化评审、反馈、todo 或 gate 转换提升。它不能批准 gate、变更 active 真相、隐藏缺失 evidence 或花费配额。

## Multica 参考点

Multica 是这种产品拆分的有用参考实现,但 Goal Harness 应借用其形态而不是完整产品类别。

公开 Multica 文档描述的栈有 Next.js 前端、使用 Chi / sqlc / WebSocket 的 Go 后端、PostgreSQL 17 加 pgvector,以及运行编码 CLI 的本地 agent daemon。其 CLI/daemon 指南把 daemon 当作本地运行时:它检测已安装 agent CLI、向 server 注册运行时、轮询认领任务、创建隔离工作区、启动 agent CLI、流回结果并发送心跳。

LoopX 的启示:

- **数据库优先**:持久协调事实应在被投影进 UI、提示或交接包之前,存在于真实 state 存储或文件支撑等价物中。
- **后端作为控制 API**:server 代码应强制执行 schema、幂等性、租约、边界、配额与投影契约。
- **Daemon/执行器在 state 存储之外**:agent 执行属于本地 daemon、Codex/App Loop、终端 agent 或基准 runner。Server 调度与观察;它不成为模型运行时。
- **事件流加投影**:issue/任务状态、评论、阻碍、心跳、认领与结果应该是可追加事实,能产生首屏卡片、评审包与自动化提示。
- **向量记忆是可选的**:当产品想要 skill 或记忆检索时,pgvector 有用。LoopX 不应为 v0 控制面正确性要求向量存储;关系/事件事实优先。

因此 LoopX 中的"server"通常应意味着:

```text
durable state store
  + event ledger
  + typed write API
  + projection API
  + scheduler / quota decisions
```

而不是:

```text
agent runtime
  + hidden planner
  + autonomous executor
```

### Client

Client 是维护者的面向 agent 代理。它把人类意图转化为受治理的控制面转换,并把原始 agent 活动转回运维者可读的界面。

Client 可以是 CLI、dashboard、Lark 文档工作流、浏览器 UI 或 host 适配器。重要的产品责任相同:

- 解释 goal 现在试图完成什么;
- 显示信号收件箱与所选高价值锚点;
- 显示发生了什么、什么被阻碍、接下来会发生什么;
- 显示 Loop Agent 是否在赚取价值、尊重控制并保持成本意识;
- 收集用户判断、品味、批准、拒绝、延迟或奖励;
- 把该输入转化为 gate、偏好、todo 变更或交接;
- 在不嵌入陈旧策略的情况下把执行器 Loop 路由到当前 state;
- 让对等方认领与显式评审交接可见。

这就是 client 超越意图分类的原因。它是长程工作的产品界面:它承载上下文、权限、反馈、可见性与信任。

Issue/PR solver 试点因此应首先以锚点管理流程出现,而不是作为单独的 issue-fix 产品。Client 可以显示:为什么这个 issue 或 PR 值得行动、谁拥有实现、允许什么动作、将接受什么 evidence,以及结果能否升格为公开 showcase 材料。

### 执行器 Loop

执行器 Loop 是 Codex、Claude Code、Cursor、终端 agent、基准 runner 或其他有界 worker。它做工作,但它不应是长期真相源。

执行器 Loop 应:

- 工作前读取当前 goal state 与配额决策;
- 尊重用户 gate、公开/私有边界与已认领 todo 所有权;
- 把一个 Turn 限制在所选的 todo 或安全旁路;
- 写回 evidence、校验、阻碍与下一步提议;
- 在敏感材料、破坏性 git、私有材料、生产动作或未批准的发布边界前停止。

执行器可以强大,但不必成为产品权威。LoopX 把权威保持在使用户与每个已注册对等方都能检查的共享 state 中。

## 交互 Loop

产品 Loop 是:

```text
user
  -> client
  -> LoopX server/state
  -> executor loop
  -> LoopX server/state
  -> client
  -> user
```

Client 不应通过把每个用户句子直接变成 agent 指令来绕过 server。Executor 不应通过在聊天或本地记忆中隐藏重要决策来绕过 client。LoopX 存在的意义是让用户判断、agent 工作、evidence 与未来规划在同一控制面中保持可见。

## 解耦显示与控制

智能显示界面可以在完整 LoopX 控制 Loop 之前采用。这种分离对早期用户与合作伙伴团队很重要。

在**仅显示模式**中,server 或本地 state 存储可以摄取 agent 工作产物与评审信号,而不拥有执行器的下一动作:

```text
external agent artifacts
  -> signal / evidence ingestion
  -> review_event_v0
  -> performance_review_v0
  -> maintainer dashboard
```

此模式量化价值,但不引导执行。它适合现有 Codex、Claude Code、OpenViking 风格 solver、office-operations 或内部 agent 工作流,用户首先想检查与打分工作。

在**LoopX 控制模式**中,已接受的评审输出成为受治理 state:

```text
performance_review_v0
  -> gate / todo / anchor / reward / preference writeback
  -> quota and boundary checked LoopX work
  -> new evidence
  -> next review event
```

两种模式应存在于一个产品系统中,目前优选一个仓库。代码边界仍应显式:显示应用可以只读运行,而写回路径必须调用 LoopX schema、gate、配额与边界检查。这让前端协作者可以构建精致界面,而不会意外创建第二真相源。

## 能力边界

LoopX 不应变成:

- 拥有模型执行、工具、计费或权限的 agent 运行时;
- 每一步都是隐藏自动化边的通用工作流引擎;
- 私有聊天、日志、基准痕迹或本地 evidence 的原始转录存储;
- 爬虫、发布器或生产动作权威;
- 项目特定适配器、评估器或领域工具的替代品。

它应围绕这些系统提供受治理投影:goal state、gate、todo、认领或租约、配额、evidence 摘要、运行历史、反馈、规划提议与交接包。

## 首批契约切片

首批产品切片应保持小而兼容 CLI-only 模式。

1. **`goal_channel_projection_v0`**:goal、gate、todo、当前阻碍、最新 evidence、配额与下一步动作的只读首屏投影。
2. **`mental_model_projection_v0`**:把内核 state 映射为 Goal、下一步、需要你的判断、Evidence 与可以继续的面向用户压缩层。Client 应在暴露原始认领、范围、配额、运行历史或交接详情前渲染它。
3. **`agent_profile_v1`**:带建议性功能角色、默认范围、任务类别与动作偏好的已注册对等方身份。任务与仓库策略拥有工作区、评审与合并要求。
4. **`task_lease_v0`**:逐 `(goal_id, todo_id)` 所有权,含 TTL、幂等键、写入范围、续期、转移与冲突行为。
5. **`planning_queue_v0`**:在控制器或用户决策加正常配额与边界检查提升前保持不可执行的建议性规划、dreaming 与重规划提议。最小记录应包括提议 id、来源运行窗口、到期/重试策略、候选 todo 引用、置信度、提升目标与幂等键。
6. **`feedback_signal_v0`**:捕获为四种控制效果之一的用户反馈:gate 决策、偏好提示、todo 变更或产品改进笔记。原始私有聊天不应成为公开 evidence。
7. **`performance_review_projection_v0`**:有界窗口内的车道或锚点汇总,含输出数量、质量标签、token 或配额成本、用户注意力成本、evidence 引用与下一个预期。它应引用来源事件,而不是复制原始工作上下文。
8. **`review_feed_card_v0`**:输出、阻碍、信号或提议 todo 的卡片级投影,可以接收用户反馈并随后产生 `feedback_signal_v0`、`todo_update`、`anchor_update` 或 `performance_review_note`。
9. **`anchor_candidate_v0`**:可能成为工作的所选外部信号。最小记录应包括来源种类、公开/私有边界、关心的理由、允许的动作、owner 拆分、停止条件、预期 evidence 与 showcase 同意状态。
10. **`project_level_reward_v0`**:跨项目的长程 agent 工作聚合价值估算。它结合数量、人工打分的质量、token 花费与用户注意力花费,使基准 evidence 可以与维护者价值比较,而不把一切约简为单个任务分数。
11. **`advisory_summary_v0`**:近期 state 的可选模型支撑摘要,仅用于措辞或聚类。它出于控制目的默认关闭,除非转化为上述类型化对象,否则不能变更 state。
12. **`handoff_packet_v0`**:承载所选 todo、停止条件、校验预期、边界笔记与写回目标的紧凑执行器输入,而不复制整个项目历史。

每个切片在成为更丰富 UI 的一部分之前,应有一个 CLI 回退、一个紧凑状态投影与一个公开/私有边界检查。

## 路线图含义

此产品形态把重心从"围绕 Markdown goal 文件的 CLI"变为"以 CLI 为首个客户端的动态 goal 控制面。"

这不会让 CLI 过时。CLI 是兼容基线与安全回退。它也让契约诚实:如果未来 server 或 dashboard 无法回退到等价 CLI 读写,它可能正在创建第二真相源。

近期路线图因此应优选:

- 契约优先的状态与写 API,而非仅 UI state;
- 思维模型投影,而非仅前端重映射;
- 本地并发正确性,而非宽泛 server 调度;
- 任务范围对等方认领与 worktree 策略,而非自主多 agent 合并;
- 规划提议,而非后台执行;
- 用户反馈与绩效评审建模,而非个性化声明;
- 锚点选择,而非领域特定 solver UI。

跨这些层级的产品承诺保持不变:让人类决策显式,保持独立时的安全旁线工作推进,并让每个 agent Loop 留下足够 evidence 让下一个 Loop 恢复剧情。

## 参考

- Multica README architecture section:
  <https://github.com/multica-ai/multica#architecture>
- Multica CLI and Agent Daemon Guide:
  <https://github.com/multica-ai/multica/blob/main/CLI_AND_DAEMON.md>
