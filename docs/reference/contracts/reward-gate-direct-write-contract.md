# 奖励与 Gate 直接写入合同

> [English](reward-gate-direct-write-contract.md)

LoopX 有两种必须保持区别的运营者决策写入:run 绑定的 `human_reward` overlay 与 `operator_gate` 决策 run。两者都把人类决策转化为持久的 runtime 证据,但都不授予写入控制权、生产访问权,或跳过下一次状态/registry/配额读取的权限。

本文定义本地运营者决策所需的最小 `decision_write_contract_v0` 规划切片。它刻意保持狭窄:在添加任何新的 dashboard 控件之前,先使用现有 CLI 与 loopback 预览/apply 路径。

## 合同字段

每条直接写入决策路径在启用写入之前都必须暴露这些公开安全字段:

- `decision_kind`:`human_reward` 或 `operator_gate`。
- `goal_id`:精确的 goal id。
- `target_ref`:`human_reward` 的精确所选 run 时间戳,或 `operator_gate` 的精确 `gate_id`。
- `decision`:紧凑的公开安全决策字符串。
- `reason_summary`:一条紧凑的公开安全理由。
- `follow_up`:可选的公开安全后续条件。
- `preview_id`:浏览器奖励追加必需;在单独的 gate 预览端点存在之前,仅 CLI 的 gate 追加可省略。
- `source_of_truth`:`run_bound_human_reward_overlay` 或 `operator_gate_decision_run`。
- `write_effect`:将要追加什么,什么是保持不变的。
- `project_agent_visibility`:写入后目标项目 Agent 应使用的读取路径。

未知字段与看似私有的文本必须被拒绝,而不是静默忽略。

## Run 绑定 Overlay

Run 绑定 overlay 是附加到精确一行 run index 的紧凑、只追加注解。它是"run 绑定"的,因为其目标是特定 run,通常由 `goal_id` 加 `run_generated_at` / run 路径标识。它是"overlay",因为它注解那个先前的 run,而不重写原始 run payload、活跃 Goal 状态或所有未来决策。

对于 `human_reward`,overlay 记录运营者对那一精确 run 或路线结果的判断:决策标签、奖励值、理由摘要、后续条件与时间戳。之后的 status、dashboard 与 controller 就绪投影可以汇总 overlay,但 run 绑定 overlay 仍然是持久的事实来源。它不授予写入控制权、生产访问权、公开提交权限,或跳过新的 registry/状态/配额读取的权限。

## 人类奖励

`human_reward` 判断一个精确 run 或路线结果。标准写入者是 `loopx reward`;本地 dashboard 可以通过 `POST /reward/dry-run` 验证同样的紧凑 payload。

只有以下条件全部成立时才允许浏览器追加:

- `serve-status` 正在 loopback 上运行。
- 服务器以 `--enable-reward-write-api` 启动。
- 追加请求复用来自 `/reward/dry-run` 的精确 `preview_id`。
- 所选的 `run_generated_at`、紧凑奖励 payload 与原始 index 数量仍与预览匹配。

成功追加会写入一行 run 绑定的 `human_reward` overlay。活跃状态可以携带摘要,但 run overlay 仍然是持久的事实来源。

## Operator Gate

`operator_gate` 回答受 gate 保护的交接或命令是否可以进行。标准写入者是 `loopx operator-gate`。review packet 可以显示本地 `operator_gate_dry_run_command`,但该命令属于运营者或 controller,不属于目标项目 Agent。

本合同中不存在 dashboard `operator_gate` apply 端点。在添加之前,先实现与奖励追加等效的独立过期预览握手,并证明在 gate 决策 run 存在后,目标 Agent 只看到已批准的交接。

已批准的 gate 必须包含带新鲜状态检查的 `operator_gate_resume_contract`。接收方 Agent 在执行已批准命令之前必须重新读取当前 registry、活跃状态、配额、repo 快照、策略与 run 状态。

## Dashboard 边界

默认 dashboard 保持以读为主:

- 它可以渲染 status、run history、review packet、奖励 CLI 草稿、`/reward/dry-run` 与控制面设置的 dry-run。
- 它只能通过 loopback `--enable-reward-write-api` 追加奖励。
- 除非相应的显式本地写入 API 已启用,否则它不得暴露 gate 追加、奖励追加或控制面 apply。

添加新的写入 surface 需要 smoke 来证明:默认禁用行为、过期预览拒绝、公开安全文本验证、精确一次 runtime 追加、状态刷新,以及紧凑响应中不泄露本地路径。
