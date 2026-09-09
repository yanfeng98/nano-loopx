# 控制面规则缝合线图


本笔记是缩小热控制面文件规模且不先改变行为的重构图。它对当前集中在 `loopx/quota.py` 与 `loopx/status.py` 的规则族进行盘点,命名稳定的抽取缝合线,并定义代码移动期间必须保持绿色的奇偶校验。

## 范围

第一个重构分支应让控制面更容易推理,而不是更聪明。本阶段的稳妥工作限于:

- 盘点规则族与归属边界;
- 为当前行为添加表征或奇偶校验;
- 在相同的公开 CLI/API 字段背后抽取纯函数;
- 保持 Markdown active state 作为人/agent 的工作界面;
- 在事件/读取路径契约被单独验证之前,避免修改规范存储。

不要把这些缝合线与评分变更、基准 runner 变更、私有 evidence 迁移、生产动作或公开首屏文案混在一起。

## 当前热文件

| 文件 | 当前职责 | 重构风险 |
| --- | --- | --- |
| `loopx/quota.py` | 配额资格、工作车道路由、agent 车道选择、monitor 轮询写回、调度提示、交互契约、花费事件与配额 markdown。 | 策略、投影、写回与渲染规则可能开始意外依赖彼此。 |
| `loopx/status.py` | active 状态解析、todo 投影、事件投影回退、关注队列、任务图、项目资产、状态收集与状态 markdown 的兼容入口。 | 读模型构造已有有界归宿,但 Markdown 解析仍然灵活且弱类型。 |

## Status/Quota 边界检查点

当前安全的抽取前沿是共享 todo 读模型。以下纯辅助函数现在应位于 `loopx/control_plane/todos/projection.py`,或经由该模块调用:

- todo 优先级标签、档位、索引值与排序键;
- 任务文本/类别、可执行打开检查、延迟检查与认领可见性检查;
- due monitor、调度间隙与 monitor 过期检查;
- claimed-by/未认领 agent 可见性;
- claim 范围的 agent id 与 monitor 写回支持标志;
- monitor 摘要项收集;
- 首个可执行推进项选择。

除非下一个候选同样是纯读模型辅助函数且已有廉价奇偶校验覆盖,否则该检查点应止住微辅助函数循环。下一个有价值的切片不是 `quota.py` 中又一个一行包装器,而是 agent 范围前沿与用户 gate 读模型的表征优先抽取。

一个微妙情形是跨摘要车道的 monitor 项聚合。当前投影会对同一 dict 对象的重复引用去重,同时仍允许同一 `todo_id` 通过不同车道投影出现。该行为不应被当作遗留兼容正当化,也不能作为长期 API 看待。改动它之前,先表征预期的车道投影身份,再迁移到稳定的键,如 `todo_id` 加投影车道/来源。

在表征 fixture 存在前,把这些区域留在 `quota.py`:

- agent 范围用户 gate 过滤与 fallback 选择;
- 交接 gate、清障后继、延迟恢复与 monitor 阻碍恢复选择;
- 工作车道契约组装与有效动作选择;
- 协议动作包、调度提示、配额花费、monitor 轮询与调度 ACK 写入路径。

这些区域混合了投影与策略。没有奇偶 fixture 就移动它们,可能悄然改变某对等方看到的 todo、某 monitor 项是否到期,或自动化报告的是安静等待还是必需进展。

因此下一个模块边界 PR 应:

1. 先添加 agent 范围/用户 gate/前沿表征 fixture,从
   `examples/control_plane/agent-scope-projection-characterization-smoke.py`
   开始;
2. 只在奇偶校验被固定后再于
   `loopx/control_plane/agents/agent_scope.py` 下抽取第一个只读 agent 范围模块;
3. 在新模块被聚焦 smoke 配置覆盖之前,把 `quota.py` 保留为策略/编排层;
4. 只在当前缝合线经聚焦配置保持绿色后,再按用户 gate、前沿与提示投影进一步拆分 `agent_scope.py`;
5. 用共享 todo 投影辅助 smoke、status/quota 评审包奇偶 smoke 与 `core-control-plane` smoke 配置校验。

## 配额规则族

