# 入门 Loop 预设

> [English](beginner-loop-presets.md)

本笔记把轻量的公开 loop 工程入门模式映射到 LoopX 原生接入。目标不是复制另一个入门运行时。目标是给新用户一条单命令路径,直达 LoopX 已经有价值的部分:与 agent 无关的执行、团队 agent 车道、持久 todo state、调度器与配额护栏、紧凑 evidence 以及人工评审 gate。

## 产品押注

LoopX 应吸收打包模式,而不是吸收真相源。

新用户应看到一个小而有用的预设菜单。每个预设应编译为现有 LoopX state、todo、调度器提示与 agent 指令,而不是创建第二个 `STATE.md` 运行时或单独的 loop 台账。首次运行应安全且易解释。高级预设可以强大,但它们必须是选择加入且可见 gate。

当前薄入口是:

```bash
loopx preset list
```

对于单个预设卡片:

```bash
loopx preset show daily-triage
loopx preset show changelog-draft
loopx preset show pr-watch
loopx preset show ci-sweeper
loopx preset show dependency-sweeper
```

这些命令是只读的。它们渲染 `/loopx ...`、`start-goal`、`quota should-run` 与 `heartbeat-prompt` 命令包;它们不写入注册表 state、不安装自动化、不编辑文档、不创建 PR。

要检查项目是否准备好运行有用的周期 Loop,使用只读评分报告:

```bash
loopx ready-score --goal-id <goal-id> --agent-id <agent-id>
```

该评分聚合现有 `doctor`、`status`、`quota`、调度器、todo 与 evidence 信号。它可以渲染徽章预览,但不写入 README 徽章,也不更改项目 state。

## 推荐矩阵

| 模式 | 用户价值 | LoopX 默认 | 推荐 |
| --- | --- | --- | --- |
| 每日分诊 | 让仓库 owner 定期获得项目摘要,而无需阅读每个 issue、PR 或状态文件。 | L1 仅报告。读取状态、active todo、打开 gate、陈旧信号与下一步动作。不编辑代码。 | 现在吸收为首个入门预设。它以低风险演示了 LoopX state、调度器、配额与无惊喜写回。 |
| Changelog 草稿 | 把最近合并的工作转化为发布说明草稿,给维护者即时有用的东西。 | L1 仅草稿。回答谁应升级、发布解决了什么、是否破坏性、如何验证、谁贡献了;然后保留 PR 支撑的产品分组与可选能力生命周期指引。不发布。 | 现在吸收为低风险展示预设。它易于演示,并帮助 README 读者理解具体输出。 |
| PR 关注 | 通过关注评审、CI 与合并阻碍防止 PR 停滞。 | 默认 L1 关注;仅显式选择加入后 L2。不自动合并。 | 吸收为早期预设,但把它展示为评审辅助,而非自主合并。 |
| Issue 分诊 | 把嘈杂的 issue 队列转化为优先级、标签与下一次回复建议。 | L1 仅提议。建议标签、owner、重复与下一次回复。除非明确批准,否则不外部写入。 | 在每日分诊后吸收,因为它共享大部分只读管道,且对公开 OSS 仓库友好。 |
| CI 清扫器 | 修复显而易见的损坏检查,移除无聊的维护者苦差。 | L2 选择加入。仅 worktree 补丁、必需 verifier、必需成本上限、合并前人工评审。 | 作为高价值高级预设包含。不要把它做成入门默认,但也不要埋没它;一旦 gate 可见,它是最清晰的 ROI 故事之一。 |
| 依赖清扫器 | 处理安全依赖升级、补丁发布与周期更新噪音。 | L2 选择加入。补丁/minor 策略、拒绝列表、verifier、成本上限、合并前人工评审。 | 在 CI 清扫器之后作为高价值高级预设包含。先从策略设计与 dry-run/报告模式开始,再自动修复。 |
| 合并后清理 | 在合并工作后寻找后续债。 | L1 先扫描;仅显式范围后 L2 小补丁。 | 从首个公开菜单推迟。它有用,但对新用户不如 CI 或发布说明易理解。 |
| 就绪评分 | 告知用户其仓库是否准备好运行有用的 Loop。 | 只读报告。从现有 LoopX 信号派生:安装、goal 连接、agent 身份、调度器、配额、todo、gate、evidence 与写入范围。 | 现在吸收为引导式开始中的支撑命令或部分。在评分模型稳定前避免徽章写回。 |
| 成本估算 | 帮助用户在启用自动化前决定节奏与成熟度。 | 仅建议。使用静态预设假设加实时 quota/调度提示;绝不断言精确计费。 | 与引导式预设一起吸收。使用 L1/L2/L3 语言,但保持估算粗放且保守。 |
| 入门模板 | 减少首次运行摩擦。 | 生成 LoopX 原生 todo、心跳提示与首次运行命令包。不要创建并行真相源。 | 仅作为薄预设输出吸收。模板应解释 LoopX state 内核,而不是隐藏它。 |

## 预设层级

### 第一层:入门默认

这些足够安全,可用于首个公开快速开始:

- Daily Triage L1
- Changelog Draft L1
- PR Watch L1

它们应被营销为"打开 Loop,获得有用报告,保持掌控"。在见到价值之前,它们不应要求用户理解 worktree、verifier agent 或合并策略。

### 第二层:高价值选择加入

这些应可见但非默认:

- CI Sweeper L2
- Dependency Sweeper L2

面向用户的承诺应是"当护栏显式时,LoopX 可以起草有界修复"。必需的护栏是:

- 隔离 git worktree;
- 显式拒绝列表与允许更新策略;
- 补丁被视为就绪前通过 verifier 或聚焦 smoke;
- token/节奏上限;
- push、merge、publish 或依赖上线前人工评审;
- 重复失败或未变化的错误签名后升级。

选择器把两者暴露为 `advanced_opt_in` 卡片。它们的默认输出先是 dry-run 或策略报告;补丁车道仅在显式 owner 选择加入后开始,并保持在隔离的 `codex/` worktree 内。

### 第三层:后期扩展

这些应等待首批预设证明路由:

- 合并后清理;
- 更丰富的入门包;
- 外部 connector 写动作;
- 无人值守 L3 模式。

它们有用,但会在产品赢得入门信任之前增加支持负担。

## README 含义

README 最终应使用三层形态:

1. 首屏:一句话、三个入门预设与一个安全承诺。
2. 快速开始:创建或检查真实 LoopX state 的真实 LoopX 命令。
3. 深层部分:与 agent 无关的控制面、团队 agent 车道、轻量 state 内核、调度器/配额、evidence gate 与 L2 选择加入预设。

这让前门保持简单,而不把 LoopX 矮化为模板集合。README 与 README.zh-CN 首屏编辑应先预览供 owner 评审再提交,因为它们改变主要公开呈现。

## 非目标

- 不要把单独的 `STATE.md` 真相源复制进 LoopX 接入。
- 不要在入门路径上暗示自动修复、自动合并、发布或依赖上线。
- 不要用友好文案隐藏 gate。LoopX 的意义在于 gate、todo、evidence 与成本保持可检查。
- 在薄预设选择器证明用户实际选择哪些路由之前,不要添加宽泛的入门脚手架。
