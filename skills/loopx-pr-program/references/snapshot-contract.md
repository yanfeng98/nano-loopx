# PR 项目快照契约

> [English](snapshot-contract.md)

把 `loopx_pr_program_snapshot_v0` 用作源获取与 LoopX 项目协调之间的
provider-neutral 边界。把源特定命令与凭据保留在提交给 LoopX 的快照生产者之外。

## 形状

```json
{
  "schema_version": "loopx_pr_program_snapshot_v0",
  "program_id": "runtime-reliability",
  "generated_at": "2026-08-06T10:00:00Z",
  "result_completeness": {
    "complete": true,
    "scope": {
      "repositories": ["example/runtime"],
      "states": ["open"],
      "authors": [],
      "time_window": {"since": null, "until": null}
    }
  },
  "requirements": [
    {
      "id": "runtime-parameters",
      "title": "Expose runtime quality and latency controls",
      "priority": "P0",
      "coverage": "partial"
    }
  ],
  "change_requests": [
    {
      "ref": "example/runtime#42",
      "repository": "example/runtime",
      "number": 42,
      "url": "https://example.invalid/example/runtime/changes/42",
      "title": "feat(runtime): expose quality control",
      "state": "open",
      "draft": true,
      "target_branch": "main",
      "head_sha": "0123456789abcdef",
      "updated_at": "2026-08-06T09:55:00Z",
      "checks": "passed",
      "review": "pending",
      "work_item": "action_required",
      "theme": "runtime parameters",
      "priority": "P0",
      "requirement_ids": ["runtime-parameters"],
      "depends_on": [],
      "supersedes": [],
      "description_digest": "sha256:public-safe-digest",
      "review_digest": "sha256:public-safe-digest"
    }
  ]
}
```

## 必需不变量

- `program_id`、`generated_at`、`result_completeness`、`requirements` 与
  `change_requests` 必须存在。
- `ref` 是稳定唯一键。优先 `repository#number`；不要使用标题。
- `result_completeness.scope` 是结构化库存身份。它必须显式命名 repository、
  state、author 与 time-window 过滤条件；数组是无序过滤集合。delta helper
  对完整对象做规范化与哈希，包括任何额外 provider-neutral 过滤条件。
- 仅当先前与当前范围 fingerprint 匹配时，`result_completeness.complete`
  才控制移除语义。只有当前库存对同一范围穷尽时，缺失行才是移除。
  不完整或范围不匹配的快照不得替换持久基线或 monitor result hash。
- `updated_at` 是观察性的。它本身不得触发材料性迁移。
- `description_digest` 与 `review_digest` 可以在不存储原始私有文本的前提下
  证明内容移动。
- `requirements[].priority` 是产品优先级。只有当所有者显式记录该选择时，
  change request 才能有更低的有效优先级。
- `coverage` 为 `none`、`partial` 或 `complete`。不要从合并的邻居推断
  `complete`。

## 集成分支组合

快照是远端生命周期与需求视图；它不是集成分支计划。当项目使用本地集成候选时，
只把显式选择的 change request 映射到单独的被忽略
`loopx_integration_branch_plan_v0` 状态。

每次协调前，证明所选本地源 ref 解析到快照行的 `head_sha`。把结果
`loopx_integration_branch_status_v0` 回读作为额外证据送入分组项目 monitor。
把源 ref 名称与同步 receipts 保留在被忽略的项目本地状态；不要仅为让此组合
生效而把它们加进公开路线图。

按如下方式规范化生命周期值：

| 字段 | 取值 |
| --- | --- |
| `state` | `open`、`merged`、`closed`、`unknown` |
| `checks` | `passed`、`failed`、`pending`、`unknown` |
| `review` | `pending`、`approved`、`changes_requested`、`unknown` |
| `work_item` | `passed`、`failed`、`action_required`、`unknown` |
| `priority` | `P0`、`P1`、`P2` 或 `unclassified` |

## 材料性字段

delta helper 认为以下字段是材料性的：

- `title`、`state`、`draft`、`target_branch` 与 `head_sha`；
- `checks`、`review` 与 `work_item`；
- `theme`、`priority`、`requirement_ids`、`depends_on` 与 `supersedes`；
- `description_digest` 与 `review_digest`；
- requirement 标题、优先级与覆盖。

把新增与完整快照移除视为材料性。把 `generated_at` 与仅时间戳的 `updated_at`
变化视为仅观察。

## 隐私清单

在提交任何源自真实项目的 fixture 或示例前，验证：

- 仓库名、URL、change request 标题、人员与评论都是公开的；
- 没有残留凭据、token、私有可执行名、内部主机名、本地路径或文档 id；
- 原始评论与描述被替换为公开安全摘要，除非其公开文本有意作为 fixture 的一部分；
- fixture 最小化，并证明一个可复用的语义不变量。
