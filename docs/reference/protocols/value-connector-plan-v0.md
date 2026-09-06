# value_connector_plan_v0

状态：公开安全的 connector 规划与 starter 运行时契约 v0。

`loopx value-connectors` 是兼容 CLI 与协议门面。通用规划与稳定命令界面保留在此。公开 GitHub probes 归 `issue-fix` 所有；`social_browser_x` 的来源、安装与 connector-trial 契约归 `content-ops` 所有。既有调用方仍调用下述命令，而门面把这些委托给相应 provider。

`value_connector_plan_v0` 是面向外部价值 connector 调用的紧凑契约。它位于真实 connector 执行之前，使 LoopX 能把有用的商务开发工作与不安全自动化分开。

v0 的目标很实际：

- 展示如何安装与运行 connector starters；
- 允许有界的公开元数据读取；
- 把账户设置、外部发布、邮件发送、付费服务、私有读取、认证物料与生产动作保持在显式关卡之后；
- 要求每个 connector 调用给出一个金钱、成本、需求或能力指标以及一个终止条件。

## CLI

检查已安装 starter 依赖：

```bash
loopx value-connectors install-check --format json
```

运行首个交付的 connector starter，不做网络读取：

```bash
loopx value-connectors github-public-probe \
  --url https://github.com/owner/repo/issues/1 \
  --format json
```

用有界公开元数据读取运行同一 connector：

```bash
loopx value-connectors github-public-probe \
  --url https://github.com/owner/repo/issues/1 \
  --fetch-metadata \
  --format json
```

在已批准的 LoopX 评论之后检测公开维护者兴趣，而不读取评论正文或顶起线程：

```bash
loopx value-connectors github-reply-monitor \
  --issue-url https://github.com/owner/repo/issues/1 \
  --after-comment-url https://github.com/owner/repo/issues/1#issuecomment-123 \
  --fetch-metadata \
  --format json
```

在任何 connector 执行前规划受关卡的外部写入或账户设置：

```bash
loopx value-connectors plan \
  --connector-id community_channel \
  --connector-kind community_channel \
  --channel "public community thread" \
  --stage external_write_request \
  --target-ref "thread asking about agent workflow operations" \
  --external-write-requested \
  --money-metric "qualified workflow owner asks for a LoopX audit" \
  --success-metric "one audit or demo request" \
  --kill-condition "channel rules reject the reply or no workflow owner appears" \
  --format json
```

## 记录

| 记录 | 用途 |
| --- | --- |
| `value_connector_plan_v0` | 计划级目标、品牌边界、connector 调用、批准关卡与事实契约。 |
| `connector_call_intent_v0` | 一次计划的 connector 调用，含 channel、阶段、访问模式、价值轴、指标、成功指标与终止条件。 |
| `connector_approval_gate_v0` | 针对账户设置、外部写入、发送、发布或私有扩展的精确调用批准关卡。 |
| `github_public_channel_probe_packet_v0` | 公开 GitHub issue/PR/discussion 元数据的 starter connector 输出。 |
| `github_public_reply_monitor_packet_v0` | LoopX 评论后公开维护者回复检测的 starter connector 输出。 |
| `content_ops_social_browser_x_provider_v0` | 兼容门面背后 content-ops 拥有的来源、安装与仅元数据试验契约。 |
| `value_connector_extension_migration_v0` | 兼容墓碑，把退役 connector id 映射到独立管理的 extension，而不执行退役 connector。 |
| `finance_market_snapshot_profile_v0` | 已退役的 Finance 规划 profile；显式遗留请求现在返回 extension 迁移元数据。 |
| `finance_market_snapshot_probe_packet_v0` | 仅为迁移血统保留的历史 Finance probe 证据 id。 |
| `value_connector_install_check_packet_v0` | connector starter 的本地安装/使用清单。 |

## 边界

契约仅在以下条件满足时有效：

