# Dashboard 奖励写入边界


LoopX 已经可以通过 `POST /reward/dry-run` 验证 dashboard 奖励草稿。浏览器侧追加路径是独立的 capability,必须保持显式启用。默认 dashboard 必须保持以读为主:状态导出、run history 检查和 dry-run 验证是允许的;加载 dashboard 并不会启用紧凑奖励 overlay 的写入。

本文定义了显式启用的 `POST /reward/append` 端点的边界。它只对以显式写入标志启动的 loopback `loopx serve-status` 会话实现。

## 当前状态

- `loopx reward` 是标准写入者。
- `loopx serve-status` 默认在 loopback 上提供 `GET /status.json` 和 `POST /reward/dry-run`。
- `loopx serve-status --enable-reward-write-api` 还会在 loopback 上提供 `POST /reward/append`。
- dry-run 端点会验证 goal id、所选 run 时间戳、奖励值、公开安全文本以及 run 制品可用性。
- dry-run 响应是紧凑的,返回 `appended=false`,并包含 `preview_id`。
- dashboard 可以显示 CLI 命令和 dry-run 结果。使用显式写入标志时,它可以把审阅后的预览追加到 `index.jsonl`。

## 追加前置条件

只有以下条件全部成立时,才能实现浏览器 append 端点:

- 服务器以显式写入标志启动,例如 `--enable-reward-write-api`。该标志必须默认关闭。
- 服务器只绑定 loopback。非 loopback 绑定应拒绝启用奖励写入。
- 服务器拒绝来自非 loopback 浏览器源的 append 请求。
- append 请求指向精确的 `goal_id` 和 `run_generated_at`;不允许从浏览器隐式追加到最新 run。
- payload 已通过与 `/reward/dry-run` 相同的验证。
- 响应保持紧凑,不返回 `index_path`、`json_path`、`markdown_path`、本地绝对路径或原始私有证据。

## 预览握手

Append 应为两步流程:

1. dashboard 使用所选 goal、所选 run 时间戳和紧凑奖励字段调用 `POST /reward/dry-run`。
2. 服务器返回一个 `preview_id`,它由所选 run key、紧凑奖励 payload 和当前原始 index 记录数派生。
3. dashboard 只能为那一个精确预览启用追加控件。
4. `POST /reward/append` 重新计算预览 id,并在 payload 改变、所选 run 改变或原始 index 记录数自预览以来改变时拒绝请求。

这样,在运营者审阅 dry-run 结果后,UI 就不会把反馈追加到过期或不同的 run 上。

## 请求形状

未来的 append 请求应只接受紧凑字段:

```json
{
  "goal_id": "example-experiment-goal",
  "run_generated_at": "2026-06-01T00:00:00+00:00",
  "preview_id": "opaque-preview-id",
  "decision": "continue_route",
  "reward": "positive",
  "reason_summary": "comparable validation improved and the route is worth extending",
  "follow_up": "promote the route to the next longer-window check"
}
```

端点应拒绝未知或看似私有的字段,而不是静默忽略。被拒绝的文本应复用与 `loopx reward` 相同的私有模式检查。

## 来源与 Capability 检查

写入路径需要比 dry-run 路径更严格的浏览器检查:

- 只允许来自已配置的 loopback dashboard 源的 append 端点 CORS,例如 `http://127.0.0.1:5173`。
- 要求显式 `--enable-reward-write-api` 服务器标志,并拒绝非 loopback 浏览器源。
- 写入 API 被禁用或浏览器源不是 loopback 时返回 `403`,预览过期时返回 `409`。
- 保持 `GET /status.json` 和 `POST /reward/dry-run` 在未启用 append 写入时也可用。

## UI 规则

dashboard 不应把奖励写入做得像普通表单提交:

- 默认状态是 `Dry-run Check`。
- 只有在成功预览且服务器能力显式启用后,写入控件才出现。
- 控件标签应说明后果,例如 `Append reward overlay`。
- 确认文案应说明该操作会向所选 run index 追加一行紧凑的 `human_reward`。
- 追加后,dashboard 应刷新状态,并显示来自 `loopx status` 的新紧凑奖励信号。

## 实现前的验证

实现 PR 应证明:

- 未带写入标志启动 `serve-status` 时,append 请求被拒绝且 index 保持不变。
- 在非 loopback host 上带写入标志启动会失败。
- 带过期预览的 append 失败且 index 保持不变。
- 带变更 payload 的 append 失败且 index 保持不变。
- 公开安全文本的 append 精确写入一行 JSONL overlay。
- 状态导出在 append 后显示 `human_reward`,且仍然隐藏本地路径。
- dashboard 可以在浏览器冒烟测试中完成 dry-run → append → refresh。

CLI 仍然是标准的奖励写入者。dashboard 的 append 路径是本地运营者对同一个 run 绑定 `human_reward` overlay 的便利操作。
