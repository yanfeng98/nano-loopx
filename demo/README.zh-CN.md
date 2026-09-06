# LoopX Demo 工作区

> **DEMO — 不是官方产品 capability。**
>
> `demo/` 下的一切都是探索性原型 / 展示,不属于交付的 LoopX 产品。它**不**随 LoopX wheel 安装,不在产品 capability 目录中注册,也不通过产品 CLI 暴露。

此目录存放自包含的 demos,保持可从仓库检出运行,供参考与实验:

- `auto_research/` — 自动研究 worker/supervisor 展示(内核、worker loop、证据包、终态结果查询、端到端 demo)。
- `multi_agent/` — 配套的多 agent 启动器展示(契约、round ledger、角色后继、可见启动策略、唤醒调度器)。
- `visible_multi_agent_launcher.py` / `visible_multi_agent_tmux.py` — demo 使用的基于 tmux 的可见多 agent 启动器。

这些 demos 依赖真实的 LoopX 产品模块(`loopx.quota`、`loopx.todos`、`loopx.status` 等),通过在仓库根导入 `demo` 包运行(示例与 smokes 已经把仓库根加入 `sys.path`)。

它们是从产品 capability 组件面(`loopx/capabilities/auto_research` 与 `loopx/control_plane/agents/multi_agent`)迁移过来的,以明确 demo/非产品边界。如果其中某部分成熟为稳定的调用方契约,应晋升回 `loopx/capabilities/<capability>/`,带真实入口点与聚焦验证。
