# Decision Context 咨询型 provider v0

`decision_context_advisory_provider_v0` 让一个可选的 LoopX extension 实现现有的 Decision Context `ContextProvider` 端口。它是检索契约，不是新 capability、状态权威或 transcript 存储。

## 所有权

- `decision-context` 拥有激活、请求界限、证据 rebase、fail-open 行为、公开投影与持久化转换策略。
- extension 生命周期拥有安装、启用、禁用、升级、doctor 就绪性与修订绑定的进程分发。
- provider 只拥有一个有界的外部读取与响应规范化。
- Goal/Todo/material/amendment owner 仍是召回 claim 持久化提升的唯一路径。

实现声明：

```toml
permissions = ["decision_context.read"]

[runtime]
protocol = "decision_context_advisory_provider_v0"
required_permissions = ["decision_context.read"]

[[implements]]
capability_id = "decision-context"
protocol = "decision_context_advisory_provider_v0"
```

Decision Context 可以选定一个精确的 `config.extension_id`。没有指定时，只有当恰好一个已启用且 doctor 就绪的 extension 实现该协议时，解析才成功。缺失、禁用、过期、歧义、失败与契约无效的 provider 会降级为不可用的召回回执；权威源收集继续。

## 检索请求

运行时接收一个 `decision_context_advisory_retrieve_request_v0` 对象：

| 字段 | 契约 |
| --- | --- |
| `schema_version` | 精确请求 schema token。 |
| `operation` | 恰好为 `retrieve`。 |
| `namespace` | 有界调用方命名空间。 |
| `scope_ref` | 为本次调用选定的 provider-neutral scope；完整证据组装可从 profile 获取它，而一次性召回则临时提供。 |
| `query` | 有界私有检索查询。 |
| `query_summary` | 公开安全描述；原始查询不投影。 |
| `max_results` | 正整数，由 Core 限制在 8。 |
| `timeout_seconds` | 从 1 到 120 秒的有限执行超时，进一步由 extension 绑定限制。 |
| `observed_at` | 调用方观察时间。 |

provider 不得把 scope 解释为 Goal 身份或授权授予。host 专属语法在 provider 边界前被规范化。例如，LoopX 解析 `codex://threads/<thread-id>` 并发出 `host-session:codex:<thread-id>`；provider 从不解析深链。

## 检索响应

运行时返回一个 `decision_context_advisory_retrieve_response_v0` 对象：

```json
{
  "schema_version": "decision_context_advisory_retrieve_response_v0",
  "ok": true,
  "status": "completed",
  "reason_code": null,
  "items": [
    {
      "resource_ref": "provider-private-reference",
      "summary": "Public-safe generic summary",
      "content": "transient exact content",
      "score": 0.5
    }
  ]
}
```

Core 拒绝缺失或未知字段、无效界限、非数值 score、不可用响应上的 items，以及 status/reason 不匹配。进程期限取 profile 请求与 extension 生命周期限制中较短者。`content` 与 `resource_ref` 在完整证据组装期间保持在进程内。对于显式的一次性 `decision-context recall-context`，content 只能在 `local_private_transient` 包中返回给当前 agent；scope、原始 provider 载荷与 content 不持久化。嵌套的公开 `context_provider_retrieval_v0` 回执保留 summary 与 score、对 resource 引用做哈希并省略 content。provider 错误以紧凑原因码报告；subprocess 输出与私有路径不复制进公开状态。每个返回的 content 项都被类型化为不受信任的咨询输入，不能提供指令或权限。

一次性命令把 `scope_ref` 作为调用参数，而私有 profile 继续把关 Goal、Agent、provider 身份、命名空间、界限与超时。它不修改 profile、不扫描权威源、不访问 cursor、不创建 settlement 状态、不授权执行。

该协议不定义 sync 或 write 操作。通过 `ContextProvider` 接口使用的 provider 对 `sync` 返回 `read_only_provider`。它不授予权限、工作区访问、claim、lease、生命周期权限、执行权限、amendment 权限或写 scope。

## Obelisk 实现

可选的 `packages/loopx-obelisk` 发行版为历史 Codex 任务实现本协议。它使用 Obelisk 公开的 `--version` 与只读 `--query` CLI 边界，过滤到精确规范化 Codex 会话，排除 `session.is_invoking`，只接受可见的用户或 assistant 文本行。它不导入 Obelisk 代码、不读取其 SQLite schema、不调用 `--build` 或 `--attune`，也不控制活动 Codex 任务。
