# Semantic Preference Hook 能力介绍


内置的 OpenViking 项目作用域适配器见
[OpenViking 项目 peer provider](docs/openviking-project-peer.md)。

LoopX 可以在领域动作执行前可选地召回语义偏好，并在其后构建一条紧凑的应用
回执。该 hook 刻意保持单薄：provider 拥有存储、排序与语义内容；调用方拥有
偏好如何影响其输出，并通过现有 LoopX evidence 或 state 表面写入回执。

除非调用方提供一份启用了的本地私有 JSON 配置，否则该 hook 保持禁用。Git
项目内的配置文件必须被忽略；被跟踪的配置会被拒绝。LoopX 绝不把 provider
命令、配置路径、召回出的语义内容或原始 provider 错误复制进回执。

首选 provider 路径是显式激活的 extension。兼容路径仍接受直接子进程 `argv`；
两条路径使用相同的核心请求、响应、失败策略与回执契约。

## 模块拥有的表面

`surfaces` 是一个以任意模块限定 id 为键的映射。运行时不会对 `issue_fix`、
`content_ops` 或任何其他领域名做分支判断。

```json
{
  "schema_version": "semantic_preference_hook_config_v0",
  "enabled": true,
  "provider": {
    "id": "local_memory",
    "args": ["--project", "."]
  },
  "surfaces": {
    "issue_fix.pr_description": {
      "query": "PR description structure and reviewer language preferences"
    },
    "content_ops.draft_language": {
      "query": "Draft language and section preferences",
      "limit": 3
    }
  }
}
```

LoopX 从运行时状态中的 `semantic-preference` capability 与
`semantic_preference_provider_v0` 协议解析已安装的 provider。`args` 追加在
manifest 拥有的入口点参数之后。manifest 拥有协议、权限、超时与 doctor；
配置无法覆盖它们。`extension_id` 在迁移既有配置或区分多个已安装实现时仍是
可选兼容选择器。`extension_state_file` 是用于测试或专用 embedding 的可选
本地私有覆盖；CLI 的全局 `--runtime-root` 选择正常的隔离运行时。如果已激活的
extension 之后被禁用或不可用，recall 遵循该表面既有的 `fail_open` 或
`fail_closed` 策略。

对于尚未采用 extension manifest 的旧式 provider，替换 provider 对象如下：

```json
{
  "id": "local_memory",
  "argv": ["semantic-preference-provider"],
  "timeout_seconds": 30,
  "probe_argv": ["semantic-preference-provider", "doctor"]
}
```

`argv` 与 `extension_id` 互斥。两者都省略时，从运行时状态选择唯一的已安装
extension 实现。

领域模块拥有表面 id、query、上下文键，以及召回条目如何影响其输出的决策。
新增模块是一次配置变更，不是 LoopX 运行时变更。

## Provider 协议

`recall --execute` 时，LoopX 向 stdin 发送一个
`semantic_preference_provider_request_v0` JSON 对象。provider 在 stdout 上返回
一个 `semantic_preference_provider_response_v0` 对象：

```json
{
  "schema_version": "semantic_preference_provider_response_v0",
  "items": [
    {
      "preference_ref": "provider-owned-reference",
      "summary": "Use concise Chinese sections for this surface."
    }
  ],
  "corpus_inventory": [
    {
      "corpus_id": "project_preferences",
      "scope_ref": "provider-owned-scope-reference",
      "read_role": "primary",
      "write_mode": "provider_managed",
      "write_actor_ref": "provider-owned-actor-reference",
      "source_of_truth": "repository_revision_and_explicit_feedback",
      "writeback_triggers": ["explicit_feedback", "source_truth_changed"],
      "closure_policy": "write_wait_l2_read_scoped_recall"
    }
  ]
}
```

`corpus_inventory` 可选且 provider-neutral。它描述哪些有界语料库参与本次召回、
什么会关闭一次维护决策；它不包含原始记忆。LoopX 校验该清单并推导出
`semantic_preference_maintenance_guidance_v0`。因此一个固定的函数边界可以在同一次
provider 调用中暴露 corpus ids、writeback triggers 与 closure policy，而不必依赖
Agent 记住另一份 runbook。省略该字段的 provider 仍然兼容。

