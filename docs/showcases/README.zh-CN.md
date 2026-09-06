# LoopX 案例展示

> [English](README.md)

本目录是 LoopX 完整、公开安全的案例清单。先从独立用户证据开始,再用案例类型与证据标签把真实世界采纳、贡献者案例、创作者 dogfooding 与可复现 demo 区分开。

## 从真实使用开始

**来源说明:** 前两个案例中的聊天截图是经所有者批准的、来自 LoopX 公共 Lark 开发者群的消息摘录。它们仍然是用户报告的证据,而不是独立复现的证明。

### 13+ 小时 C++ 算法精度运行

**独立用户** · 报告时长 `>13h` · 未报告参数微管理

LoopX 让一个复杂的精度任务与所声明的愿景保持一致,然后用 replan 触发公开研究,而不是继续本地参数折腾。用户报告精度提升,并保留了实验证据。

<p align="center">
  <a href="../assets/showcases/user-feedback/cpp-accuracy-13h-user-report.jpg"><img src="../assets/showcases/user-feedback/cpp-accuracy-13h-user-report.jpg" alt="经授权的用户反馈:报告一次超过 13 小时、精度提升且保留证据的 LoopX C++ 算法运行" width="48%"></a>
  <a href="../assets/showcases/user-feedback/cpp-accuracy-public-research-user-report.jpg"><img src="../assets/showcases/user-feedback/cpp-accuracy-public-research-user-report.jpg" alt="经授权的后续说明:LoopX replan 触发了公开研究,并发现了一个 code-memory MCP" width="48%"></a>
</p>

