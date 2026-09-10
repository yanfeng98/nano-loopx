# 欢迎使用 LoopX


LoopX 是长时 AI Agent 工作的本地控制面。它保持 objective、gate、todo、evidence、
quota 与 handoff 稳定，同时让 Codex、Claude Code、OpenCode 或自定义 runner
执行有界的 turn。

LoopX 新手？从 [Developer Book](/loopx/docs/book/) 的精心双语路径开始，
或用 [快速上手](guides/getting-started.md) 跑你的第一个 loop。

## 选择你的路径

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **开始使用 LoopX**

    安装 CLI、连接项目、检查当前 gate，并从你的 Agent 启动一个真实目标。

    [:octicons-arrow-right-24: 快速上手](guides/getting-started.md)

-   :material-map-marker-path: **理解控制面**

    了解 goals、user gates、agent todos、quota、evidence 与 handoffs 如何
    融入一个持久 state 内核。

    [:octicons-arrow-right-24: 核心概念](concepts/README.md)

-   :material-book-open-page-variant: **跟随 Developer Book**

    使用一条从控制面基础到项目上手与开发者贡献的精心双语路径。

    [:octicons-arrow-right-24: Developer Book](/loopx/docs/book/)

-   :material-console-line: **运维一个长任务**

    使用 status、quota、review packets 与本地 dashboard，
    而不让浏览器成为真相源。

    [:octicons-arrow-right-24: 运维](operations/README.md)

-   :material-source-branch: **构建或扩展 LoopX**

    从开发者指南、测试策略、协议参考与公共/私有边界检查出发。

    [:octicons-arrow-right-24: 开发](development/README.md)

</div>

## 快速上手

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor

cd /path/to/your-project
loopx connect
loopx status
```

然后从你的 Agent 开始真实工作：

```text
/loopx <complex task>
```

## 核心命令

| 需求 | 命令 |
| --- | --- |
| 检查安装 | `loopx doctor` |
| 检查当前状态 | `loopx status` |
| 判断一个 turn 能否运行 | `loopx quota should-run --goal-id <goal-id>` |
| 管理用户与 Agent todos | `loopx todo --help` |
| 构建 handoff packet | `loopx review-packet --goal-id <goal-id>` |
| 提供本地 dashboard 数据 | `loopx serve-status --global-registry --port 8766` |

## 真相源

文档站点是仓库 Markdown 的公开读模型。canonical 源仍是 `docs/` 中的 Markdown，
而项目本地运行时状态保持被忽略且私有。

- [项目 README](https://github.com/huangruiteng/loopx#readme)
- [公共/私有边界](public-private-boundary.md)
- [Status 数据契约](status-data-contract.md)
- [发布就绪](product/release-readiness.md)
