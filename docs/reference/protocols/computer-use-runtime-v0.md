# computer_use_runtime_v0

状态：公开安全研究与设计契约 v0。

Computer-use agent 可以操作浏览器、桌面与企业工具，但原始执行循环通常太底层，不适合长程工作：点击、截图、焦点变化与模态框错误本身并不能说明 goal 是否被允许、被阻塞、有价值或能否安全继续。

本契约把 computer-use provider 视为 LoopX 身旁的执行界面，而非新的 LoopX 产品 capability。一个 host 已通过驱动它的任意 agent 运行时提供足够的 computer-use 原语（浏览器工具、无障碍树、页内动作集）。LoopX 不需要拥有或重新实现那套像素级循环。LoopX 拥有的是围绕它的边界：capability 被允许发出的请求、provider 被允许报告的事实，以及随后发生的持久化状态迁移。

## 都称为「Capability」的两种东西 {#two-things-both-called-capability}

「capability」一词在此领域被过载，而这种过载正是本契约早期草稿中大部分命名混淆的来源：

- **LoopX 产品 capability**（`content-ops`、`explore`、`issue-fix`、...）是围绕调用方可见结局组织的稳定 provider-neutral 契约；
- **provider 广告的 capability** 是运行时声明它支持哪些底层原语——截图、点击、输入、无障碍树、录制/重放。

Computer use 是第二种。它本身不是 LoopX 产品 capability，不应注册为一个。它是真实产品 capability 可以选择调用的 provider/运行时执行界面，就像 capability 可能选择 API、CLI 或人类步骤一样。

## 所有权

```text
outcome capability
  -> bounded action request
CUA provider/runtime
  -> observation + typed receipt (facts only)
capability-local reducer
  -> proposed transition
LoopX Kernel
  -> accepted todo / gate / evidence / quota state
```

| 层 | 拥有 | 不拥有 |
| --- | --- | --- |
| Capability（`content-ops`、`explore`、`issue-fix`、...） | 用户可见结局、领域策略、允许哪些效果、如何解释 provider 回执。 | 浏览器安装、像素循环或任一 provider 的会话细节。 |
| CUA provider/runtime（host 浏览器工具、`ego-browser`、Playwright provider、...） | 会话、底层动作、观察、重放/证据句柄与类型化停止原因。 | 直接完成 LoopX todo、创建 gate 或决定 quota/writeback。 |
| Extension/包 | 可选 provider 的安装、doctor、启用/禁用、升级与兼容。 | 发明没有调用方结局的「capability」。 |
| Kernel | 持久化 todo、gate、quota、证据、恢复与最终迁移权限。 | 执行浏览器动作或理解某一 UI 的领域语义。 |

这是多对多关系。一个 CUA provider 可以服务多个 capability（`content-ops` 与 `explore` 都可能驱动浏览器）。一个 capability 可以为同一结局选择 CUA provider、API、CLI 或人类步骤。`value-connectors` 目前是通用外部价值包计划的兼容门面；它不是本契约的 owner，也不应成为。

Reducer 步骤刻意**不**由本协议规定。它是 capability 局部的：`unknown_modal` 在发布工作流中与支付流程或研究抓取中含义不同，因此只有拥有结局的 capability 能把回执变成提议迁移。本文档定义 reducer 允许接收什么（回执、原始动作请求、当前 gate 绑定与自身领域策略）以及它绝不能做什么（自己编写 Kernel writeback），而非 reducer 的形状。

## 中粒度动作模式

Computer-use loop 常在两极失败：

- 原始 UI 原语对规划与评审太小；
- 整个工作流太大，无法验证、重试或交回人类。

边界应落在映射到 todo 或动作包的中粒度动作单元：

```text
goal boundary
  -> bounded computer-use todo
  -> action request
  -> observed UI facts
  -> typed receipt
  -> capability-local reducer decision
  -> LoopX todo/gate/evidence writeback
```

中粒度单元示例：

- 检查设置屏幕并报告开关是否存在；
- 起草帖子但在发布前停止；
- 从已批准字段填表并在最终提交关卡前停止；
- 为成功导航路径捕获重放句柄；
- 从模态框错误恢复：返回 blocker 包，而不是点击未知提示。

## 运行时记录

本协议定义三个面向 provider 的记录。它不定义 reducer 或 writeback 记录；那些保持 capability 局部。

| 记录 | 用途 |
| --- | --- |
| `computer_use_runtime_profile_v0` | 公开安全 provider 能力：浏览器、桌面、无障碍树、截图、重放、沙箱与写模式。仅就绪性，非权限。 |
| `computer_use_action_request_v0` | capability 要求 provider 尝试的有界动作，包括其效果类别、写 scope 与当前 gate 绑定。 |
| `computer_use_receipt_v0` | Provider 实际尝试并观察到的东西。仅事实——无 writeback 决策。 |