*来源:经所有者批准的、来自 LoopX 公共 Lark 开发者群的消息摘录。运行时与结果是用户报告的;所引用的
[code-memory MCP](https://github.com/DeusData/codebase-memory-mcp) 是公开的,但私有项目及其测量值无法独立复现。
[阅读案例](cases/independent-cpp-accuracy-long-run.md)。*

### 四天无人值守 agent 运行

**独立用户** · 报告时长 `4d` · 未报告运行期间干预

LoopX 让一个 agent 在四天窗口内持续做有用工作,并保留了一个周期报告界面供事后检查。

<p align="center">
  <a href="../assets/showcases/user-feedback/four-day-unattended-user-report.jpg"><img src="../assets/showcases/user-feedback/four-day-unattended-user-report.jpg" alt="经授权的聊天摘录(最小脱敏):报告一次无人值守四天的 LoopX agent 运行" width="72%"></a>
</p>

*来源:一份经所有者批准、最小脱敏的、来自 LoopX 公共 Lark 开发者群的消息摘录。工作量、运行历史与质量评估仍然私有且为用户报告。
[阅读案例](cases/independent-four-day-unattended-agent.md)。*

### 跨越七个合并 PR 的公共 Engine 重构

**独立用户** · 七个合并 PR · 维护者审查与合并仍然在场

一个持久的重构 goal 变成了在公开
[`zilliztech/mfs` Engine issue](https://github.com/zilliztech/mfs/issues/166)
与七个合并 PR 之上的分阶段组件抽取。仓库独立验证了 issue 与 PR 序列;LoopX 归因、感知质量与所报告的 `1B+` token 规模仍然是用户报告的。

[阅读案例并检查全部七个 PR](cases/independent-public-engine-refactor.md)。

打开[托管的案例展示索引](https://huangruiteng.github.io/loopx/docs/showcases/index.html),
查看双语可视化案例界面。
[反馈覆盖地图](user-feedback-coverage.md)记录了每一个输入簇,包括被刻意未提升为成功案例的有用信号。

## 案例包含什么

案例展示不是原始运行日志。每个案例都应把一次真实协作归结为可复用的控制面模式:

- LoopX 变得有用之前的情形;
- 改变工作 Loop 的 LoopX 行为;
- 用白话表达的用户价值;
- 证据边界,包括哪些必须保持私有;
- 可复现的 demo,或 demo 仍待完成的原因;
- 未来网站可渲染为公开证据序列的可选数据。

## 目录契约

机器可读目录位于
[showcase-catalog.json](showcase-catalog.json)。公共文档与未来前端界面应消费该文件,而不是抓取散文。
第一个前端界面契约见
[frontend-surface.md](frontend-surface.md)。
种子用户反馈与案例候选在成为目录条目或前场卡片之前,应遵循
[PoC 反馈与案例报告 Loop](poc-feedback-case-report-loop.md)。

第一个静态视觉资产是公开安全的
[控制面面板](../assets/control-plane-board.svg),它展示一个用户关卡保持可见,
同时一条作用域受控的旁路穿过已认领 todo、配额护栏、运行历史与证据回写继续推进。
第一个创作者-操作者 storyboard 是
[creator-ops-fake-data-storyboard.md](creator-ops-fake-data-storyboard.md)。
它的反馈与来源状态契约是
[creator-ops-feedback-boundary-contract.md](creator-ops-feedback-boundary-contract.md)。
第一个静态前场原型由目录生成,命令为
`python3 examples/showcase-frontstage-prototype.py --output /tmp/loopx-showcases.html`。

仪表盘前场现在有一条独立的公开安全分享捆绑路径,用于展示一个看起来像实时状态的控制面面板,而不暴露本地状态:

```bash
cd apps/presentation/dashboard
npm run export:frontstage-share
```

这会写入 `/tmp/loopx-frontstage-share-bundle`,包含静态
[公共首页](https://huangruiteng.github.io/loopx/)、编译后的仪表盘、一个
脱敏的 `goal_channel_projection_v0` 状态 fixture、直接的 `/frontstage/`
静态路由支持,以及一个 manifest。GitHub Pages 发布的是这个生成工件,而不是实时 registry 文件或本地状态导出。交互式仪表盘路由仍然是导出者兼容界面,而不是被推广的公共入口。新用户应从首页开始;公共案例、
效率证据与公共边界来自本目录,而实时本地 `statusUrl` 数据流只属于明确的运维模式检查。
动画案例展示资产从
[公共 storyboard 工件](showcase-animation-storyboard.json)开始。保持
`showcase-catalog.json` 作为唯一的案例数据来源。
用以下命令生成第一个目录驱动的动画原型
`python3 examples/showcase-animation-prototype.py --output /tmp/loopx-showcase-animation.html`,
或直接打开已提交的
[showcase-animation-prototype.html](showcase-animation-prototype.html)。用
`python3 examples/showcase-animation-prototype-smoke.py` 验证该工件。

![托管的 LoopX 前场展示公开安全案例](../assets/frontstage-showcase-first-screen.png)

## 实验性功能 Demo

### DSH × LoopX:Replan 一个真实决定

[![DSH × LoopX 录屏封面](../assets/showcases/dsh-loopx/dsh-loopx-cover.png)](../assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)

[60 秒真实 DSH 录屏](../assets/showcases/dsh-loopx/dsh-loopx-quickstart-replan.mp4)
从一个明确的 `loopx` 技能选择开始,然后展示一个 serverless 约束
把日志库决定从 Pino 改为 Roarr,却没有丢失更早的证据。公共 fixture 验证了 3/3 行为,
并记录了为什么 12 个包变成 4 个。

    python3 examples/dsh-loopx-demo-smoke.py

阅读[案例与证据边界](cases/dsh-loopx-replan-demo.md),或
[复现 DSH 路径](../../examples/dsh-loopx-demo/README.md)。

### 从一个有价值的 Loop 开始

如果你想在阅读案例研究之前先看一个轻量级第一个 demo,请从新手预设选择器开始。
它展示了一个有价值的 Loop 如何编译成真实 LoopX 命令,而不授予写权限:

```bash
loopx preset list
loopx preset show daily-triage
loopx preset show ci-sweeper
```

Daily Triage、Changelog Draft 与 PR Watch 是入门级的报告/草稿/关注路径。
CI Sweeper 与 Dependency Sweeper 之所以可见,是因为它们属于高 ROI 的维护者工作流,
但它们保持 opt-in,并在尝试任何隔离 worktree 补丁之前先做 dry-run 或策略报告。

### 自动研究一键启动

自动研究路径是实验性的一键 agent-team demo:

```bash
loopx auto-research "How should we evaluate whether multi-agent auto research creates value?"
loopx auto-research start "How should we evaluate whether multi-agent auto research creates value?" --execute
```

契约命令预览研究简报、证据边界与下一次启动包。`start --execute` 命令通过通用多 agent 内核打开可见的 Codex CLI lane;lane 撰写的证据仍然需要先通过 LoopX 状态回写,demo 才能声称进展。参见
[auto-research 命令路径](../../demo/auto_research/README.md)。
对于已发布的 stop marker、`--attach` 接管与状态感知唤醒周期,请使用贡献者
[stop/takeover/wake 演练](../guides/auto-research-stop-takeover-wake-walkthrough.md)。

### 审查 Agent 工作

Review Agent Work 也是一个实验性入口:它在授予更多控制之前,使用先读后行的仪表盘路径检查已连接项目、用户关卡、agent lane、todos 与证据。

```bash
loopx serve-status --global-registry --port 8766 --limit 80
cd apps/presentation/dashboard && npm run dev
```

CLI 状态仍然是真相来源,浏览器写入需要明确的本地 opt-in,审查信号保持与执行权限分离。

## 独立用户案例

| 案例 | 问题 | LoopX 行为 | 结果边界 |
| --- | --- | --- | --- |
| [13+ 小时 C++ 算法精度运行](cases/independent-cpp-accuracy-long-run.md) | 复杂精度工作有本地折腾与上下文丢失的风险 | 愿景对齐的 replan 触发公开研究与新的 code-memory 方法 | 精度提升为用户报告;公共工具可检查 |
| [四天无人值守 agent 运行](cases/independent-four-day-unattended-agent.md) | 操作者需要无需重复提示的有用工作 | 持久延续加周期报告界面 | 四天与有用性为用户报告 |
| [公共 Engine 重构](cases/independent-public-engine-refactor.md) | 庞杂 Engine 混合了九个职责区域 | 一个持久 goal 变成分阶段、PR 规模的组件抽取 | 七个 PR 公开;归因与 token 规模为用户报告 |

目录与托管索引把这些外部案例放在首位。README 文件只保留最强三个并链接回这里;完整清单留在此目录。

## 贡献者、创作者与 Demo 案例

| 案例 | 类型 | 模式 | 证据 |
| --- | --- | --- | --- |
| [外部硬件-agent 工作流](cases/0619-dynamic-workflow-hardware-agent.html) | 贡献者案例 | 动态工作流、多 agent 收敛 | 贡献者批准的交互式案例 |
| [LoopX 自我迭代](cases/0619-loopx-self-iteration.md) | 创作者 dogfooding | 自我迭代、peer 认领、证据回写 | 公开 Git 证据 |
| [隔夜 PR 批处理](cases/0627-overnight-pr-batch.md) | 创作者 dogfooding | PR 规模切片、验证回写 | 十小时公共 Git 窗口内 22 个合并 commit |
| [隔夜项目重构](cases/0623-overnight-project-refactor.md) | 创作者 dogfooding | PR 规模切片、todo 跟进、取代 | 公开安全生命周期叙事 |
| [被阻塞 P0 安全轮换](cases/0617-blocked-p0-safe-rotation.md) | 可复现 demo | 具体用户关卡、安全的 P1/P2 兜底 | 聚焦合成 smoke |
| [PR 问题自动修复](cases/0624-pr-issue-auto-fix.md) | 可复现 demo | 问题修复工作流、复现、审查者交接 | 公开安全模式案例 |
| [Agent 对 Agent 的 PR 评论 Loop](cases/0623-agent-to-agent-pr-comments.md) | 可复现 demo | 认领交接、评论、修复、审查包 | 公开安全模式案例 |
| [DSH × LoopX Replan](cases/dsh-loopx-replan-demo.md) | 可复现录屏 demo | 原生技能选择、持久 Replan、GoalBar 收尾 | 真实 DSH 录屏加确定性公共 fixture |

## 附录案例

| 案例 | 模式 | 状态 | 公开界面 |
| --- | --- | --- | --- |
| [0620 创作者-操作者长程 agent 案例](cases/0620-creator-operator-case-spec.md) | 创作者-操作者工作流、用户关卡、反馈捕获、素材库 | 合成产品案例规格 | [假数据 storyboard](creator-ops-fake-data-storyboard.md)、[反馈契约](creator-ops-feedback-boundary-contract.md) |

附录案例是有用的产品方向,但在出现真实公开证据或经批准的公开安全用户故事之前,它们不应出现在前场顶卡上。

## 案例生命周期

1. **捕获**:一个真实项目展现出持久的控制面行为模式。把原始截图、私有聊天与内部链接留在本仓库之外。
2. **报告**:把反馈归结到
   [案例报告形态](poc-feedback-case-report-loop.md#case-report-shape):
   领域、Loop 长度、难处、LoopX 行为、人类决定、证据与私有边界。
3. **脱敏**:撰写公开安全案例卡片,领域泛化、证据边界明确、且不含私有来源材料。
4. **可复现**:添加一个不依赖私有工件、能证明可复用 LoopX 行为的小型合成 demo 或 smoke。
5. **前端就绪**:添加或更新可视化网站卡片所需的目录字段,例如证据序列、模式标签与建议视觉布局。

案例可以在有可运行 demo 之前进入目录,但其状态必须明确说明这一点。一个脱敏 stub 应做适度的声明并指出缺失的公开证据,而不是用猜测填补缺口。

## 脱敏规则

不要提交:

- 私有文档或聊天 URL;
- 内部工具的原始截图;
- 非公开用户、团队、客户或专有项目的名称;
- 本地文件系统路径、任务 id、凭据、原始轨迹、基准任务文本或 verifier 输出;
- 没有公开紧凑证据支撑的基准性能声明。

应当提交:

- 泛化的领域标签,如 `hardware-agent-development` 或 `benchmark-rotation`;
- 可复用的控制面模式,如 `concrete_user_gate`、`blocked_priority_fallback` 或 `dynamic_workflow`;
- 演练公开 LoopX 契约的合成 demo;
- 能让未来作者保持诚实、明确的 `evidence_boundary` 说明。

## 未来前端形态

目录刻意小到静态网站可以渲染。一个好的首版网站视图应展示:

- 按模式家族分组的案例卡片网格;
- 每个案例的可视时间线:触发、LoopX 状态、agent 动作、用户决定与结果;
- 当案例有合成复现时的"试试 demo"命令;
- 当案例是等待贡献者细节的 stub 时的脱敏徽标。

前端应把目录当作真相来源,并链接回人类可读的案例页面获取叙事语境。
