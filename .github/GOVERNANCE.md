# LoopX 项目治理


本文档定义 LoopX 的公开项目角色与决策流程。它管辖本仓库及其发布物，
与 LoopX 运行时概念（如 agent peer、todo claim、quota、gate、write scope）是
彼此独立的。

## 当前维护者

| 人员 | 角色 | 自 | 公开证据 |
| --- | --- | --- | --- |
| [`@huangruiteng`](https://github.com/huangruiteng) | 创建者兼首席维护者 | 2026-05-31 | [首次公开提交](https://github.com/huangruiteng/loopx/commit/7dcdc9dc79226d157ba57d3e8ff4bae664f020c1) |

首席维护者目前是发布、维护者任命、安全敏感处理以及本治理模型变更的最终
决策人。当活跃维护者群体扩大后，应重新审视这个裁决角色。

按路径划分子系统的任命与优先评审指派记录如下。子系统任命本身并不授予
仓库级维护者权限。

## 具有写权限的仓库开发者

以下开发者已经持有或受邀接受 GitHub 的仓库 `write` 角色。写权限用于仓库
规则范围内的日常 pull request 与分支工作。它本身不构成维护者任命，也不授予
发布、安全或治理权限。

| GitHub 账号 | 仓库角色 | 访问状态 |
| --- | --- | --- |
| [`@wujc12`](https://github.com/wujc12) | Write | 活跃 |
| [`@ZaynJarvis`](https://github.com/ZaynJarvis) | Write | 活跃 |
| [`@Hoey041`](https://github.com/Hoey041) | Write | 活跃 |
| [`@maxliux5`](https://github.com/maxliux5) | Write | 活跃 |
| [`@JackyCSer`](https://github.com/JackyCSer) | Write | 活跃 |
| [`@steven-kid`](https://github.com/steven-kid) | Write | 活跃 |
| [`@liubf21`](https://github.com/liubf21) | Write | 邀请待处理 |
| [`@wchwawa`](https://github.com/wchwawa) | Write | 邀请待处理 |

GitHub 的仓库设置是访问权限的实际操作依据。当写角色邀请被接受、过期或
撤销时，这份公开快照应通过 pull request 更新。维护者任命仍受下文流程约束。

## 子系统维护者

子系统维护者负责指定界面内的评审质量与契约一致性。该任命不授予无关子系统、
发布、安全处理、仓库设置或管理员绕过合并方面的权限。

### Lark 集成

| 角色 | 账号 | 范围 |
| --- | --- | --- |
| 子系统维护者 | [`@steven-kid`](https://github.com/steven-kid) | 内置 Lark 扩展、其直接 CLI 委托、Lark 能力与集成文档，以及聚焦的 Lark 验证 |
| 首席维护者兼兜底评审者 | [`@huangruiteng`](https://github.com/huangruiteng) | 仓库治理、跨子系统决策，以及对子系统维护者所写变更的评审 |

Lark 集成维护者应：

- 对 Lark 相关 pull request 提供第一批实质响应与设计评审；
- 保持扩展实现、直接 CLI 委托、公开文档与聚焦验证一致；
- 保护 authority、readback、owner-private receipt、retry、idempotency 以及
  跨平台边界；
- 对其他贡献者提交的 pull request 提交 approval 或 change-request 评审；以及
- 对改变共享扩展生命周期、status、quota、todo、release、security 或
  仓库治理契约的变更进行升级上报。

该任命不授权子系统维护者批准自己的 pull request。根据仓库规则，这些变更
仍须由非作者的评审者批准。合并、发布、安全、仓库设置与管理员绕过权限
仍由本文档与首席维护者管辖。

相应路径记录在 [`CODEOWNERS`](CODEOWNERS)。该文件提供自动评审路由。
此任命并不把 code-owner 批准设为分支保护要求。在完成至少三次（通常五次）
跨作者 exact-head 评审周期后，首席维护者可另行决定是否提议强制 code-owner
评审。

### 共享宿主集成衔接点

`@steven-kid` 对当前主要围绕以下内容的共享宿主集成衔接点是优先评审者，
而非唯一 code owner：

- `loopx/host_loop_activation.py`；
- `loopx/host_mode_planner.py`；
- `loopx/cli_commands/host_mode_plan.py`；以及
- `docs/integrations/runtime-connector-catalog.md`。

宿主集成横跨 Codex、Claude Code、OpenCode、DeepSeek Harness 及其他
runtime provider。provider 特定实现仍归相关贡献者与仓库维护者，而共享的
status、quota、todo、scheduler 与 Turn 契约不属于 Lark 任命范围。因此现阶段
这些宿主路径在 `CODEOWNERS` 中未指派给 `@steven-kid`。

### 变更子系统任命

增加、扩大、缩小或退役一个子系统任命，需要公开 pull request 更新本文档及
任何匹配的 `CODEOWNERS` 路由。仅凭贡献数量不足以作为证据。决策应考虑持久的
技术判断力、跨作者评审质量、边界纪律、响应性，以及提议的路径范围是否内聚。

## 项目角色

### 维护者

维护者可以评审与合并 pull request、发布版本、分诊安全报告，并做出仓库治理
决策。他们应保护兼容性、公共/私有边界、贡献者信任以及 LoopX 控制面契约的
质量。

维护者权限是显式的：它来自本文档与仓库权限，而非提交数量、运行时 todo claim
或某个 agent 角色。

### 贡献者

任何改进代码、测试、文档、设计、issue 或评审的人都是贡献者。被接受的提交
与共同署名提交通过公开 Git 历史与 GitHub 贡献者视图得到归属。贡献本身不授予
合并、发布或治理权限。

### Agent 与自动化

Agent 与自动化可以准备变更、运行验证，或出现在提交来源记录中。它们不会成为
人类维护者，也不能授予自己仓库权限。人类维护者仍对合并、发布与边界决策负责。

## 决策方式

- 常规变更使用 pull request 评审、聚焦验证与维护者判断。当变更需要显式
  gate 时，沉默不构成批准。
- 对持久状态、公开契约、默认值、权限、证据策略或兼容性的变更，应说明行为
  影响并包含成比例的回归覆盖。
- 重大的产品或治理变更应在定稿前通过公开 issue 或 pull request 讨论。
- 安全报告、凭据、私有证据及其他敏感内容不得发布在公开 issue 中。向维护者
  索取私下联系渠道，但不要附带敏感细节。
- 发布由维护者在文档化的发布检查通过后执行。例外与已知跳过应记录在发布
  或 pull request 中。
- 没有达成共识时，首席维护者在相关 issue 或 pull request 中记录决策与理由。

## 技术方向治理

带版本的
[当前技术方向](../docs/project/technical-directions.md) 页面是活跃战略项目、
成熟度、贡献路径与晋升 gate 的权威地图。置顶的
[GitHub Discussion](https://github.com/huangruiteng/loopx/discussions/2851) 是
其面向社区的投影；issue、Discussion、RFC 或集成分支不覆盖已合并的运行时与
稳定参考契约。

每个战略方向有一个长期存在的跟踪 issue。跟踪器记录结果、边界、实现负责人、
材料性决策，以及对有界工作的链接。它们本身不是全面实施授权。可认领的变更
应有单独的 issue 或公开任务板行，并带显式的最小切片、基线分支、非目标与
验证计划。

对某个方向的阶段、范围、实现负责人、集成分支或晋升 gate 的材料性变更，
需要 pull request 更新权威地图。当 RFC 索引与贡献者任务板的路由变化时，应在
同一个 pull request 中同步修改。维护者在合并后更新置顶 Discussion，不应在
那里维护独立的路线图正文。

`direction/*` 标签用于路由发现与评审。它们不授予权限、不承诺交付，也不意味着
Draft 或 Research 项目已可实施。被认定为实现负责人只是记录当前公开工作；
它与仓库写权限、子系统维护者任命以及仓库级维护者权限彼此独立。

## 成为维护者

维护者从展现出持久技术判断力、可靠评审、尊重项目边界并关心其他贡献者的
贡献者中产生。由一名活跃维护者提名候选人；由活跃维护者批准任命；变更通过
pull request 记录于此。

维护者可以随时卸任。需要时，不活跃或荣誉身份也应记录在此文件中，而非从
近期提交活跃度推断。

## 问责与范围

重要决策应在 issue、pull request、发布或稳定的项目文档中留下持久的公开
理由。私有事件细节与原始 agent 轨迹不属于该公开记录。

本宪章不创建法律实体、雇佣关系、版权转让或商标注册。归属参见
[作者与贡献者](../docs/project/authors.md)，名称与标识使用参见
[名称与标识](../docs/project/trademarks.md)，贡献流程参见
[`CONTRIBUTING.md`](../CONTRIBUTING.md)。