`computer_use_session_v0` 与 `computer_use_handoff_gate_v0` 完全推迟。`computer_use_replay_handle_v0` 作为独立记录推迟——目前其形状内联在回执的 `evidence` 字段里。三者只有在真实 capability 消费者需要其精确形状时才作为独立记录变得有用；参见 [相关契约](#related-contracts) 了解它们如何被提升。

## 运行时 Profile

Provider 可以在任何来源访问之前广告就绪性：

```json
{
  "schema_version": "computer_use_runtime_profile_v0",
  "provider_id": "computer_use_runtime",
  "host_kind": "browser_or_desktop_runtime",
  "visibility": "visible_or_replayable",
  "provider_primitives": {
    "screenshots": "host_owned",
    "accessibility_tree": "optional",
    "browser_session": "optional",
    "record_replay": "optional",
    "external_write": "gated",
    "private_source_read": "gated"
  },
  "boundary": {
    "credentials_copied": false,
    "cookies_exported": false,
    "raw_screenshots_copied": false,
    "raw_private_bodies_copied": false,
    "external_write_allowed_without_gate": false
  }
}
```

该 profile 是就绪事实，而非运营真实账户或读取私有物料的许可。`provider_id` 命名运行时；它不是 `value-connectors` connector id，不得暗示那种所有权。`provider_primitives` 刻意不命名为 `capabilities`——它声明的是 [都称为「Capability」的两种东西](#two-things-both-called-capability) 中的第二种 provider 广告含义，而非第一种。

## 动作请求形状

```json
{
  "schema_version": "computer_use_action_request_v0",
  "goal_id": "loopx-meta",
  "todo_id": "todo_example",
  "provider_id": "computer_use_runtime",
  "action_unit": "draft_until_review_gate",
  "effect_class": "draft",
  "write_scope": {
    "allowed_actions": [
      "open approved screen",
      "fill approved draft fields",
      "capture compact receipt"
    ],
    "forbidden_effect_classes": ["external_write", "credential_use"]
  },
  "gate_binding": {
    "gate_id": "gate_example_draft_review",
    "revision": 4,
    "status": "open"
  },
  "stop_condition": "stop at final confirmation or unknown modal",
  "validation_target": "draft screen is reachable and final action remains unclicked"
}
```

`effect_class` 与 `write_scope` 是类型化字段，不是散文。`effect_class` 为 `external_write` 或 `credential_use` 的请求必须携带带当前修订的 `gate_binding`，否则 provider 必须拒绝它。自然语言 `stop_condition` 文本可以补充类型化字段；它绝不能是唯一强制。

动作请求应由拥有 capability 从 LoopX todo/gate 状态与当前 provider 策略生成，而非从粘贴进自动化运行时的临时 prompt 生成。

## 回执形状

```json
{
  "schema_version": "computer_use_receipt_v0",
  "goal_id": "loopx-meta",
  "todo_id": "todo_example",
  "provider_id": "computer_use_runtime",
  "attempted_action_unit": "draft_until_review_gate",
  "stop_reason": "stopped_at_gate",
  "observed_facts": {
    "screen_reached": true,
    "draft_present": true,
    "final_action_clicked": false,
    "unknown_modal": false
  },
  "evidence": {
    "handle_kind": "host_replay_or_screenshot_pointer",
    "raw_evidence_copied": false,
    "private_source_redacted": true
  },
  "idempotency_key": "action_request_example_attempt_1",
  "session_reference": "provider_owned_opaque_session_handle"
}
```

`attempted_action_unit` 回显它所回应的动作请求的 `action_unit`。一个 todo 在其生命周期内可以看到多个动作请求（重试、gate 批准后的恢复尝试），因此回执必须说明它报告的是哪个有界动作，而不是让 reducer 仅凭 `todo_id` 推断。

`stop_reason` 是封闭枚举：`completed`、`stopped_at_gate`、`blocked_by_unknown_modal` 或 `failed`。回执是事实报告。**它绝不能包含 writeback 决策**——无 `complete_todo`、无 `create_user_gate`、无等价命令字段。报告此类字段的 provider 违约；合规验证器拒绝该回执而非转发它。

把该回执变成提议迁移的 reducer 属于发出原始动作请求的 capability。它把回执与携带当前 `gate_binding` 的动作请求，加只有 capability 知道的领域策略结合——例如 `blocked_by_unknown_modal` 对发布工作流与支付流程应分别意味着什么。Kernel 随后在接受或拒绝提议迁移前验证修订、权限与配额。Provider 与协议都不做该决定。

## 运行模式

| 模式 | 默认 LoopX 行为 | 关卡于 |
| --- | --- | --- |
| 公开网页元数据 | 允许紧凑观察与来源句柄。 | 引用正文文本、触达、发帖或趋势主张。 |
| 私有企业工具 | 只发出 owner gate 与运行时 profile。 | 读取私有记录、更改状态、分配用户、导出内容。 |
| 本地桌面或浏览器会话 | 允许安装/就绪检查与合成 fixture 运行。 | 使用已登录账户、下载私有文件、破坏性本地动作。 |
| 草稿工作流 | 允许从批准输入准备草稿。 | 发送、发布、提交、购买、删除、生产变更。 |
| 重放或 skill 捕获 | 只存储句柄类别与安全标志。 | 把原始重放数据、截图、凭据或私有 UI 文本复制进 LoopX 状态。 |
| Benchmark 或沙箱 | 在任务/来源策略允许时允许有界沙箱回执。 | 原始任务文本、轨迹、verifier 输出、上传或 leaderboard 提交。 |

## 人类关注契约

Provider 在减少人工干预次数、同时使剩余干预更清晰时有价值。用户应看到：

- provider 试图做什么；
- 它被显式禁止做什么；
- 捕获了什么证据；
- 下一步是否需要人工评审、另一个 agent todo，还是无需动作；
- provider 卡住时如何接管 host 界面。

呈现该问题是拥有 capability 的职责，用回执加自身领域策略——而非本协议的。需要用户 gate 时，投影必须指名精确决策：

```text
Review the host-owned draft and approve or reject the final external action.
```

它不应只说「owner gate」或「等用户」。

## 失败与恢复

Provider 在以下情况应返回 blocker 而非即兴行事：

- 未知模态框、captcha、登录、支付、权限提示或破坏性确认；
- 隐私状态不明的来源；
- 反复焦点或应用生命周期失败；
- 已声称动作的重放/证据句柄缺失；
- 过期 `gate_binding` 修订，或 `effect_class` 需要尚未开放的 gate 的动作请求。

恢复路径是另一个 LoopX todo 或用户 gate，由拥有 capability 的 reducer 决定——而不是更长的无界 UI 点击链，也不是 provider 为自己做的决定。

## Smoke 预期

初始覆盖应使用合成、声明式 fixture——fixture 描述 UI/会话状态；它不把期望答案交给假 provider。验证器必须独立于 fixture「想」证明什么，按 schema 与上述所有权规则判断每个 fixture，否则测试变成自证。

有用的公开 smokes：

- `effect_class` 为 `external_write` 或 `credential_use` 而无当前 `gate_binding` 的动作请求被拒绝；
- 对带未识别模态框的 fixture 的回执必须报告 `stop_reason: blocked_by_unknown_modal` 且无状态变更动作；
- 携带原始截图字节、cookie、凭据或完整私有页面正文的回执被拒绝——包括一个紧凑外观字段走私凭据、cookie 或 session token 形状内容、即使 provider 自身 `raw_evidence_copied` 标志伪造为 `false` 的情况；
- `gate_binding` 修订过期或同一 `idempotency_key` 被重放时，回执被拒绝或幂等处理；
- 含任何 writeback 决策形状字段（`complete_todo`、`create_user_gate` 或等价物）的回执直接拒绝——provider 绝不能编写 Kernel writeback；
- `goal_id`、`todo_id`、`provider_id` 或 `attempted_action_unit` 与它声称回应的动作请求不匹配的回执被拒绝——这只是身份检查，不是对结局的解释。

实时 provider 测试可以在以后添加，但必须使用相同紧凑包形状，并把原始 host 证据留在 host 或私有项目存储中。

## 相关契约 {#related-contracts}

- 具体垂直切片应属于拥有结局的 capability（例如 `content-ops` 对应草稿直到关卡的发布流程，或 `explore` 对应长程研究浏览），而不在本协议中也不在 `value-connectors` 中。该切片落地后见 capability 自身文档的 reducer 与 CLI 界面。
- `computer_use_session_v0`、`computer_use_replay_handle_v0` 与 `computer_use_handoff_gate_v0` 只有在第二个真实 capability 消费者需要相同形状时才提升进本协议——抽取跟随证明，而非预期。
- [Host integration surface v0](host-integration-surface-v0.md) 定义 host 集成的 CLI 等价读/写基线。
- [Session runtime to LoopX projection v0](session-runtime-loopx-projection-v0.md) 定义 host 会话事实的紧凑投影纪律。
- [Content ops surface v0](content-ops-surface-v0.md) 与 [value connector plan v0](value-connector-plan-v0.md) 定义相邻的发布关卡与外部价值模式；它们是 capability 所有权示例，而非本契约的 owner。
