# 智能管理 Surface


本说明定义 LoopX 的 maintainer 优先管理 surface。它是本地控制面与更大 "Loop Agent" 愿景之间的产品桥：保持稳定职责的 agent、吸收外部信号、产出可评审工作，并通过长期人类反馈改进交付。

该 surface 应首先服务运营 LoopX 本身的 maintainer。如果它不能帮助 maintainer 理解多个 LoopX agent、user gates、evidence、质量、成本与后续选择，把它作为通用 operator dashboard 出售就为时过早。在那之后，同一 surface 可以支撑 issue-fix loop、开源 PR 驱动增长、office operations 与领域包。

## 产品论点

Loop Engineering 不只是让 agent 进程保持运行。难的是让长程工作可管理：

- goals 保持足够稳定以恢复；
- agent 可以接收碎片化的人类与外部信号；
- 工作输出可见、可评分、可比；
- 人类注意力花在判断上，而不是调度上；
- evidence 与边界在跨 agent loop 交接后幸存。

因此 LoopX 应暴露一个管理 surface，而不只是 status 页。该 surface 回答："哪个 Loop Agent 值得托付更多工作，哪条泳道需要人类判断，以及这份成本产生了什么价值？"

## Loop Agent 定义

Loop Agent 是具有以下特征的长程 worker：

- 相对稳定的职责；
- 相对一致的 goal 或成功模型；
- 随时间吸收外部信号的能力；
- 与职责匹配的输出；
- 组织自身工作 evidence 的习惯；
- 在人类指导下的周期性表现评审；
- 在保持专注与低成本的同时改进交付的约束。

该定义刻意把 agent 与任一具体执行器分开。Codex、Claude Code、浏览器自动化、issue solver 或项目 adapter 都可以是执行器 loop。LoopX 拥有该 loop 周边的控制状态：goal、gate、todo、evidence、feedback、quota 与 handoff。

## 第一个用户：Maintainer

第一个真实用户是管理 LoopX 工作的 maintainer。这很重要，因为 maintainer 面对的是最难版本的问题：

- 许多活跃项目泳道；
- 拥有不同建议 scope 与已认领任务的注册 peers；
- 公开文档、benchmark 工作、前端工作与伙伴探索并行推进；
- 频繁出现但有用的用户反馈零散分片；
- 需要挑选少数高价值锚点，而不是追逐每个可能的 issue、案例或集成。

对开源 PR 驱动增长而言，LoopX 不必是 issue solver。伙伴或宿主产品可以运行 solver。LoopX 应帮助 maintainer 选择高价值锚点仓库、跟踪 solver 工作是否创造可信 evidence，并把有用成果转化为 showcase、onboarding 或产品反馈。

## 核心 Surface

Maintainer surface 应作为只读优先控制台起步，包含五个稳定区域。

### 1. 信号收件箱

收件箱收集外部与人类信号，但不假装它们全是任务：

- 用户反馈与问题；
- 项目或机会 issue/PR；
- 伙伴/项目更新；
- benchmark 或验证事件；
- 内容或外联机会；
- onboarding 中看到的产品摩擦。

每个信号都应携带来源、新鲜度、隐私边界与建议控制效果：忽略、询问用户、创建 todo、更新 evidence、创建锚点或安排评审。

### 2. 锚点板

锚点板是对抗"什么都做"的解药。它命名当前真正重要的少数高价值证明路径。

示例：

- LoopX 自我管理作为 dogfood 锚点；
- 托管 frontstage 与 quickstart 作为 onboarding 锚点；
- 一个公开 issue/PR loop 作为开源增长锚点；
- 一条 benchmark/evidence 泳道作为价值证明锚点。

锚点应当少、显式、可评审。一个信号或 todo 可以有用，但不一定成为锚点。

### 3. Agent 泳道板

泳道板按当前 claim 与功能档案展示注册 peers：

- runtime 或发布验证；
- 产品或 capability 工作；
- 监控与 evidence 观察；
- 领域包工作；
- 只作为 evidence 生产者时的外部伙伴 worker。

对每条泳道，显示当前 todo、claim、建议 scope、任务 workspace 策略、最新 evidence、blocker 与下一个停止条件。Peer 工作应当可见，而不是藏在后台聊天里。

### 4. 评审 feed

评审 feed 是注意力高效 surface。它可以像轻量推荐 feed，但语义是工作评审，不是娱乐。

每张卡片都应可关闭或评分：