显式反馈或 source-of-truth 变更并不意味每个语料库都必须重写。调用方要么执行
provider 拥有的更新并校验已配置的 closure policy，要么记录一条
`no_write_rationale`。LoopX 不推断语义更新、不镜像 provider 存储、也不把软性
偏好变成执行许可。

Provider 的 stderr 与非零输出被归约为有界的失败类型。`fail_open` 返回空 items
并让领域继续；`fail_closed` 以可操作的错误停止调用方。Provider 失败不会自动
变成 user gates。

`provider.id` 与 `setup_hints` 可选。旧式 `probe_argv` 必须是 provider 拥有的
只读健康检查。Extension providers 改用 manifest doctor。两条 doctor 路径都
不安装包、不启动服务、不改配置、不写凭据；setup hints 只是显式 operator
动作的指引。

## CLI

```bash
loopx semantic-preference recall \
  --project . \
  --config <ignored-config.json> \
  --surface issue_fix.pr_description \
  --context repository=owner/repo \
  --execute

loopx semantic-preference doctor \
  --project . \
  --config <ignored-config.json> \
  --execute

loopx semantic-preference receipt \
  --surface issue_fix.pr_description \
  --application-id pr-123-description-v2 \
  --outcome applied \
  --preference-ref <provider-owned-reference> \
  --artifact-ref https://github.com/owner/repo/pull/123

loopx semantic-preference maintenance-receipt \
  --trigger source_truth_changed \
  --outcome verified \
  --corpus-id project_preferences \
  --scope-ref <provider-owned-scope-reference> \
  --evidence-ref project-preference-readback-v2
```

回执只包含表面、application id、outcome、可选的公开 artifact 引用，以及
provider 拥有的偏好引用的哈希。该命令返回回执而不写文件。调用方可以把它挂到
现有 evidence log、todo evidence 或 `refresh-state` 记录上；该 hook 不维护
第二套 reward 或 memory 台账。

Maintenance receipts 同样无状态。它们只包含 trigger、outcome、corpus ids、
可选的紧凑 evidence 引用，以及 scope 引用的哈希。`verified` outcome 意味着清单
要求的 provider 特定写入、队列或索引等待、直接读取与作用域召回都已通过。
`no_write_rationale` outcome 记录该 trigger 已被评估，但不需要持久的语义变更。

`--context` 可重复，每个条目使用 `lower_snake=value` 语法。无效配置、上下文、
表面或 fail-closed 请求返回结构化的 `semantic_preference_error_v0` 载荷，退出码
为 2，而不是 Python traceback。

## 领域集成

对于经评审的 reward-memory 记录，Stage 3 还暴露
`run_semantic_preference_reward_memory`。调用方提供精确的 corpus、模块拥有的
表面、query 步骤、read-authority 检查点、provider 绑定与模型应用回调。共享的
reward-memory 核心执行 scope/freshness/conflict 守卫并返回紧凑回执；本模块
不新增另一套存储、路由或调度器。函数边界模式允许一次 query，有界的 agentic
模式允许至多三次调用方/模型撰写的 queries。

```python
from loopx.capabilities.semantic_preference import application_receipt, recall

preferences = recall(
    config_path,
    project=project_root,
    surface="issue_fix.pr_description",
    execute=True,
)
# 同一结果识别出在显式反馈或 source-of-truth 变更后需要评估的 provider 自有语料库。
guidance = preferences.get("maintenance_guidance")
# issue-fix 模块决定是否以及如何应用 preferences["items"]。
receipt = application_receipt(
    surface="issue_fix.pr_description",
    application_id="pr-123-description-v2",
    outcome="applied",
    preference_refs=[item["preference_ref"] for item in preferences["items"]],
)
# 通过现有 LoopX evidence/state 表面写入 `receipt`。
```
