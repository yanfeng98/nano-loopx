# LoopX 更新说明

> [English](README.md)

LoopX 每两周发布一份 public-safe 更新说明。说明概括公开仓库中发生了什么变化、哪些内容已经作为
产品表面交付，以及哪些控制面或文档契约变得更加稳定。

更新说明的事实源是公开仓库历史：已合并的 PR、提交主题、已交付的文档、公开 smokes 与公开 CLI
行为。私有聊天、内部文档、原始 benchmark traces、本地路径、凭证与仅 operator 可见的状态被
刻意排除在外。

## 最新

- [2026-06-28 至 2026-07-11](2026-06-28-to-2026-07-11.md)

## 归档

| 时间段 | 说明 | 主题 |
| --- | --- | --- |
| 2026-06-28 至 2026-07-11 | [阅读说明](2026-06-28-to-2026-07-11.md) | v0.2 peer-agent runtime、issue-fix 维护者循环、可恢复的 Explore 与 Auto Research、控制面状态可靠性，以及公开验证。 |
| 2026-06-14 至 2026-06-27 | [阅读说明](2026-06-14-to-2026-06-27.md) | LoopX 更名、benchmark 工作流加固、host 命令、issue-fix 工作流、事件化状态、任务图与 scheduler 可靠性。 |
| 2026-05-31 至 2026-06-13 | [阅读说明](2026-05-31-to-2026-06-13.md) | 公开 scaffold、本地控制面、dashboard 表面、quota/heartbeat 循环、review packets 与 project-agent todo 契约。 |

## 发布规则

- 保持每份说明紧凑且 public-safe。
- 优先使用稳定的产品主题，而不是原始提交列表。
- 引用有用时链接公开文档或 PR，但不要求读者检查私有状态。
- 把说明当作摘要表面。事实源仍是公开 git 历史、LoopX CLI 行为与已交付文档。
- 以 2026-05-31 的初始公开 scaffold 为锚点、每两周发布一次。
- 下一个预期时间段：2026-07-12 至 2026-07-25。

## 自动化

见 [每两周更新说明自动化](automation.md) 推荐的发布路径。简短版本：
`.github/workflows/update-notes.yml` 运行一个独立的只读 release-note job，上传可审查的草稿
artifact；草稿就绪时由人打开 PR。这不是活跃 LoopX heartbeat 内部的自定义逻辑。