- 有用 / 没用；
- 晋升为锚点；
- 要求 evidence；
- 需要用户决策；
- 太贵；
- 越界；
- 私有或不安全；
- 拆成 todo；
- 归档。

这让 maintainer 可以快速"刷过"agent 输出，同时仍创造结构化反馈。卡片结果应映射到类型化 LoopX 事件，如 `review_event`、`feedback_signal`、`todo_update`、`anchor_update` 或 `performance_review_note`。

### 5. 表现评审

表现评审把碎片工作变成价值故事。它不应是单一 benchmark 分数。对长程项目工作，价值更接近：

```text
reward = f(quantity, quality, token_cost, user_attention_cost)
```

其中：

- quantity 是任务/输出数量与交付吞吐；
- quality 来自评审 feed 分数、evidence 强度与人类反馈；
- token cost 是可观测时的模型或执行成本；
- user attention cost 是询问、中断、含糊摘要与重复转向负担。

第一个实现可以在数值精度前使用粗略标签：高/中/低质量、便宜/正常/贵成本、低/中/高注意力成本。重要的产品动作是让"agent 价值"在项目级别可评审，而不只是在单任务 benchmark 级。

更窄的 reward 模型位于
[项目级 reward 模型](../foundations/project-level-reward-model.md)。该说明把公式、评审 schema、benchmark 边界与验收标准放在一处，让管理 surface 专注于用户交互。

## 数据契约

Surface 应从显式契约成长，而不是只靠 UI 状态。

| 契约 | 用途 |
| --- | --- |
| `signal_v0` | 带来源、边界、新鲜度与建议效果的外部或人类输入。 |
| `anchor_v0` | Maintainer 想要评估的选中证明路径。 |
| `review_event_v0` | 用户对输出、todo 或信号的卡片级决策或评分。 |
| `feedback_signal_v0` | 规范化效果：gate 决策、偏好提示、todo 变更、reward 或产品说明。 |
| `performance_review_v0` | 周期性泳道级评审：输出、质量、成本、注意力与下一步期望。 |
| `management_projection_v0` | 连接 goals、泳道、锚点、gates、todos、evidence 与评审 feed 的读模型。 |
| `mental_model_projection_v0` | 把 kernel 状态压缩为 goal、下一步、blocker/权限、evidence 与继续状态的用户面向投影。 |

既有 LoopX 对象仍是控制的事实源：goal、gate、todo、quota、evidence、run 历史、handoff 与边界。管理 surface 在其周围添加评审与价值语义。

## 观察/评审/评分与控制

管理 surface 应在其被允许控制工作之前就有用。这让采用低风险，并给用户一种方式：在信任 LoopX 写回之前评判现有 agent。

| 层 | 允许行为 | 写边界 |
| --- | --- | --- |
| 观察 | 读取 goals、todos、claims、gates、evidence、run 历史与紧凑成本 | 不改动 LoopX 状态 |
| 评审 | 让用户检查卡片、标记有用/没用、要求 evidence 或标记边界疑虑 | 仅本地或草稿 `review_event_v0` |
| 评分 | 为泳道或锚点聚合质量、成本、注意力与输出标签 | 只在显式用户保存后追加评审摘要 |
| 控制 | 把反馈变成 todo 变更、gate 决策、锚点晋升或 replanning | 正常 LoopX CLI/API 写路径、quota、边界与 authority 检查 |

UI 不应模糊这些层。用户可以浏览并评分 feed，而不授予控制。一个分数可以推荐控制转变，但该转变仍须与 CLI 驱动工作一样通过同一 LoopX 状态、authority 与边界契约。

## 采用路径

管理 surface 与控制 loop 可以分阶段采用。

1. **观察与评审**：连接项目，展示 todos/evidence/泳道，让用户评分输出。不需要控制写入。
2. **结构化反馈**：把评审选择映射进 `feedback_signal_v0`、产品说明与建议 todo。
3. **LoopX 控制**：把选中反馈晋升为 gates、todo 变更、优先级变化或规划的 agent Turn。
4. **表现评审**：总结每个 Loop Agent 的输出质量、成本、注意力成本与下一个职责。

这让智能显示 surface 在完整自动化被信任之前就有价值。它也给了 LoopX 与宿主产品共同成长的路：宿主可以保留其执行器或 issue solver，而 LoopX 提供可评审的控制与管理层。

## 仓库与应用边界