| 族 | 当前锚点 | 目标缝合线 | 抽取护栏 |
| --- | --- | --- | --- |
| 工作车道策略 | `_work_lane_contract` | 纯策略模块,从紧凑状态输入选择车道、义务、monitor 策略与原因码。 | 推进、due monitor、外部 evidence 与安静跳过案例的奇偶快照。 |
| 能力与边界关卡 | `_capability_gate`, `build_agent_workspace_guard`, `_automation_prompt_upgrade` | 返回类型化决策且不修改 payload 的 gate 评估器。 | 现有配额契约字段与工作区护栏故障模式保持稳定。 |
| Agent 车道选择 | `_agent_lane_next_action`, `_agent_lane_frontier_hint` | 对归一化 todo 投影的 agent 范围选择器。 | 当前 agent 认领的 todo 优先于无关 agent;无可运行候选时前沿提示保持诊断性。 |
| Goal 前沿与重规划决策 | `loopx.control_plane.goals.goal_frontier`, `build_quota_should_run` 适配器 | Goal 前沿策略拥有完成/重规划投影;配额只选择由此产生的交互模式。 | 必需的自主重规划在 monitor 安静或 agent 范围等待分类之前决定,不扩大 quota 内的逐 agent 愿景逻辑。 |
| Agent 愿景与 goal 路由契约 | 未来的 goal 路由策略/CLI 适配器加 `goal_vision_replan_contract_v0` | CLI 强制的有界愿景字段、逐 agent 愿景检查点以及愿景/重规划状态机。 | 超预算愿景在 status/quota 之前失败或压缩;实质性收尾发出 `vision_checkpoint_v0`;配额只消费投影,不拥有逐 agent 愿景存储。 |
| 配额计划与 should-run 组装 | `build_quota_plan`, `build_quota_should_run` | 合并状态、配额核算、gate 与策略输出的薄编排层。 | `quota should-run` JSON 字段名与交互契约保持兼容。 |
| 效果包透镜 | `loopx.control_plane.effect_program.interpret_quota_should_run_packet` | 基于现有配额包的只读规范效果槽。 | 运行时决策不变;聚焦测试与文档消费该透镜。 |
| 用户/agent/CLI 分离 | `_protocol_action_packet`, `_interaction_contract` | 没有调度或写回副作用的协议包构建器。 | 运维者 gate 与有界交付 payload 保持相同的 action_required 与 must_attempt 含义。 |
| 调度策略 | `_scheduler_hint` 包装器加 `loopx.control_plane.scheduler.scheduler_hint` | 由最终决策状态驱动的纯调度提示构建器。 | RRULE、重置令牌与无花费节奏字段在宿主与本地 Loop 间保持稳定。 |
| Monitor 写回 | `_quota_decision_due_monitor_item`, `build_quota_monitor_poll_event`, `record_quota_monitor_poll` | 具有幂等 todo 查找与下次到期投影的 monitor 事件/写回模块。 | due-monitor 与外部 evidence monitor 轮询路径保持无花费,并拒绝非 monitor todo。 |
| 花费核算 | `build_quota_slot_spend_event`, `spend_quota_slot` | 具有显式可核算运行查找的配额核算模块。 | 只在已验证写回后花费;来源枚举与槽核算保持不变。 |
| Markdown 渲染 | `render_quota_should_run_markdown` 及相关渲染器 | 基于已构建 payload 的纯渲染模块。 | JSON 决策不依赖 markdown 字符串。 |

## 状态规则族

| 族 | 当前锚点 | 目标缝合线 | 抽取护栏 |
| --- | --- | --- | --- |
| Active 状态解析 | `parse_state_frontmatter`, `parse_active_state_todos`, `structured_todo_item` | 保留 Markdown 为可编辑工作台的类型化 active 状态投影模块。 | 现有 TODO 语法、优先级解析、`claimed_by` 与元数据字段继续解析。 |
| 事件支撑的 active 投影 | `active_state_event_projection_fields` | 可带显式警告回退到 Markdown 的读取路径投影适配器。 | 事件投影警告保持可见;回退不悄然隐藏畸形 state。 |
| Todo 摘要/读模型 | `compact_todo_group`, `todo_item_is_due_monitor`, `apply_resume_conditions` | 具有显式可运行、受阻、延迟、due-monitor 与可见性车道的 todo 投影模块。 | Due monitor 意为 `task_class=continuous_monitor` 加 `next_due_at<=now`;外部 evidence 关注保持独立。 |
| 卫生与修复信号 | `backlog_hygiene_warning`, `build_autonomous_replan_obligation` | 被 status 与 quota 消费的健康信号模块。 | 修复义务保持机器可读,不能被空的确认清除。 |
| 项目资产 | `build_project_asset` | 基于状态与运行历史的公开安全资产打包器。 | 项目资产支撑的队列项仍是 owner/gate/停止条件语义的唯一权威。 |
| 关注队列 | `loopx.control_plane.work_items.attention_queue.build_attention_queue`,以 `loopx.status.build_attention_queue` 为兼容入口 | 基于归一化 goal 状态、todo、gate 与项目资产的队列构建器。 | 队列排序、项目资产充实、配额护栏与候选车道保持显式且稳定。 |
| 任务图投影 | `loopx.control_plane.work_items.task_graph.build_task_graph_projection`,以 `loopx.status.build_task_graph_projection` 为面向 status 的包装器 | 只读图投影模块。 | 节点上限包含截断元数据;完整的冷路径详情位于热图之外。 |
| 状态收集组装 | `loopx.control_plane.status.collection.collect_status`,以 `loopx.status.collect_status` 为兼容入口 | 连接注册表、运行时、state 与读模型的薄收集器/编排器。 | CLI 状态 JSON 形态保持兼容;包装器/直接奇偶校验由 `examples/control_plane/status-collection-readmodel-smoke.py` 覆盖。 |
| Agent 车道状态投影 | `loopx.control_plane.status.agent_lane_projection.compact_agent_lane_status_payload_for_display` | 用于 CLI 状态展示的逐 agent 车道压缩/过滤。 | 车道范围状态保持只读;配额决策权威不变。 |
| Markdown 渲染 | `loopx/presentation/renderers/status_markdown.py` | 基于状态 payload 的纯渲染模块/辅助函数。 | 渲染不能成为调度或配额真相的来源。 |

