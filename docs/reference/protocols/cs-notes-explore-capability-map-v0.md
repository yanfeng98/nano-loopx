# cs_notes_explore_capability_map_v0

状态：公开安全选择图 v0。

本图记录从 CS-Notes 只读机制扫描中选出的可复用探索能力。它是 capability 图，不是对 CS-Notes 物料、私有队列、草稿或源正文的导入。所选模式之所以有用，是因为它们把「去看一看」变成有界、可观测且具关卡的产品工作。

## 边界

该扫描只使用通用机制界面：skill 契约、snippet 入口点、README 式工作流笔记与确定性辅助脚本接口。它有意排除私有本地状态、原始物料队列、认证配置、平台会话工件、个人草稿与原始源内容。

一个模式只有在满足以下条件才符合 LoopX 资格：

- 足够来源无关，可用于 GitHub、浏览器、聊天、论文或文档 connector；
- 明确说明读状态、访问路由与回退；
- 在读取任何私有源正文之前可以安全地表示为紧凑元数据；
- 能够产出小工件或验证结果；
- 对仓库 issue-fix、content-ops、实验或通用 connector 工作流有用，而不复制 CS-Notes 特定措辞。

## 已选能力

| 能力 | 复用内容 | LoopX 目标 | 首个产品切片 |
| --- | --- | --- | --- |
| `material_intake_profile_v0` | 意图 profile、来源 lane、S/A/B/Unread 决策与 deep/quick/background/carryover 路由。 | Connector 发现与 content-ops 信号排序。 | 增加一个 `exploration_plan_packet_v0` fixture，记录所选 lane、读状态、证据质量与下一个安全来源动作。 |
| `trusted_source_scan_plan_v0` | 扫描计划不是读取结果：它记录来源路由、访问级别、回退与稍后 writeback 的模板。 | 浏览器/聊天/文档 connector 预检。 | 让 connector 试点在任何实时来源读取前输出 route/access/fallback。 |
| `pre_tick_gate_v0` | 廉价只读信号产出一个推荐动作、gauntlet、guard 与验证期望。 | 长程 agent 的 heartbeat 与配额 preflight。 | 增加一个 preflight 包，区分仅状态 tick 与投递 tick。 |
| `todo_triage_index_v0` | 遗留任务变成结构化类别：agent 可运行、用户/环境阻塞、过期物料流、合并工作流或已完成。 | 仓库 issue fix 与 deferred-todo 可见性。 | 构建一个把导入的 issue/todo 行映射到 LoopX user/agent/deferred lane 的 fixture。 |
| `snippet_registry_contract_v0` | 可复用脚本与 prompt 必须有命名入口点、触发场景、边界说明与验证命令。 | Capability 目录与 connector 包治理。 | 为入口点、边界、验证与公开安全类别增加目录字段。 |
| `guarded_heartbeat_visibility_v0` | 更偏好用户可见的自动化；仅在有空闲 guard 与可见性提示时使用 headless 回退。 | 项目 heartbeat prompt 与 connector 监控 UX。 | 在 heartbeat/status 包中呈现传输模式与可见性风险。 |

## 场景适配

仓库 issue fix：

- `todo_triage_index_v0` 可以把 GitHub issue、评审评论与过期本地 todo 变成一个紧凑可运行集，并带显式用户关卡。
- `trusted_source_scan_plan_v0` 防止 agent 在真正检查来源之前，就把一个链接 issue、外部文档或仓库当作已读取。

自媒体与创作者运维：

- `material_intake_profile_v0` 契合 connector-信息-锚点工作流：先选来源 lane，再对证据排序，然后只把公开安全锚点提升进草稿。
- `trusted_source_scan_plan_v0` 与 `snippet_registry_contract_v0` 使浏览器/聊天 connector 在 owner 评审允许更多之前保持元数据有界。

实验与其他垂直状态界面：

- `pre_tick_gate_v0` 与 `todo_triage_index_v0` 可复用于 ML 实验 lane：待处理运行、结果可用性、失败的环境检查与人类解读关卡都可以在完整实验状态界面存在之前表示。
- `snippet_registry_contract_v0` 为每个垂直包提供一份最小的「如何运行、读取什么、写入什么、如何验证」契约。

## 未导入

这些在 CS-Notes 中有用，但不应原样复制进 LoopX：

- 精确的学习物料队列或个人优先级文本；
- 平台认证设置、会话工件、私有 connector 配置或本地自动化服务文件；
- 原始写作草稿、原始聊天/源正文、截图或私有证据；
- 当一个小型通用包契约已足够时的 CS-Notes skill 全文；
- 只对单个人职业路线图有意义的来源特定排序偏好。

## 推荐下一步

先实现 `exploration_plan_packet_v0`。初始 fixture 入口点现在是：

```bash
loopx content-ops exploration-plan --format json
```

它结合了 `material_intake_profile_v0` 与 `trusted_source_scan_plan_v0` 最强的部分：

- 所选来源 lane；
- 访问/读状态；
- 路由与回退；
- 证据质量；
- 候选提升目标；
- 当下一次读取将越入私有边界时的用户关卡；
- 验证未捕获任何源正文、凭据、本地路径或外部写入。

该包是仓库 issue 发现、content-ops 信号摄取与未来实验状态界面的公共基座。
