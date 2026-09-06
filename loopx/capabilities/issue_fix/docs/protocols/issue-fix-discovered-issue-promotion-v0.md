# issue_fix_discovered_issue_promotion_v0

> [English](issue-fix-discovered-issue-promotion-v0.md)

`issue_fix_discovered_issue_promotion_v0` 把 issue-fix agent 在真实工作中发现的
可复现缺陷,转成唯一的 canonical 公开 issue,而不创建重复的运维行。它是基于
现有 GitHub 与 issue-fix 状态的组合契约,不是另一个 workflow engine。

## 输入

`issue_fix_discovered_issue_promotion_input_v0` 只包含结构化的、public-safe
事实:

- 仓库与本地 `discovered-*` 占位引用;
- issue 标题,外加紧凑的问题、复现、预期行为与校验摘要;
- 当前仓库 revision 与 repo-relative/public 证据 refs;
- `issue_fix_duplicate_search_evidence_v0`,证明 open 与 closed issues 都被
  检查过,并记录 `reuse_existing` 或 `no_equivalent_found`,外加紧凑决策理由;
- 一个可选的聚焦 PR URL。

重复决策仍是有证据支撑的 agent 判断。LoopX 不从标题相似性猜测语义等价。
`reuse_existing` 必须指名一个有界候选列表中也出现的 canonical issue。

## 执行

不加 `--execute` 时,该命令无读写。加 `--execute` 时,它要求活跃 `publish`
authority,并执行这个有序事务:

1. 验证选中的现有 issue,或创建结构化公开 issue 并验证返回的 URL;
2. 如果存在 PR,只在需要时添加 `Fixes #N`,用有界回读重试要求 PR 暴露 canonical
   closing issue;
3. 原子替换本地占位 feasibility 行为 canonical issue 行,同时保留 revision-pinned
   上下文与紧凑交付证据;
4. 用同一个显式 `issue_ref` 更新现有 PR lifecycle 行;如果 lifecycle 投影尚未
   运行,返回 `not_projected`,让现有 lifecycle wrapper 填充,而不是让提升失败。

重试是幂等的。Closing-reference 验证最多重试三次读取,短延迟覆盖 GitHub 的
write-after-read 滞后,而不创建后台 monitor。一个 canonical feasibility 行上
已验证的 issue/PR 关联,产生零外部写,也没有重复的 Kanban 或指标行。

GitHub 无法提供跨 issue/PR 事务。如果 issue 创建成功但 PR closing-reference
更新无法验证,LoopX 仍保留 canonical issue 行,并返回具体 blocker
`retry_pr_closing_reference_then_refresh_lifecycle`。因此创建的 issue URL 保持
可审计,而不是丢失在通用错误后面。

## 边界

- raw issue 搜索结果、现有 PR 正文、provider 响应与日志都是瞬态的,从不保留;
- issue 文本由有界结构化输入组成,不是 transcript;
- 本地路径、凭据、私有材料与仓库特定分支都被拒绝;
- 创建 issue 不授权 merge 或生产动作。

## 命令

```bash
loopx issue-fix promote-discovered-issue \
  --goal-id issue-fix-goal \
  --project /path/to/connected/project \
  --promotion-json discovered-issue-promotion.json \
  --execute \
  --format json
```

## 验证

```bash
python3 examples/issue-fix-discovered-issue-promotion-smoke.py
```
