# PR 与 Issue 标签


LoopX 使用 GitHub 标签，让维护者、贡献者和 Agent monitor 能够按生命周期与产品领域
过滤、路由和汇总 issue 与 pull request。

## 生命周期标签

这些标签描述条目生命周期，由 issue 模板或维护者分类应用：

| 标签 | 应用方 | 含义 |
| --- | --- | --- |
| `bug` | Bug 报告模板 | 可复现的错误或意外行为。 |
| `enhancement` | 功能请求模板 | 具体的产品或文档改进。 |
| `triage` | Issue 模板 | 工作开始前需要维护者分类或路由。 |
| `duplicate` / `question` / `invalid` / `wontfix` | 维护者分类 | 标准 GitHub 生命周期状态。 |
| `good first issue` / `help wanted` | 维护者分类 | 贡献者上手信号。 |
| `workflow-audit` | 贡献者任务板 | 供 LoopX 审计的公开或合成 Agent 工作流。 |

## 领域标签

领域标签描述一个变更触碰的公共产品面。Issue 模板要求贡献者选择一个领域，
pull request 模板要求自标主领域；维护者应用匹配的标签：

| 标签 | 公共面 |
| --- | --- |
| `control-plane` | 目标、todo、配额、scheduler、registry、runtime、state 与 gate 生命周期。 |
| `benchmark-boundary` | Benchmark adapter、runner、verifier、计分、leaderboard 与公开 benchmark 证据。 |
| `capability-extension` | Capability、extension、provider、adapter 或 skill 契约。 |
| `public-docs` | README、协议文档、frontstage、dashboard 与首屏展示面。 |
| `build-or-ci` | 构建、打包、安装器、CI 工作流与发布流水线。 |

任何没有被领域标签明确覆盖的内容只保留其生命周期标签。

## 分类策略

1. Issue 模板自动应用 `triage` 加 `bug` 或 `enhancement`。
2. 维护者（或经批准的机器人）推进已分类条目：路由到领域标签，
   标记 `duplicate`/`question`/`invalid`/`wontfix`，或链接一个贡献者任务。
3. Pull request 在模板中自标主领域。评审者验证领域与 diff 匹配，
   不匹配时修正标签。
4. Agent monitor（PR 评审队列、issue 接收）可以把领域标签当作路由提示，
   但标签从不授予评审、merge 或写权威。

## 分阶段自动分类

今天的标签通过模板与分类由人类选择。下一阶段可能添加一个基于规则的分类器，
从标题、改动文件和评审领域建议领域标签，随后对长尾情况使用离线模型。
这一分阶段路径遵循 OpenViking 反馈可观测性设计采用的分类实践：
先以确定性规则作为增强，再走向模型，然后稳定分类法。在那之前，
标签是引导，不是自动化契约。
