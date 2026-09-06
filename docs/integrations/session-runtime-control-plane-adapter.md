# Session Runtime 控制面适配器


状态:公开安全架构目标 + 只读投影契约 v0。

LoopX 应当能够与现有 agent 宿主并存,而无需变成该宿主。目标角色是长周期任务
控制面:把会话级执行事实变成 goal 级状态,使其可恢复、可审计、受 gate、按注意力
排序并可跨会话复用。

## 层级边界

agent 宿主拥有执行平面:

- agent 定义与 runtime 配置;
- 环境与会话生命周期;
- 仅追加的会话事件;
- 工具与沙箱执行;
- 宿主认证、速率限制、计费、trace 与审计;
- 原始转录、原始日志与原始工具输出。

LoopX 拥有 goal 级控制投影:

- `goal_state`:目标、非目标、权威来源、当前边界;
- `run_projection`:指向来源事实的紧凑会话/结果摘要;
- `operator_gate`:跨会话的 owner/控制器决策;
- `human_reward`:对路由或运行结果的人类判断,与任务评分器分开;
- `work_lane_contract`:推进、监视、阻止与 user-gate 路由;
- `quota_decision`:goal 是否应消耗下一轮自动 agent Turn;
- `handoff_packet`:给项目 agent 的已批准下一动作;
- `dreaming_proposal`:在晋升之前保持建议性的背景探索。

产品界面拥有前台用户体验:任务卡片、审批、进度、恢复入口与协作视图。LoopX 应
解释卡片为何存在、是否可以运行、哪个 gate 阻止它以及批准后如何恢复;它不应
成为默认的最终用户控制台。

## 核心原则

宿主会话日志是原始事实来源。LoopX 运行历史是紧凑控制投影。投影可以引用宿主
id,例如会话、事件、工具调用、artifact、审批或结果 id,但绝不能把完整转录、
凭证、原始日志、私有 trace 或沙箱内部复制进 LoopX 状态。

这避免了第二个事件存储。如果宿主说会话已完成,而 LoopX 说 goal 仍被阻止,
投影必须解释对账规则:缺失 gate、缺失验证、结果失败、过期 artifact 或尚未记录
的人类决策。

## 适配器阶段

### 阶段 1:只读投影

输入:会话、事件、结果、审批与 artifact 的紧凑宿主摘要。

输出:一个 LoopX 关注条目,包含:

- `waiting_on`;
- `next_action`;
- 第一个未解决的 user todo;
- 第一个可执行的 agent todo;
- 最新验证或阻止项;
- gate 状态;
- 紧凑来源指针。

该阶段绝不能写回宿主、改变 runtime 行为或启动会话。第一个有用的 demo 是一个
长时运行任务首屏,回答四个问题:

1. goal 正在等待谁或什么?
2. agent 现在可以继续吗?
3. 继续之前需要什么 gate 或证据?
4. 最近一次运行验证或阻止了什么?

### 阶段 2:受控写回

在只读投影被证明有用之后,LoopX 可以把紧凑控制事件映射回宿主元数据或事件。
稳定边界是
[`session_runtime_controlled_writeback_v0`](../reference/protocols/session-runtime-controlled-writeback-v0.md):

- 操作员 gate 已请求/已解决;
- 人类奖励或路由判断;
- 交接包已接受;
- 作为 scheduler 提示的配额决策,而不是计费;
- artifact 指针或运行投影指针。

写回必须保持紧凑且可逆。它不应复制原始证据,也不应把 LoopX 变成宿主的权限
系统。

### 阶段 3:产品界面集成

产品界面应展示 LoopX 投影,而不是要求用户直接阅读 LoopX Dashboard。LoopX 仍然
是产品视图背后的可靠性与治理层。

## 非目标

LoopX 不应:

- 重新实现宿主的 agent 循环或模型策略;
- 重新实现宿主的会话事件存储;
- 在宿主已经拥有工具或沙箱时直接运行它们;
- 替代宿主认证、计费、速率限制或 trace;
- 成为普通终端用户的产品前台;
- 存储原始转录、私有 trace、凭证或原始 benchmark 日志。

## 首个公开契约

一个最小的只读适配器契约可以表示为:

```json
{
  "schema_version": "session_runtime_readonly_projection_v0",
  "source": {
    "host_kind": "session_runtime",
    "source_ids_redacted": true
  },
  "session_facts": {
    "session_count": 1,
    "latest_event_at": "2026-01-01T00:00:00Z",
    "outcome_status": "blocked",
    "approval_state": "none",
    "raw_transcript_copied": false
  },
  "goal_projection": {
    "waiting_on": "codex",
    "next_action": "write compact blocker or continue approved handoff",
    "first_user_todo": null,
    "first_agent_todo": "advance one bounded segment",
    "latest_validation": "compact validation summary"
  }
}
```

