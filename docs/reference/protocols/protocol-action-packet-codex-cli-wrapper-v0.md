# 协议动作包 Codex CLI 包装器 v0
> [English](protocol-action-packet-codex-cli-wrapper-v0.md)

此包装器是 `protocol_action_packet_v0` 与未来 Codex CLI 摘要器之间的冷路径桥接。它刻意处于 `quota should-run` 之外，使热路径保持其接口预算。

包装器消费一份合成的 `protocol_router_comparison_v0` 报告，并为隔离项目构建 Codex CLI 命令信封：

```text
codex exec --skip-git-repo-check --ephemeral --ignore-user-config
  --ignore-rules -c 'approval_policy="never"' --sandbox workspace-write
  -C <isolated-fixture-project> <public-safe prompt>
```

公共 smoke 测试使用伪可执行文件来验证命令形状与摘要 sidecar 契约。它不调用真实 Codex CLI、不读取环境值、不调用直接 LLM API、不运行 Harbor 或 Terminal-Bench、不启动 Docker/云沙箱、不使用付费算力、不读取私有 trace、不复制原始会话历史，也不触碰 leaderboard 路径。

显式的本地 probe 可以选择启用真实 Codex CLI 执行：

```bash
python3 examples/protocol/protocol-action-packet-codex-cli-wrapper-smoke.py --real-codex-cli
```

该模式仍使用隔离的临时项目、`--ephemeral`、`--ignore-user-config`、`--ignore-rules` 和同一份紧凑 prompt；只记录返回码、prompt 长度、摘要、stdout/stderr 字符数等 sidecar 字段。

仅当调用方显式选择真实执行并将输出保持为紧凑 sidecar 时，该包装器才可能成为真正的 Codex CLI 冷路径实验。直接 LLM API 接入继续推迟，直到 Codex CLI 包装器或另一个冷路径对比证明动作清晰度有可衡量的增益。
