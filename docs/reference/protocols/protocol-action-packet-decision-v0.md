# 协议动作包决策 v0

## 决策

保留 `protocol_action_packet_v0` 作为 `quota should-run` 的热路径协议简化契约。

可选的 TurnEnvelope 可以在字段级一致性成功时，从其结构化动作契约重建该包并省略重复的 summary；完整决策仍会持久化兼容包。

热路径保持确定性与纯规则：

- `llm=no_api`
- 主执行者：用户或 agent
- 用户动作要求
- agent 动作要求
- quiet-noop 许可
- 工作 lane
- 紧凑动作标签

只把 Codex CLI 包装器作为显式的冷路径 sidecar 实验。不要在常规 quota/status/heartbeat 路由中运行它。

将直接 LLM API 接入推迟，直到单独的 backend 对比实验证明：在载荷大小、user/agent 动作清晰度与公共边界安全上，它相对确定性标签有可衡量的增益。

## 证据

该决策基于四个公开安全切片：

1. `protocol_action_packet_v0` 使 `quota should-run` 在保留详细 guard 载荷的同时暴露紧凑的纯规则摘要。
2. `protocol_router_comparison_v0` 对比了推进、用户动作与仅监控场景，并在无模型调用的情况下把最小载荷缩减保持在验收底限之上。
3. `protocol_action_packet_codex_cli_wrapper_v0` 证明 Codex CLI 命令信封可以不调用模型而表示为假契约 smoke。
4. 可选的真实 Codex CLI probe 在隔离 fixture 中运行了一次，产出紧凑 sidecar，同时默认 smoke 路径保持假/无模型。

## 运行规则

`quota should-run`、dashboard 状态与周期性 heartbeat 路由应直接消费 `protocol_action_packet_v0`。它们不应调用 Codex CLI、直接 LLM API、runner 适配器、Docker/云环境或付费算力。

冷路径实验只有在命令显式、隔离、瞬时且仅 sidecar 时才可调用 Codex CLI。sidecar 可以记录最终紧凑摘要、prompt 长度、返回码与 stdout/stderr 字符数；它不得持久化原始 stderr、原始会话历史、私有 trace、凭据或本地认证材料。

## 后续工作

协议简化 spike 对当前 meta lane 已足够完整。除非出现具体协议回归，未来工作应回到长程 benchmark 计划。

下一个 benchmark 侧步骤是已批准的 Terminal-Bench/Harbor 执行环境就绪 lane：检查本地 Docker 或已批准的云执行环境是否可用，然后仅在环境与 benchmark 规则明确后进行一个单任务 no-submit Harbor Codex 试点。
