# 产品愿景


LoopX 不只是面向 AI 编码 loop 的开发者工具。它从那里起步，因为工程工作很快暴露控制面的难题：状态漂移、人类 gates、run evidence、handoffs、所有权、quota 与 public/private 边界。更大的产品类别是动态 goal 控制面：把静态 agent goal 变成长程、可评审的状态，在众多 Turn 之间保持可理解且可恢复。LoopX 运行在不同 agent harness 之上，提供长程状态、语义决策、治理、恢复与人机协同，而不替换执行工作的 harness。

长期产品应帮助不想检查 prompt、日志或轨迹的人。第一个客户是 Loop Agent 的 maintainer/operator：需要管理常开数字 worker、外部信号、人类 gates、evidence 与随时间积累价值的人。用户应当能够跨工具跑多个 agent、在非工作时间继续运行，然后打开首屏就能理解：

- agent 做了什么；
- agent 现在在做什么；
- 进展在哪里被阻塞；
- 接下来会发生什么；
- agent 需要用户提供什么；
- 用户反馈如何改变计划。

## Loop Agent

Loop Agent 是具有以下特征的常开数字 worker：

- 相对稳定的职责；
- 相对一致的工作目标；
- 它关注或接收的外部信号；
- 与职责匹配的工作产品；
- 对其所做的事及其为何重要的有组织 evidence；
- 通过轻量 performance-review loop 获得的人类反馈；
- 显式的专注与成本控制。

LoopX 不应通过在 executor 里隐藏更多自主性来让每个 worker 更聪明。它应让 worker 更可管理：可选工作、可见 gates、有界执行、紧凑 evidence、可评审成果与清晰的下一个改进目标。

## 首屏文案

**Always-on agent teams, governed by human judgment**

**Gate-aware human-in-the-loop control plane**

**Dynamic goal control plane for long-running agents**

**Runs on top of any agent harness — long-horizon state, semantic decisions, governance, recovery, and human-agent collaboration**

**让多个 agent 昼夜接力，把人的判断留在控制面。**

**运行在不同 agent harness 之上，为它们提供长程状态、语义决策、治理、恢复与人机协同。**

LoopX 把目标、用户决策、agent todo、认领关系、scope、safe fallback、
run history 和 quota 放进同一层状态：该等人的地方明确等人，不该空等的
安全侧路继续推进。

产品承诺是常开进展但不失控自主：注册 peers 可以继续独立认领有边界的工作，而人类 gates、capability gates、quota、evidence 与项目边界保持显式。从这个意义上说，LoopX 不只是更长的 prompt 或更大的 todo 列表；它是 executor loop 周围的动态 goal 状态。

## Maintainer 优先的管理 Surface

最高优先级产品 surface 是面向 maintainer/operator 的智能管理视图。它应回答：

- 自上次检查以来到达了哪些信号；
- 哪些信号是值得行动的高价值锚点；
- 每个活跃泳道由哪个 Loop Agent 拥有；
- 哪些人类 gates 需要关注；
- 什么 evidence 证明进展或解释停止；
- agent 在哪获得或失去了 performance-review 信用；
- 什么下一个管理动作最重要。

该 surface 先于领域特定 issue-fix UI。开源 issue 与 PR 工作有价值，因为它创造可见 artifacts 与可度量反馈，但它应喂养 maintainer surface，而不是定义整个产品。

### Agent 工作 Feed

理想的首交互更接近推荐 feed，而不是项目 dashboard。用户应能像浏览一串卡片一样评审 agent 工作：快速决定每个输出是否有用、被误导、有风险，或值得变成下一个锚点。

Feed 条目不是原始任务，也不是原始日志。它是 agent 工作卡：

- agent 产出了什么；
- 为什么这卡现在值得关注；
- 什么 evidence 支撑该声明；
- 它花了多少 quota 或用户注意力；
- agent 接下来提议什么；
- 有哪些一键反馈选择。

有用反馈应轻量但结构化：

- 有用；继续这个方向；
- 没用；降低这个模式的优先级；
- 方向错误；纠正 goal 或 reward；
- evidence 不足；添加验证；
- 晋升为锚点、showcase 或后续 todo；
- 有风险或私有；触发边界评审或 gate。

这把表现评审从周期性报告变成连续的人机协同信号。LoopX 应把 feed 按管理价值排序，而不是成瘾性排序：未解决 gates、高价值不确定工作、昂贵重复模式、evidence 缺口与 showcase 候选应在例行活动之前浮现。

## 显示 Surface 采用路径

智能显示 surface 与 LoopX 控制 loop 应在采用时解耦，但设计上共同成长。

第一步可以是只读：

- 摄入既有 agent artifacts、issues、PRs、docs、run 摘要或聊天反馈；
- 显示 agent 做了什么、存在什么 evidence、什么值得评审；
- 让 maintainer 对价值、质量、控制、成本与学习评分；
- 产出 performance-review 摘要，而不改变 agent 的下一个动作。

该模式甚至在一个团队采用 LoopX 之前就有用。它给 maintainer 一种低摩擦方式来检查并量化一个常开 agent 是否有用。

第二步是控制写回：

