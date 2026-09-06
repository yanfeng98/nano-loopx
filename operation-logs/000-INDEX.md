# 操作日志索引(2026-09-06,分支 `260906-dev`)

| 序号 | 文件 | 内容 |
|---|---|---|
| 001 | [001-zh-cn-full-translation.md](001-zh-cn-full-translation.md) | 全量文档中文化翻译(113 提交) |
| 002 | [002-zh-only-conversion.md](002-zh-only-conversion.md) | 只保留中文版转换(删除英文,4 提交) |
| 003 | [003-self-review-fix.md](003-self-review-fix.md) | 转换自查与修复(showcase-catalog-smoke) |
| 004 | [004-upstream-merge.md](004-upstream-merge.md) | 上游 7 commits merge(中文融合) |
| 005 | [005-merge-self-review-fix.md](005-merge-self-review-fix.md) | merge 复查与修复(chat server 时序等) |
| 006 | [006-upstream-merge-2.md](006-upstream-merge-2.md) | 上游二次 merge(3 commits,SSH remote)+ 遗留 smoke 适配 |
| 007 | [007-merge2-self-review-fix.md](007-merge2-self-review-fix.md) | 二次 merge 复查与修复(doctor 产品缺陷、42 smoke、demo README) |
| 008 | [008-upstream-merge-3.md](008-upstream-merge-3.md) | 上游三次 merge(11 commits):双语回退、官方中文采用、环境 4 目录初始化 |

- 全部操作在 `260906-dev` 分支完成。
- 时间轴: 001 → 002(用户澄清"只保留中文") → 003(自查) → 004(用户发现落后 7 commits) → 005(自查) → 006(用户发现落后 3 commits)。
- 仓库约定: 文档只保留中文版;源码/CI 与文档机制适配保持构建与测试全绿。
- 网络注意: upstream 已改用 SSH 地址(`git@github.com:huangruiteng/loopx.git`),HTTPS 直连在该环境不可用。