第一个实现可以住在现有 dashboard 的同一仓库，因为它依赖同一批公开控制面契约。保持在一起避免投影模型仍在变化时出现第二套事实源。

边界应显式：

- `loopx/control_plane/` 拥有事实源 schema、CLI 写入、status 投影、quota、gates 与 public/private 检查；
- `loopx/presentation/` 拥有基于 public-safe LoopX 状态构建的显示投影、渲染器与外部显示 sink；
- `apps/presentation/dashboard/` 拥有只读优先 operator UI、评审 feed mock 动作与 URL 支持过滤器；
- `docs/product/` 拥有产品契约与验收标准；
- 公开 showcase 路由解释想法，而 ops 路由管理真实本地状态；
- 任何浏览器写路径都必须调用类型化 LoopX 命令或本地 API，并保持在独立 capability gate 之后。

这意味着管理 surface 是 LoopX 的一部分，但并非所有未来宿主产品都必须住在这个仓库。伙伴 issue solver、office-ops 连接器或内容 agent 可以留在仓库外，向 LoopX 暴露紧凑信号、evidence 与评审卡。

## 前端协作模型

前端协作应专注于让管理 surface 感觉像真实工作产品，而不是把控制 authority 移进浏览器。

有用的协作领域：

- 项目选择器、泳道、锚点、评审 feed 与表现评审的信息架构；
- 过滤、搜索、评分与快速关闭的密集 operator 交互模式；
- 重复评审 session 的可访问性与响应式行为；
- 区分 user gates、软偏好与边界风险的视觉层级；
- 写 API 启用前的评审卡本地 mock 动作。

前端协作非目标：

- 从任意 UI 状态直接改动 `.loopx`、`.local` 或 runtime 历史；
- 无法解释为 LoopX 投影的隐藏推荐排名；
- 自动发布或生产动作；
- 把私有聊天、原始轨迹或私有文档导入公开夹具。

## 近期 PoC

第一个 PoC 应狭窄：

- 项目选择器：全部项目或单个项目；
- 按 id/文本/claim/status 的 todo 搜索；
- 注册 peers 及其当前 claims 的泳道摘要；
- 带具体问题的 user-gate 面板；
- useful/not-useful 动作 mock 或仅本地的 evidence/评审 feed；
- 一个表现评审面板，显示输出数量、质量标签、可得时的 token 成本与用户注意力成本代理。

第一个被接受的用例是 maintainer 自我管理：找到一个 todo、理解它为何被选中、评审近期输出，并决定什么应成为锚点。Issue-fix 与 office-operation 案例可以在 maintainer 流程可信后复用同一 surface。

### PoC 验收计划

当 maintainer 能在本地数据上完成以下 loop 时，PoC 通过：

1. 选择全部项目或单个项目。
2. 按 id 或文本搜索 todo，并看到其 goal、status、claim、泳道与 evidence 指针。
3. 检查当前 user gate，并确认是否需要动作。
4. 评审至少三张工作卡，在本地/草稿层标记有用、没用、需要 evidence 或越界。
5. 看到泳道级评审摘要：输出数量、质量标签、可得时的 token 成本与用户注意力成本代理。
6. 把恰好一个评审过的条目晋升为提议 todo 或锚点，且在显式写路径启用前不改动 LoopX 控制状态。

该验收路径刻意在更广 issue-solver 或 office-ops showcase 之前服务 maintainer 管理。一旦它能在 LoopX 自身工作，同一投影就可以把伙伴 issue-fix 结果或 office-operation 信号作为外部 evidence 摄入，而不是把它们当作一等控制 authority。

## 非目标

- 不把 UI 变成自主隐藏规划器。
- 不把软偏好反馈当作安全或权限策略。
- 不把私有聊天、轨迹或内部文档导入公开 evidence。
- 不只优化内容量；没有质量与注意力成本的输出数量是浅薄指标。
- 不让每个 issue 或信号都变成任务。锚点由 maintainer 选择。

## 验收标准

以下条件满足时，该设计才从文档进入实现：

- 它无需私有上下文即可解释当前 LoopX maintainer 工作流；
- 它把每个用户交互映射为类型化事件或 no-op；
- 它把观察/评审与控制/写回分开；
- 它可以按输出、质量、成本与注意力成本比较至少两条 agent 泳道；
- 它给 maintainer 一种快速方式找到 todo、评审其 evidence，并决定它是否属于高价值锚点。