公开 fixture 应只验证投影语义。私有来源 id、原始事件消息体、确切宿主 URL、
原始日志、凭证与本地路径都留在仓库之外。

当前 v0 实现是一个纯构建器,
`loopx.session_runtime.build_session_runtime_readonly_projection(...)`。它接受
紧凑的会话、事件、结果、gate、artifact 与决策结果摘要,然后返回:

- `first_screen`:等待中的 owner、用户动作、agent 动作、验证、阻止项与建议
  下一步;
- `attention_item`:带来源指针的紧凑 Dashboard/状态条目;
- `work_lane_contract`:`user_gate`、`advancement_task`、`blocker` 或
  `monitor`;
- `reconcile_rule`:宿主日志保持原始事实、LoopX 只存储紧凑控制投影的规则。

### 原材料键分类

构建器从不读取输入值来判断它们是否为原材料;它用类型化的词级规则对输入键名
分类。键按 `_`、`-` 与 camelCase 拆分为词,并按精确键、整词或精确词序列匹配,
绝不做子串匹配。每个键落入三种状态之一:

| 状态 | 效果 | 示例 |
| --- | --- | --- |
| compact(紧凑) | 允许 | 投影读取的键(`status`、`summary`、`next_action`)、时间戳,仅在没有原始证据时的指针/计数后缀(`catalog_id`、`login_at`)、显式安全碰撞(`trace_id`、`message_id`、`log_count`)、用量指标(`token_count`、`max_tokens`) |
| raw material(原材料) | `raw_material_detected`、`agent_can_continue=false`,类别记录在 `raw_material_categories` 中;其值绝不复制 | `credential`(`api_key`、`access_token`、`password`、`secret_id`、`api_key_id`)、`transcript`(`message`、`raw_transcript`、`messages`、`prompt`、`body`、`transcript_id`)、`log`(`log_path`、`stack_trace`)、`local_path`(`file_path`)、`raw_output`(`stdout_tail`、`diff`、`raw_id`) |
| unclassified(未分类) | 在 `unclassified_key_names`(有界)中报告,从不阻止 | `backlog`、`changelog`、`logical_clock` |

词 `token` 只在认证形式中才是凭证(`token`、`access_token`、`auth_token`、
`api_token`、`bearer_token`、`refresh_token`、`id_token`);`tokens_used` 这类
计数形式是紧凑的,但同一键中的原材料词或短语优先于指标与指针捷径
(`tokens_password`、`raw_tokens`、`secret_id` 与 `api_key_id` 都是原材料)。
`trace_id` 是显式安全指针;`trace`、`stack_trace` 与 `trace_path` 属日志。
`log_count`、`prompt_tokens` 与 `prompt_token_count` 是显式安全聚合,
`conversation_id` 是显式安全指针。其余情况,转录证据按精确键 `message` 与整词
`messages`、`prompt`、`prompts`、`conversation` 匹配:`prompt_id`、
`prompt_text` 与 `conversation_ref` 保持原材料,`message_count` 与
`message_ref` 是紧凑指针,而 `message_text` 报告为未分类,而不做任何方向的
猜测。`log` 只按整词匹配,因此 `catalog_id`、`login_at` 与 `changelog` 不会被
标记。

运行:

```bash
python3 examples/session_runtime/session-runtime-readonly-projection-smoke.py
```

OpenViking 式 issue-fix 记忆由公开特化版
[`openviking_session_memory_adapter_v0`](../reference/protocols/openviking-session-memory-adapter-v0.md)
覆盖。该适配器只以紧凑引用与检索 gate 形式保存按 goal 与按 issue 的会话记忆:
公开 fixture 不授权任何实时 OpenViking 检索、记忆写回、issue 或评论正文读取、
原始轨迹或原始工具输出摄取。用以下命令验证:

```bash
python3 examples/openviking-session-memory-adapter-smoke.py
```

## 指标

该集成如果提升了以下方面就有价值:

- 中断任务恢复率;
- 避免的重复计算;
- 跨会话保留的 owner gate;
- 跨会话交接成功;
- 过期投影检测;
- 从"任务被阻止"到"正确的 owner 看到阻止项"的时间。

这些指标是 goal 控制指标,不是模型质量分数。