## 建议抽取顺序

1. 表征当前行为。
   保持 `examples/control_plane/control-plane-risk-characterization-smoke.py` 绿色,并在移动规则前添加聚焦的奇偶 fixture。
2. 抽取 active 状态与 todo 读模型。
   这降低 Markdown 解析风险,同时保留 Markdown 作为工作界面。
3. 抽取配额策略函数。
   把纯工作车道、agent 车道与调度决策移到现有 `build_quota_should_run` API 之后。
4. 最后抽取渲染。
   在 JSON/读模型 payload 稳定后,移动渲染最安全。
5. 之后才重访写入正确性。
   逐 goal 锁、幂等键、乐观修订检查与租约投影应作为独立契约落地,附带非破坏性 smoke。

## 不可协商的不变量

- `quota should-run` 仍是自动化权限的真相源。
- `interaction_contract` 仍是用户/agent/CLI 职责的真相源。
- `agent_lane_next_action` 是逐 agent 的可运行路由;`## Next Action` 是持久的 goal 级指引。
- `goal_route_hint` 可以为 host 汇总当前、其他 agent 与未认领车道信号,但它是只读建议性投影,必须保留共享的 `## Next Action`。
- `goal_frontier_projection` 是用于车道局部安静/等待决策之前的小型逐 goal 完成/重规划视图;把它的策略留在 `loopx.control_plane.goals.goal_frontier`,而不是扩大 `quota.py`。
- 逐 agent 愿景是有界的 goal 路由契约,不是自由形式的规划记忆。在 CLI/写入边界强制其字符预算;把冗长论证作为 evidence/docs 存储;让重规划只通过有界契约修补愿景。
- Monitor 路由基于属性,而非名称:
  `task_class=continuous_monitor` 加到期元数据定义 due monitor 工作,而
  `waiting_on=external_evidence` 或
  `waiting_on=external_evidence_observation` 定义外部 evidence 关注。
- 热路径投影可以截断扩展详情,但必须发布截断元数据,并让完整详情可通过冷路径界面获得。
- 公开文档、示例与 fixture 不得包含私有链接、本地路径、原始基准日志、原始轨迹、凭据或内部运营上下文。

## 校验矩阵

| 重构切片 | 推送前的必需校验 |
| --- | --- |
| 仅缝合线图/文档 | `git diff --check`;对变更文档运行 `loopx check`;公开/私有边界扫描。 |
| Active 状态/todo 投影抽取 | 表征 smoke 加聚焦解析器 fixture 与对所触模块执行 `py_compile`。 |
| 配额策略抽取 | 表征 smoke 加配额计划/契约 smoke、聚焦策略奇偶 smoke 与 `quota should-run` JSON 奇偶 fixture。 |
| 状态读模型抽取 | 表征 smoke 加状态/任务图/冷路径投影 smoke。 |
| 调度/monitor 抽取 | Monitor 节奏 CLI smoke、monitor 轮询写回 smoke 与无花费花费核算检查。 |
| 写入正确性契约 | 非破坏性锁/幂等/CAS/租约 smoke;未经 owner 批准不迁移规范 state。 |

## 停止条件

当某个切片需要以下任一事项时,停止重构分支并请求评审:

- 移除或重命名一个被状态、配额、dashboard 或评审包用户消费的公开 JSON 字段;
- 改变基准 runner 行为、评分或案例任务语义;
- 迁移规范的 todo/历史存储;
- 改变公开首屏展示;
- 依赖私有源材料或原始本地产物。
