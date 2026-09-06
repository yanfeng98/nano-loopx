# active_state_structured_projection_v0
> [English](active-state-structured-projection-v0.md)

`active_state_structured_projection_v0` 是 `ACTIVE_GOAL_STATE.md` 的读模型。它把 Markdown 保持为人/agent 工作台，同时为 status、quota、评审包、dashboard 与未来 event-store 迁移暴露类型化 todo、gate、下一动作与迁移诊断。

这不是新规范存储。投影可从当前 active-state Markdown 重算，且不授予写权限。

机器拥有的 Todo 读取子集在 `coordination_state_contract_v0.json` 中单独版本化。该 provider-neutral 契约由 Python 与 TypeScript 共享。它为文件、NoKV 或 PostgreSQL 权限头声明遗留消费者记录与独立原生域记录。`archive_state` 是持久化任务状态：归档变更独立于完成地影响交接与继任资格。`source_section` 与可选 `index` 属于 Markdown 兼容投影，而非原生创建输入。遗留 v0 记录保留这些字段；把它们导入域版本需要显式资格界定，包括保留当前受 `index` 影响的优先级平局排序。不存在自动存储头迁移。Provider 绑定投影拒绝未知字段，而不是静默丢弃它。移除已声明字段需要经评审的兼容决策与 maintainer 批准，包括对已持久化但尚未被决策路径使用的字段。

## 形状

```json
{
  "schema_version": "active_state_structured_projection_v0",
  "source": "markdown_active_state",
  "source_ref": "ACTIVE_GOAL_STATE.md",
  "goal_id": "optional-goal-id",
  "frontmatter": {
    "status": "active",
    "updated_at": "2026-06-28T00:00:00+08:00"
  },
  "next_action": {
    "count": 1,
    "first": "Run the next bounded validation slice.",
    "entries": ["Run the next bounded validation slice."]
  },
  "todos": {
    "user": {
      "total_count": 1,
      "open_count": 1,
      "done_count": 0,
      "implicit_todo_id_count": 0,
      "items": []
    },
    "agent": {
      "total_count": 1,
      "open_count": 1,
      "done_count": 0,
      "implicit_todo_id_count": 0,
      "items": []
    }
  },
  "diagnostics": {
    "schema_version": "active_state_projection_diagnostics_v0",
    "parseable": true,
    "migration_ready": true,
    "warning_count": 0,
    "error_count": 0,
    "warnings": [],
    "errors": []
  }
}
```

## Todo 项

Todo 项尽可能使用既有 `todo_item_v0` 字段：

- `todo_id`、`todo_id_source`、`role`、`status`、`done`；
- `priority`、`title`、`task_class`、`action_kind`、`continuation_policy`；
- `claimed_by`、`blocks_agent`、`global_gate`、`unblocks_todo_id`；
- `resume_when`、`no_followup`；
- monitor 元数据，如 `target_key`、`cadence`、`next_due_at` 与 `consecutive_no_change`；
- 紧凑证据字段，如 `note`、`evidence`、`reason`、`completed_at` 与 `updated_at`。

`todo_id_source=metadata` 意为项携带显式 LoopX 元数据。`todo_id_source=generated` 意为投影从 role、来源节、index 与文本生成稳定兼容 id。生成 id 对读取兼容有用，但不具备迁移就绪性。

## 诊断

诊断刻意保持小而机器可读：

| 诊断 | 严重级 | 含义 |
| --- | --- | --- |
| `missing_frontmatter` | warning | Markdown 缺少 status 或 updated time 等 frontmatter。 |
| `missing_next_action` | warning | 未投影任何 `## Next Action` 条目。 |
| `missing_todo_sections` | warning | 未投影任何用户或 agent todo 项。 |
| `implicit_todo_ids` | warning | 部分 todo id 是生成而非显式元数据 id。 |
| `duplicate_todo_ids` | error | 多项使用同一显式或生成 todo id。 |

`migration_ready=true` 要求至少一个 todo 项、无错误、无隐式 todo id。非就绪投影对状态与操作员显示仍可能有用；它不应提升为规范 event-store 输入。

## 读取器契约

读取器应把本投影视为：

- 只读；
- 仅在正常 `loopx check` / 边界扫描之后公开安全；
- Markdown 之上的兼容层，而非 todo/event 写 API 的替代；
- 在把 active-state 解析移出 `status.py` 之前用于一致性测试的桥。