- 外部写入绝不直接从计划或 probe 允许；
- 每个账户设置或外部写入请求都有批准关卡；
- 金钱/成本/需求/能力指标与终止条件都存在；
- 原始正文、评论正文、timeline、私有源内容、认证物料、本地路径与原始 provider 载荷都缺席；
- 计划满足 `truth_contract.plan_only=true`；
- starter probe 报告是否有有界外部读取发生。

## 退役 Connector 迁移

`finance_market_snapshot` 不再拥有 Finance 执行，且不映射到 LoopX capability。为使升级可诊断，遗留 `source-map`、`install-check` 与 `plan --connector-id finance_market_snapshot` 选择器返回指向 `loopx-finance-value-discovery` 的 `value_connector_extension_migration_v0` 记录。

迁移记录是指导，不是隐式安装。它说明 provider 是否单独分发、指名源检出包与 manifest 路径，并给出有序的 inspect、install、register、run 序列。agent 只有在其活动权限允许时才可执行本地环境写入。若 extension 源或包不可用，它必须以 `provider source required` 停止，而不是重建旧 connector 或发明 `finance-value-discovery` capability。

## Starter Connector

`github_public_channel` 是首个实现的 starter。它接受公开 GitHub issue、PR 与 discussion URL。查询字符串、fragment、认证物料、非 `github.com` host 与非 HTTPS URL 都被拒绝。

对于 issue 与 PR URL，`--fetch-metadata` 使用 GitHub REST，只复制白名单元数据，如标题、state、labels、评论数、时间戳、author association 与 URL。它不复制 issue 正文、评论正文、timeline 事件、原始 provider 载荷、认证物料或本地路径。

对于 discussion URL，`--fetch-metadata` 在 `gh` 已安装且已认证时使用 GitHub CLI GraphQL。没有 `gh` 时，用户仍可运行 no-fetch 模式，或用 `install-check` 查看缺失依赖。

`github_public_reply_monitor` 接受一个公开 issue 或 PR URL 与一个锚点 issue-comment URL。其实时模式使用 GitHub CLI REST 元数据，只捕获评论作者、author association、时间戳与 URL。它检测公开维护者/member/collaborator 是否在 LoopX 评论后回复，并返回 `prepare_public_triage_note`；否则返回 `wait_no_bump`。

## 浏览器社交 Connector Profile

`social_browser_x` 是首个浏览器支撑的价值 connector profile。它不是无头 X API 客户端，也不授予 LoopX 发布权限。它记录用户的 agent 如何在 LoopX 保持控制面状态的同时，使用 ego-browser 会话做公开安全的 X 工作。

在精确批准关卡之前允许：

- `install-check` 报告 `ego-browser` 是否可用；
- 通过 `loopx content-ops observe-public-handle` 进行的仅元数据公开句柄包；
- 不发送研究笔记、目标特定草稿包、图像/正文/链接/提及评审包与 reply-monitor 计划；
- 面向计划帖子、回复或监控的价值指标与终止条件。

在精确批准关卡之前禁止：

- 账户创建、资料编辑、发帖、回复、转发、用于增长自动化的关注、删除、申诉或付费动作；
- captcha 绕过、凭据收集、cookie 导出、原始 timeline 捕获、私有 DM 或非公开物料；
- 声明的 LoopX 品牌边界之外的公开主张。

该 connector 存在是因为浏览器 channel 往往商业价值最高，但账户健康与公开/私有边界风险也最高。有用的 LoopX 包应让用户把自己的 agent 交给流程，而不交出判断：

```text
install-check -> public metadata packet -> no-send draft packet -> exact approval gate -> ego-browser execution -> compact reply/value monitor
```

## 用户价值

该 capability 只有在 connector 输出能产生以下之一时才有价值：

- 收入或付费转化证据；
- 可衡量的降本证据；
- 一个合格的工作流 owner、演示请求或需求信号；
- 明确能支持前三者的可复用 connector 能力。

Connector 量本身不是价值。
