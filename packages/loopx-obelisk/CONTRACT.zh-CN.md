# Decision Context 咨询 provider v0

`loopx-obelisk` 通过 `decision_context_advisory_provider_v0` 实现现有的 `decision-context` capability。LoopX 拥有 profile 激活、扩展生命周期检查、有界请求构造、失败开放行为、公开投影、证据 rebase 与每个持久转换。provider 只拥有通过 Obelisk 公开 CLI 的检索。

## 请求

该扩展在 stdin 上接收一个 `decision_context_advisory_retrieve_request_v0` JSON 对象。操作恰为 `retrieve`;`scope_ref` 恰为 `host-session:codex:<thread-id>`;结果数与超时都是有界的。provider 不接受原始深链、文件系统路径、Goal 转换或凭据。

## 响应

该扩展在 stdout 上返回一个 `decision_context_advisory_retrieve_response_v0` JSON 对象。每个条目包含 provider 私有的 `resource_ref`、public-safe 的通用 `summary`、瞬态的 `content`,以及可选的数值 `score`。Core 在创建 `ContextProviderRetrieval` 之前验证 allowlist 与边界;其公开 receipt 哈希资源引用并省略内容。显式的一次性回忆可以只在本地私有的瞬态 CLI 包中返回内容;它不持久化 scope、query 或内容。

`status=completed` 可能包含零个条目。`status=unavailable` 不含条目,并带有一个紧凑的 `reason_code`。进程失败或无效响应由 Decision Context 转换为失败开放的不可用 receipt。

## Obelisk 边界

provider 把规范化的 Codex 线程 id 转换为 Obelisk 文档化的 `codex:<thread-id>` 会话 id,并且只调用 `obelisk --query <temporary.js>`。查询使用 `search(query, { sessionId, limit })`,只接受 Codex 行,并在 Obelisk 把其会话标记为 `is_invoking` 时排除该行。临时查询文件在每次尝试后删除。doctor 只调用 `obelisk --version`。

## 验证

```bash
python3 packages/loopx-obelisk/smoke/obelisk_provider_smoke.py
python3 -m pytest -q tests/capabilities/test_decision_context_extension_provider.py
```