- 接受的反馈变成 gates、todo 变更、偏好提示、reward 说明或锚点选择；
- 低质量工作变成 blocker evidence、scope 纠正或下一个改进目标；
- 选中锚点变成带显式 evidence 与停止条件的有边界 LoopX 工作。

简而言之，显示 surface 让 agent 工作可见且可评审；LoopX 让该评审改变下一个 loop。两个 surface 可以顺序采用，但它们应共享 `signal_v0`、`anchor_v0`、`review_event_v0` 与 `performance_review_v0` 等 schema。

## 开源锚点

当开源 issue / PR solver 试点被选为高价值锚点时，它们是很强的价值证明候选：

- 可见公开 artifact：issue、PR、失败的检查、过期评审或冲突；
- 可信的 maintainer 痛点；
- 有界风险与清晰停止条件；
- 可度量成果：已路由、已诊断、已修复、已合并、已拒绝或被 gate；
- public-safe 故事潜力。

LoopX 在 maintainer 侧的职责是选锚点、定义候选 packet、记录 evidence 边界、捕获人类评审信号，把批准成果毕业为 showcase 资料。实际 solver 实现可以属于仓库特定 collaborator 或 adapter。

## Office Operations 连接器

Office 与 content-operations 工作流是另一个有用的 showcase 泳道。重点不是让 agent 产出更多帖子。重点是展示一个 Loop Agent 能连接更多信息 surface、选择更高质量信号、提议有用动作，并从人类反馈中学习。

Public-safe 工作流可以是这样：

```text
connector
  -> 信息
  -> 信号 / 趋势 / 锚点候选
  -> 草稿或动作提案
  -> 人类评分 / 反馈
  -> 可选的发布或外联 gate
  -> 表现评审 / 下一改进
```

好的连接器示例包括基于浏览器的社交研究、local-first 聊天归档搜索、issue / PR 元数据、会议笔记、任务系统与文档变更。发布或外联应保持显式 gate。

正确指标不是原始草稿数。更好的信号是已接受锚点、有用洞察、合格对话、用户评分草稿质量、反馈学习、来源边界正确性与每有用信号成本。

## 创作者-Operator 案例

一个有用的中期案例是自媒体或创作者运营用户。用户主要不关心底层 worker 是 Codex、Claude Code、浏览器 agent 还是工作流脚本。他们关心长程 agent 能否帮他们保持创作目标前进：

- 跨社交平台检测趋势；
- 把趋势对照用户创作偏好与受众；
- 提取值得创作的有用洞察；
- 起草文章、大纲、脚本或视频概念；
- 维护素材、措辞、来源与文案库；
- 显示自上次检查以来的变化；
- 在正确时机询问人类品味、风险或发布决策。

瓶颈既在产品体验也在模型能力。用户不应必须读原始浏览轨迹、私有笔记或 agent 推理才能知道工作是否有用。LoopX 应把那种活动变成一小套可见控制面对象：goals、gates、todos、evidence、feedback、boundaries 与 next actions。

## 产品化轨道

当前路线图应落地为四条 public-safe 轨道：

1. **Maintainer 管理 surface**：为信号收件箱、选中锚点、活跃泳道、gates、evidence 质量、表现评审、价值/成本趋势与下一个管理动作设计首屏卡片。
2. **非技术 operator 状态模型**：设计首屏卡片，说明发生了什么、正在发生什么、agent 在哪里被阻塞、接下来是什么，以及什么用户反馈会改变。该模型应避免内部 CLI 术语，把控制面状态翻译成通俗语言。
3. **开源锚点 packet**：定义 issue、PR、失败的检查、过期评审或冲突如何成为带 owner、风险、允许动作、evidence 边界、人类 gate 与 showcase 同意的候选。
4. **Office-operations 连接器 showcase**：用合成或经同意数据原型一个 public-safe 的连接器到信号到反馈 loop，带显式发布/外联 gate 与超出文章数的指标。
5. **反馈与边界契约**：定义用户反馈如何变成 gates、偏好、todo 更新或产品改进说明，同时保留来源归属、平台条款、no-autopublish gates 与私有创作资料边界。

## 边界

该愿景不把 LoopX 变成社交媒体爬虫、发布 bot 或最终用户内容平台。那些工具可以住在宿主产品或项目 adapter。LoopX 应提供持久控制投影：当前 goal、决策 gates、安全下一个工作、evidence 摘要、反馈写回与边界检查。

默认产品姿态保守：

- 未经显式 user gate 不自动发布内容；
- 不把私有笔记、草稿或创作资料当作公开 evidence；
- 不把原始平台数据复制进公开文档或示例；
- 不未经度量的 public-safe 基础就声称趋势、受众或性能提升；
- 把用户品味反馈与硬安全或权限 gates 保持分开。

## 为什么它属于 LoopX

该案例与工程和 benchmark loop 检验同一产品承诺，但用户不同：一个需要清晰而不是基础设施的非工程 operator。如果 LoopX 能让这个工作流可读，它就证明控制面不只是给开发者用的。它是一种保持长程 agent 工作有用、有边界、可评审且易于转向的方式。
