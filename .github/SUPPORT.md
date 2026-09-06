# LoopX 支持


LoopX 是一个开源项目，以尽力而为的社区方式提供支持。本项目不提供
响应时间或解决时限方面的 SLA，目前也不通过本仓库或其社区渠道提供商业支持。

## 选择渠道

| 需求 | 渠道 | 适用场景 |
| --- | --- | --- |
| 可复现的 bug 或安装失败 | [GitHub Issues](https://github.com/huangruiteng/loopx/issues/new/choose) | 对可在仓库中调查或修复的行为，提供公开、脱敏的复现步骤。 |
| 功能请求 | [GitHub Issues](https://github.com/huangruiteng/loopx/issues/new/choose) | 具体问题、期望结果、备选方案与最小有用的产品变更。 |
| 用法或设计问题 | [GitHub Discussions: Q&A](https://github.com/huangruiteng/loopx/discussions/categories/q-a) | 尚未确定是仓库 bug 的提问、配置帮助与设计讨论。 |
| 安全漏洞 | [私有漏洞报告](https://github.com/huangruiteng/loopx/security/advisories/new) | 疑似未打补丁的漏洞。不要在 issue、讨论或聊天中发布。参见 [`SECURITY.md`](SECURITY.md)。 |
| 非正式同伴帮助 | [Discord](https://discord.gg/XmGgQyCFZd) | 上手、工作流对比、展示与社区交流。聊天不是权威的支持或发布记录。 |

公开贡献者工作应放在
[贡献者任务板](../docs/development/contributor-tasks.md) 或贡献者任务 issue
表单中。[技术方向地图](../docs/project/technical-directions.md) 说明
哪些项目正在进行以及适用何种成熟度或晋升 gate。pull request 应遵循
[`CONTRIBUTING.md`](../CONTRIBUTING.md)。

## 官方发布来源

- [GitHub Releases](https://github.com/huangruiteng/loopx/releases) 是
  已发布版本与发布说明的权威来源。
- [GitHub Discussions: Announcements](https://github.com/huangruiteng/loopx/discussions/categories/announcements)
  是不与某个发布绑定的项目公告的权威来源。置顶的
  [当前技术方向与已知限制](https://github.com/huangruiteng/loopx/discussions/2851)
  帖子是带版本仓库地图的社区侧投影。
- [GitHub Security Advisories](https://github.com/huangruiteng/loopx/security/advisories)
  是协调漏洞披露的权威来源。

仓库文档描述当前产品与贡献者契约。Issue 与 pull request 是公开工作记录，
而非通用公告渠道。Discord、Lark 群与 README 中列出的微信联系人是非正式
社区渠道；它们的消息不能替代发布、安全公告、已合并的仓库契约或已发布的
公告。

## 账号真实性

LoopX 目前不指定独立社交媒体账号为官方发布来源。转发、截图、个人账号与
第三方社区可能有用，但它们不是项目的权威通信。当来源冲突时，优先使用 GitHub
官方来源获取相关话题，并在公开
[Discussion](https://github.com/huangruiteng/loopx/discussions) 中请求澄清。

## 提出有用的请求

对于 bug 或支持问题，请包含 LoopX 版本或提交、宿主/运行时界面、命令或工作流、
预期行为、实际行为，以及你能提供的最小公开安全复现。先搜索现有 issue 与
讨论。

在发布前移除凭据、私有仓库内容、原始 agent 会话、本地运行时状态、内部链接与
敏感日志。如果材料无法变得公开安全，不要上传到公开渠道。

维护者与社区成员可能把请求转介到更合适的渠道、关闭重复项或要求更小的复现。
公开请求不保证调查、修复、发布日期或适合生产部署。
