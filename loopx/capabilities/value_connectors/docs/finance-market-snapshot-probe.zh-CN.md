# Finance Market Snapshot 迁移包

> [English](finance-market-snapshot-probe.md)

状态：已退役的 connector 证据与升级迁移路径。

`finance_market_snapshot` 曾是一个公开安全、无凭据的 probe profile。它从未成为
活动的 connector 或交易适配器。Finance 价值发现现在位于独立打包的
`loopx-finance-value-discovery` extension 中，且没有
`finance-value-discovery` capability。

旧式调用方仍可检视迁移契约：

```bash
loopx value-connectors source-map \
  --connector finance_market_snapshot \
  --format json

loopx value-connectors install-check \
  --connector finance_market_snapshot \
  --format json

loopx value-connectors plan \
  --connector-id finance_market_snapshot \
  --format json
```

三个命令都返回 `value_connector_extension_migration_v0`。它们不执行外部读取、
安装、注册或 Finance 执行。该 packet 给 Agent 一个有界序列：

1. 检视 `loopx extension list --format json`；
2. 从 LoopX 源码 checkout 工作时，若本地环境写入已获授权，安装
   `./packages/loopx-finance-value-discovery`；
3. 用 `loopx extension install --execute` 注册其 manifest；
4. 用 `loopx extension run ... --execute` 调用它。

当前样例是共置信源包，不是随 LoopX wheel 分发的工件。如果 provider 信源或包
不可用，Agent 必须上报 `provider source required`。它绝不能重建旧 connector、
发明 Finance capability、获取凭据、访问账号或私有投资组合、提供投资建议、交易，
或启动持续盯盘（continuous watch）。

历史信源与新鲜度发现仍只是 `finance_market_snapshot_probe_packet_v0` evidence id
下的世系。它们不是当前信源建议，也不证明任何 provider endpoint 可安全自动化。
