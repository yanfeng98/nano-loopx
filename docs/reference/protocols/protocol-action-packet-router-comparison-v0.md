# 协议动作包路由器对比 v0
> [English](protocol-action-packet-router-comparison-v0.md)

`protocol_action_packet_v0` 是面向执行器动作清晰度的纯规则热路径基线。它刻意保持精简：`schema_version` 加 `quota should-run` 内部的一个紧凑 `summary` 字符串。

下一个实验必须脱离热路径。对比记录使用 schema `protocol_router_comparison_v0`，检验 Codex CLI 或可选 LLM router 摘要能否在三个公开安全标准上胜过规则包：

- `payload_shrinkage`：router 摘要比规则包摘要显著更短。
- `action_clarity`：主执行者、用户动作要求、agent 动作要求、quiet-noop 许可、lane 与 no-API 边界均得到保留。
- `boundary_safety`：对比过程不读取凭据、环境变量、私有 trace、原始会话历史、模型 API、本地工件路径或 benchmark runner 日志。

首个 fixture 是确定性的，不调用 Codex CLI、直接 LLM API、Harbor、Terminal-Bench、Docker、云沙箱、付费算力或 leaderboard 路径。直接 LLM API 接入继续推迟，直到本次冷路径对比在保留 `quota_should_run_json` 热路径预算的前提下显示出可衡量的清晰度或缩减增益。
