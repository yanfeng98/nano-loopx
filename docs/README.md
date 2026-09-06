# LoopX 文档


LoopX 是长时 Agent 工作的控制面。使用本文档主页为你想做的事情选择最短路径；
更深层的索引把产品方向、运维、协议、证据与历史材料保持可用，
而不把所有内容堆到一页上。

## 选择你的路径

| 你想... | 从这里开始 | 继续看 |
| --- | --- | --- |
| 安装前了解 LoopX | [公共主页](https://huangruiteng.github.io/loopx/) | [项目 README](../README.md) |
| 跟随精心编排的开发者课程 | [Developer Book](/loopx/docs/book/) | [英文版](/loopx/docs/book/) |
| 在仓库里试用 LoopX | [快速上手](guides/getting-started.md) | [新手上手命令路径](guides/newcomer-command-path.md) |
| 运行或恢复一个长寿命目标 | [运维](operations/README.md) | [集成指南](integration.md) |
| 理解控制面 | [架构](architecture.md) | [核心概念](concepts/README.md) |
| 接入 Agent 运行时或 provider | [集成](integrations/README.md) | [扩展与能力](reference/extensions.md) |
| 看看贡献者现在在构建什么 | [当前技术方向](project/technical-directions.md) | [贡献者任务](development/contributor-tasks.md) |
| 构建或评审 LoopX | [开发者指南](development/README.md) | [测试与质量](development/testing-and-quality.md) |
| 检查真实结果 | [展示案例](showcases/README.md) | [研究与证据](research/README.md) |

[公共主页](https://huangruiteng.github.io/loopx/)是最短的产品概览。
[项目 README](../README.md) 保留源码链接的快速上手与能力地图，
而[公共用户手册](https://my.feishu.cn/wiki/CaL5wMk9ui17ngkWzeUcMlAYnZg)提供
更长的上手路径。

## 核心参考

- [架构](architecture.md)：控制面分层与归属。
- [State 交互模型](state-interaction-model.md)：用户、Agent 与 state 通道流程。
- [项目 Agent todo 契约](project-agent-todo-contract.md)：工作、归属、关卡与继续。
- [配额分配](quota-allocation.md)：`should-run` 与 spend 语义。
- [Heartbeat 自动化提示](heartbeat-automation-prompt.md)：定时继续契约。
- [Status 数据契约](status-data-contract.md)：status 与 dashboard payload。
- [Effect interpreter packet](reference/effect-interpreter-packet.md)：
  针对 `quota should-run` 的 canonical effect-request/interpretation/observation 透镜。
- [公共/私有边界](public-private-boundary.md)：可保留或可发布的内容。
- [发布就绪](product/release-readiness.md)：支持的 v0.x 安装、兼容性与晋升关卡。

## 按主题浏览

- [指南](guides/)：上手与任务导向的演练。
- [Developer Book](/loopx/docs/book/)：双语基础、项目上手与贡献路径。
- [核心概念](concepts/README.md)：心智模型与可复用设计模式。
- [运维](operations/README.md)：运行目标、cadence、关注与权威来源。
- [架构与 RFC](architecture/README.md)：系统边界与设计提案。
- [产品](product/README.md)：基础、运行时、界面、用例与路线图。
- [集成](integrations/README.md)：host、runtime、协作与外部系统 adapter。
- [参考](reference/README.md)：稳定契约与版本化协议。
- [开发](development/README.md)：贡献者工作流与质量关卡。
- [能力](../loopx/capabilities/README.md)：outcome 拥有的能力面。
- [展示案例](showcases/README.md)：public-safe 用例与可复现演示。
- [研究](research/README.md)：公开证据与 benchmark 研究。
- [更新说明](update-notes/README.md)：当前公开进度说明。
- [归档](archive/README.md)：被取代与带日期的记录。

## 项目与社区

- [当前技术方向](project/technical-directions.md)
- [开放策略评审](community/open-strategy-reviews.md)
  
- [贡献指南](../CONTRIBUTING.md)
- [贡献者任务](development/contributor-tasks.md)
- [治理](../.github/GOVERNANCE.md)
- [作者与贡献者](project/authors.md)
- [许可与 v0.4.8 过渡](project/licensing.md)
- [项目历史](project/history.md)
- [名称与商标](project/trademarks.md)
- [对外品牌使用指南](project/brand-guide.md) 
- [ADOPTERS](../ADOPTERS.md)：自愿自证的采用目录

## 文档策略

新文档应归入最窄的拥有目录，而不是 `docs/` 根级。阅读
[文档布局与迁移策略](development/documentation-layout.md)了解摆放、
兼容、覆盖与公共边界规则。每份公开文档必须能从本页或某个类别索引到达。
