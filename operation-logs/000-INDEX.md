# 操作日志索引(2026-09-06,分支 `260906-dev`)

| 序号 | 文件 | 内容 |
|---|---|---|
| 001 | [001-zh-cn-full-translation.md](001-zh-cn-full-translation.md) | 全量文档中文化翻译(113 提交) |
| 002 | [002-zh-only-conversion.md](002-zh-only-conversion.md) | 只保留中文版转换(删除英文,4 提交) |
| 003 | [003-self-review-fix.md](003-self-review-fix.md) | 转换自查与修复(showcase-catalog-smoke) |
| 004 | [004-upstream-merge.md](004-upstream-merge.md) | 上游 7 commits merge(中文融合) |
| 005 | [005-merge-self-review-fix.md](005-merge-self-review-fix.md) | merge 复查与修复(chat server 时序等) |

- 全部操作在 `260906-dev` 分支完成,已 push 至 `origin/260906-dev`。
- 时间轴: 001 → 002(用户澄清"只保留中文") → 003(自查) → 004(用户发现落后 7 commits) → 005(自查)。
- 仓库约定: 文档只保留中文版;源码/CI 与文档机制适配保持构建与测试全绿。