写者必须继续使用 LoopX 命令，如 `loopx todo`、`loopx refresh-state`、`loopx operator-gate` 与未来事件追加 API。直接编辑投影不是状态迁移。

## Markdown 所有权边界

Markdown 不是单一无差别数据库行。其自由格式理由、笔记与操作员叙述仍由人编写。与版本化协调契约对应的小节可以在权限提升后作为确定性兼容投影重新生成。提升不得使无关散文变成生成内容，也不得丢弃机器自有记录契约之外的文本。

切换刻意按节进行，而非按文档：

- 提升前，Markdown 保持权威且既有写者不变；
- 提升后，版本化 Todo 记录位于规范 provider 头，Markdown 的 Todo 小节是兼容/工作台投影；
- 自由格式理由与操作员叙述仍归 Markdown；
- 提升后的 provider 中断失效关闭，绝不使过期 Markdown 重新变权威。

使用该边界的首个写入是 Todo claim。它演练一个完整 provider-neutral TypeScript 事务，同时保持默认本地路径不变。提升后，`loopx todo project-markdown` 可以从精确 provider 修订显式重新生成两个活动 Todo 小节。它绝不在提升前运行，也绝不把 Markdown 变回权威。

投影命令有四个安全特性：

- 它只替换活动用户与 agent Todo 小节范围内；
- 它按字节保留这些范围之外的每个段落；
- 当规范字段无法用当前 Markdown 元数据语法表示时失效关闭，而不是丢弃该字段；
- 它解析回渲染的小节，并要求确定性一致性与第二次幂等渲染才进行 `--execute` 写入。

写者导入遗留 LoopX 生成的 H2/list/metadata 布局。它在首个非生成行处停止，而不是把替换扩展到下一个 H2 或 EOF；随后的 H1、Setext、缩进标题与普通叙述都保持在其所有权之外。代码围栏与多行注释不是 Todo 标题。投影随后在每个 Todo 标题下发出配对的 `loopx:todo-region-v0` 起始/结束标记。渲染器、活动 Todo 读取器与节编辑器共享该边界契约。未来投影使用这些显式界限；孤立、嵌套、不匹配或缺失标记，以及标记区域内非生成内容，都会失效关闭。没有普通 Goal 因安装而被改写或选择加入。遗留无标记读取器与 bootstrap 输出保持不变。

叙述字节保真与规范 Todo 解析/渲染一致性是分开的检查：前者比较未触碰的源切片，后者只读取生成区域。任一标记都不是 provider 权限，也不是当前头新鲜度保证。

每个小节包含一个带规范 provider 修订的紧凑 `loopx:todo-section-projection-v0` 标记，以及该角色完整规范记录的 SHA-256 摘要。标记是血统证据，不是写 API。命令证明渲染记录来自读取时观察到的精确 provider 头。它不声称该修订在读取后仍为当前头；后续规范变更使 Markdown 投影过期并需要另一次显式投影。需要当前权限状态时，消费者必须始终读取 provider，绝不读 Markdown 标记。

回滚刻意不对称。提升前，既有影子回滚隔离候选 provider 血统，Markdown 保持规范。提升后，provider 中断或修订不匹配失效关闭；操作员可以恢复经评审的 provider 快照并重新生成 Todo 小节，但不得把过期 Markdown 提升回规范地位。

## 迁移路径

显式投影器目前只接受两个活动 Todo 小节的完整遗留 v0 记录。原生 `TodoDomainRecord` manifests 与归档记录保持失效关闭输入；此命令不得发明缺失的 Markdown 出处，也不得声称原生/归档导出资格。后续适配器切片必须证明原生域一致性、遗留排序保留与归档所有权，才可扩展该边界。它是手动读取时投影，而非自动同步所需的事务绑定投影 outbox。

1. 从 active-state Markdown 发出本投影。
2. 添加把它与既有 status todo 摘要对比的一致性 smokes。
3. 把 Markdown 解析移到同一投影字段背后的专用 active-state 读模型模块。
4. 在持久化写入者围栏之后一次提升一个完整 provider 支撑变更；保持默认 Markdown 模式不变。
5. 只从精确规范 provider 修订重新生成机器自有小节，保留人类叙述并验证解析/渲染一致性。
6. 仅在回滚与幂等检查就绪后提升 provider 投影。
